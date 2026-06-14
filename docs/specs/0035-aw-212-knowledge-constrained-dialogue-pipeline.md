# AW-212 Knowledge-Constrained Dialogue Pipeline

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-14

---

# References

- Related ADRs: `docs/decisions/0006-nightcap-continuity-v11.md`
- Architecture sections: `docs/architecture/04-knowledge-graph.md` S4.3, `docs/architecture/07-character-behavior.md` S7.3, `docs/architecture/10-content-safety.md` S10.4
- Related specs: `docs/specs/0013-aw-106-pre-generation-knowledge-constraint-hook.md`, `docs/specs/0033-aw-210-l3-policy-injection.md`, `docs/specs/0034-aw-211-behavior-profile-assembly.md`
- PRD sections: `docs/prd/03-scope.md`
- Product decisions: D-051, D-052, D-053, D-054, D-055, D-058 in `docs/product/decisions-log.csv`
- Roadmap task: `docs/roadmap/tasks/AW-212-knowledge-constrained-dialogue-pipeline.md`
- GitHub issue: `https://github.com/nickejanssen/arcwright/issues/65`

---

# Overview

AW-212 defines the current-session dialogue pipeline for AI character speech in Nightcap v1. The pipeline must query character knowledge first, build explicit known and not-known prompt blocks, route through the approved safety and model-routing entrypoint, and record or return the resulting dialogue event without expanding into v1.1 or M3 event-system scope.

---

# In Scope

- Add a character dialogue generation entrypoint in `engine/characters`.
- Require current-session character knowledge before every AI character dialogue generation.
- Build prompt messages with explicit known and not-known knowledge constraint blocks.
- Include existing AW-211 runtime character context where available: behavior profile, relationship dispositions, and participant control mode.
- Route dialogue through the approved generation path so L1, L2, L3, routing, and generation logging remain active.
- Use task type `character_dialogue` and a caller-provided quality tier.
- Record or return the generated dialogue as the local event representation needed for this task.
- Add focused tests proving the knowledge constraint path cannot emit dialogue containing facts outside the character knowledge state when generation is mocked.

---

# Out of Scope

- Nightcap Continuity, cross-session group memory, recap artifacts, continuity consent, retention, deletion, or reuse flows. These remain v1.1 scope per D-051, D-055, and `docs/decisions/0006-nightcap-continuity-v11.md`.
- Two- or three-player support, interrogatable AI player-slot fillers, or AI participants that fill empty player slots and can be the killer. These remain v1.1 scope per D-052.
- Any platform-level fixed beat-count assumption. D-053 says Nightcap uses eight Story Circle beats as an arc-level property, not as an engine property.
- Defining Nightcap v1 personalization intake prompts. D-054 adds intake to v1, but exact prompt and data-shape definition is separate follow-up work.
- Wiring mini-game behavioral-read outputs into killer assignment or dialogue policy. D-058 keeps v1 killer assignment constrained-random and defers behavioral signal wiring to v1.1.
- AI initiative scheduling or NPC-NPC exchange. That belongs to AW-213.
- M3 `ContentEvent` bus, SSE fanout, replay, SDK, API, or client delivery work.
- New dependencies, schema changes, migrations, provider strings, model strings, prompts that bypass safety, or surface-specific rendering behavior.

---

# Acceptance Criteria

- [ ] `get_character_knowledge` or the sanctioned AW-106 generation-context path is called before every AI character dialogue generation.
- [ ] Dialogue prompts include explicit known and not-known knowledge constraint blocks.
- [ ] Dialogue generation routes through the approved safety and routing entrypoint, not directly through `route_generation`.
- [ ] The generated dialogue is recorded or returned with session ID, actor character ID, target information, and structured payload sufficient for later event-system integration.
- [ ] Tests prove a mocked generation path cannot emit dialogue containing facts outside the character knowledge state.
- [ ] Tests prove the pipeline does not require or create Nightcap Continuity, AI player-slot fillers, NPC-NPC exchange, or M3 event-bus behavior.

---

# Test Plan

- Unit tests: prompt assembly includes known and not-known blocks from current-session knowledge context.
- Unit tests: generation entrypoint queries knowledge before the generation call.
- Unit tests: mocked allowed output is persisted or returned as dialogue with the expected actor and session metadata.
- Unit tests: mocked output containing an unknown fact is blocked, rejected, or converted to a neutral event according to the implementation design.
- Regression tests: no provider or model strings are introduced outside `config/routing_table.json` and `engine/routing/router.py`.
- Commands:
  - `python -m pytest engine/tests/test_character_dialogue.py -q`
  - `python -m pytest engine/tests/test_character_generation_context.py -q`
  - `python -m ruff check engine/characters engine/tests`
  - `python -m ruff format --check engine/characters engine/tests`

---

# Risks and Unknowns

**Risks**:
- If callers can bypass the dialogue entrypoint, knowledge constraints can become optional. The implementation should make the sanctioned entrypoint the only character dialogue path exposed by `engine.characters`.
- If "event emission" is interpreted as the M3 bus, AW-212 will sprawl across milestone boundaries. For this task it means only the local persisted or returned dialogue event needed by the engine.
- If prompt constraints are treated as sufficient without mocked-output validation, tests may miss leakage of unknown facts.

**Unknowns**:
- The exact shape of future M3 `ContentEvent` delivery may change. AW-212 should keep its event payload structured and simple so M3 can adapt it without rewriting dialogue generation.
- Exact D-054 intake prompt fields remain open. AW-212 may consume existing current-session context but must not define or require the intake flow.

---

# Open Questions

- None blocking AW-212 after the scope guards above.
