"""Telemetry payload builders for session lifecycle events (Signals 4 and 5)."""

from __future__ import annotations

from typing import Any


def build_session_completed_payload(
    *,
    completion_type: str,
    final_beat_reached: str,
    killer_identified: bool,
    total_duration_seconds: int,
    player_count: int,
) -> dict[str, Any]:
    return {
        "completion_type": completion_type,
        "final_beat_reached": final_beat_reached,
        "killer_identified": killer_identified,
        "total_duration_seconds": total_duration_seconds,
        "player_count": player_count,
    }


def build_replay_intent_payload(
    *,
    intent: str,
    collection_method: str,
) -> dict[str, Any]:
    return {
        "intent": intent,
        "collection_method": collection_method,
    }
