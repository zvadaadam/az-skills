# Commit note schema

Use this schema for each commit note.

```yaml
sha: 8-char short sha
full_sha: full sha
date: YYYY-MM-DD
author: string
subject: one-line subject
kind: [feature, fix, refactor, docs, test, infra, release, rollback, brand, security, billing, ui, ops, unknown]
areas:
  - top-level folders or notable files
what_changed: 1-3 sentences
why_it_matters: 1-2 sentences
signals:
  - pain_loop
  - maturity
  - pivot
  - packaging
  - trust
  - productization
  - rollback
  - release_stabilization
related_to:
  - sha or PR number if obvious
inference: optional cautious interpretation
confidence: low | medium | high
```

Guidelines:

- `what_changed` should be factual
- `inference` should be cautious
- if the commit is tiny, note that and move on
- if the commit is part of a fix train, say so explicitly

See `sample-commit-note.md` for a filled example and common anti-patterns.
