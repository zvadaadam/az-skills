# Principles and source

This skill draws on the full Lauren Tan talk supplied as `BQlPlAZCEVPDemv1.mp4`, approximately 38 minutes, locally transcribed with Whisper. The table paraphrases the recording; timestamps are approximate. Speech recognition can miss names and technical terms, so the transcript is not treated as a publication-quality quotation source.

| Recording | Principle | How the setup skill applies it |
|---|---|---|
| 00:00–04:40 | More agent output moves the bottleneck to trust, review and tribal knowledge. Invest in the working environment. | Inspect where the team repeats explanations or cannot validate changes; choose an actual friction point. |
| 07:05–09:19 | Running the software gives empirical evidence. Formal verification is a distinct, harder technique. | Require observable proof at a named layer; do not make formal methods a setup prerequisite. |
| 09:19–10:16 | Reusable controls in a skill avoid recreating scripts in every conversation. | Promote repeated operations into repository tools and teach the agent their real commands. |
| 10:16–12:29 | A feature map gives agents product knowledge, including how users reach features. | Route vague reports through user language, entry points and repeatable recipes. |
| 12:29–15:05 | Correctness and code quality need complementary workflows. Skills can encode experienced engineering methods. | Keep tests and runtime checks, and add task skills for recurring debugging and development work. |
| 15:05–22:17 | Agents copy the patterns in code. Architecture and automated constraints prevent classes of mistakes more reliably than repeated coaching. | Prefer simplifying a bad state or enforcing a boundary over expanding AGENTS.md. |
| 22:17–26:37 | Gardening keeps problematic patterns from spreading. A guard can stop new debt while old debt is cleaned up. | Improve the path in use and remove obsolete workarounds; avoid an unrelated wholesale rewrite. |
| 26:37–31:26 | Domain and runtime boundaries can encode hard-won knowledge. | Inspect and preserve the repository's own boundaries; do not import the speaker's framework. |
| 31:26–35:17 | Reports, tools and agents can form a useful outer loop once the inner workflow works. | Treat scheduled maintenance and issue automation as later, concrete extensions. |
| 35:17–38:02 | Durable corrections improve future agent work; agent count alone does not create confidence. | Evaluate the complete working loop and where each lesson should live. |

The talk's team-specific examples, including its comment policy and internal framework, are not universal recommendations. Do not copy them without a demonstrated local problem.

The setup sequence, placement table, proof-layer vocabulary, repository guidance contract and acceptance scenarios are this skill's synthesis. They are not presented as the speaker's exact system. `verify-harness` is a separate, more detailed verification skill; it also credits Lauren's pstack work and distinguishes later extensions.

The supplied recording and full local transcript remain working evidence under `.context/verification-video/` in the authoring workspace. Consumers of this skill do not need access to them to follow it. The skill does not redistribute the video or install a particular framework.
