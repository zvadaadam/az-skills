#!/usr/bin/env python3
"""
gl-snapshot v3 — Greenlight PR snapshot tool.

Single-call state gatherer for the greenlight skill. Returns structured JSON
with CI status, review comments (with code context), failure classification,
and recommended actions. Manages persistent state across context compressions.

Usage:
    python3 gl-snapshot.py                      # auto-detect PR from branch
    python3 gl-snapshot.py 7                    # explicit PR number
    python3 gl-snapshot.py --mark-seen 123,456  # mark comment IDs as processed
    python3 gl-snapshot.py --retry-failed       # rerun failed CI jobs (budget: 3/SHA)
    python3 gl-snapshot.py --wait-review        # poll until new bot review appears
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

BOT_PATTERNS = re.compile(r"\[bot\]$|coderabbit|copilot|sonar", re.IGNORECASE)

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
REVIEW_POLL_INTERVAL = 30  # seconds
REVIEW_POLL_TIMEOUT = 300  # 5 minutes


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
        "reviewer_mode": None,
        "last_sha": None,
        "bot_review_count": 0,
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
        "number,url,state,headRefName,headRefOid,reviews,mergeStateStatus,reviewDecision"])
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
        "merge_state": data.get("mergeStateStatus", ""),
        "review_decision": data.get("reviewDecision", ""),
        "reviews": data.get("reviews", []),
    }


def extract_repo(pr_url):
    parts = [p for p in pr_url.split("/") if p]
    for i, p in enumerate(parts):
        if p == "pull" and i >= 2:
            return f"{parts[i-2]}/{parts[i-1]}"
    raw = gh(["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"])
    return raw


# ── CI checks + failure diagnosis ──────────────────────────

def get_checks(pr_number, repo, head_sha):
    data = gh_json(["pr", "checks", str(pr_number),
                     "--json", "name,state,bucket,link,workflow"])
    if not data:
        data = []

    passed, failed, pending = [], [], []
    for c in data:
        bucket = (c.get("bucket") or "").lower()
        entry = {"name": c.get("name", ""), "link": c.get("link", "")}
        if bucket == "fail":
            failed.append(entry)
        elif bucket == "pass":
            passed.append(entry)
        else:
            pending.append(entry)

    # For failed checks, fetch logs and classify
    if failed:
        failed = diagnose_failures(failed, repo, head_sha)

    return {
        "passed_count": len(passed),
        "failed_count": len(failed),
        "pending_count": len(pending),
        "all_green": len(failed) == 0 and len(pending) == 0,
        "failed": failed,
    }


def diagnose_failures(failed_checks, repo, head_sha):
    """Fetch failed run logs, classify each as branch/flaky, attach excerpt."""
    # Get workflow runs for this SHA
    runs_data = gh_json([
        "api", f"repos/{repo}/actions/runs",
        "-X", "GET", "-f", f"head_sha={head_sha}", "-f", "per_page=100"
    ], allow_fail=True)
    runs = (runs_data or {}).get("workflow_runs", [])

    # Map workflow name → run_id for failed runs
    failed_run_map = {}
    for r in runs:
        if r.get("conclusion") in ("failure", "timed_out", "cancelled"):
            name = r.get("name", "")
            failed_run_map[name] = r.get("id")

    enriched = []
    for check in failed_checks:
        entry = dict(check)
        run_id = failed_run_map.get(check.get("name"))
        if run_id:
            entry["run_id"] = run_id
            logs = gh(["run", "view", str(run_id), "--log-failed", "-R", repo],
                      allow_fail=True)
            if logs:
                # Classify
                entry["classification"] = "flaky" if FLAKY_RE.search(logs) else "branch"
                # Attach last 30 lines as excerpt
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


# ── Bot detection ──────────────────────────────────────────

def detect_reviewer_mode(reviews):
    for review in reviews:
        login = review.get("author", {}).get("login", "")
        if BOT_PATTERNS.search(login):
            return "BOT"
    return "SELF"


def count_bot_reviews(reviews):
    return sum(1 for r in reviews
               if BOT_PATTERNS.search(r.get("author", {}).get("login", "")))


# ── Review comments with code context ──────────────────────

def get_new_comments(repo, pr_number, processed_ids, self_login):
    raw_text = gh(["api", "--paginate",
                   f"repos/{repo}/pulls/{pr_number}/comments"], allow_fail=True)
    if not raw_text:
        return []
    try:
        raw = json.loads(raw_text)
    except json.JSONDecodeError:
        return []
    if not isinstance(raw, list):
        return []

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

        # Attach code context: the diff hunk around the comment
        diff_hunk = c.get("diff_hunk", "")
        if diff_hunk:
            # Last 5 lines of the hunk give the relevant context
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
    if checks["failed_count"] > 0:
        sha = pr["sha"]
        retries = state.get("retries_by_sha", {}).get(sha, 0)
        # Check if all failures are flaky
        all_flaky = all(
            f.get("classification") == "flaky" for f in checks["failed"]
        )
        if retries >= MAX_FLAKY_RETRIES:
            actions.append("stop_exhausted_retries")
        elif all_flaky:
            actions.append("retry_ci")
        else:
            actions.append("fix_ci")
    if checks["pending_count"] > 0 and not actions:
        actions.append("wait_ci")
    if checks["all_green"] and not new_comments:
        actions.append("done")
    return actions if actions else ["wait_ci"]


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


# ── Wait for bot re-review ─────────────────────────────────

def wait_for_review(pr, state, sp, timeout=REVIEW_POLL_TIMEOUT):
    """Poll until a new bot review appears or timeout."""
    before_count = state.get("bot_review_count", 0)
    start = time.time()
    poll = 0

    while time.time() - start < timeout:
        poll += 1
        time.sleep(REVIEW_POLL_INTERVAL)
        # Re-fetch PR to get updated reviews
        fresh = resolve_pr(str(pr["number"]))
        current_count = count_bot_reviews(fresh["reviews"])

        if current_count > before_count:
            state["bot_review_count"] = current_count
            save_state(sp, state)
            # Now take a full snapshot to return
            return {
                "waited": True,
                "polls": poll,
                "elapsed_seconds": int(time.time() - start),
                "new_reviews": current_count - before_count,
            }

    return {
        "waited": True,
        "polls": poll,
        "elapsed_seconds": int(time.time() - start),
        "new_reviews": 0,
        "timed_out": True,
    }


# ── Main snapshot ──────────────────────────────────────────

def snapshot(pr_arg=None, mark_seen=None, do_retry=False,
             do_reset=False, do_wait_review=False, wait_timeout=REVIEW_POLL_TIMEOUT):
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

    if do_wait_review:
        wait_result = wait_for_review(pr, state, sp, timeout=wait_timeout)
        # After waiting, take a fresh snapshot
        snap = _build_snapshot(pr, state, sp)
        snap["wait_result"] = wait_result
        return snap

    return _build_snapshot(pr, state, sp)


def _build_snapshot(pr, state, sp):
    if not state.get("reviewer_mode"):
        state["reviewer_mode"] = detect_reviewer_mode(pr["reviews"])

    state["last_sha"] = pr["sha"]
    state["bot_review_count"] = count_bot_reviews(pr["reviews"])

    checks = get_checks(pr["number"], pr["repo"], pr["sha"])
    self_login = get_self_login()
    processed = set(str(x) for x in state.get("processed_comment_ids", []))
    new_comments = get_new_comments(pr["repo"], pr["number"], processed, self_login)
    actions = recommend_actions(pr, checks, new_comments, state)
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
        "mode": state["reviewer_mode"],
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
    p = argparse.ArgumentParser(description="Greenlight PR snapshot v3")
    p.add_argument("pr", nargs="?", help="PR number or URL")
    p.add_argument("--mark-seen", help="Comma-separated comment IDs")
    p.add_argument("--retry-failed", action="store_true", help="Rerun failed CI jobs")
    p.add_argument("--wait-review", action="store_true", help="Poll until new bot review")
    p.add_argument("--timeout", type=int, default=REVIEW_POLL_TIMEOUT,
                   help="Timeout for --wait-review in seconds (default 300)")
    p.add_argument("--reset", action="store_true", help="Clear state")
    args = p.parse_args()
    mark = args.mark_seen.split(",") if args.mark_seen else None
    result = snapshot(args.pr, mark, args.retry_failed, args.reset,
                      args.wait_review, args.timeout)
    print(json.dumps(result, indent=2))
