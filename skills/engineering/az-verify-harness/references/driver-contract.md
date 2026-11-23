# The `control-<app>` driver contract

What a driver needs so that agents use it instead of writing their own scripts. Build it by extracting the repository's existing test helpers, then grow it through the gaps loop.

Keep implementation in the repository's existing CLI or development tooling (for example `apps/cli`), with executable fixtures in its test directories. The agent skill holds navigation and recipes and links to the driver; it need not contain application code. Use existing browser/device controls instead of building another automation engine.

## Shape

- **A CLI, with a daemon only for persistent sessions.** Start with bounded commands that create isolated state, exercise the real entry point, retain evidence and clean up. If recipes need an open browser, PTY or runtime across commands, add a session daemon: `up` starts it, subsequent commands send short requests, and `down` stops it. Answers are JSON in either form. Do not implement controls unused by a selected recipe.
- **One table of commands** (name, where it runs, usage, one-line summary). `--help`, `replay` and the map's CI check all read it, so a recipe can never name a command that does not exist.
- **Sessions.** The default session name comes from the agent host's conversation id (for example `CLAUDE_CODE_SESSION_ID` or `CODEX_SESSION_ID`), so two agents in one checkout never share or stop each other's session. `--session <name>` picks another. A session records its owner, and `down` refuses another's without `--force`.
- **An idle stop.** A session left behind stops itself after a while, killing only the processes it started, never anything by name.

## Session isolation (`up`)

- A temporary workspace and a temporary home or profile, so it never touches the person's account, keys or recent files.
- The app started through its own documented start command, not an internal entry point.
- Offline or preview modes on, so nothing costs money. A flag such as `--live-media` opts in deliberately.
- A fixture applied through the app's own API, from a file in `fixtures/`. Fixtures are small, named and readable.
- A browser at a fixed viewport, with reduced motion so states settle at once (`--motion` keeps animations), headless unless `--headed`.

## Doctor

A read-only health check, run first and after anything surprising:

- **Build freshness.** A compiled bundle must identify the source it contains; refuse a stale bundle. `--allow-stale` is for driver checks, marked "not product proof". Direct source execution records a digest of the relevant source and fixtures instead; it needs no synthetic build step.
- The session's processes are alive, and its home is isolated.
- Page errors so far.
- Whether the tracker's owner key is available, without ever printing it.
- Open gaps.

It exits non-zero when unhealthy.

## Acting

- **By role and accessible name:** `click --role button --name "Save"`, `press Mod+S` (Mod is ⌘ on macOS and Ctrl elsewhere), `fill`, `type`, `hover`.
  - A name matches from the start of the control's name to a word boundary: "Duplicate" finds "Duplicate ⌘D", and "X" never finds "Radius px". `--exact` means the whole name.
  - An action refuses when several differently named controls match, listing them. Several with the same name use the first and say so.
  - Only visible matches count: hidden copies of a control (a mounted view behind another, a closed tab panel) are skipped. When the page shows none, look inside embedded frames.
- **Domain objects by name,** not coordinates: `click-node "<layer>"` finds a point where the object is visible and not under floating chrome. Names in a fixture are stable; ids are not, so `@Name` in arguments stands for an id.
- **Gestures as a person makes them:** drags with modifier keys held throughout, and resize handles. `--hold` stops before letting go, so you can look mid-gesture (guides, insertion markers, cursors); `release [--cancel]` ends it.
- **Scopes.** When a control repeats on every card or row, `--card "<name>"` finds it inside one container, hovering it first as a person must.
- **Inputs from outside:** `--choose-files` answers a file picker, `clipboard set --file` then a real paste, and fixture pages served on loopback for anything that fetches a URL.
- **Navigation:** open views by name, plus `back`, `forward` and `reload [--stay]`, recording any "Leave site?" prompt.

## Reading, twice

- **As a person sees it:** the accessibility tree (`snapshot`), domain panels (rows, selection chrome), and where keyboard focus is (`focus`).
- **As the product saved it:** a pass-through to the app's own CLI or API (`doc <args>`) and the files on disk (`files`).
- **`expect` for every observable result,** retried until it holds (2.5 s by default, `--timeout`, `--now`). On failure it answers `expected` and `actual`. Families worth having:
  - presence and state: visible, hidden, enabled, disabled, checked, pressed, current, focused;
  - values: an input's or a select's shown value, a style, an attribute, the text, a count, the URL;
  - order: of domain children, and of any list of controls by accessible name;
  - the saved document: a record's parent, type, children and geometry;
  - position: moved or unmoved in the document, still or shifted on screen, both since a `mark`;
  - things that left the page: a download (with its pixel size), the clipboard, an opener request, a dialog, a popup, an outbound submission;
  - perf: frame times and long tasks between `perf start` and `perf stop`;
  - `console-clean`.
- **On API answers:** `--contains` and `--lacks` state what must and must not be there. `--expect-error <code>` expects a refusal, and then `--contains` checks its words, because a refusal's words are an agent's next instruction. `--capture name=<regex>` keeps a value that a later step's `@{capture:name}` states.

## Boundaries: stand-ins that record

Mock only at an external boundary, and make each stand-in record what the app asked for:

- the tracker or feedback endpoint: submissions captured (`outbox`) unless `--live-feedback`;
- the system opener (`open`, `xdg-open`): a script first on the PATH of both the app's server and its CLI, so Reveal and sign-in links are recorded (`opened`) and never opened on the real machine;
- downloads: saved into the evidence with their type and size (`downloads`);
- dialogs: recorded and answered (`dialogs`);
- the clipboard: granted to the session browser only;
- pages the app fetches: fixture pages on loopback;
- the host an embedded app runs in: a small host page that frames the app under a strict content policy and bridges its host API. It records tool calls, context updates, display-mode requests, links and downloads (`host`). Flags make it less capable (no fullscreen, no link support, refuses display changes, declines downloads), so the refusal paths are reachable.

## Restarts and builds

- `runtime stop|start|restart` stops and starts the session's own server under the open page, on the same port and data, as an update or a crash would.
- `build --snapshot <label>` keeps the current build (for a single-file product, a copy of that file), and `up --build <label>` / `runtime restart --build <label>` run it. Keep the old build, change the source, rebuild, then restart the open page's server onto the new one.
- A `stale-build` fault stands in for another build: code the page has not loaded yet is refused until its next document load. Pair it with `expect navigated` (the page loaded again) and `expect network` (what was refused).
- Stamp the driver's code at `up`, and note on every answer when a session runs an older driver.

## Faults

Failure paths need their precondition, applied at the operating-system or network boundary and never by editing the app:

- a read-only project folder;
- failing font or asset loads;
- slow API answers, for loading placeholders;
- a failing API route, for error and retry states.

Each fault turns off with `off`, and `down` undoes it.

## Safe arguments

- Rewrite a relative path to the checkout only when it names an existing input file. Never rewrite a folder, and never the value of a write flag (`--out`, `--dir`, `--workspace`), or a command will write into the repository.
- `--bare` runs the app's CLI in an empty folder with its own home and no running server, as a fresh install would. Use it for "works before anything starts" claims.

## Evidence and proof

- `shot`, `record start|stop` (video), and `trace start|stop` (a DOM trace).
- `proof <feature> --note "…"` copies the evidence, command log, errors, captured submissions and source/build stamp to `.context/proof/<feature>/<time>/`. One-shot commands may save this bundle automatically. It survives cleanup, including failed runs.
- Label the exercised layer and real entry point, plus stand-ins and unverified paths. Record expected and actual values for assertions. A passing supported recipe must not imply that an unmapped UI or live-provider path passed.

## The map commands

- `features`: the areas, their sub-features, and the words people use.
- `route "<words>"`: which files a report is probably about.
- `checks <feature>[#sub]`: tests annotated for it, fastest first, with the command that runs each.
- `coverage`: per sub-feature, whether a test, a recipe, both or neither covers it.
- `replay <feature>`: runs the file's recipe in a fresh session of its own and keeps a proof. It answers `ok: false` and exits non-zero when any step fails.
- `sweep [--continue]`: replays every file and summarizes the failures.
- `issues <feature> | --query "<words>" | <id> | --verify`, and `report … [--send]`: the tracker (see SKILL.md).

## The gaps loop

- `script <file.mjs> --why "<what the driver could not do>" [--feature F] [--arg k=v]` runs `export default async ({ page, context, cli, url, args, evidence }) => result` inside the session and appends it to `gaps.jsonl`, one ledger shared by every session.
- `gaps` lists open gaps. `gaps close <n> --promoted "<command>"` closes one; `report <n> [--send]` files one.
- `down` names any gap still open.
