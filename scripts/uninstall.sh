#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_SKILLS="$HOME/.claude/skills"
AGENTS_SKILLS="$HOME/.agents/skills"

echo "Removing symlinks that point into $REPO/skills/"
echo ""

for skill_md in "$REPO"/skills/*/*/SKILL.md; do
  [ -f "$skill_md" ] || continue
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"

  for target_dir in "$CLAUDE_SKILLS" "$AGENTS_SKILLS"; do
    target="$target_dir/$name"
    label="$(basename "$target_dir")"

    if [ -L "$target" ] && [ "$(readlink "$target")" = "$skill_dir" ]; then
      rm "$target"
      echo "  [removed]  $label/$name"

      # Restore backup if one exists
      backup=$(ls -1d "$target".backup.* 2>/dev/null | tail -1 || true)
      if [ -n "$backup" ]; then
        mv "$backup" "$target"
        echo "  [restored] $label/$name from backup"
      fi
    fi
  done
done

echo ""
echo "Done. Symlinks removed."
