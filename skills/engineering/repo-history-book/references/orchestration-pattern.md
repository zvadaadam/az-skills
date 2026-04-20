# Orchestration Pattern

Use this pattern when the repo is too large for one pass, when the work spans multiple sessions, or when multiple agents are contributing.

## Roles

### 1. Extractor
- Reads export files and chunk manifests
- Works one stable chunk at a time
- Writes compact commit notes
- Updates `manifest.json` with chunk completion status

### 2. Merger
- Reads finished commit notes
- Updates day notes, then phase notes, then pivot notes
- Carries forward open questions instead of inventing certainty

### 3. Author
- Reads the merged notes, not raw git history unless needed
- Writes the narrative lane: overview, phases, pivots, subsystem arcs, lessons, pressure loops
- Builds the HTML/Markdown artifact

### 4. Reviewer
- Checks that the site feels like a book instead of a dashboard
- Verifies that every major claim has a backlink into evidence
- Fixes chaptering, reading order, and UX gaps

## Source-of-truth rule

Never summarize from memory if a durable note exists.

Preferred dependency chain:

```text
raw git / PR exports
  -> commit notes
  -> day notes
  -> phase notes / pivot notes
  -> book chapters
  -> HTML site
```

Each layer should be derived from the layer beneath it.

## Merge contract

Every durable note should be safe to merge later. That means:

- short, structured fields
- stable identifiers (`chunk-0007`, `2026-04-06`, `phase-4`)
- cautious interpretation, clearly separated from facts
- explicit links upward and downward when possible

## Multi-agent sharding

If multiple agents are helping:

- shard by stable chunk ID, not by arbitrary date ranges invented on the fly
- let each agent write only the note files for its assigned chunks
- merge through day notes and phase notes after chunk work completes
- reserve the narrative book/site pass for a final synthesizer

## Practical resume protocol

When resuming after context loss:

1. Read `manifest.json`
2. Read `chunks/chunks.json`
3. Read the latest completed chunk note
4. Read the relevant day note
5. Continue only the unfinished chunk or chapter

This keeps the model from reloading the whole project history just to continue one step.

## Failure modes to avoid

- Writing polished prose before commit/day notes exist
- Mixing facts and interpretation in the same field
- Re-chunking mid-project
- Letting the HTML become a pretty dashboard with no narrative spine
- Depending on remembered context instead of durable files
