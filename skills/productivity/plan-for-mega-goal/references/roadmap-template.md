# `ROADMAP.md` template

The roadmap is the single source of truth for "what's done" in a mega-goal. The orchestration loop re-reads it every turn to find the next unchecked sub-goal. Keep it scannable — the loop spends real tokens reading this file on every continuation.

## Exact structure

```markdown
# <Mega-goal name>

<2–3 sentence directional outcome for the mega-goal as a whole. The shared destination, the shared quality bar in compressed form. Same shape as `plan-for-goal`'s "directional outcome" + "quality bar" anchors, but at the system level.>

## Quality bar

<2 opinionated sentences. The hell-of-a-thing line that anchors taste across all sub-goals. Inherited by each sub-goal; a sub-goal file can sharpen it but shouldn't contradict it.>

## Sub-goals

- [ ] **01 — <sub-goal name>** — `goals/01-<slug>.md` — `Done =` <one-line condition>
- [ ] **02 — <sub-goal name>** — `goals/02-<slug>.md` — `Done =` <one-line condition>
- [ ] **03 — <sub-goal name>** — `goals/03-<slug>.md` — `Done =` <one-line condition>
- [ ] ...

## Dependencies

<Required — list each sub-goal's blockers explicitly, even when obvious from numbered order:

- 01: none
- 02: 01
- 03: 02
- 04: 01 (can interleave with 02–03)
- 05: 01, 02, 03, 04

The loop reads this section every turn to find the next workable sub-goal when one is blocked — without it the loop can't reroute around problems. This is load-bearing for autonomous multi-day operation.>

## Done

`Done =` every box above is checked AND each sub-goal's `Done =` line is proven against current state. No exceptions.
```

## Why the `Done =` line lives on the roadmap as well as in the sub-goal file

The continuation template's completion audit derives requirements from referenced files. Putting each sub-goal's `Done =` directly on the roadmap means the audit can scan the roadmap and immediately enumerate what to verify, without opening every sub-goal file just to find the success condition. Sub-goal files hold the full context (5 anchors, scope edges, where to look); the roadmap holds the high-signal "what proves it done" lines.

Both copies of the `Done =` line must agree. If you tighten one, tighten the other in the same edit.

## Updating the roadmap

- **Checking a box**: replace `- [ ]` with `- [x]`. Nothing else changes on that line.
- **Adding a sub-goal**: only allowed *between loop runs*, with the user's explicit review. Adding mid-loop is forbidden — the agent's rule is to log to `NOTES.md` and stop.
- **Removing a sub-goal**: don't. If a sub-goal is no longer relevant (scope changed, work obviated by an earlier sub-goal), mark it `- [~]` with a one-line note in `NOTES.md` explaining why. Deleting rewrites history; the strikethrough preserves it.
- **Reordering mid-loop**: also don't. The numbered order is the loop's contract. If dependencies turn out wrong, log to `NOTES.md` under `## Proposed additions` (or a new `## Proposed dependency changes` heading) and continue with the existing order — the human reviews when they return.

## What does NOT go on the roadmap

- Implementation details — those live in sub-goal files.
- Discussion of trade-offs or alternatives — those go in `NOTES.md` as they come up.
- Progress narration ("working on this", "halfway done") — the boxes are the only progress signal. A half-checked box doesn't exist.
- Anything that describes *current* state of the code — paths, line numbers, file shapes. The roadmap is re-read every turn while the codebase mutates; current-state pointers rot.

The roadmap should fit on one screen for a typical mega-goal (3–8 sub-goals). If it sprawls, the mega-goal is probably too big and should be split into two separate mega-goals.
