# Worked examples

Three reference shapes of `/goal` prompts, one for each common kind of long-running work. **Study, don't copy** — the point is to calibrate voice and see how the five anchors flex per domain. Notice especially how the **close-the-loop** and the **`Done =`** line change shape depending on whether the work is a transformation, a creation, or an iteration.

---

## Example 1 — Code migration

**Intent:** Migrate our Express API to Hono.

```
**Goal:** Every endpoint currently served by our Express app is served by Hono with identical request/response behavior, validated route-by-route, with the Express path removed once parity holds.

**What great looks like:**
Boring. Symmetric. No "we'll fix this later" branches. Every Hono handler reads like the natural way to write that endpoint — not a translated Express handler in disguise. Tests don't change.

**How to close the loop:**
1. `pnpm test` — the existing integration suite hits real endpoints; every test must pass against Hono.
2. For each route migrated, capture a curl response from Express and from Hono side-by-side. Diff must be empty modulo timestamps.
3. Delete the Express handler only when its Hono counterpart has passing tests and the diff is clean.
4. Final check: `git grep -i "express"` returns nothing in `src/`.

**Done =** All routes served by Hono, integration suite green, no `express` imports in `src/`, `package.json` no longer depends on `express`.

**Not:** new endpoints, schema changes, switching the ORM, changing the test framework, touching auth middleware logic (only its wiring).

**Open:** how to structure Hono routes — per-file, grouped, router pattern — agent picks based on what's idiomatic in the codebase.

**Where to look:**
- `src/routes/` — Express route definitions
- `tests/integration/` — the parity suite
- `src/server.ts` — entry point
- Any existing Hono usage in the repo (`grep -r "hono"`)
```

**What works here:**
- Parity is the bar — close-the-loop is a *diff*, not a feel-test. That's the migration shape.
- `Done =` is auditable from filesystem state (no stale grep hits, no stale dependency).
- The `Not:` list pre-empts the obvious adjacent temptations a migration invites (schema cleanup, ORM swap).

---

## Example 2 — Feature build / prototype

**Intent:** Add a `journal` command to our internal CLI with weekly summaries.

```
**Goal:** Engineers can log a quick note with `our-cli journal "<thing>"`, and a `--summary` mode reads back a conversational recap of the last 7 days that sounds like a colleague, not a bot.

**What great looks like:**
Logging is one shot — type, hit enter, done. The summary is short, specific, conversational. It names what you actually did, not categories. If a week was thin, it says so honestly instead of padding.

**How to close the loop:**
1. `our-cli journal "fixed the SSO bug"` — confirm instant return, entry stored.
2. Log three entries across two days, then run `our-cli journal --summary --since=7d --dry-run`. Read the output aloud. Does it sound like a teammate's recap or like a bullet list dressed up? If the latter, the prompt or aggregation is wrong.
3. Run the summary on a week with one entry. The summary must not pretend the week was busy.
4. `cargo test` for new code paths.

**Done =** Capture <1s end-to-end, summary reads conversationally for both a busy and a thin week, tests green.

**Not:** team or shared feeds, web UI, editing entries (write-only is fine for v1), cross-machine sync.

**Open:** storage format (sqlite, JSON, whatever fits), LLM prompt for the summary, delivery channel for the Monday note.

**Where to look:**
- `src/commands/` — how other subcommands are wired
- `src/config.rs` — per-user storage conventions
- `prompts/` — existing LLM prompts to match voice
```

**What works here:**
- The quality bar is sensory and opinionated (*"like a teammate's recap, not a bullet list dressed up"*) — the agent has a feel-test it can apply during the loop.
- Close-the-loop step 2 is the **read-it-aloud test** — for taste-driven features, having a human-sensory verification step beats a green checkmark.
- The thin-week edge case in step 3 names the failure mode upfront so the agent doesn't ship a polished-looking-but-dishonest output.

---

## Example 3 — Iteration / optimization

**Intent:** Get our extraction prompt above 90% on the eval suite.

```
**Goal:** Our extraction prompt reaches ≥90% on the eval suite without regressing any category that already passes.

**What great looks like:**
Tight, surgical edits. No prompt-bloat — every added instruction earns its keep on the evals. The final prompt is shorter than three paragraphs and still legible to a human a month from now.

**How to close the loop:**
1. `pnpm eval` runs the full suite and prints per-category scores.
2. Identify failing categories, hypothesize a single edit, apply it, rerun. One change per iteration so we can see what helped.
3. After each round, log score deltas in `evals/CHANGELOG.md` with a one-line "why this changed".
4. A round that regresses a previously-passing category by >2% is reverted, no exceptions.

**Done =** Suite ≥90% overall, no category below its previous baseline by more than 2%, prompt under three paragraphs, CHANGELOG explains each scoring change.

**Not:** changing the eval suite, swapping the model, adding retrieval or tools, rewriting the prompt from scratch — this is iteration, not rebuilding.

**Open:** which categories to attack in which order, what edits to try, whether to add few-shot examples or rewrite instructions.

**Where to look:**
- `prompts/extract.md` — the prompt being optimized
- `evals/` — the suite and current scores
- `evals/CHANGELOG.md` — prior iteration notes (or create if missing)
```

**What works here:**
- `Done =` is a numeric, evidence-based bar — the most auditable shape `/goal` can have.
- The "one change per iteration" rule turns the loop into a controlled experiment instead of a guess-and-mash. The agent can attribute score moves.
- The revert rule is a guardrail against the classic optimization failure mode (gain on category A, silent regression on category B).

---

## Common patterns across all three

- **The `Done =` line is one boolean per anchor.** Not a paragraph. The completion audit maps evidence to each clause.
- **`Not:` is doing real work in every example.** It cuts off the loop's natural sprawl. The temptations differ per domain (schema cleanup for migrations, polish for prototypes, scope creep for optimizations), but the discipline is the same.
- **`Open:` is generous.** The agent picks tech, structure, ordering. The user picks the destination.
- **`Where to look:` points at 3-5 concrete files, not a general "the codebase".** The agent re-reads these every turn — make them count.
