# Setup

**Models.** You and every lead run on the strongest judgment model, today Fable 5.2, because coordinators make the decisions and their mistakes cost the most. Workers run on another provider so they don't use up that limit: ask the user once which ones (recommend GPT-6.2 Astra to build and GPT-6.2 Sol to review). Run your own subagents on Opus 5.5 (`model: "opus"`). Look up exact names with `ListModels`, and always pass `agent`, `model` and `effort`.

**Running leads.** Find each workspace in flight and its lead, and send each lead one message: you coordinate landing now, your session id, and what its handoff must contain (step 1 of `gate.md`). If a lead already follows a project's own role file, that file supplies the repository's facts (commands, locks, required checks, sign-offs) and these skills decide the role, including who reports to whom and when.

**New workspaces.** Create only the ones the user asked for, and propose the rest. `CreateWorkspace` from the base branch with the brief as its first message, and put the new workspaces in one sidebar section. The brief:

1. Opens with `Use $az-workspace-coordinator to lead this workspace.`, because a lead takes that role only when it's named.
2. States the goal, the worker models the user chose, and the handoff you need (step 1 of `gate.md`).
3. Says that no session brings a window to the front while the user works, and asks which steps truly need the app in front; those wait until the user is away.
4. Ends with your session id as the one to report to.

If `az-workspace-coordinator` isn't installed where the lead runs, copy its folder (`SKILL.md` and `references/`) into the lead's `.context/` and note where and when you read it, or ask the user to run `npx skills add zvadaadam/az-skills --skill az-workspace-coordinator`. Never point a lead at a working tree someone is still editing: it can change under them.
