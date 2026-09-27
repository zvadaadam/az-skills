# Checking the map like code

A map that names commands the driver lacks, sub-features nothing points at, or tests that point at nothing teaches the next agent wrong steps. Run these checks in the normal unit-test job; they read files only and take well under a second.

## The parser

The driver owns a small parser, shared by the CLI (`features`, `checks`, `coverage`, `route`, `replay`) and by the test. It reads each `features/*.md` into:

- `id` (the file name), `title`, the paragraph;
- the header line's `Rules`, `Words people use` and `Checks`;
- sub-features: `- \`<id>\` — <sentence>` lines under `## Sub-features`;
- preconditions: unlabeled bullets under `Preconditions:`, each with its inline `control-<app> …` commands;
- steps: bold-labeled bullets, with the sub-feature ids in parentheses and the inline commands in order.

A `problemsOf(feature, commandNames)` function returns human-readable problems:

- a section is missing or in the wrong order;
- a step names an unknown sub-feature;
- a recipe uses a command the driver's table does not have;
- a sub-feature no step and no test covers (report this; don't fail yet).

## Annotations

A test that pins a sub-feature carries one comment line directly above it:

```js
// @verifies canvas-drawing#draw-rectangle
test("a drag with the rectangle tool inside an artboard makes a child", () => { … });
```

- Several lines may stack above one test. Keep them within a few lines of the `test(` call, because the parser looks back only that far.
- Annotations are comments only; adding them changes no behaviour, so a mapper can add them without touching test logic.
- `checks <feature>` lists the annotated tests, fastest first (unit before browser before install), with the command that runs each.

## The tests

```js
test("every feature file has its paragraph, words, four sections and recipes that use real driver commands", () => {
  const problems = loadMap().flatMap((feature) => problemsOf(feature, COMMAND_NAMES));
  assert.deepEqual(problems, []);
  for (const feature of loadMap()) assert.ok(feature.preconditions.some((step) => step.commands.some((command) => command[0] === "up")));
});

test("every @verifies annotation names a mapped feature and sub-feature", () => { /* resolve each; none dangling; each sits above a test( */ });

test("the index lists every feature file, and every listed file exists", () => { /* README links === folder */ });

test("the skill is found by every host: one folder, linked from each host's skills folder", () => { /* realpath checks, frontmatter name */ });

test("fixtures the recipes start from exist", () => { /* every `up --fixture X` has fixtures/X.json */ });

test("every entry point is on the map: each UI tool, API or MCP tool and CLI command", () => {
  const text = featureFiles().map(read).join("\n");
  const mcpTools = namesFrom("src/mcp", /defineTool\(\{\s*name:\s*"([a-z_]+)"/g);
  const uiTools = labelsFrom("src/ui/tool-catalog.ts").map((label) => `${label} tool`);
  const cliCommands = commandsFrom("src/cli/usage.ts", /^\s*<app> ([a-z][a-z-]*)/gm);
  assert.ok(mcpTools.size > 0 && uiTools.length > 0 && cliCommands.length > 0, "the sources still name their entry points the way this test reads them");
  const unmapped = [...missing(mcpTools, text), ...missing(uiTools, text), ...cliCommands.filter((name) => !new RegExp(`(?:<app>|doc) ${name}\\b`).test(text))];
  assert.deepEqual(unmapped, []);
});
```

While the map is being built, the completeness test reports its count with `t.diagnostic(...)`. Turn it into the assertion as soon as it reaches zero, so a new tool, command or UI control cannot ship unmapped. The sanity assertion on the registry sizes keeps the test from passing vacuously after a refactor renames the source it reads.

## What the checks cannot catch

Static checks catch renames and missing pieces, not changed meaning. A recipe step can pass while testing the wrong thing, and a gotcha can go stale. The live `sweep` and the maintenance pass (source readers per area, then one live run per area) cover meaning. Run them before releases.
