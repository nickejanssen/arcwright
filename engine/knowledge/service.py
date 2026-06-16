"""In-memory knowledge state service for the single-process MVP API surface.

Architecture: docs/architecture/09-developer-api.md §9.2.

The async ``engine.knowledge.graph`` module persists knowledge state through
the Postgres-backed ORM. That module remains the source of truth for arc
execution and generation context. This module is a lightweight in-memory
analogue that backs the REST endpoints exposed at MVP, mirroring the same
pattern as ``engine.session.service`` (AW-217). Persistence is a later M3
task; swap this module then.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


class KnowledgeFactNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class KnowledgeFact:
    fact_id: UUID
    session_id: UUID
    character_id: UUID
    fact_type: str
    fact_content: dict[str, Any]
    confidence: float
    source_character_id: UUID | None
    asserted_at: datetime
    revoked_at: datetime | None = None


@dataclass
class KnowledgeService:
    """In-process per-character knowledge facts."""

    _facts: dict[UUID, KnowledgeFact] = field(default_factory=dict)
    _by_session: dict[UUID, list[UUID]] = field(default_factory=dict)

    def assert_fact(
        self,
        *,
        session_id: UUID,
        character_id: UUID,
        fact_type: str,
        fact_content: dict[str, Any],
        confidence: float = 1.0,
        source_character_id: UUID | None = None,
    ) -> KnowledgeFact:
        """Insert a new active fact for ``character_id`` in ``session_id``."""
        fact = KnowledgeFact(
            fact_id=uuid4(),
            session_id=session_id,
            character_id=character_id,
            fact_type=fact_type,
            fact_content=dict(fact_content),
            confidence=confidence,
            source_character_id=source_character_id,
            asserted_at=datetime.now(tz=timezone.utc),
        )
        self._facts[fact.fact_id] = fact
        self._by_session.setdefault(session_id, []).append(fact.fact_id)
        return fact

    def revoke_fact(self, session_id: UUID, fact_id: UUID) -> KnowledgeFact:
        """Mark ``fact_id`` revoked. Idempotent in the sense that the active
        bit is cleared even if called twice.

        Raises ``KnowledgeFactNotFoundError`` if no fact exists, or if the fact
        belongs to a different session.
        """
        fact = self._facts.get(fact_id)
        if fact is None or fact.session_id != session_id:
            raise KnowledgeFactNotFoundError(fact_id)
        revoked = KnowledgeFact(
            fact_id=fact.fact_id,
            session_id=fact.session_id,
            character_id=fact.character_id,
            fact_type=fact.fact_type,
            fact_content=fact.fact_content,
            confidence=fact.confidence,
            source_character_id=fact.source_character_id,
            asserted_at=fact.asserted_at,
            revoked_at=fact.revoked_at or datetime.now(tz=timezone.utc),
        )
        self._facts[fact_id] = revoked
        return revoked

    def get_character_knowledge(
        self, session_id: UUID, character_id: UUID
    ) -> list[KnowledgeFact]:
        """Return all active (not revoked) facts for ``character_id``."""
        return [
            self._facts[fact_id]
            for fact_id in self._by_session.get(session_id, [])
            if self._facts[fact_id].character_id == character_id
            and self._facts[fact_id].revoked_at is None
        ]


_knowledge_service = KnowledgeService()
