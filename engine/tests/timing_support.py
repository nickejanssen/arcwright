"""Time budgets that follow how busy the machine is (AW-350).

A fixed time limit fails whenever the computer is busy, even when the code is
fine. ``machine_slowdown`` runs a small fixed piece of plain Python and compares
its fastest run to ``CALM_SECONDS``, the time that same work takes on an idle
machine. A budget is its calm-machine limit times that factor, so heavy load
raises the limit and the check still fails when the code itself gets slower.

The work is pure Python that never touches the engine, so a real slowdown in
the engine never inflates the factor and cannot excuse itself.
"""

from __future__ import annotations

import time

CALM_SECONDS = 0.037
"""Fastest time of ``_calibration_work`` on an idle machine."""

_ROUNDS = 7


def _calibration_work() -> int:
    table: dict[str, int] = {}
    for i in range(60_000):
        key = f"k{i % 997}"
        table[key] = table.get(key, 0) + len(key) * i
    return sum(sorted(table.values())[:50])


def fastest_calibration_run() -> float:
    best = float("inf")
    for _ in range(_ROUNDS):
        started = time.perf_counter()
        _calibration_work()
        best = min(best, time.perf_counter() - started)
    return best


def machine_slowdown() -> float:
    """How many times slower than an idle machine this one is right now (at least 1)."""
    return max(1.0, fastest_calibration_run() / CALM_SECONDS)
