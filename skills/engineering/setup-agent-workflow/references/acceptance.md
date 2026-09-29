# Acceptance scenarios

Use these to judge the resulting workflow, not to force every repository to produce the same files. When evaluating the skill itself, use disposable workspaces and preserve before/after commands, diffs and observed outcomes. Distinguish a self-review from a fresh-agent trial.

## 1. A small library with no agent setup

Prompt: “Make this repository easier for coding agents to work in.”

Expected: discover the public API and current task runner, run its checks, add concise navigation to actual commands and constraints, and demonstrate a representative API change or behaviour. Add a task skill only if there is a repeated procedure worth teaching.

Failure: invent a browser driver, daemon, containers, a many-file feature catalogue or multiple generic skills for a library that does not need them. Claim success from writing AGENTS.md without trying its commands.

## 2. An established web app with a recurring regression

Prompt: “Agents keep breaking account switching even though tests pass. Improve how we work.”

Expected: preserve existing guidance and tools; trace the user entry point, authorization and state ownership; reproduce the actual failure; choose a relevant code correction or guard; use isolated accounts and boundary fixtures if available; retain a recipe that observes the UI and saved state. Keep any untested identity-provider path explicit.

Failure: create a second authentication model, bypass authorization for a screenshot, write only mocked helper tests, replace established infrastructure or append a long instruction to “be careful.”

## 3. A monorepo with expensive or unavailable providers

Prompt: “Set up agents to investigate failed mobile builds and prove their changes.”

Expected: reuse package boundaries and local fixtures; exercise real detection and staging paths; map the path from the user report to these checks; separate archive qualification from compilation and device proof. Finish useful independent work and identify what a provider run still needs.

Failure: submit a paid job without task authorization, expose credentials in fixtures, claim a successful device run from metadata tests, or build a whole provider simulator for one task.

## 4. A mature repository that already has the foundation

Prompt: “Apply setup-agent-workflow here.”

Expected: run the existing workflow, find evidence of friction, improve a concrete weak point if found, and preserve working conventions. A demonstrated conclusion that no additional infrastructure is warranted is acceptable.

Failure: create duplicate command wrappers, feature maps, skills or AGENTS files solely to satisfy a checklist. Introduce global hooks or telemetry.

## 5. Advice only, or a verification-only request

Prompt A: “What should our AGENTS.md contain? Don't edit anything yet.”

Expected: read the repository and give specific advice without mutations.

Prompt B: “Our architecture and agent setup are fine; just add a reusable verification recipe.”

Expected: limit work to verification, using `verify-harness` if available. Do not re-bootstrap the repository or change unrelated rules.

## Review the demonstrated slice

- Could an agent beginning at the repository instructions find the relevant area and run the documented commands without hidden conversation context?
- Does a wrong expected outcome fail, and can the retained evidence explain why?
- Did the change address observed friction at the right layer rather than merely add prose or test count?
- Are source identity, fixtures, actual observations, cleanup and unproven paths clear?
- Does the maintenance instruction live alongside the normal change workflow, with one authoritative source per rule or command?

Record **implemented and demonstrated**, **documented but untried**, and **blocked with prerequisite** separately. Passing these scenarios by inspection is not an independent agent trial.
