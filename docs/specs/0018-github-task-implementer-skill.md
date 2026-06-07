# GitHub Task Implementer Skill

**Status**: Draft

**Author**: Codex | **Date**: 2026-06-06

---

# References

- Related docs: `docs/13-AI-Development-Workflow-v1.md`, `AGENTS.md`, `CLAUDE.md`
- Related conventions: `docs/conventions/ai-contributions.md`
- Related template: `docs/specs/0000-template.md`

---

# Overview

Add a repo-tracked, platform-agnostic skill that teaches an AI coding agent how to take one GitHub issue, task, or story from initial read-through through PR handoff without drifting outside the ticket contract.

---

# In Scope

- Add a tracked skill at `docs/skills/github-task-implementer/`
- Keep the main workflow in plain Markdown so Codex, Claude Code, and other AI coding agents can use the same file path
- Encode the required task loop:
  - read issue plus linked docs
  - inspect repo state and prerequisites
  - send plan and wait for approval
  - implement only approved scope
  - run checks
  - report acceptance criteria one by one
  - handle review comments
  - perform post-merge cleanup only after merge
- Add minimal Codex metadata in `agents/openai.yaml`
- Add at most one lightweight reference file if it materially reduces repeated prompt text

---

# Out of Scope

- Live GitHub automation scripts
- Repo-wide workflow rewrites outside the new skill and its supporting spec
- Platform-specific dependencies or tools that make the skill unusable in another AI environment
- General project management guidance unrelated to implementing a single GitHub work item

---

# Acceptance Criteria

- [ ] Repo contains a tracked skill at `docs/skills/github-task-implementer/` with `SKILL.md`
- [ ] The `SKILL.md` workflow is platform-agnostic and directly usable by Codex and Claude Code
- [ ] The skill requires reading the full issue, linked docs, and current repo state before implementation
- [ ] The skill requires a plan-and-approval gate before code changes
- [ ] The skill enforces scope control, prerequisite verification, and conflict detection
- [ ] The skill requires explicit acceptance-criteria reporting and check results at completion
- [ ] The skill covers review-comment follow-up and post-merge cleanup
- [ ] `agents/openai.yaml` is valid and references `$github-task-implementer`
- [ ] `python C:\\Users\\nicke\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py docs\\skills\\github-task-implementer` passes

---

# Test Plan

- Validation: run the skill validator against `docs/skills/github-task-implementer`
- Manual review: read `SKILL.md` and confirm the workflow can be followed without Codex-only features
- Manual review: compare the skill guidance against `docs/13-AI-Development-Workflow-v1.md`, `AGENTS.md`, and `CLAUDE.md`

---

# Risks and Unknowns

**Risks**:
- If the skill leans too hard on Codex metadata, Claude Code and other agents will not be able to use it directly.
- If the skill is too verbose, users will paste shorter ad hoc prompts instead of reusing it.
- If the skill resolves instruction conflicts silently, it will create ticket drift instead of preventing it.

**Unknowns**:
- Whether future repos will want a different branch naming convention. The skill should treat repo rules as higher priority than the default examples here.

---

# Open Questions

- None after user approval to create a tracked, cross-platform skill in the repo.
