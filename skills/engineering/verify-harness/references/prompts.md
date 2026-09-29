# Prompts that drive it

Paste these, or adapt them into the repository's notes. `<app>` is the product's short name, `<feature>` a feature file's name, and `<tracker>` the issue tracker. Name the repo's skill to invoke it: `/verify-<app>` in Claude Code, `$verify-<app>` in Codex. A request that says "verify" and names the app also triggers it through the skill's description.

## 1. Set it up in a repository

> Set up a verification harness for this repository with the verify-harness skill.
>
> 1. Interview the repository, not me. Find:
>    - what people touch, and what agents touch;
>    - how the app starts locally, and how to tell it is ready;
>    - what already drives it (test helpers first);
>    - what evidence it can produce;
>    - every per-person state folder, offline or preview switch, and outbound service a verification must not really call;
>    - every way the app can leave the session (the system opener, downloads, dialogs, the clipboard, third-party calls), and every host it runs inside (an iframe, a chat app, an extension);
>    - every registry of entry points (UI tool catalogues, CLI usage, API routes, MCP tools).
> 2. Build the smallest useful `control-<app>` by extracting existing controls, following the driver contract. Select only capabilities needed by the first real recipe; this list is a growth path, not a first-PR checklist:
>    - `up` and `down` for isolated, per-agent sessions, and `doctor` with build freshness;
>    - actions by role and name with real modifier keys;
>    - a pass-through to the app's own CLI or API, with names instead of ids;
>    - `expect` for every kind of observable result;
>    - recording stand-ins at every boundary found in step 1, faults for failure paths, and `proof`;
>    - `script` with a gaps ledger, `report` and `issues` against the tracker, and `replay` and `sweep`.
> 3. Seed the feature map with the selected area(s), growing toward three to six as needed. Use the four-section format with the header line (Rules · Words people use · Checks). State each recipe's proof layer and use explicit assertions. One-shot commands may own their session and cleanup.
> 4. Add the map's CI checks, including completeness against every registry (report only for now), and `@verifies` annotations on the existing tests.
> 5. Use one canonical skill folder and link it from the hosts the repository uses. Add one paragraph to AGENTS.md.
> 6. Replay every supported recipe and check proof survives cleanup. Name unavailable entry points and the layer actually proven; do not present component checks as application or live-provider qualification.
>
> Keep a LEARNINGS.md of what surprised you and the rule each surprise taught.

## 2. Verify a change (every PR that changes behaviour)

> Verify this change with verify-<app>.
>
> 1. `control-<app> doctor` (run `build` if it says stale), then `control-<app> issues <feature>` when a tracker is configured.
> 2. Read `features/<feature>.md`, and run what `control-<app> checks <feature>` lists, fastest first.
> 3. Start a session with `control-<app> up --fixture …` when needed, or run the bounded recipes. Drive supported entry points and relevant success, cancel, empty, error and persistence paths. State each result as an expectation and confirm side effects through the product's own read. Keep unavailable paths explicit.
> 4. Retain the automatic proof or run `control-<app> proof <feature> --note "…"`, and cite the folder.
> 5. If the driver can't do something, preserve the custom step and its purpose in the gaps ledger (using `script` when supported). Promote useful recurring steps; leave other gaps explicit, with evidence and the prerequisite to close them.
> 6. If behaviour changed, update the feature file and its recipe in this PR, and `replay` it.

## 3. Reproduce a report (the outer loop)

> Reproduce <tracker> issue `<id>` with verify-<app>.
>
> 1. `control-<app> route "<the report's words>"` to find its feature file, and `control-<app> issues <feature>` for related reports.
> 2. Reproduce the exact symptom twice through the real path: arrange with fixtures and the app's API, never inject the symptom, and keep a `proof`.
> 3. Record the outcome on the issue. "Does not reproduce on <commit>" is also a finding.
> 4. If it reproduces:
>    1. Write a failing test annotated `@verifies <feature>#<sub>`.
>    2. Fix the root cause.
>    3. Replay the feature and keep the proof.
>    4. Open the PR, linked to the issue.

## 4. Maintain the map (before each release; weekly if it stays cheap)

> Run the verify-<app> maintain pass on the default branch.
>
> 1. Source wave: one read-only sub-agent per feature file, all at once. Each explains from source how its area works now, flags likely drift with file:line citations, and returns one short live recipe. None of them drive the app or edit files.
> 2. `control-<app> sweep --continue`, plus the source wave's recipes for anything the files do not cover. Only this session drives. Triage each failure as one of three things: a wrong recipe (fix the file), map drift (fix the file), or a product regression. Report a regression under its ordinary category, naming the feature, and never edit the map to match it.
> 3. Check coverage and harness gaps:
>    - `control-<app> coverage`: add a test for each sub-feature that is "recipe only";
>    - `control-<app> issues --verify` and `control-<app> gaps --all`: promote recurring gaps into the driver;
>    - look for Playwright, CDP or curl scripts under scratch folders that went around the driver.
> 4. Run the map's CI test. It fails for any tool or command that no feature file names; map each one in its area's file.
>
> End with exactly one outcome: `clean`, `changed` (one PR) or `blocked`.

## 5. Sweep before a release

> Sweep <app> with verify-<app>. Run `control-<app> sweep --continue`, then do one exploratory pass per feature file on what its recipe does not cover, finishing with the cross-surface journeys. List anything unreachable with its blocker and the closest path you did cover.

## 6. Put it on a schedule

> Every week on the default branch: run prompt 4, open at most one PR, and send product regressions to <tracker>.

## 7. Expand the map with parallel mappers

> Map these areas with verify-<app>: `<area list>`. Use two background agents, one per group of areas, and keep driver changes in this session.
>
> Each mapper:
> 1. Reads the skill's SKILL.md and features/README.md, then the product rules and tests for its areas.
> 2. Drives each area in its own named session (`--session <name>-<n>`), writes one feature file per area in the four-section format, and replays each file twice in fresh sessions.
> 3. Uses `script` for anything the driver can't do, and sends this session one message listing the capabilities it needs, most important first. It keeps working with the script until they land, then switches its recipes to the real commands.
> 4. Adds `// @verifies <feature>#<sub>` above existing tests that pin its sub-features. It changes nothing else in those files.
> 5. Prepares product findings with `control-<app> report` without `--send`, each with evidence, and writes a report file with outcome, friction, missing capabilities and findings.
>
> This session:
> - promotes requested capabilities fast and tells the mapper;
> - reviews each finding before sending it: reproduce it, or check its evidence and the code, and search the tracker for duplicates;
> - adds the files to the index;
> - ends with a full `sweep`.
