<p align="center">
  <h1 align="center">az-skills</h1>
  <p align="center">
    A curated set of skills I use with my agents. Feel free to grab what's useful.
  </p>
</p>

<p align="center">
  <a href="#install">Install</a> &nbsp;&middot;&nbsp;
  <a href="#whats-inside">Skills</a> &nbsp;&middot;&nbsp;
  <a href="#update">Update</a>
</p>

---

Each skill is a small package of instructions and code that gives an agent a new ability — like fixing failing CI pipelines, exploring problems from multiple angles, or cleaning up messy code. This repo is updated as I build and refine new skills.

## Install

```bash
git clone https://github.com/zvadaadam/az-skills.git
cd az-skills
./scripts/install.sh
```

This connects the skills to your agent. You only need to do this once.

## Update

Pull the latest and you're done — new and improved skills load automatically:

```bash
cd az-skills
git pull
```

## Uninstall

```bash
./scripts/uninstall.sh
```

---

## What's inside

### Engineering
- **call-claude-fable** — Calls Claude Code Fable as a premium CLI advisor for hard judgment, architecture, and frontend/design critique, with resumable sessions and saved output artifacts
- **call-codex-gpt55** — Calls Codex CLI GPT-5.5 as a fast CLI worker for clean code implementation, repo exploration, tests, and bounded engineering tasks
- **code-review** — Multi-lens code review with 3 parallel sub-agents (correctness, security, design) that validates and reports only high-signal findings
- **devs-roundtable** — 5 legendary engineers (Carmack, Hickey, Metz, Torvalds, Beck) debate your problem in parallel, then build consensus
- **code-simplifier** — Reviews code for clarity and maintainability, then cleans it up
- **deslop** — Detects and removes AI-generated code slop (unnecessary abstractions, over-engineering, verbose patterns)
- **pre-factor** — Auto-fires before a feature or non-trivial change: maps the code the change will land in and surfaces the prep refactors that make the change easy (reshape the seam, add a safety net, kill duplication) — each one traced to the upcoming change, landed as its own commit first. The before-bookend to `complexity-check`
- **skill-feedback** — Shared telemetry helper used by each skill; submits concise feedback plus skill read/activation events directly to PostHog, with automatic hooks in Claude Code and anonymous installation IDs for active-install counts

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
- **plan-for-goal** — Turns conversation context into a single prompt for a coding agent's `/goal` orchestration loop — directional outcome, quality bar, and a self-verification path the loop can iterate against
- **ai-journal** — Observes how you work with AI and documents patterns, habits, and improvement ideas
