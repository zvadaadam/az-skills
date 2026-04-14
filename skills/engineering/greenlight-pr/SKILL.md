---
name: greenlight-pr
description: Greenlight a PR — fix CI failures, triage review comments, iterate until green.
argument-hint: "[PR number or URL]"
---

# Greenlight PR

Babysit a PR to merge-ready. Fix CI, triage AI code review comments, iterate until green.

**You are the decision-maker, not the reviewer.** AI code review bots (CodeRabbit, Graphite, Codex, etc.) do the reviewing. Your job is to watch their feedback, decide what's worth fixing, fix it well, and keep iterating until the PR is clean.

## Tool

```bash
python3 ~/.claude/skills/greenlight-pr/scripts/gl-snapshot.py [PR]
```

One call returns structured JSON: CI status (with failure classification + log excerpts), review comments (with diff hunk context), and recommended `actions`.

State persists in `/tmp/gl-{repo}-pr{N}.json` — survives context compression.

| Flag | Purpose |
|------|---------|
| `7` | Explicit PR number |
| `--mark-seen 123,456` | Mark comment IDs as processed |
| `--retry-failed` | Rerun failed CI jobs (budget: 3/SHA) |
| `--wait-review` | Poll until new bot review appears (timeout: 5min) |
| `--timeout 120` | Custom timeout for `--wait-review` |
| `--reset` | Clear state for fresh start |

## Actions

| Action | Do this |
|--------|---------|
| `fix_ci` | Failed checks diagnosed as branch-related — fix using `log_excerpt` + `classification` |
| `retry_ci` | All failures classified as flaky — `--retry-failed` (budget: 3) |
| `triage_comments` | New bot comments with `code_context` — triage per decision process below |
| `wait_ci` | `gh pr checks <pr> --watch --fail-fast`, then re-snapshot |
| `done` | CI green + no new comments → report final state |
| `stop_pr_closed` | PR merged/closed → stop |
| `stop_exhausted_retries` | 3 retries used → report to user |

## Workflow

```
snapshot → read actions
  │
  ├─ fix_ci?       → read failed[].classification + log_excerpt → fix → commit → push
  ├─ retry_ci?     → --retry-failed
  ├─ triage?       → TRIAGE LOOP (see below)
  ├─ wait_ci?      → gh pr checks --watch → re-snapshot
  └─ done?         → report final state

TRIAGE LOOP:
  1. Read new_comments[].body + code_context
  2. Spawn sub-agents to evaluate each comment (see Decision Process)
  3. Build triage report: Fix / Disagree / Defer
  4. Implement fixes (one commit, grouped)
  5. Reply to every comment + post round summary
  6. --mark-seen <ids>
  7. Push
  8. --wait-review → re-snapshot
  9. New comments? → goto 1
  10. No new comments + CI green → done
```

### Bot re-review cycle

AI review bots re-review after each push. The pattern:

```
you push fix → bot posts new review → may add NEW comments
                                      even if status = "approved"
```

**Always `--wait-review` after pushing, then re-snapshot.** Don't assume "approved" means no new comments. Bots often approve the overall PR but still leave new inline suggestions in the same pass.

After 3+ rounds with only nit/duplicate comments, finish.

## Decision Process

This is the core of greenlight-pr. For each batch of bot comments, decide what to do.

### Step 1: Classify each comment

```
for each comment:
  read comment.body + comment.code_context
  │
  ├─ Is it technically correct?
  │   no  → DISAGREE (explain with evidence)
  │
  ├─ Is it actionable in this branch?
  │   no  → DEFER (acknowledge, explain scope)
  │
  ├─ Does fixing it conflict with the user's intent?
  │   yes → DEFER (explain why we chose this approach)
  │
  ├─ Would the fix be a workaround or band-aid?
  │   yes → think harder — find the RIGHT fix or DISAGREE
  │
  ├─ Would the fix add unnecessary complexity?
  │   yes → DISAGREE (simpler is better unless there's a real bug)
  │
  └─ else → FIX
```

### Step 2: Validate fixes before implementing

```
for each FIX decision:
  │
  ├─ Is this a real bug or correctness issue?
  │   yes → fix it, high priority
  │
  ├─ Is this a maintainability improvement?
  │   yes → fix it if it's clean and simple
  │
  ├─ Is this a style/preference nit?
  │   yes → skip unless trivial (rename, formatting)
  │
  ├─ Would this fix require touching unrelated code?
  │   yes → DEFER instead
  │
  └─ Does this fix introduce more complexity than the issue it solves?
      yes → DISAGREE instead
```

### Step 3: Quality check on the fix itself

```
before committing any fix:
  │
  ├─ Is this the simplest correct fix?
  │   no  → simplify
  │
  ├─ Does it introduce new abstractions?
  │   yes → does the abstraction earn its keep? if not, inline it
  │
  ├─ Is it a workaround that hides the real problem?
  │   yes → fix the real problem or DISAGREE
  │
  └─ Would a senior engineer approve this in code review?
      no  → rethink
```

## Known AI Review Bots

The snapshot script detects these automatically. When detected, `mode` = `"BOT"`.

| Bot | GitHub login pattern | How it works |
|-----|---------------------|--------------|
| **CodeRabbit** | `coderabbitai[bot]` | PR summary + inline comments. Re-reviews on push. Resolves its own outdated comments. |
| **Graphite** | `graphite-app[bot]` | Inline comments + summary. Re-reviews automatically. |
| **Copilot Review** | `copilot-pull-request-review[bot]` | GitHub-native. Must re-request review after push. |
| **Sourcery** | `sourcery-ai[bot]` | Inline suggestions + quality score. Can APPROVE or REQUEST_CHANGES (rare — most bots only COMMENT). |
| **SonarCloud** | `sonarcloud[bot]` | Quality gate status check + inline comments. |
| **Qodo / PR-Agent** | `qodo-merge-pro[bot]` | PR descriptions, review comments, test generation. Trigger with `/review`. |
| **CodeGuru** | `aws-codeguru-reviewer[bot]` | Security + concurrency focus. Java/Python. |
| **CodeScene** | `codescene[bot]` | Code health via status checks (pass/fail), not inline reviews. |

If no bot is detected (`mode` = `"SELF"`), the PR has no automated reviewer. Report this to the user — they may want to set one up. **Do not run a self-review.** Greenlight-pr is the babysitter, not the reviewer.

## After every triage round

```bash
# 1. Reply to each comment individually
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies \
  -f body="Fixed — <description>. See <commit>"

# 2. Post round summary
gh pr comment <pr> --body '## Greenlight — Round N
**Fixed (X):** brief list
**Disagreed (X):** brief reasoning
**Deferred (X):** brief reasoning'

# 3. Mark as processed
python3 gl-snapshot.py --mark-seen <ids>
```

## CI failures come pre-diagnosed

Each failed check includes `classification` ("branch" or "flaky") and `log_excerpt` (last 30 lines). See `references/ci-classification.md` for the heuristics.

## Comments come with code context

Each comment includes `code_context` — the diff hunk around the commented line. Triage without reading the full file first.

## Guardrails

- **Think before fixing.** Don't blindly apply every bot suggestion.
- **No workarounds.** If you can't fix it properly, disagree or defer.
- **No over-engineering.** Bot suggestions that add complexity without solving real problems should be pushed back on.
- **Always reply.** Every inline comment gets a reply. Every round gets a summary.
- **Wait for re-review.** After every push, `--wait-review` then re-snapshot. Don't skip.
- **Know when to stop.** After 3+ rounds with only nit/duplicate comments, finish.
- **Escalate when needed.** If a comment needs a product decision, stop and ask the user.

## References

- `references/ci-classification.md` — Branch vs flaky heuristics
- `references/triage-guide.md` — Reply templates and agreement criteria
