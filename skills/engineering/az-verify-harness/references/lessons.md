# Lessons, and the rule each one taught

From building a harness for a production design tool and mapping the whole product with it: 30 feature files, five agents writing into it, 36 driver gaps opened and all promoted, and 28 product findings reported. Each lesson is what happened, then the rule that followed.

## Setting it up

- **Hosts look for project skills in different folders.** Codex reads `.agents/skills/`, Claude Code `.claude/skills/`, Cursor `.cursor/skills/`. Keep one real folder and link it from the others.
- **Name the driver apart from the product.** The product already had `verify` and `test` commands. Name the driver `control-<app>` so neither humans nor agents confuse the two.
- **Generic browser CLIs can drop modifier keys.** Shift-click and ⌘-drag silently became plain clicks. Drive with a library that holds real keys for the whole gesture.
- **Isolate personal state, not just the workspace.** The app kept a device account and recent files in a home folder, so each session gets its own home and the app's offline or preview mode.
- **The driver already exists in the test helpers.** Extract from what the E2E tests do, and don't invent a second model of the app.
- **E2E suites quietly test stale bundles.** Check build freshness against every source file, refuse to prove against a stale bundle, and let `--allow-stale` through only for driver checks, marked "not product proof".
- **Name the driver's commands after what a person sees,** not internal routes (`open settings`, not `open ?page=settings`).

## The map

- **Reporters use other words than the code.** Put a "Words people use" line in every file, and match reports against it.
- **The fastest triage aid is where a rule deliberately does not apply.** Record it in Gotchas.
- **Chained recipes find what isolated tests miss.** One continuous session per file surfaced interaction bugs that unit tests never saw.
- **Completeness comes from registries, not memory.** Read the product's own lists of tools, commands and routes. Report while mapping, then assert.
- **Map the agent surfaces too.** A product's users include its agents: the CLI, the API or MCP tools, the security boundary, sign-in, and every promise in the onboarding prompt. On the pilot, a quarter of the MCP tools were unmapped until this pass.
- **Static checks catch renames, not changed meaning.** Keep the live sweep and the maintenance pass for meaning.
- **Annotating tests is cheap, and it makes `checks` and `coverage` real.** A mapper can add a comment line without touching test logic.

## Writing expectations

- **A failed expectation is not automatically a bug.** Three of the first failures were the recipe author's own wrong expectations. Check the rule before reporting.
- **"Nothing moved" has two meanings:** unmoved in the document, or still on screen. Offer both, measured against a `mark`.
- **Wait for end states, not fixed sleeps.** Every `expect` retries for a short while; `--now` checks once.
- **"Nothing happened" needs a clean slate and a pause.** Clear the record, act, wait, then check with `--now`, so a late event can't slip past an instant pass.
- **Silent passes are worse than failures.** An assertion flag that one mode ignored made a recipe "check" words nothing read. Every flag must apply in every mode, or be refused.
- **`ok` must mean passed.** A replay once answered `ok: true, passed: false`. A failed check answers `ok: false` and exits non-zero, in the driver as in the product.
- **Refusals are where agents get their next instruction.** Assert the refusal's words, not just its code. On the pilot, three misleading refusals were found this way.
- **Values between steps must not force scripts.** Give the driver `--capture` and a placeholder for later steps.
- **Substring name matching misleads both ways.** "X" matched "Radius px" (a false pass), while `--exact` failed on menu items named with their shortcut ("Duplicate ⌘D"). Match from the start of the name to a word boundary, and refuse an action when several differently named controls match.
- **Recipes prove behaviour; screenshots are for judging looks.** Keep a `shot` at each visual state, because no expectation says whether a surface reads well.

## Boundaries

- **Mock the tracker by default.** Capture submissions; `--live-feedback` opts in.
- **Stand in for the operating system, not the product.** A "Reveal in Finder" button really opened Finder, and a CLI sign-in really opened a browser tab on the host, because the stand-in covered only the server's PATH. Put recording stand-ins on the PATH of every process the session starts.
- **A path-rewriting convenience can write into the repository.** A relative `--workspace .` was turned into the checkout, and a command created files there. Rewrite only existing input files; never folders, and never write flags.
- **Play the host the product runs inside.** An app embedded in a chat host was covered by one long install test. A small bridge built from the product's own host SDK, with a strict content policy and recorded host calls, made it drivable by every command. Downgrade flags reached refusal paths nobody had seen.
- **Failure paths need a fault switch** at the operating-system or network boundary, undone by `down`. Never inject the symptom itself.
- **Act only on what is visible.** A mounted view behind another and closed tab panels hold hidden copies of controls. Filter to visible matches, and fall back into frames only when the page shows none.
- **Restarts and updates need a driver primitive.** Give the driver `runtime restart [--build <snapshot>]` and cheap build snapshots, so "a page left open while the server comes back on a new build" is a recipe step and not a hand-built harness. Code-splitting decides where a stale page can break, so start where code loads on demand. A stand-in fault that ends on the page's next load must end on a document request, not on the app's own route changes.

## Many agents

- **Per-checkout isolation is not enough.** Two agents in one checkout shared a default session, and one could have stopped the other's. Derive the default session from the host's conversation id, record the owner, and require `--force` to stop another's.
- **The skill spreads without being told.** A peer session found the skill through its link and followed the gaps rule on its own. Keep the description precise and promotion fast.
- **Another agent's edits make everyone's build stale.** Keep the freshness gate strict, and never rebuild with someone else's half-finished edits without asking.
- **A cold agent finds the driver's gaps fastest,** and a careful cold agent writes better recipes than the code's author. Let the map be written by agents who have to use it.
- **Parallel mappers need one driver owner.** Two mappers made eleven files in about an hour, and the main session promoted more than 25 capabilities mid-task. Only the owner edits the driver.
- **A session outlives driver edits.** Another agent's promotion changes the driver under a running session. Stamp the driver at `up`, and say on every answer when the session runs older code.
- **Commit the harness on its own, early.** Otherwise every product commit must be staged hunk by hunk to leave its files out.
- **Verify sub-agent findings before they reach the tracker.** Reproducing them showed one understated finding and one with no evidence. Search the tracker for duplicates before sending.

## The tracker

- **Route issues by at least two words.** One shared word ("canvas") matched everything.
- **Verification closes old issues, not just new bugs.** Note a reproduction, or "no longer reproduces on <commit>", on the issue.
- **Keep the owner key out of output.** Read it from the environment, report only whether it is available, and never print it.
