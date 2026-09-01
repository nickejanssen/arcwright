# Nightcap Paper Test #2 v3.0 - A Knock at Midnight

**Status:** Draft fixture. Not current. Not published. Not approved for external tester distribution yet.

**Fixture ID:** `nightcap-paper-test-02-v3.0`  
**Fixture version:** `3.0`  
**Case:** *A Knock at Midnight*  
**Canon:** NON-CANON RESEARCH FIXTURE  
**Authority base:** Nightcap GDD at reconciliation commit `d62f01c37194721c07db019e8d1431df582e4174` unless that branch is merged before integration.

## Purpose

This is the next representative Gate 1 Time-to-Fun / Cohesion attempt after v2.2. It does not patch or reuse *The Last Toast*. It tests whether the revised Nightcap design produces stronger detective agency, clearer actions without handholding, scene-first discoveries, player-owned inference, visible rivalry, a murder-facing competitive pulse, understandable Leverage, satisfying commitment/reveal, and stronger replay pull.

## Research hypotheses

- **H1 Detective agency:** bounded-open investigation with several live options improves detective feeling relative to v2.2.
- **H2 Clarity without handholding:** contextual copy explains actions and consequences without explaining clue meaning.
- **H3 Observation before interpretation:** discoveries present what the player saw/heard/found and leave implications to the player.
- **H4 Competitive cohesion:** visible rival activity, The Locked Box, and one bounded information-war choice increase energy without making the murder unfair.
- **H5 Pull:** the revised flow improves fun, detective feeling, finish rate, and replay intent.

## Explicit exclusions

This fixture does **not** validate final multiplayer balance, 7–8 player viability, exact 2-vs-4 scaling, production Leverage sourcing/economy, final Case Board UX, Gate 2 memory optimization, production Structured Reconstruction UI, final minigame pool, final Postmortem, final runtime, or production simultaneous lock-picking support.

The authored rival **Nora Vance** is research scaffolding only. Her behavior cannot validate real-player rivalry.

## Approved case truth

Clara Hensley is the killer. Gideon March discovers that Clara has been feeding selected confidential research into Lenora Quill's fraudulent séances. During a confrontation in the writing room, Clara kills Gideon with a brass bookend. She substitutes Gideon's prerecorded cylinder 43 into Quill's concealed direct-voice apparatus. Quill unknowingly plays it during the séance while Clara is visibly present, creating the false impression that Gideon is alive later than he really is. Edwin Rusk finds cylinder 43 after the séance and locks it away to protect the hotel's role in Quill's fraud.

The essential truths are encoded in `case.json` with redundant evidence routes. The lock minigame is never the sole route to an essential truth.

## The Locked Box

The fixture uses a research-only lock-picking race. The human player performs a four-pin timing challenge against a deterministic authored rival clock. A human win grants temporary private first access to cylinder 43. A rival win creates a contextual `Listen In` Leverage opportunity. Break, timeout, or abort releases the cylinder publicly. After the finite first-look window, the cylinder becomes normal investigation material.

This is **not** a claim that the production Evidence Locker package supports simultaneous active pickers. The current production contract supports 2–8-player sessions with one selected active picker. This fixture is testing whether the simultaneous-race fantasy is worth pursuing.

## Leverage

The tester begins with exactly **1 test-granted Leverage**. This is an instrument control, not a production earning rule.

Only two contextual effects appear:

- **Listen In:** copy the rival's private observation after a rival lock win.
- **Follow the Thread:** take one contextual follow-up after an eligible interview.

Spending never changes truth, deletes proof, or makes the case unsolvable.

## Telemetry contract

One ordered event stream is the source of truth. Every event uses:

`sequence -> elapsed_ms -> phase -> event_type -> target -> choice -> outcome`

The fixture records opening completion, investigation choices, discoveries, player-initiated inference actions, rival activity, competitive-window start, lock actions/result, Leverage spend/save, post-lock return, Last Call, Case File commitment, gameplay completion, survey handoff, local reveal return, and voluntary abandonment where observable.

Derived metrics include time to first investigation, first discovery, first inference action, route diversity, lock completion time, post-lock return time, Last Call timing, completion status, and abandonment point.

Legacy v2.2 summary fields are derived only for compatibility with the existing form. They are not a second telemetry authority.

## Case File

Structured Reconstruction asks for one culprit plus **four or five facts**. Four facts support compact high-confidence routes; a fifth slot preserves equivalent Rusk-based and other redundant routes without making Beatrice's confrontation testimony a hidden interface bottleneck.

## Survey and reveal boundary

The current form ID remains `262397917027062`. Read-only inspection on 2026-08-31 confirmed the enabled form still exposes the 31-question structure used by v2.2, including every telemetry field mapped by `JOTFORM_FIELD_MAP`. No survey-field or hidden-field mutation is required for the v3 fixture: additional v3 timings remain derivable from the canonical `event_sequence`.

The v3 catalog records instrument version `3.0` because the fixture/event semantics and research contract changed, while the physical Jotform field layout remains compatible and unchanged.

When the player opens the survey, the fixture first records gameplay completion and then records `survey_handoff`. That makes `completed_at`, `duration_seconds`, and `completion_status=completed` available in the same prefill submission while keeping reveal-return as a separate research event. The survey screen does not expose a local truth-preview bypass.

The fixture preserves the same anonymous `run_id` in the prefill URL. If the form returns the player to this fixture in the same tab, `sessionStorage` can record `reveal_return` locally.

**That does not constitute externally verified reveal-return evidence.** The available Jotform connector does not expose redirect/settings metadata, so redirect behavior has not been changed or claimed verified. Before this fixture is sent to external testers, Harness must verify the complete form-submit -> fixture-return path through an explicitly approved smoke submission or another approved externally observable mechanism tied to the same run ID.

## Refresh / re-entry

The fixture stores exact session state in a v3-specific `sessionStorage` record. Refresh must not duplicate:

- major investigation choices;
- discoveries;
- rival events;
- lock resolution;
- first-look delivery;
- Leverage spend;
- Last Call;
- Case File commitment;
- gameplay completion;
- survey handoff;
- local reveal return.

## Test commands

```bash
node --test \
  playtests/nightcap-paper-test-02-v3.0/tests/runtime.test.mjs \
  playtests/nightcap-paper-test-02-v3.0/tests/fixture.test.mjs \
  playtests/nightcap-paper-test-02-v3.0/tests/rusk-route.test.mjs \
  playtests/nightcap-paper-test-02-v3.0/tests/survey-flow.test.mjs
```

The Pages deployment workflow is configured to run the published v2.2 tests and all four v3 test files before any future deploy.

## Draft registration / build evidence

The Steward CLI's `new --use-existing-source` path was added specifically to register already founder-approved fixture content without overwriting it. A metadata-only mirror using the actual branch CLI and catalog validator successfully registered this fixture as `draft` with `published: null`, while preserving `current_tests.nightcap = nightcap-paper-test-02-v2.2`.

Using the actual branch catalog/build logic, a deterministic mirror build generated the immutable `/nightcap/paper-test-02/v3.0/` route and listed v3 as draft on the Nightcap index while the root/current link remained v2.2. This is build-logic evidence, not a live Pages deployment or real-browser check.

Static responsive/accessibility inspection confirms a one-column choice layout below 640 CSS pixels, minimum 44-pixel button height, full-width mobile action buttons, visible focus outlines, reduced-motion handling, text plus visual lock status, and high-contrast primary text/button combinations. This is source-level evidence only; real-browser and real-phone layout remain separate checks.

## Required pre-send harness checks

- human lock win + Leverage save/use path;
- rival lock win + Listen In spend/save;
- break, timeout, and abort fallback;
- red-herring-first investigation;
- a route reaching Case File without relying on winning the lock;
- independent Rusk chronology/reconstruction route without Beatrice testimony;
- refresh during lock;
- refresh after lock result / first-look;
- refresh during partial Case File selection;
- voluntary abandonment handling where observable;
- real 360px/mobile browser rendering;
- survey handoff with same run ID;
- externally observable reveal-return proof;
- live Pages route verification after publication approval.

## Publication boundary

Do not overwrite v2.2. Do not promote this fixture to `current`, mutate Jotform, publish Pages, send a verification submission, or treat it as ready for external testing without the separate founder approvals required by `playtests/AGENTS.md`.
