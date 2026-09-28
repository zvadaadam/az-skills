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
  <a href="https://skills.sh/zvadaadam/az-skills">skills.sh</a>
</p>

---

Each skill is a small package of instructions and code that gives an agent a new ability — like fixing failing CI pipelines, exploring problems from multiple angles, or cleaning up messy code. This repo is updated as I build and refine new skills.

## Install

Use [Vercel's Skills CLI](https://github.com/vercel-labs/skills) to select skills and agents:

```bash
npx skills add zvadaadam/az-skills
```

Install the whole collection globally for Claude Code and Codex:

```bash
npx skills add zvadaadam/az-skills --skill '*' --agent claude-code codex --global
```

Or list the available skills and install just one:

```bash
npx skills add zvadaadam/az-skills --list
npx skills add zvadaadam/az-skills --skill deslop
```

Each skill includes a standalone Hivenet feedback command. The optional `az-skills-feedback` skill adds detailed reporting guidance; it is included when you install the whole collection.

The Skills CLI installs from this public GitHub repository. The `skills/<category>/<name>/SKILL.md` layout is discovered automatically; no npm package or registry upload is needed. New installs use the default branch, so repository changes become available after they reach `master`. The [skills.sh listing](https://skills.sh/zvadaadam/az-skills) is driven by installations, as described in [Vercel's FAQ](https://skills.sh/docs/faq).

The Skills CLI has its own install-count telemetry. To disable it, prefix commands with `DISABLE_TELEMETRY=1`; see the [CLI documentation](https://skills.sh/docs/cli). Hivenet commands in this repo disable automatic context collection separately.

### Install from a local checkout

For development, link skills directly to a clone so local edits are available immediately:

```bash
git clone https://github.com/zvadaadam/az-skills.git
cd az-skills
./scripts/install.sh
```

This links the skills into `~/.claude/skills`, `~/.agents/skills`, and `~/.codex/skills` and installs this repo's Git hooks for updates.

## Update

For Skills CLI installs:

```bash
npx skills update
```

For a linked local checkout, pull the latest:

```bash
cd az-skills
git pull
```

### Moving from the old installer

The local install and uninstall scripts remove the retired feedback hook, this checkout's old `skill-feedback` links, and the local installation ID. The Skills CLI copies individual skill directories and does not run this cleanup. Before switching from an earlier local install, run the cleanup from the updated checkout:

```bash
python3 scripts/remove_legacy_feedback.py
```

If you previously installed the retired `skill-feedback` package through the Skills CLI, remove it as well:

```bash
npx skills remove skill-feedback --global
```

Omit `--global` if that old package was installed in a project. Then install the current skills with `npx skills add` as above.

## Uninstall

For Skills CLI installs, name the skill to remove:

```bash
npx skills remove deslop --global
```

Omit `--global` for project installs. For a linked local checkout:

```bash
./scripts/uninstall.sh
```

## Feedback

Report broken, confusing, outdated, or notably good behavior through [Hivenet](https://hivenet.app/p/az-skills):

```sh
DO_NOT_TRACK=1 npx --yes hivenet@latest --to az-skills --dsn https://hv_pub_9f0d072c2ba5840245d83437@hivenet.app/az-skills --category skill --subject "<skill-name>" "<specific, actionable feedback>"
```

The [`az-skills-feedback` skill](skills/engineering/az-skills-feedback/SKILL.md) covers structured failed-task reports for the team's eval corpus, attachments, and follow-up questions and replies. The bundled publishable DSN fixes the destination to az-skills; no user-provided key is needed. These examples disable automatic context collection. Keep reports specific and never include secrets or private data.

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
- **tour** — Explores a codebase subsystem and produces a self-contained HTML tour

### Design
- **design-roundtable** — 5 legendary designers (Rams, Ive, Vignelli, Fukasawa, Jongerius) debate your brief in parallel, then build consensus

### Marketing
- **brand-name-explore** — Generates product/company names using multiple creative personas (Lexicon methodology, poet, linguist, culture hacker, futurist)
- **ai-answer-audit** — Reverse-engineers an AI "best X" answer back to the searches, sources, and assumptions behind it: an evidence ledger, a model-layer vs content-layer split, the multi-hop search path, and which claims are unsupported model guesswork. User-run and read-only — it never alters the answer
- **geo-optimize** — Turns an `ai-answer-audit` into a prioritized plan to get a brand cited in AI answers (ChatGPT, Perplexity, Google AI Overviews): authority gap, four levers (get-cited / fix-open-territory / open-a-lane / upgrade-evidence), per-engine moves, and a Fast Wins / Roadmap / Backlog roadmap

### DevOps
- **greenlight-pr** — Takes a PR, fixes CI failures, addresses review comments, and iterates until everything passes

### Productivity
- **interview-me** — Interviews you about a plan or design until it has all the context to build the right thing
- **noah-zender-it** — Selects relevant mental models from Noah Zender's idea library and explains how to apply them
- **plan-for-goal** — Turns conversation context into a single prompt for a coding agent's `/goal` orchestration loop — directional outcome, quality bar, and a self-verification path the loop can iterate against
- **plan-for-mega-goal** — Turns a multi-objective effort into a roadmap and a compact prompt for an autonomous goal loop
