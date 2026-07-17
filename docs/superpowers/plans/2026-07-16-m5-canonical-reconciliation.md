# M5 Canonical Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Make the M5 documentation graph and GitHub execution tracker represent one current, Couch Race-aligned contract.

**Architecture:** Update canonical GitHub docs before GitHub issues. Durable decisions and ADRs establish scope, roadmap Markdown defines work, index.json maps that work to live objects, and issues mirror the canonical files. This plan makes documentation and tracker changes only.

**Tech Stack:** Markdown, JSON, GitHub CLI, GitHub Issues, PowerShell, Python 3.11 pytest.

## Global Constraints

- Refresh origin/main before every documentation batch and before every GitHub mutation.
- Add no scope beyond D-069, D-071, D-072, ADR-0013, and spec 0072.
- Couch Race has rival investigators and one deterministically resolved AI-suspect killer. No player-killer, secret-player-role, or player performance burden may appear in M5 launch records.
- Python owns runtime authority. TypeScript remains rendering, event subscription, and player-input submission only.
- Preserve deterministic case truth, mandatory knowledge gating, surface-agnostic events, private-audience filtering, provider agnosticism, and cost-aware routing.
- Do not change runtime source, schemas, migrations, dependency manifests, or agent-local directories.

---

## File Structure

- Create: docs/roadmap/tasks/AW-275-design-system-follow-ups.md
- Create: docs/roadmap/tasks/AW-276-arc-voice-block-injection.md
- Create: docs/roadmap/tasks/AW-277-couch-race-narrator-transition-lines.md
- Create: docs/roadmap/tasks/AW-278-couch-race-truth-sequence-and-reveal-accounting.md
- Create: docs/roadmap/tasks/AW-279-detective-identity-and-opening-briefing.md
- Create: docs/roadmap/tasks/AW-280-couch-race-clue-release-content.md
- Modify: docs/roadmap/epics/M5-G-nightcap-visual-identity-and-polish.md
- Modify: docs/roadmap/epics/M5-I-nightcap-couch-race-arc-and-interrogation.md
- Modify: docs/roadmap/index.json
- Modify: docs/specs/0072-nightcap-couch-race-v1.md
- Modify live GitHub issues: #202, #203, #223, #226, #227, #228, #229, #230, #184, #234.

---

### Task 1: Capture a current decision and tracker snapshot

**Files:**
- Read: docs/product/decisions-log.csv, docs/decisions/0013-nightcap-couch-race-v1-launch-target.md, docs/specs/0072-nightcap-couch-race-v1.md, docs/roadmap/index.json.
- Read: live issues #201, #202, #203, #223, #226, #227, #228, #229, #230, #184, #234.

**Interfaces:**
- Consumes: origin/main and live issue updatedAt timestamps.
- Produces: a fresh go/no-go snapshot for canonical edits.

- [ ] **Step 1: Refresh origin/main**

~~~powershell
git fetch origin --prune
git rev-parse origin/main
git log -1 --format='%H %cs %s' origin/main
~~~

Expected: record the remote SHA before writing.

- [ ] **Step 2: Verify current product direction**

~~~powershell
git show origin/main:docs/product/decisions-log.csv | Select-String -Pattern 'D-069|D-071|D-072'
git show origin/main:docs/decisions/0013-nightcap-couch-race-v1-launch-target.md
git show origin/main:docs/specs/0072-nightcap-couch-race-v1.md
~~~

Expected: D-071 and ADR-0013 remain the Couch Race charter; spec 0072 retains AW-281 through AW-286 and the AW-276 through AW-280 retarget.

- [ ] **Step 3: Snapshot affected issues without mutation**

~~~powershell
$issues = 201,202,203,223,226,227,228,229,230,184,234
foreach ($issue in $issues) { gh issue view $issue --json number,title,body,labels,state,updatedAt,url }
~~~

Expected: every current issue body, label, state, URL, and timestamp is available before Task 2.

- [ ] **Step 4: Stop on conflict**

If a newer durable decision changes scope, or an issue changed after this snapshot, stop the affected batch. Preserve compatible edits; obtain approval before resolving a scope conflict.

### Task 2: Repair canonical roadmap records and manifest

**Files:**
- Create: the six AW-275 through AW-280 task records listed in File Structure.
- Modify: M5-G epic, M5-I epic, index.json, and spec 0072.

**Interfaces:**
- Consumes: D-069, D-071, D-072, ADR-0013, specs 0068, 0069, 0071, 0072, and the AW-281 task format.
- Produces: complete canonical task records that Task 3 mirrors exactly.

- [ ] **Step 1: Create AW-275**

Create AW-275 with this header:

~~~markdown
# AW-275: Design System Follow-Ups: Semantic Tokens And Focus Visible

**Milestone / Epic:** M5 / M5-G
**Size:** S
**Status:** Planned
~~~

Scope: replace retired mini-game CSS variables with --ink-muted, --accuse, and --theme-glow; add semantic-token focus-visible states. Acceptance: no raw colors outside nightcap-web/src/design/, visible keyboard focus on host/join/shared-display surfaces, and green Nightcap tests. Must not do: engine or API changes.

- [ ] **Step 2: Create the five Couch Race supporting tasks**

Create AW-276 through AW-280 with the standard AW-281 sections: summary, why, player impact, business value, technical scope, acceptance criteria, tests/verification, dependencies, must-not-do, architecture references, and playtest relevance.

Use these exact headers and metadata:

~~~markdown
# AW-276: Arc Voice Block Injection
# AW-277: Couch Race Narrator Transition Lines
# AW-278: Couch Race Truth Sequence And Reveal Accounting
# AW-279: Detective Identity And Opening Briefing
# AW-280: Couch Race Clue Release Content

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Planned
~~~

AW-276 injects an arc-declared cacheable voice block without game-specific engine vocabulary. AW-277 composes six-beat narrator transitions, including the cold open, from resolved state with D-070 hints. AW-278 composes the shared Truth sequence from resolved case truth, authorized lies, and provenance; it never reveals a player-killer. AW-279 delivers flavor-only detective identity and briefing, without a secret, role, or performance burden. AW-280 composes fair clue content from deterministic case truth with provenance, audience targeting, and evidence-to-intent unlock semantics.

- [ ] **Step 3: Update epic relationships**

Add AW-275 to M5-G Tasks.

Add a Supporting Rehearsal 1 Dependencies section to M5-I after its child-task list. Link AW-276 through AW-280 and state that AW-281 through AW-286 remain M5-I child tasks while AW-276 through AW-280 are supporting D-069 narrative dependencies retargeted by AW-286.

- [ ] **Step 4: Add manifest records**

Add six task objects using the existing index.json shape. Use issue numbers 223, 226, 227, 228, 229, and 230 for AW-275 through AW-280. Set AW-275 to M5/M5-G/size S and AW-276 through AW-280 to M5/M5-I/size M. Every path must be the exact new task path. Add only dependency IDs explicitly documented in the new task records.

- [ ] **Step 5: Replace the stale PR #225 sentence**

Replace spec 0072's unmerged dependency statement with:

~~~markdown
Related specs: 0071 docs/specs/0071-live-loop-ai-character-dialogue.md
(live-loop AI character dialogue, merged by PR #225 and available on
origin/main; direct dependency for AW-283)
~~~

Preserve the other related-spec references.

- [ ] **Step 6: Validate canonical documentation**

~~~powershell
Get-Content -Raw docs/roadmap/index.json | ConvertFrom-Json | Out-Null
$ids = 'AW-275','AW-276','AW-277','AW-278','AW-279','AW-280'
$index = Get-Content -Raw docs/roadmap/index.json | ConvertFrom-Json
$index.tasks | Where-Object { $_.id -in $ids } | Select-Object id,milestone,epic,size,path,github | ConvertTo-Json -Depth 5
rg -n 'player-killer|secret player|eight-beat' docs/roadmap/tasks/AW-27[6-9]*.md docs/roadmap/tasks/AW-280*.md
git diff --check
~~~

Expected: valid JSON, six resolving paths, no prohibited legacy assumptions, and no whitespace errors.

- [ ] **Step 7: Commit canonical documentation**

~~~powershell
git add docs/roadmap/tasks/AW-275-design-system-follow-ups.md docs/roadmap/tasks/AW-276-arc-voice-block-injection.md docs/roadmap/tasks/AW-277-couch-race-narrator-transition-lines.md docs/roadmap/tasks/AW-278-couch-race-truth-sequence-and-reveal-accounting.md docs/roadmap/tasks/AW-279-detective-identity-and-opening-briefing.md docs/roadmap/tasks/AW-280-couch-race-clue-release-content.md docs/roadmap/epics/M5-G-nightcap-visual-identity-and-polish.md docs/roadmap/epics/M5-I-nightcap-couch-race-arc-and-interrogation.md docs/roadmap/index.json docs/specs/0072-nightcap-couch-race-v1.md
git commit -m "docs(roadmap): reconcile M5 Couch Race tasks"
~~~

Expected: one documentation-only commit.

### Task 3: Synchronize GitHub execution records

**Files:**
- Read: Task 2 canonical task and epic files.
- Modify: live issues #202, #203, #223, #226, #227, #228, #229, #230, #184, #234.

**Interfaces:**
- Consumes: canonical task Markdown as issue body and index.json as issue mapping.
- Produces: title, body, and label parity between GitHub and the canonical docs.

- [ ] **Step 1: Re-check issue timestamps**

~~~powershell
git fetch origin --prune
$issues = 201,202,203,223,226,227,228,229,230,184,234
foreach ($issue in $issues) { gh issue view $issue --json number,updatedAt,title,labels }
~~~

Expected: no scope-changing edit since Task 1. If an issue changed, stop and reconcile before overwriting it.

- [ ] **Step 2: Correct Post-M6 labels**

~~~powershell
gh issue edit 202 --remove-label M5
gh issue edit 203 --remove-label M5
~~~

Preserve issue #201's M5 label: the M5-H epic correctly contains AW-272 as
pre-M6 exit-gate work while AW-270 and AW-271 remain Post-M6 children. Do not
invent a new label absent from .github/tracker/labels.json.

- [ ] **Step 3: Mirror the six canonical task files**

~~~powershell
gh issue edit 223 --title "AW-275: Design System Follow-Ups: Semantic Tokens And Focus Visible" --body-file docs/roadmap/tasks/AW-275-design-system-follow-ups.md --add-label M5 --add-label task --add-label size:S
gh issue edit 226 --title "AW-276: Arc Voice Block Injection" --body-file docs/roadmap/tasks/AW-276-arc-voice-block-injection.md --add-label M5 --add-label task --add-label size:M
gh issue edit 227 --title "AW-277: Couch Race Narrator Transition Lines" --body-file docs/roadmap/tasks/AW-277-couch-race-narrator-transition-lines.md --add-label M5 --add-label task --add-label size:M
gh issue edit 228 --title "AW-278: Couch Race Truth Sequence And Reveal Accounting" --body-file docs/roadmap/tasks/AW-278-couch-race-truth-sequence-and-reveal-accounting.md --add-label M5 --add-label task --add-label size:M
gh issue edit 229 --title "AW-279: Detective Identity And Opening Briefing" --body-file docs/roadmap/tasks/AW-279-detective-identity-and-opening-briefing.md --add-label M5 --add-label task --add-label size:M
gh issue edit 230 --title "AW-280: Couch Race Clue Release Content" --body-file docs/roadmap/tasks/AW-280-couch-race-clue-release-content.md --add-label M5 --add-label task --add-label size:M
~~~

Expected: each issue equals its canonical task record and no title or body retains obsolete player-killer scope.

- [ ] **Step 4: Mirror epic records**

~~~powershell
gh issue edit 184 --body-file docs/roadmap/epics/M5-G-nightcap-visual-identity-and-polish.md
gh issue edit 234 --body-file docs/roadmap/epics/M5-I-nightcap-couch-race-arc-and-interrogation.md
~~~

Expected: M5-G includes AW-275, while M5-I distinguishes child tasks AW-281 through AW-286 from supporting AW-276 through AW-280 dependencies.

### Task 4: Verify the final documentation and tracker graph

**Files:**
- Read: all changed roadmap files, spec 0072, index.json, and the eleven affected live issues.

**Interfaces:**
- Consumes: committed canonical docs and synchronized tracker metadata.
- Produces: evidence that M5 contains no tracker-only scope, broken path, or Couch Race contradiction.

- [ ] **Step 1: Validate manifest paths and Post-M6 classification**

~~~powershell
$index = Get-Content -Raw docs/roadmap/index.json | ConvertFrom-Json
$index.tasks | Where-Object { $_.milestone -eq 'M5' } | ForEach-Object { if (-not (Test-Path $_.path)) { throw "Missing task path: $($_.id) $($_.path)" } }
$index.tasks | Where-Object { $_.id -in @('AW-270','AW-271') } | Select-Object id,milestone,epic,path | ConvertTo-Json
~~~

Expected: every M5 path exists; AW-270 and AW-271 remain Post-M6.

- [ ] **Step 2: Verify live issue parity**

~~~powershell
$issues = 201,202,203,223,226,227,228,229,230,184,234
foreach ($issue in $issues) { gh issue view $issue --json number,title,body,labels,state,updatedAt,url }
~~~

Expected: #202 and #203 have no M5 label; #223 and #226 through #230 match their task records; #184 and #234 match their epic records.

- [ ] **Step 3: Run regression and diff checks**

~~~powershell
& 'C:\Users\nicke\OneDrive\Desktop\arcwright\.aw102-venv\Scripts\python.exe' -m pytest engine/tests -q --basetemp '..\pytest-tmp\m5-spec-reconciliation'
git diff origin/main --check
git status --short
~~~

Expected: 496 passed and 1 skipped when DATABASE_URL is unset, no whitespace errors, and only intentional documentation changes.

- [ ] **Step 4: Commit verification-only corrections**

If Task 4 reveals a documentation correction, make only that correction, rerun Steps 1 through 3, then run:

~~~powershell
git add docs/roadmap docs/specs/0072-nightcap-couch-race-v1.md
git commit -m "docs(roadmap): verify M5 tracker alignment"
~~~

Do not create an empty commit when verification finds no documentation delta.

---

## Plan Self-Review

- Spec coverage: Task 1 checks freshness; Task 2 repairs the canonical graph and Couch Race retarget; Task 3 mirrors it to GitHub; Task 4 verifies every required relationship.
- Placeholder scan: no incomplete marker, generic test instruction, or unspecified path remains.
- Consistency: AW-275 is M5-G; AW-276 through AW-280 are M5-I supporting dependencies; AW-281 through AW-286 remain M5-I child tasks; AW-270 and AW-271 remain Post-M6.
