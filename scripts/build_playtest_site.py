"""Build the static Arcwright Playtest Lab Pages artifact."""

import argparse
import html
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.playtest_catalog import current_tests, load_catalog, validate_catalog

PAGES_BASE_PATH = "/arcwright/"


def _public_url(route: str) -> str:
    normalized = route.lstrip("/")
    return f"{PAGES_BASE_PATH}{normalized}"


def _route_output_path(route: str) -> PurePosixPath:
    return PurePosixPath(route.lstrip("/"))


def _legacy_alias_path(entry: dict[str, Any]) -> PurePosixPath:
    return PurePosixPath(PurePosixPath(entry["source_dir"]).name)


def _read_template(template_dir: Path, relative_path: str) -> str:
    return (template_dir / relative_path).read_text(encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _is_overlapping_path(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def _ensure_safe_output_dir(
    output_dir: Path,
    repo_root: Path,
    manifest_path: Path,
    template_dir: Path,
    catalog: dict[str, Any],
) -> None:
    resolved_output = output_dir.resolve()
    resolved_root = repo_root.resolve()
    if resolved_output == resolved_root or resolved_root not in resolved_output.parents:
        raise ValueError(f"refusing to clean output outside repo root: {output_dir}")

    protected_paths = {
        manifest_path.resolve(),
        manifest_path.parent.resolve(),
        template_dir.resolve(),
    }
    existing_top_level = set()
    for child in repo_root.iterdir():
        if child.is_dir():
            child_resolved = child.resolve()
            if child.name != "_site":
                existing_top_level.add(child_resolved)
            if child_resolved != resolved_output:
                protected_paths.add(child_resolved)
    for entry in catalog["entries"]:
        protected_paths.add((repo_root / Path(entry["source_dir"])).resolve())

    if resolved_output in existing_top_level:
        raise ValueError(
            f"refusing to clean output overlapping source tree: {output_dir}"
        )
    if any(
        _is_overlapping_path(resolved_output, protected)
        for protected in protected_paths
    ):
        raise ValueError(
            f"refusing to clean output overlapping source tree: {output_dir}"
        )


def _clean_output(output_dir: Path, repo_root: Path) -> None:
    resolved_output = output_dir.resolve()
    resolved_root = repo_root.resolve()
    if resolved_output == resolved_root or resolved_root not in resolved_output.parents:
        raise ValueError(f"refusing to clean output outside repo root: {output_dir}")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)


def _enrich_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    entries = []
    for entry in catalog["entries"]:
        route = entry["route"]
        entries.append(
            {
                **entry,
                "public_url": _public_url(route),
                "legacy_public_urls": [
                    _public_url(str(_legacy_alias_path(entry)) + "/")
                ],
                "output_path": str(_route_output_path(route)),
            }
        )
    return {
        **catalog,
        "generated_at": generated_at,
        "pages_base_path": PAGES_BASE_PATH,
        "entries": entries,
    }


def _catalog_items(entries: list[dict[str, Any]]) -> str:
    return "\n".join(
        (
            '<article class="test-card">'
            f'<div class="status">{html.escape(entry["status"])}</div>'
            f"<h2>{html.escape(entry['title'])}</h2>"
            f"<p>{html.escape(entry['summary'])}</p>"
            f'<a class="button" href="{html.escape(entry["public_url"], quote=True)}">'
            "Open test</a>"
            "</article>"
        )
        for entry in entries
    )


def _current_first(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        entry
        for _, entry in sorted(
            enumerate(entries),
            key=lambda item: (item[1]["status"] != "current", item[0]),
        )
    ]


def _render(template: str, replacements: dict[str, str]) -> str:
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def build_site(
    manifest_path: Path, template_dir: Path, output_dir: Path, repo_root: Path
) -> None:
    """Build the dependency-free static Pages site from the playtest catalog."""

    repo_root = repo_root.resolve()
    manifest_path = (
        manifest_path if manifest_path.is_absolute() else repo_root / manifest_path
    )
    template_dir = (
        template_dir if template_dir.is_absolute() else repo_root / template_dir
    )
    output_dir = output_dir if output_dir.is_absolute() else repo_root / output_dir
    catalog = load_catalog(manifest_path)
    problems = validate_catalog(catalog, repo_root)
    if problems:
        raise ValueError("\n".join(problems))

    _ensure_safe_output_dir(output_dir, repo_root, manifest_path, template_dir, catalog)
    enriched_catalog = _enrich_catalog(catalog)
    current = current_tests(enriched_catalog)
    current_by_game = {entry["game"]: entry for entry in current}
    nightcap_entries = [
        entry for entry in enriched_catalog["entries"] if entry["game"] == "nightcap"
    ]
    current_nightcap = current_by_game["nightcap"]
    catalog_json = json.dumps(enriched_catalog, indent=2, sort_keys=True)
    catalog_script = f'<script src="{PAGES_BASE_PATH}catalog.js"></script>'

    _clean_output(output_dir, repo_root)
    _write_text(output_dir / "styles.css", _read_template(template_dir, "styles.css"))
    _write_text(
        output_dir / "catalog.js",
        _read_template(template_dir, "catalog.js").replace(
            '"__ARCWRIGHT_CATALOG_JSON__"', json.dumps(catalog_json)
        ),
    )
    _write_text(
        output_dir / "index.html",
        _render(
            _read_template(template_dir, "index.html"),
            {
                "BASE_PATH": PAGES_BASE_PATH,
                "CATALOG_SCRIPT": catalog_script,
                "CURRENT_TEST_LINK": html.escape(
                    current_nightcap["public_url"], quote=True
                ),
                "CURRENT_TEST_TITLE": html.escape(current_nightcap["title"]),
                "CATALOG_ITEMS": _catalog_items(current),
                "GENERATED_AT": enriched_catalog["generated_at"],
            },
        ),
    )
    _write_text(
        output_dir / "nightcap" / "index.html",
        _render(
            _read_template(template_dir, "nightcap/index.html"),
            {
                "BASE_PATH": PAGES_BASE_PATH,
                "CATALOG_SCRIPT": catalog_script,
                "NIGHTCAP_TEST_LINK": html.escape(
                    current_nightcap["public_url"], quote=True
                ),
                "NIGHTCAP_TEST_TITLE": html.escape(current_nightcap["title"]),
                "CATALOG_ITEMS": _catalog_items(_current_first(nightcap_entries)),
                "GENERATED_AT": enriched_catalog["generated_at"],
            },
        ),
    )

    for entry in enriched_catalog["entries"]:
        source_dir = repo_root / Path(entry["source_dir"])
        destination = output_dir / Path(entry["output_path"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_dir, destination)
        legacy_destination = output_dir / Path(str(_legacy_alias_path(entry)))
        shutil.copytree(source_dir, legacy_destination)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Arcwright Playtest Lab Pages")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("playtests/catalog.json"),
    )
    parser.add_argument(
        "--templates",
        type=Path,
        default=Path("playtests/site"),
    )
    parser.add_argument("--output", type=Path, default=Path("_site"))
    args = parser.parse_args()
    repo_root = Path.cwd()
    build_site(args.manifest, args.templates, args.output, repo_root)
    print(f"Built playtest site at {args.output}")


if __name__ == "__main__":
    main()
