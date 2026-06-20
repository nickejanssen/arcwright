"""Telemetry payload builder for knowledge constraint events (Signal 3)."""

from __future__ import annotations

from typing import Any


def build_knowledge_constraint_payload(
    *,
    character_id: str,
    fact_type: str,
    constraint_direction: str,
    provenance_chain_length: int,
) -> dict[str, Any]:
    return {
        "character_id": character_id,
        "fact_type": fact_type,
        "constraint_direction": constraint_direction,
        "provenance_chain_length": provenance_chain_length,
    }
