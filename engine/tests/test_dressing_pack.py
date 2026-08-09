from __future__ import annotations

from pathlib import Path

import pytest

from engine.dressing import (
    DressingError,
    DressingPackNotAuthored,
    DressingRegistryError,
    UnknownWrapper,
    declared_wrapper_ids,
    load_dressing_pack,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ENGINE_DRESSING_ROOT = REPO_ROOT / "engine" / "dressing"


def test_declared_wrapper_ids_returns_all_six_for_registered_arc() -> None:
    assert declared_wrapper_ids("nightcap-couch-race-v1") == (
        "seance_1928",
        "big_top_1899",
        "orbital_gala_2087",
        "boardroom_severance",
        "manor_gothic",
        "sim_reunion",
    )


def test_load_dressing_pack_returns_authored_beverage_list() -> None:
    pack = load_dressing_pack("nightcap-couch-race-v1", "seance_1928")
    assert pack.wrapper_id == "seance_1928"
    assert pack.drinks == (
        "The Reliable Medium",
        "Cross My Palm With Gin",
        "Cold Reading",
        "The Spirit Cabinet",
        "The Bee's Sting",
        "One Rap for Yes",
        "The Planchette",
        "Second Sight, Second Pour",
    )


def test_load_dressing_pack_returns_big_top_stage_titles() -> None:
    pack = load_dressing_pack("nightcap-couch-race-v1", "big_top_1899")
    assert pack.drinks == (
        "Sawdust Lemonade",
        "The Ringmaster's Ration",
        "Fairy Floss Fizz",
        "The Calliope's Steam",
        "The Roustabout's Reward",
        "The Barker's Own Recipe",
        "Popcorn and Regret",
        "The Big Top Toast",
    )
    assert pack.stage_name_templates == (
        "The Astonishing Vespertine",
        "Madame Corvelle",
        "The Great Alaric",
        "Doctor Pellucid",
        "Constance the Uncanny",
        "Mademoiselle Query",
        "The Vanishing Duchess",
        "Baroness Vell",
        "The Melancholy Strongman",
        "The Lantern-Eyed Lark",
    )


def test_declared_but_unauthored_wrapper_raises_specific_error() -> None:
    with pytest.raises(DressingPackNotAuthored, match="orbital_gala_2087"):
        load_dressing_pack("nightcap-couch-race-v1", "orbital_gala_2087")


def test_unknown_wrapper_raises_distinct_error() -> None:
    with pytest.raises(UnknownWrapper, match="totally_unknown_wrapper"):
        load_dressing_pack("nightcap-couch-race-v1", "totally_unknown_wrapper")


def test_unregistered_arc_raises_registry_error() -> None:
    with pytest.raises(DressingRegistryError, match="no dressing registration"):
        declared_wrapper_ids("other-arc-v1")


def test_lookup_errors_share_base_without_subclassing_each_other() -> None:
    assert issubclass(DressingPackNotAuthored, DressingError)
    assert issubclass(UnknownWrapper, DressingError)
    assert not issubclass(DressingPackNotAuthored, UnknownWrapper)
    assert not issubclass(UnknownWrapper, DressingPackNotAuthored)


def test_engine_dressing_package_contains_no_arc_specific_terms() -> None:
    forbidden_terms = ("nightcap", "seance", "big_top")
    source_files = sorted(ENGINE_DRESSING_ROOT.glob("*.py"))
    assert source_files
    for path in source_files:
        text = path.read_text(encoding="utf-8").lower()
        for term in forbidden_terms:
            assert term not in text, f"{term!r} leaked into {path.name}"
