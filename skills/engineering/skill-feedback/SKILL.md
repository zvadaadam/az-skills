---
name: skill-feedback
description: Submit concise feedback about AZ skills directly to PostHog. Use when a skill was useful, confusing, broken, missing context, or worth improving.
argument-hint: "[skill name and feedback text]"
hooks:
  PostToolUse:
    - matcher: "*"
      hooks:
        - type: command
          command: 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill skill-feedback --event skill_activated --agent-harness claude-code --quiet'
          timeout: 5
---

# Skill Feedback

This is the shared feedback helper for AZ skills. Every skill includes a short `AZ Skill Feedback` footer that reminds agents how to call this script after a run.

The script sends one anonymous PostHog event directly to the AZ skills feedback project. There is no endpoint setup, no env vars, and no user-provided token.

On first send, the telemetry helper creates one random local installation ID at `~/.az-skills/installation-id`. Only a short hash of that random ID is sent. Hostnames, usernames, emails, machine serials, file paths, and hardware identifiers are never sent.

`scripts/skill-event.py` also sends automatic read and activation events from hooks in harnesses that support them, such as Claude Code.

## Harness Support

The telemetry scripts work for any agent that can run a shell command. Automatic telemetry depends on the agent harness:

- **Claude Code**: automatic. Each skill has a scoped `PostToolUse` hook for `skill_activated`.
- **Claude Code skill reads**: automatic after `scripts/install.sh` adds one user-level `Read` hook. It emits `skill_read` only when a `SKILL.md` under a skills folder is read.
- **Codex**: supported by direct script calls when the agent follows the skill instructions. Do not assume automatic per-tool telemetry unless the Codex runtime exposes a hook adapter.
- **Pi or other agents**: supported by direct script calls or a harness-specific adapter. Use `--agent-harness <name>` to identify the runtime.

If a harness does not support hooks, submit only the events it can honestly observe. Do not fake read or activation telemetry.

## When to Submit

Submit feedback when one of these is true:

- A skill instruction was confusing or incomplete
- A skill made you choose between unclear paths
- A script or reference failed or had stale assumptions
- A skill worked unusually well and the behavior should be preserved
- You noticed a small improvement that would make future runs better

## Rules

- Keep feedback to 1-3 short sentences.
- Name the skill directly.
- Prefer concrete observations over general impressions.
- Never include secrets, private data, source code, long prompts, stack traces, API keys, or tokens.
- Use `rating=idea`, `rating=confusing`, `rating=bug`, `rating=useful`, or `rating=other`.

## Submit

```bash
python3 ~/.agents/skills/skill-feedback/scripts/skill-feedback.py \
  --skill deslop \
  --rating confusing \
  --agent-harness codex \
  --model-config unknown \
  --text "The skill should say which files it inspected before changing code."
```

Use the matching installed path when needed:

```bash
python3 ~/.claude/skills/skill-feedback/scripts/skill-feedback.py \
  --skill greenlight-pr \
  --rating useful \
  --agent-harness claude-code \
  --model-config unknown \
  --text "The retry budget guardrail avoided rerunning flaky CI forever."
```

Optional lightweight metadata:

```bash
python3 ~/.agents/skills/skill-feedback/scripts/skill-feedback.py \
  --skill greenlight-pr \
  --rating bug \
  --agent-harness codex \
  --model-config unknown \
  --context repo=zvadaadam/az-skills \
  --text "The skill assumes gh is authenticated before checking local repo context."
```

## PostHog Event

- `event`: `skill_feedback`
- `distinct_id`: `az-skills-installation:<installation_id_hash>` when the local installation ID can be read or created
- `properties.$process_person_profile`: `false`
- `properties.source`: `az-skills`
- `properties.schema_version`: `2`
- `properties.installation_id_hash`: anonymous hash of the local random installation ID
- `properties.agent_harness`: agent runtime, such as `codex` or `claude-code`
- `properties.model_config`: model/config string when the harness exposes it; otherwise `unknown`
- `properties.skill`: skill folder name, such as `deslop`
- `properties.rating`: `useful`, `confusing`, `bug`, `idea`, or `other`
- `properties.feedback_text`: short human-readable feedback
- `properties.context`: optional `key=value` metadata

To rotate the PostHog project token, update `POSTHOG_PROJECT_API_KEY` in `scripts/telemetry_common.py`.

## Product Events

Skill hooks or harness adapters send explicit PostHog events:

- `event`: `skill_read` when an agent reads a `SKILL.md`
- `event`: `skill_activated` when the skill is active and the agent makes its first tool call
- `skill`: skill folder name
- `agent_harness`: `claude-code` for bundled Claude hooks
- `model_config`: `unknown` unless the harness exposes the exact runtime model/config
- `installation_id_hash`: anonymous hash of the local random installation ID
- `session_id_hash`: short hash only; raw session IDs are not sent

`skill_activated` is triggered by the first `PostToolUse` hook for a skill in a session and is deduped locally. `skill_read` is filtered to `SKILL.md` paths only.

Tool names, tool inputs, prompts, file contents, command text, paths, stack traces, source code, hostnames, usernames, emails, machine serials, and hardware identifiers are not sent.

---

## AZ Skill Feedback

After the run, if this skill was useful, confusing, broken, or missing context, submit 1-3 safe sentences. Include `--agent-harness` when known. Include `--model-config` only if the harness exposes the exact model/config; otherwise leave it as `unknown`:

`python3 ~/.agents/skills/skill-feedback/scripts/skill-feedback.py --skill skill-feedback --rating idea --text "..."`

Never include secrets, private data, source code, long prompts, or stack traces.
