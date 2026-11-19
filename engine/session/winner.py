"""The winner rule (spec 0094, Part I).

A pure function. Inputs are the players who solved it and the standing of
every finished mini-game run (tiers of player IDs, best first, ties sharing a
tier). No time and no order of arrival is an input.

  - nobody solved it: no winner.
  - one solver: that player wins.
  - several: most mini-game runs won, then the lowest sum of placings across
    all runs. Still level: they share the win.

A run is won by its top tier, unless that tier holds every player (a run that
separated nobody is won by nobody). A placing is the tier number, best tier
1; players in one tier share it. A player missing from a run's standing is
placed after its last tier.
"""

from __future__ import annotations

from collections.abc import Collection, Sequence
from dataclasses import dataclass
from typing import Any, Literal

DecidedBy = Literal[
    "no_solver", "only_solver", "mini_game_wins", "mini_game_placings", "shared"
]

Standing = Sequence[Sequence[str]]


@dataclass(frozen=True)
class WinnerResult:
    """``winners`` is empty when nobody solved it. ``decided_by`` names the rule
    that settled it, so the room can be told."""

    winners: tuple[str, ...]
    decided_by: DecidedBy


def run_winners(standing: Any) -> list[str]:
    """The top tier of one run's standing, or nobody when it holds every player
    (or there is no tier)."""
    if not isinstance(standing, list) or len(standing) < 2:
        return []
    top = standing[0]
    return [str(p) for p in top] if isinstance(top, list) else []


def placing(standing: Standing, player: str) -> int:
    """The tier number of ``player`` in one run, best tier 1."""
    for number, tier in enumerate(standing, start=1):
        if player in tier:
            return number
    return len(standing) + 1


def decide_winners(
    solvers: Collection[str], standings: Sequence[Standing]
) -> WinnerResult:
    """Who wins, and by which rule."""
    ordered = sorted(set(solvers))
    if not ordered:
        return WinnerResult((), "no_solver")
    if len(ordered) == 1:
        return WinnerResult((ordered[0],), "only_solver")

    wins = {player: 0 for player in ordered}
    for standing in standings:
        for player in run_winners(list(map(list, standing))):
            if player in wins:
                wins[player] += 1
    most = max(wins.values())
    leaders = [p for p in ordered if wins[p] == most]
    if len(leaders) == 1:
        return WinnerResult((leaders[0],), "mini_game_wins")

    placings = {p: sum(placing(s, p) for s in standings) for p in leaders}
    best = min(placings.values())
    closest = [p for p in leaders if placings[p] == best]
    if len(closest) == 1:
        return WinnerResult((closest[0],), "mini_game_placings")
    return WinnerResult(tuple(closest), "shared")
