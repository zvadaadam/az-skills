---
name: verify-harness
description: Give a repository a verification harness its agents actually use — a `control-<app>` driver CLI that runs the real app in an isolated session and drives it the way a person and an agent do, plus a user-POV feature map that says what exists, how to reach it, how to prove it and what misleads — then keep it true. Use to set one up in a fresh repo, to expand or maintain the map, to verify a change with proof, to reproduce a bug report, or whenever agents keep writing throwaway Playwright/CDP/probe scripts to check behaviour.
hooks:
  PostToolUse:
    - matcher: "*"
      hooks:
        - type: command
          command: 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill verify-harness --event skill_activated --agent-harness claude-code --quiet'
          timeout: 5
---

<!--
Based on Lauren Tan's (@poteto) verification skills and feature maps: her talk "here's how i shipped 2,500 PRs last month to production"
and pstack's create-verification-skill, maintain-verification-skill and benny automation (MIT, © 2026 Lauren Tan), published by Cursor:
https://github.com/cursor/plugins/tree/main/pstack · example: https://github.com/poteto/verification-skill-example
Feature maps as agent navigation: Matt Pocock (@mattpocockuk).
Extended by Adam Zvada from building it for a production design tool (see "What we added").
-->

# Verify Harness

Agents that change a product need to prove the change the way a person would see it. Without a harness they write a fresh Playwright or curl script every task, look at one screenshot, and throw the script away. The next agent starts from nothing, and nobody can re-run the proof.

A verification harness fixes that with two things that live in the repository:

1. **`control-<app>`**, a driver CLI. It starts the real app in an isolated, throwaway session and acts on it the way a person does: roles and names, real modifier keys, drags, menus, files, keyboard. It also acts the way an agent does, through the app's own CLI, API or MCP. Every observable result is stated as an `expect`, and the evidence is kept as a proof.
2. **A feature map**, one file per user-facing area, written from the user's point of view. Each file says what the area does, every way to reach it, a recipe of `control-<app>` commands that proves it, and the gotchas that mislead. A recipe replays on its own, so the map is also the regression checklist.

The skill the agent reads is `verify-<app>` (SKILL.md, the driver, fixtures, `features/`). This skill builds it, grows it, uses it and keeps it true.

## Modes

Pick the one the request needs, and say which:

| Mode | When | Outcome |
|---|---|---|
| **Set up** | the repo has no verify skill, or agents write probe scripts | `verify-<app>` with a working driver, 3–6 mapped areas, CI checks, one proven replay |
| **Expand** | "map everything", a new area, the completeness check fails | new feature files, each replayed green, driver gaps promoted |
| **Verify** | a change needs proof before merge | a proof folder cited in the PR, map updated in the same PR |
| **Reproduce** | a bug report or tracker issue | reproduced twice with proof (or "does not reproduce on <commit>"), then a failing test, fix and replay |
| **Maintain** | before a release, or weekly | `clean`, `changed` (one PR) or `blocked` |

The prompts that drive each mode are in [`references/prompts.md`](references/prompts.md). Copy them into the repo's notes and adapt them.

## Set up

### 1. Interview the repository, not the person

Answer from the code, and ask only what you cannot observe:

- **Surfaces.** What does a person touch: a web UI, a desktop app, a CLI or TUI, an API? What do agents touch: a CLI, an API, MCP tools, an embedded app inside a chat host? Both kinds of user belong on the map.
- **Run.** The documented dev or start command, ports, env vars, seed data, auth. How do you tell it is ready?
- **Drive.** Existing harnesses first: E2E helpers, Playwright specs, PTY helpers, the app's own CLI. The driver is usually an extraction of what the tests already do.
- **Observe.** Screenshots, the accessibility tree, the app's saved state, logs, exit codes, files on disk.
- **Isolate.** Every per-person state folder (home, profile, device account), every offline or preview switch, and every outbound service a verification must not really call (trackers, payments, paid model APIs).
- **Escape routes.** Everything that can leave the session: the system opener (Finder, the default browser), downloads, native dialogs, the clipboard, file pickers, third-party calls. Also every host the app runs inside: an iframe, a chat app, an extension.
- **Registries.** Where the product lists its entry points: UI tool catalogues, CLI usage text, API routes, MCP tool definitions. Completeness is checked against these, not against memory.

If the checkout does not build or start, fix that first or report it precisely. A harness written against a broken base teaches wrong steps.

### 2. Build `control-<app>`

Follow [`references/driver-contract.md`](references/driver-contract.md). In short:

- **Name it apart from the product's own commands**, so `verify` or `test` never collide.
- **Sessions.** `up` starts an isolated session: a temporary workspace and home, the app started through its own start command, preview or offline modes on, outbound services captured instead of called. `down` stops only what this session started. The default session is per agent conversation, so two agents in one checkout never stop each other.
- **Doctor.** Answers "is this worth driving?": a build newer than every source file (a proof against a stale bundle shows old behaviour, so `up` refuses one), processes alive, isolation holding, open gaps.
- **Two reads for every result:** once as a person sees it (the accessibility tree, the visible state) and once as the product saved it (its own CLI or API). A result is an `expect` that retries until it holds, and answers `expected` and `actual` when it does not.
- **Stand-ins at every boundary** from the interview. Each one records what the app asked for, and the product's own checks still run: the opener, downloads, dialogs, the clipboard, outbound services, pages to fetch, the host an embedded app runs in.
- **Faults** for failure paths (a read-only folder, failing fonts, slow or failing reads), reversible and undone by `down`.
- **Evidence:** screenshots, recordings, traces, and `proof <feature>`, which bundles them with the commit and build stamp into a folder that survives cleanup.
- **The gaps loop.** `script <file> --why "…"` runs a custom step inside the session and logs it in a gaps ledger. Before the task ends, each gap is either promoted into the driver (preferred) or reported to the tracker. See "No silent scripts".
- **The map commands:** `features`, `route "<words from a report>"`, `checks <feature>` (the tests annotated for it), `coverage`, `replay <feature>`, `sweep`, and `issues <feature>` against the tracker.

### 3. Seed the feature map

Write `features/README.md` and one file per area for the 3–6 areas that change or break most. Use the four-section format in [`references/feature-file-format.md`](references/feature-file-format.md):

- a paragraph saying what the area does;
- a header line: `Rules: …` (where the rule lives), `Words people use: …` (the words reporters use, which are rarely the code's), and `Checks: control-<app> checks <feature>`;
- `## Sub-features` with stable ids;
- `## How to get to it (user POV)`, listing every entry point, including the agent ones;
- `## Driving it with control-<app>`: preconditions, then bullets. Each bullet names its sub-features and runs commands in order in one continuous session, and every observable result in it is an `expect`;
- `## Gotchas`, most valuable when they say where a rule deliberately does not apply.

### 4. Wire it into the repository

- Put the skill in one real folder and link it for each host: `.agents/skills/verify-<app>/` (Codex), linked from `.claude/skills/` (Claude Code) and `.cursor/skills/` (Cursor).
- Add one paragraph to AGENTS.md: prove behaviour with `verify-<app>`, never write standalone probe scripts, and update the feature file in the same PR.
- Add annotations like `// @verifies <feature>#<sub>` above the existing tests that pin a sub-feature, so `checks` and `coverage` are generated, not hand-kept.
- Add a CI test for the map ([`references/map-checks.md`](references/map-checks.md)). It checks each file's structure, that every recipe command exists in the driver, that every annotation resolves, that the index lists every file, and that fixtures exist. It also checks that every entry point in every registry appears in a feature file: report while mapping, assert once complete.

### 5. Prove it before handing it over

Replay every seeded file in a fresh session until each passes, and check the proof survives `down`. A harness that was never run end to end is a draft.

## Expand the map

To map a whole product, run two background mappers, each owning a group of areas. Keep every driver change in the main session. The mappers drive, write files, replay each twice, annotate tests and prepare findings. They send the main session the capabilities they need, most important first, and keep working with `script` until those land. The main session:

- promotes capabilities within minutes and tells the mapper;
- reviews every finding before it goes to the tracker (next section);
- adds the files to the index;
- ends with a full `sweep`.

Prompt 7 in [`references/prompts.md`](references/prompts.md) is the brief. Map the agent surfaces too: CLI commands, API and MCP tools, the security boundary (host and origin checks, loopback only), sign-in and account paths, and every promise in the onboarding prompt people paste.

## Verify a change

1. `control-<app> doctor` (build if stale), then `issues <feature>`: a fix awaiting review is something to confirm, and an open issue may be exactly what you are about to see.
2. Read the feature file, and run what `checks <feature>` lists, fastest first.
3. `up`, then drive every entry point the file lists, plus the success, cancel, empty, error and persistence paths the change touches. Confirm each side effect through the second read.
4. `proof <feature> --note "…"`, and cite the folder.
5. Changed behaviour means the feature file and its recipe change in the same PR, and `replay` passes.

The proof bar:

- Drive the production path a person or agent uses. Arrange preconditions through the product; never inject the symptom.
- Show the trigger and the end state.
- Confirm side effects through the product's own read, not pixels alone.
- Mock only at an external boundary.
- Name any path you could not reach, with what blocked it. Never report it as verified through another path.

## Reproduce a report

1. `route "<the report's words>"`, then `issues <feature>`.
2. Reproduce the exact symptom twice through the real path, and keep a proof.
3. Note the outcome on the issue. "Does not reproduce on <commit>" is a finding too.
4. If it reproduces: write a failing test annotated for its sub-feature, fix the root cause, replay the feature, and open the PR linked to the issue.

## Maintain

The map rots when the app changes, so re-check it:

1. Tidy the index.
2. Run a **source wave**: one read-only sub-agent per feature file, all at once. Each explains from the source how the area works now, flags likely drift with file and line, and returns one short live recipe. Sub-agents never drive the app and never edit files.
3. Run `sweep`, plus the source wave's recipes for anything the files do not cover. The coordinating session does all the driving.
4. Triage each failure as one of three things:
   - a wrong recipe or description (**doc drift**: fix the map);
   - behaviour the driver cannot reach (**harness gap**: fix the driver);
   - behaviour that broke (**product regression**: report it, and never edit the map to match).
5. Check `coverage` for sub-features with no test, the gaps ledger for recurring gaps, and the completeness test for new unmapped entry points.
6. End with exactly one outcome: `clean`, `changed` (one PR of proven corrections) or `blocked` (say what blocked it).

Maintenance edits only the verify skill's own folder, never product code.

## No silent scripts

Every custom step an agent writes goes through `control-<app> script`, which logs it in the gaps ledger. Before the task ends, the gap is promoted into the driver as a command, flag, fixture or `expect`, and its recipe uses it. Otherwise it is reported to the tracker under a verifier category (for example `x-verify`). `down` lists open gaps. A script used once and deleted teaches the next agent to write another; a promoted command teaches every agent after it.

## The tracker

Wire the harness to the team's issue tracker (HiveNet, GitHub, Linear):

- `issues <feature>` finds what reporters already said, matching at least two of the feature's words, and `issues --query "<words>"` finds duplicates before you report.
- Report driver and map problems under the verifier category, and product regressions under the product's ordinary categories, naming the feature.
- Reports are short (one to three sentences), cite the proof folder, and are stated to the person before they are sent.
- A finding from a sub-agent is reproduced, or its evidence and code are checked, before it is sent.

## What we added

Beyond the pstack skills, these held up while mapping a whole production app (30 feature files, 238 sub-features, a driver of about 70 commands, 36 gaps all promoted, 28 product reports):

- per-agent default sessions with an owner, `down --force` to stop another's, and a note on every answer when a session runs a driver older than the checkout's;
- names matched from the start of a control's name to a word boundary, and a click refused when several differently named controls match;
- `runtime restart` under an open page, kept build snapshots and a stale-build fault, so "the page survives an update" is a recipe step;
- one driver answer for the whole family of results: `expect` with retries, `--contains`/`--lacks` on API answers, `--expect-error <code>` whose words are checked too, and `--capture name=<regex>` to carry a value to a later step;
- stand-ins for the operating system (opener, downloads, dialogs, clipboard), and a host the embedded app runs in, with flags that make it less capable;
- `@verifies` annotations and a completeness check against the product's registries, asserted once complete;
- the "words people use" line and `route`;
- parallel mappers with one driver owner;
- `ok` that means passed, in the driver as in the product.

Pitfalls, and the rule each taught, are in [`references/lessons.md`](references/lessons.md).
