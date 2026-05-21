# `NOTES.md` template

Three sections with different update semantics. The header itself explains the contract — both the loop and the human read it on every visit.

## Exact structure (scaffolded by step 4)

```markdown
# <mega-goal-slug> — NOTES

## Active blockers

<Updated in place. One line per active blocker. Bump `Last verified:` only when state changes or a fresh audit is requested. Resolved blockers move to the Event log with a resolution note.>

<None yet.>

## Proposed additions

<Append-only. Sub-goals the agent discovered but didn't work because they're not in the roadmap. The human reviews on return and extends the roadmap if appropriate.>

<None yet.>

## Event log

<Append-only. One line per notable event, dated. Sub-goal completions, reviewer feedback addressed, blocker resolutions, heartbeats, cross-cutting decisions, final summary blocks.>
```

## Why three sections (not one append-only file)

- **`## Active blockers` (updated in place).** Without an in-place section, every resume appends another identical "loop stopped because X is still blocked" summary — noise that obscures the actual event log. Bumping a timestamp is cheap; replicating context is wasteful.
- **`## Proposed additions` (append-only).** Discovered scope the agent didn't work. The human extends the roadmap on return, then re-pastes the pointer prompt to resume. Never deleted — preserved for audit.
- **`## Event log` (append-only).** The audit trail. Sub-goal completions with PR numbers, reviewer feedback addressed, blocker resolutions, heartbeats. The human reads top-to-bottom on return.

## Blocker fingerprint format

Every line in `## Active blockers` follows this shape:

```
- [blocked] sub-goal <NN>: <one-line failure description>. Prerequisite: <what must change before retry is meaningful>. Last verified: <ISO timestamp>.
```

The `Prerequisite:` field is the load-bearing part — it tells the next resume what to check before retrying. If the prerequisite hasn't changed since `Last verified:`, the loop knows the blocker still holds and skips the retry (just bumps the timestamp). When the prerequisite changes, the loop retries the sub-goal.

Examples:

- *"Prerequisite: `release-sdk.yml` exists on default branch."*
- *"Prerequisite: `WORKOS_PROD_KEY` secret added to repo."*
- *"Prerequisite: WorkOS upstream incident at status.workos.com is resolved."*
- *"Prerequisite: human approves the production deploy gate."*

A prerequisite must be checkable. *"Prerequisite: bug is fixed"* is too vague — restate as *"Prerequisite: `apps/backend/src/sso-callback.ts` no longer throws on replay"* (specific, verifiable).

## Resolution flow

When a blocker is resolved:

1. Remove its line from `## Active blockers`.
2. Append to `## Event log`: `## YYYY-MM-DD HH:MM — sub-goal NN unblocked: <how>` with a one-line note about what changed.
3. Retry the sub-goal on the next turn.

## What goes in `## Event log`

One-line entries, dated, no duplicates. Examples:

```markdown
## 2026-05-18 14:23 — 01 complete
PR #412 · CI green · /code-review clean · 12min wall

## 2026-05-18 17:31 — 02 reviewer feedback addressed
PR #413: NULL email_verified_at handling. Picked "error loudly" over silent backfill. Restacked 03+04 cleanly.

## 2026-05-19 08:14 — heartbeat
Sub-goal 04 in progress, attempt 2/3 on CI flake.

## 2026-05-19 11:30 — 04 unblocked
WorkOS upstream incident resolved (status page clean). Retrying.

## 2026-05-19 14:02 — Loop complete
**Outcome:** 5 of 5 sub-goals complete.
**PRs:** #412, #413, #414, #415, #416 — all CI green, /code-review clean, awaiting merge.
**Time:** 23h 47min wall.
**Blockers resolved during run:** 1 (sub-goal 04, WorkOS upstream incident).
```

The final summary block is always the last entry — it tells the returning human everything they need to know in 30 seconds.
