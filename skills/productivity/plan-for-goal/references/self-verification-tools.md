# Self-verification tools

The close-the-loop section of a `/goal` prompt only works if the agent can actually run and inspect the feature. For pure backend, library, or CLI work, that's tests and shell commands — the agent already has what it needs. For anything **user-facing** — web, mobile, desktop — the loop needs the agent to drive a real browser, simulator, or desktop screen. Without those tools, the loop will either claim "I tested it" without testing, or stall waiting for the user every iteration.

Three open-source projects exist for exactly this — one per surface.

| Surface | Tool | Repo |
|---|---|---|
| Web (browser) | `agent-browser` | https://github.com/vercel-labs/agent-browser |
| Mobile (iOS / Android) | `agent-device` | https://github.com/callstackincubator/agent-device |
| Desktop (macOS / Windows / Linux) | `cua` | https://github.com/trycua/cua |

Equivalents already in the user's environment (Playwright MCP, `mcp__claude-in-chrome__*`, Appium, etc.) count too — **use what's there before suggesting an install.**

## Detect first, draft second

Before writing the close-the-loop section, identify the surface the work touches and check what's available:

- **Web:** `which agent-browser`, or check if a browser-control MCP (`mcp__claude-in-chrome__*`, Playwright) is loaded.
- **Mobile:** `which agent-device`, or check for `xcode-mcp` / Android tooling already wired up.
- **Desktop:** `which cua`, or check for any existing GUI automation MCP.

If the surface needs interaction and **nothing is available**, tell the user upfront — before they run `/goal` — so they can install the right tool. Don't silently write a verification path the loop can't execute.

Suggested phrasing:

> Your `/goal` loop won't be able to self-verify the [surface] without browser/device/desktop control. The fastest path is to install one of these and re-run:
> - Web → `agent-browser` ([repo](https://github.com/vercel-labs/agent-browser))
> - Mobile → `agent-device` ([repo](https://github.com/callstackincubator/agent-device))
> - Desktop → `cua` ([repo](https://github.com/trycua/cua))
>
> Follow the install instructions in the repo README for your setup. If you'd rather verify manually each iteration, say so and I'll write the close-the-loop as a checklist for you to run.

## How to reference the tool in the `/goal` prompt

Once a tool is available, **name it once** in the close-the-loop section and describe the user-visible verification path. Don't inline the tool's full command syntax — the agent reads the docs each turn anyway.

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

### Desktop example (using `cua`)

```
**How to close the loop:**
1. Build and launch the app.
2. Use cua to open the new "Export" menu item.
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
