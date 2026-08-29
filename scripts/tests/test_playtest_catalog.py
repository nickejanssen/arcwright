import json

from scripts.playtest_catalog import current_tests, load_catalog, validate_catalog


def entry(**overrides):
    value = {
        "id": "nightcap-paper-test-02-v2.2",
        "game": "nightcap",
        "version": "2.2",
        "title": "Nightcap Paper Test #2 v2.2",
        "summary": "The Last Toast",
        "status": "current",
        "route": "/nightcap/paper-test-02/v2.2/",
        "source_dir": "playtests/nightcap-paper-test-02-v2.2",
        "instrument_id": "262397917027062",
        "instrument_version": "2.2",
        "published": "2026-08-28",
    }
    value.update(overrides)
    return value


def catalog(*entries_):
    return {
        "schema_version": 1,
        "generated_at_policy": "build-time",
        "current_tests": {"nightcap": entries_[0]["id"]} if entries_ else {},
        "entries": list(entries_),
    }


def test_valid_catalog_loads_and_exposes_current_test(tmp_path):
    (tmp_path / "playtests" / "nightcap-paper-test-02-v2.2").mkdir(parents=True)
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(catalog(entry())), encoding="utf-8")

    loaded = load_catalog(path)

    assert loaded["entries"][0]["id"] == entry()["id"]
    assert validate_catalog(loaded, tmp_path) == []
    assert current_tests(loaded) == [entry()]


def test_duplicate_ids_are_reported(tmp_path):
    result = validate_catalog(catalog(entry(), entry(route="/other/")), tmp_path)

    assert any("duplicate id" in error for error in result)


def test_missing_source_directory_is_reported(tmp_path):
    result = validate_catalog(catalog(entry(source_dir="playtests/missing")), tmp_path)

    assert any("source directory does not exist" in error for error in result)


def test_invalid_route_is_reported(tmp_path):
    result = validate_catalog(catalog(entry(route="/../private/")), tmp_path)

    assert any("unsafe route" in error for error in result)


def test_multiple_current_entries_for_game_are_reported(tmp_path):
    result = validate_catalog(
        catalog(entry(), entry(id="nightcap-second", route="/nightcap/second/")),
        tmp_path,
    )

    assert any(
        "more than one current entry for game 'nightcap'" in error for error in result
    )
