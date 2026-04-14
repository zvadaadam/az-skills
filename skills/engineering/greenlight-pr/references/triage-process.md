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

## Phase 2: Synthesize + surface decisions

Collect all sub-agent results. Before implementing anything, check if you need human input.

```
triage_report = []
questions_for_user = []

for each result in sub_agent_results:

  # ── First: can I resolve this myself? ──────────────
  if result needs a judgment call:
    answer = check_existing_context(
      conversation_history,   # user may have already said their intent
      pr_description,         # PR body often explains the "why"
      code_comments,          # inline comments in the code itself
    )
    if answer found:
      use answer, continue    # don't ask what's already known

  # ── Collect questions I genuinely can't answer ─────
  if result.verdict == "FIX" and fix_requires_product_decision(result):
    # e.g. "should this fail silently or surface to user?"
    questions_for_user.append({
      comment_id: result.comment_id,
      question: describe_the_tradeoff(result)
    })
    continue  # don't decide yet — wait for answer

  if two sub-agents conflict on the same area:
    # e.g. one says simplify, another says make extensible
    questions_for_user.append({
      comment_ids: [a.comment_id, b.comment_id],
      question: "these pull in different directions — which do you prefer?"
    })
    continue

  if result.fix_sketch would open a bigger refactor:
    questions_for_user.append({
      comment_id: result.comment_id,
      question: "the right fix here goes beyond this PR — want to go there?"
    })
    continue

  # ── Route by confidence ────────────────────────────
  if result.verdict == "FIX":
    if result.confidence == "HIGH":
      triage_report.append({
        action: "FIX",
        comment_id: result.comment_id,
        fix: result.fix_sketch
      })

    elif result.confidence == "MEDIUM":
      if quality_check(result.fix_sketch) == PASS:
        triage_report.append({ action: "FIX", ... })
      else:
        triage_report.append({ action: "DISAGREE", reason: "fix would be worse than the issue" })

    elif result.confidence == "LOW":
      my_verdict = read_code_and_decide(result)
      triage_report.append(my_verdict)

  elif result.verdict == "DISAGREE":
    if reasoning_holds_up(result.reasoning):
      triage_report.append({ action: "DISAGREE", reason: result.reasoning })
    else:
      re_evaluate(result)

  elif result.verdict == "DEFER":
    triage_report.append({ action: "DEFER", reason: result.reasoning })

# ── Ask user if needed (batched, not one at a time) ──
if questions_for_user:
  present all questions to user in one message
  wait for answers
  use answers to resolve the pending items
  append resolved items to triage_report
```

### What counts as a question worth asking

```
def should_ask_user(result):
  # YES — real decisions that need human judgment:
  #   "should this error be silent or visible?"
  #   "do you want extensibility or simplicity here?"
  #   "this fix opens a bigger refactor — worth it?"
  #   "two suggestions conflict — which direction?"

  # NO — things you can figure out yourself:
  #   "what does this function return?" → read the code
  #   "is this variable used?" → grep for it
  #   "what framework is this?" → obvious from imports
  #   anything answerable from code, PR description, or conversation context

  return requires_human_judgment_about_intent_or_direction(result)
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
  if all new comments are nits or duplicates of already-addressed issues:
    reply "Acknowledged" to remaining nits
    stop — report final state to user

if user answered questions and all items are resolved:
  proceed to Act — no need to stop

if user says "that's enough" or "ship it":
  stop — respect the call

if bot keeps re-raising the same point after you disagreed:
  reply once more with reasoning, then stop — don't loop forever
```
