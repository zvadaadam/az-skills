#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TARGETS=("$HOME/.claude/skills" "$HOME/.agents/skills")

# ── Colors & animation (disabled when piped) ────────
if [ -t 1 ]; then
  bold=$'\033[1m'  dim=$'\033[2m'  reset=$'\033[0m'
  green=$'\033[32m'  yellow=$'\033[33m'  red=$'\033[31m'
  # 256-color grays for gradient logo (light → dark)
  g1=$'\033[38;5;250m'  g2=$'\033[38;5;248m'  g3=$'\033[38;5;245m'
  g4=$'\033[38;5;243m'  g5=$'\033[38;5;240m'  g6=$'\033[38;5;238m'
  # Dimmer gradient for AZ (secondary)
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
  local name="$1" ms="${2:-400}"
  $animate || return 0
  local steps=$((ms / 80))
  for ((i=0; i<steps; i++)); do
    printf "\r    %s %s" "${dim}${FRAMES[i % 10]}${reset}" "$name"
    sleep 0.08
  done
  printf "\r%s" "$clear_line"
}

configure_claude_skill_read_hook() {
  python3 - <<'PY'
import json
import os
from pathlib import Path

settings_path = Path.home() / ".claude" / "settings.json"
settings_path.parent.mkdir(parents=True, exist_ok=True)

command = 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill auto --event skill_read --agent-harness claude-code --quiet'
legacy_commands = {
    'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill auto --action skill_read --agent-harness claude-code --quiet',
}
handler = {
    "type": "command",
    "command": command,
    "timeout": 5,
}

try:
    if settings_path.exists():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    else:
        settings = {}
except json.JSONDecodeError:
    print("skip")
    raise SystemExit(0)

if not isinstance(settings, dict):
    print("skip")
    raise SystemExit(0)

hooks = settings.setdefault("hooks", {})
if not isinstance(hooks, dict):
    print("skip")
    raise SystemExit(0)

post_tool_use = hooks.setdefault("PostToolUse", [])
if not isinstance(post_tool_use, list):
    print("skip")
    raise SystemExit(0)

for group in post_tool_use:
    if not isinstance(group, dict):
        continue
    handlers = group.get("hooks")
    if not isinstance(handlers, list):
        continue
    group["hooks"] = [
        existing
        for existing in handlers
        if not (isinstance(existing, dict) and existing.get("command") in legacy_commands)
    ]

for group in post_tool_use:
    if not isinstance(group, dict):
        continue
    for existing in group.get("hooks", []):
        if isinstance(existing, dict) and existing.get("command") == command:
            print("unchanged")
            raise SystemExit(0)

read_group = None
for group in post_tool_use:
    if isinstance(group, dict) and group.get("matcher") == "Read":
        read_group = group
        break

if read_group is None:
    read_group = {"matcher": "Read", "hooks": []}
    post_tool_use.append(read_group)

read_group_hooks = read_group.setdefault("hooks", [])
if not isinstance(read_group_hooks, list):
    print("skip")
    raise SystemExit(0)

read_group_hooks.append(handler)
settings_path.write_text(json.dumps(settings, indent=2, sort_keys=True) + "\n", encoding="utf-8")
os.chmod(settings_path, 0o600)
print("installed")
PY
}

cleanup() { printf "%s" "$show_cursor"; }
trap cleanup EXIT
printf "%s" "$hide_cursor"

for dir in "${TARGETS[@]}"; do mkdir -p "$dir"; done
git -C "$REPO" config core.hooksPath .githooks 2>/dev/null || true

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
echo "  ${dim}→${reset} ~${TARGETS[0]#"$HOME"}/"
echo "  ${dim}→${reset} ~${TARGETS[1]#"$HOME"}/"

pause 0.3

echo ""

# ── Counters ────────────────────────────────────────
n_linked=0
n_unchanged=0
n_replaced=0
n_backed=0

# ── Install ─────────────────────────────────────────
prev_cat=""

for skill_md in $(find "$REPO"/skills -mindepth 3 -maxdepth 3 -name SKILL.md 2>/dev/null | sort); do
  [ -f "$skill_md" ] || continue
  skill_dir="$(dirname "$skill_md")"
  name="$(basename "$skill_dir")"
  category="$(basename "$(dirname "$skill_dir")")"

  # Category header
  if [ "$category" != "$prev_cat" ]; then
    [ -n "$prev_cat" ] && echo ""
    pause 0.15
    echo "  ${bold}${category}${reset}"
    prev_cat="$category"
  fi

  # Check if every target is already correct
  all_ok=true
  for target_dir in "${TARGETS[@]}"; do
    target="$target_dir/$name"
    if ! [ -L "$target" ] || [ "$(readlink "$target")" != "$skill_dir" ]; then
      all_ok=false
      break
    fi
  done

  if $all_ok; then
    pause 0.08
    echo "    ${dim}◇ ${name}${reset}"
    n_unchanged=$((n_unchanged + 1))
    continue
  fi

  # Spinner while linking
  spin "$name" 400

  # Fix each target
  did_backup=false
  did_replace=false

  for target_dir in "${TARGETS[@]}"; do
    target="$target_dir/$name"

    # Already correct
    if [ -L "$target" ] && [ "$(readlink "$target")" = "$skill_dir" ]; then
      continue
    fi

    # Regular directory → back up
    if [ -d "$target" ] && [ ! -L "$target" ]; then
      mv "$target" "$target.backup.$(date +%Y%m%d%H%M%S)"
      did_backup=true
    fi

    # Stale symlink → remove
    if [ -L "$target" ]; then
      rm "$target"
      did_replace=true
    fi

    ln -s "$skill_dir" "$target"
  done

  # Report
  if $did_backup; then
    echo "    ${yellow}◆${reset} ${name}  ${dim}backed up → linked${reset}"
    n_backed=$((n_backed + 1))
  elif $did_replace; then
    echo "    ${green}◆${reset} ${name}  ${dim}replaced${reset}"
    n_replaced=$((n_replaced + 1))
  else
    echo "    ${green}◆${reset} ${name}  ${dim}linked${reset}"
    n_linked=$((n_linked + 1))
  fi
done

claude_read_hook_status="$(configure_claude_skill_read_hook)"

# ── Summary ─────────────────────────────────────────
total=$((n_linked + n_replaced + n_backed + n_unchanged))

pause 0.3

echo ""
echo "  ${dim}───────────────────────────────────────────────${reset}"

parts=()
changed=$((n_linked + n_replaced + n_backed))
if [ "$changed" -gt 0 ]; then
  parts+=("${green}${changed} linked${reset}")
fi
if [ "$n_unchanged" -gt 0 ]; then
  parts+=("${dim}${n_unchanged} unchanged${reset}")
fi
if [ "$n_backed" -gt 0 ]; then
  parts+=("${yellow}${n_backed} backed up${reset}")
fi

summary=""
for i in "${!parts[@]}"; do
  [ "$i" -gt 0 ] && summary+=" ${dim}·${reset} "
  summary+="${parts[$i]}"
done

echo "  ${bold}${total} skills${reset}  ${summary}"
case "$claude_read_hook_status" in
  installed) echo "  ${green}◆${reset} claude skill-read hook  ${dim}installed${reset}" ;;
  unchanged) echo "  ${dim}◇ claude skill-read hook${reset}" ;;
  *) echo "  ${yellow}◆${reset} claude skill-read hook  ${dim}skipped: invalid ~/.claude/settings.json${reset}" ;;
esac
echo ""
