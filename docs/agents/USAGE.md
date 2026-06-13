# Using the Arcwright Agents and Skills

A practical, click-by-click guide to the roles wired up by specs 0019 and 0021. It is written for the **client apps** (the Claude desktop app, the Codex app, and VS Code with GitHub Copilot). The command line is mentioned only where it is the only or the best option, and those spots are clearly marked **CLI**.

If you read nothing else, read these three lines:

- To run a role, open the app, click the chat box, type `/`, and pick the command from the menu.
- To get the next task, ask the **Planner**; to build it, run the **Implementer**; to check it, run the **Reviewer**.
- To change how any role behaves, edit the canonical file in `docs/skills/` or `docs/agents/`, never the per-app launcher.

---

## Part 1: Words you need (plain English)

- **Skill**: a saved capability you trigger by typing a slash command, for example `/implement`. In the Claude app the skills are `/implement`, `/review-pr`, and `/scribe`. Think of a skill as a labeled button that loads a set of instructions.
- **Subagent (Claude app) or custom agent (Copilot)**: a named helper with its own job and its own limited tools, for example **Implementer** or **Reviewer**. You can pick it from a menu and talk to it directly.
- **Thinking role**: a role you talk to in the **Claude.ai Project chat** by name (Product Steward, Business Steward, System Architect, Planner, Spec Author, Scribe). These have no buttons; you invoke them by asking.
- **Canonical contract**: the single real instruction file each launcher points at, under `docs/skills/` or `docs/agents/`. The launchers are thin on purpose.

The pipeline the roles follow:

```
Intent gate: Product Steward + Business Steward + System Architect agree on a go
  -> Planner: picks and sequences the next task, gives it an AW-NNN id
  -> Spec Author: writes docs/specs/NNNN with acceptance criteria
  -> Implementer: branch, code, open a pull request (PR)
  -> Reviewer: gates the PR
Scribe records decisions and outcomes the whole way.
```

---

## Part 2: One-time setup (do this in each app, once)

The role files load when the app starts and reads the project. After the project's `main` branch changes, refresh:

- **Claude app**: make sure the app has the latest project files, then start a new chat (or reopen the project). New skills and subagents appear after a fresh start.
- **Codex app**: reopen the project, or start a new session.
- **VS Code (Copilot)**: open the Command Palette (View menu, or Ctrl+Shift+P), type "Developer: Reload Window", press Enter.

If a command, skill, or agent does not appear, this refresh is almost always the fix.

**CLI (only if your app does not auto-sync the repo):** in a terminal at the project folder, run `git pull`. Most app users can skip this; the app handles it. GitHub Desktop is a GUI alternative if you prefer not to use a terminal.

---

## Part 3: Claude desktop app (your main tool)

### 3a. How to run a skill (the slash menu)

1. Open the project in the Claude app and start a chat.
2. Click into the message box at the bottom.
3. Type a single forward slash `/`. A menu pops up listing available commands and skills.
4. Click the one you want, or keep typing to filter (for example type `imp` to find `implement`).
5. Add your input after the command, then send.

That is the whole mechanism. The three skills you will use most:

- **`/implement`**: builds one task end to end. Example: type `/implement AW-130` and send. It reads the canonical Implementer contract (`docs/skills/github-task-implementer/SKILL.md`), then shows you a short plan and waits. Read the plan, and if it looks right, reply "approved" (or tell it what to change). It then creates a branch, writes the code and tests, runs checks, and opens a PR. You do not type any git commands.
- **`/review-pr`**: checks a change or PR against the review checklist. Example: type `/review-pr` and send (optionally name a PR). It reports a clear pass or block with evidence. Use `/review-pr`, not `/review`; `/review` is a built-in that does something else.
- **`/scribe`**: records a decision. Example: `/scribe we chose Postgres over SQLite because we need pgvector`. It writes or updates an ADR for you.

### 3b. How to use the subagents (Implementer, Reviewer)

You usually do not need to pick them by hand; the slash commands above already use them. But if you want to talk to one directly:

1. In the message box, type `/agents` and send. You will see **implementer** and **reviewer** listed.
2. To use one, just ask in plain language, for example: "Use the reviewer subagent to review my current changes." The app routes the work to that helper, which loads its canonical contract and reports back.

The **Reviewer** is read-only by design: it inspects and reports, it does not edit your files.

### 3c. Asking architecture questions (the SME)

For "how does this work" or "what does the architecture say" questions, just ask in a normal chat. The Architecture SME knowledge (`docs/skills/arcwright-sme`) is available, and answers are grounded in the project's `docs/` folder with file references. Example: "What does the architecture say about the knowledge graph, and which file?"

### 3d. Approving plans and finishing

- When the Implementer shows a plan, nothing is written yet. Reply "approved" to proceed, or give corrections.
- When it finishes, it gives you a PR link.
- **To review and merge the PR, use the GitHub website (GUI):** open the PR link, read the "Files changed" tab, and click the green **Merge** button when you are satisfied. This is the easiest path and needs no terminal. GitHub Desktop also works.
- **CLI (optional):** the agent can also merge for you if you ask it to; that runs `gh pr merge` under the hood. Use this only if you prefer not to open the website.

---

## Part 4: Codex app

### 4a. See the skills

In a Codex chat, type `/skills` and send. You should see three: `github-task-implementer`, `arcwright-reviewer`, `arcwright-sme`.

### 4b. Run a skill

Reference a skill with a dollar sign and its name, in plain language:

- Implement: "Use $github-task-implementer to implement AW-130." Approve its plan when asked.
- Review: "Use $arcwright-reviewer to review the open PR."
- Ask the SME: "Use $arcwright-sme: which component owns killer assignment?"

Each skill points Codex at the same canonical contract Claude uses, so the behavior matches. The project rules in `AGENTS.md` are always applied automatically; you do not load them.

---

## Part 5: VS Code with GitHub Copilot

VS Code is the client app here; no terminal needed for the roles.

### 5a. Pick a role from the dropdown

1. Open the Copilot Chat panel (the chat icon in the left sidebar, or View menu, then Chat).
2. At the top of the chat input there is a **mode or agent dropdown**. Click it.
3. Choose **Implementer**, **Reviewer**, or **Arcwright SME**.

### 5b. Run the prompts

Alternatively, in the Copilot Chat box type `/` and pick:

- **`/implement-task`**: then describe the task (for example "implement AW-130"). Approve its plan.
- **`/review-pr`**: reviews the current change set or PR.

### 5c. The Implementer to Reviewer handoff

When you are in the **Implementer** agent and a PR is ready, it shows a **"Hand off to Reviewer"** action. Click it to switch to the Reviewer agent with the right prompt already filled in.

### 5d. Automatic guardrails (nothing to click)

- When you edit any file under `engine/` or `api/`, Copilot automatically loads the five engine rules from `.github/instructions/engine.instructions.md`.
- When Copilot reviews a PR on GitHub, it automatically uses `.github/copilot-instructions.md` (a full copy of the project rules). You do not invoke either.

---

## Part 6: The thinking roles (Claude.ai Project chat)

These run in the **Project chat**, not in a coding app, and you invoke them by name. They read their contract from the repo.

- "Act as the **Product Steward** (`docs/agents/product-steward.md`): is feature X in MVP scope?"
- "Act as the **Business Steward** (`docs/agents/business-steward.md`): is X worth building now?"
- "Act as the **System Architect** (`docs/agents/system-architect.md`): decide the approach for X and draft the ADR."
- "Act as the **Planner** (`docs/agents/planner.md`): what is the next task, and how should it be sequenced?"
- "Act as the **Spec Author** (`docs/agents/spec-author.md`): write the spec for AW-NNN."
- "Act as the **Scribe** (`docs/agents/scribe.md`): record this decision as an ADR."

The first three form the **intent gate**: get their shared go before any building. The System Architect **decides** the design and owns the ADR; the SME only **informs**.

Use [`docs/agents/expert-personas.md`](expert-personas.md) as advisory lenses when a question benefits from product, narrative, developer-stakeholder, architecture, or CEO-advisor critique. Personas inform the roles above; they do not replace role authority or create approved product scope.

### Getting the next task before the Implementer

Ask the **Planner** for the next task and its AW-NNN id. The **Spec Author** then makes sure that task has a spec. Only then do you run the Implementer. For a quick "what is next" lookup, you can also ask the **Architecture SME**, which reads `docs/roadmap/index.json`.

---

## Part 7: A full task, start to finish (client-first)

1. **Project chat:** Product Steward confirms scope, Business Steward confirms it is worth it, System Architect approves the approach. Planner gives it `AW-130`. Spec Author writes the spec.
2. **Build it in your coding app**, approving the plan first:
   - Claude app: `/implement AW-130`
   - Codex app: "Use $github-task-implementer to implement AW-130"
   - VS Code Copilot: pick the Implementer agent, or run `/implement-task`, then describe AW-130
3. **Review it:**
   - Claude app: `/review-pr`
   - Codex app: "Use $arcwright-reviewer to review the PR"
   - VS Code Copilot: use the "Hand off to Reviewer" action, or pick the Reviewer agent, or run `/review-pr`
4. **Merge it on the GitHub website:** open the PR, check "Files changed", click **Merge**.
5. **Record it:** in the Claude app, `/scribe` the decision if it was significant.

---

## Part 8: When you actually need the command line

You can do almost everything from the apps. Reach for the CLI (or GitHub Desktop) only here:

- **Getting the latest code** if your app does not auto-sync: `git pull` in the project folder. GitHub Desktop's "Pull" button does the same with no typing.
- **Merging from the terminal** if you do not want to use the GitHub website: ask the agent to merge, or run `gh pr merge <number> --squash`. The website Merge button is usually easier.
- **Branch cleanup** of old local branches: this is optional housekeeping. Ask the agent to do it, or use GitHub Desktop.

Day to day, the agents run all the git work (branching, committing, opening PRs) for you. You mainly approve plans and click Merge.

---

## Part 9: Troubleshooting

- **A command, skill, or agent is missing:** refresh the app (Part 2). They load at startup.
- **`/review` did something unexpected in the Claude app:** use `/review-pr` instead. `/review` is a built-in.
- **Copilot review seems to ignore the rules:** it reads `.github/copilot-instructions.md` (a copy of the rules), not `AGENTS.md`. The copy is kept in sync; if someone edits `AGENTS.md`, the copy must be updated too.
- **Codex does not list a skill:** confirm the project is fully synced and start a new session. The rules still apply through `AGENTS.md` regardless.
- **Golden rule:** to change how a role behaves, edit the canonical file in `docs/skills/` or `docs/agents/`, never the per-app launcher. One edit updates every app.
