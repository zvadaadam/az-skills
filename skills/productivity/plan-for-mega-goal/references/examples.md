# Worked example

One end-to-end mega-goal breakdown. **Study, don't copy** — the point is to calibrate voice, see how sub-goals split, and watch the roadmap / sub-goal / pointer-prompt triangle stay consistent under autonomous operation.

The example covers: the proposed decomposition (what the skill shows the user before writing anything), the resulting `ROADMAP.md`, one sub-goal file in full, and the final pointer prompt.

---

## Example: Replace homegrown auth with WorkOS

**Intent:** Our app uses a custom email/password auth system. We want to swap it for WorkOS — SSO, magic links, and managed password reset — without breaking existing sessions or shipping a maintenance window.

This is a mega-goal because it's 5+ sub-goals with a shared destination ("WorkOS is the only identity provider, old auth code gone, no user noticed the swap") that can't fit in 4000 chars without losing the quality bar per area.

### Step 1 — Decomposition shown to the user first (plain text, no files yet)

> **Proposed mega-goal:** `auth-rewrite` — replace homegrown auth with WorkOS, no maintenance window, no user-visible regression.
>
> **Quality bar:** Users don't notice the swap. SSO and magic-link flows feel native, not tacked-on. Zero sessions terminated mid-migration.
>
> **Sub-goals (5):**
> 1. **WorkOS connection + dev environment** — `Done =` `npx workos test` returns valid org+connection in dev, env vars in `.env.example`, PR opened via ghstack AND that PR's CI green AND /code-review on the PR clean.
> 2. **Session migration script** — `Done =` script maps every active session row to a WorkOS user, idempotent re-run produces zero diffs, PR opened via ghstack AND that PR's CI green AND /code-review on the PR clean.
> 3. **Login + magic-link UI** — `Done =` cold visit to `/login` → magic-link email → click → dashboard with valid session in <5s; cookie has `HttpOnly` + `SameSite=Lax`; PR opened via ghstack AND that PR's CI green AND /code-review on the PR clean.
> 4. **Password reset + SSO callback** — `Done =` reset email triggers WorkOS-managed flow; SSO callback handles success, error, and replay without leaking session tokens; PR opened via ghstack AND that PR's CI green AND /code-review on the PR clean.
> 5. **Tear down old auth code** — `Done =` `git grep -i "bcrypt\|password_hash"` returns nothing in `src/`, `users.password_hash` column dropped, no dead routes, PR opened via ghstack AND that PR's CI green AND /code-review on the PR clean.
>
> **Dependencies:**
> - 01: none
> - 02: 01
> - 03: 02
> - 04: 01 (can interleave with 02–03)
> - 05: 01, 02, 03, 04
>
> **Approve, or adjust:** `merge X+Y` · `split X` · `add X` · `remove X` · `sharpen X`'s Done · `reorder`.

*(User confirms or redirects. Only then do files get written.)*

### Step 2 — The `ROADMAP.md` written to disk

```markdown
# auth-rewrite

Replace the homegrown email/password auth system with WorkOS as the sole identity provider. Existing sessions survive the swap; no maintenance window; the SSO and magic-link experiences feel native to the app, not bolted on.

## Quality bar

Users don't notice the swap. Boring, bulletproof: the team stops thinking about auth after this ships. No `password_hash` anywhere, no half-migrated session table, no "we'll clean this up later" branches.

## Sub-goals

- [ ] **01 — WorkOS connection + dev environment** — `goals/01-workos-connection.md` — `Done =` `npx workos test` returns valid org+connection, env vars in `.env.example`, PR opened via ghstack AND that PR's CI green AND /code-review on the PR clean
- [ ] **02 — Session migration script** — `goals/02-session-migration.md` — `Done =` migration script maps every active session to a WorkOS user, idempotent, PR opened via ghstack AND that PR's CI green AND /code-review on the PR clean
- [ ] **03 — Login + magic-link UI** — `goals/03-login-magic-link.md` — `Done =` cold `/login` → magic-link → dashboard in <5s, cookie `HttpOnly`+`SameSite=Lax`, PR opened via ghstack AND that PR's CI green AND /code-review on the PR clean
- [ ] **04 — Password reset + SSO callback** — `goals/04-reset-and-sso.md` — `Done =` reset email triggers WorkOS flow; SSO callback handles success/error/replay without token leaks, PR opened via ghstack AND that PR's CI green AND /code-review on the PR clean
- [ ] **05 — Tear down old auth code** — `goals/05-teardown.md` — `Done =` `git grep -i "bcrypt|password_hash"` empty in `src/`, column dropped, no dead routes, PR opened via ghstack AND that PR's CI green AND /code-review on the PR clean

## Dependencies

- 01: none
- 02: 01
- 03: 02
- 04: 01 (can interleave with 02–03)
- 05: 01, 02, 03, 04

## Done

`Done =` every box above is checked AND each sub-goal's `Done =` line is proven against current state. No exceptions.
```

### Step 3 — One sub-goal file shown in full (`goals/03-login-magic-link.md`)

```markdown
# 03 — Login + magic-link UI

**Goal:** A cold visitor at `/login` enters an email, receives a magic-link email within seconds, clicks it, and lands on the dashboard with a valid session. The form looks and feels like the rest of the app — no WorkOS-default styling bleeding through.

**What great looks like:** Boring and instant. The user does not wait, does not bounce to a third-party domain, and does not see an auth screen they didn't expect. Error states are written like a teammate explains them, not like a stack trace.

**How to close the loop:**
1. `pnpm dev`; wait for the app to come up.
2. Use `agent-browser` to navigate to `/login`, enter a test email, submit.
3. Check the dev mailbox (mailpit / mailhog / etc.); a magic-link email must arrive within 5s.
4. Click the link in the browser; the redirect must land on `/dashboard` with a valid session cookie set.
5. Inspect the cookie: `HttpOnly` flag set, `SameSite=Lax`.
6. Re-run with an invalid email — the error message must read like a teammate explained it ("we don't have an account for that — want to sign up?"), not "user_not_found".
7. `gh pr checks <pr>` shows CI green.
8. `/code-review <pr>` returns no high-severity findings.

**Done =** Cold visit `/login` → magic-link email → click → `/dashboard` with valid session in under 5s, cookie has `HttpOnly` and `SameSite=Lax`, error states human-readable, no third-party UI bleed-through, PR opened via ghstack AND that PR's CI green AND /code-review on the PR clean.

**Not:** redesigning the dashboard, adding social login providers beyond what WorkOS already wires up, changing the email transport, building a "remember me" toggle, retrofitting the old session table (that's sub-goal 02's job).

**Open:** which `agent-browser`-equivalent to use if `agent-browser` isn't wired up (harness computer-use or a manual checklist are acceptable fallbacks); exact form layout so long as it matches the rest of the app's component vocabulary.

**Where to look:** The auth route layer, the existing login component, the WorkOS connection set up in sub-goal 01, the dev mailbox configuration.

**Time budget:** ~3h.

## PR body

\`\`\`markdown
**Part of mega-goal:** `auth-rewrite` (sub-goal 03 of 05)
**Roadmap:** `.megagoal/auth-rewrite/ROADMAP.md`
**Done =** Cold visit `/login` → magic-link → `/dashboard` with valid session in <5s, cookie `HttpOnly`+`SameSite=Lax`, error states human-readable, PR opened via ghstack AND that PR's CI green AND /code-review on the PR clean.
**Stack:** depends on sub-goal 02 (session migration); blocks sub-goal 05 (teardown).

## What changed
- New `/login` route with magic-link form, app-styled
- WorkOS magic-link initiation + callback handlers
- Session cookie attributes set correctly (`HttpOnly`, `SameSite=Lax`)
- Error-state copy reviewed for tone

## Verification
- `agent-browser` recording: cold `/login` → email arrives in 2.1s → click → `/dashboard` in 3.2s ✓
- Cookie inspector: `HttpOnly` ✓, `SameSite=Lax` ✓
- Invalid-email error: "we don't have an account for that — want to sign up?" ✓
- CI ✅ · /code-review clean ✅
\`\`\`
```

### Step 4 — The pointer prompt (this is what the user pastes into `/goal`)

Measured at **3,847 characters** — under the 4000 cap. (The autonomy/hard-rules prompt is large by design — every line in it is preventing an observed failure mode, not micromanaging tactics.)

```
Work the mega-goal at `.megagoal/auth-rewrite/ROADMAP.md` using stacked-prs with ghstack. Run autonomously — keep moving and self-handle interruptions, don't wait for human input.

**Turn-1 pre-flight:** `which gh ghstack`. If missing, log to NOTES.md `## Event log` and stop. Install and re-paste.

**Read every turn:** ROADMAP.md, the sub-goal file you're working on, NOTES.md `## Active blockers`. On-disk is authoritative.

**Picking what to work on.** Stack PRs = PR numbers on ROADMAP.md entries (any line with `PR #N`). If any has CHANGES_REQUESTED, fix it before new work: edit on that PR's branch, `ghstack submit`, reply. Only halt is "do not proceed". Open PRs NOT in the stack are informational unless they target the same files or block this stack's CI. Otherwise work the next unchecked sub-goal whose dependencies are checked. If its `Done =` is already true, check the box and continue. If all remaining sub-goals are blocked, retry one only if its `Prerequisite:` in `## Active blockers` has actually changed since `Last verified:`. If unchanged, bump the timestamp and skip. If nothing retries, stop.

**Working a sub-goal.** Code on a stacked branch. `ghstack submit` opens/updates the PR — immediately append `— PR #N` to the roadmap entry (still `- [ ]`). PR body's static block comes from the sub-goal file's `## PR body`; fill in `## What changed` and `## Verification` from the diff. Wait for `gh pr checks <pr>` green (NOT local tests). Run `/code-review <pr>`. Fix high-severity findings on the same branch; skip nits. If a failure persists after fixing the obvious cause more than once, add a `## Active blockers` line and hop.

**NOTES.md** (3 sections — see `notes-template.md`): `## Active blockers` updated in place with fingerprints (command · failure · prerequisite · last verified); `## Proposed additions` + `## Event log` append-only. Log to `## Event log`: sub-goal complete (PR # + wall), reviewer feedback addressed, blocker resolved, heartbeat, decisions, final summary.

**FEEDBACK.md (optional).** Friction the skill should prevent, missing tooling, codebase structure issues, contradictory pointer-prompt rules — append a paragraph under the right category. Input for improving the skill, not for run-of-the-mill events.

**Hard rules — not optional:**
- ONE open PR per sub-goal via ghstack. Zero PRs (local diff only) is an unstarted sub-goal. One mega-PR is a failure mode.
- A checked box is `- [x] — PR #N` for an open PR, or it's not checked. Local tests passing is NOT "CI green".
- Each sub-goal's verification = its file's "How to close the loop". Generic repo tests are a baseline, not sub-goal verification.
- Don't merge PRs — human's gate.
- Don't rewrite a sub-goal's `Done =` or directional outcome mid-loop.
- Don't invent sub-goals — propose in `## Proposed additions`.
- Don't amend earlier sub-goals' commits from a later branch — use a fix-up on the current branch.
- Don't append duplicate stop summaries for unchanged blockers — bump the `## Active blockers` timestamp.
- Don't burn the loop on one stuck problem.

**Stack audit before stopping:** extract every `PR #N` from ROADMAP.md; `gh pr view <N>` each to confirm open + CI green + /code-review clean. Any checked sub-goal whose PR fails → box invalid; unmark and keep working. (Don't branch-name search — ghstack uses numeric heads.)

**Stop only when** the stack audit confirms success, every remaining sub-goal is blocked with unchanged prerequisites, or token budget exhausted. On stop, append final summary to `## Event log` — outcome, PRs (#), time, blockers (point at `## Active blockers`), reviewer requests.

`Done =` every sub-goal in ROADMAP.md is `- [x] — PR #N` for an actual open PR AND each `Done =` is proven against the PR's current state (CI status, /code-review verdict, PR file contents), not local state.
```

---

## What works in this example

- **The decomposition was shown to the user first as plain text.** Wrong splits are the most expensive failure mode; catch them cheapest before scaffolding. Edit commands (`merge X+Y`, `sharpen X`) let the user redirect in single small steps instead of a full re-do.
- **Dependencies are mandatory and explicit.** The loop reads them every turn to reroute around blocked sub-goals. Without them, one blocked sub-goal would stall the whole loop instead of letting it hop to an independent one.
- **Each sub-goal's `Done =` is audit-mappable** — filesystem state, command output, browser-driven verification, CI/code-review status. None of them are "feels right".
- **PR opened via ghstack AND that PR's CI green AND /code-review on the PR clean is baked into every `Done =`.** The loop won't check a box without both. The autonomy-friendly quality gate.
- **The `Not:` list on sub-goal 03 names sub-goal 02's territory explicitly** — *"that's sub-goal 02's job"*. Mega-goal-specific discipline: scope edges aren't just "what's out of the mega-goal", they're also "what belongs to a sibling sub-goal".
- **The pointer prompt frames the work, not the procedure.** Conceptual sections (what to read, how to pick, what "done" means, what to log, what not to do, when to stop) — not a 10-step recipe. The agent brings judgment for retry counts, exact tool invocations, timing. *Why this matters:* a capable agent reads the situation and adjusts; a step-by-step recipe rots whenever the situation differs.
- **The PR body block lives in the sub-goal file.** Pre-written context (mega-goal slug, roadmap path, Done, stack position) plus agent-filled `## What changed` + `## Verification` from the actual diff. Reviewers see full context without leaving the PR.
- **`NOTES.md` is the audit trail for the multi-day run.** Sub-goal completions, reviewer feedback handled, blocks encountered, heartbeats, the final summary — all skimmable in 30 seconds when the human returns.
