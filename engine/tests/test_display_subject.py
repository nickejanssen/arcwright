"""Who a display address may personalise for (AW-331, spec 0095 M4).

No sign-in, with or without a character ID, is the shared view. A player's own
view goes only to a sign-in whose seat owns that character. Anyone else who
names a character is refused. Made-up arc and case only.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition
from engine.db.testing import make_sqlite_session_factory
from engine.session.phases import RoundError
from engine.session.room_view import display_subject
from engine.tests.rounds_support import Seated, closing_arc, seat_session


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


async def seated_two(
    db: AsyncSession, registered: Callable[[ArcDefinition], None]
) -> Seated:
    arc = closing_arc()
    registered(arc)
    return await seat_session(db, arc, players=2)


@pytest.mark.asyncio
async def test_no_sign_in_and_a_character_id_gives_the_shared_view(
    db: AsyncSession, registered: Callable[[ArcDefinition], None]
) -> None:
    seated = await seated_two(db, registered)
    subject = await display_subject(
        db,
        seated.session_id,
        character_id=seated.characters[0],
        signed_in=False,
        participant_id=None,
    )
    assert subject is None


@pytest.mark.asyncio
async def test_no_character_id_is_always_the_shared_view(
    db: AsyncSession, registered: Callable[[ArcDefinition], None]
) -> None:
    seated = await seated_two(db, registered)
    for signed_in, participant in (
        (False, None),
        (True, seated.participants[0]),
        (True, None),
    ):
        assert (
            await display_subject(
                db,
                seated.session_id,
                character_id=None,
                signed_in=signed_in,
                participant_id=participant,
            )
            is None
        )


@pytest.mark.asyncio
async def test_the_owner_of_a_character_gets_their_own_view(
    db: AsyncSession, registered: Callable[[ArcDefinition], None]
) -> None:
    seated = await seated_two(db, registered)
    subject = await display_subject(
        db,
        seated.session_id,
        character_id=seated.characters[1],
        signed_in=True,
        participant_id=seated.participants[1],
    )
    assert subject == seated.characters[1]


@pytest.mark.asyncio
async def test_another_players_sign_in_is_refused(
    db: AsyncSession, registered: Callable[[ArcDefinition], None]
) -> None:
    seated = await seated_two(db, registered)
    with pytest.raises(RoundError) as refused:
        await display_subject(
            db,
            seated.session_id,
            character_id=seated.characters[1],
            signed_in=True,
            participant_id=seated.participants[0],
        )
    assert refused.value.code == "not_your_character"


@pytest.mark.asyncio
async def test_a_sign_in_with_no_seat_is_refused_when_it_names_a_character(
    db: AsyncSession, registered: Callable[[ArcDefinition], None]
) -> None:
    """A host token or a display token carries no player seat."""
    seated = await seated_two(db, registered)
    with pytest.raises(RoundError) as refused:
        await display_subject(
            db,
            seated.session_id,
            character_id=seated.characters[0],
            signed_in=True,
            participant_id=None,
        )
    assert refused.value.code == "not_your_character"


@pytest.mark.asyncio
async def test_a_seat_from_another_session_is_refused(
    db: AsyncSession, registered: Callable[[ArcDefinition], None]
) -> None:
    seated = await seated_two(db, registered)
    with pytest.raises(RoundError) as refused:
        await display_subject(
            db,
            seated.session_id,
            character_id=seated.characters[0],
            signed_in=True,
            participant_id=uuid4(),
        )
    assert refused.value.code == "not_your_character"
