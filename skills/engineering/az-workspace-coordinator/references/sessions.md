# Sessions

**Models.** If your brief doesn't name them, ask the user once and record the answer on the board. Recommend Fable 5.2 for yourself, with your own subagents on Opus 5.5 (`model: "opus"`) so reading code doesn't use up the Fable limit; GPT-6.2 Astra for builders and the checker (Gemini 4 Neon where your setup offers it, Opus 5.5 only when the Claude budget has room); and for the reviewer a different model from the builders, such as GPT-6.2 Sol, so its read is independent. Never build or review with a small fast model like Haiku: its mistakes cost more of your turns than it saves. Look up exact names with `ListModels`, and always pass `agent`, `model` and `effort` to `CreateSession`.

**Builders**, one per independent piece. Brief each with the user outcome, the files or hunks it owns, the closest existing implementation (by file) and what the new use needs from it, and the evidence you want back. Ask it to clean its own diff with `az-deslop` (if installed), and to message you when it finishes or needs a decision, not for routine progress: its finished message is what wakes you. When the fit is uncertain, have it try the hardest case first.

**Reviewer**: independent and read-only. It reads the frozen diff, not the conversation that produced it.

**Checker**: drives the real product on the candidate build and replays the reported failure. Passing tests are not proof: in one run all 12 checks passed while 15 cards were visibly clipped. Its brief says how to launch the product without taking the user's screen (`machine-and-screen.md`), and its report says how it launched.
