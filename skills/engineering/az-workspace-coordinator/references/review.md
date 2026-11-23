# Review

Tie every result to the source revision and build that produced it. A build from the shared checkout can include a sibling's unfinished edits, and a saved build can predate the last change, so carry proof forward only when both match the candidate.

1. **Read each builder's diff for design as it arrives,** not only for faults. For each construct it adds, copies or extends, ask whether it would be fine if the next twenty agents copied it. They will, because builders copy what the file already does. A second copy of existing logic, or code that parses another module's formatted output, is a finding even when every test passes. Fix a bad pattern the change copies or extends at its one owner, in this change; list bad patterns in files the change doesn't touch as follow-ups, and propose a wider refactor before starting it.
2. **Freeze the change** once the touched packages' tests pass. Give the reviewer the base, the diff and what's out of scope, and ask for design findings as well as faults (`az-complexity-check` has the lenses, if installed). If a master coordinates you, send it the frozen revision in one line, so its independent read runs alongside your reviewer instead of after the handoff.
3. **Check each finding against the code.** For each one still open, name the failure that could still happen and the evidence that would settle it.
4. **Close a test-only correction** when the bad input now fails, valid input passes, and the change touches only the test.
5. **For a visible defect,** have the checker replay the original interaction on the fixed build.
6. **After a fix that changes behavior,** have the reviewer reread that delta; that's where fix regressions get caught.
7. **If findings keep coming back on the same path,** or a fix spreads into a neighboring flow, stop patching. Compare that flow on the base and on the candidate, then decide the design: narrow the scope, change the approach, or give the wider change its own owner.

Review is done when the material findings are settled, the changed behavior has been exercised, and the required checks are accounted for.
