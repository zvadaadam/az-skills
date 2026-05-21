# `FEEDBACK.md` template

Append-only meta-feedback the agent records **during a run** about the mega-goal skill, tooling, and codebase friction it encountered. Not work items — meta about how the run itself went. The human reads `FEEDBACK.md` after the run and decides what to fold back into improvements to `plan-for-mega-goal`, related tooling, or the codebase.

## Exact structure (scaffolded by step 4)

```markdown
# <mega-goal-slug> — Skill / tooling / codebase feedback

Append-only. Observations recorded during this run that would help improve `plan-for-mega-goal` (the skill), related tooling, or the underlying codebase. Not work items for this mega-goal — this is meta about how the run went.

The human reads this on return and decides which items land back into the skill, tooling, or codebase as separate work.

## Categories

- **Workflow friction** — places the loop got stuck or did wasteful work that the skill should prevent.
- **Missing tools** — things that don't exist but would have helped (a workflow preflight check, a stack-state JSON command, a mirror-test harness, etc.).
- **Codebase structure issues** — folders/files that complicated the work and might benefit from refactoring (not part of this mega-goal's scope, but worth noting).
- **Skill bugs / contradictions** — pointer-prompt instructions that didn't help, contradicted each other, or led to wasteful loops.
- **Documentation gaps** — undocumented behavior the loop had to discover by trial.

## Entries

<append entries here, dated, with a category and a brief description>
```

## When to write an entry

**Do write** when the run surfaced something that:

- Wasted a real chunk of agent time and could have been prevented by a different skill instruction.
- Hit a tooling gap that recurs across runs (e.g., "no way to validate a workflow_dispatch reference before pushing it").
- Revealed a codebase structure that fights against the work (e.g., "shared/ mixes runtime and types — splitting would help").
- Required the agent to invent a workaround the skill should ideally encode.

**Don't write** for:

- Run-of-the-mill events. Those go in `NOTES.md`'s `## Event log`.
- Bug reports in the work-under-mega-goal (those belong in `## Proposed additions` in NOTES.md or the actual repo's issue tracker).
- Speculation about hypothetical improvements with no concrete evidence from this run.

## Entry format

```markdown
## 2026-05-18 16:11 — [workflow friction] release-sdk.yml dispatch loop

Sub-goal 02 dispatched `release-sdk.yml` 4 times over 2h before discovering the workflow has to exist on default branch before `workflow_dispatch` can target it. The pointer prompt's blocker fingerprint format helped after the fact, but the loop would have caught this in one turn if a `workflow preflight <file>` check existed. Suggested skill change: pre-flight rule for workflow_dispatch sub-goals — verify the workflow is on default-branch HEAD before attempting dispatch.
```

One paragraph per entry. Lead with the category in brackets. Include enough context that the human reading on return can decide whether to act on it.

## Why this is a separate file from `NOTES.md`

Different audience, different lifecycle.

- `NOTES.md` is for the **loop runner** — the human who's tracking this specific mega-goal. Mostly operational state.
- `FEEDBACK.md` is for the **skill maintainer** — the human (or future agent) who improves `plan-for-mega-goal`, the tooling around it, or the codebase. Mostly meta observations.

Cross-cutting them into one file means skill-maintainer items get buried in operational noise. Separate files keep each focused and let `grep -r FEEDBACK .megagoal/` across mega-goals return only the relevant signal when you're sharpening the skill.
