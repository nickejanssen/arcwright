"""Load case skeletons, taxonomies, and resolution config from disk.

Kept arc-agnostic: the loader takes directory paths as arguments and
reads whatever JSON it finds; it does not know about ``nightcap`` or
any specific arc.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from engine.case.errors import CaseResolutionError
from engine.case.models import CaseSkeleton


class Taxonomy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    motive_families: list[dict[str, Any]] = Field(default_factory=list)
    method_families: list[dict[str, Any]] = Field(default_factory=list)
    evidence_types: list[dict[str, Any]] = Field(default_factory=list)
    lie_topics: list[dict[str, Any]] = Field(default_factory=list)


class CaseResolutionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    arc_id_prefix: str
    skeleton_directory: str
    taxonomy_directory: str
    cast_size_by_player_count: dict[str, int]


def load_skeletons(directory: Path) -> dict[str, CaseSkeleton]:
    if not directory.exists():
        raise CaseResolutionError(f"skeleton directory missing: {directory}")
    result: dict[str, CaseSkeleton] = {}
    for path in sorted(directory.glob("*.json")):
        skel = CaseSkeleton.model_validate_json(path.read_text("utf-8"))
        if skel.skeleton_id in result:
            raise CaseResolutionError(
                f"duplicate skeleton_id {skel.skeleton_id!r} in {directory}"
            )
        result[skel.skeleton_id] = skel
    if not result:
        raise CaseResolutionError(f"no skeletons found in {directory}")
    return result


def load_taxonomy(directory: Path) -> Taxonomy:
    if not directory.exists():
        raise CaseResolutionError(f"taxonomy directory missing: {directory}")

    def _load(name: str, key: str) -> list[dict[str, Any]]:
        path = directory / name
        if not path.exists():
            raise CaseResolutionError(f"taxonomy file missing: {path}")
        data = json.loads(path.read_text("utf-8"))
        if key not in data:
            raise CaseResolutionError(
                f"taxonomy file {path} missing expected top-level key {key!r}"
            )
        return list(data[key])

    return Taxonomy(
        motive_families=_load("motive_families.json", "families"),
        method_families=_load("method_families.json", "families"),
        evidence_types=_load("evidence_types.json", "types"),
        lie_topics=_load("lie_topics.json", "topics"),
    )


def load_case_resolution_config(
    config_path: Path,
) -> CaseResolutionConfig:
    if not config_path.exists():
        raise CaseResolutionError(f"case-resolution config missing: {config_path}")
    return CaseResolutionConfig.model_validate_json(config_path.read_text("utf-8"))
