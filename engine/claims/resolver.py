"""Database-backed claim recording and deterministic contradiction resolution."""

from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.case.models import AuthorizedFalsehood
from engine.claims.errors import ClaimNotFoundError
from engine.claims.evidence import participant_matching_evidence
from engine.claims.models import ClaimRecord, ContradictionOutcome, FlagResult
from engine.db.orm import Claim, ContradictionFlag
from engine.telemetry.claims import record_contradiction_outcome


class ClaimResolver:
    """Record claims and resolve flags for one session's authorized falsehoods."""

    def __init__(
        self,
        *,
        session_id: UUID,
        authorized_falsehoods: Sequence[AuthorizedFalsehood] = (),
    ) -> None:
        self.session_id = session_id
        self._falsehoods = {
            falsehood.falsehood_id: falsehood for falsehood in authorized_falsehoods
        }

    async def record_claim(
        self,
        db_session: AsyncSession,
        *,
        claim: ClaimRecord,
    ) -> ClaimRecord:
        """Persist one claim and return its database identifiers."""
        row = Claim(
            session_id=self.session_id,
            speaker_character_id=UUID(claim.speaker_id),
            asker_participant_id=(
                UUID(claim.asker_id) if claim.asker_id is not None else None
            ),
            round_index=claim.round_index,
            beat_id=claim.beat_id,
            interaction_window_id=claim.interaction_window_id,
            claim_text=claim.claim_text,
            referenced_fact_ids=list(claim.referenced_fact_ids),
            is_authorized_lie=claim.is_authorized_lie,
            falsehood_id=claim.falsehood_id,
        )
        db_session.add(row)
        await db_session.flush()
        return claim.model_copy(
            update={
                "claim_id": str(row.claim_id),
                "created_at": row.created_at,
            }
        )

    async def resolve_flag(
        self,
        db_session: AsyncSession,
        *,
        claim_id: str,
        flagging_participant_id: str,
    ) -> FlagResult:
        """Resolve a flag using authorized-lie and evidence-possession gates."""
        try:
            claim_uuid = UUID(claim_id)
            participant_uuid = UUID(flagging_participant_id)
        except ValueError as exc:
            raise ClaimNotFoundError(f"claim {claim_id!r} was not found") from exc

        claim_result = await db_session.execute(
            select(Claim).where(Claim.claim_id == claim_uuid).with_for_update()
        )
        claim = claim_result.scalar_one_or_none()
        if claim is None or claim.session_id != self.session_id:
            raise ClaimNotFoundError(f"claim {claim_id!r} was not found")

        confirmed = await db_session.scalar(
            select(ContradictionFlag.flag_id).where(
                ContradictionFlag.claim_id == claim_uuid,
                ContradictionFlag.outcome == ContradictionOutcome.confirmed.value,
            )
        )
        already_resolved = confirmed is not None

        evidence_id_used: str | None = None
        falsehood = (
            self._falsehoods.get(claim.falsehood_id)
            if not already_resolved
            and claim.is_authorized_lie
            and claim.falsehood_id is not None
            else None
        )
        if falsehood is not None:
            evidence_id_used = await participant_matching_evidence(
                db_session,
                session_id=claim.session_id,
                participant_id=participant_uuid,
                evidence_ids=list(falsehood.contradicted_by),
            )

        outcome = (
            ContradictionOutcome.confirmed
            if evidence_id_used is not None
            else ContradictionOutcome.rejected
        )
        if already_resolved:
            outcome = ContradictionOutcome.rejected
        db_session.add(
            ContradictionFlag(
                claim_id=claim_uuid,
                session_id=claim.session_id,
                flagged_by_participant_id=participant_uuid,
                outcome=outcome.value,
                evidence_id_used=evidence_id_used,
            )
        )
        await db_session.flush()
        result = FlagResult(
            claim_id=claim_id,
            outcome=outcome,
            evidence_id_used=evidence_id_used,
        )
        await record_contradiction_outcome(db_session, claim.session_id, result)
        return result
