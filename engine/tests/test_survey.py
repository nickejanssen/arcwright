"""Survey answers (AW-331, spec 0095 M3).

One answer set per player, saved as rows. A repeat is a new row and the newest
counts. The engine checks only the shape; the questions belong to the game.
Made-up arc and case only; no model is called.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition
from engine.db.orm import Event
from engine.db.testing import make_sqlite_session_factory
from engine.session import survey
from engine.session.phases import RoundError
from engine.session.service import SessionService
from engine.tests.rounds_support import Seated, at, closing_arc, seat_session


@pytest_asyncio.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    engine, factory = await make_sqlite_session_factory()
    try:
        async with factory() as session:
            try:
                yield session
            finally:
                await session.rollback()
    finally:
        await engine.dispose()


async def started(
    db: AsyncSession, registered: Callable[[ArcDefinition], None]
) -> Seated:
    arc = closing_arc()
    registered(arc)
    return await seat_session(db, arc, players=2)


GOOD: dict[str, Any] = {"fun": 4, "length": "long"}


class TestSaving:
    @pytest.mark.asyncio
    async def test_a_players_answers_are_saved_and_read_back(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated = await started(db, registered)
        me = seated.participants[0]
        assert await survey.read_survey(db, seated.session_id, me) is None
        saved = await survey.save_survey(
            db, seated.session_id, me, GOOD, "Loved it.", at(1)
        )
        assert saved.answers == GOOD and saved.comment == "Loved it."
        read = await survey.read_survey(db, seated.session_id, me)
        assert read is not None
        assert read.answers == GOOD and read.comment == "Loved it."

    @pytest.mark.asyncio
    async def test_answers_are_kept_per_player(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated = await started(db, registered)
        a, b = seated.participants
        await survey.save_survey(db, seated.session_id, a, {"fun": 5}, None, at(1))
        await survey.save_survey(db, seated.session_id, b, {"fun": 2}, None, at(1))
        one = await survey.read_survey(db, seated.session_id, a)
        two = await survey.read_survey(db, seated.session_id, b)
        assert one is not None and two is not None
        assert one.answers == {"fun": 5} and two.answers == {"fun": 2}
        assert await survey.answered_ids(db, seated.session_id) == {str(a), str(b)}

    @pytest.mark.asyncio
    async def test_a_repeat_replaces_it_and_the_older_row_is_kept(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated = await started(db, registered)
        me = seated.participants[0]
        await survey.save_survey(db, seated.session_id, me, {"fun": 1}, "meh", at(1))
        await survey.save_survey(db, seated.session_id, me, {"fun": 5}, None, at(2))
        read = await survey.read_survey(db, seated.session_id, me)
        assert read is not None
        assert read.answers == {"fun": 5} and read.comment is None
        assert read.revision == 2
        rows = (
            (
                await db.execute(
                    select(Event).where(
                        Event.session_id == seated.session_id,
                        Event.event_type == survey.SURVEY_EVENT,
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(rows) == 2
        assert {r.payload["revision"] for r in rows} == {1, 2}

    @pytest.mark.asyncio
    async def test_a_comment_is_optional(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated = await started(db, registered)
        saved = await survey.save_survey(
            db, seated.session_id, seated.participants[0], {"fun": 3}, None, at(1)
        )
        assert saved.comment is None


class TestRefusals:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "answers",
        [
            {},
            {"fun": 0},
            {"fun": 6},
            {"fun": 3.5},
            {"fun": True},
            {"fun": ""},
            {"fun": "x" * 41},
            {"": 3},
            {"k" * 41: 3},
            {"fun": [1]},
            {"fun": None},
            {f"q{i}": 3 for i in range(9)},
        ],
    )
    async def test_a_bad_shape_is_refused(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        answers: dict[str, Any],
    ) -> None:
        seated = await started(db, registered)
        with pytest.raises(RoundError) as refused:
            await survey.save_survey(
                db, seated.session_id, seated.participants[0], answers, None, at(1)
            )
        assert refused.value.code == "invalid_survey"
        assert await survey.answered_ids(db, seated.session_id) == set()

    @pytest.mark.asyncio
    async def test_eight_answers_are_allowed_and_a_long_comment_is_not(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated = await started(db, registered)
        me = seated.participants[0]
        await survey.save_survey(
            db, seated.session_id, me, {f"q{i}": 3 for i in range(8)}, "x" * 1000, at(1)
        )
        with pytest.raises(RoundError) as refused:
            await survey.save_survey(
                db, seated.session_id, me, {"fun": 3}, "x" * 1001, at(2)
            )
        assert refused.value.code == "invalid_survey"

    @pytest.mark.asyncio
    async def test_someone_who_is_not_a_player_here_is_refused(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated = await started(db, registered)
        svc = SessionService()
        slots = await svc.list_participants(db, seated.session_id)
        creator = next(p for p in slots if p.surface_type == "host")
        ai = await svc.add_ai_character(db, seated.session_id)
        for who in (uuid4(), creator.participant_id, ai.participant_id):
            with pytest.raises(RoundError) as refused:
                await survey.save_survey(db, seated.session_id, who, GOOD, None, at(1))
            assert refused.value.code == "not_a_participant"
            with pytest.raises(RoundError) as unread:
                await survey.read_survey(db, seated.session_id, who)
            assert unread.value.code == "not_a_participant"

    @pytest.mark.asyncio
    async def test_a_session_that_has_not_started_takes_no_answers(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        arc = closing_arc()
        registered(arc)
        seated = await seat_session(db, arc, players=1, start=False)
        with pytest.raises(RoundError) as refused:
            await survey.save_survey(
                db, seated.session_id, seated.participants[0], GOOD, None, at(1)
            )
        assert refused.value.code == "game_not_started"

    @pytest.mark.asyncio
    async def test_an_unknown_session_is_not_found(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        await started(db, registered)
        missing: UUID = uuid4()
        with pytest.raises(RoundError) as refused:
            await survey.save_survey(db, missing, uuid4(), GOOD, None, at(1))
        assert refused.value.code == "session_not_found"


class TestTheEngineHoldsNoQuestions:
    def test_the_survey_module_names_no_game(self) -> None:
        from pathlib import Path

        text = Path(survey.__file__).read_text("utf-8").casefold()
        for word in ("detective", "nightcap", "murder", "suspect", "killer"):
            assert word not in text
