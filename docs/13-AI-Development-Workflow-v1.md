# 13-AI-Development-Workflow-v1

**Version:** 1.0
**Date:** May 2026
**Status:** New artifact.
**Purpose:** Everything you need to run the AI-assisted development loop from first ticket through milestone completion. Reference this doc whenever you are starting a new epic, handing a task to an agent, or onboarding into a new chat session.
**Companion artifacts:** 12-Build-Roadmap-v1.1, 12b-GitHub-M1-Epic-A-Setup

---

## 1. The System in One Page

Three tools do three different jobs.

**This Project (Claude, chat interface):** Strategic decisions, architecture, and decomposition. You come here to break milestones into epics and epics into agent-ready task specs. You also come here when a coding decision affects architecture or strategy and needs to be logged.

**AI coding agents (Claude Code, Codex, Copilot):** Execution. You hand an agent one task at a time using the handoff template in Section 4. The agent reads the issue, reads the referenced docs, implements the acceptance criteria, and delivers a PR.

**GitHub Projects + Issues:** The tracker. Epics are parent issues. Tasks are sub-issues. Status moves through Backlog, In Progress, In Review, Done. The roadmap and the tracker stay in sync because you update both when things change.

The maintenance rule that holds everything together: keep 12-Build-Roadmap and the Decisions Log current in the repo after every epic closes and after every significant decision. The next chat in this Project reads those files as its source of truth.

---

## 2. The Full Build Loop

This is the rotation. Follow it from the first ticket to the last milestone.

```
1. Open epic in GitHub
      |
2. Hand first task to agent (Claude Code / Codex / Copilot)
      |
3. Agent delivers PR
      |
4. Review: run acceptance criteria yourself, read the diff
      |
      +--> Issues found: send output back to agent, ask for fix
      |
      +--> Clean: merge PR, close issue, mark Done in Project
      |
5. Repeat steps 2-4 for each remaining task in the epic
      |
6. All tasks merged: verify epic exit criteria
      |
      +--> Not met: open a new task for what is missing
      |
      +--> Met: close the epic issue
      |
7. Update 12-Build-Roadmap in repo (mark epic done)
   Log any significant decisions made during the epic
      |
8. Open a new chat in this Project
   Use the decomposition prompt (Section 3) to get the next epic
      |
9. Repeat from step 1
```

When all epics in a milestone are closed and the milestone exit criteria are met, the decomposition prompt in the new chat asks for the next milestone instead of the next epic.

---

## 3. Working With Claude in This Project

### When to open a new chat

Open a new chat in this Project when:
- An epic is complete and you need the next one decomposed into task specs
- A milestone is complete and you need the next milestone broken into epics and first-epic tasks
- A significant architectural or strategic question has come up during the build that needs resolution before you continue

Do not open a new chat for individual tickets. Those go to Claude Code using the handoff template in Section 4.

### Why new chats work here

This Project retains project knowledge between chats. As long as the roadmap and decisions log files in the repo are current, a new chat has everything it needs. Long chats degrade context quality. A fresh chat with current project knowledge is more reliable.

### Epic decomposition prompt

Use this when one epic is done and you need the next one. Paste it into a new chat in this Project.

```
[EPIC NAME] is complete. I need [NEXT EPIC NAME] decomposed 
into agent-ready GitHub issue specs.

Read 12-Build-Roadmap from project knowledge for current 
state. Read the Technical Architecture for the sections 
referenced in [NEXT EPIC NAME].

If anything about the current state, the epic scope, or the 
referenced doc sections is unclear, ask me in a single 
message before producing specs.

Produce the task specs in the same format as prior epics. 
Note anything that changed during [COMPLETED EPIC NAME] work 
that affects how [NEXT EPIC NAME] should be approached.
```

Example filled in:

```
M1 Epic A is complete. I need M1 Epic B decomposed into 
agent-ready GitHub issue specs.

Read 12-Build-Roadmap from project knowledge for current 
state. Read the Technical Architecture for the data model 
sections referenced in Epic B (AW-103 and AW-104).

If anything about the current state or how Epic A work 
affects Epic B is unclear, ask me in a single message 
before producing specs.

Produce the task specs in the same format as Epic A. Note 
anything that changed during Epic A work that affects how 
Epic B should be approached.
```

### Milestone decomposition prompt

Use this when all epics in a milestone are done and exit criteria are met.

```
[MILESTONE NAME] is complete. I need [NEXT MILESTONE NAME] 
decomposed into epics and the first epic broken into 
agent-ready task specs.

Read 12-Build-Roadmap and the Technical Architecture. Note 
any decisions made during [COMPLETED MILESTONE] that affect 
[NEXT MILESTONE] design.

If anything about the milestone scope or decisions made 
during [COMPLETED MILESTONE] is unclear, ask me in a single 
message before producing specs.

Produce the epic structure for [NEXT MILESTONE] and full 
task specs for the first epic.
```

### Bringing architecture decisions back here

When an agent makes a structural decision during execution that was not in the issue spec, and it affects the architecture or strategy, bring it back to this Project chat before moving on. Provide:
- What the agent decided
- Why (the agent's reasoning if it explained it)
- What you want: confirm it, reverse it, or log it as-is

I will produce the Decisions Log entry and flag any roadmap or architecture doc that needs updating.

---

## 4. Working With AI Coding Agents

### The universal handoff template

Paste this into Claude Code, Codex, or Copilot at the start of any task. Replace the bracketed values.

```
Work on the task described in GitHub Issue #[N]: [AW-XXX title].

Before writing any code:
- Create a branch as the first action before touching any files:
  `git checkout -b task/AW-[N]-brief-description`
  Replace [N] with the issue number and brief-description with 
  2-3 words from the task title. Example: `task/AW-101-repo-setup`
- Read the full issue body for the spec, acceptance criteria, 
  and anti-requirements
- Read the repo sections referenced in "Implements:"
- Run `ls` and inspect any files relevant to this task so you 
  understand current state before touching anything

After reading, if anything in the spec, acceptance criteria, 
or referenced docs is unclear, ask me now in a single message 
before writing any code.

Implement the acceptance criteria exactly. Do not implement 
anything not in the spec. If you hit a decision point the spec 
does not cover mid-implementation, stop and ask rather than 
guessing.

When done, confirm each acceptance criterion is met. Commit 
your work with a message that references the issue number 
(include `Closes #[N]` so GitHub closes it on merge), push 
the branch, and open a PR with the issue title as the PR title. 
List which acceptance criteria pass in the PR description.
```

### First task (AW-101) specific prompt

Use this for AW-101 only, since prior scaffolding may already exist.

```
Work on the task described in GitHub Issue #[your AW-101 issue 
number]: AW-101: Repository structure and Python project setup.

Before writing any code:
- Create a branch as the first action:
  `git checkout -b task/AW-101-repo-setup`
- Read the full issue body
- Read docs/07-Technical-Architecture at sections S2.3 and S2.4
- Run `ls -la`, `find . -name "pyproject.toml"`, and inspect any 
  existing package structure so you know exactly what already 
  exists before creating anything. An AI spine may already be 
  present.

After inspecting the repo, if anything about the existing 
structure or the acceptance criteria is unclear, ask me in 
a single message before writing any code.

Implement the acceptance criteria exactly. Do not touch the AI 
spine or any existing engine work. If you find something already 
in place that satisfies a criterion, note it and move on rather 
than replacing it.

When done, confirm each acceptance criterion is met and note 
anything you found already in place. Commit with a message 
that includes `Closes #[N]`, push the branch, and open a PR.
```

### Branch and commit conventions

Every task gets its own branch. Agents never commit directly to main.

**Branch naming:** `task/AW-[N]-brief-description`
Use the issue number and 2-4 words from the task title, lowercase, hyphens only.
Examples: `task/AW-101-repo-setup`, `task/AW-105-knowledge-graph`, `task/AW-107-routing-layer`

**Commit messages:** First line is a concise description (72 chars max). Include `Closes #[N]` so GitHub automatically closes the issue when the PR merges. If the commit is partial work on a task, use `Refs #[N]` instead.
Examples:
- `feat: scaffold engine and api packages (Closes #12)`
- `feat: postgres + pgvector + alembic init (Closes #13)`

**PR format:** Title matches the issue title. Body lists which acceptance criteria pass. Link the issue by including `Closes #[N]` in the PR description if not already in the commit.

**One branch per task.** Do not combine two tasks on one branch even if they are in the same epic. The review loop depends on one task per PR.

### The review loop

When the agent delivers a PR, do these three things before merging:

**Run the acceptance criteria yourself.** Do not take the agent's word for it. `make lint`, `make type`, `make test` should all pass. If they do not, send the full error output back to the agent verbatim and ask it to fix it. Do not paraphrase errors.

**Read the diff.** Not every line, but enough to confirm the agent did not touch things outside the issue scope. If it wandered into files not mentioned in the spec, ask why before merging.

**Close the issue and queue the next task.** Mark the completed task Done in the GitHub Project. Mark the next task in the epic `agent-ready`. Hand it using the universal template.

### Four things that matter when working with AI agents

**One task at a time.** Do not stack two tasks in one prompt. The agent will blend them and the output is harder to review and harder to attribute to a single issue.

**The spec is the contract.** If the issue says do X, the agent does X. If you want something different, update the issue first, then hand it. Verbal overrides mid-session create drift that is hard to track.

**Feed errors verbatim.** When tests or lint fail, paste the raw output back. Agents fix error output better than they fix vague descriptions of what went wrong.

**Flag unexpected structural decisions immediately.** If the agent picks a different library, restructures a package, or makes an architectural call not in the spec, stop and bring it to this Project chat. Small decisions accumulate into large drift if they are not tracked.

### Which agent for which work

**Claude Code (terminal):** Best for agentic tasks that require reading files, running commands, and writing code across multiple files. Use for most AW-xxx tasks.

**Copilot (inline):** Best for autocomplete and single-file edits. Less suited for multi-file agentic tasks with spec-based acceptance criteria.

**Codex:** Good for structured tasks with explicit specs. Works well with the handoff template format.

---

## 5. GitHub Project Workflow

### Creating a new epic and its tasks

1. Create the parent epic issue. Title format: `[Epic] M[N]-[Letter]: [Epic Name]`. Add the `epic` label and assign to the correct milestone.
2. Create each task issue using the spec from the roadmap. Title format: `AW-XXX: [Task Title]`. Add `task`, `size:S/M/L`, the milestone label. Do not add `agent-ready` yet.
3. Open the parent epic issue, scroll to Sub-issues, and add each task as a sub-issue.
4. Add both the epic and its sub-issues to the Arcwright Build Project.

### The agent-ready label

`agent-ready` means the task is fully spec'd and the agent can execute it right now without additional input from you. Only add it to the task that is currently up next. Do not mark future tasks `agent-ready` in advance.

When you hand a task to an agent, move it to In Progress in the Project board. When the PR merges, move it to Done and close the issue.

### Epic exit criteria

Before closing an epic issue, verify every item in the epic's exit criteria checklist. If a criterion is not met, open a new task for the gap. Do not close the epic until the criteria are genuinely satisfied.

### Milestone exit criteria

Before moving to the next milestone, verify the milestone exit criteria in 12-Build-Roadmap. These are harder gates than individual task acceptance criteria. If anything is unmet, it needs a task before you start the next milestone, not a plan to fix it later.

---

## 6. Incorporating New Docs Into the Repo

When new artifacts are produced (updated roadmap, new specs, decisions log additions), use these prompts to hand the integration work to an agent.

### Prompt A: Planning and roadmap documents

```
Read the file [FILENAME]. This is [brief description of what 
the doc is].

Before doing anything, inspect the repo structure. Read any 
README, CONTRIBUTING, or docs-related files you find. Also 
check the .github/ folder and any existing issue templates. 
The GitHub Project, milestones, labels, and current issues 
are already live.

Then decide: where should this document live in the repo, in 
what format, and how should it be structured so that you as 
an AI agent can find and use it efficiently when you are 
handed individual tasks? Consider whether it should stay as 
one file or be split, whether the format should change, 
whether any part should be more machine-readable or queryable, 
and whether it should cross-reference the live GitHub 
milestones and issues by number or URL.

If anything about the doc's purpose or how it relates to 
existing repo content is genuinely unclear from reading the 
files, ask me in a single message before implementing. Do not 
ask about structural decisions you should simply make yourself 
based on what you find in the repo.

Explain your reasoning briefly, then implement your decision. 
If you touch any existing files, explain what you changed 
and why.
```

### Prompt B: GitHub configuration and tracker setup

```
Read the file [FILENAME]. The GitHub Project, milestones, 
labels, epic, and task issues described in that file have 
already been created manually. The setup is live.

Before doing anything, inspect the repo. Check .github/ for 
any existing issue templates, label configs, or workflow 
files. Understand what, if anything, was auto-generated or 
is already captured there.

Then decide two things:

First, is the current GitHub setup reproducible from the 
repo? If someone had to recreate this GitHub Project from 
scratch, could they do it from what is in the codebase? If 
not, decide the best way to capture it: issue templates, a 
labels config file, a setup script, or some other format 
that fits how this repo is organized. Implement whatever 
you decide.

Second, what should happen to [FILENAME] now that the setup 
is done? Archive it, reference it, remove it, or leave it 
as-is, based on what serves the repo best.

If anything about the existing setup or what needs to be 
captured is genuinely unclear from reading the repo, ask me 
in a single message before implementing. Do not ask about 
decisions you should simply make yourself.

Explain your reasoning briefly, then implement your decisions.
```

### Prompt C: Decisions log additions

```
Read the file [FILENAME]. It contains new entries that need 
to be merged into the project's Decisions Log, which already 
exists somewhere in this repo.

Before doing anything, find the existing Decisions Log. 
Understand its current format, structure, and location.

Then decide the best way to merge these entries: whether to 
append them as-is, reformat them to match the existing log, 
or restructure the log itself if the current format is not 
serving development well. Consider whether the format makes 
the log accessible and useful to you as an AI agent when you 
need to understand past decisions during a task.

Append-only rule: do not edit or remove any existing entries. 
New entries are additions only.

If anything about the existing log format or how the new 
entries should be merged is genuinely unclear, ask me in a 
single message before implementing.

Explain your reasoning briefly, then implement your decision.
```

---

## 7. Maintenance Rules

These are the rules that keep the system working across chats and agents. If you skip them, the next chat or agent starts from stale context and produces worse output.

**After every epic closes:** Update 12-Build-Roadmap in the repo to mark the epic done. Commit it before opening the next decomposition chat.

**After every significant coding decision:** Add an entry to the Decisions Log. Use this Project chat to produce the entry if you want help formatting it. Decisions are append-only.

**After every milestone:** Verify the milestone exit criteria are genuinely met before the next decomposition chat. The exit criteria in the roadmap are the bar, not your subjective sense that things are working.

**When the roadmap changes:** If a milestone scope shifts, an epic is added or removed, or a task's acceptance criteria change because of something you learned during the build, update the roadmap file in the repo before the next decomposition session. Do not let the file drift from reality.

**When the external game platform is decided:** M4 task decomposition is currently deferred because the game UI platform is not yet named. As soon as that decision is made, log it in the Decisions Log and bring it to a new chat here to decompose M4 properly. Do not wait until M3 is closing to make this decision.

---

*New artifact, May 2026. Canonical name in repo: 13-AI-Development-Workflow. This doc is operational guidance, not a planning artifact. It describes how to run the build, not what to build. For what to build, see 12-Build-Roadmap. For why decisions were made, see 02-Decisions-Log.*
