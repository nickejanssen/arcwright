# Human Collaboration Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce interview-first, phased founder collaboration across Arcwright, retrofit current canonical work, synchronize live GitHub issues, and reset PR #243 to an honest pre-approval state.

**Architecture:** Implement in three merge-gated waves. Wave 1 establishes the global contract and role enforcement. Wave 2 begins only after Wave 1 merges and adds explicit collaboration profiles to current canonical tasks and specs. Wave 3 begins only after Wave 2 merges, mirrors canonical text to GitHub, and corrects PR #243 without inventing art direction.

**Tech Stack:** Markdown, Python 3.11 standard library, Git, GitHub Issues and pull requests, GitHub Actions YAML, PowerShell.

**Execution choice:** Inline execution with `superpowers:executing-plans`, as
selected by the founder. Do not dispatch subagents for this plan.

## Global Constraints

- Work from isolated branches or worktrees. Never implement on `main`.
- Update canonical repo documents before GitHub issue bodies.
- Do not advance a later wave until the preceding wave is merged to `main`.
- Continue reversible research when founder input is unavailable, then stop before making choices.
- Ask one focused question at a time and prefer interactive multiple-choice controls when supported.
- Treat plan approval, direction approval, artifact approval, phase go-ahead, final sign-off, and durable decision recording as separate approvals.
- Never infer founder approval from silence, PR creation, review activity, or general plan approval.
- Do not discard useful PR #243 research, but do not treat it as founder direction.
- Add no runtime dependency and change no engine, API, SDK, schema, migration, prompt, eval, routing, safety, or product behavior.
- Preserve Python authority, deterministic state, knowledge gating, surface agnosticism, privacy, provider agnosticism, and cost-aware routing.
- Do not create, modify, stage, commit, or delete agent-local files.
- Do not hardcode secrets or API keys.
- Do not use em dashes in created or modified files.
- Use conventional commit messages.

---

## File Structure

### Wave 1: Global contract

- Create: `docs/conventions/human-collaboration.md`
- Create: `scripts/verify_human_collaboration.py`
- Modify: `AGENTS.md`
- Modify: `.github/copilot-instructions.md`
- Modify: `.github/workflows/verify-tasks.yml`
- Modify: `docs/conventions/ai-contributions.md`
- Modify: `docs/conventions/review-checklist.md`
- Modify: `docs/agents/README.md`
- Modify: `docs/agents/product-steward.md`
- Modify: `docs/agents/business-steward.md`
- Modify: `docs/agents/system-architect.md`
- Modify: `docs/agents/planner.md`
- Modify: `docs/agents/spec-author.md`
- Modify: `docs/agents/scribe.md`
- Modify: `docs/agents/USAGE.md`
- Modify: `docs/skills/github-task-implementer/SKILL.md`
- Modify: `docs/skills/arcwright-reviewer/SKILL.md`
- Modify: `docs/specs/0000-template.md`
- Modify: `docs/roadmap/operations/working-model.md`

### Wave 2: Canonical current-work retrofit

- Create: `docs/roadmap/operations/human-collaboration-open-work.md`
- Modify: `scripts/verify_human_collaboration.py`
- Modify task records:
  - `docs/roadmap/tasks/AW-232-adversarial-safety-playtest-protocol.md`
  - `docs/roadmap/tasks/AW-233-safety-findings-remediation.md`
  - `docs/roadmap/tasks/AW-234-gross-margin-by-player-count.md`
  - `docs/roadmap/tasks/AW-235-second-arc-schema-design.md`
  - `docs/roadmap/tasks/AW-236-live-knowledge-graph-inspection.md`
  - `docs/roadmap/tasks/AW-237-read-only-arc-structure-inspection.md`
  - `docs/roadmap/tasks/AW-238-live-event-stream-inspection.md`
  - `docs/roadmap/tasks/AW-239-character-state-inspection.md`
  - `docs/roadmap/tasks/AW-240-closed-playtest-operations-runbook.md`
  - `docs/roadmap/tasks/AW-241-qualifying-session-instrumentation-checklist.md`
  - `docs/roadmap/tasks/AW-242-founder-run-final-rehearsal.md`
  - `docs/roadmap/tasks/AW-243-five-outside-qualifying-sessions.md`
  - `docs/roadmap/tasks/AW-244-h1-proof-analysis-and-next-step-decision.md`
  - `docs/roadmap/tasks/AW-245-second-arc-minimal-executable-product.md`
  - `docs/roadmap/tasks/AW-266-rehearsal-2-tmst-real-human-session.md`
  - `docs/roadmap/tasks/AW-267-nightcap-art-direction-brief.md`
  - `docs/roadmap/tasks/AW-268-nightcap-asset-pipeline-and-motion-system.md`
  - `docs/roadmap/tasks/AW-269-nightcap-cloud-deploy.md`
  - `docs/roadmap/tasks/AW-270-authorial-intent-block-and-fidelity-telemetry.md`
  - `docs/roadmap/tasks/AW-271-narrative-obligations-model.md`
  - `docs/roadmap/tasks/AW-272-continuity-coherence-eval-suite.md`
  - `docs/roadmap/tasks/AW-273-rehearsal-1-execution.md`
  - `docs/roadmap/tasks/AW-274-platform-agnostic-role-outcome-vocabulary.md`
  - `docs/roadmap/tasks/AW-275-design-system-follow-ups.md`
  - `docs/roadmap/tasks/AW-276-arc-voice-block-injection.md`
  - `docs/roadmap/tasks/AW-277-couch-race-narrator-transition-lines.md`
  - `docs/roadmap/tasks/AW-278-couch-race-truth-sequence-and-reveal-accounting.md`
  - `docs/roadmap/tasks/AW-279-detective-identity-and-opening-briefing.md`
  - `docs/roadmap/tasks/AW-280-couch-race-clue-release-content.md`
  - `docs/roadmap/tasks/AW-281-couch-race-arc-definition-and-case-generation.md`
  - `docs/roadmap/tasks/AW-282-interrogation-round-loop-and-question-intents.md`
  - `docs/roadmap/tasks/AW-283-suspect-answer-generation-and-contradiction-detection.md`
  - `docs/roadmap/tasks/AW-284-race-scoring-and-accusation-state.md`
  - `docs/roadmap/tasks/AW-285-couch-race-tv-and-phone-rendering.md`
  - `docs/roadmap/tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md`
- Modify related specs:
  - `docs/specs/0031-aw-245-second-arc-minimal-executable-product.md`
  - `docs/specs/0039-aw-235-daily-case-second-arc-schema-design.md`
  - `docs/specs/0064-aw-270-authorial-intent-block.md`
  - `docs/specs/0065-aw-271-narrative-obligations-model.md`
  - `docs/specs/0066-aw-272-continuity-coherence-evals.md`
  - `docs/specs/0067-development-survey-and-path-to-first-playtest.md`
  - `docs/specs/0068-game-experience-quality-bar.md`
  - `docs/specs/0069-nightcap-visual-design-system.md`
  - `docs/specs/0070-aw-274-platform-agnostic-role-outcome-vocabulary.md`
  - `docs/specs/0072-nightcap-couch-race-v1.md`
  - `docs/specs/0073-aw-276-arc-voice-directive-injection.md`
  - `docs/specs/0073-m5-canonical-reconciliation.md`

### Wave 3: GitHub synchronization and PR #243 reset

- Update live issues: `#85` through `#97`, `#114`, `#138`, `#183` through `#185`, `#188`, `#202` through `#204`, `#207`, `#220`, `#223`, `#226` through `#230`, and `#235` through `#240`.
- Update issue `#184` from the AW-267 canonical task record.
- Convert PR `#243` to draft.
- Update PR `#243` metadata and its branch files:
  - `docs/design/nightcap-art-direction.md`
  - `docs/design/moodboards/high-society.md`
  - `docs/design/moodboards/corporate.md`
  - `docs/design/moodboards/sci-fi.md`
  - `docs/product/decisions-log.csv`

---

### Task 1: Add a failing collaboration-contract verifier

**Files:**
- Create: `scripts/verify_human_collaboration.py`
- Modify: `.github/workflows/verify-tasks.yml:34`

**Interfaces:**
- Consumes: canonical Markdown files and task records from the repository root.
- Produces: `python scripts/verify_human_collaboration.py --phase global|retrofit|all` with exit code `0` on success and `2` on contract violations.

- [ ] **Step 0: Create the Wave 1 isolated worktree**

Invoke `superpowers:using-git-worktrees`, then create the worktree from the
approved design-and-plan branch:

```powershell
git -C 'C:\Users\nicke\OneDrive\Desktop\arcwright' worktree add 'C:\Users\nicke\OneDrive\Desktop\arcwright\.worktrees\human-collaboration-global' -b codex/human-collaboration-global codex/human-collaboration-contract-design
git -C 'C:\Users\nicke\OneDrive\Desktop\arcwright\.worktrees\human-collaboration-global' status --short --branch
```

Expected: the worktree is on `codex/human-collaboration-global`, includes the
approved design and plan, and is otherwise clean.

- [ ] **Step 1: Create the verifier with global and retrofit phases**

Create `scripts/verify_human_collaboration.py` with this structure:

```python
#!/usr/bin/env python3
"""Verify Arcwright's human-collaboration contract and task profiles."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE_HEADING = "# Agent Operating Guide"

GLOBAL_REQUIREMENTS = {
    "docs/conventions/human-collaboration.md": (
        "## Interaction Profiles",
        "## Interview Contract",
        "## Approval Semantics",
        "## Required Phase Gates",
        "## Checkpoint Review Package",
    ),
    "AGENTS.md": ("## Human Collaboration Contract",),
    "docs/conventions/ai-contributions.md": ("human-collaboration",),
    "docs/conventions/review-checklist.md": ("collaboration profile",),
    "docs/agents/README.md": ("Collaboration Intake",),
    "docs/agents/product-steward.md": ("Human Collaboration",),
    "docs/agents/business-steward.md": ("Human Collaboration",),
    "docs/agents/system-architect.md": ("Human Collaboration",),
    "docs/agents/planner.md": ("Human Collaboration",),
    "docs/agents/spec-author.md": ("Human Collaboration",),
    "docs/agents/scribe.md": ("Human Collaboration",),
    "docs/skills/github-task-implementer/SKILL.md": (
        "Classify Human Collaboration",
    ),
    "docs/skills/arcwright-reviewer/SKILL.md": (
        "Verify Human Collaboration Evidence",
    ),
    "docs/specs/0000-template.md": ("# Human Collaboration Contract",),
    "docs/roadmap/operations/working-model.md": ("collaboration profile",),
    "docs/agents/USAGE.md": ("interactive", "numbered-choice fallback"),
}

RETROFIT_REQUIREMENTS: dict[str, tuple[str, ...]] = {}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def instruction_body(text: str) -> str:
    _, marker, body = text.partition(GUIDE_HEADING)
    if not marker:
        return ""
    return marker + body


def check_requirements(
    requirements: dict[str, tuple[str, ...]],
) -> list[str]:
    failures: list[str] = []
    for path, tokens in requirements.items():
        candidate = ROOT / path
        if not candidate.exists():
            failures.append(f"missing file: {path}")
            continue
        content = candidate.read_text(encoding="utf-8")
        for token in tokens:
            if token not in content:
                failures.append(f"{path}: missing token {token!r}")
    return failures


def check_mirror() -> list[str]:
    agents = instruction_body(read("AGENTS.md"))
    copilot = instruction_body(read(".github/copilot-instructions.md"))
    if not agents or not copilot:
        return ["instruction mirror is missing the Agent Operating Guide heading"]
    if agents != copilot:
        return ["AGENTS.md and Copilot instruction bodies differ"]
    return []


def run(phase: str) -> int:
    failures: list[str] = []
    if phase in {"global", "all"}:
        failures.extend(check_requirements(GLOBAL_REQUIREMENTS))
        failures.extend(check_mirror())
    if phase in {"retrofit", "all"}:
        failures.extend(check_requirements(RETROFIT_REQUIREMENTS))
    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 2
    print(f"Human collaboration verification passed for phase: {phase}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--phase",
        choices=("global", "retrofit", "all"),
        default="all",
    )
    args = parser.parse_args()
    return run(args.phase)


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run the verifier and confirm the expected failure**

Run:

```powershell
python scripts/verify_human_collaboration.py --phase global
```

Expected: exit code `2`, including `missing file: docs/conventions/human-collaboration.md` and missing-token failures for enforcement surfaces.

- [ ] **Step 3: Add the verifier to CI**

Append after the `Verify M1 artifacts` step in `.github/workflows/verify-tasks.yml`:

```yaml
      - name: Verify human collaboration contract
        run: python scripts/verify_human_collaboration.py --phase global
```

- [ ] **Step 4: Run focused lint**

Run:

```powershell
python -m ruff check scripts/verify_human_collaboration.py
python -m ruff format --check scripts/verify_human_collaboration.py
```

Expected: both pass. The collaboration verifier itself still exits `2` until Tasks 2 through 4 are complete.

---

### Task 2: Establish the canonical procedure and always-on rule

**Files:**
- Create: `docs/conventions/human-collaboration.md`
- Modify: `AGENTS.md:147`
- Modify: `.github/copilot-instructions.md:147`

**Interfaces:**
- Consumes: approved design at `docs/superpowers/specs/2026-07-17-human-collaboration-contract-design.md`.
- Produces: one canonical procedure and an always-on summary ingested by every coding client.

- [ ] **Step 1: Create the canonical procedure**

Create `docs/conventions/human-collaboration.md` with these exact top-level sections and the approved rules from the design document:

```markdown
# Human Collaboration Contract

> Current version: v1.0
> Last updated: 2026-07-17
> Status: Current
> Canonical path: docs/conventions/human-collaboration.md

## Purpose
## Interaction Profiles
### Independent execution
### Decision interview
### Creative collaboration
### Facilitated live operation
## Classification Rule
## Interview Contract
## Approval Semantics
## Required Phase Gates
### Decision interview flow
### Creative collaboration flow
### Facilitated live operation flow
## Checkpoint Review Package
## Evidence Contract
## Failure Handling
## Reviewer Blocking Rules
```

Use the corresponding approved text from the design document without weakening any rule. Keep the canonical procedure platform-neutral. Name interactive controls as preferred and the numbered-choice fallback as required when controls are unavailable.

- [ ] **Step 2: Add the always-on summary to AGENTS.md**

Insert after `## Workflow Expectations` and before `## Hard Rules`:

```markdown
## Human Collaboration Contract

Before planning or implementation, classify the task using
`docs/conventions/human-collaboration.md`: independent execution, decision
interview, creative collaboration, facilitated live operation, or a
combination.

- A task is not independent when completion depends on founder taste, intent,
  private knowledge, risk tolerance, external action, or observed feedback.
- For non-independent work, ask one focused question at a time. Prefer
  interactive multiple-choice controls with a recommendation and free-form
  input. Use a clearly explained numbered-choice fallback only when the client
  cannot render controls.
- Explain every artifact, why it matters, what is fixed or open, how to review
  it, what needs attention, and what follows approval.
- Use low-cost intermediate artifacts before full UI, art, narrative,
  gameplay, or tuning implementation.
- Rehearsals and playtests pause at preparation, preflight, walkthrough,
  live-session, debrief, and remediation gates.
- Plan approval, direction approval, artifact approval, phase go-ahead, final
  sign-off, and durable decision recording are separate approvals.
- Never infer founder approval from silence, PR creation, review activity, or
  prior general approval.
- If founder input is unavailable, continue reversible research only, then
  stop before making a choice or starting dependent implementation.
```

- [ ] **Step 3: Synchronize the Copilot mirror**

Preserve the generated-mirror preamble in `.github/copilot-instructions.md`.
Replace everything from `# Agent Operating Guide` onward with the exact body
from `AGENTS.md`, beginning at the same heading.

- [ ] **Step 4: Verify the canonical and mirrored rules**

Run:

```powershell
python scripts/verify_human_collaboration.py --phase global
```

Expected: failures remain for other enforcement surfaces, but no failures for
`docs/conventions/human-collaboration.md`, `AGENTS.md`, or the mirror.

- [ ] **Step 5: Commit the canonical rule**

```powershell
git add AGENTS.md .github/copilot-instructions.md docs/conventions/human-collaboration.md scripts/verify_human_collaboration.py .github/workflows/verify-tasks.yml
git commit -m "docs(config): establish human collaboration contract"
```

---

### Task 3: Make thinking roles carry collaboration intent

**Files:**
- Modify: `docs/conventions/ai-contributions.md:3`
- Modify: `docs/agents/README.md:16`
- Modify: `docs/agents/product-steward.md:19`
- Modify: `docs/agents/business-steward.md:21`
- Modify: `docs/agents/system-architect.md:21`
- Modify: `docs/agents/planner.md:18`
- Modify: `docs/agents/spec-author.md:19`
- Modify: `docs/agents/scribe.md:19`

**Interfaces:**
- Consumes: the canonical profiles and evidence contract from Task 2.
- Produces: role outputs that preserve required human input through the intent, planning, specification, and recording pipeline.

- [ ] **Step 1: Constrain async delegation**

Replace the Codex allocation in `docs/conventions/ai-contributions.md` with:

```markdown
**Codex (cloud):** Delegated async work with explicit specs and clear
acceptance criteria. Use for independent execution and reversible research or
preparation. If a task requires a decision interview, creative collaboration,
facilitated live operation, or owner action, Codex must stop at the applicable
phase gate and wait for founder input.
```

Add under Requirements:

```markdown
**Human collaboration classification:** Before planning or implementation,
declare the interaction profile and follow
`docs/conventions/human-collaboration.md`. Approval evidence must identify the
named decision, artifact, version, or phase that was approved.
```

- [ ] **Step 2: Add Collaboration Intake to the pipeline**

In `docs/agents/README.md`, add `Collaboration Intake` between the shared
intent gate and Planner. State that Product, Business, and Architecture identify
whether founder input is needed; Planner carries profiles and phase gates;
Spec Author makes them testable; Implementer facilitates them; Reviewer blocks
missing evidence; Scribe records only explicit approvals.

- [ ] **Step 3: Add Human Collaboration sections to each thinking role**

Add `## Human Collaboration` before `## Handoff` in each role file with these
responsibilities:

- Product Steward: identify product and creative decisions, interview the
  founder one question at a time, and output explicit locked intent.
- Business Steward: use decision interviews for pricing, packaging, market,
  budget, and risk choices; distinguish analysis from founder choice.
- System Architect: use decision interviews for genuine technical trade-offs;
  present implications and a recommendation before recording the approach.
- Planner: attach profiles, required founder inputs, phases, artifacts, and
  stop gates to every task; keep independent work efficient.
- Spec Author: include the Human Collaboration Contract section from the
  template and block implementation on unresolved input.
- Scribe: record only an explicit approval tied to a named decision or artifact;
  never convert draft text, silence, or PR activity into founder sign-off.

- [ ] **Step 4: Run the verifier**

```powershell
python scripts/verify_human_collaboration.py --phase global
```

Expected: role and contribution-policy checks pass. Failures remain only for
Implementer, Reviewer, template, working model, or usage guidance.

- [ ] **Step 5: Commit role enforcement**

```powershell
git add docs/conventions/ai-contributions.md docs/agents
git commit -m "docs(config): carry collaboration through agent roles"
```

---

### Task 4: Enforce collaboration during implementation and review

**Files:**
- Modify: `docs/skills/github-task-implementer/SKILL.md:12`
- Modify: `docs/skills/arcwright-reviewer/SKILL.md:14`
- Modify: `docs/conventions/review-checklist.md:5`
- Modify: `docs/specs/0000-template.md:23`
- Modify: `docs/roadmap/operations/working-model.md:13`
- Modify: `docs/agents/USAGE.md:13`

**Interfaces:**
- Consumes: profiles, phase gates, artifact packages, and evidence definitions from Task 2.
- Produces: enforced intake, stop conditions, review blockers, authoring template, tracker guidance, and cross-client user behavior.

- [ ] **Step 1: Add Implementer classification before planning**

Insert a new workflow section after `Capture the Task Contract`:

```markdown
### 2. Classify Human Collaboration

- Read `docs/conventions/human-collaboration.md` and declare every applicable
  interaction profile with a short rationale.
- If the task is not independent, list required founder inputs, the current
  phase, the next gate, intermediate artifacts, and approval evidence needed.
- Conduct required interviews one focused question at a time. Prefer
  interactive multiple-choice controls with a recommendation and free-form
  input. Use the numbered-choice fallback only when controls are unavailable.
- Creative work begins with open-ended founder vision, followed by 2 to 3
  advised directions and explained low-cost artifacts.
- Facilitated live operations stop at every preparation, preflight,
  walkthrough, live-session, debrief, and remediation gate.
- If the founder is unavailable, continue reversible research only and stop
  before choosing or implementing dependent work.
```

Renumber subsequent workflow headings. Add stop conditions for missing profile,
missing required interview, missing artifact explanation, inferred approval,
and a live phase without its go or no-go.

- [ ] **Step 2: Add Reviewer collaboration evidence checks**

Insert after `Establish the Contract`:

```markdown
### 2. Verify Human Collaboration Evidence

- Confirm the task declares every applicable interaction profile.
- For non-independent work, verify required founder inputs, phase gates,
  explained artifacts, locked decisions, explicit approval evidence, and
  outstanding owner actions.
- Block when an interview or phase was skipped, a completed implementation
  replaced an intermediate artifact, an artifact was not reviewable, approval
  was inferred, a decision record overclaims approval, or a live operation
  advanced without its go or no-go.
- If a founder decision changed, verify dependent work and approvals were
  reopened and updated.
```

Renumber subsequent headings and add corresponding stop conditions.

- [ ] **Step 3: Extend the canonical review checklist**

Add to `Before Reading the Diff`:

```markdown
- [ ] Is the task's collaboration profile declared and justified?
- [ ] For non-independent work, are required interviews, explained artifacts,
      phase approvals, and explicit sign-off evidence present?
- [ ] Does every approval identify the exact decision, artifact, version, or
      phase approved?
```

Add before merging:

```markdown
- [ ] No decision record infers founder approval from silence, PR activity, or
      a broader approval.
- [ ] No live-operation phase advanced without its explicit go or no-go.
```

- [ ] **Step 4: Add the spec-template contract**

Insert before Acceptance Criteria in `docs/specs/0000-template.md`:

```markdown
# Human Collaboration Contract

**Interaction profiles:** Independent execution | Decision interview |
Creative collaboration | Facilitated live operation

**Classification rationale:** [Why each selected profile applies]

**Required founder inputs:**
- [Named input or "None"]

**Phase gates:**
- [Phase, artifact, and explicit approval needed]

**Review package:**
- [How artifacts will be explained and reviewed]

**Approval evidence:**
- [Named decision, artifact/version, approval, and date]

**Owner actions:**
- [External action or "None"]
```

- [ ] **Step 5: Update roadmap and client guidance**

In `docs/roadmap/operations/working-model.md`, require task records and issue
mirrors to carry profiles, required inputs, phases, artifacts, approval
evidence, and owner actions.

In `docs/agents/USAGE.md`, add a plain-language section explaining:

- independent tasks follow the normal plan flow;
- decision, creative, and live tasks pause for input;
- questions use interactive forms when available;
- the numbered-choice fallback is used otherwise;
- every artifact explains what it is, how to review it, and what needs
  attention; and
- approving a plan does not approve creative direction or final sign-off.

- [ ] **Step 6: Run global verification**

```powershell
python scripts/verify_human_collaboration.py --phase global
python -m ruff check scripts/verify_human_collaboration.py
python -m ruff format --check scripts/verify_human_collaboration.py
```

Expected: all commands pass.

- [ ] **Step 7: Commit implementation and review enforcement**

```powershell
git add docs/skills/github-task-implementer/SKILL.md docs/skills/arcwright-reviewer/SKILL.md docs/conventions/review-checklist.md docs/specs/0000-template.md docs/roadmap/operations/working-model.md docs/agents/USAGE.md
git commit -m "docs(config): enforce phased founder collaboration"
```

---

### Task 5: Verify, publish, and merge-gate Wave 1

**Files:**
- Verify all Wave 1 files.

**Interfaces:**
- Consumes: Tasks 1 through 4.
- Produces: one reviewable Wave 1 PR and a hard stop until it merges.

- [ ] **Step 1: Run static and contract checks**

```powershell
python scripts/verify_human_collaboration.py --phase global
python -m ruff check scripts/verify_human_collaboration.py
python -m ruff format --check scripts/verify_human_collaboration.py
git diff --check origin/main...HEAD
$files = @('AGENTS.md', '.github/copilot-instructions.md', 'docs/conventions/human-collaboration.md', 'docs/conventions/ai-contributions.md', 'docs/conventions/review-checklist.md', 'docs/specs/0000-template.md', 'docs/roadmap/operations/working-model.md')
$forbidden = Select-String -Path $files -Pattern ([char]0x2014)
if ($forbidden) { $forbidden; exit 1 }
```

Expected: verifier and Ruff pass; `git diff --check` is clean; the encoded
character check returns no matches.

- [ ] **Step 2: Run repository pre-commit checks**

```powershell
pre-commit run --all-files
```

Expected: all configured hooks pass.

- [ ] **Step 3: Confirm acceptance criteria**

Record evidence that Wave 1 satisfies:

- canonical profiles and procedure exist;
- always-on rules and Copilot mirror match;
- roles preserve collaboration requirements;
- Implementer and Reviewer enforce gates;
- templates and user guidance are updated; and
- independent work remains available without added interview phases.

- [ ] **Step 4: Push and open the Wave 1 PR**

Use conventional title:

```text
docs(config): enforce human collaboration contract
```

PR body must explain what changed, reference
`docs/superpowers/specs/2026-07-17-human-collaboration-contract-design.md`, list
per-criterion evidence, and state that Wave 2 cannot begin until merge.

- [ ] **Step 5: Stop for human review and merge**

Do not begin Task 6 until GitHub confirms the Wave 1 PR is merged to `main`.

---

### Task 6: Add the current-open-work inventory and retrofit verifier

**Files:**
- Create: `docs/roadmap/operations/human-collaboration-open-work.md`
- Modify: `scripts/verify_human_collaboration.py`

**Interfaces:**
- Consumes: fresh `origin/main`, live open issue inventory, and canonical task records.
- Produces: an auditable classification matrix and automated verification for every targeted canonical task.

- [ ] **Step 1: Start Wave 2 from fresh main**

After Wave 1 merge:

```powershell
git fetch origin --prune
git -C 'C:\Users\nicke\OneDrive\Desktop\arcwright' worktree add 'C:\Users\nicke\OneDrive\Desktop\arcwright\.worktrees\human-collaboration-open-work' -b codex/human-collaboration-open-work origin/main
git -C 'C:\Users\nicke\OneDrive\Desktop\arcwright\.worktrees\human-collaboration-open-work' status --short --branch
```

Expected: the new branch contains the merged global contract.

- [ ] **Step 2: Refresh live open issues without mutation**

Fetch open issues in `nickejanssen/arcwright`. Record issue number, title,
state, labels, updated timestamp, canonical task path, and interaction profiles.
If the live list differs from this plan, update only the inventory rows needed
to reflect current reality. Do not silently add product scope.

- [ ] **Step 3: Create the canonical inventory**

Create `docs/roadmap/operations/human-collaboration-open-work.md` with columns:

```markdown
| Issue | Task | Canonical path | Profiles | Founder input | Next gate |
| --- | --- | --- | --- | --- | --- |
```

Use these profile assignments:

- Facilitated live operation: AW-232, AW-242, AW-243, AW-266, AW-273, AW-286.
- Decision interview: AW-234, AW-244, AW-269, AW-274.
- Creative collaboration: AW-267, AW-277 through AW-285.
- Creative collaboration plus decision interview: AW-268.
- Operational collaboration using decision interview: AW-240, AW-241.
- Independent execution: AW-233, AW-235 through AW-239, AW-245, AW-270 through AW-272, AW-275, AW-276.
- Issue #138: Decision interview, because the host-facing drop behavior lacks a canonical locked choice. Mark the missing stable task record as a blocker rather than inventing an AW number.

- [ ] **Step 4: Populate retrofit verifier requirements**

Replace the empty `RETROFIT_REQUIREMENTS` with every task file listed in the
Wave 2 file structure and its exact required profile token. Also require the
inventory file and the related specs to contain `# Human Collaboration
Contract` or `## Human Collaboration Contract`.

- [ ] **Step 5: Run and confirm expected retrofit failures**

```powershell
python scripts/verify_human_collaboration.py --phase retrofit
```

Expected: exit code `2` with missing profile tokens in task and spec files.

- [ ] **Step 6: Commit inventory and failing retrofit verification**

```powershell
git add docs/roadmap/operations/human-collaboration-open-work.md scripts/verify_human_collaboration.py
git commit -m "docs(roadmap): classify open work by collaboration profile"
```

---

### Task 7: Retrofit decision, operational, and live-session task records

**Files:**
- Modify the decision, operational, owner-action, and facilitated-live task files listed in Wave 2.

**Interfaces:**
- Consumes: the inventory and canonical contract.
- Produces: task-local profiles, gates, review packages, approval evidence, and owner actions.

- [ ] **Step 1: Add the decision-interview task block**

For AW-234, AW-244, AW-269, and AW-274, insert before Acceptance Criteria:

```markdown
## Human Collaboration Contract

**Interaction profile:** Decision interview.

**Founder input:** The task names the concrete decision that cannot be inferred
from existing canonical records.

**Required flow:** Research and explain constraints, present 2 to 3 options
with a recommendation, ask one focused multiple-choice question at a time,
confirm the selected decision, then record only the approved scope.

**Gate:** Dependent implementation stops until the founder explicitly approves
the named decision.

**Evidence:** Record the decision, artifact or option approved, explicit
approval, date, and remaining owner actions.
```

Specialize founder input as follows:

- AW-234: cost assumptions, player counts, pricing scenario, and margin lens.
- AW-244: interpretation of H1 evidence and the selected next-step option.
- AW-269: cloud target choices, cost/risk trade-offs, credentials, and owner
  console actions.
- AW-274: schema/API/telemetry compatibility approach and sequencing.

- [ ] **Step 2: Add operational collaboration blocks**

For AW-240 and AW-241, use Decision interview and require one-question-at-a-time
interviews about host workflow, recruitment, consent, observation, evidence,
and practical constraints. Require a walkthrough-ready draft and explicit
approval before treating the runbook or checklist as operationally ready.

- [ ] **Step 3: Add facilitated-live blocks**

For AW-232, AW-242, AW-243, AW-266, AW-273, and AW-286, require these gates:

```markdown
1. Preparation and environment evidence.
2. Preflight review and readiness approval.
3. Founder walkthrough or smoke test.
4. Explicit live-session go or no-go.
5. Guided live session.
6. Structured debrief.
7. Remediation recommendation and approval before another session.
```

Require the agent to explain what the founder should inspect, what to record,
and what blocks progression at each gate.

- [ ] **Step 4: Add AW-268's combined profile**

AW-268 must declare Creative collaboration plus Decision interview. Creative
gates cover asset, motion, and wrapper execution. The decision interview covers
animation runtime choice. AW-267 explicit final sign-off remains a prerequisite.

- [ ] **Step 5: Run targeted verification**

```powershell
python scripts/verify_human_collaboration.py --phase retrofit
```

Expected: the files changed in this task pass; remaining creative and
independent task records still fail.

- [ ] **Step 6: Commit decision and live-session retrofits**

```powershell
git add docs/roadmap/tasks/AW-232-* docs/roadmap/tasks/AW-234-* docs/roadmap/tasks/AW-240-* docs/roadmap/tasks/AW-241-* docs/roadmap/tasks/AW-242-* docs/roadmap/tasks/AW-243-* docs/roadmap/tasks/AW-244-* docs/roadmap/tasks/AW-266-* docs/roadmap/tasks/AW-268-* docs/roadmap/tasks/AW-269-* docs/roadmap/tasks/AW-273-* docs/roadmap/tasks/AW-274-* docs/roadmap/tasks/AW-286-*
git commit -m "docs(roadmap): gate founder decisions and live sessions"
```

---

### Task 8: Retrofit creative and independent task records

**Files:**
- Modify the remaining task records listed in Wave 2.

**Interfaces:**
- Consumes: the inventory and contract.
- Produces: explicit creative phases or independent-execution rationales for every remaining open task record.

- [ ] **Step 1: Add creative collaboration blocks**

For AW-267 and AW-277 through AW-285, require:

```markdown
## Human Collaboration Contract

**Interaction profile:** Creative collaboration.

**Discovery:** Begin with the founder's open-ended goals, references, taste,
audience, constraints, and success definition. Ask one focused question at a
time.

**Directions:** Present 2 to 3 explained options with expert advice and a
recommendation. Pause to lock one direction.

**Intermediate artifacts:** Present low-cost review artifacts before full
implementation. Explain what each artifact is, how it fits the product, what
is fixed or open, what to inspect, how to review it, known limitations, and
the exact decision needed.

**Implementation gates:** Pause after direction selection, artifact review,
agreed implementation batches, and final sign-off.

**Evidence:** Tie every approval to the named artifact/version and date.
```

Use task-appropriate artifacts:

- AW-267: visual references and comparative moodboards.
- AW-277 through AW-280: representative narrative samples in six-beat context,
  plus failure examples.
- AW-281: authored arc and deterministic case examples.
- AW-282: intent-menu and question-token scenarios.
- AW-283: answer, lie, contradiction, and fairness samples.
- AW-284: scoring scenarios and tuning tables.
- AW-285: TV and phone wireframes or interactive prototypes with review
  instructions.

- [ ] **Step 2: Add independent-execution blocks**

For AW-233, AW-235 through AW-239, AW-245, AW-270 through AW-272, AW-275, and
AW-276, add:

```markdown
## Human Collaboration Contract

**Interaction profile:** Independent execution.

**Rationale:** Current canonical decisions and acceptance criteria fully
constrain this task. The normal plan-approval workflow applies. If execution
uncovers a subjective, strategic, external-action, or live-validation choice,
reclassify the task before deciding.

**Founder input:** None unless a reclassification trigger occurs.
```

Name the existing spec or decision that constrains each task.

- [ ] **Step 3: Run retrofit verification**

```powershell
python scripts/verify_human_collaboration.py --phase retrofit
```

Expected: task-record checks pass. Related specs still fail until Task 9.

- [ ] **Step 4: Commit task classifications**

```powershell
git add docs/roadmap/tasks
git commit -m "docs(roadmap): add collaboration contracts to open tasks"
```

---

### Task 9: Retrofit related specs, verify, and merge-gate Wave 2

**Files:**
- Modify the related specs listed in Wave 2.

**Interfaces:**
- Consumes: task-local profiles from Tasks 7 and 8.
- Produces: parent and implementation specs that preserve the same human-input gates.

- [ ] **Step 1: Add Human Collaboration Contract sections to related specs**

Insert before Acceptance Criteria in each listed spec. Use the task profile,
required founder inputs, phase gates, review packages, approval evidence, and
owner actions already defined in its canonical task record.

For multi-task parent specs:

- Spec 0067: facilitated rehearsal gates plus AW-269 owner-action gates.
- Spec 0068: creative content-review samples and facilitated rehearsal debrief.
- Spec 0069: creative visual checkpoints, explained mockups, and explicit
  founder sign-off before Tier 2 direction is canonical.
- Spec 0072: creative gameplay/content checkpoints plus AW-286 facilitated
  rehearsal gates.
- Spec 0073 M5 reconciliation: state that tracker synchronization may mirror
  collaboration requirements but cannot invent approval evidence.

For independent specs, name the canonical decision that fully constrains them
and require reclassification if a new human-input choice appears.

- [ ] **Step 2: Run full collaboration verification**

```powershell
python scripts/verify_human_collaboration.py --phase all
python -m ruff check scripts/verify_human_collaboration.py
python -m ruff format --check scripts/verify_human_collaboration.py
git diff --check origin/main...HEAD
```

Expected: all commands pass.

- [ ] **Step 3: Validate roadmap and documentation**

```powershell
python -m json.tool docs/roadmap/index.json > $null
pre-commit run --all-files
```

Expected: JSON parses and all configured hooks pass.

- [ ] **Step 4: Commit spec retrofits**

```powershell
git add docs/specs
git commit -m "docs(specs): add founder collaboration gates"
```

- [ ] **Step 5: Push and open the Wave 2 PR**

Use title:

```text
docs(roadmap): retrofit founder collaboration gates
```

List every changed task group, the classification rationale, verifier output,
and the design acceptance criteria. State that Wave 3 cannot begin until this
PR merges.

- [ ] **Step 6: Stop for human review and merge**

Do not mutate GitHub issue bodies or PR #243 until GitHub confirms Wave 2 is
merged to `main`.

---

### Task 10: Synchronize canonical collaboration contracts to GitHub issues

**Files:**
- No repository files unless live-state drift requires a canonical correction first.
- Update live GitHub issue bodies only.

**Interfaces:**
- Consumes: merged canonical task records and open-work inventory from Wave 2.
- Produces: GitHub issue bodies that mirror canonical collaboration requirements without changing labels, milestones, or scope.

- [ ] **Step 1: Refresh main and snapshot live issue state**

```powershell
git -C 'C:\Users\nicke\OneDrive\Desktop\arcwright' fetch origin --prune
git -C 'C:\Users\nicke\OneDrive\Desktop\arcwright' worktree add --detach 'C:\Users\nicke\OneDrive\Desktop\arcwright\.worktrees\human-collaboration-github-sync' origin/main
git -C 'C:\Users\nicke\OneDrive\Desktop\arcwright\.worktrees\human-collaboration-github-sync' rev-parse HEAD
```

Fetch every issue listed in the Wave 3 file structure with number, title, body,
labels, milestone, state, and `updatedAt`. Compare it to the Wave 2 snapshot.
If a body changed after the snapshot, stop that issue and reconcile the newer
text before overwriting it.

- [ ] **Step 2: Synchronize mapped task issues**

For each issue with a canonical task path in `docs/roadmap/index.json`, replace
the issue body with the current canonical task Markdown. Preserve title,
labels, milestone, assignees, and state.

Do not close issues merely because implementation appears merged. Tracker
closure is outside this collaboration-contract synchronization unless the user
separately requests reconciliation.

- [ ] **Step 3: Handle issue #138 without inventing a task ID**

Append a Human Collaboration Contract section that cites
`docs/roadmap/operations/human-collaboration-open-work.md`, declares Decision
interview, and states that the missing stable AW task record blocks planning.
Do not assign an AW number in this plan.

- [ ] **Step 4: Verify live issue bodies**

Re-fetch every changed issue. Confirm:

- the body contains the expected profile;
- canonical links are present;
- existing labels and milestone are unchanged; and
- no approval evidence was invented.

---

### Task 11: Reset PR #243 and AW-267 to founder discovery

**Files:**
- Modify on PR #243 branch: `docs/design/nightcap-art-direction.md`
- Modify on PR #243 branch: three moodboard files
- Modify on PR #243 branch: `docs/product/decisions-log.csv`
- Update GitHub issue `#184` and PR `#243` metadata.

**Interfaces:**
- Consumes: merged AW-267 collaboration contract and current PR #243 head.
- Produces: draft research artifacts with no false sign-off and an explicit next gate of founder discovery interview.

- [ ] **Step 1: Convert PR #243 to draft and mark it blocked**

Update PR metadata before touching branch files:

- draft: `true`;
- title remains unchanged;
- body begins with `## Status: blocked on founder collaboration`;
- state that current files are candidate research, not approved direction;
- state that D-073 is not approved;
- list the required discovery, directions, artifact review, revision, and final
  sign-off phases; and
- state that AW-268 remains blocked.

- [ ] **Step 2: Work on the exact PR head branch**

Resolve PR #243's current head branch and SHA, then create or use an isolated
worktree for that branch. Confirm there are no unrelated local changes before
editing.

- [ ] **Step 3: Correct the art-direction artifact statuses**

In `docs/design/nightcap-art-direction.md`, replace any founder-approved or
canonical status with:

```markdown
> Status: Candidate research, founder direction not yet selected
```

Add a short notice explaining that the document is reversible research and
cannot guide AW-268 until the collaboration phases complete.

In each moodboard, replace approval-like status with:

```markdown
> Status: Candidate research for founder interview, not approved direction.
```

Do not change palettes, references, typography, motion, or other creative
choices in this reset. Those choices belong to the later AW-267 interview.

- [ ] **Step 4: Correct D-073 without discarding traceability**

Keep the unmerged D-073 row but change its status to `Proposed`. Rewrite its
description to state that PR #243 contains candidate research, founder
discovery and direction selection are pending, and AW-268 remains blocked until
explicit final sign-off. Do not use `Committed`, `Decided`, or approval
language.

- [ ] **Step 5: Verify and commit the PR branch correction**

```powershell
python -c "import csv; list(csv.DictReader(open('docs/product/decisions-log.csv', encoding='utf-8-sig')))"
git diff --check
rg -n 'founder-approved|Status: Approved|D-073.*Committed' docs/design docs/product/decisions-log.csv
$forbidden = Select-String -Path 'docs/design/*.md','docs/design/moodboards/*.md','docs/product/decisions-log.csv' -Pattern ([char]0x2014)
if ($forbidden) { $forbidden; exit 1 }
```

Expected: CSV parses; diff is clean; no false approval or em dash matches.

Commit and push:

```powershell
git add docs/design docs/product/decisions-log.csv
git commit -m "docs(design): reset AW-267 to founder discovery"
git push
```

- [ ] **Step 6: Synchronize issue #184 and add a blocking note**

Replace issue #184 body with the merged AW-267 canonical task record. Add one
comment to issue #184 and PR #243 stating that the reset is complete, current
artifacts are candidate research, and the next action is the one-question-at-a-
time founder art-direction interview.

- [ ] **Step 7: Stop before art-direction choices**

Do not revise creative direction or record D-073 approval in this plan. Begin
the AW-267 founder interview as a separate collaborative task.

---

### Task 12: Final verification and handoff

**Files:**
- Read-only verification of repo and GitHub state.

**Interfaces:**
- Consumes: merged Waves 1 and 2 plus completed Wave 3 synchronization.
- Produces: acceptance-criteria evidence and the next interactive AW-267 action.

- [ ] **Step 1: Verify merged repository state**

On fresh `main`:

```powershell
git -C 'C:\Users\nicke\OneDrive\Desktop\arcwright' fetch origin --prune
git -C 'C:\Users\nicke\OneDrive\Desktop\arcwright' worktree add --detach 'C:\Users\nicke\OneDrive\Desktop\arcwright\.worktrees\human-collaboration-final' origin/main
Set-Location 'C:\Users\nicke\OneDrive\Desktop\arcwright\.worktrees\human-collaboration-final'
python scripts/verify_human_collaboration.py --phase all
python -m ruff check scripts/verify_human_collaboration.py
python -m ruff format --check scripts/verify_human_collaboration.py
pre-commit run --all-files
git status --short --branch
```

Expected: all checks pass and the working tree is clean.

- [ ] **Step 2: Verify GitHub state**

Confirm:

- every targeted issue body has the canonical profile and gates;
- issue labels, milestones, and states were not accidentally changed;
- PR #243 is draft and blocked on founder collaboration;
- PR #243 artifacts are marked candidate research;
- D-073 is Proposed, not approved or committed; and
- AW-268 remains blocked on AW-267 explicit final sign-off.

- [ ] **Step 3: Report acceptance criteria**

State which design acceptance criteria are satisfied, with file paths, command
results, issue links, and PR #243 evidence. Name any item blocked on merge or
external GitHub state rather than claiming completion.

- [ ] **Step 4: Offer the next interactive action**

Offer one multiple-choice control:

1. Begin the AW-267 art-direction discovery interview. Recommended.
2. Review the collaboration-contract changes first.
3. Pause here.

Do not begin the interview until the founder selects option 1.

---

## Plan Self-Review

- Spec coverage: Tasks 1 through 5 implement global enforcement; Tasks 6
  through 9 retrofit canonical work; Task 10 synchronizes issues; Task 11
  corrects PR #243 and D-073; Task 12 verifies every approved outcome.
- Completeness scan: no unresolved markers or unspecified implementation steps
  remain.
- Interface consistency: the verifier phases are `global`, `retrofit`, and
  `all` throughout; profiles match the approved design; GitHub changes depend
  on merged canonical records.
- Scope: no runtime, schema, API, dependency, prompt, eval, safety, routing, or
  product change is included.
