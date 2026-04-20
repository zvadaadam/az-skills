# HTML book experience

The HTML output should feel like an explorable engineering book.

## Recommended sections

1. Overview / thesis
2. How to read this book
3. Signals / stats
4. Timeline
5. Pivots
6. Pressure loops
7. Lessons at a glance (card grid)
8. **Deep lessons** (chapter-length, with its own sticky side-toc)
9. Subsystem arcs
10. Daily chapters
11. Commit explorer
12. Evidence / appendix

## Deep lessons layout

The deep lessons section is the book's center of gravity. Render it as chapters, not cards:

- Two-column layout on desktop: sticky left-side ToC (tracks scroll position, highlights active chapter) + main reading column (~720px max-width).
- Collapses to single column on mobile with the ToC becoming a top-of-section horizontal list.
- Each chapter has: kicker label, headline title, quotable one-liner (pull-quote style, accent-colored left border), then structured H4-divided subsections for "The problem", "What kept breaking" (bulleted with ✕ markers), "What they settled on" (boxed callout), "Why it matters beyond this codebase" (card-style pull-quote), and a monospace "Evidence: …" line.
- Use the lesson's `size` field (xl/l/m/s) to scale the H3 typography — a heavy lesson should look heavy.

## Design goals

- Elegant, calm visual design
- Strong typography and spacing
- Low-friction navigation
- Obvious distinction between summary and evidence
- Great scanability before deep reading

## Interaction goals

- Support a clear reading-mode switch when helpful: story / balanced / evidence
- Highlight the active section in navigation while the reader scrolls
- Search and filter commits
- Open commit details in-place
- Link to raw markdown notes
- Link to GitHub commits and PRs
- Make phase/day sections easy to jump to

## Failure mode to avoid

A page that is technically rich but emotionally flat. The user should feel like they are reading the engineering story of the repo, not browsing a log viewer.
