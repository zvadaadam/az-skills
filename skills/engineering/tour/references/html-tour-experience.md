# HTML tour experience

The HTML tour is the deliverable. It should feel like a polished engineering doc you'd happily send to a new teammate to onboard them onto a subsystem — calm, dense without being noisy, and structured so they can scan first and read deeply second.

## Hard constraints

- Single self-contained `.html` file. Inline CSS in a `<style>` tag in `<head>`.
- No external resources: no CDN scripts, no Google Fonts, no remote images.
- Diagrams are inline SVG or `<pre>` ASCII art.
- Opens by double-click in Finder. Works in Safari, Chrome, and Firefox.
- Optional `<script>` is fine, but only inline, and only for low-impact UX (smooth scroll, ToC active highlight, copy-to-clipboard on code). The page must remain fully readable with JS disabled.

## Page structure

```
<header>          ← title, one-line subtitle, generated date
<nav>             ← table of contents (sticky on desktop)
<main>
  <section>      ← Overview
  <section>      ← Key Concepts
  <section>      ← How It Works (longest; usually contains diagrams)
  <section>      ← Where Things Live
  <section>      ← Gotchas
</main>
<footer>          ← provenance: question that triggered the tour, files read
```

## Layout

- Two-column on desktop: sticky left ToC (~220px) + reading column (max-width ~760px).
- Collapses to single column under ~900px viewport. ToC becomes a small horizontal scroll list at the top of `<main>`, or a `<details>` block.
- Generous vertical rhythm: `1.6` line-height in body copy; `2rem`+ between major sections.
- Reading column never butts against the viewport edge — at least `1.5rem` of padding on small screens.

## Visual style

- **Calm and editorial.** Closer to a Stripe / Linear engineering blog post than a docs site.
- System font stack only:
  - Body: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
  - Code: `ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace`
- Light background (`#fafaf9` or pure white) with a single accent color used sparingly (links, active ToC item, pull-quote borders).
- Dark mode: support via `@media (prefers-color-scheme: dark)`. Don't ship a toggle.
- Headings: clear hierarchy via size and weight, not color. H1 ~2.25rem, H2 ~1.5rem with a top border-rule, H3 ~1.15rem bold.
- Code: subtle background tint, padded, monospace. Inline code uses the same tint at smaller padding.

## Components

- **Definition list (`<dl>`)** for Key Concepts — term in bold, indented one-line definition.
- **Where Things Live** as a table: file path (monospace) | one-line purpose.
- **Diagrams** as `<figure>` with optional `<figcaption>`. Diagrams sit at full reading-column width, with calm strokes (`#444` on light, `#bbb` on dark) and no fill noise.
- **Pull-quote / callout** for the most important sentence in a section: left border in the accent color, slightly larger text, italic optional.
- **Gotcha cards**: each gotcha as its own small card with a short headline and a 1-2 sentence body. Subtle warning tint (yellow-tinted background, not red — these are heads-ups, not errors).

## Diagrams

Prefer inline SVG over ASCII when:
- The relationships are 2D (sequences, flowcharts, component graphs)
- There are more than ~4 nodes or ~3 arrows

Use ASCII when:
- A single linear pipeline (`A → B → C`)
- A small file/directory tree
- A simple state list

Diagrams must be readable without color (use shape, position, line-style). Don't use color as the only signal.

## Interaction (optional, all inline)

- Sticky ToC on desktop with scrollspy: highlight the current section.
- Smooth-scroll anchor links.
- "Copy" affordance on code blocks (single inline script, ~20 lines).
- Collapsible `<details>` for less-essential subsections (e.g., a long Where Things Live list).

Do not add a search bar, theme toggle, or any feature that needs a backend.

## Failure modes to avoid

- A page that reads like a wiki dump: walls of bullet points with no narrative.
- A page that reads like a code listing: the whole point is the reader doesn't need the source.
- Decorative diagrams that don't clarify anything.
- "Color soup" — multiple accent colors competing for attention.
- Cramped layout: code blocks touching text, sections without breathing room.
- Missing the "why" — every component description should explain its purpose, not just its existence.
