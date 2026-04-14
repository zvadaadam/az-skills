#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TARGETS=("$HOME/.claude/skills" "$HOME/.agents/skills")

# ── Colors & animation (disabled when piped) ────────
if [ -t 1 ]; then
  bold=$'\033[1m'  dim=$'\033[2m'  reset=$'\033[0m'
  green=$'\033[32m'  yellow=$'\033[33m'  red=$'\033[31m'
  g1=$'\033[38;5;250m'  g2=$'\033[38;5;248m'  g3=$'\033[38;5;245m'
  g4=$'\033[38;5;243m'  g5=$'\033[38;5;240m'  g6=$'\033[38;5;238m'
  a1=$'\033[38;5;245m'  a2=$'\033[38;5;243m'  a3=$'\033[38;5;241m'
  a4=$'\033[38;5;239m'  a5=$'\033[38;5;237m'  a6=$'\033[38;5;236m'
  hide_cursor=$'\033[?25l'  show_cursor=$'\033[?25h'
  clear_line=$'\033[2K'
  animate=true
else
  bold='' dim='' reset='' green='' yellow='' red=''
  g1='' g2='' g3='' g4='' g5='' g6=''
  a1='' a2='' a3='' a4='' a5='' a6=''
  hide_cursor='' show_cursor='' clear_line=''
  animate=false
fi

FRAMES=(⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏)

pause() { $animate && sleep "$1" || true; }

spin() {
  local name="$1" ms="${2:-300}"
  $animate || return 0
  local steps=$((ms / 80))
  for ((i=0; i<steps; i++)); do
    printf "\r    %s %s" "${dim}${FRAMES[i % 10]}${reset}" "$name"
    sleep 0.08
  done
  printf "\r%s" "$clear_line"
}

cleanup() { printf "%s" "$show_cursor"; }
trap cleanup EXIT
printf "%s" "$hide_cursor"

# ── Logo ────────────────────────────────────────────
echo ""
echo "  ${a1} █████╗ ███████╗${reset}    ${g1}███████╗██╗  ██╗██╗██╗     ██╗     ███████╗${reset}"
echo "  ${a2}██╔══██╗╚══███╔╝${reset}    ${g2}██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝${reset}"
echo "  ${a3}███████║  ███╔╝ ${reset}    ${g3}███████╗█████╔╝ ██║██║     ██║     ███████╗${reset}"
echo "  ${a4}██╔══██║ ███╔╝  ${reset}    ${g4}╚════██║██╔═██╗ ██║██║     ██║     ╚════██║${reset}"
echo "  ${a5}██║  ██║███████╗${reset}    ${g5}███████║██║  ██╗██║███████╗███████╗███████║${reset}"
echo "  ${a6}╚═╝  ╚═╝╚══════╝${reset}    ${g6}╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝${reset}"

pause 0.5

echo ""
echo "  ${dim}uninstalling...${reset}"

pause 0.3

echo ""

# ── Counters ────────────────────────────────────────
n_removed=0
n_restored=0

# ── Remove ──────────────────────────────────────────
prev_cat=""

for skill_md in $(find "$REPO"/skills -mindepth 3 -maxdepth 3 -name SKILL.md 2>/dev/null | sort); do
  [ -f "$skill_md" ] || continue
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"
  category="$(basename "$(dirname "$skill_dir")")"

  # Only act if at least one target has our symlink
  has_link=false
  for target_dir in "${TARGETS[@]}"; do
    target="$target_dir/$name"
    if [ -L "$target" ] && [ "$(readlink "$target")" = "$skill_dir" ]; then
      has_link=true
      break
    fi
  done
  $has_link || continue

  # Category header
  if [ "$category" != "$prev_cat" ]; then
    [ -n "$prev_cat" ] && echo ""
    pause 0.15
    echo "  ${bold}${category}${reset}"
    prev_cat="$category"
  fi

  # Spinner while removing
  spin "$name" 300

  # Remove from each target
  restored=false
  for target_dir in "${TARGETS[@]}"; do
    target="$target_dir/$name"
    if [ -L "$target" ] && [ "$(readlink "$target")" = "$skill_dir" ]; then
      rm "$target"

      # Restore backup if one exists
      backup=$(ls -1d "$target".backup.* 2>/dev/null | tail -1 || true)
      if [ -n "$backup" ]; then
        mv "$backup" "$target"
        restored=true
      fi
    fi
  done

  if $restored; then
    echo "    ${yellow}◆${reset} ${name}  ${dim}restored from backup${reset}"
    n_restored=$((n_restored + 1))
  else
    echo "    ${red}◆${reset} ${name}  ${dim}removed${reset}"
  fi
  n_removed=$((n_removed + 1))
done

# ── Summary ─────────────────────────────────────────
pause 0.3

echo ""
echo "  ${dim}───────────────────────────────────────────────${reset}"

if [ "$n_removed" -eq 0 ]; then
  echo "  ${dim}nothing to remove${reset}"
else
  parts="${red}${n_removed} removed${reset}"
  if [ "$n_restored" -gt 0 ]; then
    parts+=" ${dim}·${reset} ${yellow}${n_restored} restored${reset}"
  fi
  echo "  ${bold}${n_removed} skills${reset}  ${parts}"
fi
echo ""
