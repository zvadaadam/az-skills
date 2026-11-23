<h1 align="center">az-skills</h1>
<p align="center">Skills I use with Claude Code and Codex.</p>

<p align="center">
  <a href="#whats-inside">Skills</a> &nbsp;&middot;&nbsp;
  <a href="#install">Install</a> &nbsp;&middot;&nbsp;
  <a href="https://skills.sh/zvadaadam/az-skills">Browse on skills.sh</a>
</p>

---

## Install

```bash
npx skills add zvadaadam/az-skills
```

[Update](#update) · [Uninstall](#uninstall)

## What's inside

Every name starts with `az-` so the skills stay together in your list and avoid clashes with built-ins like `/code-review` and names used by other collections.

### Engineering

| Skill | What it does |
|---|---|
| [az-greenlight-pr](skills/engineering/az-greenlight-pr/SKILL.md) | Gets a PR ready to merge by fixing CI, answering review threads, and checking the latest commit. |
| [az-code-review](skills/engineering/az-code-review/SKILL.md) | Reviews a branch or PR with three parallel reviewers (correctness, security, design) and reports only verified findings. |
| [az-deslop](skills/engineering/az-deslop/SKILL.md) | Strips AI slop from the code a branch added and simplifies it without changing behavior. |
| [az-complexity-check](skills/engineering/az-complexity-check/SKILL.md) | Audits a finished change for unneeded additions, droppable assumptions, spread, and duplication. Reports; does not edit. |
| [az-implementation-rehearsal](skills/engineering/az-implementation-rehearsal/SKILL.md) | Walks through a proposed change without writing it, finds the regressions and the prep refactor that makes it easy, and revises the plan. |
| [az-devs-roundtable](skills/engineering/az-devs-roundtable/SKILL.md) | Five legendary engineers (Carmack, Hickey, Metz, Torvalds, Beck) debate your problem in parallel, then converge. |
| [az-tour](skills/engineering/az-tour/SKILL.md) | Explores a subsystem and writes a self-contained HTML tour of it, optionally with an architecture critique. |
| [az-setup-agent-workflow](skills/engineering/az-setup-agent-workflow/SKILL.md) | Sets a repository up for agent work: a reliable dev loop, concise AGENTS.md guidance, task skills, and one demonstrated change-and-verify loop. |
| [az-verify-harness](skills/engineering/az-verify-harness/SKILL.md) | Gives a repo a verification harness agents actually use: a `control-<app>` driver and a user-POV feature map checked in CI. Based on Lauren Tan's ([@poteto](https://github.com/poteto)) verification skills in Cursor's pstack. |
| [az-call-advisor](skills/engineering/az-call-advisor/SKILL.md) | Calls the premium Fable advisor through the Claude Code CLI for hard judgment and design critique, with resumable sessions. |
| [az-call-worker](skills/engineering/az-call-worker/SKILL.md) | Calls a fast Codex worker through the Codex CLI for bounded implementation, tests, and repo exploration. |
| [az-multi-workspace-lead](skills/engineering/az-multi-workspace-lead/SKILL.md) | Directs coordinators across several Conductor workspaces when you ask. Checks file overlap and interface dependencies, sets landing order, and recovers stalled handoffs. |
| [az-workspace-coordinator](skills/engineering/az-workspace-coordinator/SKILL.md) | Coordinates builder, reviewer, and checker sessions for one change in one Conductor workspace. Reports to you when you assign it directly, or to the multi-workspace lead when the lead assigns it. |

### Product & Design

| Skill | What it does |
|---|---|
| [az-product-rehearsal](skills/product-design/az-product-rehearsal/SKILL.md) | Imagines a proposed feature has already shipped, walks a real user or agent through it, finds where it will be bad, and revises the proposal before anyone builds it. |
| [az-design-roundtable](skills/product-design/az-design-roundtable/SKILL.md) | Five legendary designers (Rams, Ive, Vignelli, Fukasawa, Jongerius) debate your brief in parallel, then converge. |

### Marketing

| Skill | What it does |
|---|---|
| [az-brand-name-explore](skills/marketing/az-brand-name-explore/SKILL.md) | Generates product and company names with five naming personas, based on David Placek's Lexicon method. |
| [az-ai-answer-audit](skills/marketing/az-ai-answer-audit/SKILL.md) | Traces an AI "best X" answer back to the searches, sources, and assumptions behind it. User-run and read-only. |
| [az-geo-optimize](skills/marketing/az-geo-optimize/SKILL.md) | Turns an `az-ai-answer-audit` into a prioritized plan to get a brand cited in AI answers. |

### Productivity

| Skill | What it does |
|---|---|
| [az-interview-me](skills/productivity/az-interview-me/SKILL.md) | Interviews you about a plan, one question at a time, until the agent has the context to build the right thing. |
| [az-noah-zender-it](skills/productivity/az-noah-zender-it/SKILL.md) | Ranks mental models from Noah Zender's idea library by leverage for your situation. |

## Update

```bash
npx skills update
```

## Uninstall

```bash
npx skills remove az-deslop
```

Replace `az-deslop` with the skill you want to remove. Add `--global` for a global install.

For older installs, see [renamed skills](docs/migration.md#renamed-skills) and [switching from the shell installer](docs/migration.md#shell-installer).
