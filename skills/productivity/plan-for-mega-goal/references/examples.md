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
> 1. **WorkOS connection + dev environment** — `Done =` `npx workos test` returns valid org+connection in dev, env vars in `.env.example`, CI green AND /code-review clean.
> 2. **Session migration script** — `Done =` script maps every active session row to a WorkOS user, idempotent re-run produces zero diffs, CI green AND /code-review clean.
> 3. **Login + magic-link UI** — `Done =` cold visit to `/login` → magic-link email → click → dashboard with valid session in <5s; cookie has `HttpOnly` + `SameSite=Lax`; CI green AND /code-review clean.
> 4. **Password reset + SSO callback** — `Done =` reset email triggers WorkOS-managed flow; SSO callback handles success, error, and replay without leaking session tokens; CI green AND /code-review clean.
> 5. **Tear down old auth code** — `Done =` `git grep -i "bcrypt\|password_hash"` returns nothing in `src/`, `users.password_hash` column dropped, no dead routes, CI green AND /code-review clean.
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

- [ ] **01 — WorkOS connection + dev environment** — `goals/01-workos-connection.md` — `Done =` `npx workos test` returns valid org+connection, env vars in `.env.example`, CI green AND /code-review clean
- [ ] **02 — Session migration script** — `goals/02-session-migration.md` — `Done =` migration script maps every active session to a WorkOS user, idempotent, CI green AND /code-review clean
- [ ] **03 — Login + magic-link UI** — `goals/03-login-magic-link.md` — `Done =` cold `/login` → magic-link → dashboard in <5s, cookie `HttpOnly`+`SameSite=Lax`, CI green AND /code-review clean
- [ ] **04 — Password reset + SSO callback** — `goals/04-reset-and-sso.md` — `Done =` reset email triggers WorkOS flow; SSO callback handles success/error/replay without token leaks, CI green AND /code-review clean
- [ ] **05 — Tear down old auth code** — `goals/05-teardown.md` — `Done =` `git grep -i "bcrypt|password_hash"` empty in `src/`, column dropped, no dead routes, CI green AND /code-review clean

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

**Directional outcome.** A cold visitor at `/login` enters an email, receives a magic-link email within seconds, clicks it, and lands on the dashboard with a valid session. The form looks and feels like the rest of the app — no WorkOS-default styling bleeding through.

**Quality bar.** Boring and instant. The user does not wait, does not bounce to a third-party domain, and does not see an auth screen they didn't expect. Error states are written like a teammate explains them, not like a stack trace.

**How to close the loop.**
1. `pnpm dev`; wait for the app to come up.
2. Use `agent-browser` to navigate to `/login`, enter a test email, submit.
3. Check the dev mailbox (mailpit / mailhog / etc.); a magic-link email must arrive within 5s.
4. Click the link in the browser; the redirect must land on `/dashboard` with a valid session cookie set.
5. Inspect the cookie: `HttpOnly` flag set, `SameSite=Lax`.
6. Re-run with an invalid email — the error message must read like a teammate explained it ("we don't have an account for that — want to sign up?"), not "user_not_found".
7. `gh pr checks <pr>` shows CI green.
8. `/code-review <pr>` returns no high-severity findings.

`Done =` Cold visit `/login` → magic-link email → click → `/dashboard` with valid session in under 5s, cookie has `HttpOnly` and `SameSite=Lax`, error states human-readable, no third-party UI bleed-through, CI green AND /code-review clean.

**Scope edges.** `Not:` redesigning the dashboard, adding social login providers beyond what WorkOS already wires up, changing the email transport, building a "remember me" toggle, retrofitting the old session table (that's sub-goal 02's job).

**Where to look.** The auth route layer, the existing login component, the WorkOS connection set up in sub-goal 01, the dev mailbox configuration.

**Time budget.** ~3h.

## PR body

\`\`\`markdown
**Part of mega-goal:** `auth-rewrite` (sub-goal 03 of 05)
**Roadmap:** `.megagoal/auth-rewrite/ROADMAP.md`
**Done =** Cold visit `/login` → magic-link → `/dashboard` with valid session in <5s, cookie `HttpOnly`+`SameSite=Lax`, error states human-readable, CI green AND /code-review clean.
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

Measured at **2,977 characters** — under the 4000 cap.

```
Work the mega-goal at `.megagoal/auth-rewrite/ROADMAP.md` using stacked-prs with ghstack. Run autonomously — keep moving and self-handle interruptions, don't wait for human input.

**Read every turn:** ROADMAP.md and the sub-goal file you're working on. On-disk is authoritative; memory of earlier turns may be stale.

**Picking what to work on.** First check open PRs in the stack — if any prior PR shows CHANGES_REQUESTED, address it before starting new work: read the comments, fix on that PR's branch, `ghstack submit` to restack, reply on the PR. The only thing that halts a sub-goal is a reviewer literally writing "do not proceed". Otherwise, work the next unchecked sub-goal whose dependencies (per ROADMAP.md `Dependencies:`) are all checked. Pre-flight: if its `Done =` is already true, check the box and continue. If nothing's workable but unchecked sub-goals remain, retry blocked ones once each, then stop.

**Working a sub-goal until its `Done =` is true.** Write code on a stacked branch via ghstack. `ghstack submit` opens or updates the PR — the PR body's static block comes from the sub-goal file's `## PR body`; fill in `## What changed` and `## Verification` from the actual diff. Wait for CI green. Run `/code-review <pr>`. Address high-severity findings on the same branch; skip nits. If a CI or code-review failure persists after fixing the obvious cause more than once, it's probably infrastructure flake or a deeper issue — log to NOTES.md, mark blocked, hop. Judgment beats a fixed retry count. When CI is green AND /code-review clean AND no pending CHANGES_REQUESTED on this PR: check the box (`- [ ]` → `- [x] — PR #N`), continue.

**Log to NOTES.md as you go** — one-line entries: sub-goal complete (PR # + wall time), reviewer feedback addressed (what + why), block (what was tried, what's next), periodic heartbeat when the loop's been running long, cross-cutting decisions, proposed new sub-goals under `## Proposed additions` (propose, don't work). Append-only. The human reads NOTES.md top-to-bottom on return.

**Don't:** merge PRs (human's gate) · rewrite a sub-goal's `Done =` or directional outcome mid-loop (contract is fixed) · invent sub-goals (propose, continue with existing roadmap) · amend earlier sub-goals' commits from a later branch (use a fix-up commit instead — fixing review feedback on the same PR's own branch is fine) · burn the loop on one stuck problem.

**Stop only when** all sub-goals are checked, every remaining sub-goal is blocked (after the once-each retry), or the token budget is exhausted. On any stop, write a final summary block to NOTES.md — outcome, PRs, time, blockers, reviewer requests addressed/pending. First thing the human reads on return.

`Done =` every sub-goal in `.megagoal/auth-rewrite/ROADMAP.md` is checked off AND every `Done =` line is proven against current state, audited against authoritative evidence (file contents, command output, PR check status, /code-review verdict), not memory.
```

---

## What works in this example

- **The decomposition was shown to the user first as plain text.** Wrong splits are the most expensive failure mode; catch them cheapest before scaffolding. Edit commands (`merge X+Y`, `sharpen X`) let the user redirect in single small steps instead of a full re-do.
- **Dependencies are mandatory and explicit.** The loop reads them every turn to reroute around blocked sub-goals. Without them, one blocked sub-goal would stall the whole loop instead of letting it hop to an independent one.
- **Each sub-goal's `Done =` is audit-mappable** — filesystem state, command output, browser-driven verification, CI/code-review status. None of them are "feels right".
- **CI green AND /code-review clean is baked into every `Done =`.** The loop won't check a box without both. The autonomy-friendly quality gate.
- **The `Not:` list on sub-goal 03 names sub-goal 02's territory explicitly** — *"that's sub-goal 02's job"*. Mega-goal-specific discipline: scope edges aren't just "what's out of the mega-goal", they're also "what belongs to a sibling sub-goal".
- **The pointer prompt frames the work, not the procedure.** Conceptual sections (what to read, how to pick, what "done" means, what to log, what not to do, when to stop) — not a 10-step recipe. The agent brings judgment for retry counts, exact tool invocations, timing. *Why this matters:* a capable agent reads the situation and adjusts; a step-by-step recipe rots whenever the situation differs.
- **The PR body block lives in the sub-goal file.** Pre-written context (mega-goal slug, roadmap path, Done, stack position) plus agent-filled `## What changed` + `## Verification` from the actual diff. Reviewers see full context without leaving the PR.
- **`NOTES.md` is the audit trail for the multi-day run.** Sub-goal completions, reviewer feedback handled, blocks encountered, heartbeats, the final summary — all skimmable in 30 seconds when the human returns.
