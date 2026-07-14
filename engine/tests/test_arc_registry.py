"""Tests for the arc definition registry.

The registry is how the engine finds arc definitions without hardcoding
any game's file location: `config/arc_registry.json` maps arc id prefixes
to definition paths, mirroring the routing-table pattern.
"""

from __future__ import annotations

from engine.arc.registry import (
    ARC_REGISTRY_PATH,
    default_arc_path,
    load_arc_definition,
    resolve_arc_path,
)


def test_registry_config_lives_in_config_directory() -> None:
    assert ARC_REGISTRY_PATH.parent.name == "config"
    assert ARC_REGISTRY_PATH.exists()


def test_versioned_arc_id_resolves_by_prefix() -> None:
    """Session rows store versioned ids like "nightcap-v1"; prefix matching
    must resolve them to the registered definition."""
    arc = load_arc_definition("nightcap-v1")
    assert arc is not None
    assert arc.arc_id == "nightcap"


def test_unknown_arc_id_returns_none() -> None:
    assert resolve_arc_path("unregistered-game") is None
    assert load_arc_definition("unregistered-game") is None


def test_default_arc_path_points_at_existing_definition() -> None:
    path = default_arc_path()
    assert path.exists()


def test_repeated_loads_return_cached_definition() -> None:
    first = load_arc_definition("nightcap-v1")
    second = load_arc_definition("nightcap")
    assert first is second
