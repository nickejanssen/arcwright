import json

from scripts.build_playtest_site import build_site


def write_template(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_fixture(path):
    path.mkdir(parents=True)
    (path / "index.html").write_text(
        '<!doctype html><title>Fixture</title><script type="module" src="app.js"></script>',
        encoding="utf-8",
    )
    (path / "app.js").write_text(
        "const revealUrl='?reveal=1';"
        "if(new URLSearchParams(window.location.search).get('reveal')==='1')reveal();",
        encoding="utf-8",
    )
    (path / "config.js").write_text(
        "window.NIGHTCAP_PLAYTEST={fixtureStatus:'NON-CANON TEST FIXTURE'};",
        encoding="utf-8",
    )


def read_generated_catalog(catalog_js):
    prefix = "window.ARCWRIGHT_PLAYTEST_CATALOG = JSON.parse("
    suffix = ");\n"
    assert catalog_js.startswith(prefix)
    assert catalog_js.endswith(suffix)
    return json.loads(json.loads(catalog_js[len(prefix) : -len(suffix)]))


def test_build_site_emits_pages_catalog_and_fixture_under_pages_base(tmp_path):
    repo_root = tmp_path / "repo"
    template_dir = repo_root / "playtests" / "site"
    output_dir = repo_root / "_site"
    fixture_dir = repo_root / "playtests" / "nightcap-paper-test-02-v2.2"
    manifest_path = repo_root / "playtests" / "catalog.json"
    write_fixture(fixture_dir)
    write_template(
        template_dir / "index.html",
        '<html><head><link rel="stylesheet" href="{{BASE_PATH}}styles.css"></head>'
        "<body>{{CURRENT_TEST_LINK}}{{CATALOG_SCRIPT}}</body></html>",
    )
    write_template(
        template_dir / "nightcap" / "index.html",
        '<html><head><link rel="stylesheet" href="{{BASE_PATH}}styles.css"></head>'
        "<body>{{NIGHTCAP_TEST_LINK}}{{CATALOG_SCRIPT}}</body></html>",
    )
    write_template(
        template_dir / "catalog.js",
        'window.ARCWRIGHT_PLAYTEST_CATALOG = JSON.parse("__ARCWRIGHT_CATALOG_JSON__");\n',
    )
    write_template(template_dir / "styles.css", "body{font-family:system-ui}")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_at_policy": "build-time",
                "current_tests": {"nightcap": "nightcap-paper-test-02-v2.2"},
                "entries": [
                    {
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
                ],
            }
        ),
        encoding="utf-8",
    )

    build_site(manifest_path, template_dir, output_dir, repo_root)

    home = (output_dir / "index.html").read_text(encoding="utf-8")
    nightcap = (output_dir / "nightcap" / "index.html").read_text(encoding="utf-8")
    catalog_js = (output_dir / "catalog.js").read_text(encoding="utf-8")

    assert "/arcwright/nightcap/paper-test-02/v2.2/" in home
    assert "/arcwright/nightcap/paper-test-02/v2.2/" in nightcap
    assert "/arcwright/styles.css" in home
    assert "/arcwright/catalog.js" in nightcap
    catalog = read_generated_catalog(catalog_js)
    assert catalog["entries"][0]["id"] == "nightcap-paper-test-02-v2.2"
    assert (
        catalog["entries"][0]["public_url"] == "/arcwright/nightcap/paper-test-02/v2.2/"
    )
    assert (output_dir / "styles.css").read_text(
        encoding="utf-8"
    ) == "body{font-family:system-ui}"
    assert (output_dir / "nightcap" / "paper-test-02" / "v2.2" / "index.html").is_file()
    copied_app = output_dir / "nightcap" / "paper-test-02" / "v2.2" / "app.js"
    copied_config = output_dir / "nightcap" / "paper-test-02" / "v2.2" / "config.js"
    assert "?reveal" in copied_app.read_text(encoding="utf-8")
    assert "NON-CANON TEST FIXTURE" in copied_config.read_text(encoding="utf-8")
