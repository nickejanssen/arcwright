"""The closing phases one at a time (AW-327, spec 0094 Part J).

The reveal, the result, the private part, the written truth and the arc file's
new rules. The whole game is in ``test_endgame_headless``. Made-up case and
lines only; no model is called.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Callable
from typing import Any
from uuid import UUID

import pytest
import pytest_asyncio
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.arc.models import ArcDefinition, PhaseDefinition, PhaseKind
from engine.db.orm import Decision
from engine.db.testing import make_sqlite_session_factory
from engine.events.models import AudienceTarget
from engine.session import closing
from engine.session.phases import (
    PhaseState,
    RoundError,
    current_phase,
    lock_theory,
    round_view,
    save_theory_draft,
    tick,
)
from engine.tests.rounds_support import (
    FIXTURE_RECAP,
    VALID_CASE,
    Recorder,
    Seated,
    at,
    closing_arc,
    closing_phases,
    phased_arc,
    seat_session,
    where,
)
from engine.tests.test_endgame_headless import (
    RIGHT,
    WRONG,
    everyone_ready,
    keys_of,
    play_to_last_call,
)

VERDICT_KEYS = {"solved", "right", "winners", "decided_by", "slots"}


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


async def lock_everyone(
    db: AsyncSession,
    seated: Seated,
    rec: Recorder,
    theories: list[dict[str, str] | None],
    now: float,
) -> None:
    """Save and lock a theory per seat; ``None`` leaves that seat with none."""
    for participant, theory in zip(seated.participants, theories, strict=True):
        if theory is None:
            continue
        await save_theory_draft(
            db, seated.session_id, participant, theory, "c_how_true", at(now), rec
        )
        await lock_theory(db, seated.session_id, participant, at(now), rec)


async def at_reveal(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    theories: list[dict[str, str] | None],
    *,
    players: int | None = None,
) -> tuple[Seated, Recorder, float]:
    arc = closing_arc()
    registered(arc)
    seated = await seat_session(db, arc, players=players or len(theories))
    rec = Recorder()
    now = await play_to_last_call(db, seated, rec) + 5
    await lock_everyone(db, seated, rec, theories, now)
    return seated, rec, now


class TestTheArcFile:
    def test_a_recap_phase_must_carry_recap_lines(self) -> None:
        with pytest.raises(ValidationError, match="recap"):
            PhaseDefinition.model_validate({"kind": "recap", "seconds": 5})

    def test_only_a_recap_phase_may_carry_recap_lines(self) -> None:
        with pytest.raises(ValidationError, match="recap"):
            PhaseDefinition.model_validate(
                {"kind": "reveal", "seconds": 5, "recap": FIXTURE_RECAP}
            )

    def test_case_closing_is_only_for_a_scene_without_lines_of_its_own(self) -> None:
        with pytest.raises(ValidationError, match="case_closing"):
            PhaseDefinition.model_validate(
                {"kind": "bridge", "seconds": 5, "source": "case_closing"}
            )
        with pytest.raises(ValidationError, match="case_closing"):
            PhaseDefinition.model_validate(
                {
                    "kind": "scene",
                    "seconds": 5,
                    "source": "case_closing",
                    "lines": [{"text": "x"}],
                }
            )

    def test_reveal_result_and_recap_follow_commit_in_that_order(self) -> None:
        phased_arc(
            phases={
                "finale": [
                    {"kind": "commit", "seconds": 5},
                    {"kind": "reveal", "seconds": 5},
                    {"kind": "result", "seconds": 5},
                    {"kind": "recap", "seconds": 5, "recap": FIXTURE_RECAP},
                ]
            }
        )
        with pytest.raises(ValidationError, match="order"):
            phased_arc(
                phases={
                    "finale": [
                        {"kind": "commit", "seconds": 5},
                        {"kind": "result", "seconds": 5},
                        {"kind": "reveal", "seconds": 5},
                    ]
                }
            )

    def test_a_reveal_or_result_needs_a_commit_phase_and_a_case(self) -> None:
        with pytest.raises(ValidationError, match="commit phase"):
            phased_arc(phases={"finale": [{"kind": "result", "seconds": 5}]})
        with pytest.raises(ValidationError, match="case_file"):
            phased_arc(
                case_path=None,
                phases={"finale": [{"kind": "reveal", "seconds": 5}]},
            )

    def test_a_recap_needs_a_case_and_a_result_before_it(self) -> None:
        recap = {"kind": "recap", "seconds": 5, "recap": FIXTURE_RECAP}
        with pytest.raises(ValidationError, match="result phase before"):
            phased_arc(phases={"finale": [recap]})
        with pytest.raises(ValidationError, match="result phase before"):
            phased_arc(
                phases={
                    "finale": [{"kind": "commit", "seconds": 5}, recap],
                }
            )
        with pytest.raises(ValidationError, match="case_file"):
            phased_arc(case_path=None, phases={"finale": [recap]})

    def test_the_prerequisites_must_come_earlier_in_the_arc_not_later(self) -> None:
        with pytest.raises(ValidationError, match="commit phase before"):
            phased_arc(
                mini_games={"beat_one": [], "beat_two": []},
                phases={
                    "beat_one": [{"kind": "result", "seconds": 5}],
                    "finale": [{"kind": "commit", "seconds": 5}],
                },
            )
        with pytest.raises(ValidationError, match="result phase before"):
            phased_arc(
                mini_games={"beat_one": [], "beat_two": []},
                phases={
                    "beat_one": [{"kind": "commit", "seconds": 5}],
                    "beat_two": [
                        {"kind": "recap", "seconds": 5, "recap": FIXTURE_RECAP}
                    ],
                    "finale": [{"kind": "result", "seconds": 5}],
                },
            )

    def test_the_closing_ending_loads(self) -> None:
        arc = closing_arc()
        kinds = [p.kind.value for b in arc.beats[-3:] for p in b.phases or []]
        assert kinds == ["commit", "reveal", "scene", "result", "recap"]
        assert set(closing_phases()) == {"finale", "truth", "verdict"}


class TestTheReveal:
    @pytest.mark.asyncio
    async def test_it_holds_only_the_shown_first_answer_and_no_verdict(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        _, rec, _ = await at_reveal(db, registered, [RIGHT, WRONG])
        (event,) = rec.of_type("theory_reveal")
        assert event.target_audience is AudienceTarget.all
        text = json.dumps(event.payload)
        for hidden in ("c_how_true", "c_how_false1", "slot_how"):
            assert hidden not in text
        assert not keys_of(event.payload) & VERDICT_KEYS

    @pytest.mark.asyncio
    @pytest.mark.parametrize("right_seat", [0, 1, 2])
    async def test_players_are_listed_in_the_same_order_whoever_is_right(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
        right_seat: int,
    ) -> None:
        theories = [RIGHT if seat == right_seat else WRONG for seat in range(3)]
        seated, rec, _ = await at_reveal(db, registered, theories)
        listed = [
            p["participant_id"]
            for p in rec.of_type("theory_reveal")[0].payload["players"]
        ]
        assert listed == sorted(str(p) for p in seated.participants)

    @pytest.mark.asyncio
    async def test_a_player_with_no_theory_has_no_answer_in_it(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec, now = await at_reveal(db, registered, [RIGHT, None])
        # The second player never locked, so Last Call is still on; time out.
        await tick(db, seated.session_id, at(now + 500), rec)
        by_player = {
            p["participant_id"]: p["answer"]
            for p in rec.of_type("theory_reveal")[0].payload["players"]
        }
        assert by_player[str(seated.participants[0])]["value"] == "marlowe"
        assert by_player[str(seated.participants[1])] is None


class TestTheResult:
    @pytest.mark.asyncio
    async def test_nothing_about_right_or_wrong_is_readable_before_the_result_phase(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec, _ = await at_reveal(db, registered, [RIGHT, WRONG])
        assert (await where(db, seated.session_id))[:2] == ("finale", "reveal")
        for who in (None, *seated.participants):
            view = await closing.closing_view(db, seated.session_id, who)
            assert view.result is None and view.recap is None and view.private is None
            assert not keys_of(view.reveal) & VERDICT_KEYS
        assert not rec.of_type("endgame_result")
        assert not rec.of_type("endgame_result_private")

    @pytest.mark.asyncio
    async def test_the_private_part_reaches_only_its_player_and_lists_their_slots(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec, now = await at_reveal(db, registered, [RIGHT, WRONG])
        await everyone_ready(db, seated, rec, now + 1)
        await everyone_ready(db, seated, rec, now + 2)
        assert (await where(db, seated.session_id))[:2] == ("verdict", "result")
        first, second = seated.participants
        for event in rec.of_type("endgame_result_private"):
            assert event.target_audience is AudienceTarget.specific_player
        public = rec.of_type("endgame_result")[0]
        assert "slots" not in json.dumps(public.payload)
        mine = closing_part(await closing.closing_view(db, seated.session_id, first))
        theirs = closing_part(await closing.closing_view(db, seated.session_id, second))
        assert [(s["slot_id"], s["right"]) for s in mine["slots"]] == [
            ("slot_who", True),
            ("slot_how", True),
        ]
        assert [(s["slot_id"], s["right"]) for s in theirs["slots"]] == [
            ("slot_who", False),
            ("slot_how", False),
        ]
        assert mine["participant_id"] == str(first)

    @pytest.mark.asyncio
    async def test_only_the_winners_proof_is_public(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec, now = await at_reveal(db, registered, [RIGHT, WRONG, WRONG])
        await everyone_ready(db, seated, rec, now + 1)
        await everyone_ready(db, seated, rec, now + 2)
        payload = rec.of_type("endgame_result")[0].payload
        assert [w["participant_id"] for w in payload["winners"]] == [
            str(seated.participants[0])
        ]
        assert payload["winners"][0]["proof"]["concept_id"] == "c_how_true"
        assert "c_how_false1" not in json.dumps(payload)
        assert payload["decided_by"] == "only_solver"

    @pytest.mark.asyncio
    async def test_a_second_entry_saves_and_sends_nothing_more(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec, now = await at_reveal(db, registered, [RIGHT, WRONG])
        await everyone_ready(db, seated, rec, now + 1)
        await everyone_ready(db, seated, rec, now + 2)
        state = await current_phase(db, seated.session_id)
        assert isinstance(state, PhaseState) and state.phase == "result"
        arc = closing_arc()
        await closing.enter(
            db, arc, seated.session_id, PhaseKind.result, state, at(now + 3), rec, 0
        )
        assert len(rec.of_type("endgame_result")) == 1
        assert await saved_rows(db, "endgame_result") == 1

    @pytest.mark.asyncio
    async def test_a_second_entry_to_the_recap_saves_and_sends_nothing_more(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec, now = await at_reveal(db, registered, [RIGHT, WRONG])
        for step in range(3):
            await everyone_ready(db, seated, rec, now + 1 + step)
        state = await current_phase(db, seated.session_id)
        assert isinstance(state, PhaseState) and state.phase == "recap"
        before = rec.of_type("recap_lines")[0].payload
        await closing.enter(
            db,
            closing_arc(),
            seated.session_id,
            PhaseKind.recap,
            state,
            at(now + 9),
            rec,
            1,
        )
        assert len(rec.of_type("recap_lines")) == 1
        assert await saved_rows(db, "recap_lines") == 1
        view = await closing.closing_view(db, seated.session_id)
        assert view.recap == before

    @pytest.mark.asyncio
    async def test_the_result_is_refused_for_someone_not_in_the_session(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, _, _ = await at_reveal(db, registered, [RIGHT, WRONG])
        with pytest.raises(RoundError) as refused:
            await closing.closing_view(db, seated.session_id, UUID(int=1))
        assert refused.value.code == "not_a_participant"


class TestTheWrittenTruth:
    @pytest.mark.asyncio
    async def test_the_truth_scene_shows_the_cases_closing_lines_and_only_then(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
    ) -> None:
        seated, rec, now = await at_reveal(db, registered, [RIGHT, WRONG])
        written = json.loads(VALID_CASE.read_text("utf-8"))["closing"]
        before = await round_view(db, seated.session_id, at(now))
        assert before.lines == ()
        assert not [
            e for e in rec.of_type("phase_line") if e.payload["beat_id"] == "truth"
        ]
        await everyone_ready(db, seated, rec, now + 1)
        view = await round_view(db, seated.session_id, at(now + 1))
        assert view.beat_id == "truth"
        assert [line["text"] for line in view.lines] == written


class TestOtherPlayerCounts:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("players", [1, 3, 5])
    async def test_the_closing_does_not_assume_two_or_four_players(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        no_model_calls: None,
        players: int,
    ) -> None:
        theories = [RIGHT] + [WRONG] * (players - 1)
        seated, rec, now = await at_reveal(db, registered, theories)
        for step in range(3):
            await everyone_ready(db, seated, rec, now + 1 + step)
        assert (await where(db, seated.session_id))[:2] == ("verdict", "recap")
        lines = rec.of_type("recap_lines")[0].payload["lines"]
        assert len(lines) == players
        assert len({line["participant_id"] for line in lines}) == players
        assert len(rec.of_type("endgame_result_private")) == players


async def saved_rows(db: AsyncSession, decision_type: str) -> int:
    count = await db.scalar(
        select(func.count())
        .select_from(Decision)
        .where(Decision.decision_type == decision_type)
    )
    return int(count or 0)


def closing_part(view: closing.ClosingView) -> dict[str, Any]:
    assert view.private is not None
    return view.private
