# AW-212: Knowledge-Constrained Dialogue Pipeline

**Milestone / Epic:** M2 / M2-E  
**Size:** L  
**Status:** Planned

## Plain-English Summary

Generate character dialogue through knowledge query, safety, routing, and event emission.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/04-knowledge-graph.md S4.3` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Generate character dialogue through knowledge query, safety, routing, and event emission. Likely files affected: engine/characters, engine/knowledge, engine/safety, engine/events, engine/tests.

Scope guard: this is current-session Nightcap v1 dialogue work only. "Event emission" means recording or returning the dialogue event through the existing persistence or local engine path needed by this task. It does not mean building the M3 ContentEvent bus, SSE fanout, or replay system.

## Acceptance Criteria

- [ ] `get_character_knowledge` is called before every AI character dialogue generation.
- [ ] Dialogue prompts include explicit known and not-known knowledge constraint blocks.
- [ ] Tests prove a mocked generation path cannot emit dialogue containing facts outside the character knowledge state.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-210
- AW-211

## Likely Files Affected

engine/characters, engine/knowledge, engine/safety, engine/events, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.
- Do not implement Nightcap Continuity, cross-session group memory, recap artifacts, continuity consent, retention, deletion, or reuse flows. Those are v1.1 scope per D-051 and D-055.
- Do not implement two- or three-player support, interrogatable AI player-slot fillers, or AI participants that can fill empty player slots and be the killer. Those are v1.1 scope per D-052.
- Do not encode a platform-level fixed beat count. Nightcap uses eight Story Circle beats as an arc-level property per D-053.
- Do not implement Nightcap v1 personalization intake prompts beyond consuming already-available current-session context. Intake definition belongs to the D-054 follow-up.
- Do not wire mini-game behavioral-read outputs into killer assignment or dialogue policy. D-058 keeps v1 killer assignment constrained-random and defers behavioral signal wiring to v1.1.
- Do not implement AI initiative scheduling or NPC-NPC exchange. That belongs to AW-213.

## Architecture References

- docs/architecture/04-knowledge-graph.md S4.3
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
