---
name: tour
description: Take a guided tour of a codebase subsystem — explore the code in parallel, then produce a self-contained HTML tour document that teaches the architecture so the reader doesn't need to read the code themselves. Optionally critiques the architecture for issues.
---

# Tour

Give the user a guided tour of a part of the codebase. Explore in parallel, synthesize a senior-engineer mental model, and write it out as a standalone HTML document the user can open in a browser and learn from without ever touching the source.

The HTML doc is the deliverable. The chat output is just a pointer to it.

Two modes:

1. **Tour** (default) — explore the codebase and produce the HTML tour
2. **Critique** — tour first, then spawn multiple models to independently identify architectural issues

## Tour Mode

### Step 1 — Understand the Question and Assess Complexity

Parse what the user is asking about. They might say:

- "Tour message virtualization" — a subsystem
- "How do we handle billing for on-demand usage?" — a feature flow
- "How is the auth service structured?" — an architectural overview
- "Walk me through what happens when a user sends a message" — a runtime trace

Identify the scope. If it's ambiguous, make your best guess and state your interpretation before exploring. Don't ask — explore and let the user redirect if you're off.

**Assess complexity to decide the approach:**

- **Simple** (a single module, a small utility, a narrow question like "how does function X work"): Skip explorer agents entirely. The explainer agent explores and writes the HTML in a single pass. Go directly to Step 2b.
- **Complex** (a subsystem spanning multiple files/services, a cross-cutting feature, a full architectural overview): Spawn parallel explorer agents first, then hand off to the explainer. Go to Step 2a.

When in doubt, lean toward the simple path — you can always spawn explorers if the explainer hits a wall.

### Step 2a — Explore (complex questions only)

Decompose the question into 2-4 parallel exploration angles. Each angle should cover a distinct slice of the subsystem so the explorers aren't duplicating work. For example, if the question is "tour message virtualization", you might split into:

- Explorer 1: the data model and state management
- Explorer 2: the rendering pipeline and DOM interaction
- Explorer 3: the scroll/measurement infrastructure

The right decomposition depends on the question — use your judgment. For narrow questions, 2 explorers is fine. For broad subsystems, use up to 4.

Spawn all explorers in a single message:

- `subagent_type`: `generalPurpose`
- `model`: `opus`
- `readonly`: `true`

Each explorer gets the same base prompt from `references/explorer-prompt.md`, plus a specific exploration angle telling it which slice to focus on. Each explorer should:
- Start broad: Glob for relevant directories, Grep for key types/interfaces/class names
- Follow the thread: once you find an entry point, trace the call chain — callers, callees, data flow, type definitions
- Read the actual code, don't guess from file names
- Stop when you can describe the full path from input to output (or from trigger to effect) without hand-waving any step
- Note things that are surprising, non-obvious, or that a newcomer would get wrong

Each explorer returns structured findings: the components it found, the flow it traced, the files it read, and anything non-obvious. Overlap between explorers is fine — the explainer will reconcile.

Then proceed to Step 3.

### Step 2b — Direct Tour (simple questions)

Spawn a single Task subagent that explores and writes the HTML tour in one pass:

- `subagent_type`: `generalPurpose`
- `model`: `opus`
- `readonly`: `false` (needs to write the HTML file)

This agent does its own exploration (Glob, Grep, Read) and writes the HTML directly. Read `references/explainer-prompt.md` for the communication style and HTML output format — the agent follows the same structure, it just doesn't have explorer findings as input.

Proceed to Step 4.

### Step 3 — Synthesize into HTML (complex questions only)

Once all explorers have returned, spawn a single Task subagent to synthesize their findings into the HTML tour:

- `subagent_type`: `generalPurpose`
- `model`: `opus`
- `readonly`: `false` (needs to write the HTML file)

The explainer gets all explorers' findings and writes the HTML document. Read `references/explainer-prompt.md` for the full prompt template and `references/html-tour-experience.md` for the visual/interaction spec. The explainer reconciles overlapping findings, resolves contradictions, and weaves the separate slices into one coherent tour.

### Step 4 — Present

Once the HTML is written, tell the user:
- The path to the HTML file
- A 1-2 sentence summary of what's covered

Suggest opening the file (`open <path>` on macOS). Don't paste the explanation contents into chat — the HTML is the deliverable, and pasting it would just duplicate the work in a worse format.

### HTML Output

The HTML tour goes into `./tours/tour-{topic-slug}.html` relative to the working directory (create the `tours/` directory if it doesn't exist). Use a slug derived from the question — e.g. `tour-message-virtualization.html`, `tour-billing-flow.html`. If the file already exists, overwrite it.

The HTML must be a single self-contained file: inline CSS, no external scripts or fonts, opens cleanly with a double-click. See `references/html-tour-experience.md` for the visual and structural spec.

The content covers (adapt to the question — not every section is needed every time):

**Overview** — What is this thing, what does it do, why does it exist. The reader should be able to read just this and know whether to keep going.

**Key Concepts** — The important types, services, or abstractions. Brief definitions, just the ones needed to understand the rest.

**How It Works** — The core. Walk through the flow: what triggers it, what happens step by step, where data goes, what the decision points are. Use prose, not pseudocode. Include diagrams (inline SVG or ASCII art) when the flow involves multiple components or staged transformations. Reference specific files and functions so the reader knows where to look — but the goal is that they don't *need* to look.

**Where Things Live** — A brief file/directory map. Just the ones someone would need to find to start working in this area. Each entry one line: path + one-line purpose.

**Gotchas** — Things that are non-obvious, surprising, or that would trip someone up. Historical context that explains why something looks weird. Known sharp edges. Skip if there's nothing worth calling out.

## Critique Mode

Triggered when the user asks for architectural issues, problems, or improvements — not just understanding.

### Step 1 — Tour First

Run the full tour flow above (Steps 1-4). You need to understand the architecture before you can critique it.

### Step 2 — Spawn Critics

After the HTML tour is written, spawn architectural critics. Launch all in a single message:

| Subagent | Model |
|----------|-------|
| Critic A | `opus` |
| Critic B | `sonnet` |
| Critic C | `opus` |

For each critic:
- `subagent_type`: `generalPurpose`
- `model`: the model from the table. These are starting suggestions — escalate to a higher reasoning tier of the same model family when the architecture warrants deeper analysis.
- `readonly`: `true`

Read `references/critic-prompt.md` for the prompt template. Each critic gets:
1. The explanation from Step 1 (so they don't waste time re-exploring)
2. The relevant file paths (so they can read the actual code)
3. The architectural critique rubric from `references/critique-rubric.md`

### Step 3 — Lead Judgment

You're a pragmatic lead, not an aggregator.

Categorize findings:
- **Act on** — Architectural problems worth fixing now
- **Consider** — Real concerns, but the cost/benefit is unclear
- **Noted** — Valid observations, low priority
- **Dismissed** — Wrong, missing context, or style preference

Append the critique verdict as a new section at the end of the HTML tour (don't overwrite the tour — the explanation should still stand on its own for someone who just wants to understand the system). Then summarize the verdict in chat with a pointer back to the HTML.
