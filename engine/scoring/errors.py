from __future__ import annotations


class ScoringError(Exception):
    """Base error for deterministic scoring and accusation-state failures."""


class AccusationLockedOutError(ScoringError):
    """Raised when an accusation is submitted while the player's lockout is active."""


class AlreadyCorrectError(ScoringError):
    """Raised when a player who already has a correct accusation submits another."""
