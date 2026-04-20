#!/usr/bin/env python3
"""Assemble a self-contained HTML repo history book.

Reads durable notes + exports from a history-book directory and produces
a single-file HTML with:

  - Thesis / Overview
  - Timeline of phases
  - Pivots
  - Pressure loops
  - Lessons at a glance (card grid)
  - Deep lessons (chapter-length, with sticky side-toc)
  - Subsystem arcs
  - Daily chapters (searchable)
  - Commit explorer (searchable, sortable, paginated)

Inputs expected under --in:
  exports/all-commits.json       (required)
  exports/merged-prs.json        (required, may be [])
  exports/manifest.json          (required)
  book/narrative.json            (required)
  book/days.json                 (required)
  book/subsystems.json           (optional)
  book/deep_lessons.json         (optional; strongly recommended)

Usage:
  python3 build_book.py --in .context/history-book --out .context/history-book/book/index.html
  python3 build_book.py --in .context/history-book --title "Open Agents"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load(base: Path, rel: str, required: bool = True):
    p = base / rel
    if not p.exists():
        if required:
            sys.exit(f"error: required input missing: {p}")
        return None
    return json.loads(p.read_text())


def derive_title(manifest, narrative, cli_title):
    if cli_title:
        return cli_title
    if narrative and isinstance(narrative.get("project_name"), str):
        return narrative["project_name"]
    if manifest and isinstance(manifest.get("repo"), str):
        return Path(manifest["repo"]).name
    return "Repo History Book"


def derive_gh_base(prs):
    for p in prs or []:
        url = p.get("url") or ""
        if url.startswith("https://github.com/"):
            parts = url.split("/")
            if len(parts) >= 5:
                return "/".join(parts[:5])
    return ""


def slim(all_commits, merged_prs):
    slim_commits = [{
        "sha": c["short"],
        "full": c["sha"],
        "date": c["date"],
        "author": c["author"],
        "subject": c["subject"],
        "kind": "merge" if c.get("is_merge") else "commit",
        "top": c.get("top_levels", []),
        "files": c.get("file_count", 0),
        "ins": c.get("insertions", 0),
        "del": c.get("deletions", 0),
    } for c in all_commits]

    slim_prs = [{
        "number": p.get("number"),
        "title": p.get("title", ""),
        "mergedAt": (p.get("mergedAt") or "")[:10],
        "url": p.get("url", ""),
        "headRef": p.get("headRefName", ""),
    } for p in (merged_prs or [])]

    return slim_commits, slim_prs


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>__TITLE__ — Repo History Book</title>
<style>
:root {
  --bg: #fbf8f1;
  --bg-2: #f2ece1;
  --ink: #1a1b1f;
  --ink-soft: #4c4a45;
  --ink-faint: #7a776f;
  --accent: #b45309;
  --accent-soft: #e7c79a;
  --line: #dfd6c5;
  --card: #ffffff;
  --shadow: 0 1px 0 rgba(0,0,0,0.02), 0 8px 24px -16px rgba(30,20,10,0.15);
  --narrow: 760px;
  --wide: 1140px;
  --mono: 'JetBrains Mono', 'SF Mono', ui-monospace, Menlo, monospace;
  --serif: 'Iowan Old Style', 'Palatino', 'Charter', Georgia, serif;
  --sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #17161a; --bg-2: #1e1d22; --ink: #eceae3; --ink-soft: #b6b2a9;
    --ink-faint: #7e7b74; --accent: #f59e0b; --accent-soft: #634a1e;
    --line: #2b2a2f; --card: #1e1d22;
    --shadow: 0 1px 0 rgba(255,255,255,0.02), 0 8px 24px -16px rgba(0,0,0,0.5);
  }
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { background: var(--bg); color: var(--ink); font-family: var(--sans);
  font-size: 16px; line-height: 1.6; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }
a { color: var(--accent); text-decoration: none; border-bottom: 1px dotted var(--accent-soft); }
a:hover { border-bottom-style: solid; }
code, .mono { font-family: var(--mono); font-size: 0.92em; }
h1, h2, h3, h4 { font-family: var(--serif); font-weight: 600; line-height: 1.25; letter-spacing: -0.01em; }
h1 { font-size: 2.6rem; margin: 0 0 0.5rem 0; }
h2 { font-size: 1.7rem; margin: 3rem 0 1rem 0; }
h3 { font-size: 1.2rem; margin: 1.5rem 0 0.5rem 0; font-family: var(--sans); letter-spacing: 0; }

.container { max-width: var(--wide); margin: 0 auto; padding: 0 2rem; }
.prose { max-width: var(--narrow); margin: 0 auto; }

header.hero { padding: 5rem 2rem 3rem; border-bottom: 1px solid var(--line);
  background: linear-gradient(180deg, var(--bg-2) 0%, var(--bg) 100%); }
.hero .kicker { font-family: var(--mono); font-size: 0.72rem; text-transform: uppercase;
  letter-spacing: 0.18em; color: var(--ink-faint); margin-bottom: 1rem; }
.hero .subtitle { color: var(--ink-soft); font-size: 1.1rem; margin-top: 0.5rem; max-width: 700px; }
.hero .stats { display: flex; gap: 2.5rem; flex-wrap: wrap; margin-top: 2rem;
  font-family: var(--mono); font-size: 0.85rem; color: var(--ink-soft); }
.hero .stats .n { color: var(--ink); font-weight: 600; font-size: 1.1rem; display: block; }
.hero .stats .l { text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.7rem; color: var(--ink-faint); }

nav.toc { position: sticky; top: 0; z-index: 10; background: rgba(251, 248, 241, 0.92);
  backdrop-filter: saturate(180%) blur(12px); -webkit-backdrop-filter: saturate(180%) blur(12px);
  border-bottom: 1px solid var(--line); }
@media (prefers-color-scheme: dark) { nav.toc { background: rgba(23, 22, 26, 0.92); } }
nav.toc .inner { max-width: var(--wide); margin: 0 auto; padding: 0.8rem 2rem;
  display: flex; gap: 1.5rem; overflow-x: auto; scrollbar-width: none; font-size: 0.85rem; }
nav.toc .inner::-webkit-scrollbar { display: none; }
nav.toc a { color: var(--ink-soft); border: none; white-space: nowrap; padding: 0.25rem 0; position: relative; }
nav.toc a:hover, nav.toc a.active { color: var(--ink); }
nav.toc a.active::after { content: ''; position: absolute; left: 0; right: 0; bottom: -0.8rem;
  height: 2px; background: var(--accent); }

section.block { padding: 3rem 2rem; border-bottom: 1px solid var(--line); }
section.block:last-child { border-bottom: none; }
.section-kicker { font-family: var(--mono); font-size: 0.7rem; text-transform: uppercase;
  letter-spacing: 0.2em; color: var(--ink-faint); margin-bottom: 0.25rem; }
.lead { font-family: var(--serif); font-size: 1.25rem; line-height: 1.55;
  color: var(--ink-soft); margin: 1.5rem 0; }

.cards { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); margin-top: 1.5rem; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 10px;
  padding: 1.25rem; box-shadow: var(--shadow); }
.card h3 { margin-top: 0; }
.card .meta { font-family: var(--mono); font-size: 0.72rem; color: var(--ink-faint);
  text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.6rem; }
.card p { margin: 0.5rem 0; }
.card .body { color: var(--ink-soft); }
.tags { display: flex; flex-wrap: wrap; gap: 0.3rem; margin-top: 0.8rem; }
.tag { display: inline-block; padding: 0.12rem 0.55rem; border-radius: 99px;
  background: var(--bg-2); color: var(--ink-soft); font-size: 0.75rem;
  font-family: var(--mono); letter-spacing: 0.02em; border: 1px solid var(--line); }
.tag.accent { background: var(--accent-soft); color: var(--ink); border-color: transparent; }

.timeline { position: relative; margin: 2rem 0; padding-left: 2rem; }
.timeline::before { content: ''; position: absolute; left: 0.4rem; top: 0.5rem; bottom: 0.5rem;
  width: 2px; background: var(--line); }
.phase { position: relative; margin-bottom: 2rem; }
.phase::before { content: ''; position: absolute; left: -1.9rem; top: 0.4rem; width: 0.9rem; height: 0.9rem;
  background: var(--accent); border: 3px solid var(--bg); border-radius: 50%; box-shadow: 0 0 0 1px var(--accent); }
.phase .dates { font-family: var(--mono); font-size: 0.78rem; color: var(--ink-faint);
  text-transform: uppercase; letter-spacing: 0.1em; }
.phase h3 { font-family: var(--serif); font-size: 1.35rem; margin: 0.1rem 0 0.4rem 0; letter-spacing: -0.01em; }
.phase .summary { color: var(--ink-soft); margin: 0.4rem 0; }
.phase .prs { font-family: var(--mono); font-size: 0.8rem; color: var(--ink-faint); margin-top: 0.6rem; }

.pivot-grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
.pivot { background: var(--card); border: 1px solid var(--line); border-radius: 10px;
  padding: 1.25rem; box-shadow: var(--shadow); }
.pivot .when { font-family: var(--mono); font-size: 0.72rem; color: var(--accent);
  text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.4rem; }
.pivot h3 { margin: 0 0 0.8rem 0; font-family: var(--serif); font-size: 1.2rem; }
.pivot .before, .pivot .after { padding: 0.6rem 0.8rem; border-left: 3px solid var(--line);
  margin: 0.5rem 0; color: var(--ink-soft); font-size: 0.95rem; }
.pivot .after { border-left-color: var(--accent); }
.pivot .before::before { content: 'Before · '; font-family: var(--mono); font-size: 0.7rem;
  text-transform: uppercase; letter-spacing: 0.1em; color: var(--ink-faint); }
.pivot .after::before { content: 'After · '; font-family: var(--mono); font-size: 0.7rem;
  text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent); }
.pivot .ev { font-family: var(--mono); font-size: 0.78rem; color: var(--ink-faint); margin-top: 0.7rem; }

.explorer { margin-top: 1rem; }
.explorer-controls { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-bottom: 1rem; }
.explorer-controls input, .explorer-controls select {
  padding: 0.5rem 0.75rem; border: 1px solid var(--line); border-radius: 6px;
  background: var(--card); color: var(--ink); font-family: var(--mono); font-size: 0.88rem;
}
.explorer-controls input { flex: 1; min-width: 200px; }
.commit-table { width: 100%; border-collapse: collapse; font-family: var(--mono); font-size: 0.82rem; }
.commit-table thead th { text-align: left; font-family: var(--sans); font-weight: 600;
  font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--ink-faint);
  padding: 0.5rem 0.6rem; border-bottom: 2px solid var(--line); background: var(--bg-2); }
.commit-table td { padding: 0.45rem 0.6rem; border-bottom: 1px solid var(--line); vertical-align: top; }
.commit-table tr:hover td { background: var(--bg-2); }
.commit-table .sha { color: var(--accent); font-weight: 500; }
.commit-table .date { color: var(--ink-faint); white-space: nowrap; }
.commit-table .subj { color: var(--ink); font-family: var(--sans); font-size: 0.92rem; }
.commit-table .tops { color: var(--ink-faint); font-size: 0.72rem; }

.days-grid { display: grid; gap: 0.5rem; margin-top: 1rem; }
.day { background: var(--card); border: 1px solid var(--line); border-radius: 8px;
  padding: 0.75rem 1rem; display: grid; grid-template-columns: 110px 1fr auto; gap: 1rem; align-items: start; }
.day .date { font-family: var(--mono); font-size: 0.8rem; color: var(--ink-faint); }
.day .title { font-weight: 600; color: var(--ink); }
.day .summary { color: var(--ink-soft); font-size: 0.88rem; margin-top: 0.25rem; }
.day .meta { font-family: var(--mono); font-size: 0.72rem; color: var(--ink-faint); text-align: right; white-space: nowrap; }
.day .kind-pill { display: inline-block; padding: 0.1rem 0.5rem; border-radius: 4px;
  font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; }
.kind-foundation, .kind-scaffolding { background: #e0f2fe; color: #075985; }
.kind-feature-push { background: #dcfce7; color: #166534; }
.kind-stabilization { background: #fef3c7; color: #854d0e; }
.kind-refactor { background: #e9d5ff; color: #6b21a8; }
.kind-docs { background: #f3f4f6; color: #374151; }
.kind-rebrand { background: #fecaca; color: #991b1b; }
.kind-release { background: #bfdbfe; color: #1e40af; }
.kind-rollback { background: #fee2e2; color: #991b1b; }
.kind-quiet { background: var(--bg-2); color: var(--ink-faint); }
@media (prefers-color-scheme: dark) {
  .kind-foundation, .kind-scaffolding { background: #0c4a6e; color: #bae6fd; }
  .kind-feature-push { background: #14532d; color: #bbf7d0; }
  .kind-stabilization { background: #713f12; color: #fde68a; }
  .kind-refactor { background: #4c1d95; color: #e9d5ff; }
  .kind-docs { background: #374151; color: #e5e7eb; }
  .kind-rebrand { background: #7f1d1d; color: #fecaca; }
  .kind-release { background: #1e3a8a; color: #bfdbfe; }
  .kind-rollback { background: #7f1d1d; color: #fecaca; }
}

/* Deep lessons */
.deep-layout { display: grid; grid-template-columns: 240px 1fr; gap: 3rem; margin-top: 2rem; align-items: start; }
.deep-toc { position: sticky; top: 70px; padding: 1rem 0; font-size: 0.85rem; border-left: 2px solid var(--line); }
.deep-toc a { display: block; padding: 0.35rem 0 0.35rem 1rem; color: var(--ink-soft); border: none;
  border-left: 2px solid transparent; margin-left: -2px; line-height: 1.35; }
.deep-toc a:hover { color: var(--ink); }
.deep-toc a.active { color: var(--accent); border-left-color: var(--accent); font-weight: 500; }
.deep-chapters { max-width: 720px; }
.deep-chapter { margin-bottom: 4rem; padding-bottom: 3rem; border-bottom: 1px solid var(--line); }
.deep-chapter:last-child { border-bottom: none; }
.deep-chapter .dc-kicker { font-family: var(--mono); font-size: 0.7rem; text-transform: uppercase;
  letter-spacing: 0.2em; color: var(--ink-faint); margin-bottom: 0.5rem; }
.deep-chapter h3 { font-family: var(--serif); font-size: 1.8rem; margin: 0 0 0.6rem 0;
  letter-spacing: -0.01em; line-height: 1.2; color: var(--ink); }
.deep-chapter .one-liner { font-family: var(--serif); font-size: 1.15rem; font-style: italic;
  color: var(--accent); margin: 1rem 0 1.5rem 0; padding: 0.6rem 0 0.6rem 1.2rem;
  border-left: 3px solid var(--accent); line-height: 1.45; }
.deep-chapter h4 { font-family: var(--sans); font-size: 0.78rem; text-transform: uppercase;
  letter-spacing: 0.16em; color: var(--ink-faint); margin: 1.8rem 0 0.6rem 0; font-weight: 600; }
.deep-chapter p { color: var(--ink-soft); margin: 0.5rem 0 1rem 0; line-height: 1.65; }
.deep-chapter ul.what-broke { padding-left: 0; list-style: none; margin: 0.5rem 0 1.5rem 0; }
.deep-chapter ul.what-broke li { padding: 0.5rem 0 0.5rem 1.4rem; position: relative; color: var(--ink-soft);
  font-size: 0.95rem; line-height: 1.55; border-bottom: 1px dashed var(--line); }
.deep-chapter ul.what-broke li:last-child { border-bottom: none; }
.deep-chapter ul.what-broke li::before { content: '\2715'; position: absolute; left: 0; top: 0.55rem;
  color: var(--accent); font-size: 0.8rem; font-weight: 600; }
.deep-chapter .settled { background: var(--bg-2); border-left: 3px solid var(--accent);
  padding: 1rem 1.2rem; border-radius: 0 6px 6px 0; margin: 0.5rem 0 1.5rem 0; }
.deep-chapter .settled p { margin: 0; color: var(--ink); }
.deep-chapter .transferable { font-family: var(--serif); font-size: 1.05rem; line-height: 1.55;
  color: var(--ink); margin: 1.5rem 0; padding: 1rem 1.2rem; border: 1px solid var(--line);
  border-radius: 6px; background: var(--card); box-shadow: var(--shadow); }
.deep-chapter .evidence { font-family: var(--mono); font-size: 0.78rem; color: var(--ink-faint);
  padding: 0.8rem 0; margin-top: 1rem; border-top: 1px dashed var(--line); line-height: 1.55; }
.deep-chapter .evidence strong { color: var(--ink-soft); font-weight: 500; }
.deep-chapter.size-xl h3 { font-size: 2rem; }
.deep-chapter.size-s h3 { font-size: 1.5rem; }

@media (max-width: 900px) {
  .deep-layout { grid-template-columns: 1fr; }
  .deep-toc { position: static; border-left: none; border-top: 2px solid var(--line); padding: 1rem 0; }
  .deep-toc a { padding: 0.35rem 0; border-left: none; margin-left: 0;
    border-bottom: 2px solid transparent; display: inline-block; margin-right: 0.8rem; }
  .deep-toc a.active { border-bottom-color: var(--accent); border-left-color: transparent; }
}

footer { text-align: center; padding: 3rem 2rem; color: var(--ink-faint); font-size: 0.85rem; }

@media (max-width: 720px) {
  .day { grid-template-columns: 1fr; }
  .day .meta { text-align: left; }
  h1 { font-size: 2rem; }
  .hero { padding: 3rem 1.25rem 2rem; }
  section.block { padding: 2rem 1.25rem; }
}
</style>
</head>
<body>

<header class="hero">
  <div class="container">
    <div class="kicker">A Repo History Book</div>
    <h1>__TITLE__</h1>
    <div class="subtitle" id="thesis"></div>
    <div class="stats" id="stats"></div>
  </div>
</header>

<nav class="toc">
  <div class="inner">
    <a href="#overview">Overview</a>
    <a href="#timeline">Timeline</a>
    <a href="#pivots">Pivots</a>
    <a href="#pressure">Pressure Loops</a>
    <a href="#lessons">Lessons</a>
    <a href="#deep-lessons">Deep Lessons</a>
    <a href="#subsystems">Subsystems</a>
    <a href="#days">Days</a>
    <a href="#explorer">Commit Explorer</a>
  </div>
</nav>

<main class="container">

<section class="block" id="overview">
  <div class="section-kicker">01 · Overview</div>
  <h2>Thesis</h2>
  <div class="prose">
    <p class="lead" id="overview-thesis"></p>
    <h3>How to read this book</h3>
    <p id="reading-guide"></p>
  </div>
</section>

<section class="block" id="timeline">
  <div class="section-kicker">02 · Timeline</div>
  <h2 id="timeline-title">Phases</h2>
  <div class="prose"><p class="lead" id="timeline-lead"></p></div>
  <div class="timeline" id="phases"></div>
</section>

<section class="block" id="pivots">
  <div class="section-kicker">03 · Pivots</div>
  <h2>Before and after</h2>
  <div class="prose">
    <p class="lead">These are the moments where the repo changed shape. Each one is anchored in a specific commit or PR.</p>
  </div>
  <div class="pivot-grid" id="pivot-grid"></div>
</section>

<section class="block" id="pressure">
  <div class="section-kicker">04 · Pressure Loops</div>
  <h2>What the team kept fixing</h2>
  <div class="prose">
    <p class="lead">Repeated clusters of commits in the same area over time. These are where the lessons live.</p>
  </div>
  <div class="cards" id="pressures"></div>
</section>

<section class="block" id="lessons">
  <div class="section-kicker">05 · Lessons</div>
  <h2>Lessons at a glance</h2>
  <div class="prose">
    <p class="lead">Hedged interpretations grounded in the commit record. For the in-depth chapter on each, see <a href="#deep-lessons">Deep Lessons</a> below.</p>
  </div>
  <div class="cards" id="lessons-list"></div>
</section>

<section class="block" id="deep-lessons">
  <div class="section-kicker">05b · Deep Lessons</div>
  <h2>What the team actually learned, in depth</h2>
  <div class="prose"><p class="lead" id="deep-intro"></p></div>
  <div class="deep-layout">
    <aside class="deep-toc" id="deep-toc"></aside>
    <div class="deep-chapters" id="deep-chapters"></div>
  </div>
</section>

<section class="block" id="subsystems">
  <div class="section-kicker">06 · Subsystems</div>
  <h2>How the pieces evolved</h2>
  <div class="prose">
    <p class="lead">The top subsystems in the repo, each with its own arc.</p>
  </div>
  <div class="cards" id="subsystems-list"></div>
</section>

<section class="block" id="days">
  <div class="section-kicker">07 · Daily Chapters</div>
  <h2>Every active day, summarized</h2>
  <div class="prose">
    <p class="lead"><span id="day-count"></span> active days. Skim by kind (colored pill) or title.</p>
  </div>
  <div class="explorer-controls">
    <input id="day-search" type="search" placeholder="Filter days by title, theme, or date…"/>
    <select id="day-kind-filter"><option value="">All kinds</option></select>
  </div>
  <div class="days-grid" id="days-grid"></div>
</section>

<section class="block" id="explorer">
  <div class="section-kicker">08 · Evidence Lane</div>
  <h2>Commit Explorer</h2>
  <div class="prose">
    <p class="lead"><span id="commit-count-lead"></span> commits. Search by subject, sha, or path. Sort by clicking a header.</p>
  </div>
  <div class="explorer">
    <div class="explorer-controls">
      <input id="commit-search" type="search" placeholder="Search commits — subject, sha, path prefix, PR number…"/>
      <select id="commit-month-filter"><option value="">All months</option></select>
      <select id="commit-kind-filter">
        <option value="">All types</option>
        <option value="merge">Merges only</option>
        <option value="commit">Non-merges only</option>
      </select>
    </div>
    <table class="commit-table">
      <thead><tr>
        <th data-sort="date">Date</th>
        <th data-sort="sha">SHA</th>
        <th data-sort="subject">Subject</th>
        <th data-sort="top">Area</th>
        <th data-sort="files">Δ</th>
      </tr></thead>
      <tbody id="commit-tbody"></tbody>
    </table>
    <div id="commit-pagination" style="text-align:center; margin-top:1rem; font-family: var(--mono); font-size: 0.82rem; color: var(--ink-faint);"></div>
  </div>
</section>

</main>

<footer>
  <div>Generated by the <code>repo-history-book</code> skill · <span id="manifest-stats"></span></div>
  <div style="margin-top: 0.5rem;">Narrative is interpretation; evidence is the commit record itself.</div>
</footer>

<script type="application/json" id="book-data">__DATA__</script>
<script>
(function(){
  const DATA = JSON.parse(document.getElementById('book-data').textContent);
  const { narrative, days, subsystems, deep_lessons, commits, prs, manifest, ghBase } = DATA;

  function el(tag, attrs = {}, children = []) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'class') e.className = v;
      else if (k === 'html') e.innerHTML = v;
      else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
      else if (v !== undefined && v !== null) e.setAttribute(k, v);
    }
    (Array.isArray(children) ? children : [children]).forEach(c => {
      if (c == null) return;
      e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    });
    return e;
  }

  // Hero + overview
  document.getElementById('thesis').textContent = narrative.thesis || '';
  document.getElementById('overview-thesis').textContent = narrative.thesis || '';
  document.getElementById('reading-guide').textContent = narrative.reading_guide || '';
  document.getElementById('commit-count-lead').textContent = commits.length.toLocaleString();
  document.getElementById('day-count').textContent = Object.keys(days).length.toLocaleString();

  const stats = document.getElementById('stats');
  const firstDate = commits[0]?.date || '';
  const lastDate = commits[commits.length-1]?.date || '';
  [
    ['commits', manifest.commit_count?.toLocaleString() || commits.length.toLocaleString()],
    ['active days', Object.keys(days).length.toLocaleString()],
    ['merged PRs', (manifest.merged_pr_count ?? prs.length ?? 0).toLocaleString()],
    ['phases', (narrative.phases || []).length],
    ['subsystems', (subsystems || []).length],
    ['span', `${firstDate} → ${lastDate}`],
  ].forEach(([l, n]) => {
    stats.appendChild(el('div', {}, [
      el('span', {class: 'n'}, String(n)),
      el('span', {class: 'l'}, l),
    ]));
  });

  document.getElementById('manifest-stats').textContent =
    `${manifest.commit_count || commits.length} commits · ${Object.keys(days).length} days · ${manifest.merged_pr_count || prs.length || 0} PRs · rendered from durable notes in .context/history-book/`;

  // Timeline
  const phases = narrative.phases || [];
  document.getElementById('timeline-title').textContent =
    phases.length ? `${phases.length} phase${phases.length === 1 ? '' : 's'}` : 'Phases';
  document.getElementById('timeline-lead').textContent = phases.length
    ? 'Natural inflection points in the commit record, each with its dominant pressure.'
    : 'No phases defined yet.';
  const phasesEl = document.getElementById('phases');
  phases.forEach(p => {
    phasesEl.appendChild(el('div', {class: 'phase'}, [
      el('div', {class: 'dates'}, `${p.date_range || ''}${p.commits_approx ? ' · ~' + p.commits_approx + ' commits' : ''}`),
      el('h3', {}, p.title || ''),
      el('div', {class: 'summary'}, p.summary || ''),
      el('div', {class: 'tags'}, (p.themes || []).map(t => el('span', {class: 'tag'}, t))),
      p.key_prs && p.key_prs.length ? el('div', {class: 'prs'}, 'Key PRs: ' + p.key_prs.join(', ')) : null,
    ]));
  });

  // Pivots
  const pivotEl = document.getElementById('pivot-grid');
  (narrative.pivots || []).forEach(p => {
    pivotEl.appendChild(el('div', {class: 'pivot'}, [
      el('div', {class: 'when'}, p.when || ''),
      el('h3', {}, p.title || ''),
      el('div', {class: 'before'}, p.before || ''),
      el('div', {class: 'after'}, p.after || ''),
      p.evidence && p.evidence.length ? el('div', {class: 'ev'}, 'Evidence: ' + p.evidence.join(' · ')) : null,
    ]));
  });

  // Pressure loops
  const pressuresEl = document.getElementById('pressures');
  (narrative.pressure_loops || []).forEach(p => {
    pressuresEl.appendChild(el('div', {class: 'card'}, [
      p.commit_count_estimate ? el('div', {class: 'meta'}, `~${p.commit_count_estimate} commits`) : null,
      el('h3', {}, p.title || ''),
      el('p', {class: 'body'}, p.pattern || ''),
      p.interpretation
        ? el('p', {class: 'body', style: 'margin-top:0.8rem; padding-top:0.8rem; border-top:1px dashed var(--line);'}, p.interpretation)
        : null,
    ]));
  });

  // Lessons at a glance
  const lessonsEl = document.getElementById('lessons-list');
  (narrative.lessons || []).forEach((l, i) => {
    lessonsEl.appendChild(el('div', {class: 'card'}, [
      el('div', {class: 'meta'}, `Lesson ${String(i + 1).padStart(2, '0')}`),
      el('h3', {}, l.title || ''),
      el('p', {class: 'body'}, l.summary || ''),
    ]));
  });

  // Deep lessons
  if (deep_lessons && Array.isArray(deep_lessons.chapters) && deep_lessons.chapters.length) {
    document.getElementById('deep-intro').textContent = deep_lessons.intro || '';
    const deepTocEl = document.getElementById('deep-toc');
    const deepChaptersEl = document.getElementById('deep-chapters');
    deep_lessons.chapters.forEach((c, i) => {
      deepTocEl.appendChild(el('a', {href: '#' + (c.id || ''), 'data-deep-id': c.id || ''},
        `${String(i + 1).padStart(2, '0')} · ${c.title || ''}`));
      const chap = el('article', {class: 'deep-chapter size-' + (c.size || 'm'), id: c.id || ''}, [
        el('div', {class: 'dc-kicker'}, `Lesson ${String(i + 1).padStart(2, '0')}`),
        el('h3', {}, c.title || ''),
        c.one_liner ? el('div', {class: 'one-liner'}, c.one_liner) : null,
        el('h4', {}, 'The problem'),
        el('p', {}, c.problem || ''),
        c.what_broke && c.what_broke.length ? el('h4', {}, 'What kept breaking') : null,
        c.what_broke && c.what_broke.length ? el('ul', {class: 'what-broke'}, c.what_broke.map(b => el('li', {}, b))) : null,
        c.what_they_learned ? el('h4', {}, 'What they settled on') : null,
        c.what_they_learned ? el('div', {class: 'settled'}, el('p', {}, c.what_they_learned)) : null,
        c.transferable ? el('h4', {}, 'Why it matters beyond this codebase') : null,
        c.transferable ? el('div', {class: 'transferable'}, c.transferable) : null,
        c.evidence && c.evidence.length ? el('div', {class: 'evidence'}, [
          el('strong', {}, 'Evidence: '),
          document.createTextNode(c.evidence.join(' · ')),
        ]) : null,
      ]);
      deepChaptersEl.appendChild(chap);
    });
    function updateDeepNav() {
      const links = document.querySelectorAll('.deep-toc a');
      if (!links.length) return;
      const scroll = window.scrollY + 150;
      let active = null;
      deep_lessons.chapters.forEach(c => {
        const e = document.getElementById(c.id);
        if (e && e.offsetTop <= scroll) active = c.id;
      });
      links.forEach(a => a.classList.toggle('active', a.getAttribute('data-deep-id') === active));
    }
    window.addEventListener('scroll', updateDeepNav, { passive: true });
    updateDeepNav();
  } else {
    document.getElementById('deep-lessons').style.display = 'none';
    document.querySelectorAll('nav.toc a[href="#deep-lessons"]').forEach(a => a.style.display = 'none');
  }

  // Subsystems
  const subsEl = document.getElementById('subsystems-list');
  (subsystems || []).forEach(s => {
    subsEl.appendChild(el('div', {class: 'card'}, [
      s.hot_file ? el('div', {class: 'meta'}, s.hot_file) : null,
      el('h3', {}, s.name || ''),
      el('p', {class: 'body'}, s.arc || ''),
      el('div', {class: 'tags'}, (s.signals || []).map(t => el('span', {class: 'tag'}, t))),
      s.key_commits && s.key_commits.length
        ? el('div', {class: 'prs', style: 'margin-top: 0.6rem; font-family: var(--mono); font-size: 0.78rem; color: var(--ink-faint);'},
            'Key: ' + s.key_commits.join(' · '))
        : null,
    ]));
  });
  if (!subsystems || !subsystems.length) {
    document.getElementById('subsystems').style.display = 'none';
    document.querySelectorAll('nav.toc a[href="#subsystems"]').forEach(a => a.style.display = 'none');
  }

  // Days
  const daysGrid = document.getElementById('days-grid');
  const daySearch = document.getElementById('day-search');
  const dayKindFilter = document.getElementById('day-kind-filter');
  const allKinds = [...new Set(Object.values(days).map(d => d.kind).filter(Boolean))].sort();
  allKinds.forEach(k => dayKindFilter.appendChild(el('option', {value: k}, k)));

  function renderDays() {
    daysGrid.innerHTML = '';
    const q = daySearch.value.trim().toLowerCase();
    const kf = dayKindFilter.value;
    const filtered = Object.entries(days).sort().filter(([date, d]) => {
      if (kf && d.kind !== kf) return false;
      if (!q) return true;
      return date.includes(q) || (d.title || '').toLowerCase().includes(q) || (d.themes || []).some(t => t.toLowerCase().includes(q));
    });
    filtered.forEach(([date, d]) => {
      daysGrid.appendChild(el('div', {class: 'day'}, [
        el('div', {}, [
          el('div', {class: 'date'}, date),
          d.kind ? el('div', {style: 'margin-top:0.3rem;'}, el('span', {class: `kind-pill kind-${d.kind}`}, d.kind)) : null,
        ]),
        el('div', {}, [
          el('div', {class: 'title'}, d.title || ''),
          el('div', {class: 'summary'}, d.summary || ''),
          el('div', {class: 'tags', style: 'margin-top:0.4rem;'},
            (d.themes || []).slice(0, 3).map(t => el('span', {class: 'tag'}, t))),
        ]),
        el('div', {class: 'meta'}, [
          el('div', {}, `${d.commit_count || 0} commits`),
          el('a', {href: `#explorer`, onclick: () => {
            document.getElementById('commit-search').value = date;
            state.filters.query = date;
            state.page = 0;
            renderCommits();
          }, style: 'color: var(--accent); font-size: 0.75rem; margin-top: 0.3rem; display: inline-block;'}, 'view \u2192'),
        ]),
      ]));
    });
    if (filtered.length === 0) {
      daysGrid.appendChild(el('div', {style: 'color: var(--ink-faint); padding: 1rem; text-align: center;'}, 'No days match.'));
    }
  }
  daySearch.addEventListener('input', renderDays);
  dayKindFilter.addEventListener('change', renderDays);
  renderDays();

  // Commit explorer
  const tbody = document.getElementById('commit-tbody');
  const searchEl = document.getElementById('commit-search');
  const monthEl = document.getElementById('commit-month-filter');
  const kindEl = document.getElementById('commit-kind-filter');
  const pagEl = document.getElementById('commit-pagination');
  const months = [...new Set(commits.map(c => c.date.slice(0, 7)))].sort();
  months.forEach(m => monthEl.appendChild(el('option', {value: m}, m)));

  const state = { sortBy: 'date', sortDir: 1, page: 0, pageSize: 50, filters: { query: '', month: '', kind: '' } };

  function filteredCommits() {
    let out = commits;
    if (state.filters.month) out = out.filter(c => c.date.startsWith(state.filters.month));
    if (state.filters.kind) out = out.filter(c => c.kind === state.filters.kind);
    if (state.filters.query) {
      const q = state.filters.query.toLowerCase();
      out = out.filter(c =>
        c.sha.includes(q) ||
        c.subject.toLowerCase().includes(q) ||
        c.date.includes(q) ||
        (c.top || []).some(t => t.toLowerCase().includes(q))
      );
    }
    out = [...out].sort((a, b) => {
      const av = a[state.sortBy] ?? '';
      const bv = b[state.sortBy] ?? '';
      if (av < bv) return -state.sortDir;
      if (av > bv) return state.sortDir;
      return 0;
    });
    return out;
  }

  function renderCommits() {
    const filtered = filteredCommits();
    const start = state.page * state.pageSize;
    const slice = filtered.slice(start, start + state.pageSize);
    tbody.innerHTML = '';
    slice.forEach(c => {
      const shaLink = ghBase ? `${ghBase}/commit/${c.full}` : null;
      tbody.appendChild(el('tr', {}, [
        el('td', {class: 'date'}, c.date),
        el('td', {}, shaLink
          ? el('a', {class: 'sha', href: shaLink, target: '_blank', rel: 'noopener'}, c.sha)
          : el('span', {class: 'sha'}, c.sha)),
        el('td', {class: 'subj'}, c.subject),
        el('td', {class: 'tops'}, (c.top || []).slice(0, 3).join(' · ')),
        el('td', {class: 'tops'}, `${c.files}f · +${c.ins}/-${c.del}`),
      ]));
    });
    const pages = Math.max(1, Math.ceil(filtered.length / state.pageSize));
    pagEl.innerHTML = '';
    pagEl.appendChild(el('span', {}, `${filtered.length.toLocaleString()} match${filtered.length === 1 ? '' : 'es'} · page ${state.page + 1} / ${pages}  `));
    if (state.page > 0) pagEl.appendChild(el('a', {href: '#explorer', onclick: () => { state.page--; renderCommits(); }}, '\u2190 prev'));
    pagEl.appendChild(document.createTextNode(' '));
    if (state.page < pages - 1) pagEl.appendChild(el('a', {href: '#explorer', onclick: () => { state.page++; renderCommits(); }}, 'next \u2192'));
  }

  searchEl.addEventListener('input', () => { state.filters.query = searchEl.value.trim(); state.page = 0; renderCommits(); });
  monthEl.addEventListener('change', () => { state.filters.month = monthEl.value; state.page = 0; renderCommits(); });
  kindEl.addEventListener('change', () => { state.filters.kind = kindEl.value; state.page = 0; renderCommits(); });

  document.querySelectorAll('.commit-table thead th').forEach(th => {
    th.style.cursor = 'pointer';
    th.addEventListener('click', () => {
      const k = th.dataset.sort;
      if (state.sortBy === k) state.sortDir *= -1;
      else { state.sortBy = k; state.sortDir = 1; }
      state.page = 0;
      renderCommits();
    });
  });
  renderCommits();

  // Top nav active-section highlighting
  const navLinks = Array.from(document.querySelectorAll('nav.toc a'));
  const sectionIds = navLinks.map(a => a.getAttribute('href').slice(1));
  function updateNav() {
    const scroll = window.scrollY + 100;
    let active = sectionIds[0];
    for (const id of sectionIds) {
      const e = document.getElementById(id);
      if (e && e.offsetTop <= scroll) active = id;
    }
    navLinks.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + active));
  }
  window.addEventListener('scroll', updateNav, { passive: true });
  updateNav();
})();
</script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Assemble a self-contained HTML repo history book.")
    parser.add_argument("--in", dest="inp", default=".context/history-book",
                        help="history-book directory containing exports/ and book/ subdirs")
    parser.add_argument("--out", default=None,
                        help="output HTML path (default: <in>/book/index.html)")
    parser.add_argument("--title", default=None,
                        help="project title for the book (default: derived from narrative or manifest)")
    args = parser.parse_args()

    base = Path(args.inp).resolve()
    if not base.is_dir():
        sys.exit(f"error: input dir does not exist: {base}")

    narrative = load(base, "book/narrative.json", required=True)
    days = load(base, "book/days.json", required=True)
    subsystems = load(base, "book/subsystems.json", required=False) or []
    deep_lessons = load(base, "book/deep_lessons.json", required=False)
    all_commits = load(base, "exports/all-commits.json", required=True)
    merged_prs = load(base, "exports/merged-prs.json", required=False) or []
    manifest = load(base, "exports/manifest.json", required=True)

    title = derive_title(manifest, narrative, args.title)
    gh_base = derive_gh_base(merged_prs)
    slim_commits, slim_prs = slim(all_commits, merged_prs)

    data_blob = {
        "narrative": narrative,
        "days": days,
        "subsystems": subsystems,
        "deep_lessons": deep_lessons,
        "commits": slim_commits,
        "prs": slim_prs,
        "manifest": manifest,
        "ghBase": gh_base,
    }

    payload = json.dumps(data_blob, ensure_ascii=False).replace("</", "<\\/")
    html = HTML_TEMPLATE.replace("__TITLE__", title).replace("__DATA__", payload)

    out_path = Path(args.out) if args.out else base / "book" / "index.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html)

    print(f"wrote {out_path}")
    print(f"  title: {title}")
    print(f"  size: {len(html):,} chars")
    print(f"  embedded: {len(slim_commits)} commits, {len(slim_prs)} PRs, "
          f"{len(days)} days, {len(subsystems)} subsystems, "
          f"{len(deep_lessons.get('chapters', [])) if deep_lessons else 0} deep lessons")


if __name__ == "__main__":
    main()
