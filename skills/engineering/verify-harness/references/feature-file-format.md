# Feature file format

One file per user-facing area in `features/`, named by area (`canvas-text.md`, `flows-runs.md`, `local-runtime-boundary.md`). An area is what a person or an agent thinks of as one thing, not a code module. The four H2s follow Lauren Tan's feature maps; the header line, the sub-feature ids and the recipe conventions are what made the map checkable and replayable.

## Anatomy

```markdown
# <Area name>

<One paragraph, user POV: what the area does, its rules in plain words, what persists, what never happens.>

Rules: AGENTS.md › "<the rule's opening words>", …; [decision doc](../relative/link.md) · Words people use: <comma-separated words reporters and users actually say> · Checks: `control-<app> checks <feature>`

## Sub-features

- `<id>` — <one sentence a person could check>.

## How to get to it (user POV)

- <every entry point: buttons by their accessible names, keys, menus, panels, URLs, the agent's CLI commands and API or MCP tools>.
- In this skill, <which driver commands reach it, and anything unusual about them>.

## Driving it with control-<app>

Preconditions:

- `control-<app> up --fixture <name>`.
- `control-<app> doctor` must report a build newer than the source.

- **<What this step proves, in plain words>** (`<sub-id>`, `<sub-id>`). Run `control-<app> …`, `control-<app> …` and `control-<app> expect …`. <One sentence on what the result means, if it isn't obvious.>

## Gotchas

- <What misleads: where a rule deliberately does not apply, timing, what the fixture hides, known bugs with their tracker reference, paths a session cannot reach and the tests that cover them.>
```

## Rules for each part

- **Paragraph.** Say what the area does and how it behaves, so a reader who never opens the code can judge a report against it. Keep rationale in the rules docs it links.
- **Rules.** Point at where each behaviour is decided (AGENTS.md rules quoted by their opening words, decision records, design docs). This is how a reviewer tells drift from regression.
- **Words people use.** Reporters say "the right panel" when the code says `inspector`, and "run just this step" when the API says `nodeId`. `route` matches reports against these words, and `issues <feature>` needs two of them to match.
- **Sub-features.** Stable, short ids (`move`, `snap`, `one-step`), each one sentence a person could check. Tests reference them (`@verifies feature#id`), and recipe steps name them, so renaming one is a map change.
- **How to get to it.** List every entry point, including keyboard shortcuts, context menus, the agent CLI and API, and embedded or desktop hosts. A proof through one convenient entry point is incomplete when the file lists others.
- **Recipe.**
  - State the proof layer, entry point and external stand-ins. The preconditions include `doctor` and a fixture; persistent recipes use `up`, while one-shot commands create fresh state themselves.
  - Each bullet is bold words saying what it proves, then its sub-features in parentheses, then commands in backticks.
  - `replay` runs the recipe commands in order. A persistent recipe uses one fresh session, with each bullet continuing from the previous state. Bounded commands may own independent fresh state; make that choice explicit.
  - Every observable result is an `expect`, an explicit assertion flag, or a named recipe assertion returning expected/actual values. A command that only acts proves nothing.
  - Arrange through the product (fixtures, the app's CLI or API), never by editing the page. The behaviour under test comes from a person's or agent's input.
  - Include refusal steps, with the refusal's words checked, and at least one persistence check (reload, or the saved file).
  - End the file with `expect console-clean`, or its equivalent for the surface.
- **Gotchas.** The fastest triage aid. Write down:
  - where a rule deliberately does not apply;
  - timing, such as coalescing windows and refetch intervals;
  - what the fixture or preview mode cannot show;
  - driver pitfalls (screen versus document pixels);
  - known bugs with their tracker reference, and the date observed;
  - paths a session cannot reach, with the tests that cover them.

## README index

`features/README.md` holds:

- **baseline preconditions:** what every session is (isolated, signed out, preview, stand-ins);
- **conventions:** targeting by role and name, `Mod` keys, how recipes chain, and every result being an `expect`;
- **proof and skip reporting:** what counts as evidence, and how to name an unreachable path;
- **the words people use** for the product's main nouns, with their code names;
- **the features,** grouped by surface, one line each;
- **not mapped yet:** what remains, and what is deliberately out of scope;
- **the full sweep.**

The CI check fails if the index and the folder disagree.

## A short example

```markdown
# Canvas drawing

A person adds shapes by drawing. The dock's **Rectangle tool** (R) draws a rectangle, and a click alone makes a default 160×120 one. A shape drawn over an artboard becomes its child, with frame-local coordinates, and one drawn on open canvas stays top-level. After one shape the tool returns to Select, and each shape is one undo step.

Rules: AGENTS.md › "Objects belong to the infinite canvas when dropped outside an artboard" · Words people use: draw, rectangle tool, shape, R, default size · Checks: `control-app checks canvas-drawing`

## Sub-features

- `draw-rectangle` — a drag over an artboard makes "Rectangle" inside it, at the dragged size, and selects it.
- `click-default` — a click without a drag makes a 160×120 shape at the click point.

## How to get to it (user POV)

- The tool dock's **Rectangle tool**, or the key R. Escape or V returns to Select.
- In this skill, `drag-xy <x,y> --by dx,dy` draws from a screen point; `press Shift+0` first makes screen pixels document pixels.

## Driving it with control-app

Preconditions:

- `control-app up --fixture two-artboards`.
- `control-app doctor` must report a build newer than the source.

- **Draw a rectangle into an artboard** (`draw-rectangle`). Run `control-app press Shift+0`, `control-app press r`, `control-app drag-xy 540,500 --by 100,60`, `control-app expect doc "Rectangle" --parent "Artboard A" --width 100 --height 60` and `control-app expect selected "Rectangle"`.

## Gotchas

- `drag-xy` works in screen pixels; at the fitted zoom a 100 px drag is about 63 document pixels.
```
