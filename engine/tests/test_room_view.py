"""The room view (AW-331, spec 0095 M1): the one unsigned read a shared screen
rebuilds itself from.

Named proof: a whole fixture game, join to recap, at two and four players. At
every step the view is read with no sign-in and checked for what it must carry
and for anything private it must never carry. No model is called (the
``no_model_calls`` fixture fails the test if one is). Everything is made up.
"""

from __future__ import annotations

import dataclasses
import json
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.arc.models import ArcDefinition
from engine.db.testing import make_sqlite_session_factory
from engine.session import closing, host_seat, survey
from engine.session.choices import read_holdings
from engine.session.phases import (
    lock_theory,
    mark_ready,
    round_view,
    save_theory_draft,
    tick,
)
from engine.session.room_view import RoomView, room_view
from engine.session.service import SessionService
from engine.tests.rounds_support import (
    Recorder,
    Seated,
    at,
    closing_arc,
    phased_arc,
    where,
)
from engine.tests.test_endgame_headless import (
    RIGHT,
    VERDICT_KEYS,
    WRONG,
    everyone_ready,
    keys_of,
    play_to_last_call,
)

NAMES = ["Ada", "Bo", "Cy", "Di"]


@pytest_asyncio.fixture()
async def factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine, session_factory = await make_sqlite_session_factory()
    try:
        yield session_factory
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def db(
    factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


async def join_room(
    db: AsyncSession, arc: ArcDefinition, players: int, *, start: bool = True
) -> Seated:
    svc = SessionService()
    created, _ = await svc.create_session(
        db, arc_id=arc.arc_id, host_account_id=uuid4()
    )
    seats = [
        await svc.lobby_join(
            db, join_code=str(created.join_code), display_name=NAMES[i]
        )
        for i in range(players)
    ]
    if start:
        await svc.start_session(db, created.session_id)
    return Seated(
        created.session_id,
        tuple(s.participant_id for s in seats),
        tuple(s.character_id for s in seats),
    )


def as_json(view: RoomView) -> dict[str, Any]:
    plain: dict[str, Any] = json.loads(
        json.dumps(dataclasses.asdict(view), default=str)
    )
    return plain


def public_text(view: RoomView, *, without_closing: bool = False) -> str:
    body = dataclasses.asdict(view)
    if without_closing:
        body.pop("closing")
    return json.dumps(body, default=str).casefold()


MUST_CARRY = {
    "session_status",
    "round_title",
    "phase",
    "seconds_left",
    "paused",
    "paused_by",
    "lines",
    "players",
    "over",
    "closing",
}
PLAYER_KEYS = {
    "participant_id",
    "display_name",
    "ready",
    "locked",
    "answered_survey",
    "is_host",
}
NEVER = {"beat_id", "concept_id", "join_token", "character_id", "slots", "private"}


async def check(
    db: AsyncSession,
    seated: Seated,
    secrets: set[str],
    *,
    now: float,
    result_reached: bool,
) -> RoomView:
    """Read the room with no sign-in and hold it to the privacy rules."""
    view = await room_view(db, seated.session_id, at(now))
    body = as_json(view)
    assert MUST_CARRY <= set(body)
    assert [set(p) for p in body["players"]] == [PLAYER_KEYS] * len(seated.participants)
    assert {p["participant_id"] for p in body["players"]} == {
        str(p) for p in seated.participants
    }
    # The public result names the proof concept of each winner; that is the one
    # place a concept ID is public, and only once the result has been reached.
    never = NEVER - {"concept_id"} if result_reached else NEVER
    assert not keys_of(body) & never
    # The closing part is the public closing view, passed through unchanged and
    # checked equal below (a winner's proof text is public there by design), so
    # once the result is out the privacy scan covers everything else.
    text = public_text(view, without_closing=result_reached)
    for secret in secrets:
        assert secret.casefold() not in text, secret
    if not result_reached:
        assert not keys_of(body) & VERDICT_KEYS
        assert body["closing"] is None or body["closing"]["result"] is None
    # The room view carries the round's own facts, not a second copy of them.
    round_ = await round_view(db, seated.session_id, at(now))
    assert body["round_title"] == round_.beat_name
    assert body["phase"] == round_.phase
    assert body["seconds_left"] == round_.seconds_left
    # The public closing view is passed through as it is.
    if body["closing"] is not None:
        public = await closing.closing_view(db, seated.session_id)
        assert body["closing"] == {
            "reveal": public.reveal,
            "result": public.result,
            "recap": public.recap,
        }
    return view


async def private_markers(db: AsyncSession, seated: Seated) -> set[str]:
    """Written text each player holds for themselves: it must never be public."""
    found: set[str] = set()
    for participant in seated.participants:
        for held in await read_holdings(db, seated.session_id, participant):
            found.add(held.text)
    return {text for text in found if len(text) > 12}


@pytest.mark.asyncio
@pytest.mark.parametrize("players", [2, 4])
async def test_a_whole_game_read_with_no_sign_in_at_every_step(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    no_model_calls: None,
    players: int,
    tmp_path: Path,
) -> None:
    original = closing_arc()
    assert original.case_file
    path = tmp_path / "session-fixture.json"
    path.write_bytes(Path(original.case_file).read_bytes())
    arc = closing_arc(path)
    registered(arc)
    seated = await join_room(db, arc, players, start=False)

    # Before the start: who is here, nothing else.
    lobby = await check(db, seated, set(), now=0, result_reached=False)
    assert lobby.session_status == "created" and lobby.phase is None
    assert not lobby.over and not lobby.paused
    assert [p.display_name for p in lobby.players] == sorted(
        NAMES[:players], key=str.casefold
    )
    assert [p.is_host for p in lobby.players].count(True) == 1
    host = next(p for p in lobby.players if p.is_host)
    assert host.participant_id == str(seated.participants[0])
    assert not any(p.ready or p.locked or p.answered_survey for p in lobby.players)

    await SessionService().start_session(db, seated.session_id)
    await db.commit()
    db.expunge_all()
    # Every play-time read below must survive loss of the authored source.
    path.write_text("{}", encoding="utf-8")
    rec = Recorder()
    await tick(db, seated.session_id, at(0), rec)
    opening = await check(db, seated, set(), now=0, result_reached=False)
    assert opening.session_status == "active" and opening.phase is not None
    assert opening.round_title and opening.seconds_left is not None
    assert opening.lines, "the opening's public lines are carried"

    # Ready flags follow what is saved.
    await mark_ready(db, seated.session_id, seated.participants[0], at(0), rec)
    one_ready = await check(db, seated, set(), now=0, result_reached=False)
    flags = {p.participant_id: p.ready for p in one_ready.players}
    assert flags[str(seated.participants[0])] is True
    assert list(flags.values()).count(True) == 1

    now = await play_to_last_call(db, seated, rec)
    secrets = await private_markers(db, seated)
    assert secrets, "the players hold private written text by now"
    commit = await check(db, seated, secrets, now=now, result_reached=False)
    assert commit.phase == "commit"

    # Last Call: drafts are private, a lock shows only as locked.
    now += 5
    drafts = RIGHT, WRONG
    for seat, participant in enumerate(seated.participants):
        await save_theory_draft(
            db,
            seated.session_id,
            participant,
            drafts[0] if seat == 0 else drafts[1],
            "c_how_true",
            at(now),
            rec,
        )
    drafting = await check(
        db, seated, secrets | {"c_how_true"}, now=now, result_reached=False
    )
    assert not any(p.locked for p in drafting.players)
    await lock_theory(db, seated.session_id, seated.participants[0], at(now), rec)
    one_locked = await check(
        db, seated, secrets | {"c_how_true"}, now=now, result_reached=False
    )
    assert [p.locked for p in one_locked.players].count(True) == 1
    for participant in seated.participants[1:]:
        await lock_theory(db, seated.session_id, participant, at(now), rec)
    assert (await where(db, seated.session_id))[:2] == ("finale", "reveal")
    reveal = await check(db, seated, secrets, now=now, result_reached=False)
    assert reveal.closing is not None and reveal.closing["reveal"] is not None

    now += 1
    await everyone_ready(db, seated, rec, now)
    await check(db, seated, secrets, now=now, result_reached=False)

    now += 1
    await everyone_ready(db, seated, rec, now)
    assert (await where(db, seated.session_id))[:2] == ("verdict", "result")
    result = await check(db, seated, secrets, now=now, result_reached=True)
    assert result.closing is not None
    public = result.closing["result"]
    assert public is not None and public["players"]
    assert "slots" not in json.dumps(public)

    now += 1
    await everyone_ready(db, seated, rec, now)
    assert (await where(db, seated.session_id))[:2] == ("verdict", "recap")
    recap = await check(db, seated, secrets, now=now, result_reached=True)
    assert recap.closing is not None and recap.closing["recap"] is not None
    assert not recap.over

    now += 1
    await everyone_ready(db, seated, rec, now)
    assert await where(db, seated.session_id) == ("verdict", "recap", "ended")
    final = await check(db, seated, secrets, now=now, result_reached=True)
    assert final.over is True


@pytest.mark.asyncio
async def test_a_pause_shows_who_paused_and_the_time_left(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    no_model_calls: None,
) -> None:
    arc = closing_arc()
    registered(arc)
    seated = await join_room(db, arc, 2)
    await tick(db, seated.session_id, at(0))
    running = await room_view(db, seated.session_id, at(5))
    assert running.paused is False and running.paused_by is None
    left_running = running.seconds_left
    assert left_running is not None

    svc = SessionService()
    await svc.pause_session(
        db, seated.session_id, now=at(5), paused_by=seated.participants[1]
    )
    paused = await room_view(db, seated.session_id, at(50))
    assert paused.paused is True and paused.session_status == "paused"
    assert paused.paused_by == "Bo"
    assert paused.seconds_left == pytest.approx(left_running)

    await svc.resume_session(db, seated.session_id, now=at(60))
    resumed = await room_view(db, seated.session_id, at(60))
    assert resumed.paused is False and resumed.paused_by is None


@pytest.mark.asyncio
async def test_a_pause_by_the_operator_key_names_nobody(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    no_model_calls: None,
) -> None:
    arc = closing_arc()
    registered(arc)
    seated = await join_room(db, arc, 2)
    await tick(db, seated.session_id, at(0))
    await SessionService().pause_session(db, seated.session_id, now=at(5))
    paused = await room_view(db, seated.session_id, at(6))
    assert paused.paused is True and paused.paused_by is None


@pytest.mark.asyncio
async def test_survey_and_host_flags_are_yes_or_no_only(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    no_model_calls: None,
) -> None:
    arc = closing_arc()
    registered(arc)
    seated = await join_room(db, arc, 3)
    await survey.save_survey(
        db,
        seated.session_id,
        seated.participants[1],
        {"fun": 5},
        "a private comment about the game",
        at(1),
    )
    view = await room_view(db, seated.session_id, at(1))
    answered = {p.participant_id: p.answered_survey for p in view.players}
    assert answered[str(seated.participants[1])] is True
    assert list(answered.values()).count(True) == 1
    assert "private comment" not in public_text(view)
    await host_seat.hand_over(
        db, seated.session_id, seated.participants[2], at(2), None
    )
    after = await room_view(db, seated.session_id, at(2))
    assert [p.participant_id for p in after.players if p.is_host] == [
        str(seated.participants[2])
    ]


@pytest.mark.asyncio
async def test_an_unknown_session_is_not_found(
    db: AsyncSession, registered: Callable[[ArcDefinition], None]
) -> None:
    from engine.session.phases import RoundError

    registered(closing_arc())
    with pytest.raises(RoundError) as refused:
        await room_view(db, uuid4(), at(0))
    assert refused.value.code == "session_not_found"


@pytest.mark.asyncio
async def test_cold_lobby_does_not_validate_the_case(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arc = closing_arc()
    registered(arc)
    seated = await join_room(db, arc, 2, start=False)

    def unexpected(*args: Any) -> None:
        pytest.fail("lobby read started validation")

    monkeypatch.setattr(closing, "_case", unexpected)
    assert (await room_view(db, seated.session_id, at(0))).session_status == "created"


@pytest.mark.asyncio
async def test_phased_lobby_without_a_case_has_no_closing_view(
    db: AsyncSession, registered: Callable[[ArcDefinition], None]
) -> None:
    arc = phased_arc(case_path=None)
    registered(arc)
    seated = await join_room(db, arc, 2, start=False)
    assert (await room_view(db, seated.session_id, at(0))).closing is None
