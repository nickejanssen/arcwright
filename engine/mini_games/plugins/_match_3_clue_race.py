"""Stub plugin for the match-3-clue-race mechanic (crime-scene-smash).

Mechanic-specific scoring is out of scope for AW-251. This stub satisfies
the registry dispatch slot. A future task implements score() and is_threshold_met().
"""

from __future__ import annotations

from typing import Any

from engine.db.orm import MiniGameSubmission
from engine.mini_games.resolver import ResolvedMiniGameSnapshot

MECHANIC_TYPE = "match-3-clue-race"


class Match3ClueRacePlugin:
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
            "match-3-clue-race scoring is not yet implemented (AW-252)"
        )
