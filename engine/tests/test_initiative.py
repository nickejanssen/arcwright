"""Tests for the AW-213 initiative scheduler and NPC-NPC exchange."""

from __future__ import annotations

import asyncio
import uuid
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest
from sqlalchemy import JSON, Text, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import ColumnDefault, DefaultClause

from engine.characters import (
    CharacterInitiativeProfile,
    InitiativeScheduler,
    InitiativeSessionState,
    RelationshipDispositionContext,
    ScheduledInitiativeAction,
    build_npc_npc_messages,
    compute_initiative_score,
    effective_initiative_threshold,
    generate_npc_npc_exchange,
    schedule_initiative_tasks,
    select_initiative_target,
)
from engine.characters.context import build_character_generation_context
from engine.db.orm import (
    Base,
    Character,
    Event,
    Fact,
    RelationshipState,
    Session,
    SessionParticipant,
)
from engine.knowledge import assert_knowledge
from engine.routing.router import RouteResult, resolve_model_key
from engine.safety import L2_BLOCK_SENTINEL, NEUTRAL_L2_BRIDGE

CHARACTER_STANDARD_MODEL = resolve_model_key("character_dialogue", "standard")

_PATCHED = False


def _patch_metadata_for_sqlite() -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    for table in Base.metadata.tables.values():
        for col in table.columns:
            if type(col.type).__name__ == "VECTOR":
                col.type = Text()

            if isinstance(col.type, JSONB):
                col.type = JSON()

            sd = col.server_default
            if sd is None:
                continue
            arg_str = str(getattr(sd, "arg", ""))

            if "gen_random_uuid" in arg_str:
                col.server_default = None
                col.default = ColumnDefault(uuid.uuid4)
            elif arg_str.strip() == "now()":
                col.server_default = DefaultClause(text("CURRENT_TIMESTAMP"))
            elif "::jsonb" in arg_str:
                col.server_default = DefaultClause(text(arg_str.replace("::jsonb", "")))


_patch_metadata_for_sqlite()


@pytest.fixture
async def session() -> AsyncSession:  # type: ignore[override]
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as sess:  # type: ignore[attr-defined]
        yield sess  # type: ignore[misc]

    await engine.dispose()


def _route_result(content: str) -> RouteResult:
    return RouteResult(
        content=content,
        model_used=CHARACTER_STANDARD_MODEL,
        input_tokens=100,
        output_tokens=30,
        latency_ms=120,
        used_fallback=False,
    )


def _blocked_route_result() -> RouteResult:
    return RouteResult(
        content=NEUTRAL_L2_BRIDGE,
        model_used=L2_BLOCK_SENTINEL,
        input_tokens=0,
        output_tokens=0,
        latency_ms=0,
        used_fallback=False,
    )


# ---------------------------------------------------------------------------
# Pure-unit tests for the scheduler
# ---------------------------------------------------------------------------


def test_compute_initiative_score_combines_idle_and_tension() -> None:
    state = InitiativeSessionState(
        seconds_since_last_player_action=60.0,
        current_beat_id="the_dig",
        tension_score=0.5,
    )
    # idle normalized to 1.0, tension 0.5 → 0.6 * 1.0 + 0.4 * 0.5 = 0.8
    assert compute_initiative_score(state) == pytest.approx(0.8)


def test_initiative_threshold_not_met_produces_no_actions() -> None:
    scheduler = InitiativeScheduler()
    character_id = uuid4()
    state = InitiativeSessionState(
        seconds_since_last_player_action=5.0,
        current_beat_id="the_dig",
        tension_score=0.1,
    )
    profiles = [
        CharacterInitiativeProfile(
            character_id=character_id,
            is_ai_controlled=True,
            initiative_threshold=0.6,
        )
    ]
    actions = scheduler.evaluate(profiles, state)
    assert actions == []


def test_initiative_threshold_met_produces_action_without_player_input() -> None:
    scheduler = InitiativeScheduler()
    actor_id = uuid4()
    target_id = uuid4()
    state = InitiativeSessionState(
        seconds_since_last_player_action=120.0,
        current_beat_id="the_dig",
        tension_score=0.9,
    )
    profiles = [
        CharacterInitiativeProfile(
            character_id=actor_id,
            is_ai_controlled=True,
            initiative_threshold=0.6,
        )
    ]
    actions = scheduler.evaluate(
        profiles,
        state,
        eligible_targets_by_character={actor_id: [target_id]},
        relationships_by_character={
            actor_id: [
                RelationshipDispositionContext(
                    target_character_id=target_id,
                    trust=0.1,
                    history="rivalry",
                    current_affect="cool",
                )
            ]
        },
    )
    assert len(actions) == 1
    action = actions[0]
    assert action.initiating_character_id == actor_id
    assert action.target_character_id == target_id
    assert action.target_type == "npc"
    assert action.initiative_score >= 0.6


def test_human_controlled_characters_never_take_initiative() -> None:
    scheduler = InitiativeScheduler()
    human_id = uuid4()
    target_id = uuid4()
    state = InitiativeSessionState(
        seconds_since_last_player_action=600.0,
        current_beat_id="the_dig",
        tension_score=1.0,
    )
    profiles = [
        CharacterInitiativeProfile(
            character_id=human_id,
            is_ai_controlled=False,
            initiative_threshold=0.0,
        )
    ]
    actions = scheduler.evaluate(
        profiles,
        state,
        eligible_targets_by_character={human_id: [target_id]},
    )
    assert actions == []


def test_threshold_overrides_take_precedence_over_profile_and_default() -> None:
    scheduler = InitiativeScheduler()
    actor_id = uuid4()
    state = InitiativeSessionState(
        seconds_since_last_player_action=30.0,
        current_beat_id="the_dig",
        tension_score=0.0,
    )
    # score = 0.6 * 0.5 + 0.4 * 0.0 = 0.30
    profile = CharacterInitiativeProfile(
        character_id=actor_id,
        is_ai_controlled=True,
        initiative_threshold=0.6,
    )

    # No override: profile threshold 0.6 not met → no action
    assert scheduler.evaluate([profile], state) == []

    # Override at 0.2: now met → action produced
    actions_with_override = scheduler.evaluate(
        [profile],
        state,
        threshold_overrides={actor_id: 0.2},
    )
    assert len(actions_with_override) == 1
    assert actions_with_override[0].initiating_character_id == actor_id

    # Mid-life override change (same scheduler instance) flips outcome again
    assert (
        scheduler.evaluate([profile], state, threshold_overrides={actor_id: 0.9}) == []
    )


def test_effective_threshold_lookup_chain_falls_back_to_profile_then_default() -> None:
    profile_with_value = CharacterInitiativeProfile(
        character_id=uuid4(),
        is_ai_controlled=True,
        initiative_threshold=0.42,
    )
    profile_default = CharacterInitiativeProfile(
        character_id=uuid4(),
        is_ai_controlled=True,
    )
    assert effective_initiative_threshold(profile_with_value, None) == 0.42
    assert effective_initiative_threshold(profile_default, None) == pytest.approx(0.6)
    assert (
        effective_initiative_threshold(
            profile_with_value, {profile_with_value.character_id: 0.99}
        )
        == 0.99
    )


# ---------------------------------------------------------------------------
# Target-selection determinism
# ---------------------------------------------------------------------------


def test_select_target_prefers_beat_character_emphasis() -> None:
    initiator = uuid4()
    emphasized = uuid4()
    other = uuid4()
    target = select_initiative_target(
        initiating_character_id=initiator,
        eligible_target_ids=[other, emphasized],
        beat_character_emphasis=[emphasized],
        relationships=[
            RelationshipDispositionContext(
                target_character_id=other,
                trust=0.0,
                history="rivalry",
                current_affect="hostile",
            ),
            RelationshipDispositionContext(
                target_character_id=emphasized,
                trust=0.5,
                history="neutral",
                current_affect="cool",
            ),
        ],
    )
    assert target == emphasized


def test_select_target_strongest_relationship_signal_when_no_emphasis() -> None:
    initiator = uuid4()
    distrusted = uuid4()
    neutral = uuid4()
    trusted = uuid4()
    target = select_initiative_target(
        initiating_character_id=initiator,
        eligible_target_ids=[neutral, trusted, distrusted],
        beat_character_emphasis=None,
        relationships=[
            RelationshipDispositionContext(
                target_character_id=neutral,
                trust=0.5,
                history="neutral",
                current_affect="cool",
            ),
            RelationshipDispositionContext(
                target_character_id=trusted,
                trust=0.85,
                history="ally",
                current_affect="warm",
            ),
            RelationshipDispositionContext(
                target_character_id=distrusted,
                trust=0.05,
                history="rivalry",
                current_affect="hostile",
            ),
        ],
    )
    # abs(0.05 - 0.5) = 0.45 wins over abs(0.85 - 0.5) = 0.35
    assert target == distrusted


def test_select_target_tie_breaks_by_recency_then_uuid() -> None:
    initiator = uuid4()
    # Force equal relationship strength but different recency
    a = UUID("00000000-0000-0000-0000-000000000001")
    b = UUID("00000000-0000-0000-0000-000000000002")
    target = select_initiative_target(
        initiating_character_id=initiator,
        eligible_target_ids=[a, b],
        beat_character_emphasis=None,
        relationships=[
            RelationshipDispositionContext(
                target_character_id=b,
                trust=0.1,
                history="rivalry",
                current_affect="cool",
            ),
            RelationshipDispositionContext(
                target_character_id=a,
                trust=0.1,
                history="rivalry",
                current_affect="cool",
            ),
        ],
    )
    # Equal strength; b appears first in relationships list (more recent) → b wins
    assert target == b


def test_select_target_falls_back_to_player_group_when_no_npc_eligible() -> None:
    initiator = uuid4()
    target = select_initiative_target(
        initiating_character_id=initiator,
        eligible_target_ids=[initiator],
        beat_character_emphasis=None,
        relationships=[],
    )
    assert target is None


def test_target_selection_is_deterministic_across_calls() -> None:
    initiator = uuid4()
    targets = [uuid4() for _ in range(5)]
    relationships = [
        RelationshipDispositionContext(
            target_character_id=t,
            trust=0.4,
            history="neutral",
            current_affect="cool",
        )
        for t in targets
    ]
    first = select_initiative_target(
        initiating_character_id=initiator,
        eligible_target_ids=list(targets),
        beat_character_emphasis=None,
        relationships=list(relationships),
    )
    second = select_initiative_target(
        initiating_character_id=initiator,
        eligible_target_ids=list(targets),
        beat_character_emphasis=None,
        relationships=list(relationships),
    )
    assert first == second
    assert first is not None


# ---------------------------------------------------------------------------
# DB-backed tests for NPC-NPC exchange
# ---------------------------------------------------------------------------


async def _make_session_row(db: AsyncSession) -> Session:
    row = Session(
        session_id=uuid4(),
        arc_id="nightcap",
        status="active",
        host_account_id=uuid4(),
        current_beat_id="the_dig",
        quality_tier="standard",
        player_count=4,
    )
    db.add(row)
    await db.flush()
    return row


async def _make_character(db: AsyncSession, name: str, secret: str) -> Character:
    character = Character(
        character_id=uuid4(),
        behavior_profile={
            "personality": {
                "traits": ["evasive"],
                "communication_style": f"speaks like {name}",
            },
            "goals": [f"Protect {secret}"],
            "secrets": [{"content": secret}],
            "tells": [f"Pauses when asked about {secret}"],
            "initiative_threshold": 0.5,
        },
    )
    db.add(character)
    await db.flush()
    return character


async def _make_participant(
    db: AsyncSession,
    *,
    session_id: UUID,
    character_id: UUID,
    is_ai_controlled: bool = True,
) -> SessionParticipant:
    participant = SessionParticipant(
        participant_id=uuid4(),
        session_id=session_id,
        character_id=character_id,
        account_id=None,
        join_token=f"join-{uuid4().hex[:8]}",
        surface_type="phone",
        is_ai_controlled=is_ai_controlled,
    )
    db.add(participant)
    await db.flush()
    return participant


async def _make_fact(
    db: AsyncSession,
    *,
    session_id: UUID,
    fact_content: dict[str, object],
    fact_type: str = "clue",
) -> Fact:
    fact = Fact(
        fact_id=uuid4(),
        session_id=session_id,
        fact_type=fact_type,
        fact_content=fact_content,
    )
    db.add(fact)
    await db.flush()
    return fact


async def _make_relationship(
    db: AsyncSession,
    *,
    session_id: UUID,
    source_char_id: UUID,
    target_char_id: UUID,
    trust_level: float,
    current_affect: str,
) -> RelationshipState:
    rel = RelationshipState(
        relationship_id=uuid4(),
        session_id=session_id,
        source_char_id=source_char_id,
        target_char_id=target_char_id,
        trust_level=trust_level,
        history_tag="rivalry",
        current_affect=current_affect,
    )
    db.add(rel)
    await db.flush()
    return rel


async def _make_npc_pair_fixture(db: AsyncSession) -> dict[str, object]:
    session_row = await _make_session_row(db)
    butler = await _make_character(db, "butler", "the ledger debt")
    housekeeper = await _make_character(db, "housekeeper", "the hidden key")
    await _make_participant(
        db,
        session_id=session_row.session_id,
        character_id=butler.character_id,
    )
    await _make_participant(
        db,
        session_id=session_row.session_id,
        character_id=housekeeper.character_id,
    )

    butler_known = await _make_fact(
        db,
        session_id=session_row.session_id,
        fact_content={"detail": "The ledger was on the study desk"},
    )
    butler_unknown = await _make_fact(
        db,
        session_id=session_row.session_id,
        fact_content={"detail": "The hidden safe is behind the portrait"},
    )
    housekeeper_known = await _make_fact(
        db,
        session_id=session_row.session_id,
        fact_content={"detail": "The pantry door was unlocked"},
    )

    await assert_knowledge(
        db,
        session_id=session_row.session_id,
        character_id=butler.character_id,
        fact_type=butler_known.fact_type,
        fact_content=butler_known.fact_content,
        confidence=0.9,
    )
    await assert_knowledge(
        db,
        session_id=session_row.session_id,
        character_id=housekeeper.character_id,
        fact_type=housekeeper_known.fact_type,
        fact_content=housekeeper_known.fact_content,
        confidence=0.9,
    )

    await _make_relationship(
        db,
        session_id=session_row.session_id,
        source_char_id=butler.character_id,
        target_char_id=housekeeper.character_id,
        trust_level=0.2,
        current_affect="suspicious",
    )
    await _make_relationship(
        db,
        session_id=session_row.session_id,
        source_char_id=housekeeper.character_id,
        target_char_id=butler.character_id,
        trust_level=0.3,
        current_affect="guarded",
    )

    return {
        "session": session_row,
        "butler": butler,
        "housekeeper": housekeeper,
        "butler_known": butler_known,
        "butler_unknown": butler_unknown,
        "housekeeper_known": housekeeper_known,
    }


async def test_npc_npc_exchange_prompt_includes_both_knowledge_states_and_relationships(
    session: AsyncSession,
) -> None:
    fixture = await _make_npc_pair_fixture(session)
    butler = fixture["butler"]
    housekeeper = fixture["housekeeper"]
    butler_known = fixture["butler_known"]
    butler_unknown = fixture["butler_unknown"]
    housekeeper_known = fixture["housekeeper_known"]

    butler_context = await build_character_generation_context(
        session,
        session_id=fixture["session"].session_id,
        character_id=butler.character_id,
    )
    housekeeper_context = await build_character_generation_context(
        session,
        session_id=fixture["session"].session_id,
        character_id=housekeeper.character_id,
    )

    messages = build_npc_npc_messages(
        speaker_context=butler_context,
        partner_context=housekeeper_context,
        current_beat_id="the_dig",
        scene_goal="Question the housekeeper about the pantry.",
        prior_turns=[],
    )

    system_prompt = messages[0]["content"]
    assert "[INITIATING CHARACTER IDENTITY AND PERSONALITY]" in system_prompt
    assert "[INITIATING CHARACTER KNOWN KNOWLEDGE]" in system_prompt
    assert "[INITIATING CHARACTER NOT-KNOWN KNOWLEDGE]" in system_prompt
    assert "[TARGET CHARACTER IDENTITY AND PERSONALITY]" in system_prompt
    assert "[TARGET CHARACTER KNOWN KNOWLEDGE]" in system_prompt
    assert "[RELATIONSHIP CONTEXT]" in system_prompt
    assert "[CURRENT SCENE]" in system_prompt
    # Butler's known and unknown fact ids appear
    assert str(butler_known.fact_id) in system_prompt
    assert str(butler_unknown.fact_id) in system_prompt
    # Housekeeper's known fact id appears (target context)
    assert str(housekeeper_known.fact_id) in system_prompt
    # Both relationship directions appear (butler→housekeeper and housekeeper→butler)
    assert str(housekeeper.character_id) in system_prompt
    assert str(butler.character_id) in system_prompt


async def test_npc_npc_exchange_single_turn_persists_one_event(
    session: AsyncSession,
) -> None:
    fixture = await _make_npc_pair_fixture(session)
    butler = fixture["butler"]
    housekeeper = fixture["housekeeper"]

    with patch(
        "engine.characters.initiative.generate",
        new_callable=AsyncMock,
        return_value=_route_result("I notice you spend a lot of time near the pantry."),
    ):
        exchange = await generate_npc_npc_exchange(
            session,
            session_id=fixture["session"].session_id,
            initiating_character_id=butler.character_id,
            target_character_id=housekeeper.character_id,
            quality_tier="standard",
            max_turns=1,
            current_beat_id="the_dig",
        )

    assert len(exchange.turns) == 1
    assert exchange.turns[0].actor_character_id == butler.character_id
    assert exchange.turns[0].turn_index == 0
    persisted = (
        await session.scalars(
            select(Event).where(
                Event.session_id == fixture["session"].session_id,
                Event.event_type == "npc_npc_exchange_turn",
            )
        )
    ).all()
    assert len(persisted) == 1
    payload = persisted[0].payload
    assert payload["exchange_id"] == str(exchange.exchange_id)
    assert payload["initiating_character_id"] == str(butler.character_id)
    assert payload["target_character_id"] == str(housekeeper.character_id)
    assert payload["speaker_character_id"] == str(butler.character_id)
    assert payload["partner_character_id"] == str(housekeeper.character_id)
    assert payload["task_type"] == "character_dialogue"


async def test_npc_npc_exchange_multi_turn_alternates_speakers_and_requeries_knowledge(
    session: AsyncSession,
) -> None:
    fixture = await _make_npc_pair_fixture(session)
    butler = fixture["butler"]
    housekeeper = fixture["housekeeper"]

    contents = iter(
        [
            "Housekeeper, where were you?",
            "I was in the pantry the whole time.",
        ]
    )
    contexts_built: list[UUID] = []

    real_build = build_character_generation_context

    async def spy_build_context(
        db_session: AsyncSession,
        *,
        session_id: UUID,
        character_id: UUID,
    ):
        contexts_built.append(character_id)
        return await real_build(
            db_session, session_id=session_id, character_id=character_id
        )

    with (
        patch(
            "engine.characters.initiative.build_character_generation_context",
            side_effect=spy_build_context,
        ),
        patch(
            "engine.characters.initiative.generate",
            new_callable=AsyncMock,
            side_effect=lambda *a, **kw: _route_result(next(contents)),
        ),
    ):
        exchange = await generate_npc_npc_exchange(
            session,
            session_id=fixture["session"].session_id,
            initiating_character_id=butler.character_id,
            target_character_id=housekeeper.character_id,
            quality_tier="standard",
            max_turns=2,
            current_beat_id="the_dig",
        )

    assert len(exchange.turns) == 2
    assert exchange.turns[0].actor_character_id == butler.character_id
    assert exchange.turns[1].actor_character_id == housekeeper.character_id
    # Knowledge context built twice per turn (speaker + partner), total 4 calls
    assert len(contexts_built) == 4


async def test_npc_npc_exchange_safety_block_ends_exchange_early(
    session: AsyncSession,
) -> None:
    fixture = await _make_npc_pair_fixture(session)
    butler = fixture["butler"]
    housekeeper = fixture["housekeeper"]

    with patch(
        "engine.characters.initiative.generate",
        new_callable=AsyncMock,
        return_value=_blocked_route_result(),
    ):
        exchange = await generate_npc_npc_exchange(
            session,
            session_id=fixture["session"].session_id,
            initiating_character_id=butler.character_id,
            target_character_id=housekeeper.character_id,
            quality_tier="standard",
            max_turns=3,
            current_beat_id="the_dig",
        )

    assert len(exchange.turns) == 1
    assert exchange.turns[0].safety_blocked is True
    assert exchange.turns[0].safety_layer == "L2"
    persisted = (
        await session.scalars(
            select(Event).where(
                Event.session_id == fixture["session"].session_id,
                Event.event_type == "npc_npc_exchange_blocked",
            )
        )
    ).all()
    assert len(persisted) == 1


# ---------------------------------------------------------------------------
# Non-blocking dispatch
# ---------------------------------------------------------------------------


async def test_schedule_initiative_tasks_returns_immediately_without_blocking() -> None:
    session_opened = asyncio.Event()
    session_released = asyncio.Event()

    @asynccontextmanager
    async def slow_session_factory():
        session_opened.set()
        # Block until the test releases us, simulating a slow generation call
        await session_released.wait()
        yield AsyncMock(spec=AsyncSession)

    actions = [
        ScheduledInitiativeAction(
            initiating_character_id=uuid4(),
            target_character_id=None,
            target_type="player_group",
            initiative_score=0.7,
        )
    ]

    loop = asyncio.get_running_loop()
    start = loop.time()
    tasks = schedule_initiative_tasks(
        slow_session_factory,
        actions,
        session_id=uuid4(),
        quality_tier="standard",
    )
    elapsed = loop.time() - start

    # schedule_initiative_tasks returned synchronously (no awaiting) — coordinator
    # is free to continue. We assert it returned in well under a second even
    # though the dispatched coroutine is blocked.
    assert elapsed < 0.05
    assert len(tasks) == 1
    assert not tasks[0].done()

    # Yield to event loop so the dispatched task actually enters the factory
    await asyncio.sleep(0)
    assert session_opened.is_set()

    # Cancel the dispatched task to clean up
    tasks[0].cancel()
    session_released.set()
    with pytest.raises((asyncio.CancelledError, BaseException)):
        await tasks[0]


# ---------------------------------------------------------------------------
# Social pressure end-to-end: generate_npc_npc_exchange flows pressure into prompt
# ---------------------------------------------------------------------------


async def test_npc_npc_exchange_pressure_block_in_prompt_when_speaker_above_threshold(
    session: AsyncSession,
) -> None:
    """Social pressure_by_character flows through generate_npc_npc_exchange."""
    session_row = await _make_session_row(session)

    # Speaker has crumble_threshold 0.5 — will show strain at pressure >= 0.5
    speaker = Character(
        character_id=uuid4(),
        behavior_profile={
            "personality": {"traits": ["evasive"], "communication_style": "terse"},
            "goals": ["Protect the secret"],
            "secrets": [{"content": "the ledger debt", "crumble_threshold": 0.5}],
            "tells": ["Pauses before answering"],
        },
    )
    partner = Character(
        character_id=uuid4(),
        behavior_profile={
            "personality": {"traits": ["confident"], "communication_style": "direct"},
            "goals": ["Find the truth"],
            "secrets": [],
            "tells": [],
        },
    )
    session.add(speaker)
    session.add(partner)
    await session.flush()

    await _make_participant(
        session,
        session_id=session_row.session_id,
        character_id=speaker.character_id,
    )
    await _make_participant(
        session,
        session_id=session_row.session_id,
        character_id=partner.character_id,
    )

    captured_messages: list[list[dict]] = []

    async def _capture(*args, **kwargs):
        captured_messages.append(kwargs.get("messages", []))
        return _route_result("I was in the library all evening.")

    with patch("engine.characters.initiative.generate", side_effect=_capture):
        await generate_npc_npc_exchange(
            session,
            session_id=session_row.session_id,
            initiating_character_id=speaker.character_id,
            target_character_id=partner.character_id,
            quality_tier="standard",
            max_turns=1,
            social_pressure_by_character={speaker.character_id: 0.7},
        )

    assert len(captured_messages) == 1
    system_prompt = captured_messages[0][0]["content"]
    assert "[SOCIAL PRESSURE]" in system_prompt
    assert "[END SOCIAL PRESSURE]" in system_prompt


async def test_npc_npc_exchange_no_pressure_block_when_speaker_below_threshold(
    session: AsyncSession,
) -> None:
    """Pressure below crumble_threshold produces no pressure block in prompt."""
    session_row = await _make_session_row(session)

    speaker = Character(
        character_id=uuid4(),
        behavior_profile={
            "personality": {"traits": ["calm"], "communication_style": "measured"},
            "goals": ["Stay composed"],
            "secrets": [{"content": "nothing serious", "crumble_threshold": 0.8}],
            "tells": [],
        },
    )
    partner = Character(
        character_id=uuid4(),
        behavior_profile={
            "personality": {"traits": ["curious"], "communication_style": "probing"},
            "goals": ["Ask questions"],
            "secrets": [],
            "tells": [],
        },
    )
    session.add(speaker)
    session.add(partner)
    await session.flush()

    await _make_participant(
        session,
        session_id=session_row.session_id,
        character_id=speaker.character_id,
    )
    await _make_participant(
        session,
        session_id=session_row.session_id,
        character_id=partner.character_id,
    )

    captured_messages: list[list[dict]] = []

    async def _capture(*args, **kwargs):
        captured_messages.append(kwargs.get("messages", []))
        return _route_result("Perfectly calm response.")

    with patch("engine.characters.initiative.generate", side_effect=_capture):
        await generate_npc_npc_exchange(
            session,
            session_id=session_row.session_id,
            initiating_character_id=speaker.character_id,
            target_character_id=partner.character_id,
            quality_tier="standard",
            max_turns=1,
            social_pressure_by_character={speaker.character_id: 0.5},
        )

    assert len(captured_messages) == 1
    system_prompt = captured_messages[0][0]["content"]
    assert "[SOCIAL PRESSURE]" not in system_prompt
