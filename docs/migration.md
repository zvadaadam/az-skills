# Migrate an older installation

## Renamed skills

Most skills gained the `az-` prefix in November 2026. For example, `deslop` is now `az-deslop`. A few changed more substantially.

| Old name | Where to find it |
|---|---|
| `az-master-coordinator` | `az-multi-workspace-lead`. Use `az-workspace-coordinator` for a single workspace. |
| `pre-factor` | The prep-refactor pass is part of `az-implementation-rehearsal`. |
| `code-simplifier` | Merged into `az-deslop`. |
| `plan-for-goal`, `plan-for-mega-goal`, `repo-history-book` | Retired. |

Install the skills you want under their new names. Run `npx skills list` in the project or `npx skills list --global` for a global install. Other collections use some of the old names. Remove an old skill only when its listed source is `zvadaadam/az-skills`. For example, run `npx skills remove deslop` for a project copy from this repo. Add `--global` for a global copy.

## Shell installer

1. In the original clone, if `git config --local --get core.hooksPath` prints `.githooks`, run `git config --local --unset-all core.hooksPath '^\.githooks$'`. This prevents a later checkout or pull from reinstalling the links.
2. Run `./scripts/uninstall.sh` there if it still exists. In `~/.claude/skills`, `~/.agents/skills`, and `~/.codex/skills`, unlink any remaining symlinks that point into that clone. For each link you remove manually, restore the newest matching `<name>.backup.<timestamp>` directory to `<name>` if present.
3. If you used the retired `skill-feedback` package, remove its `skill-feedback/scripts/skill-event.py` handler from `PostToolUse` in `~/.claude/settings.json` and delete `~/.az-skills/installation-id` if present. For a CLI-installed copy, check its source before removing it in its original scope.

Install with `npx skills add zvadaadam/az-skills --global` to match the shell installer's scope.
