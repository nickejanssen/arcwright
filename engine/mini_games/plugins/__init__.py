"""Mechanic plugin stubs and registry factory.

Mechanic-specific scoring implementations are out of scope for AW-251.
This package provides the protocol, the stub shells, and the factory that
wires them into the closed registry consumed by ``MiniGameRuntime``.
"""

from engine.mini_games.plugins._evidence_locker_breach import EvidenceLockerBreachPlugin
from engine.mini_games.plugins._match_3_clue_race import Match3ClueRacePlugin
from engine.mini_games.runtime import MechanicRegistry


def default_registry() -> MechanicRegistry:
    """Return the standard closed registry with all approved mechanic plugins."""
    return MechanicRegistry(
        [
            Match3ClueRacePlugin(),
            EvidenceLockerBreachPlugin(),
        ]
    )


__all__ = [
    "EvidenceLockerBreachPlugin",
    "Match3ClueRacePlugin",
    "default_registry",
]
