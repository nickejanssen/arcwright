"""Telemetry payload builder for arc beat transition events (Signal 1)."""

from __future__ import annotations

from typing import Any


def build_beat_transition_payload(
    *,
    from_beat: str,
    to_beat: str,
    duration_seconds: int,
    player_action_count: int,
) -> dict[str, Any]:
    return {
        "from_beat": from_beat,
        "to_beat": to_beat,
        "duration_seconds": duration_seconds,
        "player_action_count": player_action_count,
    }
