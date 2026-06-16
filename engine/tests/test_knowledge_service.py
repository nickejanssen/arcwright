"""Tests for the in-memory KnowledgeService (AW-218).

AC2: Knowledge assert, revoke, and query operations work as documented.
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from engine.knowledge.service import (
    KnowledgeFactNotFoundError,
    KnowledgeService,
)


@pytest.fixture()
def svc() -> KnowledgeService:
    return KnowledgeService()


class TestAssertFact:
    def test_returns_fact_with_id_and_timestamp(self, svc: KnowledgeService) -> None:
        session_id = uuid4()
        character_id = uuid4()
        fact = svc.assert_fact(
            session_id=session_id,
            character_id=character_id,
            fact_type="alibi",
            fact_content={"location": "library", "time": "21:30"},
        )
        assert fact.session_id == session_id
        assert fact.character_id == character_id
        assert fact.fact_content == {"location": "library", "time": "21:30"}
        assert fact.revoked_at is None

    def test_appears_in_character_knowledge(self, svc: KnowledgeService) -> None:
        session_id = uuid4()
        character_id = uuid4()
        fact = svc.assert_fact(
            session_id=session_id,
            character_id=character_id,
            fact_type="alibi",
            fact_content={"x": 1},
        )
        facts = svc.get_character_knowledge(session_id, character_id)
        assert [f.fact_id for f in facts] == [fact.fact_id]


class TestRevokeFact:
    def test_revoke_clears_active_set(self, svc: KnowledgeService) -> None:
        session_id = uuid4()
        character_id = uuid4()
        fact = svc.assert_fact(
            session_id=session_id,
            character_id=character_id,
            fact_type="clue",
            fact_content={"a": 1},
        )
        svc.revoke_fact(session_id, fact.fact_id)
        assert svc.get_character_knowledge(session_id, character_id) == []

    def test_revoke_marks_revoked_at(self, svc: KnowledgeService) -> None:
        session_id = uuid4()
        character_id = uuid4()
        fact = svc.assert_fact(
            session_id=session_id,
            character_id=character_id,
            fact_type="clue",
            fact_content={},
        )
        revoked = svc.revoke_fact(session_id, fact.fact_id)
        assert revoked.revoked_at is not None

    def test_revoke_unknown_fact_raises(self, svc: KnowledgeService) -> None:
        with pytest.raises(KnowledgeFactNotFoundError):
            svc.revoke_fact(uuid4(), uuid4())

    def test_revoke_with_wrong_session_raises(self, svc: KnowledgeService) -> None:
        session_id = uuid4()
        fact = svc.assert_fact(
            session_id=session_id,
            character_id=uuid4(),
            fact_type="clue",
            fact_content={},
        )
        with pytest.raises(KnowledgeFactNotFoundError):
            svc.revoke_fact(uuid4(), fact.fact_id)


class TestQuery:
    def test_isolates_by_character(self, svc: KnowledgeService) -> None:
        session_id = uuid4()
        a = uuid4()
        b = uuid4()
        svc.assert_fact(
            session_id=session_id,
            character_id=a,
            fact_type="clue",
            fact_content={"k": "a"},
        )
        svc.assert_fact(
            session_id=session_id,
            character_id=b,
            fact_type="clue",
            fact_content={"k": "b"},
        )
        a_facts = svc.get_character_knowledge(session_id, a)
        b_facts = svc.get_character_knowledge(session_id, b)
        assert len(a_facts) == 1 and a_facts[0].fact_content == {"k": "a"}
        assert len(b_facts) == 1 and b_facts[0].fact_content == {"k": "b"}

    def test_isolates_by_session(self, svc: KnowledgeService) -> None:
        character_id = uuid4()
        s1 = uuid4()
        s2 = uuid4()
        svc.assert_fact(
            session_id=s1,
            character_id=character_id,
            fact_type="clue",
            fact_content={"k": 1},
        )
        assert svc.get_character_knowledge(s2, character_id) == []
