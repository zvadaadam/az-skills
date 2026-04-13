---
name: greenlight-pr
description: Greenlight a PR — fix CI failures, triage review comments, iterate until green.
argument-hint: "[PR number or URL]"
---

# Greenlight PR

Shepherd a PR to merge-ready: CI green + reviews addressed.

## Tool

```bash
python3 ~/.claude/skills/greenlight/scripts/gl-snapshot.py [PR]
```

One call returns structured JSON: CI status (with failure classification + log excerpts), review comments (with diff hunk context), reviewer mode, and recommended `actions`.

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
| `triage_comments` | New comments with `code_context` attached — triage per `references/triage-guide.md` |
| `wait_ci` | `gh pr checks <pr> --watch --fail-fast`, then re-snapshot |
| `done` | CI green + no new comments → report final state |
| `stop_pr_closed` | PR merged/closed → stop |
| `stop_exhausted_retries` | 3 retries used → report to user |

## Workflow

```
1. Snapshot  →  read actions
2. fix_ci?   →  check failed[].classification + log_excerpt, fix, commit, push
   retry_ci? →  --retry-failed
3. triage?   →  read new_comments[].body + code_context, triage, fix, reply, --mark-seen
4. wait_ci?  →  gh pr checks --watch, re-snapshot
5. Push?     →  BOT: --wait-review then re-snapshot
              SELF: just re-snapshot
6. done?     →  report final state
```

### CI failures come pre-diagnosed

Each failed check includes `classification` ("branch" or "flaky") and `log_excerpt` (last 30 lines). No need to manually run `gh run view --log-failed` — the script already did it.

### Comments come with code context

Each comment includes `code_context` — the diff hunk around the commented line. Triage without reading the full file first.

### BOT mode: wait for re-review

After pushing, use `--wait-review` instead of manual sleep loops:
```bash
python3 gl-snapshot.py --wait-review
```
Polls every 30s, returns snapshot when new bot review appears (or times out at 5min).

### SELF mode: self-review once

See `references/self-review.md` for agent prompts. Spawn 3 agents (correctness, API, architecture) on the full diff. Triage findings, fix, push. No re-review needed after.

## After every triage round

```bash
python3 gl-snapshot.py --mark-seen <ids>
# Reply to each comment (see references/triage-guide.md)
# Post round summary as PR comment
```

## Guardrails

- Think before fixing. Don't blindly apply every suggestion.
- BOT mode: use `--wait-review` after every push. Don't skip.
- ALWAYS reply to inline comments AND post top-level summary.
- After 3+ rounds with only duplicate/nit comments, finish.
- If a comment needs a product decision, stop and ask user.

## References

- `references/ci-classification.md` — Branch vs flaky heuristics
- `references/triage-guide.md` — Triage process, reply templates, agreement criteria
- `references/self-review.md` — Sub-agent prompts for SELF mode review
