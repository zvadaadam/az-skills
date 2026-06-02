---
name: interview-me
description: Interview the user about a plan, design, or idea until reaching shared understanding. Walks down every branch of the decision tree, resolving dependencies one by one. Maintains a durable transcript on disk so the interview survives context loss. Use when you want to stress-test a plan, think through a design, or need the agent to gather all the context it needs before building.
argument-hint: "[what you're planning, designing, or building]"
hooks:
  PostToolUse:
    - matcher: "*"
      hooks:
        - type: command
          command: 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill interview-me --action started --agent-harness claude-code --quiet'
          timeout: 5
  Stop:
    - hooks:
        - type: command
          command: 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill interview-me --action completed --agent-harness claude-code --quiet'
          timeout: 5
---

# Interview Me

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one by one.

## The Topic

$ARGUMENTS

## Durable Transcript

The interview lives in a markdown file on disk. Your context window may be cleared mid-interview — the file is the source of truth. Never rely on conversation memory alone.

**File location**:
- `.context/interview-me/<slug>.md` if a `.context/` directory exists at the workspace root (conductor convention)
- `./interview-me-<slug>.md` otherwise

`<slug>` is a 2–4 word kebab-case identifier derived from the topic (e.g. `auth-rewrite`, `pricing-page`).

**Before asking the first question**:
1. Glob both candidate locations for any existing `interview-me*.md` file.
2. If one matches this topic (same slug or semantically close), read it. Tell me in one short message: what's resolved, what's still open, and the next question you intend to ask. Then resume — don't restart.
3. If none matches, create the file using the structure below, then ask question 1.

**File structure**:

```
# Interview: <topic>

**Status**: in-progress
**Started**: YYYY-MM-DD
**Last updated**: YYYY-MM-DD

## Topic
<full $ARGUMENTS verbatim>

## Open Questions
- [ ] short phrasing of each unresolved question

## Resolved Decisions
- <decision> — <one-line reason>

## Q&A Log

### Q1: <question>
**Recommendation**: <your suggested answer + reasoning>
**Answer**: <user's actual answer, paraphrased if long>
**Notes**: <what got pinned down, or what new sub-questions this opened>

### Q2: ...
```

**Update after every one of my answers, before posing the next question**:
1. Append the Q&A entry to `## Q&A Log`.
2. Move the resolved item from `## Open Questions` into `## Resolved Decisions`.
3. Add any newly-revealed sub-questions to `## Open Questions`.
4. Bump `Last updated`.

The update is one atomic step — don't ask the next question until the file reflects the last answer.

## How to Interview

1. **Start broad** — understand the goal, the audience, and the constraints
2. **Go deep on each branch** — when an answer opens sub-questions, follow them before moving on
3. **One question at a time** — never ask multiple questions in one message
4. **Recommend an answer** — for each question, give your suggested answer with reasoning, then ask if I agree or want to go a different direction
5. **Explore the codebase first** — if a question can be answered by reading existing code, configs, or docs, do that instead of asking me
6. **Resolve dependencies** — if decision B depends on decision A, make sure A is settled first
7. **Challenge my answers** — if something doesn't add up or could be simpler, push back

## What You're Building Toward

By the end of this interview, you should have everything you need to:
- Write a clear implementation plan
- Make confident design decisions without guessing
- Know exactly what to build and what to skip
- Understand the tradeoffs I'm willing to make

## When to Stop

Stop interviewing when:
- Every branch of the decision tree is resolved
- You could explain the plan back to me and I'd say "yes, exactly"
- There are no open questions that would change the approach

Then flip `Status` to `complete`, append a `## Plan` section to the file with the actionable plan synthesized from the Q&A log, and show that plan back to me.

---

## AZ Skill Feedback

After the run, if this skill was useful, confusing, broken, or missing context, submit 1-3 safe sentences. Include `--agent-harness` when known. Include `--model-config` only if the harness exposes the exact model/config; otherwise leave it as `unknown`:

`python3 ~/.agents/skills/skill-feedback/scripts/skill-feedback.py --skill interview-me --rating idea --text "..."`

Never include secrets, private data, source code, long prompts, or stack traces.
