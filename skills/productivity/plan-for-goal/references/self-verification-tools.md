# Self-verification tools

The close-the-loop section of a `/goal` prompt only works if the agent can actually run and inspect the feature. For pure backend, library, or CLI work, that's tests and shell commands — the agent already has what it needs. For anything **user-facing** — web, mobile, desktop — the loop needs the agent to drive a real browser, simulator, or desktop screen. Without those tools, the loop will either claim "I tested it" without testing, or stall waiting for the user every iteration.

There's usually more than one option per surface. Pick the **highest-available tier** from the ladders below — if the top option isn't installed, fall back to the next one. Only suggest the user install something new when nothing in the ladder is wired up.

## Preference ladder — by surface

### Web

1. **`agent-browser`** — recommended. Purpose-built for AI agents with a clean API designed for LLM-driven flows. ([repo](https://github.com/vercel-labs/agent-browser))
2. **Playwright MCP** / **`mcp__claude-in-chrome__*`** / equivalent browser-control MCP — solid alternatives if already wired up. Use them as-is; no need to layer `agent-browser` on top.
3. **Harness-native computer-use** (Codex computer-use, Claude computer-use) — drives a browser via screen/pixel control. Works, but more brittle than a DOM-aware tool because it operates on rendered pixels instead of the document.
4. **Manual checklist** — the user runs verification each iteration. The loop continues; the human verifies.

### Mobile (iOS / Android)

1. **`agent-device`** — recommended. Purpose-built for AI agents driving simulators and physical devices, understands app lifecycle and native gestures. ([repo](https://github.com/callstackincubator/agent-device))
2. **`mcp__xcode-mcp__*`** (iOS) / Android-emulator tooling — fine alternatives if already wired up.
3. **Harness-native computer-use** — can interact with a simulator window as if it were a desktop, but doesn't understand device concepts. Less reliable for gesture flows.
4. **Manual checklist** — same fallback.

### Desktop (macOS / Windows / Linux)

1. **Harness-native computer-use** (Codex, Claude) — recommended *when available*. Desktop apps lack a universal automation API, so pixel/screen control is the realistic baseline, and the harness's built-in version is the cleanest path: no install, already authenticated, maintained alongside the agent.
2. **`cua`** — dedicated cross-platform GUI automation; use when the harness doesn't ship with computer-use, or when you want a more programmable interface. ([repo](https://github.com/trycua/cua))
3. **AppleScript** / **`xdotool`** / OS-native scripting — fine for narrow, well-defined flows.
4. **Manual checklist** — same fallback.

## Detect what's available, then draft

Before writing close-the-loop, identify the surface and walk the ladder top-down:

- **Web:** `which agent-browser` → check loaded MCP tools for browser control (`mcp__claude-in-chrome__*`, Playwright MCP) → check whether the harness exposes computer-use.
- **Mobile:** `which agent-device` → check for `mcp__xcode-mcp__*` or Android emulator tooling → harness computer-use.
- **Desktop:** check whether the harness exposes computer-use → `which cua` → OS-native scripting hooks.

Pick the highest-tier available option and **name it explicitly** in the close-the-loop section so the agent uses it consistently across the loop.

## When nothing on the ladder is wired up

Tell the user upfront — before they run `/goal` — so they can install something. The recommended top-of-ladder is the cleanest path; the rest are fine alternatives. Suggested phrasing:

> Your `/goal` loop won't be able to self-verify the [surface] without [browser/device/desktop] control. The recommendation is to install **[top tier]** since that's the highest-fidelity option, but any of these will work — pick what fits your setup:
>
> - **Web** → `agent-browser` (best) → Playwright MCP / claude-in-chrome → harness computer-use
> - **Mobile** → `agent-device` (best) → xcode-mcp / Android tooling → harness computer-use
> - **Desktop** → harness computer-use (best when available) → `cua` → AppleScript / xdotool
>
> If you'd rather verify manually each iteration, say so and I'll write the close-the-loop as a checklist for you to run.

## How to reference the chosen tool in the `/goal` prompt

Once a tool is picked, **name it once** in the close-the-loop section and describe the user-visible verification path. Don't inline the tool's full command syntax — the agent reads the docs each turn anyway.

### Web example (using `agent-browser`)

```
**How to close the loop:**
1. `pnpm dev`; wait for http://localhost:3000.
2. Use agent-browser to navigate to /pricing and click "Subscribe" on the Pro plan.
3. The Stripe Checkout iframe must appear within 2s. Use test card 4242 4242 4242 4242.
4. After redirect, read the DOM — the active-plan badge must say "Pro".
5. Replay the webhook from Stripe CLI; user record must remain at Pro (idempotency check).
```

### Mobile example (using `agent-device`)

```
**How to close the loop:**
1. Build for iOS simulator and launch the app via agent-device.
2. Tap Settings → Appearance → Dark.
3. Walk every top-level tab. Read each screen — no light-mode surfaces remain.
4. Background and relaunch. The dark theme must be active before splash dismisses.
5. `pnpm test` is green.
```

### Desktop example (using harness computer-use, fallback to `cua`)

```
**How to close the loop:**
1. Build and launch the app.
2. Open the "Export" menu item via computer-use (or cua if computer-use isn't available).
3. Pick PDF; confirm the save dialog. Wait for completion.
4. Read the destination on disk — file exists and opens as a valid PDF.
5. Run the export with no file selected. The error toast must say "Pick a file first" — not a stack trace.
```

## Manual-verification fallback

If the user explicitly opts out of installing automation tools, **make it explicit in the prompt** so the agent doesn't claim it self-verified:

```
**How to close the loop (manual verification — the agent cannot self-drive the UI in this loop):**
After each iteration, write a one-screen status note for the user to walk through:
1. [steps the user will run]
2. [what they should see]
3. [what counts as "still broken"]
End the turn after the status note and wait.
```

The loop still iterates, but verification becomes a human-in-the-loop step. State the trade-off honestly rather than letting the agent hallucinate verification.
