"""Pure deterministic superlative computation for completed sessions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

from engine.scoring.models import AccusationAttempt

CatchRecord = int | Sequence[datetime]


def compute_superlatives(
    accusations: Sequence[AccusationAttempt],
    confirmed_catches_by_player: Mapping[str, CatchRecord],
    evidence_by_player: Mapping[str, int],
) -> dict[str, str]:
    """Return the three session superlatives from immutable input data.

    Best Interrogator uses the same deterministic point dimensions as the
    reveal summary. Lie Detector prioritizes catch count then earliest catch.
    Most Confidently Wrong prioritizes wrong-attempt count then penalty size.
    """
    participants = {
        *evidence_by_player,
        *confirmed_catches_by_player,
        *(attempt.accuser_participant_id for attempt in accusations),
    }
    if not participants:
        raise ValueError("superlatives require at least one participant")

    catch_counts = {
        participant_id: _catch_count(confirmed_catches_by_player.get(participant_id, 0))
        for participant_id in participants
    }

    best_interrogator = min(
        participants,
        key=lambda participant_id: (
            -(
                evidence_by_player.get(participant_id, 0) * 10
                + catch_counts[participant_id] * 50
                + sum(
                    attempt.points_awarded
                    for attempt in accusations
                    if attempt.accuser_participant_id == participant_id
                )
            ),
            participant_id,
        ),
    )

    lie_detector = min(
        participants,
        key=lambda participant_id: (
            -catch_counts[participant_id],
            _earliest_catch(confirmed_catches_by_player.get(participant_id, 0)),
            participant_id,
        ),
    )

    wrong_by_player = {
        participant_id: [
            attempt
            for attempt in accusations
            if attempt.accuser_participant_id == participant_id
            and attempt.outcome.value == "wrong"
        ]
        for participant_id in participants
    }
    most_confidently_wrong = min(
        participants,
        key=lambda participant_id: (
            -len(wrong_by_player[participant_id]),
            -sum(
                abs(attempt.points_awarded)
                for attempt in wrong_by_player[participant_id]
            ),
            participant_id,
        ),
    )

    return {
        "best_interrogator": best_interrogator,
        "lie_detector": lie_detector,
        "most_confidently_wrong": most_confidently_wrong,
    }


def _catch_count(value: CatchRecord) -> int:
    if isinstance(value, int):
        return value
    return len(value)


def _earliest_catch(value: CatchRecord) -> datetime:
    if isinstance(value, int) or not value:
        return datetime.max.replace(tzinfo=timezone.utc)
    return min(_as_utc(timestamp) for timestamp in value)


def _as_utc(value: Any) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
