# Sub-goal file template

Each file under `goals/` is shaped exactly like a `plan-for-goal` output. **Read `../../plan-for-goal/SKILL.md` first** — that's the canonical spec for the 5 anchors and the rules. This file only covers (a) the exact markdown structure of a sub-goal file and (b) the small list of `plan-for-goal` rules that change when applied per-sub-goal.

## Exact structure

```markdown
# <NN> — <sub-goal name>

**Directional outcome.** <2–3 sentences. What's true about the world when this sub-goal is done. Outcome, not a task list.>

**Quality bar.** <1–2 opinionated sentences. Inherits the mega-goal's quality bar from the roadmap; a sub-goal can sharpen it for its specifics but shouldn't contradict it.>

**How to close the loop.** <How the agent verifies, every iteration, that this sub-goal is working. Which commands, which surfaces (browser, simulator, CLI, tests). Use the self-verification tooling actually available — see `../../plan-for-goal/references/self-verification-tools.md`.>

`Done = <single boolean the completion audit maps evidence to. MUST include "CI green AND /code-review clean" — the loop will not check the box otherwise.>`

**Scope edges.** <What's in, what's not. The `Not:` list of adjacent tempting work — the highest-leverage anchor against sprawl.>

**Where to look.** <Zones, not paths. Skip if obvious from the sub-goal name.>

**Time budget.** <Optional. A soft target like `~30min` or `~2h`. If work runs long, the loop notes it but doesn't stop — soft instrumentation for the human to spot sub-goals that ballooned. Use judgment for what "running long" means; a fixed multiplier would be the wrong shape here.>

## PR body

<Required. This block is auto-substituted into the GitHub PR description when the loop opens the PR for this sub-goal. Pre-write the static parts during scaffolding; the agent fills in `## What changed` and `## Verification` from the actual implementation.>

```markdown
**Part of mega-goal:** `<slug>` (sub-goal NN of <total>)
**Roadmap:** `.megagoal/<slug>/ROADMAP.md`
**Done =** <same Done = line as above, full sentence form>
**Stack:** <what this depends on (e.g. "sub-goal 02"); what this blocks (e.g. "sub-goals 04–05")>

## What changed
<2–3 bullets, filled by the agent from the actual diff>

## Verification
<the close-the-loop steps that were actually run, with results — `npx workos test` ✓, `pnpm test` ✓, browser test recorded, etc.>
```
```

## Overrides from `plan-for-goal`

Three rules from `plan-for-goal/SKILL.md` need adjustment when writing a sub-goal file:

### "Under 4000 chars — hard limit" → does not apply to sub-goal files

The 4000-char cap is enforced on the user-typed objective handed to `/goal`. Sub-goal files live on disk; the continuation template loads them as referenced files during the completion audit. **There is no hard cap on a sub-goal file.** Still keep them tight — padding compounds across however many turns the loop spends on this sub-goal — but you don't have to count characters. The cap moves to the *pointer prompt*, where it's easily met.

### "One objective, not a backlog" → applies *per sub-goal*, not to the mega-goal

The mega-goal IS a backlog by design; that's why the roadmap exists. The rule still applies inside each sub-goal: don't smuggle a backlog into a single sub-goal file. If a sub-goal has more than one `Done =` condition, or its outcome describes multiple unrelated end-states, **split it** into two sub-goals on the roadmap.

### "Where to look — zones not paths" → still applies inside sub-goal files, but the pointer prompt is allowed one path

Inside each sub-goal file, keep `Where to look` as durable zone names (`the auth middleware`, `the integration test suite`) — same rule as `plan-for-goal`. The exception is the **pointer prompt**, which must name the exact path `.megagoal/<slug>/ROADMAP.md`. That path IS the durable artifact, not a current-state pointer that rots — the roadmap file is committed and stable across loop turns.

## What transfers from `plan-for-goal` untouched

- Directional, not prescriptive — describe the destination, let the agent pick the route.
- Re-readable cold — no "continue", "as discussed", "finish what's left". Each turn re-reads the sub-goal file from scratch.
- 2–4 sentences per anchor — padding compounds.
- Don't duplicate the harness — the continuation template already enforces completion audits, scope preservation, budget discipline. Don't restate.
- The `Done =` line is one boolean per clause, mapped to authoritative evidence.
- The `Not:` list does real work — it cuts off the loop's natural sprawl into adjacent tempting work.

## The `Done =` line is load-bearing — write it twice

The sub-goal's `Done =` line appears in two places:

1. **In the sub-goal file** under "How to close the loop" — full sentence form, with the evidence path made explicit.
2. **On the roadmap entry** for this sub-goal — compressed one-liner, scannable.

The roadmap line is what the completion audit scans first. The full sub-goal file is what it opens when it needs the surrounding context. **Both copies must agree.** If you tighten one, tighten the other in the same edit. Drift between them confuses the audit and is the most common way a mega-goal loop quietly miscounts what's actually done.

## Why the `## PR body` section exists

Every sub-goal file ends with a `## PR body` block. It's the template the loop substitutes into the GitHub PR description when opening the PR for this sub-goal. Three reasons it lives here:

- **Reviewers see context without leaving the diff.** They know which mega-goal this is part of, which sub-goal, what its `Done =` is, what depends on it. A reviewer opening PR #414 sees *"sub-goal 03 of 05 in `auth-rewrite`, depends on 02, blocks 04–05"* immediately.
- **The PR description becomes part of the engineering record.** Months later, anyone looking at the merged PR can trace back to the roadmap and sub-goal file that motivated it.
- **`## What changed` and `## Verification` live next to the actual diff.** The agent fills them in from real evidence at PR-open time, not from intent.

The static parts (mega-goal slug, sub-goal number/total, roadmap path, `Done =`, stack position) are pre-written when the sub-goal file is created during scaffolding. The agent only fills in `## What changed` and `## Verification` at PR-open time.

## Voice and length

Match the worked examples in `../../plan-for-goal/references/examples.md` — sensory quality bars, audit-mappable `Done =` lines, generous `Not:` lists. A sub-goal file that reads exactly like one of those examples is the target shape. A typical sub-goal file is under 1500 chars; if yours is much longer, check whether you're slipping prescriptive recipes into anchors that should be directional.
