---
name: interview-me
description: Interview the user about a plan, design, or idea until reaching shared understanding. Walks down every branch of the decision tree, resolving dependencies one by one. Use when you want to stress-test a plan, think through a design, or need the agent to gather all the context it needs before building.
argument-hint: "[what you're planning, designing, or building]"
---

# Interview Me

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one by one.

## The Topic

$ARGUMENTS

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

Then summarize everything into a clear, actionable plan.
