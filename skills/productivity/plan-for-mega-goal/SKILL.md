---
name: plan-for-mega-goal
description: Turn a multi-objective piece of work into a roadmap on disk plus a small pointer prompt for the agent's `/goal` orchestration loop. Each sub-goal in the roadmap is shaped like a single `plan-for-goal` output; the roadmap holds the multi-goal scaffolding that wouldn't fit in `/goal`'s 4000-character objective limit. Use when the conversation has 3+ distinct objectives that share a destination.
argument-hint: "[optional: extra context or constraints]"
---

# Plan for Mega-Goal

For work that's **bigger than one goal but smaller than an unbounded backlog**. Produces a **roadmap folder on disk** that survives the loop, plus a **short pointer prompt** to paste into `/goal`. The loop reads the roadmap every turn; the pointer prompt stays tiny.

## The Topic

$ARGUMENTS

## When to use this vs `plan-for-goal`

Almost always start with `plan-for-goal`. Reach for this skill only when:

- The work has **3+ genuinely independent objectives** that share a destination and a quality bar, AND
- Collapsing them into one prompt would either lose load-bearing information or blow past 4000 chars.

If you can't name 3+ distinct sub-goals each with their own `Done =` line, this is one goal — go back to `plan-for-goal`. A flat list of unrelated tasks isn't a mega-goal either; those are separate goals to run separately. A mega-goal has **one shared destination**, multiple paths to it.

## How this rides on top of `/goal`

`/goal` is one-objective-per-thread (codex enforces this at the data layer) and caps the user-typed objective at 4000 characters. But its continuation template explicitly treats *"any referenced files, plans, specifications, issues, or user instructions"* as a source of requirements for the completion audit. We use that mechanism: the pointer prompt is short and points at a roadmap file; the roadmap holds the multi-goal structure; the completion audit walks the roadmap.

## Each sub-goal inherits from `plan-for-goal`

Every file under `goals/` IS a `plan-for-goal` output — same anchors (`Goal`, `What great looks like`, `How to close the loop`, `Done =`, `Not`, `Open`, `Where to look`), same labels, same rules. **Read `../plan-for-goal/SKILL.md` first.** This skill governs only how sub-goals fit together as a system, not how each individual one is written.

**Delegation, not duplication.** `references/subgoal-template.md` describes only the deltas: four rule overrides (4000-char cap doesn't apply to disk files; "one objective" applies per sub-goal; the pointer prompt is allowed one exact path; `Done =` / close-the-loop must be PR-specific and sub-goal-specific) plus two mega-goal-specific additions (`Time budget:` and `## PR body`). Updates to `plan-for-goal`'s anchors, labels, or rules flow through to mega-goal sub-goals automatically — sharpen `plan-for-goal`, every mega-goal benefits.

## What you produce

**On disk, committed to the repo** (the roadmap is engineering record-of-work, not ephemeral):

```
.megagoal/<slug>/
├── ROADMAP.md            # checkbox list — source of truth for what's done, records PR #s
├── POINTER_PROMPT.md     # the exact text pasted into /goal — durable + resumable
├── NOTES.md              # three sections: Active blockers (in place) · Proposed additions · Event log
├── FEEDBACK.md           # append-only meta-feedback for improving the skill / tooling / codebase
└── goals/
    ├── 01-<slug>.md      # one plan-for-goal-shaped file per sub-goal
    ├── 02-<slug>.md
    └── ...
```

**`FEEDBACK.md`** is the meta layer — append-only observations the agent records *during* the run about friction in the skill, missing tooling, or codebase issues that complicated the work. The audience is the skill maintainer (you), not the loop runner. After the run, you skim `FEEDBACK.md` and decide which items to fold back into `plan-for-mega-goal`, related tooling, or the codebase as separate work. See `references/feedback-template.md`. Without this, every mega-goal run's lessons evaporate; with it, the skill gets sharper with every use.

**`ROADMAP.md`** records PR numbers as soon as they exist, not just when boxes get checked: `- [ ] — PR #117` for in-progress sub-goals, `- [x] — PR #117` for complete. This makes ROADMAP.md the canonical lookup for "what PRs belong to this stack" — no fragile branch-name search needed.

**`POINTER_PROMPT.md`** holds the raw prompt (no markdown wrapper) — `cat .megagoal/<slug>/POINTER_PROMPT.md | pbcopy` regenerates the clipboard so the user can resume the loop hours or days later from any machine. It's also the durable record of "what spec was the loop actually running under" — without it, the prompt only lives in `/goal`'s thread-scoped SQLite and dies when the thread ends.

**`NOTES.md`** has structured sections with different update semantics — `## Active blockers` is updated in place (no duplicate stop summaries), `## Proposed additions` is append-only, `## Event log` is append-only. See `references/notes-template.md`. Without this structure, every resume of a blocked loop appends another identical stop summary to NOTES.md — noise that obscures the real event log.

**The pointer prompt** — the only thing the user pastes into `/goal`. It encodes how the loop runs **autonomously for hours or days without human intervention**: how to pick the next sub-goal, how to handle review feedback / CI failures / stack-tool conflicts inline, the discipline rules, and the genuine stop conditions. Under 4000 chars (codex's hard cap). See `references/examples.md` for the full form.

## How to use it

1. **Pre-flight: detect the loop's required tools — but don't block on missing ones.** The `/goal` loop needs:
   - **`gh`** (GitHub CLI) — for PR creation, status checks, reading reviewer comments.
   - **`ghstack`** — to manage the stacked PRs.

   Run `which gh ghstack` to detect what's installed locally. **Do not attempt to install missing tools yourself** — that crosses too many trust boundaries (system paths, network, possibly sudo).

   **Don't stop the plan if something's missing locally.** The planning agent and the `/goal` loop may run in different environments — the user may invoke `/plan-for-mega-goal` in Claude Code on one machine and paste the prompt into `/goal` on another. Local detection is necessary but not sufficient. Note what was missing (if anything) and surface it as a **prominent install-first banner** when you show the pointer prompt in step 7.

   The pointer prompt itself MUST include a turn-1 pre-flight that re-runs `which gh ghstack` and stops the loop if either is missing — that's defense in depth and catches the cross-environment case.

   *Why ghstack and not Graphite (`gt`) or `spr`:* open source, single-command install, pure Python, battle-tested at scale (PyTorch). The skill's pointer-prompt template uses ghstack commands; if you have a strong preference for another stack tool, swap the commands manually after scaffolding. The default opinion is ghstack.

2. **Decompose first, confirm, *then* write.** Read the conversation. Draft a sub-goal list (typically **3–8 items** — fewer and it's one goal, more and the loop loses coherence). For each one: a name, a one-line `Done =`, and any dependencies on other sub-goals. Show this to the user as plain text **before touching disk**. The wrong decomposition is the most expensive failure mode — fix it before scaffolding.

3. **Pick the `<slug>`** as a short kebab-case noun for the whole mega-goal (e.g. `auth-rewrite`, `pricing-page`, `eval-harness`). State it to the user.

4. **Write the scaffolding once approved.** Create `.megagoal/<slug>/` at repo root with:
   - `ROADMAP.md` per `references/roadmap-template.md`
   - sub-goal files in `goals/` (numbered `01-…`, `02-…`) per `references/subgoal-template.md`
   - `NOTES.md` pre-scaffolded with three section headers (`## Active blockers`, `## Proposed additions`, `## Event log`) per `references/notes-template.md`
   - `FEEDBACK.md` pre-scaffolded with the header and category list per `references/feedback-template.md`

   Don't leave NOTES.md or FEEDBACK.md empty — the loop needs the section structure to know where to write. `POINTER_PROMPT.md` gets written in step 6 after the prompt is measured.

5. **Each sub-goal file follows `plan-for-goal`'s 5 anchors** with the overrides in `references/subgoal-template.md`. Sub-goal files can be longer than 4000 chars — they're read from disk, not injected. Keep them tight anyway; padding compounds across the loop.

6. **Measure the pointer prompt AND write it to disk.** Pipe through `wc -m` to verify under the 4,000-char hard cap. State the count to the user in one line above the code block — e.g. *"Pointer prompt: 3,595 chars — under the 4000 cap."* If you're at 3,000–4,000, audit what's there: hard constraints that prevent observed failure modes (good — keep) vs. step-by-step recipes specifying exact retry counts, exact time intervals, exact command flags (micromanaging — trim). The reference pointer prompt in `references/examples.md` is ~3,600 chars and earned every line by preventing real failure modes — but don't pad to match it.

   Then **save the exact prompt to `.megagoal/<slug>/POINTER_PROMPT.md`** as raw text (no markdown wrapper, no banner — the banner is human-facing context, not the prompt itself). This makes the prompt durable: someone returning days later can `cat .megagoal/<slug>/POINTER_PROMPT.md | pbcopy` to regenerate the clipboard and resume `/goal` without needing to find the original conversation.

7. **Copy the pointer prompt to the clipboard, then show it.** Output shape: a prominent install-first warning banner FIRST, then the pointer prompt in a fenced code block. The banner is non-negotiable — the worst-observed failure mode is the user pasting the prompt into a `/goal` loop where `ghstack` isn't installed, resulting in a 34-minute autonomous run that produces a single local change set and zero PRs. Visibility-first prevents this.

   Banner template (adjust the **emphasis** based on what was detected in step 1):

   > ⚠️ **INSTALL REQUIRED BEFORE PASTING INTO `/goal`** ⚠️
   >
   > The autonomous loop needs these installed **in whatever environment runs `/goal`** (not just where you ran `/plan-for-mega-goal`):
   > - **`gh`** (GitHub CLI) — `brew install gh && gh auth login`
   > - **`ghstack`** — `pip install ghstack && ghstack auth`
   >
   > Without these, the loop will produce a single local change set instead of a stacked PR series. The pointer prompt's turn-1 pre-flight catches missing tools and stops the loop, but the banner prevents the wasted-time failure mode upstream.

   If step 1 found something missing locally, sharpen the banner: e.g. *"You currently have `gh` but not `ghstack` here — install before pasting, or ensure it's installed wherever you run `/goal`."*

8. **If the loop drifts later, edit `ROADMAP.md` or a sub-goal file directly** — the loop re-reads them every turn. Don't patch the pointer prompt; the prompt is just a pointer, the roadmap is the lever.

## What the pointer prompt must encode

The pointer prompt frames the work for hours or days without human intervention. It gives the agent the **shape** of autonomous operation while trusting the agent's judgment for tactical decisions. The skill is a track, not a remote control — describe the shape, define the few autonomy boundaries, and let the agent handle the rest.

### Hard constraints

These are autonomy boundaries AND the workflow shape itself, not productivity tactics. The skill exists to enforce them. The pointer prompt must phrase them as rules with no softening language — agents will rationalize around constraints that read like "good defaults".

- **One PR per sub-goal via `ghstack`.** Not zero PRs with local-only changes; not one mega-PR with everything in it. A sub-goal that exists only as un-PR'd local diff is an unstarted sub-goal, regardless of what the local diff contains. This is the core of "stacked PRs" — without this constraint, the agent will rationalize a 30-file local change set as "the mega-goal is done."
- **Record PR # on the roadmap entry as soon as `ghstack submit` opens it.** Update the line to `- [ ] — PR #N` (still unchecked) when the PR is opened, then to `- [x] — PR #N` when the sub-goal is complete. The PR # exists on the roadmap from the moment it exists in GitHub — not just at completion. This makes ROADMAP.md the canonical lookup for the stack PR set.
- **A checked box is `- [x] — PR #N` or it's not checked.** No third form. The box-PR coupling is mechanical: without a PR number on a checked line, the box is invalid.
- **"CI green" means the open PR's CI, NOT local tests.** `bun run test` (or `pnpm test`, `cargo test`, etc.) passing locally is not the gate. The gate is `gh pr checks <pr>` returning all-green on the open PR.
- **Don't merge PRs.** Merging is the human's gate. The loop's job ends at *"stack opened, all PRs approved, ready for `ghstack land`"*.
- **Don't rewrite a sub-goal's `Done =` or directional outcome mid-loop.** The contract is fixed once scaffolded. The agent CAN append a `## Notes` section to a sub-goal file explaining a deviation; the goal itself is immutable.
- **`ROADMAP.md` is the source of truth for "what's done" AND for which PRs are in the stack.** Not memory, not assertion, not branch-name search.
- **No new sub-goals mid-loop.** Discovered ones go under `## Proposed additions` in `NOTES.md`; the human reviews on return.
- **Three genuine stop conditions:** all sub-goals checked-with-PR (success), every remaining sub-goal blocked with unchanged prerequisite, or token budget exhausted. Anything else → keep moving.
- **Before claiming success, audit the stack via roadmap PR numbers.** Extract every `PR #N` reference from ROADMAP.md; for each, `gh pr view <N> --json state,reviewDecision,statusCheckRollup`. Confirm open + CI green + /code-review clean. Any checked sub-goal whose PR fails the check → box is invalid → unmark and keep working. Don't use `gh pr list --search "head:..."` for this — ghstack uses numeric heads that won't match a slug-based pattern.
- **On any stop, append a final summary block to `## Event log` in `NOTES.md`** — outcome, PRs (with #), time, blockers (point at `## Active blockers`, don't repeat full context), reviewer requests addressed and pending. The first thing the human reads on return.
- **`NOTES.md` has structured sections with different rules:** `## Active blockers` is **updated in place** (no duplicate stop summaries); `## Proposed additions` and `## Event log` are append-only.
- **Every blocker in `## Active blockers` has a fingerprint:** `command · failure · prerequisite · last verified`. Same fingerprint twice in a row → just bump `Last verified`. Different fingerprint → new line. Don't append duplicate stop summaries to `## Event log` for the same blocker.
- **Retry blocked sub-goals only when the prerequisite has changed since `Last verified`.** If unchanged, bump the timestamp and skip the retry — no-op retries waste turns.
- **Each sub-goal has its own verification path — generic test runs are not enough.** Every sub-goal file's "How to close the loop" must include sub-goal-specific commands or surfaces (a specific test file, browser flow, CLI invocation, or grep) that prove THIS sub-goal's outcome. Generic `bun run test` / `pnpm test` is a baseline — not sub-goal verification.
- **Stack PRs are the PRs whose numbers appear on roadmap entries.** Open PRs NOT in that set are informational unless they target the same files or block this stack's CI — don't react to unrelated review activity.

## The whole scaffold guides the loop, not just the pointer prompt

`/goal` re-injects the pointer prompt every turn AND treats referenced files as requirements (per codex's continuation template: *"derive concrete requirements from the objective and any referenced files"*). That means **everything the skill produces — `ROADMAP.md`, every sub-goal file, even `NOTES.md` as it grows — guides the loop agent**, not just the pointer prompt.

The pointer prompt is the short re-injected lever. The sub-goal files are the durable, detailed specifications. The loop's behavior comes from the union of all of them. So:

- A vague sub-goal file produces vague execution, no matter how strict the pointer prompt is.
- A precise sub-goal file (specific verification path, clear `Done =`, named scope edges) lets a less-strict pointer prompt still produce the right work, because the loop re-reads the sub-goal file every turn.
- The skill's leverage is in how well-shaped the *whole scaffold* is — the pointer prompt enforces the workflow shape, the sub-goal files enforce the per-sub-goal rigor.

### Good defaults (guidance, not commandments)

Suggestions with reasoning. The agent uses judgment when the situation differs:

- **Retry-then-hop on CI failures and `/code-review` findings.** Fix the obvious cause, retry. If the same failure persists after a couple of fix attempts, it's probably infrastructure flake or a deeper issue — log to `NOTES.md`, mark blocked, hop. *Why:* fixed retry counts force either premature give-up or futile retry loops; judgment beats a number.
- **Address review feedback inline, on the affected PR's own branch.** When a prior PR shows `CHANGES_REQUESTED`, read the comments, fix on that PR's branch, `ghstack submit` to restack, reply on the PR. *Why:* otherwise the loop pauses on every review and kills the autonomy property. The only literal halt-this-sub-goal phrase is *"do not proceed"*.
- **Prefer fix-up commits over amending earlier sub-goals' history.** When a later sub-goal finds a bug planted in an earlier one, add a fix-up commit on the current branch with a one-line note in the message. *Why:* amending an already-approved PR re-triggers review and churns reviewers. (Pushing review-feedback fixes to the *same PR's own branch* is fine and expected — the guidance is about not modifying earlier sub-goals' commits from a later sub-goal's branch.)
- **Pre-flight: before working a sub-goal, check whether its `Done =` is already true.** If so, check the box, log it, continue. *Why:* don't manufacture work the world already did.
- **Retry blocked sub-goals only when nothing else is workable.** Natural cooldown — make progress on whatever you can, circle back. *Why:* otherwise the loop burns turns on one stuck problem instead of accumulating progress.
- **Periodic heartbeat to `NOTES.md` when the loop's been running for hours with nothing else to log.** *Why:* the human returning after many hours wants a recent timestamp confirming the loop didn't die.

### `NOTES.md` is the audit trail (three sections, different rules)

See `references/notes-template.md` for the full template. Quick summary:

- **`## Active blockers`** — updated in place. One line per active blocker with the fingerprint format: `[blocked] sub-goal NN: <failure>. Prerequisite: <what must change>. Last verified: <ISO timestamp>.` Bump the timestamp only when state changes or a fresh audit is requested.
- **`## Proposed additions`** — append-only. Sub-goals the agent discovered but didn't work (because they're not in the roadmap).
- **`## Event log`** — append-only. One-line entries per notable event: sub-goal complete (PR # + wall time), reviewer feedback addressed, blocker resolved, heartbeat, cross-cutting decision, final summary block.

The human reads NOTES.md top-to-bottom on return; aim for skimmable-in-30-seconds. The append-only/in-place split prevents the "every resume appends another identical stop summary" failure mode.

### Trust the agent — but be precise about what to trust it for

There are two kinds of decisions in the pointer prompt, and they need opposite treatment:

**Trust the agent on HOW** — tactics. Retry counts, retry timing, exact command flags, error-message wording, when to give up on a stuck failure, which test failure looks like a flake vs a real bug. If you find yourself writing *"exactly N retries"* or *"every N hours"* or a 10-step recipe, you're micromanaging. Restate as a directional principle (*"a couple of attempts before giving up"*, *"periodically"*) and trust the agent's judgment.

**Do NOT trust the agent on WHAT** — the workflow shape. Stacked PRs. One PR per sub-goal. Not merging. Not checking a box without a PR. These look like *"procedural details"* to a permissive reader, and the agent will rationalize around them if you frame them as good defaults — *"my local tests passed, that's CI green for practical purposes, I don't need to open the PR"*. They are the *shape* of the work, not tactics. They go in **Hard constraints** with no softening language, written as commands not suggestions.

The dividing line: if the rule defines *what the output is*, it's a hard constraint. If it defines *how the agent gets there*, trust the agent. A pointer prompt that gets this wrong fails either by micromanaging tactics (rigid) or by letting the agent skip the workflow (no real artifacts). Real failure mode observed: an autonomous loop ran for 34 minutes, marked all 5 sub-goals "complete" in ROADMAP.md, but opened zero PRs and committed zero code. The pointer prompt's `ghstack submit` and `CI green AND /code-review clean` rules were read as suggestions because the surrounding framing said *"trust the agent"*.

## When NOT to use this

- The work fits in one 4000-char `plan-for-goal` prompt → use `plan-for-goal`.
- A list of unrelated tasks → those are separate goals, run separately.
- Open-ended exploration where the sub-goals aren't yet known → keep talking, surface the goals first, then plan.
- Two sub-goals that feel like they could be one → merge them, this is one goal in disguise.

---

**References:**
- `../plan-for-goal/SKILL.md` — anchor structure and rules for each sub-goal file. **Read first.**
- `references/roadmap-template.md` — exact `ROADMAP.md` structure and update rules.
- `references/subgoal-template.md` — sub-goal file format and the override list from `plan-for-goal`.
- `references/notes-template.md` — `NOTES.md`'s three-section structure (Active blockers · Proposed additions · Event log) and the blocker fingerprint format.
- `references/feedback-template.md` — `FEEDBACK.md`'s structure for capturing skill/tooling/codebase friction during a run.
- `references/examples.md` — one worked mega-goal breakdown end to end.
