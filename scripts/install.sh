#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_SKILLS="$HOME/.claude/skills"
AGENTS_SKILLS="$HOME/.agents/skills"

mkdir -p "$CLAUDE_SKILLS" "$AGENTS_SKILLS"

# Set up git hooks so future git pull / checkout auto-runs install
git -C "$REPO" config core.hooksPath .githooks 2>/dev/null || true

echo "Installing skills into ~/.claude/skills/ and ~/.agents/skills/"
echo ""

# Walk all category subdirs, find folders containing SKILL.md
for skill_md in "$REPO"/skills/*/*/SKILL.md; do
  [ -f "$skill_md" ] || continue
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"
  category="$(basename "$(dirname "$skill_dir")")"

  for target_dir in "$CLAUDE_SKILLS" "$AGENTS_SKILLS"; do
    target="$target_dir/$name"
    label="$(basename "$target_dir")"

    # Already linked correctly — skip
    if [ -L "$target" ] && [ "$(readlink "$target")" = "$skill_dir" ]; then
      echo "  [skip]    $label/$name (already linked)"
      continue
    fi

    # Regular directory — back it up
    if [ -d "$target" ] && [ ! -L "$target" ]; then
      backup="$target.backup.$(date +%Y%m%d%H%M%S)"
      echo "  [backup]  $label/$name -> $backup"
      mv "$target" "$backup"
    fi

    # Symlink pointing elsewhere — remove it
    if [ -L "$target" ]; then
      echo "  [replace] $label/$name (was -> $(readlink "$target"))"
      rm "$target"
    fi

    ln -s "$skill_dir" "$target"
    echo "  [link]    $label/$name -> skills/$category/$name"
  done
done

echo ""
echo "Done. Skills symlinked for Claude Code and Codex."
echo "Edit in the repo, git pull, and changes propagate instantly."
