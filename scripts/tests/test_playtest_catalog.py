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


def test_drive_qualified_route_is_reported(tmp_path):
    result = validate_catalog(catalog(entry(route="C:/Windows")), tmp_path)

    assert any("unsafe route" in error for error in result)


def test_rooted_windows_route_is_reported(tmp_path):
    result = validate_catalog(catalog(entry(route="/C:/Windows")), tmp_path)

    assert any("unsafe route" in error for error in result)


def test_drive_qualified_source_directory_is_reported(tmp_path):
    result = validate_catalog(catalog(entry(source_dir="C:/Windows")), tmp_path)

    assert any("unsafe source_dir" in error for error in result)


def test_rooted_windows_source_directory_is_reported(tmp_path):
    result = validate_catalog(catalog(entry(source_dir="/C:/Windows")), tmp_path)

    assert any("unsafe source_dir" in error for error in result)


def test_multiple_current_entries_for_game_are_reported(tmp_path):
    result = validate_catalog(
        catalog(entry(), entry(id="nightcap-second", route="/nightcap/second/")),
        tmp_path,
    )

    assert any(
        "more than one current entry for game 'nightcap'" in error for error in result
    )


def test_missing_current_tests_reference_is_reported(tmp_path):
    value = catalog(entry())
    del value["current_tests"]

    result = validate_catalog(value, tmp_path)

    assert any("current_tests must be an object" in error for error in result)


def test_unknown_current_tests_reference_is_reported(tmp_path):
    value = catalog(entry())
    value["current_tests"] = {"nightcap": "missing"}

    result = validate_catalog(value, tmp_path)

    assert any(
        "current_tests['nightcap'] references unknown id 'missing'" in error
        for error in result
    )


def test_mismatched_current_tests_reference_is_reported(tmp_path):
    value = catalog(entry())
    value["entries"][0]["status"] = "archived"

    result = validate_catalog(value, tmp_path)

    assert any("must reference a current entry" in error for error in result)


def test_current_tests_resolves_declared_references():
    first = entry()
    second = entry(id="other", game="other", route="/other/", status="current")
    value = catalog(first, second)
    value["current_tests"] = {"other": "other", "nightcap": first["id"]}

    assert current_tests(value) == [second, first]


def test_non_object_catalog_returns_actionable_error(tmp_path):
    assert validate_catalog([], tmp_path) == ["catalog root must be a JSON object"]
    assert validate_catalog("catalog", tmp_path) == [
        "catalog root must be a JSON object"
    ]


def test_symlink_escaping_source_directory_is_reported(tmp_path):
    external_root = tmp_path.parent / "external-playtest-source"
    external_root.mkdir()
    escaped = external_root / "nightcap-paper-test-02-v2.2"
    escaped.mkdir()
    linked = tmp_path / "playtests" / "nightcap-paper-test-02-v2.2"
    linked.parent.mkdir(parents=True, exist_ok=True)
    try:
        linked.symlink_to(escaped, target_is_directory=True)
    except (OSError, NotImplementedError):
        return

    result = validate_catalog(catalog(entry()), tmp_path)

    assert any("unsafe source_dir" in error for error in result)


def test_route_cannot_collide_with_legacy_alias_path(tmp_path):
    source = tmp_path / "playtests" / "nightcap-paper-test-02-v2.2"
    source.mkdir(parents=True)

    result = validate_catalog(
        catalog(
            entry(
                route="/nightcap-paper-test-02-v2.2/",
                source_dir="playtests/nightcap-paper-test-02-v2.2",
            )
        ),
        tmp_path,
    )

    assert any("overlaps" in error and "legacy alias" in error for error in result)


def test_route_cannot_collide_with_another_entry_legacy_alias(tmp_path):
    (tmp_path / "playtests" / "nightcap-paper-test-02-v2.2").mkdir(parents=True)
    (tmp_path / "playtests" / "other-test").mkdir(parents=True)

    result = validate_catalog(
        catalog(
            entry(),
            entry(
                id="other",
                route="/nightcap-paper-test-02-v2.2/",
                source_dir="playtests/other-test",
                status="archived",
            ),
        ),
        tmp_path,
    )

    assert any("overlaps" in error for error in result)
