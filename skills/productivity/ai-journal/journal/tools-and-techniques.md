# Tools & Techniques

*What Adam uses and how he leverages AI tooling.*

## Claude Code Features Used

- **Custom skills**: Builds and maintains many custom skills (peon-ping, hivenet, design engineering, etc.)
- **MCP servers**: Uses Obsidian MCP, Pencil design tool, Exa search
- **Sub-agents / Task tool**: Understands and uses background agents for parallel work
- **Hooks**: Has SessionStart, UserPromptSubmit, Stop, Notification, and PermissionRequest hooks configured
- **Skills as infrastructure**: Treats skills as reusable, cross-repo tools rather than project-specific helpers

## Environment

- macOS (Darwin)
- Shell: zsh
- Editor: Claude Code CLI
- Note-taking: Obsidian (az-obsidian vault)
- Design: Pencil (.pen files)

## Patterns

- Prefers storing config/data in `~/.claude/` for cross-repo access
- Uses symlinks to share skills between locations (`~/.agents/skills/` -> `~/.claude/skills/`)
- Quick to abandon tools that don't work reliably (e.g., Obsidian MCP when it hangs)

---
*Last updated: 2026-03-01*
