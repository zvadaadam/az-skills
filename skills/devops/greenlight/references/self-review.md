# Self-Review Templates (SELF mode)

When no bot reviewers are detected, spawn 2-3 review sub-agents in parallel on the full PR diff. Each agent focuses on one concern.

## How to run

```bash
DIFF=$(git diff origin/main...HEAD)
```

Spawn agents in parallel with the Agent tool, each with one of these prompts:

## Agent 1: Correctness

```
Review this PR diff for correctness issues. Title: {pr_title}

Focus on:
- Logic errors, off-by-one, null/nil handling
- Race conditions, thread safety
- Missing error handling for failure paths
- Edge cases that would crash or corrupt data
- State management bugs (stale state, leaks)

Rules:
- Only flag things that are actually wrong or risky
- Each finding: file, line range, what's wrong, suggested fix
- Severity: critical > correctness > maintainability
- If everything looks fine for your focus area, say so

Diff:
{diff}
```

## Agent 2: API & Interface

```
Review this PR diff for API and interface quality. Title: {pr_title}

Focus on:
- Public API design: are types, names, and signatures clear?
- Backwards compatibility: does this break existing callers?
- Naming consistency: do new names match existing conventions?
- Type safety: are there unnecessary force casts, Any types, or loose typing?
- Protocol conformance: are Codable, Hashable, Identifiable correct?

Rules:
- Only flag things that are actually wrong or risky
- Each finding: file, line range, what's wrong, suggested fix
- Skip style preferences — focus on things that affect correctness or usability
- If everything looks fine for your focus area, say so

Diff:
{diff}
```

## Agent 3: Architecture & Performance

```
Review this PR diff for architecture and performance. Title: {pr_title}

Focus on:
- Performance: O(n²) loops, unnecessary allocations, work on main thread
- Memory: retain cycles, unbounded caches, leaked observers
- Architecture: circular dependencies, God objects, missing abstractions
- Concurrency: @MainActor violations, data races, deadlocks

Rules:
- Only flag things that are actually wrong or risky
- Each finding: file, line range, what's wrong, suggested fix
- Don't flag theoretical issues — only things likely to cause real problems
- If everything looks fine for your focus area, say so

Diff:
{diff}
```

## After agents return

Collect all findings, triage them (Fix/Disagree/Defer), fix actionable ones, commit, push. Post a self-review summary as a PR comment.
