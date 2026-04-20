---
name: repo-history-book
description: Build a durable, evidence-backed "book" of how an engineering project evolved by mining git history, PRs, releases, and docs. Use when the user wants repository archaeology, commit-by-commit walkthroughs, engineering learning extraction, pivot analysis, or a readable chronology of what the team changed, learned, reverted, and refined over time.
---

# Repo History Book

Use this skill when the user wants more than a changelog:

- "walk me through how this repo evolved"
- "what did the engineers learn building this?"
- "turn the git history into a readable book"
- "go commit by commit / PR by PR"
- "extract pivots, aha moments, pain points, and refactors"

The core problem is **memory**. Do not rely on the model remembering hundreds of commits. Externalize state early and keep it hierarchical.

## Outcome

Produce a repository history "book" with:

1. **Exhaustive evidence store** — all commits, grouped into stable chunks
2. **Durable intermediate notes** — commit notes, day notes, phase notes, pivot notes
3. **Reader-facing output** — markdown and/or HTML that reads like a book, not a log dump
4. **Clear interpretation** — distinguish facts from inference, and explain what the team likely learned

In practice, the output should have **two lanes**:

- **Narrative lane** — the readable book: phases, pivots, subsystem arcs, pressure loops, lessons
- **Evidence lane** — the verification layer: commit explorer, raw notes, PR lists, tags, appendices

## Non-negotiable rules

- **Build the book in passes.** First produce durable evidence and notes; then do a second pass to improve readability, chaptering, and UI.
- **Keep a narrative lane and an evidence lane.** Readers should be able to skim the story or drill into proof.
- **Cross-link everything.** The final HTML should link back to day notes, phase notes, commit notes, PRs, and raw chapters.
- **Persist after every chunk.** Never keep important history analysis only in the model context.
- **Summarize hierarchically.** Commit → chunk/day → phase → book chapter.
- **Use stable chunking.** Chunks must be deterministic so work can resume later.
- **Keep provenance.** Every major claim should be traceable to commits/PRs.
- **Separate fact from inference.** "They changed X" is fact; "they learned Y" is interpretation.
- **Prefer breadth first, depth second.** First map the whole repo, then deepen important zones.
- **Use an orchestration protocol.** Large histories should be processed by stable passes and merged through note files, not by trying to remember prior analysis. See `references/orchestration-pattern.md`.

## Workflow

### Step 1 — Export the full history

Create a durable workspace, usually under `.context/history-book/`:

```text
.context/history-book/
├── exports/
│   ├── all-commits.json
│   ├── commits-by-day.json
│   ├── first-parent.json
│   ├── merged-prs.json
│   ├── tags.json
│   └── all-commits.tsv
├── chunks/
│   ├── chunks.json
│   └── chunk-0001.md
├── notes/
│   ├── commits/
│   ├── days/
│   ├── phases/
│   └── pivots/
├── book/
│   ├── index.md
│   ├── timeline.md
│   ├── lessons.md
│   └── appendix-commits.md
└── manifest.json
```

Use bundled scripts when possible. Paths are relative to the skill directory (e.g. `~/.claude/skills/repo-history-book/` after install, or `skills/engineering/repo-history-book/` in this repo):

```bash
# 1. Export git history into durable JSON/TSV
python3 "$SKILL_DIR/scripts/export_git_history.py" /path/to/repo --out .context/history-book/exports

# 2. Build stable chunks
python3 "$SKILL_DIR/scripts/chunk_history.py" \
    .context/history-book/exports/commits-by-day.json \
    --out .context/history-book/chunks/chunks.json

# 3. (later, after narrative/days/subsystems/deep_lessons.json exist) render the HTML book
python3 "$SKILL_DIR/scripts/build_book.py" --in .context/history-book --title "My Project"
```

If the repo has GitHub PR history available (via `gh`), the export captures it automatically. If `gh` is absent or unauthenticated, the script silently proceeds with git alone.

**Note on the workspace path.** `.context/history-book/` works out-of-the-box in Conductor (where `.context/` is gitignored by default). Outside Conductor, add `.context/` to your `.gitignore` before running, or choose a different output directory.

### Step 2 — Create stable chunks

Default chunking strategy:

1. Group by **calendar day**
2. If a day has more than ~25 commits, split into `day-part-a`, `day-part-b`, etc.
3. If the repo is sparse, chunk by **20–30 commits** instead

Do not invent ad hoc batches midstream. The chunk IDs must stay stable across resumptions.

See `references/chunking-strategy.md`.

### Step 3 — Write commit notes, not essays

For each commit in a chunk, write a compact structured note using the schema in `references/commit-note-schema.md`.

Focus on:

- what changed
- which subsystem changed
- whether this was feature / fix / refactor / infra / docs / rollback / brand / release
- why it matters in the broader story
- what pain point or learning it hints at

Keep each commit note short. The goal is durable memory, not prose polish.

### Step 4 — Merge commit notes into day notes

After finishing a chunk, immediately write or update:

- `notes/days/YYYY-MM-DD.md`
- `manifest.json`

A day note should answer:

- what happened on this day?
- what were the dominant themes?
- what pains were recurring?
- what new capability, refactor, rollback, or belief shift occurred?
- what might the team have learned?

Use `references/day-note-schema.md`.

### Step 5 — Build phase notes

Once day notes exist, group them into 4–8 larger **phases**. Good boundaries usually come from:

- major PR merges
- renames / rebrands
- subsystem deletions
- deployment model changes
- release-train bursts
- repeated fixes around the same incident class

Phase notes are where the repo starts to become readable as a narrative.

### Step 6 — Extract pivots and aha moments

Use the heuristics in `references/aha-heuristics.md`.

Especially look for:

- **add → fix → revert** loops
- repeated fixes in the same area within a few days
- deleting an entire subsystem
- adding CI/tests/compliance after instability
- docs/papers/legal pages appearing after technical churn
- renames that clarify positioning
- packaging/install work dominating feature work

These often reveal what the engineers actually learned.

### Step 7 — Write the book

The book is assembled from JSON files that live under `.context/history-book/book/`:

- `narrative.json` — thesis, phases, pivots, pressure_loops, lessons (card-sized)
- `days.json` — map of date → day summary (title, summary, themes, kind, key_commits)
- `subsystems.json` *(optional)* — array of subsystem arcs
- `deep_lessons.json` *(strongly recommended)* — chapter-length deep lessons (see Step 7a)

Once those JSON files exist, run the bundled renderer to produce a self-contained HTML artifact with navigation, search, and a commit explorer:

```bash
python3 "$SKILL_DIR/scripts/build_book.py" --in .context/history-book --title "My Project"
# opens: .context/history-book/book/index.html
```

The script works incrementally — if `deep_lessons.json` or `subsystems.json` are missing, those sections are hidden from the output and the nav. Re-run the script any time you update the underlying JSON.

The final book should usually have:

- **Overview** — one-paragraph read on what this repo became
- **How to read this book** — explain the narrative lane vs evidence lane
- **Timeline** — major phases
- **Pivots** — before/after moments
- **Pressure loops** — repeated pain patterns like packaging, billing, runtime, or rollback loops
- **Lessons at a glance** — one-card summaries for skimming
- **Deep lessons** — full chapters on the load-bearing lessons (see Step 7a)
- **Subsystem arcs** — how major components changed role over time
- **Daily / chunk notes** — exhaustive but skimmable
- **Appendix** — all commits / PRs / tags

See `references/book-outline.md`.

### Step 7a — Write deep lessons

The lesson cards above are easy to skim and easy to forget. The **deep lessons** chapter is the book's center of gravity — a small number of full chapters on the load-bearing things the team actually learned.

A topic deserves a deep lesson when it has at least two of:

- A dedicated section of the team's own notes (e.g. `docs/agents/lessons-learned.md`) with 4+ bullets
- A clear pressure loop in the commit record (10+ commits in one area over weeks)
- A hot file (top 5 in `top-files.tsv`) that keeps being rewritten
- A pivot or architectural bet whose consequences echo through later work

For each deep lesson, write: title (as a claim, not a topic), one quotable `one_liner`, `problem`, bulleted `what_broke` symptoms (grounded in primary sources), `what_they_learned` (the rule they converged on), `transferable` (the universal insight), and `evidence` (PR numbers, file paths, team-doc sections).

**Aim for 6–10 deep lessons. Fewer and the chapter is thin; more and the signal dilutes.** Use size categories (`xl` / `l` / `m` / `s`) so the heaviest lessons look heavy.

See `references/deep-lesson-schema.md` and `references/sample-deep-lesson.md`.

Two primary sources that will disproportionately feed this chapter:

1. **The team's own lessons doc.** Most projects that write one use a path like `docs/agents/lessons-learned.md`, `CONTRIBUTING.md`, or `docs/engineering-notes.md`. Grep for file names matching `lessons`, `learnings`, `postmortem`, `decisions` — if one exists, it is gold and the deep lessons should mostly trace back to its sections.
2. **The pressure loops you already identified.** Every pressure loop that lasted weeks is almost certainly a deep lesson waiting to be written.

### Step 8 — Do a second-pass review

The first build is rarely good enough. After generating the initial book/site, review it specifically for:

- Does it feel like a **book**, or just a dashboard?
- Is there a clear **reading path** for humans?
- Are the biggest **learning loops** obvious?
- Can a reader jump from prose to raw evidence in one click?
- Are the most important subsystem arcs clearly explained?

Use `references/output-review-checklist.md`. Patch the skill output and rerender.

## Interpreting responsibly

Do not overclaim motive. Use careful language:

- Good: "This suggests the team learned…"
- Good: "A plausible interpretation is…"
- Good: "The commit pattern implies…"
- Bad: "The team definitely believed…" unless documented explicitly

When uncertain, name the uncertainty.

## Orchestration pattern

For large repos, long-running work, or multi-agent execution, use the merge protocol in `references/orchestration-pattern.md`. The short version: one pass extracts notes, one pass merges them upward, one pass authors the book/site, and every pass reads from durable files rather than model memory.

## Resume strategy

When continuing work later:

1. Read `manifest.json`
2. Read the latest chunk note and the relevant day note
3. Read only the next unfinished export/chunk files
4. Continue from there

Do **not** reload the entire book into context unless necessary.

## Quality bar

A good result is:

- exhaustive in evidence
- layered in summary
- readable like a book
- honest about uncertainty
- explicit about lessons, pain loops, and pivots

A bad result is:

- one giant undifferentiated summary
- no durable notes
- no stable chunking
- no provenance
- treating every commit as equally important in the prose layer

## HTML expectation

When the user asks for HTML, prefer a polished interactive artifact with:

- section navigation
- chapter cards
- lesson cards
- phase timeline
- pivot cards
- pressure-loop cards
- searchable commit explorer
- raw-note backlinks

Use `references/html-book-experience.md`.
