import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts import playtest_tool


def current_entry():
    return {
        "id": "nightcap-paper-test-02-v2.2",
        "game": "nightcap",
        "version": "2.2",
        "title": "Nightcap Paper Test #2 v2.2",
        "summary": "Representative test using non-canon The Last Toast.",
        "status": "current",
        "route": "/nightcap/paper-test-02/v2.2/",
        "source_dir": "playtests/nightcap-paper-test-02-v2.2",
        "instrument_id": "262397917027062",
        "instrument_version": "2.2",
        "published": "2026-08-28",
    }


def write_catalog(repo_root):
    playtests = repo_root / "playtests"
    playtests.mkdir(parents=True, exist_ok=True)
    current_source = playtests / "nightcap-paper-test-02-v2.2"
    current_source.mkdir()
    catalog = {
        "schema_version": 1,
        "generated_at_policy": "build-time",
        "current_tests": {"nightcap": "nightcap-paper-test-02-v2.2"},
        "entries": [current_entry()],
    }
    path = playtests / "catalog.json"
    path.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    return path


def test_new_can_register_existing_approved_fixture_as_unpublished_draft(tmp_path, capsys):
    catalog_path = write_catalog(tmp_path)
    source = tmp_path / "playtests" / "nightcap-paper-test-02-v3.0"
    source.mkdir()
    marker = source / "index.html"
    marker.write_text("approved fixture", encoding="utf-8")
    readme = source / "README.md"
    readme.write_text("approved research contract", encoding="utf-8")

    result = playtest_tool.main(
        [
            "--repo-root",
            str(tmp_path),
            "--json",
            "new",
            "--id",
            "nightcap-paper-test-02-v3.0",
            "--game",
            "nightcap",
            "--version",
            "3.0",
            "--title",
            "Nightcap Paper Test #2 v3.0",
            "--summary",
            "Non-canon research scaffold awaiting approved fixture content.",
            "--route",
            "/nightcap/paper-test-02/v3.0/",
            "--source-dir",
            "playtests/nightcap-paper-test-02-v3.0",
            "--instrument-id",
            "262397917027062",
            "--instrument-version",
            "3.0",
            "--use-existing-source",
        ]
    )
    captured = capsys.readouterr()

    assert result == 0, captured.out
    assert marker.read_text(encoding="utf-8") == "approved fixture"
    assert readme.read_text(encoding="utf-8") == "approved research contract"

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    assert catalog["current_tests"] == {"nightcap": "nightcap-paper-test-02-v2.2"}
    draft = next(item for item in catalog["entries"] if item["id"] == "nightcap-paper-test-02-v3.0")
    assert draft["status"] == "draft"
    assert draft["published"] is None
