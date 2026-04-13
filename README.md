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
- **eng-explore** — Explores a problem from the perspective of 5 legendary engineers (Carmack, Hickey, Metz, Torvalds, Beck), then builds consensus
- **code-simplifier** — Reviews code for clarity and maintainability, then cleans it up
- **deslop** — Detects and removes AI-generated code slop (unnecessary abstractions, over-engineering, verbose patterns)

### Design
- **design-explore** — Explores a design challenge from the perspective of 5 legendary designers (Rams, Ive, Vignelli, Fukasawa, Jongerius)
- **name-explore** — Generates naming ideas using multiple creative approaches (linguistic analysis, cultural references, wordplay)

### DevOps
- **greenlight** — Takes a PR, fixes CI failures, addresses review comments, and iterates until everything passes

### Productivity
- **ai-journal** — Observes how you work with AI and documents patterns, habits, and improvement ideas
