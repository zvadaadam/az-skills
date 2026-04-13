# Session Observations

*Running log of notable observations. Most recent first. Capped at ~30 entries.*

---

## 2026-04-11 - Unified Parts Architecture (chengdu-v3)

**What Adam was doing**: Implementing a "unified Parts" message rendering architecture across Claude and Codex adapters in Deus Machine (agent-server + backend + frontend).

**Observations**:
- Greeted with "heloo" — casual session start, minimal context given upfront
- The branch name contains an issue title hint: "i-would-love-to-impr" — likely from a GitHub issue
- Work spans 6 numbered commits (#1–#6), each scoped and test-verified — suggests either Adam prompted for this structure or the AI naturally broke it down this way
- Each commit increments meaningfully: adapter → handler → backend persistence → shared schema → frontend wiring
- 830 tests passing at commit #6 — Adam tracks test counts explicitly in commit messages
- Dual-write pattern used: new Parts system runs alongside legacy events for non-destructive rollout

**Patterns noted**:
- Large features broken into numbered sequential commits with clear per-step scope
- Test counts in commit messages used as a quality signal
- Non-destructive rollout strategy: new + old systems coexist during transition

---

## 2026-03-01 - Building the AI Journal Skill

**What Adam was doing**: Creating a proactive skill to automatically document his AI workflow patterns.

**Observations**:
- Adam uses voice-to-text input heavily - prompts contain phonetic errors ("teh", "jpurnal", "obsiidna", "mcps erve rsem to owkr") but the intent is always clear
- He thinks at the systems level: instead of just writing notes about his workflow, he wants an automated system that observes and documents it for him
- He iterates fast: started with Obsidian MCP storage, quickly pivoted to local file storage when the MCP server was unreliable
- He values cross-repo consistency: wanted the skill to work "across all repos"
- He's comfortable delegating to sub-agents and understands the Task/background agent pattern
- He prefers things to be proactive/automatic rather than requiring manual invocation
- He gives broad direction and expects the AI to figure out the details ("think about where we're gonna store the data")

**Patterns noted**:
- Voice-first prompting style
- Systems thinking over one-off solutions
- Quick pivots when something doesn't work
- Trusts AI to handle implementation details
