# Hand over

Show the user, or the master coordinator, a workspace that holds the candidate: one active PR per visible workspace, with its branch, Changes view and running preview all on the revision you name.

Then send one handoff: the candidate revision and base, the frozen diff, what ran on which build, proof still pending, a Patterns line (what older code got better, what was found and left), the decision needed, your recommendation, and one evidence link. If the scope shrank, also say which tests still apply, what must still run, which reservation to release, and who acts next.

Before the PR opens, confirm the user allowed opening it and that no sign-off they asked for is still outstanding, such as how an interaction feels; a checker's pass is not the user's approval. Then the named PR owner opens it and watches it to green (`az-greenlight-pr` if installed).

After the go, a fix for a CI or review finding lands under that go only if a check that failed before the fix passes after it and the full gate ran on the new head; send its delta with the merge report. Anything more goes back for a read before merge.
