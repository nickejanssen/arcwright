"""Battle of Wits through the authored loader, saved run, and round clock."""

import json
from collections.abc import AsyncIterator, Callable
from datetime import datetime, timedelta, timezone
from pathlib import Path
from shutil import copytree
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.arc.models import ArcDefinition
from engine.db.testing import make_sqlite_session_factory
from engine.events.bus import SessionEventBus
from engine.mini_games.audience_view import Audience, Viewer, build_run_view
from engine.mini_games.plugins import default_registry
from engine.mini_games.resolver import (
    MiniGameContentResolutionError,
    resolve_mini_game_package_snapshot,
)
from engine.mini_games.runtime import MiniGameRuntime, RunStateError
from engine.session.phases import current_phase, public_mini_game_result, tick
from engine.session.service import SessionService
from engine.tests.rounds_support import (
    Recorder,
    at,
    phased_arc,
    reach_phase,
    seat_session,
    where,
)

GAME_ID = "battle-of-wits"
PACKAGE = Path(__file__).resolve().parents[2] / "nightcap/mini_games" / GAME_ID
ROOT = "nightcap/mini_games"
START = at(100)

# Deliberately different from the order in which players see the cards.
CORRECT_SORT = ["copper", "pine", "willow", "opal"]
PARTIAL_SORT = ["copper", "willow", "pine", "opal"]


@pytest_asyncio.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    engine, factory = await make_sqlite_session_factory()
    try:
        async with factory() as session:
            yield session
    finally:
        await engine.dispose()


def choice(question: int, option: str) -> dict:
    return {"action": "choice", "question_index": question, "option_id": option}


def ordering(order: list[str]) -> dict:
    return {"action": "sort", "question_index": 1, "order": order}


def runtime(db: AsyncSession, now: datetime, bus=None) -> MiniGameRuntime:
    return MiniGameRuntime(
        db,
        bus if bus is not None else SessionEventBus(),
        default_registry(),
        clock=lambda: now,
    )


def aware(deadline: datetime | None) -> datetime:
    assert deadline is not None
    return deadline if deadline.tzinfo else deadline.replace(tzinfo=timezone.utc)


def view(run, character: UUID | None = None, audience=Audience.shared_display):
    return build_run_view(
        default_registry(),
        run,
        Viewer(Audience.player, str(character)) if character else Viewer(audience),
    ).runtime_state


@pytest.mark.asyncio
async def test_all_timeout_shares_last_rank_and_releases_nothing(
    db, registered, no_model_calls
):
    arc = phased_arc()
    registered(arc)
    seated = await seat_session(db, arc, players=2, start=False)
    snapshot = await resolve_mini_game_package_snapshot(
        db,
        session_id=seated.session_id,
        package_path=PACKAGE,
        quality_tier="low",
    )
    bus = SessionEventBus()
    game = runtime(db, START, bus)
    run = await game.create_run(seated.session_id, snapshot)
    await game.start_run(run.run_id)

    invalid = await game.submit_action(
        run.run_id,
        "malformed",
        seated.characters[0],
        ordering(["copper"] * 4),
    )
    assert not invalid.is_accepted
    async with db.begin_nested() as savepoint:
        with pytest.raises(RunStateError, match="not available"):
            await game.submit_action(
                run.run_id,
                "unknown",
                seated.characters[0],
                choice(0, "unknown"),
            )
        await savepoint.rollback()
    await db.refresh(run)
    run.deadline = aware(run.deadline)

    deadline = aware(run.deadline)
    late = runtime(db, deadline + timedelta(milliseconds=1), bus)
    event_count = len(bus.replay_since(0))
    async with db.begin_nested() as savepoint:
        with pytest.raises(RunStateError, match="window has closed"):
            await late.submit_action(
                run.run_id,
                "late",
                seated.characters[0],
                choice(0, "four"),
            )
        await savepoint.rollback()
    await db.refresh(run)
    assert view(run)["stage"]["phase"] == "question"
    assert len(bus.replay_since(0)) == event_count

    for _ in range(3):
        now = aware(run.deadline) + timedelta(milliseconds=1)
        await runtime(db, now).check_timeout(run.run_id)
        assert view(run)["stage"]["correct"] == []
        await runtime(
            db, aware(run.deadline) + timedelta(milliseconds=1)
        ).check_timeout(run.run_id)
    assert run.status == "timed_out"
    assert run.outcome["standing"] == [sorted(map(str, seated.participants))]
    assert run.outcome["scores"] == dict.fromkeys(map(str, seated.characters), 0)
    assert not run.clue_unlock_record["unlocked"]


@pytest.mark.asyncio
async def test_fresh_session_can_rejoin_and_submit(db, registered, no_model_calls):
    arc = phased_arc()
    registered(arc)
    seated = await seat_session(db, arc, players=2, start=False)
    snapshot = await resolve_mini_game_package_snapshot(
        db,
        session_id=seated.session_id,
        package_path=PACKAGE,
        quality_tier="low",
    )
    game = runtime(db, START)
    run = await game.create_run(seated.session_id, snapshot)
    await game.start_run(run.run_id)
    await db.commit()

    factory = async_sessionmaker(db.bind, expire_on_commit=False)
    async with factory() as fresh:
        game = runtime(fresh, START + timedelta(seconds=1))
        saved = await game.get_active_run(seated.session_id)
        assert saved is not None and saved.deadline == START + timedelta(seconds=12)
        result = await game.submit_action(
            saved.run_id,
            "fresh",
            seated.characters[0],
            choice(0, "four"),
        )
        assert result.is_accepted
        await fresh.commit()
    async with factory() as fresh:
        rejoined = await runtime(fresh, START).get_active_run(seated.session_id)
        assert view(rejoined, seated.characters[0])["player"][
            str(seated.characters[0])
        ]["locked"]


@pytest.mark.asyncio
@pytest.mark.parametrize("players", range(1, 9))
async def test_declared_counts_run_and_rank(db, registered, players, no_model_calls):
    arc = phased_arc()
    registered(arc)
    seated = await seat_session(db, arc, players=players, start=False)
    snapshot = await resolve_mini_game_package_snapshot(
        db,
        session_id=seated.session_id,
        package_path=PACKAGE,
        quality_tier="low",
    )
    assert (snapshot.min_players, snapshot.max_players) == (1, 8)
    game = runtime(db, START)
    run = await game.create_run(seated.session_id, snapshot)
    await game.start_run(run.run_id)
    assert aware(run.deadline) == START + timedelta(seconds=12)

    for index, seconds in enumerate((12, 20, 12)):
        stage = view(run)["stage"]
        assert (stage["phase"], stage["index"]) == ("question", index)
        if index == 1:
            answer = ordering(CORRECT_SORT)
        else:
            answer = choice(index, "four" if index == 0 else "east")
        deadline = aware(run.deadline)
        for seat, character in enumerate(seated.characters):
            submission = await runtime(
                db, deadline - timedelta(seconds=seat % seconds)
            ).submit_action(run.run_id, f"{index}-{seat}", character, answer)
            assert submission.is_accepted
        assert view(run)["stage"]["phase"] == "question"
        assert await runtime(db, deadline).check_timeout(run.run_id) is None
        reveal_at = deadline + timedelta(milliseconds=1)
        assert await runtime(db, reveal_at).check_timeout(run.run_id) is run
        revealed = view(run)["stage"]
        assert revealed["phase"] == "reveal"
        assert set(revealed["correct"]) == set(map(str, seated.characters))
        assert aware(run.deadline) == reveal_at + timedelta(seconds=5)
        await runtime(
            db, aware(run.deadline) + timedelta(milliseconds=1)
        ).check_timeout(run.run_id)

    assert run.status == "completed"
    assert run.outcome["scores"] == dict.fromkeys(map(str, seated.characters), 12)
    assert run.outcome["standing"] == [sorted(map(str, seated.participants))]
    assert not run.clue_unlock_record["unlocked"]


@pytest.mark.asyncio
@pytest.mark.parametrize("players", [2, 3, 4], ids=["two", "three", "four"])
async def test_round_starts_reveals_ranks_and_returns_to_story(
    db,
    registered: Callable[[ArcDefinition], None],
    monkeypatch,
    players,
    no_model_calls,
):
    binding = {"binding_id": "battle", "game_id": GAME_ID, "version": "0.1.0"}
    data = phased_arc(
        mini_game_root=ROOT,
        mini_games={"beat_one": [binding]},
    ).model_dump(mode="json")
    phase = next(p for p in data["beats"][1]["phases"] if p["kind"] == "mini_game")
    phase.update(seconds=75, result_hold_seconds=10, result_public=True)
    arc = ArcDefinition.model_validate(data)
    registered(arc)
    monkeypatch.setattr(
        "engine.session.mini_game_phase.build_registry", default_registry
    )
    seated = await seat_session(db, arc, players=players)
    recorder = Recorder()
    await tick(db, seated.session_id, at(0), recorder)
    await reach_phase(db, seated, "beat_one", "mini_game", START, recorder)
    run = await runtime(db, START).get_active_run(seated.session_id)
    assert run is not None and run.status == "active"
    run.deadline = aware(run.deadline)
    for index, payload in enumerate(
        (choice(0, "four"), ordering(CORRECT_SORT), choice(2, "east"))
    ):
        deadline = aware(run.deadline)
        await runtime(db, deadline - timedelta(seconds=1)).submit_action(
            run.run_id,
            str(index),
            seated.characters[0],
            payload,
        )
        await tick(db, seated.session_id, deadline + timedelta(seconds=1), recorder)
        assert view(run)["stage"]["phase"] == "reveal"
        await tick(
            db,
            seated.session_id,
            aware(run.deadline) + timedelta(seconds=1),
            recorder,
        )

    result = await public_mini_game_result(db, seated.session_id)
    expected = [
        [str(seated.participants[0])],
        sorted(map(str, seated.participants[1:])),
    ]
    assert result is not None and result["standing"] == expected
    assert run.outcome["scores"] == {
        str(seated.characters[0]): 12,
        **dict.fromkeys(map(str, seated.characters[1:]), 0),
    }
    assert not run.clue_unlock_record["unlocked"]
    hold = await current_phase(db, seated.session_id)
    assert hold is not None and hold.result_run_id == str(run.run_id)
    await tick(db, seated.session_id, aware(hold.deadline_at), recorder)
    assert (await where(db, seated.session_id))[:2] == ("beat_one", "bridge")
    assert await public_mini_game_result(db, seated.session_id) is None


@pytest.mark.asyncio
async def test_catch_up_rejoin_sort_credit_and_audience(db, registered, no_model_calls):
    arc = phased_arc()
    registered(arc)
    seated = await seat_session(db, arc, players=3, start=False)
    await SessionService().add_ai_character(db, seated.session_id)
    snapshot = await resolve_mini_game_package_snapshot(
        db,
        session_id=seated.session_id,
        package_path=PACKAGE,
        quality_tier="low",
    )
    bus = SessionEventBus()
    game = runtime(db, START, bus)
    run = await game.create_run(seated.session_id, snapshot)
    await game.start_run(run.run_id)
    lead, tied_last, absent = seated.characters

    async def advance():
        now = aware(run.deadline) + timedelta(milliseconds=1)
        await runtime(db, now, bus).check_timeout(run.run_id)
        return now

    first = await game.submit_action(run.run_id, "same", lead, choice(0, "four"))
    assert await game.submit_action(run.run_id, "same", lead, choice(0, "one")) is first
    async with db.begin_nested() as savepoint:
        with pytest.raises(RunStateError, match="already locked"):
            await game.submit_action(run.run_id, "second", lead, choice(0, "one"))
        await savepoint.rollback()
    await db.refresh(run)
    run.deadline = aware(run.deadline)
    assert view(run, lead)["player"][str(lead)]["locked"]
    assert "answer" not in view(run)["stage"]
    await advance()
    sort_started = await advance()
    assert view(run, lead)["player"][str(lead)] == {"locked": False}
    for character in (tied_last, absent):
        assert view(run, character)["player"] == {
            str(character): {
                "locked": False,
                "pinned": {"id": "copper", "position": 0},
            },
        }
    for audience in (Audience.host, Audience.shared_display):
        assert "player" not in view(run, audience=audience)
        assert "answer" not in view(run, audience=audience)["stage"]
    after_rejoin = await runtime(db, sort_started).get_active_run(seated.session_id)
    assert after_rejoin is not None
    assert view(after_rejoin, tied_last) == view(run, tied_last)
    sort_game = runtime(db, sort_started, bus)
    await sort_game.submit_action(run.run_id, "sort-lead", lead, ordering(CORRECT_SORT))
    await sort_game.submit_action(
        run.run_id, "sort-last", tied_last, ordering(PARTIAL_SORT)
    )
    await advance()
    assert view(run)["stage"]["scores"] == {
        str(lead): 8,
        str(tied_last): 2,
        str(absent): 0,
    }
    final_started = await advance()
    help_options = view(run, absent)["player"][str(absent)]["disabled"]
    assert len(set(help_options)) == 2 and "east" not in help_options
    assert "disabled" not in view(run, tied_last)["player"][str(tied_last)]
    private_events = [
        event
        for event in bus.replay_since(0)
        if event.event_type == "battle_of_wits_player"
    ]
    assert private_events and all(
        e.target_player_id in seated.participants for e in private_events
    )
    assert all(e.payload["run_id"] == str(run.run_id) for e in private_events)
    assert all(
        "player" not in e.payload
        for e in bus.replay_since(0)
        if e.event_type == "battle_of_wits_stage"
    )
    async with db.begin_nested() as savepoint:
        with pytest.raises(RunStateError, match="current question"):
            await runtime(db, final_started, bus).submit_action(
                run.run_id,
                "stale",
                absent,
                choice(0, "four"),
            )
        await savepoint.rollback()
    await db.refresh(run)
    run.deadline = aware(run.deadline)
    await advance()
    await advance()
    assert run.outcome["standing"] == [[str(p)] for p in seated.participants]


def test_game_id_registered():
    assert default_registry().get(GAME_ID).mechanic_type == GAME_ID


@pytest.mark.asyncio
async def test_private_fixture_is_resolved_from_the_selected_package(
    db,
    registered,
    tmp_path,
    no_model_calls,
):
    arc = phased_arc()
    registered(arc)
    seated = await seat_session(db, arc, players=2, start=False)
    package = tmp_path / GAME_ID
    copytree(PACKAGE, package)
    fixture = package / "server/questions-0.1.0.json"
    content = json.loads(fixture.read_text(encoding="utf-8"))
    questions = content["questions"]
    questions[0]["prompt"] = "A fresh invented question from the copied package."
    fixture.write_text(json.dumps(content), encoding="utf-8")
    snapshot = await resolve_mini_game_package_snapshot(
        db,
        session_id=seated.session_id,
        package_path=package,
        quality_tier="low",
    )
    fixture.unlink()
    game = runtime(db, START)
    run = await game.create_run(seated.session_id, snapshot)
    await game.start_run(run.run_id)
    assert view(run)["stage"]["prompt"] == questions[0]["prompt"]
    assert "answer" not in view(run)["stage"]


@pytest.mark.asyncio
async def test_private_content_must_stay_in_the_package_server_directory(db, tmp_path):
    package = tmp_path / GAME_ID
    copytree(PACKAGE, package)
    definition = package / "definitions/0.1.0.json"
    authored = json.loads(definition.read_text(encoding="utf-8"))
    authored["authored_content"]["server_content_path"] = "manifest.json"
    definition.write_text(json.dumps(authored), encoding="utf-8")
    with pytest.raises(
        MiniGameContentResolutionError, match="package server directory"
    ):
        await resolve_mini_game_package_snapshot(
            db,
            session_id=UUID(int=0),
            package_path=package,
            quality_tier="low",
        )
