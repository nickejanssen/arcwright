---
id: nightcap.gdd.nightcap.03-playtest-evidence.99-paper-test-02-v3.1-validation
namespace: nightcap
title: Nightcap Paper Test 2 v3.1 Validation Ledger
owner: Nico Janssen
status: active
review_by: "2027-04-01"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Nightcap Paper Test 2 v3.1 Validation Ledger

**Status:** Draft tracking ledger, 2026-10-01. All 32 acceptance rows remain pending until their required evidence exists.
**Authority:** `docs/specs/0091-nightcap-v3.1-improvements.md` and `docs/superpowers/plans/2026-10-01-nightcap-v3.1-improvements.md`.
**Fixture:** `nightcap-paper-test-02-v3.1`, non-canon, not catalog registered or published at Task 1 start.

Each implementation, automated, browser, human and external column is independent. `Pending` means no v3.1 evidence recorded. Historical v3.0 QA is not carried forward as v3.1 validation. Automated evidence can establish source behavior only; it cannot establish fun, prose quality, phone operation, Jotform read-back or return.

| Item | Required outcome                                                                                                                 | Task    | Required evidence | Implementation                                                     | Automated         | Browser | Human   | External | Overall |
| ---- | -------------------------------------------------------------------------------------------------------------------------------- | ------- | ----------------- | ------------------------------------------------------------------ | ----------------- | ------- | ------- | -------- | ------- |
| 01   | Explicit spend/save/unused distinct, including human-win-save                                                                    | 1, 3    | A, B              | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 02   | Click uptake distinguished from deduction; neutral debrief                                                                       | 1, 2    | A, H              | Task 1 protocol and Task 2 events present                          | Source reviewed   | Pending | Pending | Pending  | Pending |
| 03   | Missingness cannot fabricate pass; sample limits explicit                                                                        | 1       | A                 | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 04   | Accurate interval endpoints and interpretation                                                                                   | 1, 3    | A                 | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 05   | Gameplay/submission/reveal separate; phone handoff verified                                                                      | 1, 5, 6 | A, B, E           | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 06   | Consistent approval prose; triage records evidence, cause, class, confidence, smallest fix and what would disprove the diagnosis | 1       | A                 | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 07   | Each fact established by an earned visible encounter                                                                             | 2, 4    | A, H              | Task 2 provenance added; Task 4 editorial review pending           | Source tests pass | Pending | Pending | Pending  | Pending |
| 08   | Earned transcript and private notes retained without new grants                                                                  | 2       | A, B              | Implemented                                                        | Node tests pass   | Pending | Pending | Pending  | Pending |
| 09   | Costs/cap/free questions consistent in runtime and UI                                                                            | 2       | A, B              | Implemented                                                        | Node tests pass   | Pending | Pending | Pending  | Pending |
| 10   | Clear decline path preserving solvability                                                                                        | 3       | A, B, H           | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 11   | Clear contextual actions without supplied inference                                                                              | 2, 4    | A, H              | Task 2 gates/prompts added; Task 4 prose review pending            | Source tests pass | Pending | Pending | Pending  | Pending |
| 12   | Public hooks and earned suspect history without spoilers                                                                         | 2, 4    | A, H              | Task 2 UI added; Task 4 prose review pending                       | Source tests pass | Pending | Pending | Pending  | Pending |
| 13   | Untimed instructions, accurate deadline and input wording                                                                        | 3       | A, B, H           | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 14   | Stable focus; truthful accessibility assessment                                                                                  | 3, 6    | A, B, H           | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 15   | Input timing checked; first-use tuning evidence recorded                                                                         | 3, 6    | A, B, H           | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 16   | Acquired information and expiry visible and precise                                                                              | 3       | A, B, H           | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 17   | Justified rival trajectory independent of lock winner                                                                            | 3, 4    | A, H              | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 18   | Concise causal release/rival transitions                                                                                         | 3, 4    | A, H              | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 19   | Clear player role, purpose, and rivalry                                                                                          | 4       | H                 | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 20   | Distinguishable suspect voices                                                                                                   | 4       | H                 | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 21   | Attributable testimony; alternate routes preserved                                                                               | 2, 4    | A, H              | Task 2 transitions added; Task 4 editorial review pending          | Route tests pass  | Pending | Pending | Pending  | Pending |
| 22   | Credible stakes grounded in existing truth                                                                                       | 4       | H                 | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 23   | Delivered evidence supports timeline/access causal chain                                                                         | 2, 4    | A, H              | Task 2 transitions added; Task 4 editorial review pending          | Route tests pass  | Pending | Pending | Pending  | Pending |
| 24   | Samples and full prose reviewed by founder                                                                                       | 4       | H                 | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 25   | Count/review reduce bookkeeping; proxy limitation explicit                                                                       | 5       | A, B, H           | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 26   | Justified sufficient proof sets with legal acquisition paths                                                                     | 2       | A, H              | Legal paths implemented; causal sufficiency pending founder review | Route tests pass  | Pending | Pending | Pending  | Pending |
| 27   | Post-truth verdict explains decisive reason                                                                                      | 5       | A, B, H           | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 28   | Missing-state reveal fabricates no failure or completion                                                                         | 5       | A, B              | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 29   | Correct visibility/outcome-specific QA assertions                                                                                | 6       | A, B              | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 30   | Physical device distinguished from CSS viewport                                                                                  | 1, 6    | A, H              | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 31   | Long URL, submitted read-back, storage and return checked                                                                        | 5, 6    | A, B, E           | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |
| 32   | Immutable versions, bounded scope, exclusions and gates                                                                          | 1, 6    | A, E              | Pending                                                            | Pending           | Pending | Pending | Pending  | Pending |

## Task evidence

### Task 1: Successor baseline and research protocol

- Task 1 implementation was committed at `a0083ab5dd0b289fc877b8068d2f9730a4ee3f62`. This records technical completion only; the 32 acceptance rows retain their distinct browser, human and external gates.
- Base HEAD: `59a08dd7083d46e0ba75a99c1de22a18220465dc` on `claude/phase-1-v3-send-readiness`; no pre-existing working changes were reported by `git status --porcelain=v1`.
- Published source tree IDs at base: v2.2 `17e5c904120bdf76f2ae3699ba826cb1c2e22ebc`; v3.0 `0c11a929319a741e71daef732e85ef73e52258f3`. Recheck after each task.
- Original 32-item improvement review remains at `docs/gdd/nightcap/04-supporting-design/99-paper-test-02-v3.0-improvement-review.md`; it was not rewritten.
- Controller read-only preflight on 2026-10-01: `python scripts/playtest_tool.py --json validate` returned `ok: true` with no errors. Jotform form `262397917027062` fetched read-only as ENABLED, with 31 questions, submission count 3 and updated timestamp `2026-08-28 22:09:50`. The fetch exposed field labels, not redirect or partial-save settings. No submissions were fetched. This is external settings context, not form return evidence.
- Research helper RED: three intended assertion failures with the initial stub under `node --test playtests/nightcap-paper-test-02-v3.1/tests/research.test.mjs`. This Node binary rejected `--experimental-default-type=module`; the explicit `node --test` invocation emitted only a module-type warning in addition to assertion failures.
- Task 1 GREEN on 2026-10-01: `node --test playtests/nightcap-paper-test-02-v3.1/tests/research.test.mjs playtests/nightcap-paper-test-02-v3.1/tests/runtime.test.mjs playtests/nightcap-paper-test-02-v3.1/tests/fixture.test.mjs playtests/nightcap-paper-test-02-v3.1/tests/rusk-route.test.mjs playtests/nightcap-paper-test-02-v3.1/tests/security.test.mjs playtests/nightcap-paper-test-02-v3.1/tests/survey-flow.test.mjs` returned 35 tests, 35 passed, 0 failed. Node emitted `MODULE_TYPELESS_PACKAGE_JSON` warnings; this installed binary rejected `--experimental-default-type=module`. No package setting was changed.
- Published v2.2/v3.0 tracked sources had no working diff and no untracked files under their paths at Task 1 final check. Their Git tree IDs match the base IDs above. The fixture copy, protocol, helper, tests and ledger are Task 1 artifacts only. Browser, human and external checks remain pending.
- Task 1 self-review: the change set is confined to the successor fixture, its research protocol and ledger, and the stale v3.0 approval paragraph. No Task 2 gameplay behavior or catalog metadata is included. A separate task reviewer remains pending before Task 2.
- Task 1 commit hook on 2026-10-01: gitleaks, Prettier, ESLint, and temporary-marker checks passed; Ruff hooks skipped because no Python files were staged. The focused Node suites and `git diff --check` also passed.

### Task 2: Investigation and proof acquisition

- Focused TDD RED: `node --test playtests/nightcap-paper-test-02-v3.1/tests/investigation.test.mjs` reported six intended assertion failures for missing transition functions. Runtime transition, earned history and notes implementation then made all six pass.
- Legal paths use `visitInvestigation`, `challengeClaim`, `followThread`, lock and Last Call transitions; no major action counter or discovery is seeded. Beatrice, Rusk without Beatrice confrontation testimony, rival lock win and red herring first paths pass. A single Leverage cannot earn both descriptive motive-route follow-ups.
- Successor suite on 2026-10-01: `node --test` from `playtests/nightcap-paper-test-02-v3.1` passed 49 tests, 0 failed. The installed Node emits `MODULE_TYPELESS_PACKAGE_JSON` warnings; no dependency or package setting changed. `git diff --check` passed. Browser, founder and external evidence remains pending.
- Prettier check passed for all ten Task 2 files. `node --check` passed for `app.js` and `runtime.js`. ESLint was unavailable in the safe checkout: invoking the existing ESLint 10.4.0 binary from the `65b9` checkout against Task 2 JavaScript files exited 1 with `ERR_MODULE_NOT_FOUND` for `@eslint/js` imported by this checkout's `eslint.config.mjs`. No dependency was installed or changed.
- Proof dossier enumerates scorer-minimal sets, unreachable two-reward combinations and the compressed inference. Automated reachability does not settle whether the Rusk and motive groups are causally sufficient; founder artifact review is pending before any authored proof correction.

## Browser, device and debrief evidence template

Record: date; artifact commit; anonymous local QA run label; physical device or emulated viewport; CSS width; browser family/version; operating system; input method; encounter/action; expected and observed result; evidence location; limitation. Do not record private identities or raw comments here. Warn before a live timed lock and keep Browser-pane work in the controller session.

Private debrief uses the two approved descriptive prompts in the v3.1 analysis plan. Log only counts and anonymized conclusions here after consent and review. Separate automated, browser, founder and external evidence. A human or external column remains pending until that action actually occurs.

## Feedback triage template

| Encounter | Observed problem | Supporting evidence | Likely cause | Game/Fidelity/Harness | Confidence | Affected hypothesis | Smallest fix | Acceptance check | What would disprove the diagnosis |
| --------- | ---------------- | ------------------- | ------------ | --------------------- | ---------- | ------------------- | ------------ | ---------------- | --------------------------------- | ------- |
| Pending   | Pending          | Pending             | Pending      | Pending               | Pending    | Pending             | Pending      | Pending          | Pending                           | Pending |

## Scope and release gates

Published v2.2 and v3.0 sources must remain byte-for-byte unchanged. The v3.1 catalog draft registration belongs to Task 6. `current_tests.nightcap` stays v3.0 until a separately approved promotion. This ledger records local evidence; publication, survey changes, smoke submissions, live phone sessions, external invitations and durable product decisions each require their own action and evidence. The actual Jotform return target is still unknown.
