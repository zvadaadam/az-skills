#!/usr/bin/env python3
"""
gl-snapshot — Greenlight PR snapshot tool.

Single-call state gatherer for the greenlight skill. Returns structured JSON
with CI status, review comments (with code context), failure classification,
and recommended actions. Manages persistent state across context compressions.

Usage:
    python3 gl-snapshot.py                      # auto-detect PR from branch
    python3 gl-snapshot.py 7                    # explicit PR number
    python3 gl-snapshot.py --mark-seen 123,456  # mark comment IDs as processed
    python3 gl-snapshot.py --retry-failed       # rerun failed CI jobs (budget: 3/SHA)
    python3 gl-snapshot.py --wait-comments      # poll until new comments appear
    python3 gl-snapshot.py --reset              # clear state for fresh start
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ── Constants ──────────────────────────────────────────────

BOT_CHECK_PATTERNS = re.compile(
    r"coderabbit|copilot|sonar|graphite|codex|openai"
    r"|ellipsis|bito|codeium|sourcery|codeguru|qodo|codescene",
    re.IGNORECASE,
)

FLAKY_LOG_PATTERNS = [
    r"timed?\s*out", r"ETIMEDOUT", r"ECONNRESET", r"ECONNREFUSED",
    r"rate.limit", r"\b429\b", r"\b503\b", r"\b502\b",
    r"runner.*provision", r"infrastructure",
    r"dns.*resol", r"network.*error", r"registry.*error",
    r"Could not resolve host", r"Service Unavailable",
    r"GitHub Actions.*outage", r"runner.*startup",
]
FLAKY_RE = re.compile("|".join(FLAKY_LOG_PATTERNS), re.IGNORECASE)

MAX_FLAKY_RETRIES = 3
POLL_INTERVAL = 30  # seconds
POLL_TIMEOUT = 300  # 5 minutes


# ── gh CLI helpers ─────────────────────────────────────────

def gh(args, allow_fail=False):
    try:
        proc = subprocess.run(
            ["gh"] + args, capture_output=True, text=True, check=True
        )
        return proc.stdout.strip()
    except FileNotFoundError:
        die("`gh` CLI not found")
    except subprocess.CalledProcessError as e:
        if allow_fail:
            return ""
        die(f"gh {' '.join(args)} failed: {e.stderr.strip()}")


def gh_json(args, allow_fail=False):
    raw = gh(args, allow_fail=allow_fail)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def die(msg):
    print(json.dumps({"error": msg}))
    sys.exit(1)


# ── State file ─────────────────────────────────────────────

def state_path(repo, pr_number):
    slug = repo.replace("/", "-")
    return Path(f"/tmp/gl-{slug}-pr{pr_number}.json")


def load_state(path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "processed_comment_ids": [],
        "retries_by_sha": {},
        "round": 0,
        "last_sha": None,
        "last_comment_count": 0,
    }


def save_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(state, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise


# ── PR resolution ──────────────────────────────────────────

def resolve_pr(pr_arg):
    cmd = ["pr", "view"]
    if pr_arg:
        cmd.append(str(pr_arg))
    cmd.extend(["--json",
        "number,url,state,headRefName,headRefOid,mergeStateStatus,reviewDecision"])
    data = gh_json(cmd)
    if not data:
        die("Could not resolve PR")
    repo = extract_repo(data.get("url", ""))
    return {
        "number": data["number"],
        "url": data.get("url", ""),
        "repo": repo,
        "sha": data.get("headRefOid", ""),
        "branch": data.get("headRefName", ""),
        "state": data.get("state", ""),
    }


def extract_repo(pr_url):
    parts = [p for p in pr_url.split("/") if p]
    for i, p in enumerate(parts):
        if p == "pull" and i >= 2:
            return f"{parts[i-2]}/{parts[i-1]}"
    raw = gh(["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"])
    return raw


# ── CI checks + failure diagnosis ──────────────────────────

def is_bot_check(name):
    return bool(BOT_CHECK_PATTERNS.search(name))


def get_checks(pr_number, repo, head_sha):
    data = gh_json(["pr", "checks", str(pr_number),
                     "--json", "name,state,bucket,link,workflow"],
                    allow_fail=True)
    if not data:
        data = []

    passed, failed, pending_ci, pending_bots = [], [], [], []
    for c in data:
        bucket = (c.get("bucket") or "").lower()
        name = c.get("name", "")
        entry = {"name": name, "link": c.get("link", "")}
        if bucket == "fail":
            failed.append(entry)
        elif bucket == "pass":
            passed.append(entry)
        elif is_bot_check(name):
            pending_bots.append(entry)
        else:
            pending_ci.append(entry)

    if failed:
        failed = diagnose_failures(failed, repo, head_sha)

    passed_bots = [p["name"] for p in passed if is_bot_check(p["name"])]

    return {
        "passed": len(passed),
        "failed": len(failed),
        "pending_ci": len(pending_ci),
        "pending_bots": [p["name"] for p in pending_bots],
        "passed_bots": passed_bots,
        "all_green": len(failed) == 0 and len(pending_ci) == 0,
        "failures": failed,
    }


def diagnose_failures(failed_checks, repo, head_sha):
    """Fetch failed run logs, classify each as branch/flaky, attach excerpt."""
    runs_data = gh_json([
        "api", f"repos/{repo}/actions/runs",
        "-X", "GET", "-f", f"head_sha={head_sha}", "-f", "per_page=100"
    ], allow_fail=True)
    runs = (runs_data or {}).get("workflow_runs", [])

    failed_run_map = {}
    for r in runs:
        if r.get("conclusion") in ("failure", "timed_out", "cancelled"):
            failed_run_map[r.get("name", "")] = r.get("id")

    enriched = []
    for check in failed_checks:
        entry = dict(check)
        run_id = failed_run_map.get(check.get("name"))
        if run_id:
            entry["run_id"] = run_id
            logs = gh(["run", "view", str(run_id), "--log-failed", "-R", repo],
                      allow_fail=True)
            if logs:
                entry["classification"] = "flaky" if FLAKY_RE.search(logs) else "branch"
                lines = logs.strip().split("\n")
                entry["log_excerpt"] = "\n".join(lines[-30:])
            else:
                entry["classification"] = "unknown"
                entry["log_excerpt"] = ""
        else:
            entry["classification"] = "unknown"
            entry["log_excerpt"] = ""
        enriched.append(entry)

    return enriched


# ── Review comments with code context ──────────────────────

def get_all_comments(repo, pr_number):
    """Fetch all PR review comments (not issue comments)."""
    raw_text = gh(["api", "--paginate",
                   f"repos/{repo}/pulls/{pr_number}/comments"], allow_fail=True)
    if not raw_text:
        return []
    try:
        raw = json.loads(raw_text)
    except json.JSONDecodeError:
        return []
    return raw if isinstance(raw, list) else []


def get_new_comments(repo, pr_number, processed_ids, self_login):
    raw = get_all_comments(repo, pr_number)

    new = []
    for c in raw:
        cid = str(c.get("id", ""))
        if not cid or cid in processed_ids:
            continue
        if c.get("in_reply_to_id"):
            continue
        author = (c.get("user") or {}).get("login", "")
        if author == self_login:
            continue

        comment = {
            "id": cid,
            "author": author,
            "body": (c.get("body") or "")[:500],
            "path": c.get("path"),
            "line": c.get("line") or c.get("original_line"),
        }

        diff_hunk = c.get("diff_hunk", "")
        if diff_hunk:
            hunk_lines = diff_hunk.strip().split("\n")
            comment["code_context"] = "\n".join(hunk_lines[-8:])

        new.append(comment)

    return new


def get_self_login():
    try:
        data = gh_json(["api", "user"], allow_fail=True)
        return data.get("login", "") if data else ""
    except SystemExit:
        return ""


# ── Actions recommendation ─────────────────────────────────

def recommend_actions(pr, checks, new_comments, state):
    if pr["state"] in ("CLOSED", "MERGED"):
        return ["stop_pr_closed"]

    actions = []

    if new_comments:
        actions.append("triage_comments")

    if checks["failed"] > 0:
        sha = pr["sha"]
        retries = state.get("retries_by_sha", {}).get(sha, 0)
        all_flaky = all(
            f.get("classification") == "flaky" for f in checks["failures"]
        )
        if retries >= MAX_FLAKY_RETRIES:
            actions.append("stop_exhausted_retries")
        elif all_flaky:
            actions.append("retry_ci")
        else:
            actions.append("fix_ci")

    if not actions:
        # Nothing to fix/triage — what are we waiting on?
        if checks["pending_ci"] > 0:
            actions.append("wait_ci")
        elif checks["pending_bots"]:
            actions.append("wait_review")
        elif checks["all_green"] and not new_comments:
            # Race condition guard: bot check can pass before comments are indexed.
            # If a bot check passed but we've never seen any comments, wait once.
            has_bot_passed = bool(checks.get("passed_bots"))
            ever_seen_comments = len(state.get("processed_comment_ids", [])) > 0
            if has_bot_passed and not ever_seen_comments and state.get("round", 0) <= 1:
                actions.append("wait_review")
            else:
                actions.append("done")

    return actions if actions else ["done"]


# ── Retry failed jobs ──────────────────────────────────────

def retry_failed(pr, state, sp):
    sha = pr["sha"]
    retries = state.get("retries_by_sha", {}).get(sha, 0)
    if retries >= MAX_FLAKY_RETRIES:
        return {"retried": False, "reason": "budget_exhausted"}
    runs_data = gh_json([
        "api", f"repos/{pr['repo']}/actions/runs",
        "-X", "GET", "-f", f"head_sha={sha}", "-f", "per_page=100"
    ], allow_fail=True)
    runs = (runs_data or {}).get("workflow_runs", [])
    failed_ids = [
        r["id"] for r in runs
        if r.get("conclusion") in ("failure", "timed_out", "cancelled")
        and str(r.get("head_sha", "")) == sha
    ]
    if not failed_ids:
        return {"retried": False, "reason": "no_failed_runs"}
    for run_id in failed_ids:
        gh(["run", "rerun", str(run_id), "--failed", "-R", pr["repo"]], allow_fail=True)
    if "retries_by_sha" not in state:
        state["retries_by_sha"] = {}
    state["retries_by_sha"][sha] = retries + 1
    save_state(sp, state)
    return {"retried": True, "count": len(failed_ids), "retries_used": retries + 1}


# ── Wait for new comments ─────────────────────────────────

def wait_for_comments(pr, state, sp, timeout=POLL_TIMEOUT):
    """Poll until new comments appear or timeout."""
    before_count = state.get("last_comment_count", 0)
    start = time.time()
    poll = 0

    while time.time() - start < timeout:
        poll += 1
        time.sleep(POLL_INTERVAL)
        all_comments = get_all_comments(pr["repo"], pr["number"])
        # Count non-reply, non-self comments
        self_login = get_self_login()
        top_level = [c for c in all_comments
                     if not c.get("in_reply_to_id")
                     and (c.get("user") or {}).get("login", "") != self_login]

        if len(top_level) > before_count:
            state["last_comment_count"] = len(top_level)
            save_state(sp, state)
            return {
                "waited": True,
                "polls": poll,
                "elapsed_seconds": int(time.time() - start),
                "new_comments": len(top_level) - before_count,
            }

    return {
        "waited": True,
        "polls": poll,
        "elapsed_seconds": int(time.time() - start),
        "new_comments": 0,
        "timed_out": True,
    }


# ── Main snapshot ──────────────────────────────────────────

def snapshot(pr_arg=None, mark_seen=None, do_retry=False,
             do_reset=False, do_wait=False, wait_timeout=POLL_TIMEOUT):
    pr = resolve_pr(pr_arg)
    sp = state_path(pr["repo"], pr["number"])
    state = load_state(sp)

    if do_reset:
        sp.unlink(missing_ok=True)
        state = load_state(sp)

    if mark_seen:
        seen = set(state.get("processed_comment_ids", []))
        seen.update(mark_seen)
        state["processed_comment_ids"] = sorted(seen)
        save_state(sp, state)

    if do_retry:
        result = retry_failed(pr, state, sp)
        return {"retry_result": result, "pr": {"number": pr["number"], "sha": pr["sha"][:8]}}

    if do_wait:
        wait_result = wait_for_comments(pr, state, sp, timeout=wait_timeout)
        snap = _build_snapshot(pr, state, sp)
        snap["wait_result"] = wait_result
        return snap

    return _build_snapshot(pr, state, sp)


def _build_snapshot(pr, state, sp):
    checks = get_checks(pr["number"], pr["repo"], pr["sha"])
    self_login = get_self_login()
    processed = set(str(x) for x in state.get("processed_comment_ids", []))
    new_comments = get_new_comments(pr["repo"], pr["number"], processed, self_login)

    # Track total comment count for --wait-comments polling
    all_comments = get_all_comments(pr["repo"], pr["number"])
    top_level = [c for c in all_comments
                 if not c.get("in_reply_to_id")
                 and (c.get("user") or {}).get("login", "") != self_login]
    state["last_comment_count"] = len(top_level)

    actions = recommend_actions(pr, checks, new_comments, state)
    state["last_sha"] = pr["sha"]
    state["round"] = state.get("round", 0) + 1
    save_state(sp, state)

    return {
        "pr": {
            "number": pr["number"],
            "url": pr["url"],
            "sha": pr["sha"][:8],
            "branch": pr["branch"],
            "state": pr["state"],
        },
        "ci": checks,
        "round": state["round"],
        "new_comments": new_comments,
        "new_comment_count": len(new_comments),
        "processed_count": len(processed),
        "actions": actions,
        "retries": {
            "used": state.get("retries_by_sha", {}).get(pr["sha"], 0),
            "max": MAX_FLAKY_RETRIES,
        },
        "state_file": str(sp),
    }


# ── CLI ────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Greenlight PR snapshot")
    p.add_argument("pr", nargs="?", help="PR number or URL")
    p.add_argument("--mark-seen", help="Comma-separated comment IDs")
    p.add_argument("--retry-failed", action="store_true", help="Rerun failed CI jobs")
    p.add_argument("--wait-review", action="store_true",
                    help="Poll until new comments appear (from bot re-review or human)")
    p.add_argument("--timeout", type=int, default=POLL_TIMEOUT,
                    help="Timeout for --wait-review in seconds (default 300)")
    p.add_argument("--reset", action="store_true", help="Clear state")
    args = p.parse_args()
    mark = args.mark_seen.split(",") if args.mark_seen else None
    result = snapshot(args.pr, mark, args.retry_failed, args.reset,
                      args.wait_review, args.timeout)
    print(json.dumps(result, indent=2))
