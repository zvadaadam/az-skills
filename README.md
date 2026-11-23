<p align="center">
  <h1 align="center">az-skills</h1>
  <p align="center">
    A curated set of skills I use with my agents. Feel free to grab what's useful.
  </p>
</p>

<p align="center">
  <a href="#install">Install</a> &nbsp;&middot;&nbsp;
  <a href="#whats-inside">Skills</a> &nbsp;&middot;&nbsp;
  <a href="#update">Update</a> &nbsp;&middot;&nbsp;
  <a href="#feedback">Feedback</a> &nbsp;&middot;&nbsp;
  <a href="https://skills.sh/zvadaadam/az-skills">Browse on skills.sh</a>
</p>

---

## Install

From your project, run the skills.sh CLI with Node.js 22.20 or later.

```bash
npx skills add zvadaadam/az-skills
```

Choose the skills and agents you use. Add `--skill deslop` to pick one by name or `--global` to install across projects.

## Update

```bash
npx skills update
```

## Uninstall

Remove a skill by name. Add `--global` if you installed it globally.

```bash
npx skills remove deslop
```

<details>
<summary>Switching from the old installer</summary>

1. In the original clone, if `git config --local --get core.hooksPath` prints `.githooks`, run `git config --local --unset-all core.hooksPath '^\.githooks$'`. This prevents a later checkout or pull from reinstalling the links.
2. Run `./scripts/uninstall.sh` there if it still exists. In `~/.claude/skills`, `~/.agents/skills`, and `~/.codex/skills`, unlink any remaining symlinks that point into that clone. For each link you remove manually, restore the newest matching `<name>.backup.<timestamp>` directory to `<name>` if present.
3. If you used the retired `skill-feedback` package, remove its `skill-feedback/scripts/skill-event.py` handler from `PostToolUse` in `~/.claude/settings.json` and delete `~/.az-skills/installation-id` if present. For a CLI-installed copy, also run `npx skills remove skill-feedback` in its original scope.

Then run the install command above. Add `--global` to match the old installer's scope.

</details>

## Feedback

Report broken, confusing, outdated, or notably good behavior through [Hivenet](https://hivenet.app/p/az-skills):

```sh
DO_NOT_TRACK=1 npx --yes hivenet@latest --to az-skills --dsn https://hv_pub_9f0d072c2ba5840245d83437@hivenet.app/az-skills --category skill --subject "<skill-name>" "<specific, actionable feedback>"
```

The [`az-skills-feedback` skill](skills/engineering/az-skills-feedback/SKILL.md) covers structured failed-task reports for the team's eval corpus, attachments, and follow-up questions and replies. The bundled publishable DSN fixes the destination to az-skills; no user-provided key is needed. These examples disable automatic context collection. Keep reports specific and never include secrets or private data.

To opt out of the Skills CLI's install counts, prefix its commands with `DISABLE_TELEMETRY=1`. [CLI telemetry settings](https://skills.sh/docs/cli)

---

## What's inside

### Engineering
- **az-skills-feedback** — Hivenet support channel for skill feedback, structured failed-task reports, and replies from the az-skills team
- **call-advisor** — Calls the premium Fable advisor through Claude Code CLI for hard judgment, architecture, and frontend/design critique, with resumable sessions and saved output artifacts
- **call-worker** — Calls the fast Codex GPT-5.5 worker through Codex CLI for clean code implementation, repo exploration, tests, and bounded engineering tasks
- **code-review** — Multi-lens code review with 3 parallel sub-agents (correctness, security, design) that validates and reports only high-signal findings
- **devs-roundtable** — 5 legendary engineers (Carmack, Hickey, Metz, Torvalds, Beck) debate your problem in parallel, then build consensus
- **code-simplifier** — Reviews code for clarity and maintainability, then cleans it up
- **complexity-check** — Audits a change for unnecessary additions, assumptions, spread, and duplication
- **deslop** — Detects and removes AI-generated code slop (unnecessary abstractions, over-engineering, verbose patterns)
- **implementation-rehearsal** — Walks through a proposed implementation without changing code, challenges likely regressions, and revises the plan before building
- **pre-factor** — Auto-fires before a feature or non-trivial change: maps the code the change will land in and surfaces the prep refactors that make the change easy (reshape the seam, add a safety net, kill duplication) — each one traced to the upcoming change, landed as its own commit first. The before-bookend to `complexity-check`
- **repo-history-book** — Builds an evidence-backed account of how a project evolved from its commits, PRs, releases, and docs
- **setup-agent-workflow** — Sets up a repository for effective AI agent work: learn the product, repair the development loop, encode recurring mistakes in code and checks, connect concise AGENTS.md guidance to task skills and feature knowledge, then demonstrate and maintain a complete change-and-verification loop. Reuses existing tools and adds only what the repository needs
- **tour** — Explores a codebase subsystem and produces a self-contained HTML tour
- **verify-harness** — Gives a repo a verification harness its agents actually use: a `control-<app>` driver CLI that runs the real app in an isolated session and drives it the way a person and an agent do, plus a user-POV feature map (what exists, how to reach it, a replayable recipe of `expect`s, what misleads) checked in CI for completeness. Covers setup, expanding the map with parallel mappers, verifying a change with proof, reproducing reports, and maintenance — with a "no silent scripts" gaps loop that turns every one-off probe into a driver command. Based on Lauren Tan's (@poteto) verification skills in Cursor's pstack

### Design
- **design-roundtable** — 5 legendary designers (Rams, Ive, Vignelli, Fukasawa, Jongerius) debate your brief in parallel, then build consensus

### Marketing
- **brand-name-explore** — Generates product/company names using multiple creative personas (Lexicon methodology, poet, linguist, culture hacker, futurist)
- **ai-answer-audit** — Reverse-engineers an AI "best X" answer back to the searches, sources, and assumptions behind it: an evidence ledger, a model-layer vs content-layer split, the multi-hop search path, and which claims are unsupported model guesswork. User-run and read-only — it never alters the answer
- **geo-optimize** — Turns an `ai-answer-audit` into a prioritized plan to get a brand cited in AI answers (ChatGPT, Perplexity, Google AI Overviews): authority gap, four levers (get-cited / fix-open-territory / open-a-lane / upgrade-evidence), per-engine moves, and a Fast Wins / Roadmap / Backlog roadmap

### Product
- **product-rehearsal** — Imagines a proposed feature has already shipped, walks a real user or agent through finding and using it, surfaces where it will be bad, and revises the proposal before building. The behavior-level sibling of `implementation-rehearsal`

### DevOps
- **greenlight-pr** — Takes a PR, fixes CI failures, addresses review comments, and iterates until everything passes

### Productivity
- **interview-me** — Interviews you about a plan or design until it has all the context to build the right thing
- **noah-zender-it** — Selects relevant mental models from Noah Zender's idea library and explains how to apply them
- **plan-for-goal** — Turns conversation context into a single prompt for a coding agent's `/goal` orchestration loop — directional outcome, quality bar, and a self-verification path the loop can iterate against
- **plan-for-mega-goal** — Turns a multi-objective effort into a roadmap and a compact prompt for an autonomous goal loop
