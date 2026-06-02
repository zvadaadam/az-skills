---
name: code-review
description: Multi-lens code review — spawns parallel sub-agents to independently review branch changes for bugs, security, and design, then validates and reports only high-signal findings. Use when you want a thorough review before merging or when self-reviewing your own changes.
argument-hint: "[PR number, branch name, or leave blank for current branch]"
hooks:
  PostToolUse:
    - matcher: "*"
      hooks:
        - type: command
          command: 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill code-review --action started --agent-harness claude-code --quiet'
          timeout: 5
  Stop:
    - hooks:
        - type: command
          command: 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill code-review --action completed --agent-harness claude-code --quiet'
          timeout: 5
---

# Code Review

Run a rigorous, multi-perspective code review of the current branch's changes. Three independent reviewers examine the diff through different lenses, a validator filters false positives, and you get a structured report of only high-signal findings.

## Scoping the Review

**Always review the branch diff, never the full codebase.**

```bash
# Find the base branch
BASE=$(git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null)

# Committed changes on this branch
git diff $BASE...HEAD

# Uncommitted work in progress (staged + unstaged)
git diff HEAD

# Changed files
git diff --name-only $BASE...HEAD
```

Review **both** outputs: the first shows all committed changes relative to the base branch, the second catches any uncommitted WIP.

If `$ARGUMENTS` is a PR number, use `gh pr diff $ARGUMENTS` instead.

Before launching reviewers, read the diff yourself to understand the scope and intent of the changes. This context is essential for writing good reviewer prompts.

## Process

### Phase 0 — Signal Review Started

If reviewing a PR, **immediately** post a status comment so other tools (e.g., greenlight-pr) know a review is in progress and should wait:

```bash
gh pr comment $PR --body "$(cat <<'EOF'
## Code Review — In Progress

Review started. Analyzing changes...

<!-- code-review-status: in_progress -->
EOF
)"
```

The `<!-- code-review-status: in_progress -->` marker lets other tools detect that a review is running. The final summary in Phase 5 will include `<!-- code-review-status: complete -->` to signal completion.

### Phase 1 — Understand the Full Picture

Don't just read the diff — understand the world around it. A review without context is just pattern matching.

1. **Get the diff** and list of changed files
2. **Understand the intent** — read the PR description, commit messages, and any linked issues. What is the developer trying to achieve? What problem are they solving?
3. **Read each changed file in full** — understand the surrounding code, not just the changed lines
4. **Trace the connections** — follow imports, function calls, and type definitions into related files. If the diff touches a service, read its callers. If it changes an API, read its consumers. If it modifies a data model, read what queries it.
5. **Understand the product context** — look at the feature area, the module's README or docs, and how this change fits into the larger system. What is this module's purpose? Where is it heading?
6. **Check conventions** — read CLAUDE.md files (root + any in directories of changed files) for project rules

Build a mental model of:
- **What** the developer built and **why** (the product goal, not just the code)
- **How** it fits into the existing architecture
- **Where** this area of the codebase is heading (are there related TODOs, follow-up issues, or a pattern being established?)

This context is essential — pass it to every reviewer.

### Phase 2 — Review (3 Parallel Sub-Agents)

Spawn **3 sub-agents in parallel** using the Agent tool. Each receives:
- The branch diff
- PR title/description or commit messages explaining intent
- The list of changed files and their full contents
- **Context summary** from Phase 1: the product goal, how the change fits into the system, related files and their roles, and where this area of the code is heading
- Any relevant CLAUDE.md rules

Each reviewer operates independently and does not see other reviewers' findings.

**Every reviewer must explore the codebase before critiquing.** Read the related code, trace call chains, and understand the developer's intent. Judge the code against what it's trying to accomplish, not against an abstract ideal.

**Reviewer 1 — Logic & Correctness** (model: opus)

```
You are a code reviewer focused on CORRECTNESS. Your job is to find bugs, logic errors, and broken behavior.

BEFORE reviewing, explore the codebase:
- Read every changed file in full, not just the diff
- Follow imports and function calls into related files — understand what calls this code and what it calls
- Understand the developer's intent: what product goal does this serve? What behavior should it produce?

Then look for:
- Logic errors, off-by-one bugs, incorrect conditions
- Code that will fail to compile, parse, or run
- Missing null/undefined/error handling that WILL cause crashes (not hypothetical)
- Race conditions and concurrency issues in concurrent code
- Broken data flow — wrong types passed, missing transformations, lost values
- N+1 queries, infinite loops, unbounded growth
- Regressions — does this break existing behavior?
- Misalignment between the code and its stated purpose — does it actually achieve what the developer intended?

For each finding:
- Quote the exact code
- Explain what the code is trying to do (the developer's intent)
- Explain what will go wrong and under what conditions
- Rate confidence: HIGH (certain this is a bug) or MEDIUM (likely a bug)
- Suggest a fix

Do NOT flag: style preferences, naming opinions, potential issues that require unlikely inputs, or hypothetical concerns.
```

**Reviewer 2 — Security & Edge Cases** (model: opus)

```
You are a security-focused code reviewer. Your job is to find vulnerabilities and dangerous edge cases.

BEFORE reviewing, explore the codebase:
- Read every changed file in full, not just the diff
- Trace the data flow: where does user input enter? What transformations does it go through? Where does it end up?
- Understand the system boundaries — what is trusted internal code vs. what faces external input?
- Check what security patterns the project already uses (middleware, validation layers, auth checks)

Then look for:
- Injection vulnerabilities (SQL, XSS, command injection, path traversal)
- Authentication/authorization bypasses or missing checks
- Sensitive data exposure (secrets in logs, error messages, responses)
- Insecure deserialization, SSRF, open redirects
- Input validation gaps at system boundaries
- Unsafe file operations, resource exhaustion vectors
- Dependency issues — known vulnerable patterns

For each finding:
- Quote the exact vulnerable code
- Explain what the code is trying to do and where it falls short on security
- Describe the attack vector — how would someone exploit this?
- Rate severity: CRITICAL (exploitable now) or HIGH (exploitable under realistic conditions)
- Suggest a mitigation

Do NOT flag: theoretical concerns without a realistic attack path, or issues that existing middleware/frameworks already handle.
```

**Reviewer 3 — Design & Maintainability** (model: sonnet)

```
You are a senior engineer reviewing for design quality. Your job is to catch structural problems that will cause pain later.

BEFORE reviewing, explore the codebase:
- Read every changed file in full and the files around it — understand the module's architecture
- Look at the broader feature area: what patterns does this codebase use? What conventions are established?
- Understand the product direction: what is this feature for? What are the likely next steps? Is the code structured to support where it's heading?
- Check for related TODOs, follow-up issues, or emerging patterns that signal intent

Then look for:
- Wrong abstraction level — over-engineered or under-engineered for the problem and its likely evolution
- API design that is confusing, inconsistent, or easy to misuse
- Missing or misleading tests — tests that pass but don't actually verify the behavior
- CLAUDE.md or project convention violations (quote the exact rule)
- Code that fights the existing architecture rather than extending it naturally
- Duplicated logic that should share an implementation
- Breaking changes to public APIs without migration path
- Misalignment between the code structure and where the product is heading

For each finding:
- Explain what the developer is building toward and how the structure falls short
- Rate impact: HIGH (will cause real problems soon) or MEDIUM (worth addressing)
- Suggest an alternative approach that fits the codebase's direction

Do NOT flag: minor style preferences, cosmetic issues, or matters of taste.
```

### Phase 3 — Validate

After all three reviewers report back:

1. **Deduplicate** — merge findings that describe the same issue from different angles. When multiple reviewers flag the same issue, promote its severity (this is a strong signal).

2. **Validate each finding** — for every issue rated HIGH or CRITICAL:
   - Read the actual code to confirm the issue exists
   - Check if surrounding context (types, middleware, tests) already handles it
   - Drop any finding you cannot verify in the code

3. **Classify** each validated finding:
   - **Blocking** — must fix before merge (confirmed bugs, security vulnerabilities, broken tests)
   - **Should Fix** — real issues worth addressing (design problems, missing edge cases, convention violations)
   - **Consider** — optional improvements backed by solid reasoning
   - **Praise** — patterns or decisions done well (reinforces good work)

### Phase 4 — Comment

Post each finding as an **inline comment** on the exact line of code where the issue lives.

**If reviewing a PR** (`$ARGUMENTS` is a PR number), post inline review comments using the GitHub API:

```bash
# Get the latest commit SHA
COMMIT_SHA=$(gh pr view $PR --json headRefOid -q .headRefOid)

# Post an inline comment on a specific line
gh api repos/{owner}/{repo}/pulls/$PR/comments \
  -f body="$COMMENT_BODY" \
  -f commit_id="$COMMIT_SHA" \
  -f path="$FILE_PATH" \
  -F line=$LINE_NUMBER \
  -f side="RIGHT"
```

**If reviewing a branch** (no PR), output each comment with its file location — the user can navigate to each one.

**Each inline comment must:**

1. **Explain what the code is doing** — describe the behavior at this line so the reader doesn't have to re-derive it
2. **Explain what's wrong** — the specific bug, vulnerability, or design flaw
3. **Explain the impact** — what will happen if this ships (crash, data loss, security breach, maintenance pain)
4. **Suggest a fix** — concrete code or approach, not vague advice. For small self-contained fixes, include a code suggestion block. For larger structural changes, describe the approach.

Example inline comment:
```
**Bug: off-by-one in pagination**

This line calculates the last page as `total / pageSize`, but when `total` is
exactly divisible by `pageSize`, it creates an empty final page. For 100 items
with pageSize=10, this returns 11 pages where page 11 is empty.

**Impact:** Users see a blank last page on every paginated list.

**Fix:**
\`\`\`suggestion
const lastPage = Math.ceil(total / pageSize);
\`\`\`
```

**Rules for inline comments:**
- **One comment per issue.** Do not post duplicate comments for the same finding.
- **Only you post comments.** Sub-agents must never post comments themselves — they report findings back to you, and you post.

### Phase 5 — Summary

After posting inline comments, output a summary:

```markdown
## Code Review — [branch or PR title]

**Scope:** N files changed, +X/-Y lines
**Verdict:** APPROVE | REQUEST CHANGES | DISCUSS

### Findings

#### Blocking
- **[file:line]** One-line description.

#### Should Fix
- **[file:line]** One-line description.

#### Consider
- **[file:line]** One-line description.

### Praise
- What was done well and why it's good.

### Summary
1-3 sentences on the overall quality, key risks, and recommended next steps.

<!-- code-review-status: complete -->
```

If there are no blocking issues, say so clearly: **"No blocking issues found."**

If reviewing a PR, also post the summary as a top-level PR comment. The `<!-- code-review-status: complete -->` marker signals to other tools (e.g., greenlight-pr) that the review is finished and the verdict is final.

```bash
gh pr comment $PR --body "$(cat <<'EOF'
[the summary output, including the <!-- code-review-status: complete --> marker]
EOF
)"
```

## False Positives (Do NOT Flag)

Use this list when evaluating and validating findings — these are NOT real issues:

- **Pre-existing issues** — problems that exist on the base branch, not introduced by this diff
- **Correct code that looks suspicious** — something that appears buggy but is actually intentional
- **Pedantic nitpicks** a senior engineer would wave through
- **Linter-catchable issues** — the linter will handle these (do not run the linter to verify)
- **General quality concerns** (e.g., missing test coverage, vague security worries) unless explicitly required by CLAUDE.md
- **Silenced rules** — issues covered by an explicit ignore comment (e.g., `// eslint-disable`, `# noqa`)
- **Subjective suggestions** — "you might want to consider..." or "it would be nice if..."
- **Potential issues that "might" be problems** — if it requires interpretation or judgment calls, drop it

## Guardrails

- **High signal only.** Every finding must be something a senior engineer would flag. If you're not confident an issue is real, drop it.
- **No rubber stamps.** "Looks good" with no analysis is not a review. Always explain what you checked, even if you found nothing.
- **No noise.** Don't flag style, naming, or formatting unless it violates an explicit project rule.
- **Verify before reporting.** Read the actual code before claiming something is a bug. False positives erode trust.
- **Explain the why.** For every finding, explain why it matters — not just what's wrong, but what will happen if it ships.
- **Acknowledge good work.** The praise section is not optional. Good patterns should be reinforced.

## Fallback: No Sub-Agents

If sub-agents are not available, perform all review axes yourself sequentially: read the diff, check CLAUDE.md compliance, scan for bugs, review design, validate each finding, then report. The process is the same — just single-threaded.

---

## AZ Skill Feedback

After the run, if this skill was useful, confusing, broken, or missing context, submit 1-3 safe sentences. Include `--agent-harness` when known. Include `--model-config` only if the harness exposes the exact model/config; otherwise leave it as `unknown`:

`python3 ~/.agents/skills/skill-feedback/scripts/skill-feedback.py --skill code-review --rating idea --text "..."`

Never include secrets, private data, source code, long prompts, or stack traces.
