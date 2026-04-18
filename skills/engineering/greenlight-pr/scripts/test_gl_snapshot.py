#!/usr/bin/env python3
"""Tests for gl-snapshot.py — pure function tests, no network calls."""

import importlib.util
import json
from pathlib import Path

import pytest

# Import the module
MODULE_PATH = Path(__file__).with_name("gl-snapshot.py")
spec = importlib.util.spec_from_file_location("gl_snapshot", MODULE_PATH)
gl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gl)


# ── Fixtures ───────────────────────────────────────────────

def sample_pr(**overrides):
    pr = {
        "number": 7, "url": "https://github.com/test/repo/pull/7",
        "repo": "test/repo", "sha": "abc12345", "branch": "feature",
        "state": "OPEN", "merge_state": "CLEAN", "review_decision": "",
        "reviews": [],
    }
    pr.update(overrides)
    return pr


def sample_checks(**overrides):
    checks = {
        "passed": 3, "failed": 0, "pending_ci": 0,
        "pending_bots": [], "passed_bots": [],
        "all_green": True, "failures": [],
    }
    checks.update(overrides)
    return checks


# ── Action recommendation tests ────────────────────────────

class TestRecommendActions:
    def test_done_when_green_no_comments(self):
        actions = gl.recommend_actions(
            sample_pr(), sample_checks(), [], {"retries_by_sha": {}}
        )
        assert actions == ["done"]

    def test_triage_when_new_comments(self):
        actions = gl.recommend_actions(
            sample_pr(), sample_checks(),
            [{"id": "1", "body": "fix this"}], {"retries_by_sha": {}}
        )
        assert actions == ["triage_comments"]

    def test_fix_ci_when_branch_failure(self):
        actions = gl.recommend_actions(
            sample_pr(),
            sample_checks(failed=1, all_green=False,
                          failures=[{"name": "Build", "classification": "branch"}]),
            [], {"retries_by_sha": {}}
        )
        assert "fix_ci" in actions

    def test_retry_ci_when_all_flaky(self):
        actions = gl.recommend_actions(
            sample_pr(),
            sample_checks(failed=2, all_green=False, failures=[
                {"name": "Build", "classification": "flaky"},
                {"name": "Lint", "classification": "flaky"},
            ]),
            [], {"retries_by_sha": {}}
        )
        assert "retry_ci" in actions

    def test_fix_ci_when_mixed_failures(self):
        actions = gl.recommend_actions(
            sample_pr(),
            sample_checks(failed=2, all_green=False, failures=[
                {"name": "Build", "classification": "branch"},
                {"name": "Lint", "classification": "flaky"},
            ]),
            [], {"retries_by_sha": {}}
        )
        assert "fix_ci" in actions
        assert "retry_ci" not in actions

    def test_stop_when_retries_exhausted(self):
        actions = gl.recommend_actions(
            sample_pr(),
            sample_checks(failed=1, all_green=False,
                          failures=[{"name": "Build", "classification": "flaky"}]),
            [], {"retries_by_sha": {"abc12345": 3}}
        )
        assert "stop_exhausted_retries" in actions

    def test_stop_when_pr_closed(self):
        actions = gl.recommend_actions(
            sample_pr(state="CLOSED"), sample_checks(), [], {}
        )
        assert actions == ["stop_pr_closed"]

    def test_triage_takes_priority_over_ci(self):
        actions = gl.recommend_actions(
            sample_pr(),
            sample_checks(failed=1, all_green=False,
                          failures=[{"name": "Build", "classification": "branch"}]),
            [{"id": "1", "body": "fix this"}],
            {"retries_by_sha": {}}
        )
        assert actions[0] == "triage_comments"

    def test_wait_ci_when_pending(self):
        actions = gl.recommend_actions(
            sample_pr(),
            sample_checks(pending_ci=2, all_green=False),
            [], {"retries_by_sha": {}}
        )
        assert actions == ["wait_ci"]

    def test_wait_review_when_bots_pending(self):
        actions = gl.recommend_actions(
            sample_pr(),
            sample_checks(pending_bots=["coderabbitai"]),
            [], {"retries_by_sha": {}}
        )
        assert actions == ["wait_review"]


# ── Bot detection tests ────────────────────────────────────

class TestBotDetection:
    def test_detects_coderabbit(self):
        assert gl.is_bot_check("coderabbitai")

    def test_detects_copilot(self):
        assert gl.is_bot_check("copilot-review")

    def test_detects_sonarcloud(self):
        assert gl.is_bot_check("SonarCloud Code Analysis")

    def test_does_not_match_normal_check(self):
        assert not gl.is_bot_check("Build")
        assert not gl.is_bot_check("lint")
        assert not gl.is_bot_check("test-unit")


# ── Flaky detection tests ─────────────────────────────────

class TestFlakyDetection:
    def test_detects_timeout(self):
        assert gl.FLAKY_RE.search("Error: connection timed out after 30s")

    def test_detects_dns(self):
        assert gl.FLAKY_RE.search("Could not resolve host: registry.npmjs.org")

    def test_detects_rate_limit(self):
        assert gl.FLAKY_RE.search("HTTP 429 Too Many Requests")

    def test_does_not_match_normal_error(self):
        assert not gl.FLAKY_RE.search("error: cannot find type 'Foo' in scope")

    def test_does_not_match_test_failure(self):
        assert not gl.FLAKY_RE.search("XCTAssertEqual failed: 3 is not equal to 4")


# ── State management tests ─────────────────────────────────

class TestState:
    def test_fresh_state(self, tmp_path):
        state = gl.load_state(tmp_path / "nonexistent.json")
        assert state["round"] == 0
        assert state["processed_comment_ids"] == []

    def test_save_and_load(self, tmp_path):
        sp = tmp_path / "state.json"
        state = {"round": 3, "processed_comment_ids": ["1", "2"],
                 "retries_by_sha": {}, "last_sha": "abc", "last_comment_count": 5}
        gl.save_state(sp, state)
        loaded = gl.load_state(sp)
        assert loaded["round"] == 3
        assert loaded["processed_comment_ids"] == ["1", "2"]

    def test_corrupt_state_returns_fresh(self, tmp_path):
        sp = tmp_path / "state.json"
        sp.write_text("not json{{{")
        state = gl.load_state(sp)
        assert state["round"] == 0


# ── Repo extraction tests ─────────────────────────────────

class TestExtractRepo:
    def test_extracts_from_pr_url(self):
        assert gl.extract_repo("https://github.com/owner/repo/pull/7") == "owner/repo"

    def test_extracts_from_full_url(self):
        url = "https://github.com/zvadaadam/opendevs-mobile/pull/7"
        assert gl.extract_repo(url) == "zvadaadam/opendevs-mobile"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
