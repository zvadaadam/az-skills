---
name: greenlight-pr
description: Greenlight a PR — fix CI failures, triage review comments, iterate until green.
argument-hint: "[PR number or URL]"
---

# Greenlight PR

Drive a PR to green — fix CI, address AI code reviews, iterate until merge-ready.

**You are the decision-maker, not the reviewer.** AI review bots do the reviewing. You evaluate their feedback, decide what's worth fixing, fix it well, and iterate until clean.

## Tool

```bash
python3 ~/.claude/skills/greenlight-pr/scripts/gl-snapshot.py [PR]
```

Returns structured JSON: CI status, review comments (with code context), and recommended `actions`. State persists in `/tmp/gl-{repo}-pr{N}.json`.

| Flag | Purpose |
|------|---------|
| `7` | Explicit PR number |
| `--mark-seen 123,456` | Mark comment IDs as processed |
| `--retry-failed` | Rerun failed CI jobs (budget: 3/SHA) |
| `--wait-review` | Poll until new comments appear (timeout: 5min) |
| `--timeout 120` | Custom timeout for `--wait-review` |
| `--reset` | Clear state for fresh start |

## Main Loop

```
snapshot = gl-snapshot.py [PR]
actions = snapshot.actions

loop:
  if "stop_pr_closed" in actions:
    return "PR merged or closed"

  if "stop_exhausted_retries" in actions:
    return "CI retries exhausted — ask user"

  if "fix_ci" in actions:
    for each check in snapshot.ci.failed:
      if check.classification == "branch":
        read check.log_excerpt
        find the failure cause in the code
        fix it
    commit → push
    goto snapshot

  if "retry_ci" in actions:
    gl-snapshot.py --retry-failed
    gh pr checks [PR] --watch --fail-fast
    goto snapshot

  if "triage_comments" in actions:
    run TRIAGE PROCESS (see references/triage-process.md)
    push fixes
    gh pr checks [PR] --watch --fail-fast   # wait for CI first
    gl-snapshot.py --wait-review             # then wait for bot re-review
    goto snapshot                            # fresh snapshot picks up new comments

  if "wait_review" in actions:
    gl-snapshot.py --wait-review    # bot still reviewing (e.g. CodeRabbit pending)
    goto snapshot

  if "wait_ci" in actions:
    gh pr checks [PR] --watch --fail-fast
    goto snapshot

  if "done" in actions:
    return "CI green, no new comments — merge-ready"
```

## Happy Path Example

Concrete commands for the most common flow: bot posts comments → triage → fix → re-review.

```bash
# 1. Snapshot
python3 ~/.claude/skills/greenlight-pr/scripts/gl-snapshot.py 42
# → actions: ["triage_comments"], new_comments: [{id: "123", body: "...", code_context: "..."}]

# 2. Triage (see references/triage-process.md)
#    Read comments, spawn sub-agents, decide FIX/DISAGREE/DEFER
#    Fix the code...

# 3. Commit and push
git add -A && git commit -m "Address review: fix X, Y" && git push

# 4. Reply to each comment
gh api repos/owner/repo/pulls/42/comments/123/replies -f body="Fixed — description. See abc1234"

# 5. Post round summary
gh pr comment 42 --body "## Greenlight — Round 1
**Fixed (2):** X, Y
**Disagreed (1):** Z — reasoning"

# 6. Mark as seen
python3 ~/.claude/skills/greenlight-pr/scripts/gl-snapshot.py --mark-seen 123,456,789

# 7. Wait for bot re-review, then re-snapshot
gh pr checks 42 --watch --fail-fast
python3 ~/.claude/skills/greenlight-pr/scripts/gl-snapshot.py --wait-review
python3 ~/.claude/skills/greenlight-pr/scripts/gl-snapshot.py 42
# → new round: check actions again
```

## What counts as a comment

The snapshot only returns **inline review comments** with `code_context` (the diff hunk). It ignores:
- Big walkthrough/summary comments that bots post at the top of the PR
- Issue-level comments (not attached to a line of code)
- Your own replies

If CodeRabbit auto-marks a comment as "Addressed in commit X", you don't need to reply again unless you want an audit trail.

## Recovery after interruption

State persists in `/tmp/gl-{repo}-pr{N}.json`. If a session is interrupted, just re-run the snapshot — it picks up where you left off with all processed comment IDs intact.

## Triage Process (overview)

The full process with sub-agent prompts and decision trees is in `references/triage-process.md`. Summary:

```
Phase 1 — EVALUATE
  spawn sub-agents to evaluate each comment
  each returns: verdict (FIX/DISAGREE/DEFER) + reasoning + confidence

Phase 2 — SYNTHESIZE
  collect sub-agent results
  resolve conflicts (agents may disagree)
  filter: only HIGH/MEDIUM confidence FIXes that pass quality check

Phase 3 — ACT
  implement fixes (one commit, grouped)
  reply to every comment individually
  post round summary as PR comment
  gl-snapshot.py --mark-seen <ids>
```

## Guardrails

- **Think before fixing.** Don't blindly apply every bot suggestion.
- **No workarounds.** If you can't fix it properly, disagree or defer.
- **No over-engineering.** Push back on suggestions that add complexity without solving real problems.
- **Always reply.** Every inline comment gets a reply. Every round gets a summary.
- **Wait for re-review.** After every push, `--wait-review` then re-snapshot.
- **Know when to stop.** 3+ rounds of only nit/duplicate comments → done.
- **Escalate.** Product decisions → stop and ask user.

## References

- `references/triage-process.md` — Sub-agent prompts, decision pseudocode, quality checks, reply templates
- `references/ci-classification.md` — Branch vs flaky heuristics
- `references/known-bots.md` — AI review bot catalog and re-review patterns
