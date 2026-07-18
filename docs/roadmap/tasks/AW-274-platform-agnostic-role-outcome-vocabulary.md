# AW-274: Platform-Agnostic Role, Knowledge-Seeding, and Session-Outcome Vocabulary

**Milestone / Epic:** M5 / M5-C
**Size:** M
**Status:** Planned

## Plain-English Summary

Remove murder-mystery (Nightcap) vocabulary that is hardcoded into shared
platform code, the arc schema, the session-end API, the `session_completed`
telemetry payload, and the harness, and replace it with generic,
arc-configurable mechanisms. Nightcap keeps identical behavior by supplying
the concrete values in `nightcap/arc.json`.

## Why This Matters

These identifiers (`killer_assignment`, `killer_knows_they_did_it`,
`murder_timing_range`, `killer_identified`, harness `_KILLER_ROLE`) were
introduced under AW-206 but sit in platform-shared code. The agnosticism
pass in #213 generalized beat/element hardcodes and did not generalize this
role/outcome vocabulary. It violates Architecture Principle #1 (surface/game
agnosticism) and #4 (unified role model): a second game or third-party arc
cannot express its own hidden roles, knowledge seeding, event timing, or
resolution outcome without editing platform code.

## Player Impact

No direct player-visible change for Nightcap (behavior-preserving). Unlocks a
correctly-agnostic platform so future games reach players without platform
forks.

## Business Value

Directly supports the M5-C second-arc proof and the H1 platform thesis: the
engine must run a second experience without game-specific edits. Removes
tech debt that would otherwise compound with every new arc.

## Technical Scope

- Generalize three arc-schema fields in `engine/arc/models.py` (generative
  role assignment, per-role knowledge seeding, timed-event range).
- Replace the `killer_identified` session-end outcome with arc-declared
  generic `resolution_outcomes` across `api/schemas`, `api/routers/sessions.py`,
  `engine/session/service.py`, and `engine/telemetry/session.py`.
- Replace harness role constants in `engine/harness/runner.py` and
  `engine/harness/scenario.py` with a generic role key from arc/runtime config.
- Supply concrete Nightcap values in `nightcap/arc.json` for behavior parity.
- Author the ADR the spec requires (schema + API + telemetry decision).

## Human Collaboration Contract

**Interaction profile:** Decision interview.

**Founder input:** Preferred platform-agnostic vocabulary, compatibility policy
for schemas, APIs, and telemetry, and rollout sequencing.

**Required flow:** Map the current terms and compatibility constraints, then
explain the consumer impact and migration consequences in plain language.
Present two or three viable vocabulary and compatibility approaches with a
recommendation. Ask one focused interactive choice question at a time, confirm
the selected approach and sequence, and record only the approved decision.

**Gate:** Schema, API, telemetry, and migration changes stop until the founder
explicitly approves the named vocabulary, compatibility behavior, and sequence.

**Evidence:** Preserve the mappings, options, recommendation, explicit approval,
approval date, compatibility commitments, and owner actions.

## Acceptance Criteria

- [ ] `git grep -iE "killer|murder" -- engine/ api/` returns nothing outside
  `engine/safety/` (owned by #219) and comments.
- [ ] Nightcap behavior unchanged via `nightcap/arc.json`; seeded harness
  replay reproduces identical role assignment and reveal state (AW-206
  determinism preserved).
- [ ] A second arc with a different hidden role and resolution outcome
  validates and runs end-to-end with no platform code change.
- [ ] Session-end API + `session_completed` telemetry carry generic
  `resolution_outcomes`; `killer_identified` back-compat implemented and
  documented (SDK impact noted).
- [ ] ADR referenced from spec 0070 before implementation; PR flags the
  schema + API + telemetry + cross-module hard rules.

## Tests/Verification

- Schema validation, knowledge-seeding, and generic-outcome unit tests pass.
- Golden/replay integration test: Nightcap seeded run identical to `main`.
- Synthetic second-arc run to session completion with non-Nightcap role and
  outcome.
- Guard test (`test_aw256_beat_hardcode.py` or sibling) asserts no
  role/outcome hardcodes remain in shared engine/api modules.

## Dependencies

- `docs/specs/0070-aw-274-platform-agnostic-role-outcome-vocabulary.md`
- AW-206 (origin of the vocabulary), #213 (agnosticism pass)
- M5-C second-arc validation coverage (AW-235/AW-245/AW-256)

## Must Not Do

- Do not touch the safety-layer term lists (`engine/safety/l1.py`, `l2.py`,
  `l3.py`), that is issue #219's scope; changing safety heuristics here is a
  hard-rule violation.
- Do not add new gameplay capability; this refactor must be behavior-preserving
  for Nightcap.
- Do not change the live session-end contract without a back-compat path, the
  web SDK sends `killer_identified` today, right before Rehearsal 1 (AW-273).
- Do not implement before the spec's ADR is approved.

## Architecture References

- `docs/architecture/03-arc-execution.md` §3.4–3.7 (role assignment)
- `docs/architecture/04-knowledge-graph.md` (knowledge seeding)
- `docs/architecture/11-telemetry.md` (`session_completed` payload)
- `AGENTS.md` Architecture Principles #1 and #4

## Playtest Relevance

Pre-M6 tech-debt/agnosticism refactor. Behavior-preserving for Nightcap;
sequence consciously relative to Rehearsal 1 (AW-273) because it touches the
live session-end path.
