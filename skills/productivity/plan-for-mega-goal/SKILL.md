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

Every file under `goals/` is shaped exactly like a `plan-for-goal` output — same 5 anchors, same rules — with a small override list. **Read `../plan-for-goal/SKILL.md` first.** This skill governs only how sub-goals fit together as a system, not how each individual one is written. The override list lives in `references/subgoal-template.md`.

## What you produce

**On disk, committed to the repo** (the roadmap is engineering record-of-work, not ephemeral):

```
.megagoal/<slug>/
├── ROADMAP.md     # checkbox list — single source of truth for what's done
├── goals/
│   ├── 01-<slug>.md     # one plan-for-goal-shaped file per sub-goal
│   ├── 02-<slug>.md
│   └── ...
└── NOTES.md       # cross-cutting decisions, append-only
```

**The pointer prompt** — the only thing the user pastes into `/goal`. It encodes how the loop runs **autonomously for hours or days without human intervention**: how to pick the next sub-goal, how to handle review feedback / CI failures / stack-tool conflicts inline, the discipline rules, and the genuine stop conditions. Under 4000 chars (codex's hard cap). See `references/examples.md` for the full form.

## How to use it

1. **Pre-flight: check the loop's required tools** before drafting anything. The `/goal` loop needs:
   - **`gh`** (GitHub CLI) — for PR creation, status checks, reading reviewer comments.
   - **`ghstack`** — to manage the stacked PRs.

   Run `which gh ghstack` to verify both are installed. **Do not attempt to install missing tools yourself** — that crosses too many trust boundaries (system paths, network, possibly sudo). If anything's missing, tell the user upfront with install commands and stop. Don't scaffold without these — the loop will fail mid-run with no clean recovery path. Suggested phrasing:

   > Your `/goal` loop will need these installed before it can run:
   > - **`gh`** (GitHub CLI) — `brew install gh && gh auth login` (or your platform's package manager).
   > - **`ghstack`** — `pip install ghstack && ghstack auth`.
   >
   > Install what's missing, then re-run `/plan-for-mega-goal`.

   *Why ghstack and not Graphite (`gt`) or `spr`:* open source, single-command install, pure Python, battle-tested at scale (PyTorch). The skill's pointer-prompt template uses ghstack commands; if you have a strong preference for another stack tool, you'd swap the commands manually after scaffolding. The default opinion is ghstack.

   If both are present, confirm to the user ("`gh` and `ghstack` are installed — proceeding") and continue to step 2.

2. **Decompose first, confirm, *then* write.** Read the conversation. Draft a sub-goal list (typically **3–8 items** — fewer and it's one goal, more and the loop loses coherence). For each one: a name, a one-line `Done =`, and any dependencies on other sub-goals. Show this to the user as plain text **before touching disk**. The wrong decomposition is the most expensive failure mode — fix it before scaffolding.

3. **Pick the `<slug>`** as a short kebab-case noun for the whole mega-goal (e.g. `auth-rewrite`, `pricing-page`, `eval-harness`). State it to the user.

4. **Write the scaffolding once approved.** Create `.megagoal/<slug>/` at repo root with `ROADMAP.md`, sub-goal files in `goals/` (numbered `01-…`, `02-…`), and an empty `NOTES.md`. Use the templates in `references/`.

5. **Each sub-goal file follows `plan-for-goal`'s 5 anchors** with the overrides in `references/subgoal-template.md`. Sub-goal files can be longer than 4000 chars — they're read from disk, not injected. Keep them tight anyway; padding compounds across the loop.

6. **Measure the pointer prompt against the 4000-char limit** with `wc -m`. State the count to the user in one line above the code block — e.g. *"Pointer prompt: 2,400 chars — under the 4000 cap. Roadmap and 5 sub-goal files written to `.megagoal/auth-rewrite/`."* If your pointer prompt creeps over 3,000 chars, you're likely micromanaging — specific retry counts, exact time intervals, step-by-step recipes are signs to trim and trust the agent's judgment instead.

7. **Copy the pointer prompt to the clipboard, then show it in a single fenced code block** so the user can paste it straight into `/goal`.

8. **If the loop drifts later, edit `ROADMAP.md` or a sub-goal file directly** — the loop re-reads them every turn. Don't patch the pointer prompt; the prompt is just a pointer, the roadmap is the lever.

## What the pointer prompt must encode

The pointer prompt frames the work for hours or days without human intervention. It gives the agent the **shape** of autonomous operation while trusting the agent's judgment for tactical decisions. The skill is a track, not a remote control — describe the shape, define the few autonomy boundaries, and let the agent handle the rest.

### Hard constraints

These are autonomy boundaries, not productivity tactics. The skill exists to enforce them:

- **Don't merge PRs.** Merging is the human's gate; an autonomous loop should never quietly ship. The loop's job ends at *"stack opened, all PRs approved, ready for `ghstack land`"*.
- **Don't rewrite a sub-goal's `Done =` or directional outcome mid-loop.** The contract is fixed once scaffolded. The agent CAN append a `## Notes` section to a sub-goal file explaining a deviation; the goal itself is immutable. Agents that rewrite their own goals can't be audited.
- **`ROADMAP.md` boxes are the source of truth for "what's done".** Not memory, not assertion, not "I did it on the previous turn." If it's not checked in ROADMAP.md, the loop treats it as not done.
- **CI green AND `/code-review` clean before any box is checked.** The autonomy-friendly quality gate. The loop will not check a box without both.
- **No new sub-goals mid-loop.** Discovered ones go under `## Proposed additions` in `NOTES.md`; the human reviews on return. The loop continues with the existing roadmap.
- **Three genuine stop conditions:** all sub-goals checked (success), every remaining sub-goal blocked (after one retry each), or token budget exhausted. Anything else → keep moving.
- **On any stop, write a final summary block to `NOTES.md`** — outcome, PRs, time, blockers, reviewer requests addressed and pending. The first thing the human reads on return.
- **`NOTES.md` is append-only.** Preserve the history; never rewrite prior entries.

### Good defaults (guidance, not commandments)

Suggestions with reasoning. The agent uses judgment when the situation differs:

- **Retry-then-hop on CI failures and `/code-review` findings.** Fix the obvious cause, retry. If the same failure persists after a couple of fix attempts, it's probably infrastructure flake or a deeper issue — log to `NOTES.md`, mark blocked, hop. *Why:* fixed retry counts force either premature give-up or futile retry loops; judgment beats a number.
- **Address review feedback inline, on the affected PR's own branch.** When a prior PR shows `CHANGES_REQUESTED`, read the comments, fix on that PR's branch, `ghstack submit` to restack, reply on the PR. *Why:* otherwise the loop pauses on every review and kills the autonomy property. The only literal halt-this-sub-goal phrase is *"do not proceed"*.
- **Prefer fix-up commits over amending earlier sub-goals' history.** When a later sub-goal finds a bug planted in an earlier one, add a fix-up commit on the current branch with a one-line note in the message. *Why:* amending an already-approved PR re-triggers review and churns reviewers. (Pushing review-feedback fixes to the *same PR's own branch* is fine and expected — the guidance is about not modifying earlier sub-goals' commits from a later sub-goal's branch.)
- **Pre-flight: before working a sub-goal, check whether its `Done =` is already true.** If so, check the box, log it, continue. *Why:* don't manufacture work the world already did.
- **Retry blocked sub-goals only when nothing else is workable.** Natural cooldown — make progress on whatever you can, circle back. *Why:* otherwise the loop burns turns on one stuck problem instead of accumulating progress.
- **Periodic heartbeat to `NOTES.md` when the loop's been running for hours with nothing else to log.** *Why:* the human returning after many hours wants a recent timestamp confirming the loop didn't die.

### `NOTES.md` is the audit trail

Append a one-line entry per notable event — sub-goal complete (PR # + wall time), reviewer feedback addressed (what + why), block encountered (what was tried, what's next), periodic heartbeat, cross-cutting decision, proposed new sub-goal (under `## Proposed additions`). Date each entry. The human reads `NOTES.md` top-to-bottom on return; aim for skimmable-in-30-seconds.

### Trust the agent

The skill gives shape; the agent provides judgment. Don't write exact retry counts, exact time intervals, exact command flags into the pointer prompt. If you find yourself writing *"exactly N retries"* or *"every N hours"* or a numbered 10-step recipe, you're micromanaging — restate as a directional principle (*"a couple of attempts before giving up"*, *"periodically"*) and trust the agent to read the situation. The pointer prompt should feel like a brief, not a procedure manual.

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
- `references/examples.md` — one worked mega-goal breakdown end to end.
