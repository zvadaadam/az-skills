---
name: geo-optimize
description: Turn an ai-answer-audit into a prioritized plan to get a brand cited in AI answers (ChatGPT, Perplexity, Google AI Overviews). Acts only on the audit's affectable content layer — earned citations, your own pages, open territory — and never promises to move the model layer. User-run on an audit + your brand/URL; a one-shot plan, not citation monitoring.
disable-model-invocation: true
argument-hint: "[paste the ai-answer-audit output + your brand name/URL — optional: geography, competitors to displace]"
hooks:
  PostToolUse:
    - matcher: "*"
      hooks:
        - type: command
          command: 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill geo-optimize --event skill_activated --agent-harness claude-code --quiet'
          timeout: 5
---

# GEO Optimize

Turn an `ai-answer-audit` into a concrete plan to get a brand **cited** in AI answers. The audit diagnosed what an answer rested on; this acts on the one part you can change.

You consume the audit; you do not re-diagnose. **Act only on the content layer** — the affectable sources and domains. The **model layer** (the queries the model runs, its `model prior` claims) is intrinsic: it tells you which queries to target, but no content moves it, and you never promise a win there.

GEO is **entity-first, not page-first.** Most AI citations are earned on third-party sources — listicles, Reddit, review sites, primary docs — not on your own homepage. So the highest-leverage moves are usually getting *into* the sources that already won, not polishing your own site.

## What you need

- **The `ai-answer-audit` output** — its evidence ledger (Level + Authority + Influence per row), the `Ignored` "open territory" domains, and the model-layer query set.
- **The brand + canonical URL(s)** to get cited; optionally the target query, geography, and competitors to displace.

**Refuse without an audit.** Handed a raw AI answer and no audit, stop and say "run `ai-answer-audit` first." The audit is the single source of truth; never reconstruct a ledger here.

## The four levers

Every recommendation acts through exactly one lever, and names the **audit row** it acts on plus the **model-layer query** it answers:

- **A — Get cited** on a High/Medium-influence domain already driving the answer (earn a listing, review, or quote on the listicle, forum, or primary page that won). Usually the highest leverage — this is where most citations come from.
- **B — Fix open territory** — a page of yours that surfaced but fed nothing (`Ignored`): repair the intent mismatch, missing claim, or weak authority so the engine feeds from it. Lowest friction.
- **C — Open a lane** — target a model-layer query whose current winners are low-authority, with a primary-quality artifact (your own page, or for forum/Reddit-intent queries an indexable third-party thread). Cite the audit row the model actually *used* for that query and show its **authority** is low — a High-influence but low-authority winner is the prime C target (key on authority, not influence). If that query's used winners are high-authority, it isn't C — route to A or D.
- **D — Upgrade evidence** — turn a snippet-only High-influence seam *you control or can get content into* into open-page-worthy content.

**One lever per recommendation.** Never tag two (no `C/D`, no `A/C`); if two seem to apply the action is under-specified — split it into two rows. **A vs C:** A requires a domain that *already appears as an audit row driving the answer*; a domain or source type not in the ledger (Reddit, Wikipedia, G2, a fresh benchmark) is C, not A. A **competitor-owned snippet seam** is never D — use C (your own primary page) or A (earn a cite there). Tag only the *final* lever — never a compound like `D→C`; put any "looks-like-D-but-the-seam-isn't-mine" reasoning in a note, not the lever column.

## Workflow

1. **Ingest and validate the audit.** Confirm it has an evidence ledger (Authority + Influence tags), an open-territory / `Ignored` list, and the model-layer query set; quote all three into the plan header. Work from the audit — do not re-search by default (re-running engines is opt-in, tagged `rerun evidence` and dated). *Done when* all three are present; if any is missing, stop and ask the user to run/extend `ai-answer-audit`.
2. **Place the brand — exactly once.** Find the brand's domain in the audit: a **Driver** (High/Med/Low), **Open-territory** (surfaced but `Ignored`), or **Absent**. If **Absent**, Lever B is unavailable — all work is net-new via A/C/D, and you don't borrow another brand's `Ignored` rows; if the competitor to displace is also Absent, reframe the goal as *entering* the answer, not a head-to-head. *Done when* the brand carries exactly one label, citing the audit row(s).
3. **Run the crawler preflight.** For each brand URL: robots.txt isn't blocking GPTBot / ClaudeBot / PerplexityBot / Google-Extended; critical content is server-rendered HTML, not JS-only; CDN/WAF allows AI crawlers. *Done when* each URL is marked pass/fail — or, for a consumed-only audit with no crawler data, **required-but-unverified** (never a fabricated pass/fail); any fail becomes a Fast Win sequenced before on-page tactics (most sites silently fail here).
4. **Map each opportunity to exactly one lever.** *Done when* every opportunity names a single lever (A–D) + a specific **audit row number** (never `—`; a blank row doesn't trace — cut it or re-express it as a Lever C with its model-layer query) + the model-layer query it answers. The crawler-preflight gate is the sole exception — it carries no lever and row `—`, listing instead the rows it unblocks.
5. **Branch per engine.** Cited domains barely overlap across engines, so tag each recommendation by where it pays off — ChatGPT (Wikipedia/G2, encyclopedic neutrality, named authors), Perplexity (Reddit + recency / year-stamps), Google AIO (topical coverage + YouTube). *Done when* each recommendation states which engine(s) it moves; recency advice is engine-scoped, not blanket.
6. **Rank by leverage and write actions.** Leverage = the audit's influence rank × feasibility for this brand × durability. For the top 3–7, write a content or earned-citation action tied to an exact target page/claim, grouped **Fast Wins / Roadmap / Backlog**. Don't recommend debunked tactics (llms.txt does nothing for AI search; ranking #1 alone isn't enough). **Hub > leaf:** if the audit's search path marks a source as a **hub** (it seeded a downstream hop), rank it above a leaf citation of equal influence — a hub shapes which options get compared and on what terms, and can win *without being cited*; landing a specific, falsifiable, numeric, entity-named claim on a hub is usually Lever A or D. Caveat: seed leverage steers the decision *logic*, not the verdict — the durable play is a seed whose claim survives verification. *Done when* each action has an exact target and a checkable "done when" line, leverage-ranked.
7. **Name the model-layer wall and check honesty.** List the queries and `model prior` claims no content will move, as intel — not promised wins. *Done when* every recommendation traces to a row + lever + query, the brand is placed once, no action promises to move a `model prior` claim, and the audit's vocabulary is reused verbatim.

## Output format

Use this structure unless the user asks otherwise.

```markdown
## GEO Optimization Plan

**Brand / URL:** <brand> — <url>
**Target answer/query:** <the "best X" being competed for>
**Source audit:** <reference + date>  ·  **Search stance:** consumed-only | rerun-augmented
**Queries the model ran (model layer):** "<q1>", "<q2>", …

### Where you stand now
<Driver (High/Med/Low) | Open-territory | Absent> — tied to the audit row(s). One label, no hedging.

### Authority gap & preflight
- **Gap:** the High/Med-influence domains the answer leaned on that the brand is absent from.
- **Preflight:** per-URL pass/fail (GPTBot/ClaudeBot/PerplexityBot/Google-Extended; SSR vs JS-only; WAF). Fails → Fast Wins.

### Opportunity map
| Opportunity | Lever | Target query | Target domain/page | Audit row | Influence to capture | Engine(s) | Feasibility | Priority |
|---|---|---|---|---|---|---|---|---|

### Prioritized actions
Each line restates lever + audit row + query + engine inline (don't rely on the table above):
**Fast Wins** — <action · lever + audit row # · model-layer query · engine(s) · exact target claim/page · done-when (a brand-verifiable artifact-state; defer ranking/citation outcomes to the re-audit loop)>
**Roadmap** — <…>
**Backlog** — <…>

### Open-territory targets
The `Ignored` pages where the brand already surfaced but fed nothing — what intent/claim/spec to add so the engine feeds from it. Lowest-friction lane (your own URL).

### The model-layer wall
`model prior` claims + intrinsic query behavior that no content will move — targeting intel, explicitly not promised as wins.

### What this plan can't do
A point-in-time plan, not citation monitoring: it won't track share over time, prove an action worked, or watch competitors. GEO moves over ~6–12 months and share is volatile. To re-measure, re-run `ai-answer-audit` after shipping and diff it.

### Bottom line
The single highest-leverage move and why — which High-influence slot it touches.
```

Scale to the audit: a handful of opportunities for a thin audit, more for a rich one. Lead with the earned placement that touches the highest-influence driver.

## Honesty checks (run before returning)

- The brand is placed exactly once (Driver / Open-territory / Absent), citing an audit row.
- Every recommendation names exactly one lever + a specific audit row number + a model-layer query — anything untraceable (or row `—`, except the preflight gate) is invented; cut it or re-lever it.
- Every Lever D names a seam the brand controls or can place content into — a competitor/third-party domain re-levers to C or A.
- Every Lever C cites the audit row showing its current winners are low-authority.
- No product attribute, SKU, or competitor is claimed that the audit doesn't contain; for an Absent brand, product specifics are marked assumption-to-verify.
- No action promises to move a `model prior` or other model-layer item; the model-layer wall is stated.
- Preflight fails are sequenced before on-page tactics.
- The "what this plan can't do" boundary is present — the plan is never sold as monitoring.

---

## AZ Skill Feedback

After the run, if this skill was useful, confusing, broken, or missing context, submit 1-3 safe sentences. Include `--agent-harness` when known. Include `--model-config` only if the harness exposes the exact model/config; otherwise leave it as `unknown`:

`python3 ~/.agents/skills/skill-feedback/scripts/skill-feedback.py --skill geo-optimize --rating idea --text "..."`

Never include secrets, private data, source code, long prompts, or stack traces.
