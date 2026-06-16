"""Tests for the in-memory SessionService (AW-217 acceptance criteria).

AC5: session lifecycle state machine and join-token validation.
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from engine.session.models import QualityTier, SessionStatus
from engine.session.service import (
    SessionNotFoundError,
    SessionService,
    SessionStateError,
)


@pytest.fixture()
def svc() -> SessionService:
    return SessionService()


class TestCreateSession:
    def test_returns_session_and_join_token(self, svc: SessionService) -> None:
        session, token = svc.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )

        assert session.arc_id == "nightcap-v1"
        assert session.status is SessionStatus.created
        assert session.current_beat_id == "arrival"
        assert session.player_count == 0
        assert isinstance(token, str) and len(token) > 0

    def test_respects_quality_tier(self, svc: SessionService) -> None:
        session, _ = svc.create_session(
            arc_id="nightcap-v1",
            host_account_id=uuid4(),
            quality_tier=QualityTier.premium,
        )
        assert session.quality_tier is QualityTier.premium

    def test_each_call_returns_distinct_session_id(self, svc: SessionService) -> None:
        s1, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        s2, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        assert s1.session_id != s2.session_id

    def test_created_at_is_set(self, svc: SessionService) -> None:
        session, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        assert session.created_at is not None


class TestGetSession:
    def test_returns_none_for_unknown_session(self, svc: SessionService) -> None:
        assert svc.get_session(uuid4()) is None

    def test_returns_session_after_create(self, svc: SessionService) -> None:
        session, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        result = svc.get_session(session.session_id)
        assert result is not None
        assert result.session_id == session.session_id


class TestStartSession:
    def test_transitions_to_active(self, svc: SessionService) -> None:
        session, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        started = svc.start_session(session.session_id, uuid4())

        assert started.status is SessionStatus.active
        assert started.started_at is not None

    def test_fails_if_already_active(self, svc: SessionService) -> None:
        session, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        svc.start_session(session.session_id, uuid4())
        with pytest.raises(SessionStateError):
            svc.start_session(session.session_id, uuid4())

    def test_fails_for_unknown_session(self, svc: SessionService) -> None:
        with pytest.raises(SessionNotFoundError):
            svc.start_session(uuid4(), uuid4())


class TestPauseResumeSession:
    def test_pause_transitions_active_to_paused(self, svc: SessionService) -> None:
        session, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        svc.start_session(session.session_id, uuid4())
        paused = svc.pause_session(session.session_id, uuid4())
        assert paused.status is SessionStatus.paused

    def test_resume_transitions_paused_to_active(self, svc: SessionService) -> None:
        session, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        svc.start_session(session.session_id, uuid4())
        svc.pause_session(session.session_id, uuid4())
        resumed = svc.resume_session(session.session_id, uuid4())
        assert resumed.status is SessionStatus.active

    def test_pause_fails_if_not_active(self, svc: SessionService) -> None:
        session, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        with pytest.raises(SessionStateError):
            svc.pause_session(session.session_id, uuid4())

    def test_resume_fails_if_not_paused(self, svc: SessionService) -> None:
        session, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        svc.start_session(session.session_id, uuid4())
        with pytest.raises(SessionStateError):
            svc.resume_session(session.session_id, uuid4())


class TestEndSession:
    def test_transitions_to_completed_from_active(self, svc: SessionService) -> None:
        session, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        svc.start_session(session.session_id, uuid4())
        ended = svc.end_session(session.session_id, uuid4())

        assert ended.status is SessionStatus.completed
        assert ended.completed_at is not None

    def test_end_session_can_end_created_session(self, svc: SessionService) -> None:
        session, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        ended = svc.end_session(session.session_id, uuid4())
        assert ended.status is SessionStatus.completed

    def test_end_fails_if_already_completed(self, svc: SessionService) -> None:
        session, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        svc.end_session(session.session_id, uuid4())
        with pytest.raises(SessionStateError):
            svc.end_session(session.session_id, uuid4())

    def test_end_fails_for_unknown_session(self, svc: SessionService) -> None:
        with pytest.raises(SessionNotFoundError):
            svc.end_session(uuid4(), uuid4())


class TestValidateJoinToken:
    def test_returns_participant_for_valid_token(self, svc: SessionService) -> None:
        session, host_token = svc.create_session(
            arc_id="nightcap-v1", host_account_id=uuid4()
        )
        participant = svc.validate_join_token(session.session_id, host_token)

        assert participant is not None
        assert participant.session_id == session.session_id
        assert participant.surface_type == "host"

    def test_returns_none_for_unknown_token(self, svc: SessionService) -> None:
        session, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        assert svc.validate_join_token(session.session_id, "not-a-real-token") is None

    def test_returns_none_when_token_belongs_to_different_session(
        self, svc: SessionService
    ) -> None:
        s1, t1 = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        s2, _ = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        assert svc.validate_join_token(s2.session_id, t1) is None

    def test_tokens_are_unique_per_session(self, svc: SessionService) -> None:
        _, t1 = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        _, t2 = svc.create_session(arc_id="nightcap-v1", host_account_id=uuid4())
        assert t1 != t2
