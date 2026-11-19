"""The theory check (spec 0094, Part H).

A pure function: the case's solution slots and the locked theories in, right
or wrong for each player and slot out. It reads nothing else (no clock, order
of arrival, text or model), so the same inputs always give the same result.
It is run once, when the result is worked out, never while theories are still
being built.

A slot is right when the player's answer is one of the slot's accepted
answers. An answer's ``needs`` are for the fairness check and are not read
here. A player with no theory, or with a slot left empty, is wrong there.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from engine.case.authored.models import AuthoredSlot


@dataclass(frozen=True)
class TheoryCheck:
    """One player's result: ``slots`` holds ``(slot_id, right)`` in slot order."""

    slots: tuple[tuple[str, bool], ...]
    solved: bool


def check_theories(
    solution: Sequence[AuthoredSlot],
    theories: Mapping[str, Mapping[str, str] | None],
) -> dict[str, TheoryCheck]:
    """Judge every locked theory. ``theories`` maps a player's ID to their
    answers by slot ID, or to None when they have no theory."""
    accepted = {
        slot.slot_id: frozenset(answer.value for answer in slot.accepted)
        for slot in solution
    }
    results: dict[str, TheoryCheck] = {}
    for player, answers in theories.items():
        given = answers or {}
        slots = tuple(
            (slot.slot_id, given.get(slot.slot_id) in accepted[slot.slot_id])
            for slot in solution
        )
        results[player] = TheoryCheck(
            slots=slots, solved=bool(slots) and all(right for _, right in slots)
        )
    return results
