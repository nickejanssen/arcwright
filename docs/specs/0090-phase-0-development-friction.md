---
id: engineeringpractice.specs.0090-phase-0-development-friction
namespace: engineering-practice
title: Phase 0 Development Friction
owner: Nico Janssen
status: active
review_by: "2027-09-27"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: [development, ci, setup]
supersedes: []
---

# Phase 0 Development Friction

**Status**: Approved design; implementation submitted for review, 2026-09-27

**Author**: Founder and Codex | **Date**: 2026-09-27

**Canonical path**: `docs/specs/0090-phase-0-development-friction.md`

---

# References

- Related ADRs: None
- Architecture sections: `docs/architecture/15-development-guide.md`, Sections 15.2 and 15.8
- Related specs: None
- PRD sections: None; this work changes no product behavior
- Implementation plan: `docs/superpowers/plans/2026-09-27-phase-0-dev-friction.md`
- Original approved design record: `docs/superpowers/specs/2026-09-27-phase-0-dev-friction-design.md` (compatibility pointer)
- Pull request: #339

**x-scope-evidence**: `none`. This specification authorizes no new product scope.

---

# Overview

Reduce development friction by keeping unconfigured deploy workflows green, recording the approved tooling freeze D-110, and documenting reproducible Python 3.11 setup. No product code in `engine/`, `api/`, `sdk/`, `dashboard/`, or `config/` changes.

## Evidence

Measured on 2026-09-27: Deploy API had failed all 32 observed runs since July at Google Cloud authentication because no workload identity provider was configured. Deploy Web had failed all 8 observed runs. The repository had no Actions secrets or variables. `.python-version` already pins Python 3.11, while the Windows launcher selected Python 3.14; mypy then failed on NumPy type stubs. CI uses Python 3.11; a local 3.11 environment passed mypy on 126 files, ruff, and 912 engine tests with one database integration skip. Between September 1 and September 27, nearly all commits went to agent and knowledge-base infrastructure while Paper Test #2 v3.0 had no external sessions.

---

# In Scope

- Add a presence-only preflight job to `.github/workflows/deploy-api.yml` and `.github/workflows/deploy-web.yml`. Retain their push filters, add `workflow_dispatch`, connect the preflight output to the deploy job, and leave deploy steps unchanged.
- With no settings, emit a `Deploy skipped` notice and skip deploy successfully. With partial settings, name missing setting keys and fail. With all settings present, proceed to the existing deploy steps. Never print setting values.
- Append the approved D-110 decision to `docs/product/decisions-log.csv`, including its break-fix exception and Gate 1 end condition.
- Document Python 3.11 setup using `uv` and a complete Windows `py -3.11` fallback that installs project requirements, verification tools, and pre-commit inside `.venv`.

---

# Out of Scope

- Changing engine, API, SDK, dashboard, or configuration product code.
- Configuring GCP or Cloudflare credentials, making a deploy succeed, or changing Cloud Run runtime secrets managed by Secret Manager (AW-269).
- Enforcing the tooling freeze with hooks or CI.
- Other README corrections or changes to `AGENTS.md`.
- Changing the malformed Section value in an existing decisions-log row.
- Dispatching post-merge workflows before the founder confirms merge.

---

# Human Collaboration Contract

**Interaction profiles**: Independent execution.

**Classification rationale**: The founder approved the three design sections, credential-presence preflight, tooling-freeze endpoint, and executor. Implementation follows the specified behavior; no taste or product decision remains open.

**Required founder inputs**: None for implementation.

**Phase gates**: The founder merges the PR. After the founder confirms merge, Task 5 dispatches both workflows and verifies skipped deploy jobs and notices.

**Review package**: This specification, implementation plan, acceptance evidence in PR #339, and automated checks.

**Approval evidence**: Founder approval of the Phase 0 plan/spec and credential-presence preflight on 2026-09-27. The founder approved the README pre-commit installation correction; PR review then identified and resolved the incomplete no-uv fallback.

**Owner actions**: Merge the PR; later confirm merge before Task 5.

---

# Acceptance Criteria

- [x] README uses `uv venv` and `uv pip` for requirements, pinned verification tools, and pre-commit; its Windows no-uv fallback uses `py -3.11 -m venv` and `python -m pip` for the same installs. The reason for Python 3.11 and `.python-version` is stated.
- [x] The documented uv setup produced Python 3.11.15; ruff and mypy passed, and engine tests reported 912 passed and one `DATABASE_URL`-dependent skip.
- [x] Both deploy workflows retain their push filters, add manual dispatch, use a preflight output to gate deploy, and preserve deploy steps byte-for-byte.
- [x] Preflight evaluates setting presence only, prints no values, and handles none, partial, and full configuration as specified. The local harness failed against both baseline workflows and passed all six updated cases.
- [x] D-110 appears once as the final six-column CSV row with Section `Process / Tooling` and Status `Committed`; the appended D-110 decision is the only row changed; its canonical spec reference is current.
- [x] `scripts/checks/scope_evidence_check.py` passes.
- [x] Only the plan's enumerated files, this canonical specification, its compatibility pointer, and the spec index are changed. No product code or agent-local files change.

---

# Test Plan

- Parse both workflow files as YAML and execute their actual preflight scripts under bash with no settings, partial settings, and all settings. Confirm expected exit status, output, and annotations.
- Compare original and final deploy steps byte-for-byte.
- Parse the decisions CSV with `csv.DictReader`; verify D-110 uniqueness, position, six fields, values, and diff shape. Run `python scripts/checks/scope_evidence_check.py`.
- Follow both README setup paths: Python 3.11, install requirements and pinned tools, confirm pre-commit resolves from `.venv`, then run ruff, mypy, and engine tests.
- Run CI, CodeQL, Verify Roadmap Tasks, and team-ai checks on the PR.
- Only after founder merge confirmation, dispatch both deploy workflows on `main` and confirm successful preflight, skipped deploy, and the visible notice.

---

# Risks and Unknowns

**Risks**:
- A partially configured deployment intentionally fails and identifies missing setting names so configuration can be completed.
- A `uv` virtual environment is unseeded by default; installing pre-commit with system `pip` would target a different Python. Both documented paths therefore use their active environment's package installer.

**Unknowns**:
- Actual credentials, deployment success, and live post-merge skip behavior are not verified before merge; Task 5 is the explicit follow-up gate.

---

# Open Questions

None for this approved implementation. Task 5 remains gated on founder merge confirmation.