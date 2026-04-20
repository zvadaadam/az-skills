# Deep lesson schema

A **deep lesson** is a chapter, not a card. Use it when the team's pain around a topic spans many commits, many team-written bullets, or both. Deep lessons are the book's center of gravity — readers skim the one-line lesson cards, but they *remember* the deep chapters.

## When to write a deep lesson

A topic deserves a deep lesson when it has **at least two of**:

- A dedicated section of the team's own notes (e.g. `docs/agents/lessons-learned.md`) with 4+ bullets
- A clear pressure loop in the commit record (10+ commits in one area over weeks)
- A hot file (top 5 in `top-files.tsv`) that keeps being rewritten
- A pivot or architectural bet whose consequences echo through later work

Short incidents, one-file fixes, or niche library gotchas belong in the "lessons at a glance" card grid — not here.

## Schema

```yaml
id: lesson-<slug>           # stable id for anchoring/linking
title: "..."                # the lesson stated as a headline, not a topic
one_liner: "..."            # one quotable sentence; the thing to remember
size: xl | l | m | s        # how much weight this lesson carries visually
problem: >
  2–3 sentences. What was the thing that kept breaking and why it was non-obvious.
  Name the actors (sandbox lifecycle, chat streaming, GitHub auth, etc.).
what_broke:                 # the symptoms — primary-source bullets, ideally quoted
  - "Symptom 1, grounded in a specific file/PR/bullet."
  - "Symptom 2."
  - "... (aim for 3–8 bullets; 1 bullet is fine for a small lesson)"
what_they_learned: >
  2–4 sentences. The resolution or discipline the team converged on. This is
  the answer, not a recap. Include the specific rule ("/api/sandbox/reconnect
  is a read-only probe", "persist at request start, not onFinish").
transferable: >
  1–2 sentences. The insight that generalizes beyond this repo. Readers
  forking the code will remember THIS paragraph.
evidence:                   # primary-source citations
  - "docs/agents/lessons-learned.md §Sandbox Lifecycle"
  - "#590 feat: add vercel base snapshot refresh tooling"
  - "apps/web/app/api/sandbox/route.ts (28 touches)"
```

## Size categories

| Size | When to use | Typical length |
|------|-------------|----------------|
| `xl` | Load-bearing lessons with the largest pressure loop in the repo | 6–8 what_broke bullets, ~600 char each section |
| `l`  | Big lessons backed by a team section or a major pivot | 4–6 bullets, ~450 chars |
| `m`  | Real lessons, grounded but narrower in scope | 3–4 bullets, ~400 chars |
| `s`  | Sharp, specific technical lessons | 1–3 bullets, terse |

The HTML renderer uses these to scale typography — big lessons look big, small lessons look small. Don't size-inflate a small lesson; it reads as padding.

## What makes a deep lesson good

- **Headline title.** "Sandbox lifecycle is infrastructure, not a feature" — not "Sandbox lifecycle."
- **Quotable one_liner.** A reader should be able to tweet it. "Any UI element that says `2:34 remaining` is making a claim about physics across two machines."
- **Specific what_broke bullets.** Paraphrase the team's own words where possible; each bullet names the thing that broke (a file, a call, a race).
- **`what_they_learned` states the rule.** "/api/sandbox/reconnect is a read-only probe" is a rule. "They fixed it" is not.
- **`transferable` earns its keep.** If the universal takeaway feels obvious, either cut it or rewrite until it carries weight.
- **Evidence cites primary sources.** PR numbers, file paths, team-doc section headings. Not vague pointers.

## What a deep lesson is NOT

- A summary of a single commit. (That's a commit note.)
- A list of symptoms without a settled resolution. (That's just the pain.)
- A restatement of the pressure loop. (Pressure loops describe the pattern; lessons describe the answer.)
- Interpretation with no provenance. (Deep lessons cite.)

See `sample-deep-lesson.md` for a filled example.
