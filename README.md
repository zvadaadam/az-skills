<p align="center">
  <h1 align="center">az-skills</h1>
  <p align="center">
    A curated set of skills I use with my agents. Feel free to grab what's useful.
  </p>
</p>

<p align="center">
  <a href="#whats-inside">Skills</a> &nbsp;&middot;&nbsp;
  <a href="#install">Install</a> &nbsp;&middot;&nbsp;
  <a href="#update">Update</a> &nbsp;&middot;&nbsp;
  <a href="#feedback">Feedback</a> &nbsp;&middot;&nbsp;
  <a href="https://skills.sh/zvadaadam/az-skills">Browse on skills.sh</a>
</p>

---

Each skill is a small package of instructions and code that gives an agent a new ability, like getting a PR green, rehearsing a change before writing it, or exploring a problem from several angles. They work in Claude Code and Codex. Every name starts with `az-`, so they sit together in a skill list and never collide with built-in commands or other collections.

## Install

From your project, run the skills.sh CLI with Node.js 22.20 or later.

```bash
npx skills add zvadaadam/az-skills
```

Choose the skills and agents you use. Add `--skill az-deslop` to pick one by name or `--global` to install across projects.

## What's inside

### Engineering

| Skill | What it does |
|---|---|
| `az-greenlight-pr` | Drives a PR to merge-ready: fixes CI, verifies and answers every review comment, and waits for re-review until it is green. |
| `az-code-review` | Reviews a branch or PR with three parallel reviewers (correctness, security, design) and reports only verified findings. |
| `az-deslop` | Strips AI slop from the code a branch added and simplifies it without changing behavior. |
| `az-complexity-check` | Audits a finished change for unneeded additions, droppable assumptions, spread, and duplication. Reports; does not edit. |
| `az-implementation-rehearsal` | Walks through a proposed change without writing it, finds the regressions and the prep refactor that makes it easy, and revises the plan. |
| `az-devs-roundtable` | Five legendary engineers (Carmack, Hickey, Metz, Torvalds, Beck) debate your problem in parallel, then converge. |
| `az-tour` | Explores a subsystem and writes a self-contained HTML tour of it, optionally with an architecture critique. |
| `az-setup-agent-workflow` | Sets a repository up for agent work: a reliable dev loop, concise AGENTS.md guidance, task skills, and one demonstrated change-and-verify loop. |
| `az-verify-harness` | Gives a repo a verification harness agents actually use: a `control-<app>` driver and a user-POV feature map checked in CI. Based on Lauren Tan's ([@poteto](https://github.com/poteto)) verification skills in Cursor's pstack. |
| `az-call-advisor` | Calls the premium Fable advisor through the Claude Code CLI for hard judgment and design critique, with resumable sessions. |
| `az-call-worker` | Calls a fast Codex worker through the Codex CLI for bounded implementation, tests, and repo exploration. |
| `az-master-coordinator` | Coordinates several Conductor workspaces from one session: a board of everything in flight, landing order from measured file overlap, a go or no-go on each frozen revision, and recovery of stalled handoffs. Starts only when you ask for it, never on its own. |
| `az-workspace-coordinator` | Leads one change in one Conductor workspace through builder, reviewer, and checker sessions, with one writer per hunk and one evidence-backed handoff. Starts only when you or a master coordinator assign it. |
| `az-skills-feedback` | The full guide for sending feedback, failed-task reports, and follow-ups to the az-skills team. |

### Product & Design

| Skill | What it does |
|---|---|
| `az-product-rehearsal` | Imagines a proposed feature has already shipped, walks a real user or agent through it, finds where it will be bad, and revises the proposal before anyone builds it. |
| `az-design-roundtable` | Five legendary designers (Rams, Ive, Vignelli, Fukasawa, Jongerius) debate your brief in parallel, then converge. |

### Marketing

| Skill | What it does |
|---|---|
| `az-brand-name-explore` | Generates product and company names with five naming personas, based on David Placek's Lexicon method. |
| `az-ai-answer-audit` | Traces an AI "best X" answer back to the searches, sources, and assumptions behind it. User-run and read-only. |
| `az-geo-optimize` | Turns an `az-ai-answer-audit` into a prioritized plan to get a brand cited in AI answers. |

### Productivity

| Skill | What it does |
|---|---|
| `az-interview-me` | Interviews you about a plan, one question at a time, until the agent has the context to build the right thing. |
| `az-noah-zender-it` | Ranks mental models from Noah Zender's idea library by leverage for your situation. |

Some skills build on others. Each works alone, but installs better in pairs:

- `az-product-rehearsal` decides what a feature should do; `az-implementation-rehearsal` rehearses how the code would change.
- `az-geo-optimize` starts from an `az-ai-answer-audit` report.
- `az-setup-agent-workflow` hands verification work to `az-verify-harness`.
- `az-call-advisor` and `az-call-worker` are the judgment and implementation halves of one setup.
- `az-greenlight-pr` answers `az-code-review` comments like any other reviewer's.
- `az-master-coordinator` orders the work that `az-workspace-coordinator` leads in each workspace; a lead hands its PR to `az-greenlight-pr`.

Requirements: `az-greenlight-pr` and `az-code-review` need an authenticated [GitHub CLI](https://cli.github.com); bundled scripts need `python3`; `az-call-advisor` needs the Claude Code CLI and `az-call-worker` the Codex CLI; the coordinators need Conductor.

## Update

```bash
npx skills update
```

## Uninstall

Remove a skill by name. Add `--global` if you installed it globally.

```bash
npx skills remove az-deslop
```

<details>
<summary>Renamed skills (November 2026)</summary>

Most skills gained the `az-` prefix. For example, `deslop` is now `az-deslop`. `plan-for-goal`, `plan-for-mega-goal`, and `repo-history-book` were retired. The prep-refactor pass moved from `pre-factor` to `az-implementation-rehearsal`, and `code-simplifier` merged into `az-deslop`.

Install the skills you want under their new names. Run `npx skills list` in the project or `npx skills list --global` for a global install. Remove an old name only if its listed source is `zvadaadam/az-skills`. For example, if that source owns the old project copy, run `npx skills remove deslop`. Add `--global` for a global copy.

</details>

<details>
<summary>Switching from the old installer</summary>

1. In the original clone, if `git config --local --get core.hooksPath` prints `.githooks`, run `git config --local --unset-all core.hooksPath '^\.githooks$'`. This prevents a later checkout or pull from reinstalling the links.
2. Run `./scripts/uninstall.sh` there if it still exists. In `~/.claude/skills`, `~/.agents/skills`, and `~/.codex/skills`, unlink any remaining symlinks that point into that clone. For each link you remove manually, restore the newest matching `<name>.backup.<timestamp>` directory to `<name>` if present.
3. If you used the retired `skill-feedback` package, remove its `skill-feedback/scripts/skill-event.py` handler from `PostToolUse` in `~/.claude/settings.json` and delete `~/.az-skills/installation-id` if present. For a CLI-installed copy, check its source as described above before removing it in its original scope.

Then run the install command above. Add `--global` to match the old installer's scope.

</details>

## Feedback

Report broken, confusing, outdated, or notably good behavior through [Hivenet](https://hivenet.app/p/az-skills):

```sh
DO_NOT_TRACK=1 npx --yes hivenet@latest --to az-skills --dsn https://hv_pub_9f0d072c2ba5840245d83437@hivenet.app/az-skills --category skill --subject "<skill-name>" "<specific, actionable feedback>"
```

The [`az-skills-feedback` skill](skills/engineering/az-skills-feedback/SKILL.md) covers structured failed-task reports for the team's eval corpus, attachments, and follow-up questions and replies. The bundled publishable DSN fixes the destination to az-skills; no user-provided key is needed. These examples disable automatic context collection. Keep reports specific and never include secrets or private data.

To opt out of the Skills CLI's install counts, prefix its commands with `DISABLE_TELEMETRY=1`. [CLI telemetry settings](https://skills.sh/docs/cli)
