"""Stub plugin for the evidence-locker-breach mechanic (evidence-locker-402).

Mechanic-specific scoring is out of scope for AW-251. This stub satisfies
the registry dispatch slot. A future task implements score() and is_threshold_met().
"""

from __future__ import annotations

from typing import Any

from engine.db.orm import MiniGameSubmission
from engine.mini_games.resolver import ResolvedMiniGameSnapshot

MECHANIC_TYPE = "evidence-locker-breach"


class EvidenceLockerBreachPlugin:
    mechanic_type: str = MECHANIC_TYPE

    def validate_payload(self, payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise ValueError("payload must be a JSON object")

    def is_threshold_met(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
    ) -> bool:
        return False

    def score(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
    ) -> dict[str, Any]:
        raise NotImplementedError(
            "evidence-locker-breach scoring is not yet implemented (AW-253)"
        )
