# Review Comment Triage Guide

## Process: Think → Decide → Act → Reply

Do NOT touch code before thinking. For each new comment:

### 1. Understand
- What exactly is the reviewer claiming?
- Read the referenced code to verify their claim.
- Is it actually a problem, or a false positive?

### 2. Categorize

| Category | When | Action |
|----------|------|--------|
| **Fix** | Correct and actionable | Fix the code, commit |
| **Disagree** | Wrong or not applicable | Explain why with evidence |
| **Defer** | Valid but out of scope | Acknowledge, explain scope |
| **Acknowledge** | Style nit, no functional impact | Note it, skip code change |

### 3. Prioritize
- Critical bug > Correctness > Maintainability > Style nit
- Group related Fix items for one commit
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
gh pr comment <pr> --body '## Review Response — Round N
**Fixed (X):** brief list
**Disagreed (X):** brief reasoning
**Deferred (X):** brief reasoning'
```

### 5. Mark as processed
```bash
python3 gl-snapshot.py --mark-seen <comma-separated-ids>
```

## Agreement Criteria (from Codex babysit-pr)

Address the comment when:
- Technically correct
- Actionable in the current branch
- Does not conflict with user intent
- Can be made safely without unrelated refactors

Do NOT auto-fix when:
- Ambiguous, needs clarification
- Conflicts with explicit user instructions
- Requires product/design decisions the user hasn't made
- Codebase is in a dirty/unrelated state
