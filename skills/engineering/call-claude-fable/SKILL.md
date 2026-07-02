---
name: call-claude-fable
description: Call Claude Code Fable from Codex as an external CLI advisor for hard judgment, architecture, product thinking, frontend/design critique, and high-stakes decisions. Treat Fable as the premium, smartest, most expensive advisor in this local setup. Use when the user asks Codex to consult Fable, call Claude/Fable, get a second opinion, compare another agent's output, improve design quality, reason through a hard problem, start or resume a Claude Code Fable session, reuse Fable session cache, use high thinking/effort Fable, or manage Claude Code background agents while controlling Fable token/cost exposure. Prefer a Codex CLI worker for routine implementation, fast code edits, tests, and mechanical cleanup.
---

# Call Claude Fable

## Overview

Use the local `claude` CLI to call Claude Code with `--model fable` and an explicit effort level. Treat Fable as an external advisor or worker: keep prompts scoped, set `--max-budget-usd`, capture the `session_id`, and resume existing sessions instead of restarting context-heavy work.

## Model Role

Treat Fable as the expensive senior advisor in this setup:

- Best for hard judgment, ambiguous strategy, architecture tradeoffs, product direction, deep debugging hypotheses, security-sensitive reasoning, prompt/agent design, and frontend/design critique.
- Strong for design taste: visual direction, UX critique, interaction polish, hierarchy, layout, product feel, and "does this look right?" questions.
- Use when being wrong is expensive, when the main Codex agent wants a serious second opinion, or when a design/architecture choice will shape a lot of downstream work.
- Avoid for routine implementation, file-by-file cleanup, straightforward test fixes, bulk edits, or cheap verification. Prefer `call-codex-gpt55` for fast worker tasks.

Ask Fable for advice, critique, options, or a plan more often than for direct edits. When Fable does produce code, treat it as a proposal and have Codex verify and integrate it.

## Quick Start

Prefer the bundled wrapper because it applies the Fable defaults and handles Claude CLI argument ordering:

```bash
python3 /path/to/call-claude-fable/scripts/claude_fable.py run \
  "Answer in three bullets: what is the narrow next step here?"
```

Equivalent raw CLI:

```bash
claude -p "Answer in three bullets: what is the narrow next step here?" \
  --model fable \
  --effort high \
  --max-budget-usd 0.50 \
  --output-format json \
  --tools ""
```

Keep the prompt before `--tools`. In Claude Code `--tools` is variadic, so flags or prompts placed after it can be consumed as tool names.

## Workflow

1. Check availability cheaply:

```bash
claude --version
claude --help
```

If a run returns `Not logged in - Please run /login`, stop and report that Claude Code auth is missing. Do not spend time debugging the task prompt until authentication is fixed.

2. Start with a narrow, low-budget Fable run:

```bash
python3 /path/to/call-claude-fable/scripts/claude_fable.py run \
  --max-budget-usd 0.25 \
  "Inspect this issue conceptually. Return: finding, confidence, next action."
```

3. Read the returned `session_id`, `total_cost_usd`, and `output_path`. Save the session id and output path in your notes or final answer when the user may want continuation.

4. Resume instead of replaying context:

```bash
python3 /path/to/call-claude-fable/scripts/claude_fable.py run \
  --resume SESSION_ID \
  "Continue from the previous answer. Only expand the second bullet."
```

Use saved-session resume to reuse cache without remembering the id:

```bash
python3 /path/to/call-claude-fable/scripts/claude_fable.py last
python3 /path/to/call-claude-fable/scripts/claude_fable.py run \
  --resume-last \
  "Continue from the saved Fable session. Check only the naming question."
```

Use `--continue-latest` only when the current directory has exactly the recent Claude session you intend to continue. Use `--fork-session` with `--resume` or `--resume-last` when the continuation should branch from the old context without mutating that session.

## Effort And Thinking

Claude Code exposes "thinking size" through `--effort`. Default to `high` for Fable unless the user asks for a different size.

- `low` or `medium`: cheap smoke tests, formatting, tiny checks.
- `high`: normal Fable sub-agent work.
- `xhigh` or `max`: use only for hard reasoning tasks or when the user explicitly asks; raise the budget deliberately.

The wrapper accepts both names:

```bash
python3 /path/to/call-claude-fable/scripts/claude_fable.py run --thinking high "..."
python3 /path/to/call-claude-fable/scripts/claude_fable.py run --effort high "..."
```

## Tools And Permissions

Default to no Claude tools for pure analysis:

```bash
--tools ""
```

For codebase work, explicitly choose the smallest tool surface and directory access required:

```bash
python3 /path/to/call-claude-fable/scripts/claude_fable.py run \
  --tools "Read,Grep,Glob" \
  --add-dir "$PWD" \
  "Find the likely source file for this bug. Do not edit files."
```

Allow edits only when the user wants Claude Code to make changes and the worktree can tolerate another agent editing files. State the write scope in the prompt. Do not use `--dangerously-skip-permissions` unless the user explicitly requests that risk.

## Background Agents

Start a Claude Code background agent only for work that can continue independently:

```bash
claude --bg "Investigate the failing test and report the smallest fix." \
  --model fable \
  --effort high \
  --max-budget-usd 1.00 \
  --name fable-test-investigation
```

List agents for the current workspace:

```bash
python3 /path/to/call-claude-fable/scripts/claude_fable.py agents --cwd "$PWD"
```

Use background agents sparingly: they are easy to forget and Fable can become expensive.

## Output Handling

With `--output-format json`, capture:

- `result`: Claude's answer.
- `session_id`: the id to pass to `--resume`; the wrapper also saves the latest id.
- `total_cost_usd`: actual spend reported by Claude Code.
- `is_error` and `api_error_status`: error handling.
- `output_path`: a durable artifact with full stdout/stderr and compact metadata.

If the wrapper prints an error with `total_cost_usd: 0` and a login message, report the auth issue. If cost is near or above the budget cap, summarize what was learned and ask before rerunning with a higher cap.

## Output Artifacts

Treat wrapper output as an artifact, not just terminal text. By default each non-dry run writes:

```text
$CODEX_HOME/external-agent-outputs/claude-fable/<timestamp-session-id>/
  summary.json
  stdout.txt
  stderr.txt
```

Use `summary.json` after context compaction to recover the command, cwd, return code, compact summary, and raw output paths. Use `stdout.txt` for the full Claude payload. Override the artifact root with `AI_AGENT_OUTPUT_DIR`; disable saving with `--no-save-output` only for throwaway smoke tests.

## Bundled Script

Use `scripts/claude_fable.py` for repeatable runs, dry runs, saved-session resume, output artifact capture, and agent listing. It stores the most recent session in `$AI_AGENT_SESSIONS_PATH` when set, otherwise `$CODEX_HOME/external-agent-sessions.json` or `~/.codex/external-agent-sessions.json`. Read or patch the script if the installed Claude CLI changes flags.
