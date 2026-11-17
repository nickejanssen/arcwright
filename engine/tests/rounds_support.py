"""Shared fixtures for the rounds tests (AW-325, spec 0093 Parts C and D).

Everything here is made up. The case is ``fixtures/authored_case/valid_case.json``;
the arc is the registered couch-race file with its beats replaced. No real case
file is read, and no model is ever called.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition
from engine.db.orm import Session as OrmSession
from engine.events.models import AudienceTarget, ContentEvent
from engine.session.phases import current_phase, host_move_on
from engine.session.service import SessionService

ENGINE_DIR = Path(__file__).resolve().parent.parent
VALID_CASE = Path(__file__).resolve().parent / "fixtures/authored_case/valid_case.json"
BEATS = ["opening", "beat_one", "beat_two", "beat_three", "finale"]
ROUND_BEATS = BEATS[1:4]
T0 = datetime(2026, 12, 12, 20, 0, 0, tzinfo=timezone.utc)

SCENE_SECONDS = 20
CHOICES_SECONDS = 60
MINI_GAME_SECONDS = 30
BRIDGE_SECONDS = 10
SCENE_TEXT = "The lamp flickers over the {beat} table."


def at(seconds: float) -> datetime:
    return T0 + timedelta(seconds=seconds)


def _line(text: str, **hints: Any) -> dict[str, Any]:
    return {"text": text, "hints": hints}


def round_phases(beat_id: str) -> list[dict[str, Any]]:
    return [
        {
            "kind": "scene",
            "seconds": SCENE_SECONDS,
            "audience": "shared_display",
            "lines": [
                _line(SCENE_TEXT.format(beat=beat_id), emotion="uneasy"),
                _line("Nobody speaks.", pause_before_ms=500),
            ],
        },
        {"kind": "choices", "seconds": CHOICES_SECONDS},
        {"kind": "mini_game", "seconds": MINI_GAME_SECONDS},
        {
            "kind": "bridge",
            "seconds": BRIDGE_SECONDS,
            "audience": "shared_display",
            "lines": [_line(f"On from {beat_id}.")],
        },
    ]


def phased_arc(
    *,
    case_path: Path | None = VALID_CASE,
    budget: int | None = None,
    phases: dict[str, list[dict[str, Any]] | None] | None = None,
) -> ArcDefinition:
    """The fixture arc: opening, three rounds, a final beat, all phased."""
    couch = ArcDefinition.model_validate_json(
        (ENGINE_DIR.parent / "nightcap" / "couch-race.arc.json").read_text("utf-8")
    )
    template = couch.beats[0].model_dump(mode="json")
    template.update(
        mini_games=None,
        interaction_ids=[],
        authored_content=None,
        exit_conditions=[],
        entry_conditions=[],
    )
    per_beat: dict[str, list[dict[str, Any]] | None] = {
        "opening": [
            {
                "kind": "scene",
                "seconds": SCENE_SECONDS,
                "lines": [_line("Welcome to the house.")],
            },
            {"kind": "bridge", "seconds": BRIDGE_SECONDS},
        ],
        **{beat: round_phases(beat) for beat in ROUND_BEATS},
        "finale": [{"kind": "scene", "seconds": SCENE_SECONDS}],
    }
    per_beat.update(phases or {})
    beats = [
        {**template, "beat_id": b, "beat_name": b, "phases": per_beat[b]} for b in BEATS
    ]
    data = couch.model_dump(mode="json")
    data.update(
        arc_id="fixture-arc-v1",
        beats=beats,
        beat_graph={a: [b] for a, b in zip(BEATS, BEATS[1:])} | {BEATS[-1]: []},
        interactions=[],
        resource_effects=[],
        obligations=[],
        authorial_intent=None,
        case_file=str(case_path) if case_path else None,
    )
    if budget is not None:
        data["choice_config"] = {"budget": budget}
    return ArcDefinition.model_validate(data)


@dataclass
class Recorder:
    """Stands in for the event bus: remembers every published event."""

    events: list[ContentEvent] = field(default_factory=list)

    async def __call__(self, event: ContentEvent) -> ContentEvent:
        self.events.append(event)
        return event

    def of_type(self, event_type: str) -> list[ContentEvent]:
        return [e for e in self.events if e.event_type == event_type]


@dataclass(frozen=True)
class Seated:
    session_id: UUID
    participants: tuple[UUID, ...]
    characters: tuple[UUID, ...]


@contextmanager
def fixture_arc_registered(arc: ArcDefinition) -> Iterator[None]:
    """Make the session service and the rounds code see ``arc``."""
    with (
        patch("engine.session.service.load_arc_definition", lambda _id: arc),
        patch("engine.session.phases.load_arc_definition", lambda _id: arc),
        patch("engine.session.choices.load_arc_definition", lambda _id: arc),
    ):
        yield


@pytest.fixture()
def registered(monkeypatch: pytest.MonkeyPatch) -> Callable[[ArcDefinition], None]:
    def register(arc: ArcDefinition) -> None:
        for target in (
            "engine.session.service.load_arc_definition",
            "engine.session.phases.load_arc_definition",
            "engine.session.choices.load_arc_definition",
        ):
            monkeypatch.setattr(target, lambda _id, _arc=arc: _arc)

    return register


@pytest.fixture()
def no_model_calls() -> Iterator[None]:
    """Any model call fails the test."""
    with patch(
        "engine.routing.router.litellm.acompletion",
        side_effect=AssertionError("a model was called"),
    ) as mocked:
        yield
        assert mocked.call_count == 0


async def seat_session(
    db: AsyncSession, arc: ArcDefinition, *, players: int = 2, start: bool = True
) -> Seated:
    """Create a session, seat ``players`` human participants, and start it."""
    svc = SessionService()
    created, _ = await svc.create_session(
        db, arc_id=arc.arc_id, host_account_id=uuid4()
    )
    participants: list[UUID] = []
    characters: list[UUID] = []
    for _ in range(players):
        participant, _ = await svc.add_player(db, created.session_id)
        participants.append(participant.participant_id)
        characters.append(participant.character_id)
    if start:
        await svc.start_session(db, created.session_id)
    return Seated(created.session_id, tuple(participants), tuple(characters))


def private_to(events: list[ContentEvent], participant_id: UUID) -> list[ContentEvent]:
    return [
        e
        for e in events
        if e.target_audience is AudienceTarget.specific_player
        and e.target_player_id == participant_id
    ]


async def where(
    db: AsyncSession, session_id: UUID
) -> tuple[str, str | None, str | None]:
    """(beat, phase, status) as saved, read back from the database."""
    orm = await db.get(OrmSession, session_id)
    assert orm is not None
    await db.refresh(orm)
    state = await current_phase(db, session_id)
    if state is None:
        return orm.current_beat_id, None, None
    assert state.beat_id == orm.current_beat_id
    return orm.current_beat_id, state.phase, state.status


async def reach_phase(
    db: AsyncSession,
    seated: Seated,
    beat: str,
    phase: str,
    now: datetime,
    publish: Recorder | None = None,
) -> datetime:
    """Move by host move-on until (beat, phase) is current. Returns ``now``."""
    for _ in range(40):
        if (await where(db, seated.session_id))[:2] == (beat, phase):
            return now
        await host_move_on(db, seated.session_id, now, publish)
    raise AssertionError(f"never reached {beat}/{phase}")
