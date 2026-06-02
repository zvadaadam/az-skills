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
- **code-review** — Multi-lens code review with 3 parallel sub-agents (correctness, security, design) that validates and reports only high-signal findings
- **devs-roundtable** — 5 legendary engineers (Carmack, Hickey, Metz, Torvalds, Beck) debate your problem in parallel, then build consensus
- **code-simplifier** — Reviews code for clarity and maintainability, then cleans it up
- **deslop** — Detects and removes AI-generated code slop (unnecessary abstractions, over-engineering, verbose patterns)
- **skill-feedback** — Shared telemetry helper used by each skill; submits concise feedback plus skill lifecycle events directly to PostHog, with automatic hooks in Claude Code

### Design
- **design-roundtable** — 5 legendary designers (Rams, Ive, Vignelli, Fukasawa, Jongerius) debate your brief in parallel, then build consensus

### Branding
- **brand-name-explore** — Generates product/company names using multiple creative personas (Lexicon methodology, poet, linguist, culture hacker, futurist)

### DevOps
- **greenlight-pr** — Takes a PR, fixes CI failures, addresses review comments, and iterates until everything passes

### Productivity
- **interview-me** — Interviews you about a plan or design until it has all the context to build the right thing
- **plan-for-goal** — Turns conversation context into a single prompt for a coding agent's `/goal` orchestration loop — directional outcome, quality bar, and a self-verification path the loop can iterate against
- **ai-journal** — Observes how you work with AI and documents patterns, habits, and improvement ideas
