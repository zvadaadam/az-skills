---
name: complexity-check
description: After making changes, audit the diff through four lenses — Additions, Premises, Spread, Duplicates — to catch overbuilt changes and surface simplification opportunities the change itself can't see. Use after implementing a feature, refactor, or bug fix, before committing. Apply only the lenses that have signal to find for your diff; mark the rest N/A.
hooks:
  PostToolUse:
    - matcher: "*"
      hooks:
        - type: command
          command: 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill complexity-check --action started --agent-harness claude-code --quiet'
          timeout: 5
  Stop:
    - hooks:
        - type: command
          command: 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill complexity-check --action completed --agent-harness claude-code --quiet'
          timeout: 5
---

# Complexity Check

You just made changes. Before you ship them, run four independent lenses on the diff. Each asks a different question:

1. **Additions** — was each new thing necessary?
2. **Premises** — could any assumption be dropped to delete code?
3. **Spread** — is the concept localized?
4. **Duplicates** — does something like this already exist?

The lenses are independent — findings from one rarely overlap with findings from another. Apply only the lenses that have signal to find for your diff; mark the rest **N/A** in the output with a one-line reason, so the reader can see the lens was considered.

## When to run this

- After implementing a feature or bug fix, before committing
- After a refactor that touched more files than expected
- When something felt harder to write than it should have been
- When you were tempted to add "for future flexibility"

Skip the whole skill for: tiny fixes (typos, renames, dep bumps), pure deletions, mechanical refactors.

## Scoping

Always work from the diff against the base branch.

```bash
BASE=$(git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null)
git diff $BASE...HEAD                  # committed changes
git diff HEAD                          # uncommitted WIP
git diff --name-only $BASE...HEAD      # changed files
```

Read each changed file **in full** — not just the diff. The diff hides the surrounding context that decides whether a piece of complexity is justified.

## Additions — was each new thing necessary?

*Skip if the diff is pure deletions or renames.*

For each meaningful chunk of the diff, ask:

- **New abstraction** (function, class, type, hook, interface, module): is it used in more than one place? If not, why does it exist?
- **New branch** (if/else, switch case, ternary): does the alternative path ever fire in practice? Could the caller's input have been narrowed instead?
- **New parameter / option / config flag**: is it set to a non-default value anywhere today? If not, delete it.
- **New error handling** (try/catch, null guard, fallback): does the error actually happen, or is this defending against an impossible state in trusted internal code?
- **New file or module**: could this code have lived in an existing file that already owns the concept?
- **New concept the reader must learn** (a name, a pattern, a layer): is the concept earning its cognitive cost?
- **Net line count**: lines added minus lines removed — is the project meaningfully better, or just bigger?

For each finding, name **the specific complexity** and **what you'd cut**.

**One-paragraph defense rule:** if defending a piece of complexity needs more than one paragraph, flag it. Short defenses mean it's earning its place; long defenses mean you're rationalizing.

## Premises — could any assumption be dropped to delete code?

*Skip if the touched files were created in this same PR — there are no established premises to challenge yet.*

Walk the touched code (the files and their immediate neighbors). List the assumptions it relies on. Look for:

- **Multiplicity**: "an X can have many Y" — is it ever more than one in practice?
- **Configurability**: "X is configurable per Y" — does anyone configure it to something other than the default?
- **Backward compat**: "we still support format/version Z" — does anyone still use it?
- **Feature flags**: "this is gated on flag F" — is F still serving a purpose, or is it permanently on/off?
- **Modes / variants**: "the system handles case A and case B" — does case B ever happen?
- **Optionality**: "field F can be null" — does it ever arrive null from any real caller?
- **Generality**: "this works for any type T" — is T ever anything other than the one concrete case?
- **Async-ness**: "this is async / queued / retried" — does it ever actually need to be?

For each assumption, ask: **if we asserted this is false (or always true), what could we delete?** Estimate the deletion: a few lines, a function, a file, a subsystem.

Findings here are higher-leverage than the other lenses — they don't just trim the diff, they trim the codebase. But they're claims, not facts: each one needs verification (grep, git log, ask the team) before action.

## Spread — is the concept localized?

*Skip if the diff touches ≤2 files.*

Look at the *shape* of the change across the codebase. One conceptual change that requires edits in many places usually means the abstraction is leaking — the diff is the symptom; the architecture is the bug.

Ask:

- **Is one concept being threaded through many files?** "Add notification read-state" requiring edits to schema + types + service + 3 components + settings + tests is a sign read-state isn't owned anywhere — it's smeared across the system.
- **Is the same logic repeated at multiple call sites?** Three components independently null-checking `readAt` and rendering an "unread" badge — three places to keep in sync.
- **Is the change list-shaped?** "Add this field to A, B, C, D, E…" patterns mean the *next* change like this will require another N-way edit. Table-driven or registry-based designs collapse N-way changes into 1-way changes.

For each finding, name **the concept** and **where it's smeared**. The action is usually "extract a registry / hook / table" so the next change is one-touch — but the skill's job is to *notice*, not fix.

## Duplicates — does something like this already exist?

*Skip in a brand-new module with no neighbors to compare against.*

For each new function, type, hook, utility, or component the diff introduced, check whether the codebase already has something with the same shape.

Quick checks:

- `grep -r "function <name>" src/` for new function names — and also grep for likely synonyms (`debounce` / `throttle`, `fetch` / `get` / `load`).
- For new types/interfaces, search for similar shapes elsewhere — particularly in adjacent modules.
- For new components, check the design system or shared component directory first.
- For new utilities, check `utils/`, `lib/`, and the top-level `package.json` for libraries already imported elsewhere.

Shapes that get reinvented constantly: debounce/throttle, deep-equal, deep-clone, retry-with-backoff, classnames helpers, async queues, event emitters, ID generators, date formatters.

For each finding, name **the new thing** and **what already exists** — include the file path of the existing primitive so the user can verify in one click.

## Output

```markdown
## Complexity Check

**Diff scope:** N files changed, +X/-Y lines

### Additions — was each new thing necessary?
- **[file:line]** [Specific complexity]. → [What to cut, and why it's safe.]
- ...

If nothing flagged: "Change is appropriately sized for what it does."
If skipped: "N/A — [reason]."

### Premises — could any assumption be dropped?
- **[Assumption]** Currently: [where it shows up]. If false: [what could be deleted, rough size]. To verify: [grep / git log / ask whom].
- ...

If nothing flagged: "No assumptions in this area look ripe to challenge."
If skipped: "N/A — [reason]."

### Spread — is the concept localized?
- **[Concept]** Smeared across: [files/lines]. → [What to extract / centralize.]
- ...

If nothing flagged: "Change is appropriately localized."
If skipped: "N/A — [reason]."

### Duplicates — does something like this already exist?
- **[New thing]** at [file:line]. Existing equivalent at [file:line]. → [Use the existing primitive.]
- ...

If nothing flagged: "No obvious duplication of existing primitives."
If skipped: "N/A — [reason]."

### Verdict
One sentence: **ship as-is** | **trim before shipping** | **broader simplification opportunity here — worth a separate task**.
```

## Guardrails

- **Surface, don't auto-fix.** Flag complexity and assumption challenges; let the user decide. Simplification needs intent.
- **Premises findings are claims, not facts.** Mark each with how to verify (`grep for usages`, `check git log for last config change`, `ask the team`). Never delete based on a Premises finding without verifying.
- **Stay scoped to the diff and its neighbors.** Don't audit the whole codebase.
- **Keep the report tight.** 3–7 findings total across all four lenses. More than that and the user won't act on any.
- **Mark skipped lenses N/A explicitly.** Silence on a lens is ambiguous; "N/A — only 1 file changed" tells the reader the lens was considered.
- **Don't flag things you'd let through in a code review.** This is a self-critique pass, not a search for perfection.

---

## AZ Skill Feedback

After the run, if this skill was useful, confusing, broken, or missing context, submit 1-3 safe sentences. Include `--agent-harness` when known. Include `--model-config` only if the harness exposes the exact model/config; otherwise leave it as `unknown`:

`python3 ~/.agents/skills/skill-feedback/scripts/skill-feedback.py --skill complexity-check --rating idea --text "..."`

Never include secrets, private data, source code, long prompts, or stack traces.
