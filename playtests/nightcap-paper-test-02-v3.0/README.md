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

The fixture records opening completion, investigation choices, discoveries, player-initiated inference actions, rival activity, competitive-window start, lock actions/result, Leverage spend/save, post-lock return, Last Call, Case File commitment, survey handoff, local reveal return, completion, and voluntary abandonment where observable.

Derived metrics include time to first investigation, first discovery, first inference action, route diversity, lock completion time, post-lock return time, Last Call timing, completion status, and abandonment point.

Legacy v2.2 summary fields are derived only for compatibility with the existing form. They are not a second telemetry authority.

## Survey and reveal boundary

The current form ID remains `262397917027062` for draft compatibility. This fixture does **not** mutate the form.

The fixture records `survey_handoff` before navigating to the form and preserves the same anonymous `run_id` in the prefill URL. If the form returns the player to this fixture in the same tab, `sessionStorage` can record `reveal_return` locally.

**That does not constitute externally verified reveal-return evidence.** Before this fixture is sent to external testers, Research + Harness must choose and verify the smallest approved observation mechanism that can prove reveal return tied to the same run ID. A redirect configuration alone is insufficient.

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
- survey handoff;
- local reveal return.

## Test commands

```bash
node --test playtests/nightcap-paper-test-02-v3.0/tests/runtime.test.mjs playtests/nightcap-paper-test-02-v3.0/tests/fixture.test.mjs
```

## Required pre-send harness checks

- human lock win + Leverage save/use path;
- rival lock win + Listen In spend/save;
- break, timeout, and abort fallback;
- red-herring-first investigation;
- a route reaching Case File without relying on winning the lock;
- refresh during lock;
- refresh after lock result / first-look;
- refresh during partial Case File selection;
- voluntary abandonment handling where observable;
- 360px mobile layout;
- survey handoff with same run ID;
- externally observable reveal-return proof;
- static site build after a draft catalog entry exists.

## Publication boundary

Do not overwrite v2.2. Do not hand-edit `playtests/catalog.json` from an environment that cannot run the Steward CLI. Do not promote this fixture to `current`, edit Jotform, publish Pages, or treat it as ready for external testing without the separate founder approvals required by `playtests/AGENTS.md`.
