# Aha moment extraction heuristics

Use these patterns to infer what the engineers likely learned.

## Strong signals

### Add → fix → revert
This usually means the team discovered hidden complexity or a wrong abstraction.

### Same-area burst over 1-3 days
Often indicates a real pain loop: release breakage, packaging mismatch, race condition, billing bug, parser issue, etc.

### Delete a whole subsystem
This is usually a strategic learning moment, not cleanup.

### New tests / CI / compliance after instability
Often means the team was burned by something and institutionalized the lesson.

### Rename + docs refresh + marketing copy change
Often signals a thesis clarification or repositioning.

### Installer / bundle / release work dominating feature work
Usually means distribution has become part of the architecture.

### Public legal/docs/papers appear late
Often means the team is shifting from experiment to something more legible, credible, or externally facing.

## Language to use

Prefer:
- "This suggests…"
- "A likely lesson is…"
- "The pattern implies…"

Avoid:
- "They definitely realized…"
- "The founders believed…" without direct evidence
