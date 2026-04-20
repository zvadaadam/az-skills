# Sample commit note

A realistic filled example, following `commit-note-schema.md`. Use as a quality reference when writing your own.

```yaml
sha: 3f9f7092
full_sha: 3f9f7092b060e6bb59108c036bb8606064ce38c0
date: 2026-04-14
author: Adam Zvada
subject: "Redesign install/uninstall with polished CLI experience (#2)"
kind: refactor
areas:
  - scripts
  - skills
what_changed: >
  Rewrote install.sh and uninstall.sh to use symlinks into ~/.claude/skills
  and ~/.agents/skills with colored status output and idempotent checks.
  Added .githooks/post-merge to re-run install automatically after pull.
why_it_matters: >
  Shifts the distribution model from "copy these files" to "manage a
  live link." The post-merge hook makes updates invisible to the user.
signals:
  - packaging
  - productization
related_to:
  - "#1"
inference: >
  The packaging rewrite so soon after the initial commit suggests the
  author bumped into rough edges using v1 in anger and decided the install
  story was part of the product, not a side concern.
confidence: medium
```

## What this illustrates

- **Facts live in `what_changed` and `areas`.** Claims are verifiable against the diff.
- **`inference` is clearly hedged.** "Suggests", "likely", "appears" — the reader knows this is interpretation.
- **`signals` are vocabulary, not free text.** They drive the pressure-loop and pivot sections of the book later.
- **Length is short.** The note exists to be merged into a day note, not to be read standalone.

## Anti-examples

Do **not** write:

- `what_changed: "Big refactor of the install system, lots of changes to make the install scripts more polished and user-friendly with better error handling and nicer output messages."` — waffle, no specifics.
- `inference: "The team realized they needed proper packaging."` — stated as fact without the "suggests" framing.
- A commit note that is longer than the commit itself.
