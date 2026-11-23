#!/usr/bin/env python3
"""pr-state: one JSON snapshot of a pull request, for az-greenlight-pr.

  pr-state.py [PR] [--repo OWNER/NAME] [--wait] [--timeout 540] [--interval 30]

PR is a number, URL, or branch. Omit it to use the current branch's PR.

The snapshot holds the merge-gate verdict (`ready`, `blockers`), the head
commit, failed and pending checks, review threads that need a reply, reviews,
pending review requests, and conversation comments posted since the head
commit. One GraphQL call per snapshot.

--wait polls until something needs attention, then prints a fresh snapshot
with `wake_reason`: the PR closed, the head moved, a check failed, every check
finished, a new review comment, review or comment arrived, a requested bot
review finished, or the branch fell behind or conflicts. After an event it
waits one more interval so a bot's batch of comments arrives together. It
stops with `wake_reason: "timeout"` after --timeout seconds (default 540,
under the common 10-minute command limit).

Exit status: 0 with a snapshot, 1 when GitHub cannot be read, 2 on bad input.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time

QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  viewer { login }
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      number url state isDraft
      author { login }
      baseRefName headRefName headRefOid
      mergeStateStatus reviewDecision
      reviewRequests(first: 20) {
        nodes { requestedReviewer {
          __typename
          ... on Bot { login }
          ... on User { login }
          ... on Mannequin { login }
          ... on Team { slug }
        } }
      }
      latestReviews(first: 50) {
        nodes { author { __typename login } state body submittedAt url commit { oid } }
      }
      comments(last: 30) {
        nodes { author { __typename login } body createdAt url }
      }
      commits(last: 1) {
        nodes { commit { oid committedDate statusCheckRollup { contexts(first: 100) {
          pageInfo { hasNextPage }
          nodes {
            __typename
            ... on CheckRun { name status conclusion detailsUrl isRequired(pullRequestNumber: $number) }
            ... on StatusContext { context state targetUrl isRequired(pullRequestNumber: $number) }
          }
        } } } }
      }
      reviewThreads(first: 100) {
        pageInfo { hasNextPage }
        nodes {
          id isResolved isOutdated path line originalLine
          root: comments(first: 1) { nodes { databaseId author { __typename login } body url } }
          latest: comments(last: 1) { nodes { databaseId author { __typename login } body } }
        }
      }
    }
  }
}
"""

PASSED = {"SUCCESS", "NEUTRAL", "SKIPPED"}
FAILED = {"FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE", "STALE"}
# CI and deploy bots repeat what checks already report; their comments are not review.
NOISE_AUTHORS = re.compile(r"^(github-actions|vercel|netlify|codecov|changeset-bot)", re.I)
PR_URL = re.compile(r"https?://[^/\s]+/([^/\s]+)/([^/\s]+)/pull/(\d+)")
RUN_URL = re.compile(r"/actions/runs/(\d+)")
# Bots wrap findings in icons, collapsed sections and hidden markers. Keep the finding.
MARKUP = re.compile(r"<!--.*?-->|<details>.*?</details>|<picture>.*?</picture>|<img[^>]*>|<source[^>]*>", re.S | re.I)
TAGS = re.compile(r"</?(a|b|br|dd|details|div|dl|dt|em|i|p|span|strong|sub|summary|sup)\b[^>]*>", re.I)


class GhError(Exception):
    pass


def gh(args):
    try:
        proc = subprocess.run(["gh", *args], capture_output=True, text=True)
    except FileNotFoundError:
        raise GhError("the GitHub CLI (`gh`) is not installed") from None
    if proc.returncode != 0:
        raise GhError(proc.stderr.strip() or f"gh {args[0]} failed")
    return proc.stdout


def resolve(pr, repo):
    """Return (owner, name, number) for a PR number, URL, or branch."""
    match = PR_URL.search(pr or "")
    if match:
        return match[1], match[2], int(match[3])
    if repo and pr and pr.isdigit():
        owner, _, name = repo.partition("/")
        return owner, name, int(pr)
    args = ["pr", "view", *([pr] if pr else []), "--json", "url"]
    if repo:
        args += ["--repo", repo]
    match = PR_URL.search(json.loads(gh(args))["url"])
    return match[1], match[2], int(match[3])


def fetch(owner, name, number):
    raw = json.loads(gh([
        "api", "graphql", "-f", f"query={QUERY}",
        "-f", f"owner={owner}", "-f", f"name={name}", "-F", f"number={number}",
    ]))
    pr = ((raw.get("data") or {}).get("repository") or {}).get("pullRequest")
    if not pr:
        errors = "; ".join(e.get("message", "") for e in raw.get("errors", []))
        raise GhError(errors or f"pull request {owner}/{name}#{number} not found")
    return raw["data"]["viewer"]["login"], pr


def clip(text, limit):
    text = TAGS.sub("", MARKUP.sub("", text or ""))
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text if len(text) <= limit else text[:limit].rstrip() + " …[truncated; open the url]"


def who(author):
    author = author or {}
    return author.get("login") or "ghost", author.get("__typename") == "Bot"


def parse_checks(contexts):
    failed, pending, passed = [], [], 0
    for node in contexts:
        if node.get("__typename") == "CheckRun":
            name, url = node.get("name"), node.get("detailsUrl") or ""
            outcome = node.get("conclusion") if node.get("status") == "COMPLETED" else None
        else:
            name, url = node.get("context"), node.get("targetUrl") or ""
            state = node.get("state")
            outcome = None if state in ("PENDING", "EXPECTED") else state
        check = {"name": name, "required": bool(node.get("isRequired"))}
        if outcome is None:
            pending.append(check)
        elif outcome in FAILED:
            run = RUN_URL.search(url)
            failed.append({**check, "conclusion": outcome, "url": url,
                           "run_id": int(run[1]) if run else None})
        elif outcome in PASSED:
            passed += 1
        else:
            pending.append(check)
    return {"failed": failed, "pending": pending, "passed": passed}


def parse_threads(nodes, me):
    needs_reply, answered = [], []
    for node in nodes:
        if node.get("isResolved"):
            continue
        root = (node.get("root") or {}).get("nodes") or [{}]
        latest = (node.get("latest") or {}).get("nodes") or root
        root, latest = root[0], latest[0]
        author, bot = who(root.get("author"))
        last_author, _ = who(latest.get("author"))
        thread = {
            "thread_id": node.get("id"),
            "comment_id": root.get("databaseId"),
            "path": node.get("path"),
            "line": node.get("line") or node.get("originalLine"),
            "author": author,
        }
        if last_author in me:
            answered.append(thread)
            continue
        thread.update({"bot": bot, "outdated": bool(node.get("isOutdated")),
                       "body": clip(root.get("body"), 1500), "url": root.get("url")})
        if latest.get("databaseId") != root.get("databaseId"):
            thread["latest"] = {"author": last_author, "comment_id": latest.get("databaseId"),
                                "body": clip(latest.get("body"), 600)}
        needs_reply.append(thread)
    return needs_reply, answered


def parse(viewer, pr):
    me = {viewer, (pr.get("author") or {}).get("login")}
    commit = ((pr.get("commits") or {}).get("nodes") or [{}])[0].get("commit") or {}
    rollup = (commit.get("statusCheckRollup") or {}).get("contexts") or {}
    threads = pr.get("reviewThreads") or {}
    since = commit.get("committedDate") or ""
    head = pr.get("headRefOid")

    reviews = []
    for node in (pr.get("latestReviews") or {}).get("nodes") or []:
        author, bot = who(node.get("author"))
        if author == viewer:
            continue
        review = {"author": author, "bot": bot, "state": node.get("state"),
                  "on_head": ((node.get("commit") or {}).get("oid")) == head,
                  "submitted_at": node.get("submittedAt")}
        body = clip(node.get("body"), 400)
        if body:
            review["body"] = body
        reviews.append(review)

    requested = {"bots": [], "humans": []}
    for node in (pr.get("reviewRequests") or {}).get("nodes") or []:
        reviewer = node.get("requestedReviewer") or {}
        login = reviewer.get("login") or reviewer.get("slug")
        if login:
            requested["bots" if reviewer.get("__typename") == "Bot" else "humans"].append(login)

    comments = []
    for node in (pr.get("comments") or {}).get("nodes") or []:
        author, bot = who(node.get("author"))
        if author in me or NOISE_AUTHORS.match(author) or (node.get("createdAt") or "") < since:
            continue
        body = clip(node.get("body"), 400)
        if body:
            comments.append({"author": author, "bot": bot, "created_at": node.get("createdAt"),
                             "body": body, "url": node.get("url")})

    needs_reply, answered = parse_threads(threads.get("nodes") or [], me)
    url = PR_URL.search(pr.get("url") or "")
    snap = {
        "ready": False,
        "blockers": [],
        "pr": {
            "repo": f"{url[1]}/{url[2]}" if url else None,
            "number": pr.get("number"), "url": pr.get("url"), "state": pr.get("state"),
            "draft": bool(pr.get("isDraft")), "base": pr.get("baseRefName"),
            "branch": pr.get("headRefName"), "head_sha": head,
            "merge_state": pr.get("mergeStateStatus"), "review_decision": pr.get("reviewDecision"),
        },
        "checks": parse_checks(rollup.get("nodes") or []),
        "threads": {"needs_reply": needs_reply, "answered_unresolved": answered},
        "reviews": reviews,
        "requested_reviewers": requested,
        "comments_since_head": comments,
    }
    truncated = [part for part, conn in (("checks", rollup), ("threads", threads))
                 if (conn.get("pageInfo") or {}).get("hasNextPage")]
    if truncated:
        snap["truncated"] = truncated
    snap["blockers"] = blockers(snap)
    snap["ready"] = not snap["blockers"]
    return snap


def blockers(snap):
    pr, checks = snap["pr"], snap["checks"]
    if pr["state"] != "OPEN":
        return [f"PR is {pr['state'].lower()}"]
    found = []
    if pr["draft"]:
        found.append("PR is a draft")
    if checks["failed"]:
        found.append("failing checks: " + ", ".join(c["name"] for c in checks["failed"]))
    if checks["pending"]:
        found.append("pending checks: " + ", ".join(c["name"] for c in checks["pending"]))
    for bot in snap["requested_reviewers"]["bots"]:
        found.append(f"review requested from {bot} has not arrived")
    if snap["threads"]["needs_reply"]:
        found.append(f"{len(snap['threads']['needs_reply'])} review thread(s) need a reply")
    for review in snap["reviews"]:
        if review["state"] == "CHANGES_REQUESTED" and not review["bot"]:
            found.append(f"{review['author']} requested changes")
    if pr["merge_state"] == "BEHIND":
        found.append("branch is behind its base")
    if pr["merge_state"] == "DIRTY":
        found.append("branch conflicts with its base")
    if pr["review_decision"] == "REVIEW_REQUIRED":
        found.append("a required approval is missing")
    if pr["merge_state"] == "BLOCKED" and not found:
        found.append("branch protection blocks the merge")
    return found


def wake_reason(prev, cur):
    """Why `cur` needs attention compared with the previous poll, or None."""
    if cur["pr"]["state"] != "OPEN":
        return f"PR {cur['pr']['state'].lower()}"
    if cur["pr"]["head_sha"] != prev["pr"]["head_sha"]:
        return "head moved"
    newly_failed = {c["name"] for c in cur["checks"]["failed"]} - {c["name"] for c in prev["checks"]["failed"]}
    if newly_failed:
        return "check failed: " + ", ".join(sorted(newly_failed))
    if prev["checks"]["pending"] and not cur["checks"]["pending"]:
        return "checks finished"

    def replies(snap):
        return {(t["thread_id"], (t.get("latest") or {}).get("comment_id")) for t in snap["threads"]["needs_reply"]}

    if replies(cur) - replies(prev):
        return "new review comment"
    if {(r["author"], r["submitted_at"]) for r in cur["reviews"]} - {(r["author"], r["submitted_at"]) for r in prev["reviews"]}:
        return "new review"
    if {c["url"] for c in cur["comments_since_head"]} - {c["url"] for c in prev["comments_since_head"]}:
        return "new comment"
    finished = set(prev["requested_reviewers"]["bots"]) - set(cur["requested_reviewers"]["bots"])
    if finished:
        return "bot review finished: " + ", ".join(sorted(finished))
    state = cur["pr"]["merge_state"]
    if state in ("BEHIND", "DIRTY") and state != prev["pr"]["merge_state"]:
        return "branch is behind its base" if state == "BEHIND" else "branch conflicts with its base"
    return None


def wait(take, timeout, interval):
    deadline = time.monotonic() + timeout
    prev = take()
    if prev["pr"]["state"] != "OPEN":
        return {"wake_reason": f"PR {prev['pr']['state'].lower()}", **prev}
    failures = 0
    while time.monotonic() < deadline:
        time.sleep(max(0.0, min(interval, deadline - time.monotonic())))
        try:
            cur = take()
        except GhError as error:
            failures += 1
            if failures >= 5:
                raise
            print(f"pr-state: retrying after error: {error}", file=sys.stderr)
            continue
        failures = 0
        reason = wake_reason(prev, cur)
        if reason:
            if cur["pr"]["state"] == "OPEN":
                time.sleep(interval)
                try:
                    cur = take()
                except GhError:
                    pass
            return {"wake_reason": reason, **cur}
        prev = cur
    return {"wake_reason": "timeout", **prev}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Snapshot a pull request for az-greenlight-pr.")
    parser.add_argument("pr", nargs="?", help="PR number, URL, or branch (default: current branch)")
    parser.add_argument("--repo", help="OWNER/NAME when PR is a bare number outside the repo")
    parser.add_argument("--wait", action="store_true", help="block until something needs attention")
    parser.add_argument("--timeout", type=int, default=540, help="seconds --wait may block (default 540)")
    parser.add_argument("--interval", type=int, default=30, help="seconds between polls (default 30)")
    args = parser.parse_args(argv)
    if args.timeout < 1 or args.interval < 1:
        parser.error("--timeout and --interval must be positive")
    try:
        owner, name, number = resolve(args.pr, args.repo)
        take = lambda: parse(*fetch(owner, name, number))  # noqa: E731
        result = wait(take, args.timeout, args.interval) if args.wait else take()
    except GhError as error:
        print(f"pr-state: {error}", file=sys.stderr)
        return 1
    except (ValueError, KeyError, TypeError) as error:
        print(f"pr-state: unexpected response from GitHub: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
