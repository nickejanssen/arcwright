"""Database-backed deterministic accusation resolution."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, MutableMapping
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.case.models import ResolvedCase
from engine.claims.models import ContradictionOutcome
from engine.db.orm import Accusation, ContradictionFlag, SuspectLock
from engine.scoring.calculator import (
    accusation_base_value,
    chain_reaction_countdown,
    momentum_multiplier,
    motive_method_bonus,
    wrong_accusation_cost,
)
from engine.scoring.errors import AccusationLockedOutError, AlreadyCorrectError
from engine.scoring.models import AccusationAttempt, AccusationOutcome

TelemetryRecorder = Callable[[AsyncSession, UUID, AccusationAttempt], Awaitable[None]]
Clock = Callable[[], datetime]


def accusations_locked_or_countdown_expired(
    remaining_seconds: float,
    *,
    eligible_participant_ids: set[str],
    locked_out_participant_ids: set[str],
) -> bool:
    """Return whether Last Call can end by expiry or an all-locked state."""
    if remaining_seconds <= 0:
        return True
    return (
        bool(eligible_participant_ids)
        and eligible_participant_ids <= locked_out_participant_ids
    )


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class AccusationResolver:
    """Resolve private accusations against an already-resolved case truth."""

    def __init__(
        self,
        *,
        resolved_case: ResolvedCase,
        session_id: UUID | None = None,
        session_context: MutableMapping[str, Any] | None = None,
        clock: Clock = _utcnow,
        round_duration_seconds: float = 60.0,
        last_call_duration_seconds: float = 300.0,
        telemetry_recorder: TelemetryRecorder | None = None,
    ) -> None:
        self.resolved_case = resolved_case
        self.session_id = session_id
        self.session_context = session_context if session_context is not None else {}
        self._clock = clock
        self._round_duration_seconds = round_duration_seconds
        self._last_call_duration_seconds = last_call_duration_seconds
        self._telemetry_recorder = telemetry_recorder

    async def submit_accusation(
        self,
        db_session: AsyncSession,
        *,
        session_id: UUID | str | None = None,
        accuser_participant_id: UUID | str,
        beat_id: str,
        beat_progress_fraction: float,
        accused_cast_member_id: str,
        motive_correct: bool | None,
        method_correct: bool | None,
    ) -> AccusationAttempt:
        active_session_id = self._resolve_session_id(session_id)
        participant_id = UUID(str(accuser_participant_id))
        now = self._clock()

        prior_attempts = await self._load_attempts(
            db_session,
            session_id=active_session_id,
            participant_id=participant_id,
        )
        if any(
            attempt.outcome == AccusationOutcome.correct.value
            for attempt in prior_attempts
        ):
            raise AlreadyCorrectError(
                f"participant {participant_id} already has a correct accusation"
            )

        latest = prior_attempts[-1] if prior_attempts else None
        if latest is not None and latest.lockout_until is not None:
            if _as_utc(latest.lockout_until) > _as_utc(now):
                last_call_attempts = [
                    attempt
                    for attempt in prior_attempts
                    if attempt.beat_id == "last_call"
                ]
                last_word_escape = (
                    beat_id == "last_call"
                    and latest.beat_id == "last_call"
                    and latest.outcome == AccusationOutcome.wrong.value
                    and latest.used_last_word
                    and len(last_call_attempts) == 1
                )
                if not last_word_escape:
                    raise AccusationLockedOutError(
                        f"participant {participant_id} is locked out until "
                        f"{latest.lockout_until.isoformat()}"
                    )

        last_attempt = prior_attempts[-1] if prior_attempts else None
        catches_banked = await self._count_confirmed_catches(
            db_session,
            session_id=active_session_id,
            participant_id=participant_id,
            since=last_attempt.submitted_at if last_attempt is not None else None,
        )
        prior_wrong_count = sum(
            attempt.outcome == AccusationOutcome.wrong.value
            for attempt in prior_attempts
        )
        is_correct = accused_cast_member_id == self.resolved_case.culprit_id
        prior_correct_count = sum(
            attempt.outcome == AccusationOutcome.correct.value
            for attempt in await self._load_session_attempts(
                db_session, session_id=active_session_id
            )
        )

        if is_correct:
            accusation_points = round(
                accusation_base_value(
                    beat_id, beat_progress_fraction=beat_progress_fraction
                )
                * (1 + momentum_multiplier(catches_banked))
            )
            points_awarded = accusation_points + motive_method_bonus(
                motive_correct=bool(motive_correct),
                method_correct=bool(method_correct),
            )
            outcome = AccusationOutcome.correct
            lockout_until = None
            used_last_word = False
        else:
            lockout_rounds, points_awarded = wrong_accusation_cost(
                beat_id, repeat_offense_count=prior_wrong_count
            )
            lockout_until = self._lockout_until(
                beat_id=beat_id,
                lockout_rounds=lockout_rounds,
                now=now,
            )
            outcome = AccusationOutcome.wrong
            used_last_word = beat_id == "last_call" and not any(
                attempt.used_last_word
                for attempt in prior_attempts
                if attempt.beat_id == "last_call"
            )

        row = Accusation(
            session_id=active_session_id,
            accuser_participant_id=participant_id,
            beat_id=beat_id,
            accused_cast_member_id=accused_cast_member_id,
            motive_correct=motive_correct,
            method_correct=method_correct,
            outcome=outcome.value,
            catches_banked_at_submission=catches_banked,
            points_awarded=points_awarded,
            repeat_offense_count=prior_wrong_count,
            lockout_until=lockout_until,
            used_last_word=used_last_word,
            triggered_last_call=is_correct and prior_correct_count == 0,
        )
        db_session.add(row)
        await db_session.flush()

        submitted_at = row.submitted_at or now
        if is_correct:
            self._update_countdown(
                prior_correct_count=prior_correct_count,
            )

        attempt = AccusationAttempt(
            session_id=str(active_session_id),
            accuser_participant_id=str(participant_id),
            beat_id=beat_id,
            accused_cast_member_id=accused_cast_member_id,
            outcome=outcome,
            catches_banked_at_submission=catches_banked,
            points_awarded=points_awarded,
            motive_correct=motive_correct,
            method_correct=method_correct,
            repeat_offense_count=prior_wrong_count,
            lockout_until=lockout_until,
            used_last_word=used_last_word,
            triggered_last_call=row.triggered_last_call,
            accusation_id=str(row.accusation_id),
            submitted_at=submitted_at,
        )
        if self._telemetry_recorder is not None:
            await self._telemetry_recorder(db_session, active_session_id, attempt)
        return attempt

    async def set_suspect_lock(
        self,
        db_session: AsyncSession,
        *,
        session_id: UUID | str | None = None,
        participant_id: UUID | str,
        suspect_cast_member_id: str,
    ) -> None:
        active_session_id = self._resolve_session_id(session_id)
        participant_uuid = UUID(str(participant_id))
        result = await db_session.execute(
            select(SuspectLock)
            .where(
                SuspectLock.session_id == active_session_id,
                SuspectLock.participant_id == participant_uuid,
            )
            .with_for_update()
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = SuspectLock(
                session_id=active_session_id,
                participant_id=participant_uuid,
                suspect_cast_member_id=suspect_cast_member_id,
                updated_at=self._clock(),
            )
            db_session.add(row)
        else:
            row.suspect_cast_member_id = suspect_cast_member_id
            row.updated_at = self._clock()
        await db_session.flush()

    def _resolve_session_id(self, session_id: UUID | str | None) -> UUID:
        value = session_id if session_id is not None else self.session_id
        if value is None:
            raise ValueError("session_id is required")
        return UUID(str(value))

    async def _load_attempts(
        self,
        db_session: AsyncSession,
        *,
        session_id: UUID,
        participant_id: UUID,
    ) -> list[Accusation]:
        result = await db_session.execute(
            select(Accusation)
            .where(
                Accusation.session_id == session_id,
                Accusation.accuser_participant_id == participant_id,
            )
            .order_by(Accusation.submitted_at, Accusation.accusation_id)
        )
        return list(result.scalars().all())

    async def _load_session_attempts(
        self, db_session: AsyncSession, *, session_id: UUID
    ) -> list[Accusation]:
        result = await db_session.execute(
            select(Accusation)
            .where(Accusation.session_id == session_id)
            .order_by(Accusation.submitted_at, Accusation.accusation_id)
        )
        return list(result.scalars().all())

    async def _count_confirmed_catches(
        self,
        db_session: AsyncSession,
        *,
        session_id: UUID,
        participant_id: UUID,
        since: datetime | None,
    ) -> int:
        query = (
            select(func.count())
            .select_from(ContradictionFlag)
            .where(
                ContradictionFlag.session_id == session_id,
                ContradictionFlag.flagged_by_participant_id == participant_id,
                ContradictionFlag.outcome == ContradictionOutcome.confirmed.value,
            )
        )
        if since is not None:
            query = query.where(ContradictionFlag.created_at > since)
        return int((await db_session.scalar(query)) or 0)

    def _lockout_until(
        self, *, beat_id: str, lockout_rounds: float, now: datetime
    ) -> datetime:
        if beat_id == "last_call":
            remaining = float(
                self.session_context.get(
                    "last_call_remaining_seconds", self._last_call_duration_seconds
                )
            )
            return now + timedelta(seconds=max(0.0, remaining))
        return now + timedelta(seconds=lockout_rounds * self._round_duration_seconds)

    def _update_countdown(self, *, prior_correct_count: int) -> None:
        if prior_correct_count == 0:
            self.session_context.setdefault(
                "last_call_remaining_seconds", self._last_call_duration_seconds
            )
            return
        remaining = float(
            self.session_context.get(
                "last_call_remaining_seconds", self._last_call_duration_seconds
            )
        )
        self.session_context["last_call_remaining_seconds"] = chain_reaction_countdown(
            remaining,
            additional_correct_count=1,
        )
