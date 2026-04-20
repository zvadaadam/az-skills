# Chunking strategy

The model will forget. Chunking is how you win.

## Default

- group commits by day
- if a day has `<= 25` commits, keep it as one chunk
- if a day has `> 25` commits, split into balanced parts (e.g. 30 → 15+15, 40 → 20+20, 55 → 19+18+18)

`chunk_history.py` does this automatically; `--max-per-chunk` (default `25`) is the upper bound per part.

## Alternate strategies

Use only if day-based chunking is poor:

- by merged PR
- by first-parent segment between major merges
- by fixed commit count (20-30)

## Stability rules

- chunk IDs must be deterministic
- chunk boundaries must not drift as notes are added
- store the boundary list in `chunks/chunks.json`
- write one chunk note file per chunk

## Good chunk names

- `2026-04-06-a`
- `2026-04-06-b`
- `phase-3-pr-7`

## Bad chunk names

- `later-fixes`
- `misc`
- `more-stuff`
