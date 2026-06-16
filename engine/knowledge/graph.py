"""Core knowledge graph operations against the facts and knowledge_states tables.

Architecture:
  - docs/architecture/04-knowledge-graph.md §4.2, §4.3
  - docs/architecture/15-development-guide.md §15.5

The assert/revoke/query trio is the only sanctioned entry into the
knowledge graph and is the canonical backing for both the arc execution
layer and the REST endpoints documented in §9.2.

Invariants:
  - A fact exists once per (session_id, fact_type, fact_content) — §4.2.
    The first assert with a given content tuple inserts; subsequent asserts
    reuse the existing fact_id and only add a new knowledge_states row.
  - Revoke writes a new knowledge_states row that supersedes the original.
    The original is never deleted (append-only, §4.3). The new "tombstone"
    row self-references via ``superseded_by = self.ks_id``, which makes the
    ``superseded_by IS NULL`` read query naturally exclude it without
    altering query semantics for callers.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from engine.db.orm import Fact, KnowledgeState


async def assert_knowledge(
    session: AsyncSession,
    *,
    session_id: UUID,
    character_id: UUID,
    fact_type: str,
    fact_content: dict[str, Any],
    source_character_id: UUID | None = None,
    confidence: float = 1.0,
    expires_at: datetime | None = None,
) -> KnowledgeState:
    """Make ``character_id`` know a fact.

    Upserts a ``facts`` row keyed on ``(session_id, fact_type, fact_content)``
    JSONB equality (per §4.2 — a fact exists once per session), then inserts
    a new ``knowledge_states`` row referencing it.

    ``provenance_chain`` is built by appending ``character_id`` to the
    source's current chain (or starting a fresh chain at ``[character_id]``
    when the source is None — direct observation).

    Signature matches docs/architecture/15-development-guide.md §15.5.
    """
    fact = await _get_or_create_fact(
        session,
        session_id=session_id,
        fact_type=fact_type,
        fact_content=fact_content,
    )

    provenance_chain = await _build_provenance_chain(
        session,
        session_id=session_id,
        character_id=character_id,
        source_character_id=source_character_id,
        fact_id=fact.fact_id,
    )

    ks = KnowledgeState(
        session_id=session_id,
        character_id=character_id,
        fact_id=fact.fact_id,
        source_character_id=source_character_id,
        confidence=confidence,
        provenance_chain=[str(uid) for uid in provenance_chain],
        expires_at=expires_at,
    )
    session.add(ks)
    await session.flush()
    return ks


async def get_character_knowledge(
    session: AsyncSession,
    *,
    session_id: UUID,
    character_id: UUID,
) -> list[KnowledgeState]:
    """Return all active (``superseded_by IS NULL``) knowledge states for a
    character in a session.

    Mandatory pre-generation chokepoint per §4.3.
    """
    result = await session.execute(
        select(KnowledgeState)
        .where(
            KnowledgeState.session_id == session_id,
            KnowledgeState.character_id == character_id,
            KnowledgeState.superseded_by.is_(None),
        )
        .order_by(KnowledgeState.asserted_at, KnowledgeState.fact_id)
        .options(selectinload(KnowledgeState.fact))
    )
    return list(result.scalars().all())


async def revoke_knowledge(
    session: AsyncSession,
    *,
    existing_ks_id: UUID,
    replacement: KnowledgeState,
) -> KnowledgeState:
    """Low-level: mark an existing knowledge state as superseded by a
    replacement record.

    The replacement must already be flushed (has a valid ``ks_id``). Caller
    should ``await session.flush()`` before passing the replacement if it
    was just created.
    """
    result = await session.execute(
        select(KnowledgeState).where(KnowledgeState.ks_id == existing_ks_id)
    )
    old_record: KnowledgeState = result.scalar_one()
    old_record.superseded_by = replacement.ks_id
    await session.flush()
    return old_record


async def revoke_fact_in_session(
    session: AsyncSession,
    *,
    session_id: UUID,
    fact_id: UUID,
) -> list[KnowledgeState]:
    """Mass-revoke a fact across every character that currently knows it.

    Backs ``DELETE /v1/sessions/{id}/knowledge/{fact_id}``. For each active
    knowledge state with the given ``fact_id`` in the session:
      1. Inserts a new tombstone knowledge state with ``confidence = 0.0``.
      2. Sets the tombstone's ``superseded_by`` to its own ``ks_id`` so it
         is excluded from the active-set query without altering the
         existing read predicate.
      3. Points the original record's ``superseded_by`` at the tombstone.

    Returns the tombstone records in the order they were created. Returns
    an empty list if nothing was active (idempotent re-revoke).
    """
    active = await session.execute(
        select(KnowledgeState).where(
            KnowledgeState.session_id == session_id,
            KnowledgeState.fact_id == fact_id,
            KnowledgeState.superseded_by.is_(None),
        )
    )
    tombstones: list[KnowledgeState] = []
    for original in active.scalars().all():
        tombstone = KnowledgeState(
            session_id=session_id,
            character_id=original.character_id,
            fact_id=fact_id,
            source_character_id=original.source_character_id,
            confidence=0.0,
            provenance_chain=list(original.provenance_chain or []),
        )
        session.add(tombstone)
        await session.flush()
        tombstone.superseded_by = tombstone.ks_id
        original.superseded_by = tombstone.ks_id
        await session.flush()
        tombstones.append(tombstone)
    return tombstones


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _get_or_create_fact(
    session: AsyncSession,
    *,
    session_id: UUID,
    fact_type: str,
    fact_content: dict[str, Any],
) -> Fact:
    """Return the existing fact for ``(session_id, fact_type, fact_content)``
    or insert a new one.

    Dedup test is exact content equality (§4.2 — "a fact exists once").
    Implemented in Python rather than SQL because JSONB equality semantics
    differ subtly across Postgres versions and SQLite has no JSONB at all.
    """
    result = await session.execute(
        select(Fact).where(
            Fact.session_id == session_id,
            Fact.fact_type == fact_type,
        )
    )
    for candidate in result.scalars().all():
        if candidate.fact_content == fact_content:
            return candidate

    fact = Fact(
        session_id=session_id,
        fact_type=fact_type,
        fact_content=dict(fact_content),
    )
    session.add(fact)
    await session.flush()
    return fact


async def _build_provenance_chain(
    session: AsyncSession,
    *,
    session_id: UUID,
    character_id: UUID,
    source_character_id: UUID | None,
    fact_id: UUID,
) -> list[UUID]:
    """Build the provenance chain for a new knowledge state.

    Per §4.2, the chain is the ordered list of character ids from original
    source to current knower. A direct observation (no source) starts a
    fresh chain at ``[character_id]``. If the source already has an active
    knowledge state for the same fact, the source's chain is the prefix
    and ``character_id`` is appended; otherwise the chain is
    ``[source_character_id, character_id]``.
    """
    if source_character_id is None:
        return [character_id]

    result = await session.execute(
        select(KnowledgeState)
        .where(
            KnowledgeState.session_id == session_id,
            KnowledgeState.character_id == source_character_id,
            KnowledgeState.fact_id == fact_id,
            KnowledgeState.superseded_by.is_(None),
        )
        .order_by(KnowledgeState.asserted_at.desc())
        .limit(1)
    )
    source_record = result.scalars().first()
    if source_record is None:
        return [source_character_id, character_id]

    prefix = [UUID(str(uid)) for uid in (source_record.provenance_chain or [])]
    if not prefix:
        prefix = [source_character_id]
    return [*prefix, character_id]
