# Setup

**Models.** You and each workspace coordinator run on the strongest judgment model, today Fable 5.2, because these roles make the decisions and their mistakes cost the most. Tell the user up front how many Claude sessions will run at once, including Opus subagents. Sessions on the same account share a usage limit and can all stop together. Workers run on another provider so they don't use up that limit: ask the user once which ones (recommend GPT-6.2 Astra to build and GPT-6.2 Sol to review). Run your own subagents on Opus 5.5 (`model: "opus"`). Look up exact names with `ListModels`, and always pass `agent`, `model` and `effort`.

**Existing workspaces.** Identify the coordinator of each workspace in scope. Tell each one that you now handle landing order, give your session ID, and specify the handoff you need (step 1 of `gate.md`). Ask for a one-line message with the revision as soon as each coordinator freezes its first candidate. If a coordinator already follows a project's role file, that file supplies the repository's commands, locks, required checks and sign-offs.

**New workspaces.** Create only the ones the user asked for, and propose the rest. `CreateWorkspace` from the base branch with the brief as its first message, and put the new workspaces in one sidebar section. The brief:

1. Assigns one change to the workspace coordinator. If `az-workspace-coordinator` is installed there, open with `Use $az-workspace-coordinator to coordinate this workspace.`
2. States the goal, the worker models the user chose, the one-line notice when the first candidate freezes, and the handoff you need (step 1 of `gate.md`).
3. Tells sessions to keep windows in the background while the user works. Schedule steps that need the foreground early, when the user is away. If a coordinator has waited 30 minutes, it tells you and you ask the user for time at the screen.
4. Ends with your session id as the one to report to.

If the coordinator skill is unavailable, put the assignment in the brief itself: direct builders in that checkout, have a reviewer check the change and a checker exercise it, then return the verified revision to you. If you supply a copy of the skill, include its `references/` in the coordinator's `.context/` and record the source revision so the instructions stay stable.

**The fallback wake.** While any workspace has work in flight, keep one recurring wake about every 45 minutes. A usage limit can stop every coordinator before anyone sends the message that would wake you. In Claude Code, use `CronCreate` at a minute other than :00 or :30 with the prompt "Run Each turn". The wake belongs to this session. Recreate it after a relaunch and delete it with `CronDelete` when the last workspace finishes. Record any usage-limit reset time on the board. On the first wake after the reset, resume the stopped coordinators so they can resume their workers.
