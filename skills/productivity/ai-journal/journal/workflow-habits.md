# Adam's Workflow Habits

*Common workflows, task types, and how Adam approaches work.*

## Task Types

- **Tooling & automation**: Building skills, hooks, MCP servers, workflow improvements
- **Cross-repo infrastructure**: Prefers global solutions that work everywhere
- **Large feature slices**: Multi-layer changes spanning adapters, backend, shared types, and frontend in one branch

## Work Style

- **Iterative**: Starts with an idea, gets it built, then refines ("you know what? I got a different idea")
- **Fast pivots**: Doesn't dwell on approaches that don't work - moves to alternatives quickly
- **Delegation-oriented**: Comfortable spawning sub-agents and background tasks
- **Systems over tasks**: Prefers building a system that handles something automatically over doing it manually each time
- **Non-destructive rollouts**: Uses dual-write / coexistence patterns when migrating to new systems (new + legacy run in parallel)

## Session Patterns

- Sessions often involve building or improving developer tooling
- Mixes high-level architecture discussions with hands-on implementation
- Expects AI to be proactive and anticipate needs
- Large features are broken into numbered sequential commits (#1, #2, ... #N) — each scoped and test-verified before moving on
- Test counts included in commit messages as a quality signal

## Quality Signals Adam Uses

- Test counts in commit messages ("all 830 tests passing")
- TypeScript compilation as a gate
- Numbered commit series to track progress through a feature

---
*Last updated: 2026-04-11*
