# Sample deep lesson

A realistic filled example, following `deep-lesson-schema.md`. From the Open Agents history book — the load-bearing lesson about sandbox lifecycle.

```yaml
id: lesson-lifecycle
title: Sandbox lifecycle is infrastructure, not a feature
one_liner: >
  If users can walk away from your sandbox, you are running a distributed
  system — and every client-side heuristic is a liability.
size: xl
problem: >
  A Vercel sandbox can be created, used, hibernated, restored from snapshot,
  reconnected, expired, snapshotted-while-you-read, or silently killed while
  its command stream looks fine. Users leave tabs open for hours. Clients
  with stale clocks predict countdowns. Multiple UI elements (status chip,
  overlay, indicator dot) each have their own idea of whether the sandbox
  is alive. Every one of these is a place state can drift. Two full sections
  of the team's lessons-learned.md — ~35 bullet points — are dedicated to
  this single problem.
what_broke:
  - "Status chip showed `Paused` while the indicator dot stayed green — two
    components deriving from different heuristics."
  - "Reconnect polling was incorrectly refreshing `lastActivityAt`, so idle
    sessions never hibernated."
  - "Auto-resume fired on generic reconnect failures instead of only on
    confirmed `no_sandbox`, causing surprise resumes."
  - "`/api/sandbox/status` mutated runtime state from polling, downgrading
    active sessions to `no_sandbox` and later restoring from stale snapshots."
  - "Vercel `sdk.domain(port)` threw on restored sandboxes that had no route
    for a configured port — every preview-URL call could crash."
  - "Snapshotting a sandbox silently shut it down — the team had initially
    modeled snapshot as non-disruptive."
what_they_learned: >
  The only durable answer was to make the server the single source of truth.
  `/api/sandbox/status` became a DB-backed read-only view polled at a fixed
  cadence (~15s). `/api/sandbox/reconnect` became a read-only probe that does
  not mutate lifecycle. `hibernateAfter` and `sandboxExpiresAt` are server
  timestamps; the client only renders them. When the workflow path is
  unavailable, the status endpoint detects overdue `hibernateAfter` and
  kicks lifecycle as a safety net. The discipline: one endpoint mutates,
  one endpoint reads, and the UI is a dumb consumer of both.
transferable: >
  When a component has a lifecycle independent of the request that created
  it, you are running infrastructure. The temptation to predict transitions
  on the client is always wrong: client clocks drift, tabs sleep, predictive
  state contradicts reality within hours. Invest in a durable source of
  truth early — retrofitting it later costs roughly as much as every UI
  state you already shipped on top of the client-predictive version.
evidence:
  - "docs/agents/lessons-learned.md §Sandbox Lifecycle (13 bullets)"
  - "docs/agents/lessons-learned.md §Sandbox UI State (22 bullets)"
  - "#590 feat: add vercel base snapshot refresh tooling"
  - "apps/web/app/api/sandbox/route.ts (28 touches)"
```

## What this illustrates

- **The title is a claim, not a topic.** "Sandbox lifecycle is infrastructure" is something you can argue with — that's what makes it a lesson.
- **`one_liner` is quotable.** A reader remembers one sentence. Make it worth their memory.
- **`what_broke` bullets are paraphrased from the team's own doc.** Every symptom ties back to something verifiable: a file, a race, a named bug behavior.
- **`what_they_learned` names the rule.** "/api/sandbox/reconnect is a read-only probe" is the take-away, not "they fixed the reconnect logic."
- **`transferable` carries the generalization.** This paragraph is what a reader forking the code for a different product actually needs.
- **Evidence cites everything above.** Two doc sections, one PR, one hot file. A reader can verify in five clicks.

## Anti-examples

Don't write:

- `title: "Sandbox lifecycle issues"` — topic, not lesson.
- `one_liner: "The team had to deal with sandbox lifecycle bugs."` — not quotable, not an insight.
- `what_broke: ["There were many bugs in the lifecycle code."]` — not grounded, not specific.
- `what_they_learned: "They rewrote the lifecycle handling to be more robust."` — restates that they fixed it, doesn't state the rule.
- `evidence: ["The git log"]` — useless pointer.
