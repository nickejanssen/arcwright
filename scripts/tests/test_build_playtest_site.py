import json

from scripts.build_playtest_site import build_site


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
        "current_tests": {"nightcap": "nightcap-paper-test-02-v2.2"},
        "entries": list(entries),
    }


def write_template(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_catalog(manifest_path, value):
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(value, indent=2), encoding="utf-8")


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
    assert catalog["entries"][0]["legacy_public_urls"] == [
        "/arcwright/nightcap-paper-test-02-v2.2/"
    ]
    assert (output_dir / "styles.css").read_text(
        encoding="utf-8"
    ) == "body{font-family:system-ui}"
    assert (output_dir / "nightcap" / "paper-test-02" / "v2.2" / "index.html").is_file()
    assert (output_dir / "nightcap-paper-test-02-v2.2" / "index.html").is_file()
    copied_app = output_dir / "nightcap" / "paper-test-02" / "v2.2" / "app.js"
    copied_config = output_dir / "nightcap" / "paper-test-02" / "v2.2" / "config.js"
    assert "?reveal" in copied_app.read_text(encoding="utf-8")
    assert "NON-CANON TEST FIXTURE" in copied_config.read_text(encoding="utf-8")


def test_build_site_refuses_output_paths_that_overlap_repo_sources(tmp_path):
    repo_root = tmp_path / "repo"
    template_dir = repo_root / "playtests" / "site"
    fixture_dir = repo_root / "playtests" / "nightcap-paper-test-02-v2.2"
    manifest_path = repo_root / "playtests" / "catalog.json"
    write_fixture(fixture_dir)
    write_template(template_dir / "index.html", "{{CATALOG_ITEMS}}")
    write_template(template_dir / "nightcap" / "index.html", "{{CATALOG_ITEMS}}")
    write_template(
        template_dir / "catalog.js",
        'window.ARCWRIGHT_PLAYTEST_CATALOG = JSON.parse("__ARCWRIGHT_CATALOG_JSON__");\n',
    )
    write_template(template_dir / "styles.css", "")
    write_catalog(
        manifest_path,
        catalog(
            entry(),
        ),
    )
    playtests_marker = repo_root / "playtests" / "marker.txt"
    docs_marker = repo_root / "docs" / "marker.txt"
    playtests_marker.parent.mkdir(parents=True, exist_ok=True)
    docs_marker.parent.mkdir(parents=True, exist_ok=True)
    playtests_marker.write_text("keep", encoding="utf-8")
    docs_marker.write_text("keep", encoding="utf-8")

    for blocked_output in (repo_root / "playtests", repo_root / "docs"):
        try:
            build_site(manifest_path, template_dir, blocked_output, repo_root)
        except ValueError as exc:
            assert "refusing to clean output" in str(exc)
        else:
            raise AssertionError("expected build_site to refuse overlapping output")

    assert playtests_marker.read_text(encoding="utf-8") == "keep"
    assert docs_marker.read_text(encoding="utf-8") == "keep"


def test_nightcap_catalog_renders_current_entries_before_archived_entries(tmp_path):
    repo_root = tmp_path / "repo"
    template_dir = repo_root / "playtests" / "site"
    output_dir = repo_root / "_site"
    manifest_path = repo_root / "playtests" / "catalog.json"
    write_fixture(repo_root / "playtests" / "nightcap-paper-test-02-v2.1")
    write_fixture(repo_root / "playtests" / "nightcap-paper-test-02-v2.2")
    write_template(template_dir / "index.html", "{{CATALOG_ITEMS}}")
    write_template(template_dir / "nightcap" / "index.html", "{{CATALOG_ITEMS}}")
    write_template(
        template_dir / "catalog.js",
        'window.ARCWRIGHT_PLAYTEST_CATALOG = JSON.parse("__ARCWRIGHT_CATALOG_JSON__");\n',
    )
    write_template(template_dir / "styles.css", "")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            catalog(
                entry(
                    id="nightcap-paper-test-02-v2.1",
                    version="2.1",
                    title="Nightcap Paper Test #2 v2.1",
                    status="archived",
                    route="/nightcap/paper-test-02/v2.1/",
                    source_dir="playtests/nightcap-paper-test-02-v2.1",
                    instrument_version="2.1",
                    published="2026-08-20",
                ),
                entry(),
            )
        ),
        encoding="utf-8",
    )

    build_site(manifest_path, template_dir, output_dir, repo_root)

    nightcap = (output_dir / "nightcap" / "index.html").read_text(encoding="utf-8")

    assert nightcap.index("Nightcap Paper Test #2 v2.2") < nightcap.index(
        "Nightcap Paper Test #2 v2.1"
    )


def test_generated_pages_escape_catalog_text_and_route_attributes(tmp_path):
    repo_root = tmp_path / "repo"
    template_dir = repo_root / "playtests" / "site"
    output_dir = repo_root / "_site"
    fixture_dir = repo_root / "playtests" / "nightcap-paper-test-02-v2.2"
    manifest_path = repo_root / "playtests" / "catalog.json"
    write_fixture(fixture_dir)
    write_template(
        template_dir / "index.html",
        "<html><body>{{CATALOG_ITEMS}}{{CURRENT_TEST_LINK}}{{CATALOG_SCRIPT}}</body></html>",
    )
    write_template(
        template_dir / "nightcap" / "index.html",
        "<html><body>{{CATALOG_ITEMS}}{{NIGHTCAP_TEST_LINK}}{{CATALOG_SCRIPT}}</body></html>",
    )
    write_template(
        template_dir / "catalog.js",
        'window.ARCWRIGHT_PLAYTEST_CATALOG = JSON.parse("__ARCWRIGHT_CATALOG_JSON__");\n',
    )
    write_template(template_dir / "styles.css", "")
    write_catalog(
        manifest_path,
        catalog(
            entry(
                title='Nightcap <script>alert("x")</script> Paper Test',
                summary='Summary with <img src=x onerror="alert(1)"> markup.',
                route="/nightcap/paper-test-02/v2.2/foo&bar's/",
                source_dir="playtests/nightcap-paper-test-02-v2.2",
            ),
        ),
    )

    build_site(manifest_path, template_dir, output_dir, repo_root)

    home = (output_dir / "index.html").read_text(encoding="utf-8")
    nightcap = (output_dir / "nightcap" / "index.html").read_text(encoding="utf-8")

    assert '<script>alert("x")</script>' not in home
    assert '<img src=x onerror="alert(1)">' not in nightcap
    assert "foo&bar's" not in home
    assert "foo&amp;bar&#x27;s" in home
    assert "foo&amp;bar&#x27;s" in nightcap
