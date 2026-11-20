"""The host seat (AW-331, spec 0095 Q1 and M6, D-133).

The first human seat to join is the host. The role is saved as rows, checked on
every call, and can be handed to another seated human. An AI seat is never the
host. Made-up arc and case only; no model is called.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.arc.models import ArcDefinition
from engine.db.testing import make_sqlite_session_factory
from engine.events.models import AudienceTarget
from engine.session import host_seat
from engine.session.phases import RoundError
from engine.session.service import SessionService
from engine.tests.rounds_support import Recorder, at, closing_arc


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


async def room(
    db: AsyncSession, registered: Callable[[ArcDefinition], None], names: list[str]
) -> tuple[SessionService, UUID, list[UUID]]:
    arc = closing_arc()
    registered(arc)
    svc = SessionService()
    created, _ = await svc.create_session(
        db, arc_id=arc.arc_id, host_account_id=uuid4()
    )
    seated = [
        (
            await svc.lobby_join(
                db, join_code=str(created.join_code), display_name=name
            )
        ).participant_id
        for name in names
    ]
    return svc, created.session_id, seated


class TestTheFirstJoinIsTheHost:
    @pytest.mark.asyncio
    async def test_the_first_seat_is_host_and_the_second_is_not(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        _svc, session_id, (first, second) = await room(db, registered, ["Ada", "Bo"])
        assert await host_seat.current_host(db, session_id) == first
        assert await host_seat.is_host_seat(db, session_id, first)
        assert not await host_seat.is_host_seat(db, session_id, second)

    @pytest.mark.asyncio
    async def test_a_session_nobody_joined_has_no_host_seat(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        _svc, session_id, _ = await room(db, registered, [])
        assert await host_seat.current_host(db, session_id) is None
        assert not await host_seat.is_host_seat(db, session_id, uuid4())

    @pytest.mark.asyncio
    async def test_the_session_creators_own_slot_is_never_the_host_seat(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        svc, session_id, (first,) = await room(db, registered, ["Ada"])
        slots = await svc.list_participants(db, session_id)
        creator = next(p for p in slots if p.surface_type == "host")
        assert not await host_seat.is_host_seat(db, session_id, creator.participant_id)
        assert not await host_seat.is_seated_player(
            db, session_id, creator.participant_id
        )
        assert await host_seat.is_seated_player(db, session_id, first)

    @pytest.mark.asyncio
    async def test_an_ai_seat_is_never_host_and_never_a_seated_player(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        svc, session_id, _ = await room(db, registered, [])
        ai = await svc.add_ai_character(db, session_id)
        await svc.lobby_join(
            db,
            join_code=str(
                (await svc.get_session(db, session_id)).join_code  # type: ignore[union-attr]
            ),
            display_name="Ada",
        )
        host = await host_seat.current_host(db, session_id)
        assert host is not None and host != ai.participant_id
        assert not await host_seat.is_seated_player(db, session_id, ai.participant_id)

    @pytest.mark.asyncio
    async def test_the_choice_is_saved_not_held_in_memory(
        self,
        factory: async_sessionmaker[AsyncSession],
        registered: Callable[[ArcDefinition], None],
    ) -> None:
        async with factory() as db:
            _svc, session_id, (first, _second) = await room(
                db, registered, ["Ada", "Bo"]
            )
            await db.commit()
        async with factory() as fresh:
            assert await host_seat.current_host(fresh, session_id) == first

    @pytest.mark.asyncio
    async def test_two_phones_joining_at_once_give_exactly_one_host(
        self,
        factory: async_sessionmaker[AsyncSession],
        registered: Callable[[ArcDefinition], None],
    ) -> None:
        arc = closing_arc()
        registered(arc)
        svc = SessionService()
        async with factory() as setup:
            created, _ = await svc.create_session(
                setup, arc_id=arc.arc_id, host_account_id=uuid4()
            )
            await setup.commit()
        code = str(created.join_code)

        async def join(name: str) -> UUID:
            async with factory() as db:
                participant = await svc.lobby_join(
                    db, join_code=code, display_name=name
                )
                await db.commit()
                return participant.participant_id

        joined = await asyncio.gather(*(join(n) for n in ("Ada", "Bo", "Cy")))
        async with factory() as check:
            hosts = [
                p
                for p in joined
                if await host_seat.is_host_seat(check, created.session_id, p)
            ]
        assert len(hosts) == 1


class TestHandingOver:
    @pytest.mark.asyncio
    async def test_hand_over_moves_the_role_at_once_and_tells_the_room(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        _svc, session_id, (first, second) = await room(db, registered, ["Ada", "Bo"])
        rec = Recorder()
        new_host = await host_seat.hand_over(db, session_id, second, at(1), rec)
        assert new_host == second
        assert await host_seat.current_host(db, session_id) == second
        assert not await host_seat.is_host_seat(db, session_id, first)
        assert await host_seat.is_host_seat(db, session_id, second)
        told = rec.of_type("host_changed")
        assert len(told) == 1
        assert told[0].target_audience is AudienceTarget.all
        assert told[0].payload == {"participant_id": str(second), "display_name": "Bo"}

    @pytest.mark.asyncio
    async def test_the_role_can_go_back_and_forth(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        _svc, session_id, (first, second) = await room(db, registered, ["Ada", "Bo"])
        await host_seat.hand_over(db, session_id, second, at(1))
        await host_seat.hand_over(db, session_id, first, at(2))
        assert await host_seat.current_host(db, session_id) == first

    @pytest.mark.asyncio
    async def test_it_cannot_go_to_the_current_host(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        _svc, session_id, (first, _second) = await room(db, registered, ["Ada", "Bo"])
        with pytest.raises(RoundError) as refused:
            await host_seat.hand_over(db, session_id, first, at(1))
        assert refused.value.code == "already_host"

    @pytest.mark.asyncio
    async def test_it_cannot_go_to_someone_who_is_not_seated(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        svc, session_id, (_first,) = await room(db, registered, ["Ada"])
        ai = await svc.add_ai_character(db, session_id)
        slots = await svc.list_participants(db, session_id)
        creator = next(p for p in slots if p.surface_type == "host")
        for target in (uuid4(), ai.participant_id, creator.participant_id):
            with pytest.raises(RoundError) as refused:
                await host_seat.hand_over(db, session_id, target, at(1))
            assert refused.value.code == "not_a_participant"

    @pytest.mark.asyncio
    async def test_an_unknown_session_is_not_found(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        await room(db, registered, [])
        with pytest.raises(RoundError) as refused:
            await host_seat.hand_over(db, uuid4(), uuid4(), at(1))
        assert refused.value.code == "session_not_found"

    @pytest.mark.asyncio
    async def test_a_session_with_no_host_seat_can_be_given_one(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        svc, session_id, _ = await room(db, registered, [])
        participant, _token = await svc.add_player(db, session_id)
        assert await host_seat.current_host(db, session_id) is None
        await host_seat.hand_over(db, session_id, participant.participant_id, at(1))
        assert await host_seat.current_host(db, session_id) == (
            participant.participant_id
        )


class TestSeatedPlayers:
    @pytest.mark.asyncio
    async def test_a_player_of_another_session_is_not_seated_here(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        _svc, session_id, (_first,) = await room(db, registered, ["Ada"])
        _svc2, _other_id, (stranger,) = await room(db, registered, ["Zed"])
        assert not await host_seat.is_seated_player(db, session_id, stranger)
        assert not await host_seat.is_host_seat(db, session_id, stranger)
