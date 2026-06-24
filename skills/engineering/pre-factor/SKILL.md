---
name: pre-factor
description: Before implementing a feature or non-trivial change, scan the code it will land in and surface prep refactors that make the change easy — so the feature lands clean instead of accreting tech debt (Kent Beck "make the change easy, then make the easy change"). Use BEFORE writing code, when about to build a feature, add a new case/provider/handler to an existing pattern, restructure in service of upcoming work, or just after an implementation plan is set. Every proposal must trace to the upcoming change — not generic cleanups. Skip tiny edits and brand-new code; for changes already written use complexity-check instead.
hooks:
  PostToolUse:
    - matcher: "*"
      hooks:
        - type: command
          command: 'python3 "$HOME/.claude/skills/skill-feedback/scripts/skill-event.py" --skill pre-factor --event skill_activated --agent-harness claude-code --quiet'
          timeout: 5
---

# Pre-Factor

> "For each desired change, make the change easy (warning: this may be hard), then make the easy change." — Kent Beck

You're about to build something. Before you write the feature, look at the code it will land in and **make the change easy** first. A **pre-factor** is a small, behavior-preserving reshaping that turns the upcoming feature from a fight into a one-liner — landed as its own commit, *before* the feature. This is the forward-looking bookend to `complexity-check`, which audits the diff after.

The whole discipline is one rule: **every pre-factor must trace to the change you're about to make.** A refactor that doesn't make *this* feature easier, safer, or smaller isn't a pre-factor — it's a generic cleanup, and it goes to the backlog, not the plan.

## Fire fast, don't derail

You fired automatically, mid-flow, on code the user wants *now*. Stay light: do the analysis, surface a tight plan, get one quick "go," then proceed. Never turn the feature into a rewrite, and never block — if the user signals speed ("just build it"), name the single highest-leverage pre-factor in one line and move on.

**Skip entirely** for: tiny edits (typo, rename, dep bump), brand-new code with no neighbors yet, and anything already written (that's `complexity-check`).

## 1. Pin the change

State in one sentence what's being built and the entry points it adds or modifies. Take it from the user's request, the conversation, or the plan. If you can't name it crisply, ask — a fuzzy target makes every lens below noise.

✓ Done when: you can name the change in one sentence and list the symbols/files it will add or touch.

## 2. Map the landing zone

The **landing zone** is the set of files, functions, and seams the change will edit or sit beside. Find it — `grep` for the pattern you're about to extend, then read those files *in full* (a diff-sized view hides whether the surrounding shape is ready). Stay targeted; this is not a whole-repo scan.

✓ Done when: you have a concrete list of the files and symbols the change will touch.

For an unusually large landing zone, fan out `Explore` sub-agents — one per module — to map it in parallel. Default to a single pass.

## 3. Run the lenses over the landing zone

Apply each lens to the landing zone only. Each asks the same question from a different angle — *would fixing this first make the change easy?* A lens with nothing to say is an explicit **N/A**, not silence.

- **Seam fit** — you're about to extend a structure (if/else chain, `switch`, a copy-pasted block, a list of `if type ==`). Reshaping it into a registry / table / polymorphic dispatch *first* turns your feature from an N-way edit into a one-line add. The highest-leverage lens.
- **Safety net** — is the code you're about to change covered by tests? If not, characterization tests come *first*, so the pre-factor and the feature are both safe to land.
- **Duplication you're about to feed** — about to add the 3rd copy of something? Collapse the existing copies to one *before* adding to the pile.
- **Vocabulary** — will the current names and types force the new code to read awkwardly, cast, or thread a value it shouldn't know about? Fix names/types first so the feature speaks the domain.
- **Stale premise** — does the feature break an assumption the code bakes in ("there's only ever one X", "this is always sync")? Loosen that premise as a prep step instead of fighting it inline.

✓ Done when: every lens has produced a finding or an explicit N/A against the landing zone.

## 4. Gate each finding

For every finding, in order:

1. **Trace it** — one sentence tying it to the change. No sentence → cut it (backlog, not plan).
2. **Bucket it:**
   - **Do-first** — small, behavior-preserving, directly unblocks the feature. Its own commit, before the feature.
   - **Fold-in** — natural to do as part of the feature work itself.
   - **Defer** — real, but not needed for *this* change. Name it for the backlog and move on.
3. Prefer the **smallest** pre-factor that unblocks. Cap Do-first at ~3; if there are more, the feature is probably too big or wants its own refactor task — say so.

✓ Done when: every finding is traced and bucketed, and Do-first holds only what this change needs.

## 5. Surface the plan

Output the plan below. Then proceed: do the **Do-first** pre-factors as separate behavior-preserving commits, in order, then build the feature on the cleaned ground. If a pre-factor is risky or large, stop and confirm before touching code.

```markdown
## Pre-Factor — <the change, in one line>

**Landing zone:** <files / symbols the change touches>

### Do first (separate commits, before the feature)
1. **<pre-factor>** — <what changes>. Makes the change easy by: <trace>. _Cost: S/M · behavior-preserving._

### Fold into the feature
- **<pre-factor>** — <why it rides along>.

### Defer (backlog — not needed for this change)
- **<thing>** — <why it's real but out of scope now>.

**Sequence:** <refactor commit(s)> → <feature commit>
```

If nothing needs doing: **"Landing zone is ready — build directly."**

## Guardrails

- **Trace or cut.** Generic "this'd be nicer" findings are out — that's `code-simplifier`'s job, not this one.
- **Smallest prep that unblocks.** Don't turn a feature into a rewrite; a big restructure is a *deferred* task you surface, not work you start inline.
- **Behavior-preserving, separate commits, before the feature.** Keeps review clean and revert cheap.
- **Surface and recommend; the human greenlights code changes.** You auto-fired — earn the interruption by being short.
- **Don't re-litigate `complexity-check`.** This is the pre-implementation pass; that is the post-implementation one.

---

## AZ Skill Feedback

After the run, if this skill was useful, confusing, broken, or missing context, submit 1-3 safe sentences. Include `--agent-harness` when known. Include `--model-config` only if the harness exposes the exact model/config; otherwise leave it as `unknown`:

`python3 ~/.agents/skills/skill-feedback/scripts/skill-feedback.py --skill pre-factor --rating idea --text "..."`

Never include secrets, private data, source code, long prompts, or stack traces.
