# Triage Process

Full decision process for handling AI code review comments. All decision points are pseudocode — follow them step by step.

## Phase 1: Evaluate (sub-agents)

Spawn one sub-agent per comment (or batch related comments on the same file).

### Sub-agent prompt

```
You are evaluating an AI code review comment on a PR.

COMMENT:
{comment.body}

CODE CONTEXT (diff hunk):
{comment.code_context}

FILE PATH:
{comment.path}

Read the full file if the diff hunk is not enough context.

EVALUATE:
1. Is the bot's claim technically correct? Verify against the actual code.
2. If correct — is the suggested fix the RIGHT fix, or would it be:
   - A workaround that hides a deeper issue?
   - Over-engineered for the actual risk?
   - Requiring changes to unrelated code?
3. If you would fix it — what is the simplest correct change?

RESPOND AS JSON:
{
  "verdict": "FIX" | "DISAGREE" | "DEFER",
  "reasoning": "1-2 sentences",
  "fix_sketch": "what to change, in which file (only if FIX)",
  "confidence": "HIGH" | "MEDIUM" | "LOW"
}
```

## Phase 2: Synthesize

Collect all sub-agent results. Make the final call:

```
triage_report = []

for each result in sub_agent_results:

  if result.verdict == "FIX":
    if result.confidence == "HIGH":
      # trusted — implement as-is
      triage_report.append({
        action: "FIX",
        comment_id: result.comment_id,
        fix: result.fix_sketch
      })

    elif result.confidence == "MEDIUM":
      # verify the fix passes quality check
      if quality_check(result.fix_sketch) == PASS:
        triage_report.append({ action: "FIX", ... })
      else:
        # fix doesn't meet bar — rethink or disagree
        triage_report.append({ action: "DISAGREE", reason: "fix would be worse than the issue" })

    elif result.confidence == "LOW":
      # don't trust — read the code yourself, make final call
      my_verdict = read_code_and_decide(result)
      triage_report.append(my_verdict)

  elif result.verdict == "DISAGREE":
    # verify the reasoning is solid before replying
    if reasoning_holds_up(result.reasoning):
      triage_report.append({ action: "DISAGREE", reason: result.reasoning })
    else:
      # agent was wrong to disagree — re-evaluate as potential FIX
      re_evaluate(result)

  elif result.verdict == "DEFER":
    triage_report.append({ action: "DEFER", reason: result.reasoning })
```

### quality_check(fix_sketch)

```
def quality_check(fix):
  if fix is a workaround or band-aid:
    return FAIL  # find the real fix or disagree

  if fix introduces new abstractions that aren't justified:
    return FAIL  # inline it, keep it simple

  if fix adds more complexity than the issue it solves:
    return FAIL  # the cure is worse than the disease

  if fix touches code unrelated to the comment:
    return FAIL  # scope creep — defer instead

  if fix would not pass a senior engineer's code review:
    return FAIL  # rethink

  return PASS
```

### Priority ordering

```
sort triage_report.FIX items by:
  1. critical bug / data corruption     → fix first
  2. correctness / logic error           → fix next
  3. maintainability / clarity           → fix if clean and simple
  4. style nit / naming preference       → skip unless trivial
```

## Phase 3: Act

### Implement fixes

```
fixes = [item for item in triage_report if item.action == "FIX"]

if len(fixes) > 0:
  for each fix in fixes:
    apply fix to codebase
  commit all fixes in one commit with descriptive message
```

### Reply to every comment (MANDATORY)

```
for each item in triage_report:

  if item.action == "FIX":
    reply to comment:
      "Fixed — {description}. See {commit_sha}"

  elif item.action == "DISAGREE":
    reply to comment:
      "I looked into this — {reasoning}."

  elif item.action == "DEFER":
    reply to comment:
      "Good point — out of scope for this PR because {reason}."
```

Reply commands:
```bash
# Reply to inline comment
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies \
  -f body="<reply text>"
```

### Post round summary

```bash
gh pr comment <pr> --body '## Greenlight — Round N
**Fixed (X):** brief list of what was fixed
**Disagreed (X):** brief reasoning for each
**Deferred (X):** brief reasoning for each'
```

### Mark as processed

```bash
python3 gl-snapshot.py --mark-seen <comma-separated-ids>
```

## When to stop iterating

```
if round >= 3:
  new_comments = only_nits_or_duplicates(snapshot.new_comments)
  if new_comments:
    stop — reply "Acknowledged" to remaining nits, report to user

if any comment requires a product/design decision:
  stop — ask the user

if any comment is ambiguous and could be interpreted multiple ways:
  stop — ask the user
```
