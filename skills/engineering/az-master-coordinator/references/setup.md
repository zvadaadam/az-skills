# Setup

**Models.** You and every lead run on the strongest judgment model, today Fable 5.2, because coordinators make the decisions and their mistakes cost the most. Every Claude session on the user's account, coordinators and their Opus subagents alike, draws on one usage limit, so tell the user at the start how many will run at once: when the limit hits, they all stop at the same moment. Workers run on another provider so they don't use up that limit: ask the user once which ones (recommend GPT-6.2 Astra to build and GPT-6.2 Sol to review). Run your own subagents on Opus 5.5 (`model: "opus"`). Look up exact names with `ListModels`, and always pass `agent`, `model` and `effort`.

**Running leads.** Find each workspace in flight and its lead, and send each lead one message: you coordinate landing now, your session id, what its handoff must contain (step 1 of `gate.md`), and to send you its revision in one line when it first freezes a candidate. If a lead already follows a project's own role file, that file supplies the repository's facts (commands, locks, required checks, sign-offs) and these skills decide the role, including who reports to whom and when.

**New workspaces.** Create only the ones the user asked for, and propose the rest. `CreateWorkspace` from the base branch with the brief as its first message, and put the new workspaces in one sidebar section. The brief:

1. Opens with `Use $az-workspace-coordinator to lead this workspace.`, because a lead takes that role only when it's named.
2. States the goal, the worker models the user chose, the one-line note you want when it first freezes a candidate, and the handoff you need (step 1 of `gate.md`).
3. Says that no session brings a window to the front while the user works, and asks which steps truly need the app in front. Those run early in the lane, when the user is away; after 30 minutes of waiting, the lead asks you, and you ask the user for a few minutes at the screen.
4. Ends with your session id as the one to report to.

If `az-workspace-coordinator` isn't installed where the lead runs, copy its folder (`SKILL.md` and `references/`) into the lead's `.context/` and note where and when you read it, or ask the user to run `npx skills add zvadaadam/az-skills --skill az-workspace-coordinator`. Never point a lead at a working tree someone is still editing: it can change under them.

**The fallback wake.** While any lane is in flight, keep one recurring wake about every 45 minutes, because a usage limit can stop every coordinator at once, and then no lead's message ever comes to start your next turn. In Claude Code, create it with `CronCreate` at a minute that isn't :00 or :30, with the prompt "Run Each turn". It lives only in this session: recreate it after a relaunch, and delete it with `CronDelete` when no lane is in flight. When a limit stops the work, put its reset time on the board; at the first wake after the reset, steer each stopped lead to continue, leads before their workers.
