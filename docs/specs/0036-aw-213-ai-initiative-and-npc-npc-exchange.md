# AW-213 AI Initiative And NPC-NPC Exchange

**Status**: Approved

**Author**: Claude Code
**Date**: 2026-06-14

---

# References

- Related roadmap task: `docs/roadmap/tasks/AW-213-ai-initiative-and-npc-npc-exchange.md`
- Architecture sections: `docs/architecture/07-character-behavior.md` S7.3-S7.6, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0034-aw-211-behavior-profile-assembly.md`, `docs/specs/0035-aw-212-knowledge-constrained-dialogue-pipeline.md`, `docs/specs/0033-aw-210-l3-policy-injection.md`, `docs/specs/0027-aw-207-dramatic-tension-pacing-engine.md`
- PRD sections: `docs/prd/01-overview.md`
- Product decisions: D-052, D-053, D-055, D-058 in `docs/product/decisions-log.csv`
- GitHub issue: `https://github.com/nickejanssen/arcwright/issues/66`

---

# Overview

AW-213 completes epic M2-E (Character Behavior Engine) by adding the initiative scheduler and NPC-NPC exchange generation. The scheduler lets AI characters take action without a player prompting them; NPC-NPC exchange generates dialogue between two AI characters with both sides' knowledge state and relationship dispositions in the prompt. The dispatch path must never block the session coordinator loop.

The design is platform-agnostic. The same primitives serve Nightcap NPC interrogation, Monster RPG ambient NPC behavior, and any future arc that needs AI characters acting on their own.

---

# In Scope

- Add `engine/characters/initiative.py` containing:
  - `InitiativeScheduler` and supporting dataclasses for evaluating which AI characters should act on a given session tick.
  - Deterministic NPC-NPC target selection.
  - `generate_npc_npc_exchange()` which builds a combined two-character system prompt, routes through the existing AW-212 safety and routing path, and supports both single-utterance and multi-turn exchanges via a `max_turns` parameter.
  - `schedule_initiative_tasks()` which dispatches scheduled actions via `asyncio.create_task()` and returns immediately so the session coordinator loop is never blocked.
- Reuse `build_character_generation_context()` from AW-211 unchanged. Knowledge state is re-queried per speaker per turn; nothing is cached across turns.
- Reuse the existing safety and routing pipeline. No new model strings, no new provider strings.
- Add focused tests covering all three acceptance criteria plus target-selection determinism and runtime threshold override.

---

# Out of Scope

- Schema changes, migrations, or new tables. The `behavior_profile.initiative_threshold` key reuses the existing JSONB column.
- Cross-session memory, recap artifacts, continuity consent, retention, deletion, or reuse flows. These remain v1.1 scope per D-051 and D-055.
- Interrogatable AI participants that fill empty player slots or can be the killer. These remain v1.1 scope per D-052.
- Mini-game behavioral-read inputs to initiative or NPC-NPC selection. D-058 keeps v1 killer assignment constrained-random and defers behavioral signal wiring to v1.1.
- A platform-level fixed beat count. Beat structure is an arc-level property per D-053.
- M3 ContentEvent bus, SSE fanout, replay, SDK, API, or client delivery work.
- Defining or owning the runtime threshold-calibration policy. AW-213 ships a calibration dial (`threshold_overrides`) that the session coordinator can pass in; deciding when to nudge it lives outside this task.
- Provider, model, or routing-table changes.
- Surface-specific rendering behavior.

---

# Design

## Initiative scheduler

Pure, deterministic, no I/O.

```text
CharacterInitiativeProfile:
    character_id: UUID
    is_ai_controlled: bool
    initiative_threshold: float   # from behavior_profile.initiative_threshold, fallback 0.6

InitiativeSessionState:
    seconds_since_last_player_action: float
    current_beat_id: str
    tension_score: float          # from AW-207

ScheduledInitiativeAction:
    initiating_character_id: UUID
    target_character_id: UUID | None
    target_type: Literal["npc", "player_group"]
    initiative_score: float

InitiativeScheduler.evaluate(
    character_profiles: list[CharacterInitiativeProfile],
    session_state: InitiativeSessionState,
    *,
    threshold_overrides: dict[UUID, float] | None = None,
    eligible_targets_by_character: dict[UUID, list[UUID]] | None = None,
    beat_character_emphasis: list[UUID] | None = None,
    relationships_by_character: dict[UUID, list[RelationshipDispositionContext]] | None = None,
) -> list[ScheduledInitiativeAction]
```

`initiative_score = 0.6 * normalized_idle + 0.4 * tension_score`, clamped 0.0-1.0. `normalized_idle` is `min(seconds_since_last_player_action / 60.0, 1.0)`. A character produces a `ScheduledInitiativeAction` when `initiative_score >= effective_threshold(character_id)`.

`effective_threshold(character_id)` lookup order: `threshold_overrides[character_id]` then `character.initiative_threshold` then `0.6`. This is computed per call, not frozen at session start, so the session coordinator can recalibrate during play.

## Deterministic target selection

`select_initiative_target(initiating_character_id, ...)` priority chain. First match wins:

1. **Beat character emphasis** — if `beat_character_emphasis` lists eligible AI characters other than the initiator, pick from that list first. The arc author has already told us who matters in this beat.
2. **Strongest relationship signal** — among remaining eligible AI characters, pick the one where the initiator has the largest `abs(trust_level - 0.5)`. Strong trust or strong distrust produces dramatic exchanges; neutral relationships produce filler.
3. **Most recently updated relationship** — tie-break by `RelationshipState.updated_at` descending. Caller is responsible for ordering relationships by recency before passing them in.
4. **Stable final tie-break** — lowest `target_character_id` UUID.

If no eligible AI target exists, `target_type` falls back to `"player_group"` and `target_character_id` is `None`.

## NPC-NPC exchange generation

```text
NpcNpcExchangeTurn:
    event_id: UUID
    actor_character_id: UUID
    content: str
    turn_index: int

NpcNpcExchangeEvent:
    exchange_id: UUID
    session_id: UUID
    initiating_character_id: UUID
    target_character_id: UUID
    turns: tuple[NpcNpcExchangeTurn, ...]

generate_npc_npc_exchange(
    db_session: AsyncSession,
    *,
    session_id: UUID,
    initiating_character_id: UUID,
    target_character_id: UUID,
    quality_tier: str,
    max_turns: int = 1,
    current_beat_id: str | None = None,
    scene_goal: str | None = None,
    tension_score: float | None = None,
    safety_policy_context: dict[str, Any] | str | None = None,
    content_rails: ContentRailsConfig | None = None,
    nightcap_mode: bool = False,
) -> NpcNpcExchangeEvent
```

For each turn, the function:

1. Calls `build_character_generation_context()` for the current speaker. (Mandatory knowledge requery per platform principle 5.)
2. Calls `build_character_generation_context()` for the other character to read relationship and identity context.
3. Assembles a combined system prompt with the same five-block structure AW-212 uses for the speaker, plus one extra block for the partner character identity and relationship-back direction. Knowledge constraints are enforced on the speaker only (the partner's knowledge informs how the speaker models the partner, but only the speaker may speak).
4. Routes through `engine.routing.generate` with task type `character_dialogue` and the caller-supplied quality tier. Safety layers L1, L2, L3 are active.
5. Persists an `Event` row with `event_type="npc_npc_exchange"` and a payload containing `exchange_id`, `turn_index`, `initiating_character_id`, `target_character_id`, both speakers' knowledge-constraint fact id lists, and `task_type`.
6. Swaps speakers and continues until `max_turns` is reached or a turn is safety-blocked. A safety-blocked turn ends the exchange early with a `dialogue_blocked` event for that turn.
7. If a generated turn references a fact outside the speaker's knowledge state, `KnowledgeConstraintViolation` is raised (same enforcement as AW-212).

## Non-blocking dispatch

```text
schedule_initiative_tasks(
    session_factory: Callable[[], AsyncContextManager[AsyncSession]],
    actions: list[ScheduledInitiativeAction],
    *,
    session_id: UUID,
    quality_tier: str,
    max_turns: int = 1,
    current_beat_id: str | None = None,
    scene_goal: str | None = None,
    tension_score: float | None = None,
    safety_policy_context: dict[str, Any] | str | None = None,
    content_rails: ContentRailsConfig | None = None,
    nightcap_mode: bool = False,
) -> list[asyncio.Task]
```

For each action, creates an `asyncio.Task` that opens its own DB session through `session_factory` and awaits `generate_npc_npc_exchange()` (or a single-utterance variant when `target_type == "player_group"`). Returns the list of `asyncio.Task` handles immediately. The caller may await them later, store them, or fire-and-forget. The session coordinator loop is never blocked. Tasks own their own DB sessions to keep the coordinator's session free.

---

# Acceptance Criteria

- [ ] `InitiativeScheduler.evaluate()` produces a non-empty list when a character's initiative score crosses its threshold without any player input parameter on the path, satisfying AC1.
- [ ] `generate_npc_npc_exchange()` includes both characters' known and not-known knowledge blocks and both directions of relationship context in the assembled prompt, satisfying AC2.
- [ ] `schedule_initiative_tasks()` dispatches via `asyncio.create_task()` and returns its task handles in a single event-loop tick without awaiting them, satisfying AC3.
- [ ] Target selection priority chain (`beat character_emphasis` then strongest relationship signal then recency then UUID) is deterministic and tested.
- [ ] Runtime `threshold_overrides` take precedence over `behavior_profile.initiative_threshold` and the global default.
- [ ] No provider strings or model strings are introduced outside `config/routing_table.json` and `engine/routing/router.py`.
- [ ] No schema or migration changes.

---

# Test Plan

- Unit test: initiative score below effective threshold produces no scheduled action.
- Unit test: initiative score at or above effective threshold produces a scheduled action with no player input on the path (AC1).
- Unit test: combined NPC-NPC prompt for `max_turns=1` includes both speakers' known and not-known fact blocks and both directions of relationship dispositions (AC2).
- Unit test: `max_turns=2` produces two persisted turns alternating speakers, with knowledge requeried per turn (AC2, calibration coverage).
- Unit test: `schedule_initiative_tasks()` returns task handles without awaiting them; event-loop timing assertion confirms the coordinator loop is not blocked (AC3).
- Unit test: target selection picks the beat-emphasized character when one is eligible; otherwise picks the strongest relationship signal; tie-breaks by recency then UUID.
- Unit test: `threshold_overrides[character_id]` takes precedence over `behavior_profile.initiative_threshold` and the global default, and a mid-evaluation override changes outcome on the next `evaluate()` call without re-instantiating the scheduler.
- Regression: no provider or model strings introduced outside `config/routing_table.json` and `engine/routing/router.py`.
- Commands:
  - `python -m pytest engine/tests/test_initiative.py -q`
  - `python -m pytest engine/tests/test_character_dialogue.py -q`
  - `python -m pytest engine/tests/test_character_generation_context.py -q`
  - `python -m ruff check engine/characters engine/tests`
  - `python -m ruff format --check engine/characters engine/tests`

---

# Risks and Unknowns

**Risks**:
- If the scheduler ever calls into generation directly instead of returning data, the non-blocking contract dies. The scheduler must remain pure.
- If knowledge context is cached across turns of a multi-turn exchange, character knowledge can drift from the live graph. Each turn must re-query.
- If `schedule_initiative_tasks()` shares the session coordinator's DB session, a task error or long-running call could affect coordinator state. Each task must take its own session via the `session_factory`.
- If `max_turns` is unbounded by the caller, NPC-NPC exchanges could run away. Callers should pick a small value (1-3) at MVP.

**Unknowns**:
- Runtime threshold-calibration policy (how a coordinator decides to nudge `threshold_overrides`) is not specified by this task and is left to a later session-coordinator task.
- Exact M3 ContentEvent shape is still open. NPC-NPC events are written through the existing local persistence path so a later M3 task can adapt them.

---

# Open Questions

- None blocking AW-213 after the scope guards above.

---

# Playtest Relevance

AW-213 closes epic M2-E (Character Behavior Engine). With initiative and NPC-NPC exchange in place, the character behavior layer is complete enough for AW-214 (M2 Headless Nightcap Exit Harness) to run a full Nightcap arc end to end with realistic ensemble dynamics. This unlocks the M2 exit gate and protects the M6 readiness path by ensuring AI characters in qualifying sessions can act on their own and produce the emergent NPC-NPC moments that the architecture identifies as the most memorable parts of a session.
