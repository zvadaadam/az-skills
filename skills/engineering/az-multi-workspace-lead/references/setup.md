# Setup

**Models.** You and each workspace coordinator run on the strongest judgment model, today Fable 5.2, because these roles make the decisions and their mistakes cost the most. Workers run on another provider so they don't use up that limit: ask the user once which ones (recommend GPT-6.2 Astra to build and GPT-6.2 Sol to review). Run your own subagents on Opus 5.5 (`model: "opus"`). Look up exact names with `ListModels`, and always pass `agent`, `model` and `effort`.

**Existing workspaces.** Identify the coordinator of each workspace in scope. Tell each one that you now handle landing order, give your session ID, and specify the handoff you need (step 1 of `gate.md`). If a coordinator already follows a project's role file, that file supplies the repository's commands, locks, required checks and sign-offs.

**New workspaces.** Create only the ones the user asked for, and propose the rest. `CreateWorkspace` from the base branch with the brief as its first message, and put the new workspaces in one sidebar section. The brief:

1. Assigns one change to the workspace coordinator. If `az-workspace-coordinator` is installed there, open with `Use $az-workspace-coordinator to coordinate this workspace.`
2. States the goal, the worker models the user chose, and the handoff you need (step 1 of `gate.md`).
3. Says that no session brings a window to the front while the user works, and asks which steps truly need the app in front; those wait until the user is away.
4. Ends with your session id as the one to report to.

If the coordinator skill is unavailable, put the assignment in the brief itself: direct builders in that checkout, have a reviewer check the change and a checker exercise it, then return the verified revision to you. If you supply a copy of the skill, include its `references/` in the coordinator's `.context/` and record the source revision so the instructions stay stable.
