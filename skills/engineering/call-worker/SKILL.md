---
name: call-worker
description: Call the fast Codex GPT-5.5 worker through Codex CLI from Codex or another terminal for clean code implementation, focused repo exploration, tests, refactors, bug fixes, and mechanical engineering tasks. Treat the worker as fast and strong at code, but less suited than the Fable advisor for hard judgment and frontend/design taste. Use when the user asks to call a worker, trigger Codex from the CLI, delegate bounded code work, run Codex outside the Codex IDE/app, run non-interactive codex exec, resume or reuse a worker/Codex CLI thread, use GPT-5.5 with high reasoning effort, or wrap Codex CLI behavior for repeatable agent runs. Prefer call-advisor for expensive advisor work, design critique, architecture judgment, and ambiguous strategy.
---

# Call Worker

## Overview

Use the local `codex` CLI to call a fast Codex worker with `--model gpt-5.5` and `model_reasoning_effort="high"`. Prefer `codex exec` for scriptable worker runs, and capture the returned `thread_id` so work can be resumed.

## Model Role

Treat the worker as the fast code implementation model in this setup:

- Best for focused implementation, clean patches, repo exploration, bug fixing, tests, refactors, migration chores, small scripts, and validating a hypothesis in code.
- Strong when the task has a clear definition of done and the result can be checked by tests, diff review, or command output.
- Use when speed matters, when work can be delegated in a bounded write scope, or when the main Codex agent wants another implementation pass.
- Weak relative to the advisor for frontend/design taste, visual hierarchy, broad product judgment, ambiguous strategy, and hard architecture calls.

Give worker prompts with ownership boundaries, expected files or modules, and verification commands. Use `call-advisor` first when the question is "what should we build or choose?" rather than "make this patch."

## Quick Start

Prefer the bundled wrapper because it sets the model/effort defaults, uses stdin safely, and summarizes JSONL events:

```bash
python3 /path/to/call-worker/scripts/worker.py run \
  "Answer in three bullets: what is the narrow next step here?"
```

Equivalent raw CLI:

```bash
printf '%s' "Answer in three bullets: what is the narrow next step here?" | \
  codex exec - \
    --model gpt-5.5 \
    --config model_reasoning_effort='"high"' \
    --config approval_policy='"never"' \
    --sandbox read-only \
    --skip-git-repo-check \
    --json
```

`codex exec` has no direct `--effort` flag in this installed CLI; use the config override `--config model_reasoning_effort='"high"'`.

## Workflow

1. Check the local CLI and auth cheaply:

```bash
codex --version
codex doctor
```

`codex doctor` should show auth configured. If auth is missing, run `codex login`.

2. Start with a narrow prompt. Codex CLI does not expose a `--max-budget-usd` cap here, so scope the prompt manually and avoid broad repo-wide requests unless needed.

```bash
python3 /path/to/call-worker/scripts/worker.py run \
  --sandbox read-only \
  "Inspect this issue conceptually. Return: finding, confidence, next action."
```

3. Read the returned `thread_id`, `last_agent_message`, `usage`, and `output_path`. Save `thread_id` and output path when the user may want continuation or later retrieval.

4. Resume instead of replaying context:

```bash
python3 /path/to/call-worker/scripts/worker.py resume THREAD_ID \
  "Continue from the previous answer. Only expand the second bullet."
```

Use saved-thread resume to reuse cache without remembering the id:

```bash
python3 /path/to/call-worker/scripts/worker.py last
python3 /path/to/call-worker/scripts/worker.py resume --saved-last \
  "Continue from the saved Codex worker thread. Check only the naming question."
```

Use `--last` only when the most recent Codex exec session is definitely the one to continue; prefer `--saved-last` when the wrapper recorded the thread you want.

## Effort

Default to GPT-5.5 high:

```bash
--model gpt-5.5 --effort high
```

The wrapper maps `--effort high` to:

```bash
--config model_reasoning_effort='"high"'
```

Use `low` or `medium` for cheap smoke tests. Use `xhigh` or `max` only when the user explicitly asks or the task is hard enough to justify the extra reasoning tokens.

## Sandboxing And Edits

Default to read-only for investigation or review work:

```bash
--sandbox read-only
```

For edits inside the current repo, opt in deliberately:

```bash
python3 /path/to/call-worker/scripts/worker.py run \
  --sandbox workspace-write \
  --cd "$PWD" \
  "Make the smallest patch for this bug. Do not touch unrelated files."
```

Avoid `--dangerously-bypass-approvals-and-sandbox` unless the user explicitly requests that risk and the environment is externally sandboxed.

## Interactive CLI

For a real terminal session rather than non-interactive output:

```bash
python3 /path/to/call-worker/scripts/worker.py tui \
  "Start by inspecting the repo and proposing a plan."
```

Raw equivalent:

```bash
codex "Start by inspecting the repo and proposing a plan." \
  --model gpt-5.5 \
  --config model_reasoning_effort='"high"'
```

Use `codex resume --include-non-interactive THREAD_ID` to continue a saved non-interactive thread in the TUI picker when needed.

## Output Handling

With `--json`, Codex emits JSONL events plus possible warning lines. Capture:

- `thread_id` from `thread.started`: id to pass to `resume`; the wrapper also saves the latest id.
- `last_agent_message`: a compact preview of the latest completed agent message.
- `usage` from `turn.completed`: input, cached input, output, and reasoning tokens.
- `output_path`: a durable artifact with full JSONL stdout/stderr and compact metadata.

The wrapper prints a compact JSON summary unless `--raw` is used.

## Output Artifacts

Treat wrapper output as an artifact, not just terminal text. By default each non-dry run writes:

```text
$CODEX_HOME/external-agent-outputs/worker/<timestamp-thread-id>/
  summary.json
  prompt.txt
  stdout.jsonl
  stderr.txt
```

Use `summary.json` after context compaction to recover the command, cwd, return code, compact summary, and raw output paths. Use `stdout.jsonl` for the full Codex event stream and complete agent messages. Override the artifact root with `AI_AGENT_OUTPUT_DIR`; disable saving with `--no-save-output` only for throwaway smoke tests.

## Bundled Script

Use `scripts/worker.py` for repeatable non-interactive runs, saved-thread resume, output artifact capture, TUI command construction, dry runs, and JSONL summarization. It stores the most recent worker thread in `$AI_AGENT_SESSIONS_PATH` when set, otherwise `$CODEX_HOME/external-agent-sessions.json` or `~/.codex/external-agent-sessions.json`. It can still read the previous `codex-gpt55` state key for migration. Read or patch it if the installed Codex CLI changes flags.
