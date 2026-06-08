"""Deterministic trace canonicalization helpers for harness runs."""

from __future__ import annotations

from typing import Any

from engine.harness.models import HarnessTraceEntry

_STRUCTURAL_TRACE_FIELDS = (
    "step_index",
    "transition_name",
    "from_configuration",
    "to_configuration",
    "payload",
)


def canonicalize_trace(trace: list[HarnessTraceEntry]) -> list[dict[str, Any]]:
    """Keep only the structural fields used for deterministic comparisons."""

    return [
        {
            "step_index": entry.step_index,
            "transition_name": entry.transition_name,
            "from_configuration": list(entry.from_configuration),
            "to_configuration": list(entry.to_configuration),
            "payload": dict(entry.payload),
        }
        for entry in trace
    ]


def traces_equal(left: list[HarnessTraceEntry], right: list[HarnessTraceEntry]) -> bool:
    return canonicalize_trace(left) == canonicalize_trace(right)


__all__ = [
    "canonicalize_trace",
    "traces_equal",
    "_STRUCTURAL_TRACE_FIELDS",
]
