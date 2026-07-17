"""AW-281 — validate the Couch Race arc JSON loads and shapes correctly."""

from __future__ import annotations

from pathlib import Path

from engine.arc.models import ArcDefinition, PlayMode
from engine.arc.registry import resolve_arc_path

REPO_ROOT = Path(__file__).resolve().parents[2]
COUCH_RACE_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"


def test_arc_json_file_present() -> None:
    assert COUCH_RACE_PATH.exists(), "nightcap/couch-race.arc.json must exist"


def test_arc_definition_validates() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    assert arc.arc_id == "nightcap-couch-race-v1"
    assert arc.play_mode == PlayMode.detective_race
    assert arc.min_players == 2
    assert arc.max_players == 8


def test_beat_sequence() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    beat_ids = [b.beat_id for b in arc.beats]
    assert beat_ids == ["pour", "scene", "grill", "twist", "last_call", "truth"]


def test_beat_graph_linear() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    assert arc.beat_graph["pour"] == ["scene"]
    assert arc.beat_graph["scene"] == ["grill"]
    assert arc.beat_graph["grill"] == ["twist"]
    assert arc.beat_graph["twist"] == ["last_call"]
    assert arc.beat_graph["last_call"] == ["truth"]
    assert arc.beat_graph["truth"] == []


def test_pacing_weights_sum_to_one() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    pc = arc.pacing_config
    total = pc.w_time + pc.w_action + pc.w_suspicion + pc.w_coverage
    assert abs(total - 1.0) < 1e-6


def test_killer_assignment_disabled() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    assert arc.generative_elements.killer_assignment is False


def test_registry_resolves_couch_race() -> None:
    path = resolve_arc_path("nightcap-couch-race-v1")
    assert path is not None
    assert path.resolve() == COUCH_RACE_PATH.resolve()


def test_registry_still_resolves_original_nightcap() -> None:
    path = resolve_arc_path("nightcap")
    assert path is not None
    assert path.name == "arc.json"
