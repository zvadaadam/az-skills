#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> str:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True).stdout


def try_run(cmd: list[str], cwd: Path) -> str | None:
    try:
        return run(cmd, cwd)
    except Exception:
        return None


def export_history(repo: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    revs = run(['git', 'rev-list', '--reverse', 'HEAD'], repo).splitlines()
    commits = []
    by_day = defaultdict(list)
    file_counter: Counter[str] = Counter()

    for sha in revs:
        meta = run(['git', 'show', '-s', '--date=short', '--format=%H%x1f%P%x1f%ad%x1f%an%x1f%ae%x1f%s%x1f%b', sha], repo).rstrip('\n')
        full_sha, parents, date, author, email, subject, body = (meta.split('\x1f', 6) + [''])[:7]
        # --diff-merges=first-parent shows merges as diff vs first parent (PR contents);
        # no-op for non-merge commits. Without it, merges show an empty combined diff.
        diff = run(['git', 'show', '--numstat', '--format=', '--diff-merges=first-parent', sha], repo)
        files = []
        top_levels = set()
        insertions = 0
        deletions = 0
        for line in diff.splitlines():
            parts = line.split('\t')
            if len(parts) != 3:
                continue
            a_raw, d_raw, path = parts
            a = 0 if a_raw == '-' else int(a_raw)
            d = 0 if d_raw == '-' else int(d_raw)
            insertions += a
            deletions += d
            files.append({'path': path, 'insertions': a, 'deletions': d})
            top = path.split('/')[0]
            top_levels.add(top)
            file_counter[path] += 1
        commit = {
            'sha': full_sha,
            'short': full_sha[:8],
            'parents': parents.split() if parents else [],
            'is_merge': len(parents.split()) > 1,
            'date': date,
            'author': author,
            'email': email,
            'subject': subject,
            'body': body.strip(),
            'files': files,
            'file_count': len(files),
            'insertions': insertions,
            'deletions': deletions,
            'top_levels': sorted(top_levels),
        }
        commits.append(commit)
        by_day[date].append(commit)

    first_parent = []
    fp = run(['git', 'log', '--first-parent', '--reverse', '--date=short', '--format=%H%x1f%ad%x1f%an%x1f%s'], repo)
    for line in fp.splitlines():
        sha, date, author, subject = line.split('\x1f')
        first_parent.append({'sha': sha, 'short': sha[:8], 'date': date, 'author': author, 'subject': subject})

    tags = []
    tag_list = try_run(['git', 'tag', '--sort=creatordate'], repo) or ''
    for tag in tag_list.splitlines():
        date = run(['git', 'log', '-1', '--format=%ad', '--date=short', tag], repo).strip()
        subject = run(['git', 'log', '-1', '--format=%s', tag], repo).strip()
        tags.append({'tag': tag, 'date': date, 'subject': subject})

    merged_prs = []
    gh_path = shutil.which('gh')
    if gh_path:
        raw = try_run(['gh', 'pr', 'list', '--state', 'merged', '--limit', '200', '--json', 'number,title,mergedAt,author,baseRefName,headRefName,url'], repo)
        if raw:
            merged_prs = json.loads(raw)

    (out / 'all-commits.json').write_text(json.dumps(commits, indent=2))
    (out / 'commits-by-day.json').write_text(json.dumps(by_day, indent=2))
    (out / 'first-parent.json').write_text(json.dumps(first_parent, indent=2))
    (out / 'tags.json').write_text(json.dumps(tags, indent=2))
    (out / 'merged-prs.json').write_text(json.dumps(merged_prs, indent=2))

    with (out / 'all-commits.tsv').open('w') as f:
        f.write('date\tsha\tauthor\tfiles\tins\tdel\ttop_levels\tsubject\n')
        for c in commits:
            tops = ','.join(c['top_levels'])
            subj = c['subject'].replace('\t', ' ').replace('\n', ' ')
            f.write(f"{c['date']}\t{c['short']}\t{c['author']}\t{c['file_count']}\t{c['insertions']}\t{c['deletions']}\t{tops}\t{subj}\n")

    with (out / 'top-files.tsv').open('w') as f:
        f.write('touches\tpath\n')
        for path, count in file_counter.most_common():
            f.write(f'{count}\t{path}\n')

    manifest = {
        'repo': str(repo),
        'commit_count': len(commits),
        'active_days': len(by_day),
        'merged_pr_count': len(merged_prs),
        'tag_count': len(tags),
        'first_commit': commits[0]['short'] if commits else None,
        'last_commit': commits[-1]['short'] if commits else None,
    }
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description='Export repo git history into durable JSON/TSV files.')
    parser.add_argument('repo', nargs='?', default='.', help='path to git repo')
    parser.add_argument('--out', default='.context/history-book/exports', help='output directory')
    args = parser.parse_args()
    export_history(Path(args.repo).resolve(), Path(args.out).resolve())


if __name__ == '__main__':
    main()
