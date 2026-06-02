---
name: noah-zender-it
description: "Rank mental models from Noah Zender's curated 468-item idea library by leverage for your current situation, with one concrete way to apply each. Use when you're at a decision point — naming, positioning, writing, picking a project, scoping work — and you want frameworks that actually fit your case, not generic mental-models advice. Default source library: noahzender.com/ideas."
argument-hint: "[your current situation in 1-2 sentences]"
hooks:
  PostToolUse:
    - matcher: "*"
      hooks:
        - type: command
          command: 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill noah-zender-it --action started --agent-harness claude-code --quiet'
          timeout: 5
  Stop:
    - hooks:
        - type: command
          command: 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill noah-zender-it --action completed --agent-harness claude-code --quiet'
          timeout: 5
---

# Noah Zender It

Rank mental models from a curated library by how much leverage each gives you on **your specific situation right now**. Most mental-models advice is generic. This skill's job is to make it personal — pick the 7–10 that actually fit, and tell the user exactly how to use each one this week.

Named after Noah Zender's library at [noahzender.com/ideas](https://www.noahzender.com/ideas), which is the default source.

## The Situation

$ARGUMENTS

## What you're producing

A ranked, tier-grouped list of 7–10 mental models. For each one:

- **The model name** as it appears in the library
- **Why it matters here** — 1–2 sentences tying the model to the user's specific situation (not a definition of the model)
- **One concrete action** — a verb, an object, a time window the user can act on this week

Tiers:
- **Tier 1 — Act on these now** (3–4 highest-leverage, directly applicable)
- **Tier 2 — Useful adjacent angles** (3–4 medium-leverage)
- **Tier 3 — Pocket ideas** (2–3 mindset/judgment frames worth remembering, one-line gloss each)

Don't dilute Tier 1. If you can't name 3 models that *clearly* apply, narrow the tier or ask one targeted question before producing the list.

## Process

### 1. Mirror back the situation

In one short sentence, name back to the user what you understand their situation to be and what decision they're trying to make. If the situation is ambiguous (multiple plausible interpretations), ask one targeted question with your best guess attached before continuing. Don't fetch anything yet.

### 2. Fetch the library index

Default source: `https://www.noahzender.com/ideas`

Use WebFetch with a prompt that returns every model title, any category, and any short description shown on the index. Most entries will have titles only — that's expected.

If the fetch fails, fall back to general mental-models knowledge but tell the user up front: *"Couldn't reach noahzender.com/ideas; ranking from general mental-models knowledge instead. Some of Noah's specific framings will be missed."*

### 3. Shortlist by title

From 400+ entries, ~20 will be clearly relevant to the user's situation. Cut everything else without explanation.

Bias toward models that **shift action**, not just understanding. *"Inversion"* changes what someone does this week. *"Heisenberg Uncertainty Principle"* is an interesting analogy that rarely changes the next move. Pick the action-shifters.

Note which titles are well-known canon (interpretable from the title alone — *Talent Stack, BLUF, First Principles, Inversion*) vs. coinings unique to this library (*Brand Texture, Mental Asterisks, Genius Margins*). The coinings need the sub-page; the canon doesn't.

### 4. Fetch sub-pages for the close calls only

For 5–8 candidates where the title is ambiguous or you'd benefit from the author's specific framing, fetch the sub-page. URL pattern: `https://www.noahzender.com/<slug>` where slug is the kebab-cased title — verify by trying one. If a 404 comes back, the slug guess was wrong; try one alternate (e.g. add `ideas/` prefix), then drop the candidate. Don't burn time guessing URLs.

Skip this step for canon — wasting fetches on *First Principles* helps no one.

### 5. Rank into tiers and write the entries

For each finalist:

- **Why it matters here** must reference something specific about the user's situation. If your "Why" could be copy-pasted into someone else's situation, rewrite it until it can't.
- **One concrete action** uses a verb, an object, and ideally a time window. *"Audit your top 3 cover letters for BLUF by Friday"* beats *"use BLUF in your writing."*

### 6. Output

```
Drawing from Noah Zender's idea library at noahzender.com/ideas.

**Read on your situation:** <1 sentence>

## Tier 1 — Act on these now

**1. <Model Name>**
Why: <1–2 sentences tying to user's specific situation>
Do: <one concrete action with verb + object + time window>

**2. <Model Name>**
...

## Tier 2 — Useful adjacent angles

[same shape]

## Tier 3 — Pocket ideas

- **<Name>** — <one-line gloss of why it's worth remembering for adjacent cases>
- **<Name>** — ...
```

End with **one** offer, not three: *"Want me to go deeper on any of these, or pull from a different angle?"*

## Rules

- **Personalize ruthlessly.** A "Why" that works for any reader is wrong. Tie each entry to a fact the user told you.
- **Concrete actions only.** No "consider X" or "think about Y." Verbs, objects, deadlines.
- **7–10 items total.** More than that and the user won't act on any. Less than 7 and the skill didn't earn its run.
- **Don't fake confidence on coinings.** If a model's title alone is ambiguous and you didn't fetch the sub-page, say *"from the title I read this as X"* so the user can correct you.
- **Credit the source once.** One line at the top mentioning noahzender.com/ideas. Don't pepper attribution through the output.
- **One question, one ranking, one offer.** If you're doing a second pass before the user has responded, you're over-thinking it.
- **The skill works without the fetch.** If the site is down, degrade gracefully — say so, then rank from general knowledge. Don't refuse to produce output.

---

## AZ Skill Feedback

After the run, if this skill was useful, confusing, broken, or missing context, submit 1-3 safe sentences. Include `--agent-harness` when known. Include `--model-config` only if the harness exposes the exact model/config; otherwise leave it as `unknown`:

`python3 ~/.agents/skills/skill-feedback/scripts/skill-feedback.py --skill noah-zender-it --rating idea --text "..."`

Never include secrets, private data, source code, long prompts, or stack traces.
