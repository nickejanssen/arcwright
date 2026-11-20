"""What each audience may read of a mini-game run's saved state (AW-347).

A run's saved mechanic state can hold every player's private input. A mechanic
declares, as data, which top-level keys of that state are public and which are
per-player; this module copies out only what the viewer may see. The default is
to send nothing: no rule, an unknown mechanic or a malformed value gives an
empty result, never the raw state.

Pure and deterministic. No arc logic, no model calls, no rendering.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
from typing import Any

from engine.mini_games.runtime import (
    MechanicRegistry,
    MiniGameRuntime,
    UnknownMechanicTypeError,
)


class Audience(str, Enum):
    shared_display = "shared_display"
    player = "player"
    host = "host"


@dataclass(frozen=True)
class Viewer:
    """Who is reading. A player is identified by character ID."""

    audience: Audience
    character_id: str | None = None


@dataclass(frozen=True)
class AudienceRule:
    """A mechanic's declaration of what each audience may read.

    ``public_state``: top-level state keys everyone may read.
    ``own_state``: top-level state keys whose value maps character ID to that
    player's entry. A player reads only their own entry; nobody else gets the key.
    ``withheld_presentation``: presentation keys kept from the shared display and
    the host (for example a prompt meant for one phone).
    """

    public_state: tuple[str, ...] = ()
    own_state: tuple[str, ...] = ()
    withheld_presentation: tuple[str, ...] = ()


@dataclass(frozen=True)
class RunView:
    runtime_state: dict[str, Any]
    presentation: dict[str, Any]


def _nothing() -> RunView:
    return RunView(runtime_state={}, presentation={})


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def build_run_view(registry: MechanicRegistry, run: Any, viewer: Viewer) -> RunView:
    """Copy out the part of the run's state and presentation the viewer may read."""
    snapshot = _as_dict(getattr(run, "definition_snapshot", None))
    mechanic_type = snapshot.get("mechanic_type")
    if not isinstance(mechanic_type, str):
        return _nothing()
    try:
        plugin = registry.get(mechanic_type)
    except UnknownMechanicTypeError:
        return _nothing()

    presentation = _as_dict(snapshot.get("presentation"))
    rule = getattr(plugin, "audience_rule", None)
    if not isinstance(rule, AudienceRule):
        return RunView(runtime_state={}, presentation=copy.deepcopy(presentation))

    own_entries = viewer.audience is Audience.player and viewer.character_id
    withheld = () if own_entries else rule.withheld_presentation
    shown_presentation = {
        key: copy.deepcopy(value)
        for key, value in presentation.items()
        if key not in withheld
    }

    state = MiniGameRuntime._mechanic_state(run)

    runtime_state: dict[str, Any] = {
        key: copy.deepcopy(state[key]) for key in rule.public_state if key in state
    }
    if own_entries:
        for key in rule.own_state:
            entries = state.get(key)
            if not isinstance(entries, dict):
                continue
            mine = str(viewer.character_id)
            if mine in entries:
                runtime_state[key] = {mine: copy.deepcopy(entries[mine])}
    return RunView(runtime_state=runtime_state, presentation=shown_presentation)
