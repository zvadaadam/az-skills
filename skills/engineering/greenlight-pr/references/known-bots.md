# Known AI Review Bots

The snapshot script auto-detects these via login pattern matching. When any bot is detected, `mode` = `"BOT"`.

## Bot Catalog

| Bot | GitHub login | Behavior |
|-----|-------------|----------|
| **CodeRabbit** | `coderabbitai[bot]` | PR summary + inline comments. Auto re-reviews on push. Resolves its own outdated comments. Most common. |
| **Graphite** | `graphite-app[bot]` | Inline comments + summary. Auto re-reviews. Tied to Graphite stacking workflow. |
| **Copilot Review** | `copilot-pull-request-review[bot]` | GitHub-native. You must re-request review after push (not automatic). |
| **Sourcery** | `sourcery-ai[bot]` | Inline suggestions + quality score. Can use APPROVE or REQUEST_CHANGES (most bots only COMMENT). |
| **SonarCloud** | `sonarcloud[bot]` | Quality gate via status check (pass/fail) + inline comments on new issues. |
| **Qodo / PR-Agent** | `qodo-merge-pro[bot]` | PR descriptions, review comments, test generation. Manual trigger with `/review`. |
| **CodeGuru** | `aws-codeguru-reviewer[bot]` | Security + concurrency focus. Java/Python only. |
| **CodeScene** | `codescene[bot]` | Code health via status checks, not inline reviews. |

## Re-review patterns

```
most bots (CodeRabbit, Graphite, Sourcery, SonarCloud):
  push → bot auto re-reviews → may post new comments
  always --wait-review after push

copilot:
  push → must manually re-request review from Copilot
  use: gh pr edit <pr> --add-reviewer "copilot"

qodo:
  push → comment "/review" on PR to trigger re-review

codescene:
  push → status check re-runs automatically (no inline comments)
```

## Important: "approved" does not mean "done"

```
bot posts review with status = "APPROVED"
  but ALSO adds new inline comments in the same review
  → you still have unseen comments to triage

always check: snapshot.new_comment_count > 0
  even when PR review status shows approved
```

## No bot detected

If `mode` = `"SELF"`, there is no automated reviewer on this repo. Report to the user — they may want to set up CodeRabbit, Graphite, or similar. Do not attempt a self-review. Greenlight-pr drives PRs to green, it does not review code.
