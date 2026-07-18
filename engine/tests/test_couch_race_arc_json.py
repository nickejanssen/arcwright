"""AW-281 - validate the Couch Race arc JSON loads and shapes correctly."""

from __future__ import annotations

from pathlib import Path

from engine.arc.models import ArcDefinition, PlayMode
from engine.arc.registry import resolve_arc_path
from engine.safety.l3 import build_l3_policy_block, inject_l3_policy_block

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


def test_killer_knows_they_did_it() -> None:
    # Couch Race's killer is an AI character, not a player who receives a
    # dramatic mid-session revelation. The killer must know internally
    # from session start so it can compose consistent, knowledge-gated
    # misdirection during interrogation (story bible section 3, spec 0072
    # "AI composes suspect dialogue from resolved knowledge state").
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    assert arc.knowledge_rules.killer_knows_they_did_it is True


def test_registry_resolves_couch_race() -> None:
    path = resolve_arc_path("nightcap-couch-race-v1")
    assert path is not None
    assert path.resolve() == COUCH_RACE_PATH.resolve()


def test_registry_still_resolves_original_nightcap() -> None:
    path = resolve_arc_path("nightcap")
    assert path is not None
    assert path.name == "arc.json"


def test_content_rails_produce_a_nonempty_l3_policy_block() -> None:
    # Regression test: engine/safety/l3.py only falls back to the
    # platform-minimum policy when content_rails is None. A non-null
    # but empty ContentRailsConfig (empty prohibited_categories and
    # empty extra_prohibitions) silently produces NO policy text at
    # all, and inject_l3_policy_block returns the messages unmodified.
    # This proves the Couch Race arc's rails actually produce a rule
    # block, not just that the field is present.
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    policy_text = build_l3_policy_block(arc.content_rails)
    assert policy_text.strip(), (
        "Couch Race content_rails produced an empty L3 policy block; "
        "the arc's suspect-dialogue generation would run with zero "
        "in-prompt safety rules"
    )
    assert "graphic_violence" in policy_text
    assert "real_person_targeting" in policy_text


def test_content_rails_inherit_nightcap_prohibited_categories() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    rails = arc.content_rails
    assert "csam" in rails.prohibited_categories
    assert "graphic_violence" in rails.prohibited_categories
    assert "real_person_targeting" in rails.prohibited_categories
    assert rails.extra_prohibitions, "expected non-empty extra_prohibitions"


def test_content_rails_actually_get_injected_into_a_prompt() -> None:
    # End-to-end proof at the actual call site suspect-dialogue
    # generation uses: inject_l3_policy_block must change the message
    # list, not pass it through untouched.
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    original_messages = [{"role": "user", "content": "What did you see?"}]
    injected = inject_l3_policy_block(list(original_messages), arc.content_rails)
    assert injected != original_messages
    assert any(
        "graphic_violence" in str(m.get("content", ""))
        or "Do not" in str(m.get("content", ""))
        for m in injected
    )


def test_scene_beat_binds_crime_scene_smash() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    scene_beat = next(b for b in arc.beats if b.beat_id == "scene")
    assert len(scene_beat.mini_games) == 1
    binding = scene_beat.mini_games[0]
    assert binding.game_id == "crime-scene-smash"
    assert binding.version == "0.1.0"


def test_twist_beat_binds_evidence_locker() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    twist_beat = next(b for b in arc.beats if b.beat_id == "twist")
    assert len(twist_beat.mini_games) == 1
    binding = twist_beat.mini_games[0]
    assert binding.game_id == "evidence-locker-402"
    assert binding.version == "0.1.0"


def test_bound_mini_game_packages_exist_on_disk() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    mini_games_dir = REPO_ROOT / "nightcap" / "mini_games"
    for beat in arc.beats:
        for binding in beat.mini_games:
            package_dir = mini_games_dir / binding.game_id
            assert package_dir.is_dir(), (
                f"beat {beat.beat_id!r} binds game_id={binding.game_id!r} "
                f"but no package directory exists at {package_dir}"
            )
            definition_path = package_dir / "definitions" / f"{binding.version}.json"
            assert definition_path.is_file(), (
                f"beat {beat.beat_id!r} binds version={binding.version!r} "
                f"of {binding.game_id!r} but no definition file exists at "
                f"{definition_path}"
            )
