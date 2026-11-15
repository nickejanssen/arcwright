---
id: productroadmap.roadmap.tasks.aw-298-require-the-ci-and-knowledge-base-checks-before-merging-to-main
namespace: product-roadmap
title: "AW-298: Require The CI And Knowledge-Base Checks Before Merging To Main"
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-298: Require The CI And Knowledge-Base Checks Before Merging To Main

**Milestone / Epic:** M7 / M7-A  
**Size:** S  
**Product:** Shared (Arcwright and Nightcap)  
**Owner:** Founder  
**Target date:** 2026-11-21

## Plain-English Summary

Today a pull request can merge with the web tests, the secret scan or the knowledge-base validation failing, because only one check is required. Make the other two required.

## Why This Matters

Verified on 15 November 2026 through the GitHub API: branch protection on `main` requires only `verify` (Python lint, types, engine tests). The `Lint, Typecheck, Test, Build, and Scan` job and the `team-ai` job are optional. A change that breaks the web client, leaks a secret or breaks knowledge-base front matter can land with a green required check.

## Technical Scope

- Your steps: open the repository on GitHub, then Settings, then Branches, then edit the rule for `main`.
- Under "Require status checks to pass before merging", search for and add `Lint, Typecheck, Test, Build, and Scan` and `team-ai`. Keep `verify`.
- Save. Both workflows run on every pull request with no path filter, so requiring them cannot leave a pull request waiting on a check that never starts.

## Human Collaboration Contract

**Interaction profile:** Founder action. Only a repository admin can change branch protection. About ten minutes.

## Acceptance Criteria

- [ ] `gh api repos/nickejanssen/arcwright/branches/main/protection` lists three required checks: `verify`, `Lint, Typecheck, Test, Build, and Scan`, `team-ai`.
- [ ] `HANDOVER.md` no longer lists the single required check as a known issue.

## Tests/Verification

- The API call above, run by any session after the change.

## Dependencies

- None
- Findings and evidence: `docs/product/2026-11-15-reset-audit.md`

## Must Not Do

- Do not require CodeQL or the eval workflow: the eval workflow only runs on some paths and would block unrelated pull requests.
