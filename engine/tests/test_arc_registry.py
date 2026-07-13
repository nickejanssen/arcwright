"""Tests for the arc definition registry.

The registry is how the engine stays game-agnostic: which arcs exist, and
where their definition files live, is config in config/arcs.json rather
than engine code. These tests prove id resolution, caching identity, and
unknown-arc behavior.
"""

from __future__ import annotations

from engine.arc.registry import (
    default_arc_path,
    load_arc_definition,
    resolve_arc_path,
)


def test_load_arc_definition_resolves_registered_prefix() -> None:
    """An arc_id matching a registered prefix loads that arc definition."""
    arc = load_arc_definition("nightcap-v1")

    assert arc is not None
    assert arc.beats, "loaded arc must have beats"


def test_load_arc_definition_matches_prefix_with_version_suffix() -> None:
    """Prefix matching covers versioned arc ids without registry changes."""
    base = load_arc_definition("nightcap")
    versioned = load_arc_definition("nightcap-v2")

    assert base is not None
    assert versioned is not None
    # Same registry entry resolves to the same cached definition object.
    assert base is versioned


def test_load_arc_definition_returns_none_for_unregistered_arc() -> None:
    """Unknown arc ids resolve to None so callers decide error vs no-op."""
    assert load_arc_definition("some-other-game") is None
    assert resolve_arc_path("some-other-game") is None


def test_default_arc_path_points_at_registered_definition() -> None:
    """The default arc path exists and is a registered arc definition file."""
    path = default_arc_path()

    assert path.is_file()
    assert path == resolve_arc_path("nightcap")
