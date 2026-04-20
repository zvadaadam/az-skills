#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def chunk_day(commits: list[dict], max_per_chunk: int) -> list[list[dict]]:
    n = len(commits)
    if n <= max_per_chunk:
        return [commits]
    # balanced split: avoids a tiny trailing chunk (e.g. 26 commits, max 25 → 13+13, not 25+1)
    num_parts = (n + max_per_chunk - 1) // max_per_chunk
    base, extra = divmod(n, num_parts)
    parts: list[list[dict]] = []
    i = 0
    for p in range(num_parts):
        size = base + (1 if p < extra else 0)
        parts.append(commits[i:i + size])
        i += size
    return parts


def build_chunks(by_day: dict[str, list[dict]], max_per_chunk: int) -> list[dict]:
    chunks = []
    for day in sorted(by_day):
        commits = by_day[day]
        parts = chunk_day(commits, max_per_chunk)
        if len(parts) == 1:
            chunks.append({
                'id': day,
                'date': day,
                'part': None,
                'count': len(parts[0]),
                'from': parts[0][0]['short'],
                'to': parts[0][-1]['short'],
                'commits': [c['short'] for c in parts[0]],
            })
        else:
            for idx, part in enumerate(parts, start=1):
                part_id = chr(ord('a') + idx - 1)
                chunks.append({
                    'id': f'{day}-{part_id}',
                    'date': day,
                    'part': part_id,
                    'count': len(part),
                    'from': part[0]['short'],
                    'to': part[-1]['short'],
                    'commits': [c['short'] for c in part],
                })
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description='Create stable history chunks from commits-by-day.json')
    parser.add_argument('input', nargs='?', default='.context/history-book/exports/commits-by-day.json')
    parser.add_argument('--out', default='.context/history-book/chunks/chunks.json')
    parser.add_argument('--max-per-chunk', type=int, default=25)
    args = parser.parse_args()

    by_day = json.loads(Path(args.input).read_text())
    chunks = build_chunks(by_day, args.max_per_chunk)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(chunks, indent=2))
    print(f'wrote {len(chunks)} chunks to {out}')


if __name__ == '__main__':
    main()
