from __future__ import annotations

from pathlib import Path

from engine.arc.models import ArcDefinition
from engine.dressing import load_dressing_pack

REPO_ROOT = Path(__file__).resolve().parents[2]
COUCH_RACE_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"


def test_couch_race_arc_declares_wrapper_host_selection() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text(encoding="utf-8"))

    wrapper_option = arc.aesthetic_config.selection_model["wrapper"]

    assert wrapper_option.type == "host_select"
    assert wrapper_option.allow_random is True


def test_seance_wrapper_selection_loads_wrapper_id_and_drinks() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text(encoding="utf-8"))

    pack = load_dressing_pack(arc.arc_id, "seance_1928")

    assert pack.wrapper_id == "seance_1928"
    assert pack.option_lists["beverages"]
