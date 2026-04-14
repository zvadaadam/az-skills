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
| `--wait-review` | Poll until new bot review appears (timeout: 5min) |
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
    gl-snapshot.py --wait-review    # wait for bot to re-review
    goto snapshot

  if "wait_review" in actions:
    gl-snapshot.py --wait-review    # bot is reviewing (e.g. CodeRabbit pending)
    goto snapshot                   # will have comments to triage after

  if "wait_ci" in actions:
    gh pr checks [PR] --watch --fail-fast
    goto snapshot

  if "done" in actions:
    return "CI green, no new comments — merge-ready"
```

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
