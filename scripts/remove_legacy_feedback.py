#!/usr/bin/env python3
"""Remove retired feedback hooks, skill links, and local installation identity."""

import json
import sys
from pathlib import Path


READ_HOOK_COMMANDS = {
    'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill auto --event skill_read --agent-harness claude-code --quiet',
    'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill auto --action skill_read --agent-harness claude-code --quiet',
}


def remove_read_hook(settings_path: Path) -> None:
    if not settings_path.exists():
        return
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        print(f"Cannot read {settings_path}; remove the old skill-read hook manually.", file=sys.stderr)
        return

    hooks = settings.get("hooks") if isinstance(settings, dict) else None
    groups = hooks.get("PostToolUse") if isinstance(hooks, dict) else None
    if not isinstance(groups, list):
        return

    remaining_groups = []
    changed = False
    for group in groups:
        handlers = group.get("hooks") if isinstance(group, dict) else None
        if not isinstance(handlers, list):
            remaining_groups.append(group)
            continue
        remaining_handlers = [
            handler
            for handler in handlers
            if not (
                isinstance(handler, dict)
                and handler.get("type") == "command"
                and isinstance(handler.get("command"), str)
                and handler["command"] in READ_HOOK_COMMANDS
            )
        ]
        if len(remaining_handlers) == len(handlers):
            remaining_groups.append(group)
        else:
            changed = True
            if remaining_handlers:
                remaining_groups.append({**group, "hooks": remaining_handlers})

    if not changed:
        return
    if remaining_groups:
        hooks["PostToolUse"] = remaining_groups
    else:
        del hooks["PostToolUse"]
    if not hooks:
        del settings["hooks"]
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    print("Removed retired skill-read hook.")


def cleanup(home: Path, repo: Path) -> None:
    remove_read_hook(home / ".claude" / "settings.json")
    retired_skill = repo.resolve() / "skills" / "engineering" / "skill-feedback"
    for harness in (".claude", ".agents", ".codex"):
        link = home / harness / "skills" / "skill-feedback"
        if link.is_symlink() and link.resolve() == retired_skill:
            link.unlink()
            print(f"Removed retired {harness}/skills/skill-feedback link.")

    identity = home / ".az-skills" / "installation-id"
    if identity.is_file() or identity.is_symlink():
        identity.unlink()
        print("Removed retired installation ID.")


if __name__ == "__main__":
    cleanup(Path.home(), Path(__file__).resolve().parent.parent)
