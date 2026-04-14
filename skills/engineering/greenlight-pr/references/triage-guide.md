# Review Comment Triage Guide

## Process: Think → Decide → Act → Reply

Do NOT touch code before thinking. For each new comment:

### 1. Understand
- What exactly is the bot claiming?
- Read the `code_context` attached to the comment.
- Is it actually a problem, or a false positive?

### 2. Categorize

| Category | When | Action |
|----------|------|--------|
| **Fix** | Correct, actionable, and the fix is clean | Fix the code, commit |
| **Disagree** | Wrong, not applicable, or fix would over-engineer | Explain why with evidence |
| **Defer** | Valid but out of scope for this PR | Acknowledge, explain scope |

### 3. Prioritize
- Critical bug > Correctness > Maintainability > Style nit
- Group related Fix items into one commit
- Don't over-engineer: fix what's actually wrong

### 4. Reply (MANDATORY)

**Every inline comment** must get a reply:
```bash
# Fixed
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies -f body="Fixed — <description>. See <commit>"

# Disagree
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies -f body="I looked into this — <reasoning>."

# Defer
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies -f body="Good point — out of scope for this PR because <reason>."
```

**Top-level summary** after each round:
```bash
gh pr comment <pr> --body '## Greenlight — Round N
**Fixed (X):** brief list
**Disagreed (X):** brief reasoning
**Deferred (X):** brief reasoning'
```

### 5. Mark as processed
```bash
python3 gl-snapshot.py --mark-seen <comma-separated-ids>
```

## Agreement Criteria

Address the comment when ALL of these are true:
- Technically correct
- Actionable in the current branch
- Does not conflict with user intent
- Can be fixed cleanly without unrelated refactors
- The fix is simpler or equal in complexity to the current code

Do NOT auto-fix when:
- Ambiguous — needs clarification from the user
- Conflicts with explicit user instructions
- Requires product/design decisions the user hasn't made
- The fix would be a workaround, not a real solution
- The fix adds abstraction/complexity that doesn't earn its keep
