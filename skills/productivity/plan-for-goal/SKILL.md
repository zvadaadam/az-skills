---
name: plan-for-goal
description: Turn whatever's in the current conversation into one prompt to hand to the agent's `/goal` orchestration loop (Claude Code, Codex, or any harness with the same shape). The prompt is re-injected on every turn of the loop, so it must hold direction, taste, and a self-verification path across many iterations. Use when you're ready to hand a piece of work to `/goal`.
argument-hint: "[optional: extra context or constraints]"
---

# Plan for Goal

Craft **one prompt** to hand to a coding agent's `/goal` command. The prompt is **re-injected on every turn** of the orchestration loop — it must hold up cold, without any "as discussed earlier".

## The Topic

$ARGUMENTS

## How `/goal` works

`/goal` is a self-perpetuating loop, not a one-shot task. The objective the user pastes in is re-injected on every continuation turn until the agent decides the work is complete. Each turn the agent re-reads the prompt from scratch, inspects the current state of the repo, and either keeps working or marks the goal complete *after auditing every requirement against current evidence*. The harness already enforces verification rigor, scope preservation, and budget discipline — your prompt's job is to set **direction, taste, and a bar that's actually auditable**.

A good goal is **bigger than one prompt but smaller than an open-ended backlog** — one objective with one stopping condition, sized so the loop can run for hours without your input but knows when to stop.

## What the prompt must contain

Use the conversation so far as your input. The prompt you produce needs five things:

1. **A directional outcome.** What's true about the world when this is done. Outcome, not a task list. Not "implement X", but "users can do Y and it feels Z".

2. **The quality bar — the hell-of-a-thing line.** Vivid, opinionated, sensory. This is the compass for the hundred micro-decisions the loop will make. Two opinionated sentences beat a paragraph of qualifiers. Examples: *"Boring. Bulletproof. Nobody on the team thinks about payments after this ships."* / *"Feels like the OS did it, not a bolt-on."* / *"Reads like a colleague summarized your week, not a robot stapling bullets together."*

3. **How to close the loop.** How the agent verifies, by itself, that this is working — every iteration. Which command to run, which surface to poke (browser, simulator, CLI, tests), what counts as "actually working" vs "compiles". Use the tools actually available in this environment. For web/mobile/desktop work, the loop needs a tool that can drive that surface — see `references/self-verification-tools.md` and tell the user upfront if the relevant tool isn't installed, so they can install it before running `/goal`. *End with one explicit line:* **`Done = …`** *— a single boolean the completion audit can map evidence to.*

4. **Scope edges.** What's in, what's not, and which choices the agent is free to make. The highest-leverage move here is the **`Not:`** list — the adjacent features the agent will be tempted to build and shouldn't (`--verbose`, a refactor, a second flag). Naming them upfront is what keeps a 30-turn loop from sprawling.

5. **Where to look.** Files, designs, prior art that orient the agent. The agent reads current state every turn — point at the state that matters most so it doesn't grep blind.

## Rules for the prompt

- **Directional, not prescriptive.** Describe the destination vividly; let the agent pick the route. No step-by-step recipes, no locked-in libraries unless the user explicitly required them.
- **One objective, not a backlog.** If you find yourself listing unrelated tasks, you have multiple goals — split them. A goal is one durable target with one stopping condition.
- **Re-readable cold.** No "continue", "finish what's left", "as we discussed". Each turn re-reads this from scratch.
- **Under 4000 characters — hard limit.** Most `/goal` implementations clip past this. Measure before showing (see step 4 below); don't ship a draft you haven't counted.
- **2-4 sentences per anchor.** The prompt is re-injected every turn; padding compounds across the whole loop.
- **Don't duplicate the harness.** The continuation template already enforces completion audits, scope preservation, and budget discipline. Don't restate that.

## How to use it

1. Read the conversation. If something critical is missing for one of the pieces above, ask — one targeted question at a time, with your best guess attached.
2. Draft the prompt as plain prose with clear sections.
3. **Cold-read self-check before showing it.** Re-read your own draft as if it were turn 50 and you had zero other context. If you can't tell what "done" looks like, fix the close-the-loop section before showing the user.
4. **Measure the draft against the 4000-char limit.** Pipe it through `wc -m` (or count yourself if no shell) and verify the result is `< 4000`. If it's over, tighten — cut adverbs, fold redundant anchors, drop examples from the quality bar — and re-measure. Don't show the user a draft you haven't measured. State the final count to the user in one line above the code block (e.g. *"3,847 chars — under the 4000 cap."*) so they can trust it without re-checking.
5. Copy the final prompt to the clipboard, then show it in a single fenced code block so the user can paste it straight into `/goal`.
6. Offer to sharpen the voice, tighten, or restore anchors the user flags missing.
7. If the loop drifts later, come back here and **rewrite the goal** — the harness re-reads the prompt every turn, so a tighter prompt is the lever, not patches to a running goal.

---

**References:**
- `references/examples.md` — three worked example prompts (migration, feature build, optimization). Read it when calibrating voice or seeing how anchors flex per domain.
- `references/self-verification-tools.md` — CLI/MCP tools that let the loop drive a browser, simulator, or desktop (`agent-browser`, `agent-device`, `cua`). Consult before drafting close-the-loop for any UI work; warn the user if nothing's installed.
