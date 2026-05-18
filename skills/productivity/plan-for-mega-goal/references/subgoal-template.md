# Sub-goal file template

Each file under `goals/` IS a `plan-for-goal` output. **Read `../../plan-for-goal/SKILL.md` first** — that's the canonical spec for the anchors (`Goal`, `What great looks like`, `How to close the loop`, `Done =`, `Not`, `Open`, `Where to look`), their voice, and their rules.

**Delegation, not duplication.** This file describes only the deltas:

- **Four override rules** — `plan-for-goal` rules that change when applied per-sub-goal in a mega-goal context.
- **Two mega-goal-specific additions** — `Time budget:` (optional) and `## PR body` (required) — neither exists in `plan-for-goal`; both go at the end of every sub-goal file.

By pointing at `plan-for-goal`'s spec instead of restating its structure here, sub-goal files automatically inherit any improvements made to `plan-for-goal` — sharpen an anchor description there, every mega-goal benefits. Don't write the sub-goal anchor labels in this file; they live in `plan-for-goal`.

## Overrides — `plan-for-goal` rules that change for sub-goals

### "Under 4000 chars — hard limit" → does not apply

The 4000-char cap is enforced on the user-typed objective handed to `/goal`. Sub-goal files live on disk and get loaded as referenced files by the continuation template's completion audit. **No hard cap on a sub-goal file.** Keep them tight — padding compounds across however many turns the loop spends on this sub-goal — but you don't have to count characters. The cap moves to the pointer prompt, where it's easily met.

### "One objective, not a backlog" → applies per sub-goal, not to the mega-goal

The mega-goal IS a backlog by design; the roadmap structures it. The rule still applies inside each sub-goal: don't smuggle a backlog into a single sub-goal file. If a sub-goal has more than one `Done =` condition or describes multiple unrelated end-states, **split it** into two sub-goals on the roadmap.

### "Where to look — zones not paths" → still applies inside sub-goal files

Inside each sub-goal file, keep `Where to look:` as durable zone names (`the auth middleware`, `the integration test suite`) — same as `plan-for-goal`. The exception lives in the pointer prompt (not in sub-goal files), which must name `.megagoal/<slug>/ROADMAP.md` as an exact path because that path IS the durable artifact, not a current-state pointer that rots.

### `Done =` and `How to close the loop:` must be PR-specific and sub-goal-specific

`plan-for-goal`'s `Done =` is "any single boolean the completion audit maps evidence to," and `How to close the loop:` is "which commands the agent runs every iteration to verify the goal." For mega-goal sub-goals, both must be sharpened:

- **`Done =` must end with the literal clause:** *"PR opened via ghstack AND that PR's CI green AND /code-review on the PR clean."* Generic `CI green` is ambiguous — agents read it as local tests passing. The PR-specific phrasing mechanically ties box-checking to an actual open PR, not to a local change set.
- **`How to close the loop:` must include sub-goal-specific commands or surfaces** (specific test file, specific browser flow, specific CLI invocation, specific grep for an artifact's presence/absence) that prove THIS sub-goal's outcome — NOT generic `bun run test` / `pnpm test` / `cargo test`. Generic repo tests are a baseline gate, not sub-goal verification. A sub-goal without its own verification path gets marked "done" any time repo-wide tests are green, regardless of whether the sub-goal's actual work was done — exactly the failure mode that produced 34 minutes of local edits and zero PRs.

## Mega-goal-specific additions

Every sub-goal file ends with two things that don't exist in `plan-for-goal`:

### `**Time budget:**` (optional)

A line near the end of the sub-goal file. A soft target like `~30min` or `~2h`. If work runs long, the loop notes it in `NOTES.md` but doesn't stop — soft instrumentation for the human to spot sub-goals that ballooned. Use judgment for what "running long" means; a fixed multiplier would be the wrong shape here.

### `## PR body` (required)

This block is the template the loop substitutes into the GitHub PR description when opening the PR for this sub-goal. It exists because:

- **Reviewers see context without leaving the diff** — mega-goal slug, sub-goal NN of total, `Done =` line, dependencies, stack position. A reviewer opening PR #414 sees *"sub-goal 03 of 05 in `auth-rewrite`, depends on 02, blocks 04–05"* immediately.
- **The PR description becomes part of the engineering record.** Months later, anyone looking at the merged PR can trace back to the roadmap and sub-goal file that motivated it.
- **`## What changed` and `## Verification` stay next to the actual diff.** The agent fills them in from real evidence at PR-open time, not from intent.

Structure:

````markdown
## PR body

```markdown
**Part of mega-goal:** `<slug>` (sub-goal NN of <total>)
**Roadmap:** `.megagoal/<slug>/ROADMAP.md`
**Done =** <same Done = line as above, full sentence form>
**Stack:** <what this depends on (e.g. "sub-goal 02"); what this blocks (e.g. "sub-goals 04–05")>

## What changed
<2–3 bullets, filled by the agent from the actual diff>

## Verification
<the close-the-loop steps that were actually run, with results>
```
````

The static parts (mega-goal slug, sub-goal number/total, roadmap path, `Done =`, stack position) are pre-written during scaffolding. The agent only fills in `## What changed` and `## Verification` at PR-open time from real evidence.

## The `Done =` line lives in two places — both must agree

It appears in:

1. **The sub-goal file** (full sentence form, under `How to close the loop:` per `plan-for-goal`'s structure).
2. **The roadmap entry** for this sub-goal (compressed one-liner — `goals/NN-<slug>.md` — `Done =` ...).

The roadmap line is what the completion audit scans first; the sub-goal file is what it opens for surrounding context. **Both copies must agree.** If you tighten one, tighten the other in the same edit. Drift between them is the most common way a mega-goal loop quietly miscounts what's actually done.

## Voice and length

Match the worked examples in `../../plan-for-goal/references/examples.md` — sensory `What great looks like:` lines, audit-mappable `Done =` lines, generous `Not:` lists, `Open:` anchors that give the agent room to pick tactics. A sub-goal file that reads exactly like one of those examples plus a `Time budget:` line and a `## PR body` block is the target shape. Typical sub-goal file: under 1500 chars before the `## PR body` block.
