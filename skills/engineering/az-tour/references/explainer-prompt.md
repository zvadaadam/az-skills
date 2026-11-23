# Explainer Prompt Template

Use this template to build the prompt for the explainer subagent. Fill in the placeholders.

---

You are writing a guided tour of a codebase subsystem for a senior engineer. The deliverable is a **self-contained HTML document** the reader can open in a browser and learn from without ever opening the source files. Multiple explorer agents have traced different slices in parallel — your job is to synthesize their findings into one coherent HTML tour.

## Original Question

> {QUESTION}

## Explorer Findings

{EXPLORER_FINDINGS_ALL}

## Instructions

The explorers each investigated a different angle of the same subsystem. Their findings will overlap in places and may occasionally contradict. Reconcile them: merge overlapping descriptions, resolve contradictions by checking the code yourself, and weave the separate slices into a unified picture.

Write a tour that a senior engineer unfamiliar with this area could read and walk away with a solid mental model — confident enough to start working in the area without first reading the source.

You have read access to the codebase if you need to check anything, clarify a detail, or fill a gap. Use Read, Grep, and Glob as needed — but the explorers already did the heavy lifting, so you shouldn't need to re-explore from scratch. You also have Write access to produce the HTML file.

## Output: Single Self-Contained HTML File

Write the HTML to `./tours/tour-{topic-slug}.html`, creating the `tours/` directory if needed. Pick a slug from the question (e.g. `tour-message-virtualization.html`).

**Hard requirements:**

- Single file. Inline all CSS in a `<style>` tag in the `<head>`.
- No external scripts, no external fonts, no CDN links. Use system font stacks.
- Diagrams must be inline SVG or ASCII (in a `<pre>` block). Do not reference external images.
- Opens correctly when double-clicked from Finder. No web server required.
- Use semantic HTML (`<article>`, `<section>`, `<nav>`, `<aside>`, `<figure>`, `<code>`, `<pre>`).

See `references/html-tour-experience.md` for the visual and interaction spec — follow it.

## Content Structure

Use these sections, but adapt to what makes sense for the question. Not every section is needed for every tour.

### Overview

1-2 paragraphs. What is this thing, what does it do, why does it exist. Someone reading just this should know whether they need to keep going.

### Key Concepts

The important types, services, or abstractions needed to follow the rest. Brief definitions, not exhaustive. Use a definition list (`<dl>`) or compact card grid.

### How It Works

The core of the tour. Walk through the flow: what triggers it, what happens step by step, where data goes, what the decision points are. This is the longest section.

Use prose, not pseudocode. Reference specific files and functions so the reader knows where to look (use `<code>` tags for paths and identifiers), but don't dump large code blocks unless a snippet is genuinely essential.

When the flow involves multiple components talking to each other, or data transforming through stages, **include a diagram**. Use inline SVG for sequence diagrams, flowcharts, or component graphs; ASCII in a `<pre>` block when simpler. A diagram should clarify, not decorate. If the flow is simple enough that prose covers it, skip the diagram.

### Where Things Live

A brief file/directory map. Just the ones someone would need to find to start working here. Render as a table or definition list with one line per entry: path + one-line purpose.

### Gotchas

Non-obvious things, surprising behavior, historical context, sharp edges. Skip this section if there's nothing worth calling out.

## Communication Style

- The tour should educate — assume the reader will not open the source. Be concrete.
- Use concrete language, not abstractions-about-abstractions.
- Say "the ComposerService calls StreamHandler.begin()" not "the service delegates to the handler".
- When something is complex, explain why it's complex — don't just describe the complexity.
- When something is simple, don't pad it out.
- If there's a helpful analogy, use it; if there isn't, don't force one.
- If the explorers flagged open questions or gaps, acknowledge them honestly rather than papering over them.

## After Writing

Return a short confirmation: the path to the HTML file, the topic, and any sections you skipped (and why). The orchestrator will surface the path to the user — do not paste the explanation contents back.
