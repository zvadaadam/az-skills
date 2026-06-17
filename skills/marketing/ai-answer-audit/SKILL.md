---
name: ai-answer-audit
description: Audit an AI answer back to the searches, sources, citations, and assumptions behind it — which results actually shaped it, and which claims are unsupported model guesswork. Traces what the answer was based on; does not grade whether it is correct. User-run on an answer (with its question if available); read-only — never alters the answer.
disable-model-invocation: true
argument-hint: "[paste the AI answer to audit — with its question if you have it — or point at it above]"
hooks:
  PostToolUse:
    - matcher: "*"
      hooks:
        - type: command
          command: 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill ai-answer-audit --event skill_activated --agent-harness claude-code --quiet'
          timeout: 5
---

# AI Answer Audit

Reverse-engineer an answer back to its sources. Show exactly what evidence was available, which pieces most influenced the response, and which parts came from `model prior` — the model's own judgment, not visible source text.

This is an **audit**, not a defense. The job is to expose the chain — including the weak links — not to make the original answer look well-sourced.

An AI answer rests on **two layers**, and the audit keeps them apart:

- **Model layer** *(intrinsic — not optimizable)* — the queries the model formulated and whatever it answered from `model prior`. It comes from training, varies model-to-model, and no content change touches it; you only *observe* it.
- **Content layer** *(affectable)* — the pages and domains those queries surfaced and the answer leaned on. The only surface that publishing or earning citations can move.

Tag each driver's layer. The content layer is what someone could change to move the answer; the model layer is intel, not a lever. One nuance: a drill-down query (hop 2+) is a *hybrid* — the *decision* to ask is model-layer, but its *terms* can be content-seeded (it searched "Brand X" because a page named Brand X). That seeding is the rare seam where content steers the model layer; the search path is where you surface it.

## What you're auditing

The user points you at an AI answer — alongside the question that produced it, or pasted in after the fact. Audit whatever trail comes with it: the full searches and opened pages if they're in view, or just the answer text if that's all there is (then you're reconstructing — see audit modes below).

**Read-only on the answer.** Explain what the answer rested on; never rewrite, defend, or improve it. Nothing you produce should change the answer itself.

## First: establish the audit mode

State this up front in the output — it caps what the rest of the audit can claim.

- **Live transcript** — the queries *and their returned output* (result snippets, titles, URLs, and any opened-page text) are all printed in this conversation. Only here can you trace real evidence to what the answer actually saw.
- **Reconstructed** — only the final answer is available; the original tool calls are gone. You must rerun searches to approximate what was likely seen. Everything recovered this way is `rerun evidence`, dated, never presented as what the original run actually saw.
- **Mixed** — some tool output survives, some doesn't. Label each row by what's actually in view.

**Visibility is per-element, not per-conversation — check the results, not just the queries.** Most harnesses (ChatGPT, Codex, Claude Code sub-agents) print the search *query* — "Searched the web: \<query\>" — but collapse or omit the snippets, URLs, and page text it returned. Seeing the query is **not** seeing the results. That state is **Mixed** (queries visible, outputs missing) — the single most common real case, and the one that produces fabricated ledgers.

Do **not** assume that auditing your own answer from earlier in the same conversation is Live mode. It usually isn't: the queries get echoed back but the returned results are gone. For each query, look for its actual returned text in the transcript; if it isn't there, you did not see it — recover it by rerun (step 4), never from memory.

## Core rules

- **Never claim a page was read** unless it was actually opened/fetched — during the original answer or during this audit. A search-result snippet is not the page.
- **Tag every piece of evidence with its level:** `search result` (title/snippet only), `opened page` (fetched and read), `document/PDF`, `tool output` (non-web tool), `model prior` (knowledge, not a visible source), `rerun evidence` (recovered now, dated).
- **Never invent** quotes, snippets, rankings, timestamps, or influence. If a line can't be recovered, write `not visible in the transcript` — do not paraphrase from memory and present it as a source.
- **A visible query is not visible results — the phantom-results trap.** Seeing "Searched: \<query\>" tells you what was *asked*, never what came *back*. If a query's returned snippets/titles/URLs aren't printed in the transcript, you have not seen them: rerun the exact query to recover them as `rerun evidence` (dated), or mark them `not visible in the transcript`. Writing ledger rows that describe results you never actually saw — their "key quote," authority, influence — is the failure this skill exists to prevent, and it hides behind auditing your own recent answer.
- **The query text itself is evidence — read it for the prior shortlist.** Candidates named in the **first** query came from `model prior` (no result could have introduced them yet): search *verified* them, it didn't *discover* them — flag them as the model's prior shortlist and tag those hops **verification**. For a **later** query, first check whether an earlier hop's *result* already named the entity: if it did, that's **discovery** (content-seeded — a search-path edge), *not* a prior. Only an entity named in a query with no earlier result introducing it is prior shortlist. Where the shortlist came from is the highest-level *why this answer*, and it's invisible if you only read the citations.
- **Quote short and exact.** Only the phrase you need, usually **under 25 words** per source, then paraphrase. Quotes must be copyable verbatim from the source/transcript.
- **Judge authority explicitly.** Prefer official, primary, or directly relevant sources. Mark blogs, forums, ads, affiliate/comparison pages, and SEO content farms as lower-authority.
- **Separate evidence from interpretation.** A source can justify a factual premise ("switch X is hot-swappable") while the recommendation itself ("therefore it's best for you") still rests on judgment. Keep these in different columns.
- **"Discusses" is not "supports."** A source that mentions a product/option does not back every spec the answer gives about it. Map each *specific* claim to an exact quoted phrase from the source. If the phrase isn't there — even when the source is clearly on-topic, or attributes the spec to a *different* item — the claim is `model prior`, not sourced. Call this the **discusses-vs-supports trap** — the single easiest place to be fooled, and catching it is the highest-value thing the skill does.
- **The audit can disagree with the answer.** If the evidence doesn't actually support a claim, say so.

## Workflow

1. **Identify the target.** Quote the exact answer/claim under audit and the specific question the user wants explained. If they recommended several things, list each recommendation as its own claim.
2. **Set the audit mode** (above) and the date.
3. **Inventory every relevant search/tool call.** For each: the exact query or tool input; order/timestamp if known; returned URL + title + snippet, or the opened-page text; and **whether the content was actually visible to the agent at answer time**.
4. **Recover missing outputs by rerun — mandatory when a query is visible but its returned results are not.** This is the common ChatGPT/Codex/sub-agent case and the one that produces fake ledgers: the moment you have a query's exact text but can't see what it returned, rerun that exact query and read the real results instead of inventing snippets or guessing influence. Label every recovered row `rerun evidence` with today's date and present it only as what the query returns *now* — never as what the original run saw (the live answer and the rerun can disagree, and that gap is itself a finding). In genuine Live mode, don't rerun just to pad the ledger; in Reconstructed mode, rerun whatever queries you can recover.
5. **Build the evidence ledger** — one row per influential source or result (template below).
6. **Rank influence** for each claim using the counterfactual test (heuristics below). *Every* inventoried/rerun row gets an influence tag — High / Medium / Low / Ignored — including results that surfaced but fed nothing (`Ignored`). No row may be left untagged.
7. **Trace the reasoning chain** (and, when multi-hop, the **search path**). For *every* claim from step 1, write one line showing which ledger rows feed it and where source text stops and model judgment takes over (a claim with no backing row rests on `model prior` — say so). **Search path:** *only* when a query reused an entity/number/framing first seen in an earlier hop's result (the **token-carryover test** — not merely "more than one query ran"), draw forward edges `R<row> --seeds--> HOP<n>`, tag each node **hub** (seeded a later hop) / **leaf** (cited, seeded nothing) / **dead-end** (opened, neither), and mark each edge `[stated]` (the query literally carried the prior result's token) or `[inferred]`. A never-cited **hub** can be the highest-leverage node — flag it. If nothing passes the test, write "single-hop / prior-seeded — no search tree". In Reconstructed/Mixed mode seeding isn't recoverable — write "not recoverable" and never infer a tree from rerun data.
8. **Cross-check the specifics, then flag the unsupported.** Pull every concrete claim out of the answer — each spec, number, price, ranking, named feature, date, and superlative. For each, point to the exact quoted phrase that backs it. Anything left without a matching quote is `model prior` and goes in the unsupported section (the discusses-vs-supports trap — see Core rules).
9. **Split the two layers.** Sort the drivers into the **model layer** (the queries + every `model prior` claim — intrinsic; label that it varies by model) and the **content layer** (the influential sources). The content layer is the hand-off surface an optimizer could act on; the model layer is intel, not a lever.
10. **Run the honesty checks** before returning.

## Influence heuristics

Rank by the **counterfactual test**: *if this source vanished, would the answer change?*

- **High** — remove it and the main recommendation/conclusion changes or loses its basis. It directly shaped the headline answer.
- **Medium** — remove it and a caveat, exception, runner-up, or supporting point changes, but the headline survives.
- **Low** — redundant confirmation of something already established, background, or weak authority that merely echoed stronger sources.
- **Ignored** — surfaced by search but did not feed the recommendation at all. List these too; what got ignored is part of the audit. *Live mode only:* if you never saw the original results (Mixed/Reconstructed), you cannot know a source was ignored — label rerun-surfaced sources `surfaced / original influence unknown`, never `Ignored`.

Tie-breakers: a source actually **opened and quoted** outranks one seen only as a snippet; a **primary/official** source outranks a blog saying the same thing; a source that uniquely supplied a fact outranks one of many saying it.

Influence and evidence-level are **independent axes**. A snippet-only source can still be `High` influence if a recommendation leans on it — that's not a contradiction, it's a red flag. When a load-bearing claim rests on a source that was never opened, mark it High influence *and* call out in the bottom line that the answer is standing on unread text.

## Output format

Use this structure unless the user asks for something else.

```markdown
## AI Answer Audit

**Answer under audit:** "<exact quote of the recommendation/claim>"
**Question it answered:** <the user's original question>
**Audit mode:** Live transcript | Reconstructed | Mixed — <one line on what was/wasn't available; state explicitly whether the search *results* were visible or only the queries>
**Date:** <YYYY-MM-DD> (rerun evidence, if any, reflects this date)
**Queries the model ran (model layer):** "<q1>", "<q2>", … — intrinsic to this model; another model may search differently.

### Evidence ledger

| # | Source (title / URL) | Level | Surfaced by (query) | Key quote (≤25 words) | What it supported | Authority | Influence |
|---|----------------------|-------|---------------------|------------------------|-------------------|-----------|-----------|
| 1 | <title> — <url> | opened page | "<exact query>" | "<verbatim phrase>" | <claim it backs> | primary / blog / forum / ad | High |
| 2 | <title> — <url> | search result | "<exact query>" | not visible in the transcript | <…> | comparison page | Low |
| 3 | <title> — <url> | search result | "<exact query>" | "<verbatim phrase>" | — | forum | Ignored |

### Reasoning chain

- **<Claim 1>** ← rows [1, 4]. <How the source text maps to the claim. Where judgment filled a gap.>
- **<Claim 2>** ← row [2] + model prior. <…>

### Search path (only when multi-hop)
`R<row> --seeds--> HOP<n>` edges (reuse ledger row numbers); nodes tagged **hub** / **leaf** / **dead-end**; edges `[stated]` / `[inferred]`. A never-cited hub can be the highest-leverage node — flag it. Write "single-hop / prior-seeded — no search tree" when the token-carryover test fails; "not recoverable" in Reconstructed mode.

### Unsupported or weakly supported

- **<specific claim / number / ranking>** — <model prior | weak authority | not in any visible source>. <What it would take to confirm.>

### What couldn't be recovered

- <queries/outputs missing in Reconstructed mode, anything labeled "not visible in the transcript", and why it matters.>

### Two layers — what's affectable

- **Content layer (affectable):** <the sources/domains that actually drove the answer — the surface a content strategy could move>.
- **Model layer (intrinsic):** <the query strategy + `model prior` claims that drove it — fixed by this model, would differ elsewhere; intel, not a lever>.

### Bottom line

One or two sentences: how well-grounded is the answer overall, and which 1–3 sources (or which unverified assumption) is it really standing on?
```

Scale the ledger to the answer: 3–5 rows for a quick pick, more for a heavily-researched recommendation. Don't list every URL that ever appeared — list what influenced the answer, plus the notable `Ignored` ones.

## Honesty checks (run before returning)

- Every quote is copyable verbatim from the source/transcript.
- Every "opened page" row was actually fetched/read; snippet-only rows say `search result`.
- Audit mode is stated, and rerun rows are labeled and dated.
- No ledger row describes a search result whose returned text was never actually in view — every result row is either visible in the transcript or recovered by a dated rerun, never reconstructed from the query alone (the phantom-results trap).
- At least one claim is attributed to `model prior` if the answer contains specifics no source backs — if everything is conveniently "sourced," re-check, because real answers lean on priors.
- Every spec/number/price/ranking is matched to an exact quoted phrase — none waved through the discusses-vs-supports trap.
- Every driver is sorted into the model layer (queries + priors, intrinsic) or the content layer (sources, affectable), and the query set is shown as model layer.
- A search path is drawn only if a query passed the token-carryover test; every seed edge is `[stated]` or `[inferred]`, no tree is fabricated, and it's suppressed in Reconstructed mode.
- The influence ranking would survive the counterfactual test if challenged.
- Where the evidence is thin or contradicts the answer, the audit says so plainly rather than smoothing it over.

---

## AZ Skill Feedback

After the run, if this skill was useful, confusing, broken, or missing context, submit 1-3 safe sentences. Include `--agent-harness` when known. Include `--model-config` only if the harness exposes the exact model/config; otherwise leave it as `unknown`:

`python3 ~/.agents/skills/skill-feedback/scripts/skill-feedback.py --skill ai-answer-audit --rating idea --text "..."`

Never include secrets, private data, source code, long prompts, or stack traces.
