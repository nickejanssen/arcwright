import json

from scripts.build_playtest_site import build_site


def _write_fixture(path):
    path.mkdir(parents=True)
    (path / "index.html").write_text("<!doctype html><title>Fixture</title>", encoding="utf-8")


def _entry(version, status):
    fixture_id = f"nightcap-paper-test-02-v{version}"
    return {
        "id": fixture_id,
        "game": "nightcap",
        "version": version,
        "title": f"Nightcap Paper Test #2 v{version}",
        "summary": f"Fixture {version}",
        "status": status,
        "route": f"/nightcap/paper-test-02/v{version}/",
        "source_dir": f"playtests/{fixture_id}",
        "instrument_id": "262397917027062",
        "instrument_version": "2.2",
        "published": "2026-08-28",
    }


def test_playtest_lab_home_lists_current_and_archived_playable_builds(tmp_path):
    repo_root = tmp_path / "repo"
    template_dir = repo_root / "playtests" / "site"
    output_dir = repo_root / "_site"
    manifest = repo_root / "playtests" / "catalog.json"

    _write_fixture(repo_root / "playtests" / "nightcap-paper-test-02-v2.2")
    _write_fixture(repo_root / "playtests" / "nightcap-paper-test-02-v3.0")
    (template_dir / "nightcap").mkdir(parents=True)
    (template_dir / "index.html").write_text("{{CATALOG_ITEMS}}", encoding="utf-8")
    (template_dir / "nightcap" / "index.html").write_text("{{CATALOG_ITEMS}}", encoding="utf-8")
    (template_dir / "catalog.js").write_text(
        'window.ARCWRIGHT_PLAYTEST_CATALOG = JSON.parse("__ARCWRIGHT_CATALOG_JSON__");\n',
        encoding="utf-8",
    )
    (template_dir / "styles.css").write_text("", encoding="utf-8")
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_at_policy": "build-time",
                "current_tests": {"nightcap": "nightcap-paper-test-02-v3.0"},
                "entries": [_entry("2.2", "archived"), _entry("3.0", "current")],
            }
        ),
        encoding="utf-8",
    )

    build_site(manifest, template_dir, output_dir, repo_root)

    home = (output_dir / "index.html").read_text(encoding="utf-8")
    assert "Nightcap Paper Test #2 v3.0" in home
    assert "Nightcap Paper Test #2 v2.2" in home
    assert home.index("Nightcap Paper Test #2 v3.0") < home.index("Nightcap Paper Test #2 v2.2")
