"""Tests for the in-memory CharacterService (AW-218).

AC1: Player input endpoint accepts typed character action or dialogue input.
AC3: Player clients cannot reach another character's surface.
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from engine.characters.service import (
    CharacterAccessError,
    CharacterNotFoundError,
    CharacterService,
)
from engine.session.service import SessionService


@pytest.fixture()
def services() -> tuple[SessionService, CharacterService]:
    sessions = SessionService()
    return sessions, CharacterService(sessions=sessions)


class TestListCharacters:
    def test_excludes_host_participant(
        self, services: tuple[SessionService, CharacterService]
    ) -> None:
        sessions, characters = services
        session, _ = sessions.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        sessions.add_player(session.session_id)
        sessions.add_player(session.session_id)

        result = characters.list_characters(session.session_id)
        assert len(result) == 2
        assert all(c.surface_type == "player" for c in result)

    def test_unknown_session_returns_empty_list(
        self, services: tuple[SessionService, CharacterService]
    ) -> None:
        _, characters = services
        assert characters.list_characters(uuid4()) == []


class TestGetCharacterForPlayer:
    def test_owner_receives_detail(
        self, services: tuple[SessionService, CharacterService]
    ) -> None:
        sessions, characters = services
        session, _ = sessions.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        participant, _ = sessions.add_player(session.session_id)

        detail = characters.get_character_for_player(
            session.session_id,
            participant.character_id,
            participant.participant_id,
        )
        assert detail.character_id == participant.character_id
        assert detail.participant_id == participant.participant_id

    def test_non_owner_is_rejected(
        self, services: tuple[SessionService, CharacterService]
    ) -> None:
        sessions, characters = services
        session, _ = sessions.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        owner, _ = sessions.add_player(session.session_id)
        intruder, _ = sessions.add_player(session.session_id)

        with pytest.raises(CharacterAccessError):
            characters.get_character_for_player(
                session.session_id,
                owner.character_id,
                intruder.participant_id,
            )

    def test_unknown_character_raises(
        self, services: tuple[SessionService, CharacterService]
    ) -> None:
        sessions, characters = services
        session, _ = sessions.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        with pytest.raises(CharacterNotFoundError):
            characters.get_character_for_player(session.session_id, uuid4(), uuid4())


class TestSubmitInput:
    def test_owner_can_submit_action(
        self, services: tuple[SessionService, CharacterService]
    ) -> None:
        sessions, characters = services
        session, _ = sessions.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        participant, _ = sessions.add_player(session.session_id)

        record = characters.submit_input(
            session_id=session.session_id,
            character_id=participant.character_id,
            requesting_participant_id=participant.participant_id,
            kind="action",
            content="Looks under the table.",
        )
        assert record.kind == "action"
        assert record.content == "Looks under the table."
        assert characters.get_inputs(session.session_id) == [record]

    def test_owner_can_submit_dialogue(
        self, services: tuple[SessionService, CharacterService]
    ) -> None:
        sessions, characters = services
        session, _ = sessions.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        participant, _ = sessions.add_player(session.session_id)

        record = characters.submit_input(
            session_id=session.session_id,
            character_id=participant.character_id,
            requesting_participant_id=participant.participant_id,
            kind="dialogue",
            content="Where were you at midnight?",
        )
        assert record.kind == "dialogue"

    def test_non_owner_cannot_submit(
        self, services: tuple[SessionService, CharacterService]
    ) -> None:
        sessions, characters = services
        session, _ = sessions.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        owner, _ = sessions.add_player(session.session_id)
        intruder, _ = sessions.add_player(session.session_id)

        with pytest.raises(CharacterAccessError):
            characters.submit_input(
                session_id=session.session_id,
                character_id=owner.character_id,
                requesting_participant_id=intruder.participant_id,
                kind="action",
                content="impersonation attempt",
            )

    def test_unknown_character_raises(
        self, services: tuple[SessionService, CharacterService]
    ) -> None:
        sessions, characters = services
        session, _ = sessions.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        with pytest.raises(CharacterNotFoundError):
            characters.submit_input(
                session_id=session.session_id,
                character_id=uuid4(),
                requesting_participant_id=uuid4(),
                kind="action",
                content="x",
            )
