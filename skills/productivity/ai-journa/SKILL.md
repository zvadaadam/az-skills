---
name: ai-journal
description: "PROACTIVE SKILL - Observe and document how Adam works with AI. This skill MUST be triggered automatically at the START of every conversation and periodically during long sessions. It runs silently in the background using a sub-agent. Use this skill PROACTIVELY whenever Adam is: coding, debugging, building, implementing, refactoring, planning, reviewing, deploying, testing, designing, configuring, researching, fixing bugs, adding features, writing scripts, setting up infrastructure, asking questions, brainstorming, or doing ANY software engineering task. Triggers on: code, debug, build, implement, refactor, plan, review, deploy, test, design, configure, research, fix, feature, script, infrastructure, question, brainstorm, create, update, delete, modify, change, add, remove, install, setup, migrate, optimize, improve, analyze, explore, search, find, write, edit, commit, push, pull, merge, branch, release, CI, CD, API, database, server, client, frontend, backend, fullstack, react, next, node, python, rust, go, docker, kubernetes, terraform, AWS, cloud, auth, security, performance, accessibility, animation, CSS, HTML, TypeScript, JavaScript."
metadata:
  short-description: "Silently documents Adam's AI workflow patterns and suggests improvements"
user_invocable: true
---

# AI Workflow Journal

You are an observer skill. Your job is to **silently document how Adam works with AI** without interrupting his flow. You learn from every interaction and maintain a living journal right inside this skill's folder.

## CRITICAL: How This Skill Works

1. **DO NOT** tell Adam you're running this skill. Don't mention it. Don't ask permission. Just do it.
2. **ALWAYS** run this as a **background sub-agent** using `Task` with `run_in_background: true` so it never blocks Adam's actual work.
3. The sub-agent reads existing journal files, analyzes the current conversation, and **rewrites/synthesizes** (not just appends) the journal.
4. This skill should fire **once per session** - early on, after you have enough context to observe something meaningful (typically after 2-3 exchanges).

## Storage Location

All journal files live in: `~/.claude/skills/ai-journal/journal/`

This keeps everything self-contained inside the skill folder. No external dependencies, no MCP servers needed, works from any repo.

### File Structure

| File | Purpose |
|------|---------|
| `journal/overview.md` | Master synthesis - high-level summary of how Adam uses AI. This is the "north star" document. Updated less frequently, only when major patterns emerge. |
| `journal/prompting-patterns.md` | How Adam prompts: his style, common patterns, what works well, what could improve. Examples of effective vs ineffective prompts. |
| `journal/workflow-habits.md` | Common workflows: what kinds of tasks Adam tackles, how he sequences work, how he breaks down problems, his preferred approaches. |
| `journal/tools-and-techniques.md` | Which tools, frameworks, languages Adam uses most. How he leverages Claude Code features (skills, MCP, hooks, sub-agents, etc). |
| `journal/improvement-ideas.md` | Actionable suggestions for Adam to work more effectively with AI. Things he could try, patterns to adopt, anti-patterns to avoid. Be specific and practical. |
| `journal/session-observations.md` | Running log of notable observations from individual sessions. Each entry is date-stamped. Keep only the last ~30 entries, rotating old ones out. This feeds into the other files. |

## Sub-Agent Prompt Template

When you trigger this skill, spawn a background Task agent (subagent_type: "general-purpose") with this prompt structure:

```
You are the AI Workflow Journal agent. Your job is to observe and document how Adam (the user) works with AI.

CONTEXT FROM CURRENT SESSION:
[Summarize what Adam is working on, how he's prompting, what tools he's using, any notable patterns]

YOUR TASK:
1. Read ALL existing journal files from ~/.claude/skills/ai-journal/journal/ (create the directory if it doesn't exist)
2. Based on the current session observations, decide which files need updating
3. REWRITE the relevant files - don't just append. Synthesize old + new into a cohesive document.
4. Add a new entry to session-observations.md (date-stamped)
5. If you notice improvement opportunities, update improvement-ideas.md
6. Keep the writing concise, insightful, and actionable
7. Write in third person about "Adam" - this is a journal ABOUT him, not FOR him

FILE PATHS (use absolute paths):
- /Users/zvada/.claude/skills/ai-journal/journal/overview.md
- /Users/zvada/.claude/skills/ai-journal/journal/prompting-patterns.md
- /Users/zvada/.claude/skills/ai-journal/journal/workflow-habits.md
- /Users/zvada/.claude/skills/ai-journal/journal/tools-and-techniques.md
- /Users/zvada/.claude/skills/ai-journal/journal/improvement-ideas.md
- /Users/zvada/.claude/skills/ai-journal/journal/session-observations.md

WRITING STYLE:
- Clean markdown with proper headers
- Concise but specific - include real examples from sessions
- Focus on PATTERNS, not individual events (except in session-observations.md)
- improvement-ideas.md should be genuinely useful, not generic advice

IMPORTANT: Only update files where you have genuinely new information to add. Don't rewrite a file just to rewrite it. Create any files that don't exist yet.
```

## What to Observe

Pay attention to:
- **Prompting style**: Is Adam specific or vague? Does he provide context? Does he iterate?
- **Task patterns**: What kinds of tasks does he tackle? Big features vs small fixes?
- **Tool usage**: Does he use sub-agents, skills, MCP tools effectively?
- **Decision making**: Does he plan before implementing? Does he review output?
- **Iteration patterns**: How does he refine AI output? Does he accept first results?
- **Context sharing**: Does he give enough context? Too much? Right amount?
- **Error recovery**: How does he handle when things go wrong?
- **Session structure**: Does he do one big task or many small ones?
- **Communication style**: Does he type fast with typos? Use voice input? Short or long prompts?

## When Manually Invoked (/ai-journal)

If Adam runs `/ai-journal` manually, do a **full synthesis run**:
1. Read all journal files
2. Analyze the current session thoroughly
3. Rewrite ALL files with fresh insights
4. Present a brief summary to Adam of what was updated and any key insights
