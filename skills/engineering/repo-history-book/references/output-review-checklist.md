# Output review checklist

Use this after the first build.

## Narrative quality

- Does the output feel like a readable book, not a dump?
- Is there a clear suggested reading path?
- Are the biggest lessons stated directly?
- Are pivots and rollbacks easy to spot?
- Are repeated pain loops called out explicitly?

## Deep lessons quality

- Are there 6–10 deep lessons? (Fewer = thin. More = signal dilutes.)
- Does each lesson's title read as a **claim**, not a topic?
- Does the `one_liner` survive out of context? (If you copy-pasted it into a tweet, would it still mean something?)
- Are `what_broke` bullets paraphrased from **primary sources** (team-written lessons docs, specific PRs, specific files)?
- Does `what_they_learned` state the **rule the team converged on**, not just "they fixed it"?
- Does `transferable` carry a generalization that would survive being lifted into a different codebase?
- Does each lesson cite **at least 2 pieces of evidence** (PR numbers, file paths, doc sections)?
- Do the size categories (xl/l/m/s) match the actual weight — or is a small lesson puffed up to look important?

## Evidence quality

- Can the reader jump from summary to day note to commit note to GitHub evidence?
- Are PRs, tags, and hotspot files exposed?
- Are facts and interpretations clearly separated?

## Interaction quality

- Is there a clear story-vs-evidence framing, optionally with reading modes?
- Does the current section stay obvious in navigation while scrolling?
- Is the HTML skimmable on first load?
- Is there a commit explorer with useful filters?
- Are important note files linked directly?
- Does the chapter structure hold up on mobile widths?

## Improvement heuristic

If the first output feels smart but not memorable, add more chaptering, more subsystem arcs, and more pressure-loop summaries.
