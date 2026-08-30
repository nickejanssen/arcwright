import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts import playtest_tool


def entry(**overrides):
    value = {
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
    value.update(overrides)
    return value


def catalog(*entries):
    return {
        "schema_version": 1,
        "generated_at_policy": "build-time",
        "current_tests": {
            item["game"]: item["id"]
            for item in entries
            if item.get("status") == "current"
        },
        "entries": list(entries),
    }


def write_catalog(repo_root, value):
    (repo_root / "playtests").mkdir(parents=True, exist_ok=True)
    path = repo_root / "playtests" / "catalog.json"
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")
    return path


def write_templates(template_dir):
    template_dir.mkdir(parents=True)
    (template_dir / "nightcap").mkdir()
    (template_dir / "index.html").write_text(
        "{{CURRENT_TEST_LINK}}{{CATALOG_SCRIPT}}{{CATALOG_ITEMS}}",
        encoding="utf-8",
    )
    (template_dir / "nightcap" / "index.html").write_text(
        "{{NIGHTCAP_TEST_LINK}}{{CATALOG_SCRIPT}}{{CATALOG_ITEMS}}",
        encoding="utf-8",
    )
    (template_dir / "catalog.js").write_text(
        'window.ARCWRIGHT_PLAYTEST_CATALOG = JSON.parse("__ARCWRIGHT_CATALOG_JSON__");\n',
        encoding="utf-8",
    )
    (template_dir / "styles.css").write_text("", encoding="utf-8")


def run_cli(repo_root, *args, capsys):
    result = playtest_tool.main(["--repo-root", str(repo_root), *args])
    captured = capsys.readouterr()
    return result, captured


def test_list_json_is_read_only_and_reports_catalog_entries(tmp_path, capsys):
    (tmp_path / "playtests" / "nightcap-paper-test-02-v2.2").mkdir(parents=True)
    manifest = write_catalog(tmp_path, catalog(entry()))
    before = manifest.read_text(encoding="utf-8")

    result, captured = run_cli(tmp_path, "--json", "list", capsys=capsys)

    assert result == 0
    assert manifest.read_text(encoding="utf-8") == before
    payload = json.loads(captured.out)
    assert payload == {
        "ok": True,
        "entries": [
            {
                "id": "nightcap-paper-test-02-v2.2",
                "game": "nightcap",
                "version": "2.2",
                "status": "current",
                "route": "/nightcap/paper-test-02/v2.2/",
                "source_dir": "playtests/nightcap-paper-test-02-v2.2",
            }
        ],
    }


def test_validate_json_reports_invalid_catalog_without_mutating_it(tmp_path, capsys):
    manifest = write_catalog(
        tmp_path,
        catalog(
            entry(source_dir="playtests/missing"),
            entry(id="nightcap-copy", route="/nightcap/paper-test-02/v2.2/"),
        ),
    )
    before = manifest.read_text(encoding="utf-8")

    result, captured = run_cli(tmp_path, "--json", "validate", capsys=capsys)

    assert result == 2
    assert manifest.read_text(encoding="utf-8") == before
    payload = json.loads(captured.out)
    assert payload["ok"] is False
    assert any(
        "source directory does not exist" in error for error in payload["errors"]
    )
    assert any("duplicate route" in error for error in payload["errors"])


def test_new_creates_draft_scaffold_and_rejects_existing_version(tmp_path, capsys):
    write_catalog(tmp_path, catalog())

    args = [
        "--json",
        "new",
        "--id",
        "nightcap-paper-test-03-v1.0",
        "--game",
        "nightcap",
        "--version",
        "1.0",
        "--title",
        "Nightcap Paper Test #3 v1.0",
        "--summary",
        "Research scaffold awaiting approved fixture content.",
        "--route",
        "/nightcap/paper-test-03/v1.0/",
        "--source-dir",
        "playtests/nightcap-paper-test-03-v1.0",
        "--instrument-id",
        "research-instrument-03",
        "--instrument-version",
        "1.0",
        "--published",
        "2026-08-29",
    ]

    result, captured = run_cli(tmp_path, *args, capsys=capsys)

    assert result == 0
    payload = json.loads(captured.out)
    assert payload["entry"]["status"] == "draft"
    scaffold = tmp_path / "playtests" / "nightcap-paper-test-03-v1.0"
    assert (scaffold / "README.md").is_file()
    assert not (scaffold / "index.html").exists()
    manifest = json.loads(
        (tmp_path / "playtests" / "catalog.json").read_text(encoding="utf-8")
    )
    assert manifest["entries"][0]["id"] == "nightcap-paper-test-03-v1.0"

    duplicate_result, duplicate_capture = run_cli(tmp_path, *args, capsys=capsys)

    assert duplicate_result == 2
    assert "already exists" in duplicate_capture.out


def test_new_rejects_reused_game_version_before_creating_scaffold(tmp_path, capsys):
    (tmp_path / "playtests" / "nightcap-paper-test-02-v2.2").mkdir(parents=True)
    write_catalog(tmp_path, catalog(entry()))

    result, captured = run_cli(
        tmp_path,
        "--json",
        "new",
        "--id",
        "nightcap-paper-test-02-copy",
        "--game",
        "nightcap",
        "--version",
        "2.2",
        "--title",
        "Nightcap Paper Test #2 Copy",
        "--summary",
        "Research scaffold awaiting approved fixture content.",
        "--route",
        "/nightcap/paper-test-02/copy/",
        "--source-dir",
        "playtests/nightcap-paper-test-02-copy",
        "--instrument-id",
        "research-instrument-02-copy",
        "--instrument-version",
        "2.2",
        "--published",
        "2026-08-29",
        capsys=capsys,
    )

    assert result == 2
    assert "version already exists" in captured.out
    assert not (tmp_path / "playtests" / "nightcap-paper-test-02-copy").exists()


def test_new_rejects_secret_like_metadata_without_creating_files(tmp_path, capsys):
    write_catalog(tmp_path, catalog())

    result, captured = run_cli(
        tmp_path,
        "--json",
        "new",
        "--id",
        "nightcap-paper-test-03-v1.0",
        "--game",
        "nightcap",
        "--version",
        "1.0",
        "--title",
        "Nightcap Paper Test #3 v1.0",
        "--summary",
        "Do not store api_key=placeholder in metadata.",
        "--route",
        "/nightcap/paper-test-03/v1.0/",
        "--source-dir",
        "playtests/nightcap-paper-test-03-v1.0",
        "--instrument-id",
        "research-instrument-03",
        "--instrument-version",
        "1.0",
        "--published",
        "2026-08-29",
        capsys=capsys,
    )

    assert result == 2
    assert "secret-like value" in captured.out
    assert not (tmp_path / "playtests" / "nightcap-paper-test-03-v1.0").exists()


def test_new_rejects_creative_fixture_prose_without_creating_files(tmp_path, capsys):
    write_catalog(tmp_path, catalog())

    result, captured = run_cli(
        tmp_path,
        "--json",
        "new",
        "--id",
        "nightcap-paper-test-03-v1.0",
        "--game",
        "nightcap",
        "--version",
        "1.0",
        "--title",
        "Nightcap: The Last Toast Returns",
        "--summary",
        "Rhea whispers that the killer switched Sebastian's dose before the toast.",
        "--route",
        "/nightcap/paper-test-03/v1.0/",
        "--source-dir",
        "playtests/nightcap-paper-test-03-v1.0",
        "--instrument-id",
        "research-instrument-03",
        "--instrument-version",
        "1.0",
        "--published",
        "2026-08-29",
        capsys=capsys,
    )

    assert result == 2
    assert "creative content is not accepted by the Steward CLI" in captured.out
    assert not (tmp_path / "playtests" / "nightcap-paper-test-03-v1.0").exists()


def test_new_rejects_narrative_summary_with_neutral_title(tmp_path, capsys):
    write_catalog(tmp_path, catalog())

    result, captured = run_cli(
        tmp_path,
        "--json",
        "new",
        "--id",
        "nightcap-paper-test-03-v1.0",
        "--game",
        "nightcap",
        "--version",
        "1.0",
        "--title",
        "Nightcap Paper Test #3 v1.0",
        "--summary",
        "Sebastian Vale dies before the toast and Rhea knows why.",
        "--route",
        "/nightcap/paper-test-03/v1.0/",
        "--source-dir",
        "playtests/nightcap-paper-test-03-v1.0",
        "--instrument-id",
        "research-instrument-03",
        "--instrument-version",
        "1.0",
        "--published",
        "2026-08-29",
        capsys=capsys,
    )

    assert result == 2
    assert "creative content is not accepted by the Steward CLI" in captured.out
    assert not (tmp_path / "playtests" / "nightcap-paper-test-03-v1.0").exists()


def test_new_missing_required_metadata_returns_stable_invalid_exit(tmp_path, capsys):
    write_catalog(tmp_path, catalog())

    result, captured = run_cli(
        tmp_path,
        "--json",
        "new",
        "--id",
        "nightcap-paper-test-03-v1.0",
        capsys=capsys,
    )

    assert result == 2
    assert "required" in captured.out


def test_list_missing_catalog_returns_stable_operational_failure(tmp_path, capsys):
    result, captured = run_cli(tmp_path, "--json", "list", capsys=capsys)

    assert result == 1
    payload = json.loads(captured.out)
    assert payload["ok"] is False
    assert any("could not read catalog" in error for error in payload["errors"])


def test_archive_requires_exact_id_and_preserves_artifact_history(tmp_path, capsys):
    source_dir = tmp_path / "playtests" / "nightcap-paper-test-02-v2.2"
    source_dir.mkdir(parents=True)
    marker = source_dir / "index.html"
    marker.write_text("published artifact", encoding="utf-8")
    write_catalog(tmp_path, catalog(entry()))

    result, captured = run_cli(
        tmp_path,
        "--json",
        "archive",
        "nightcap-paper-test-02-v2.2",
        "--archived-on",
        "2026-08-29",
        "--reason",
        "Superseded by a later approved instrument.",
        capsys=capsys,
    )

    assert result == 0
    payload = json.loads(captured.out)
    assert payload["entry"]["status"] == "archived"
    assert marker.read_text(encoding="utf-8") == "published artifact"
    manifest = json.loads(
        (tmp_path / "playtests" / "catalog.json").read_text(encoding="utf-8")
    )
    assert manifest["current_tests"] == {}
    assert manifest["entries"][0]["archived"] == "2026-08-29"

    second_result, second_capture = run_cli(
        tmp_path,
        "--json",
        "archive",
        "nightcap-paper-test-02-v2.2",
        "--archived-on",
        "2026-08-30",
        capsys=capsys,
    )

    assert second_result == 2
    assert "already archived" in second_capture.out


def test_build_delegates_to_static_site_builder(tmp_path, capsys):
    source_dir = tmp_path / "playtests" / "nightcap-paper-test-02-v2.2"
    source_dir.mkdir(parents=True)
    (source_dir / "index.html").write_text("published artifact", encoding="utf-8")
    template_dir = tmp_path / "playtests" / "site"
    write_templates(template_dir)
    write_catalog(tmp_path, catalog(entry()))

    result, captured = run_cli(
        tmp_path,
        "--json",
        "build",
        "--output",
        "_site",
        capsys=capsys,
    )

    assert result == 0
    payload = json.loads(captured.out)
    assert payload["output"] == "_site"
    assert (
        tmp_path / "_site" / "nightcap" / "paper-test-02" / "v2.2" / "index.html"
    ).is_file()
