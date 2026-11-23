#!/usr/bin/env python3
"""Tests for pr-state.py. No network: GitHub responses are fixtures.

Run: python3 -m unittest discover -s skills/engineering/az-greenlight-pr/scripts
"""

import copy
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("pr_state", Path(__file__).with_name("pr-state.py"))
pr_state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pr_state)

HEAD = "a" * 40


def check_run(name, status="COMPLETED", conclusion="SUCCESS", required=False, url=""):
    return {"__typename": "CheckRun", "name": name, "status": status, "conclusion": conclusion,
            "detailsUrl": url, "isRequired": required}


def thread(tid, root_author="coderabbitai", bot=True, last_author=None, resolved=False):
    root = {"databaseId": int(tid[1:]), "author": {"__typename": "Bot" if bot else "User", "login": root_author},
            "body": "<!-- marker -->**Null check missing.**", "url": f"https://github.com/o/r/pull/7#{tid}"}
    latest = root if last_author is None else {
        "databaseId": int(tid[1:]) + 1000, "author": {"__typename": "User", "login": last_author}, "body": "reply"}
    return {"id": tid, "isResolved": resolved, "isOutdated": False, "path": "src/a.py", "line": 3,
            "originalLine": 3, "root": {"nodes": [root]}, "latest": {"nodes": [latest]}}


def pull(**overrides):
    pr = {
        "number": 7, "url": "https://github.com/o/r/pull/7", "state": "OPEN", "isDraft": False,
        "author": {"login": "me"}, "baseRefName": "main", "headRefName": "feature", "headRefOid": HEAD,
        "mergeStateStatus": "CLEAN", "reviewDecision": None,
        "reviewRequests": {"nodes": []},
        "latestReviews": {"nodes": []},
        "comments": {"nodes": []},
        "commits": {"nodes": [{"commit": {"oid": HEAD, "committedDate": "2026-11-21T10:00:00Z",
                                          "statusCheckRollup": {"contexts": {"pageInfo": {"hasNextPage": False},
                                                                             "nodes": [check_run("build")]}}}}]},
        "reviewThreads": {"pageInfo": {"hasNextPage": False}, "nodes": []},
    }
    pr.update(overrides)
    return pr


def with_checks(*nodes, **overrides):
    pr = pull(**overrides)
    pr["commits"]["nodes"][0]["commit"]["statusCheckRollup"]["contexts"]["nodes"] = list(nodes)
    return pr


def snap(pr):
    return pr_state.parse("me", pr)


class ParseTests(unittest.TestCase):
    def test_green_pr_is_ready(self):
        result = snap(pull())
        self.assertTrue(result["ready"])
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["checks"]["passed"], 1)

    def test_check_outcomes(self):
        result = snap(with_checks(
            check_run("build"),
            check_run("lint", conclusion="SKIPPED"),
            check_run("test", conclusion="FAILURE", required=True,
                      url="https://github.com/o/r/actions/runs/123/job/456"),
            check_run("e2e", status="IN_PROGRESS", conclusion=None),
            {"__typename": "StatusContext", "context": "ci/circle", "state": "ERROR", "targetUrl": "https://circleci.com/x"},
            {"__typename": "StatusContext", "context": "deploy", "state": "PENDING", "targetUrl": ""},
        ))
        checks = result["checks"]
        self.assertEqual(checks["passed"], 2)
        self.assertEqual([(c["name"], c["run_id"], c["required"]) for c in checks["failed"]],
                         [("test", 123, True), ("ci/circle", None, False)])
        self.assertEqual([c["name"] for c in checks["pending"]], ["e2e", "deploy"])
        self.assertIn("failing checks: test, ci/circle", result["blockers"])
        self.assertIn("pending checks: e2e, deploy", result["blockers"])
        self.assertFalse(result["ready"])

    def test_threads_split_by_who_spoke_last(self):
        result = snap(pull(reviewThreads={"pageInfo": {"hasNextPage": False}, "nodes": [
            thread("t1"),                                   # bot finding, no reply yet
            thread("t2", last_author="me"),                 # we answered
            thread("t3", resolved=True),                    # done
            thread("t4", root_author="alice", bot=False, last_author="alice"),
        ]}))
        needs = result["threads"]["needs_reply"]
        self.assertEqual([t["thread_id"] for t in needs], ["t1", "t4"])
        self.assertEqual(needs[0]["comment_id"], 1)
        self.assertEqual(needs[0]["body"], "**Null check missing.**")
        self.assertTrue(needs[0]["bot"])
        self.assertNotIn("latest", needs[0])
        self.assertEqual(needs[1]["latest"]["author"], "alice")
        self.assertEqual([t["thread_id"] for t in result["threads"]["answered_unresolved"]], ["t2"])
        self.assertIn("2 review thread(s) need a reply", result["blockers"])

    def test_reviews_requests_and_comments(self):
        result = snap(pull(
            reviewDecision="CHANGES_REQUESTED",
            latestReviews={"nodes": [
                {"author": {"__typename": "User", "login": "alice"}, "state": "CHANGES_REQUESTED",
                 "body": "Split this.", "submittedAt": "2026-11-21T11:00:00Z", "commit": {"oid": HEAD}},
                {"author": {"__typename": "Bot", "login": "sourcery-ai"}, "state": "CHANGES_REQUESTED",
                 "body": "", "submittedAt": "2026-11-21T09:00:00Z", "commit": {"oid": "b" * 40}},
                {"author": {"__typename": "User", "login": "me"}, "state": "COMMENTED", "body": "x",
                 "submittedAt": "2026-11-21T11:30:00Z", "commit": {"oid": HEAD}},
            ]},
            reviewRequests={"nodes": [
                {"requestedReviewer": {"__typename": "Bot", "login": "copilot-pull-request-reviewer"}},
                {"requestedReviewer": {"__typename": "Team", "slug": "core"}},
            ]},
            comments={"nodes": [
                {"author": {"__typename": "Bot", "login": "claude"}, "body": "Found a bug in a.py",
                 "createdAt": "2026-11-21T10:05:00Z", "url": "u1"},
                {"author": {"__typename": "Bot", "login": "github-actions"}, "body": "Coverage 90%",
                 "createdAt": "2026-11-21T10:06:00Z", "url": "u2"},
                {"author": {"__typename": "User", "login": "bob"}, "body": "old comment",
                 "createdAt": "2026-11-20T10:00:00Z", "url": "u3"},
                {"author": {"__typename": "Bot", "login": "coderabbitai"}, "body": "<details>x</details><img src=y>",
                 "createdAt": "2026-11-21T10:07:00Z", "url": "u4"},
            ]},
        ))
        self.assertEqual([(r["author"], r["on_head"]) for r in result["reviews"]],
                         [("alice", True), ("sourcery-ai", False)])
        self.assertNotIn("body", result["reviews"][1])
        self.assertEqual(result["requested_reviewers"],
                         {"bots": ["copilot-pull-request-reviewer"], "humans": ["core"]})
        self.assertEqual([c["url"] for c in result["comments_since_head"]], ["u1"])
        self.assertIn("alice requested changes", result["blockers"])
        self.assertNotIn("sourcery-ai requested changes", result["blockers"])
        self.assertIn("review requested from copilot-pull-request-reviewer has not arrived", result["blockers"])

    def test_merge_state_and_draft(self):
        self.assertEqual(snap(pull(state="MERGED"))["blockers"], ["PR is merged"])
        self.assertEqual(snap(pull(isDraft=True))["blockers"], ["PR is a draft"])
        self.assertEqual(snap(pull(mergeStateStatus="BEHIND"))["blockers"], ["branch is behind its base"])
        self.assertEqual(snap(pull(mergeStateStatus="DIRTY"))["blockers"], ["branch conflicts with its base"])
        self.assertEqual(snap(pull(mergeStateStatus="BLOCKED", reviewDecision="REVIEW_REQUIRED"))["blockers"],
                         ["a required approval is missing"])
        self.assertEqual(snap(pull(mergeStateStatus="BLOCKED"))["blockers"], ["branch protection blocks the merge"])

    def test_truncation_is_reported(self):
        pr = pull()
        pr["reviewThreads"]["pageInfo"]["hasNextPage"] = True
        self.assertEqual(snap(pr)["truncated"], ["threads"])
        self.assertNotIn("truncated", snap(pull()))


class ClipTests(unittest.TestCase):
    def test_strips_bot_markup(self):
        body = ('**<picture><img src="i.svg"></picture> Minor**\n\n\n\nReal finding.\n'
                '<details><summary>Prompt</summary>long</details><!-- fingerprint -->')
        self.assertEqual(pr_state.clip(body, 100), "** Minor**\n\nReal finding.")

    def test_truncates_long_text(self):
        self.assertTrue(pr_state.clip("x" * 50, 10).startswith("x" * 10 + " …[truncated"))


class WakeTests(unittest.TestCase):
    def wake(self, before, after):
        return pr_state.wake_reason(snap(before), snap(after))

    def test_nothing_changed(self):
        self.assertIsNone(self.wake(pull(), pull()))

    def test_closed_and_head_moved(self):
        self.assertEqual(self.wake(pull(), pull(state="CLOSED")), "PR closed")
        self.assertEqual(self.wake(pull(), pull(headRefOid="c" * 40)), "head moved")

    def test_check_transitions(self):
        pending = with_checks(check_run("test", status="IN_PROGRESS", conclusion=None))
        failed = with_checks(check_run("test", conclusion="FAILURE"))
        self.assertEqual(self.wake(pending, failed), "check failed: test")
        self.assertEqual(self.wake(pending, pull()), "checks finished")
        self.assertIsNone(self.wake(failed, failed))
        # A rerun that fails again is news: pending in between, failed now.
        self.assertEqual(self.wake(pending, failed), "check failed: test")

    def test_new_review_activity(self):
        threads = lambda *nodes: {"pageInfo": {"hasNextPage": False}, "nodes": list(nodes)}
        self.assertEqual(self.wake(pull(), pull(reviewThreads=threads(thread("t1")))), "new review comment")
        # The bot answered our reply: the thread needs us again.
        self.assertEqual(self.wake(pull(reviewThreads=threads(thread("t1", last_author="me"))),
                                   pull(reviewThreads=threads(thread("t1", last_author="coderabbitai")))),
                         "new review comment")
        review = {"author": {"__typename": "User", "login": "alice"}, "state": "APPROVED", "body": "",
                  "submittedAt": "2026-11-21T12:00:00Z", "commit": {"oid": HEAD}}
        self.assertEqual(self.wake(pull(), pull(latestReviews={"nodes": [review]})), "new review")
        comment = {"author": {"__typename": "User", "login": "bob"}, "body": "hm",
                   "createdAt": "2026-11-21T12:00:00Z", "url": "u1"}
        self.assertEqual(self.wake(pull(), pull(comments={"nodes": [comment]})), "new comment")

    def test_bot_review_finished_and_merge_state(self):
        requested = pull(reviewRequests={"nodes": [
            {"requestedReviewer": {"__typename": "Bot", "login": "copilot-pull-request-reviewer"}}]})
        self.assertEqual(self.wake(requested, pull()), "bot review finished: copilot-pull-request-reviewer")
        self.assertEqual(self.wake(pull(), pull(mergeStateStatus="DIRTY")), "branch conflicts with its base")
        behind = pull(mergeStateStatus="BEHIND")
        self.assertIsNone(self.wake(behind, copy.deepcopy(behind)))


class WaitTests(unittest.TestCase):
    def setUp(self):
        self.sleep = pr_state.time.sleep
        pr_state.time.sleep = lambda seconds: None
        self.addCleanup(setattr, pr_state.time, "sleep", self.sleep)

    def test_returns_settled_snapshot_with_reason(self):
        states = iter([
            snap(with_checks(check_run("test", status="IN_PROGRESS", conclusion=None))),
            snap(pull()),
            snap(pull(headRefName="settled")),
        ])
        result = pr_state.wait(lambda: next(states), timeout=60, interval=1)
        self.assertEqual(result["wake_reason"], "checks finished")
        self.assertEqual(result["pr"]["branch"], "settled")

    def test_closed_pr_returns_at_once(self):
        result = pr_state.wait(lambda: snap(pull(state="MERGED")), timeout=60, interval=1)
        self.assertEqual(result["wake_reason"], "PR merged")

    def test_retries_errors_then_gives_up(self):
        calls = {"n": 0}

        def take():
            calls["n"] += 1
            if calls["n"] == 1:
                return snap(pull())
            raise pr_state.GhError("rate limited")

        with self.assertRaises(pr_state.GhError):
            pr_state.wait(take, timeout=60, interval=1)
        self.assertEqual(calls["n"], 6)


class ResolveTests(unittest.TestCase):
    def test_url_and_number_with_repo(self):
        self.assertEqual(pr_state.resolve("https://github.com/o/r/pull/42", None), ("o", "r", 42))
        self.assertEqual(pr_state.resolve("42", "o/r"), ("o", "r", 42))


if __name__ == "__main__":
    unittest.main()
