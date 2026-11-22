"""AW-347: what each audience may read of a mini-game run's saved state.

A mechanic declares which keys of its saved state are public and which are
per-player. The engine copies out only what the viewer may see, and sends
nothing when the rule is missing or anything is malformed.
"""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from engine.mini_games.audience_view import (
    Audience,
    AudienceRule,
    Viewer,
    build_run_view,
)
from engine.mini_games.plugins import default_registry
from engine.mini_games.runtime import MechanicRegistry

CHAR_A = "11111111-1111-1111-1111-111111111111"
CHAR_B = "22222222-2222-2222-2222-222222222222"
MARKER_A = "marker-for-player-a"
MARKER_B = "marker-for-player-b"


class _RuledMechanic:
    mechanic_type = "test-ruled"
    audience_rule = AudienceRule(
        public_state=("step",),
        own_state=("notes",),
        public_presentation=("title",),
    )


class _UnruledMechanic:
    mechanic_type = "test-unruled"


def _registry() -> MechanicRegistry:
    return MechanicRegistry([_RuledMechanic(), _UnruledMechanic()])  # type: ignore[list-item]


def _run(
    mechanic_type: str = "test-ruled",
    state: Any = None,
    presentation: dict[str, Any] | None = None,
) -> Any:
    if state is None:
        state = {
            "step": "input",
            "notes": {CHAR_A: MARKER_A, CHAR_B: MARKER_B},
            "hidden": "never-sent",
        }
    return SimpleNamespace(
        definition_snapshot={
            "mechanic_type": mechanic_type,
            "presentation": presentation
            if presentation is not None
            else {"title": "A title", "secret_prompt": "only for phones"},
        },
        clue_unlock_record={"runtime_state": state},
    )


def test_shared_display_gets_public_keys_only() -> None:
    view = build_run_view(_registry(), _run(), Viewer(Audience.shared_display))
    assert view.runtime_state == {"step": "input"}
    assert MARKER_A not in str(view) and MARKER_B not in str(view)


def test_host_gets_public_keys_only() -> None:
    view = build_run_view(_registry(), _run(), Viewer(Audience.host))
    assert view.runtime_state == {"step": "input"}
    assert MARKER_A not in str(view) and MARKER_B not in str(view)


def test_player_gets_public_keys_and_only_their_own_entry() -> None:
    view_a = build_run_view(_registry(), _run(), Viewer(Audience.player, CHAR_A))
    view_b = build_run_view(_registry(), _run(), Viewer(Audience.player, CHAR_B))
    assert view_a.runtime_state == {"step": "input", "notes": {CHAR_A: MARKER_A}}
    assert view_b.runtime_state == {"step": "input", "notes": {CHAR_B: MARKER_B}}
    assert MARKER_B not in str(view_a)
    assert MARKER_A not in str(view_b)


def test_keys_the_rule_does_not_name_are_never_sent() -> None:
    view = build_run_view(_registry(), _run(), Viewer(Audience.player, CHAR_A))
    assert "hidden" not in view.runtime_state


def test_player_whose_entry_is_missing_gets_no_notes_key() -> None:
    state = {"step": "input", "notes": {CHAR_B: MARKER_B}}
    view = build_run_view(
        _registry(), _run(state=state), Viewer(Audience.player, CHAR_A)
    )
    assert view.runtime_state == {"step": "input"}


def test_presentation_keys_not_named_public_go_to_players_only() -> None:
    player = build_run_view(_registry(), _run(), Viewer(Audience.player, CHAR_A))
    tv = build_run_view(_registry(), _run(), Viewer(Audience.shared_display))
    host = build_run_view(_registry(), _run(), Viewer(Audience.host))
    assert player.presentation == {
        "title": "A title",
        "secret_prompt": "only for phones",
    }
    assert tv.presentation == {"title": "A title"}
    assert host.presentation == {"title": "A title"}


def test_presentation_keys_the_rule_does_not_name_never_reach_tv_or_host() -> None:
    run = _run(
        presentation={
            "title": "A title",
            "added_later_by_a_generator": "UNLISTED-VALUE",
        }
    )
    for viewer in (Viewer(Audience.shared_display), Viewer(Audience.host)):
        view = build_run_view(_registry(), run, viewer)
        assert view.presentation == {"title": "A title"}
        assert "UNLISTED-VALUE" not in str(view)
    player = build_run_view(_registry(), run, Viewer(Audience.player, CHAR_A))
    assert player.presentation["added_later_by_a_generator"] == "UNLISTED-VALUE"


def test_unknown_mechanic_sends_nothing() -> None:
    view = build_run_view(
        _registry(), _run(mechanic_type="no-such"), Viewer(Audience.player, CHAR_A)
    )
    assert view.runtime_state == {}
    assert view.presentation == {}


def test_mechanic_without_a_rule_sends_no_state() -> None:
    view = build_run_view(
        _registry(), _run(mechanic_type="test-unruled"), Viewer(Audience.player, CHAR_A)
    )
    assert view.runtime_state == {}
    assert view.presentation == {"title": "A title", "secret_prompt": "only for phones"}


def test_mechanic_without_a_rule_sends_the_shared_display_no_presentation() -> None:
    view = build_run_view(
        _registry(), _run(mechanic_type="test-unruled"), Viewer(Audience.shared_display)
    )
    assert view.runtime_state == {}
    assert view.presentation == {}
    assert "only for phones" not in str(view)


def test_mechanic_without_a_rule_sends_the_host_no_presentation() -> None:
    view = build_run_view(
        _registry(), _run(mechanic_type="test-unruled"), Viewer(Audience.host)
    )
    assert view.runtime_state == {}
    assert view.presentation == {}


def test_seated_player_of_a_mechanic_without_a_rule_keeps_the_whole_presentation() -> (
    None
):
    view = build_run_view(
        _registry(), _run(mechanic_type="test-unruled"), Viewer(Audience.player, CHAR_B)
    )
    assert view.presentation == {"title": "A title", "secret_prompt": "only for phones"}


def test_player_without_a_seat_of_a_mechanic_without_a_rule_gets_nothing() -> None:
    view = build_run_view(
        _registry(), _run(mechanic_type="test-unruled"), Viewer(Audience.player, None)
    )
    assert view.presentation == {}


def test_every_registered_mechanic_without_a_rule_keeps_presentation_off_the_tv() -> (
    None
):
    registry = default_registry()
    unruled = [
        mechanic_type
        for mechanic_type, plugin in registry._registry.items()
        if not isinstance(getattr(plugin, "audience_rule", None), AudienceRule)
    ]
    assert unruled, "expected at least one registered mechanic without a rule"
    for mechanic_type in unruled:
        run = _run(
            mechanic_type=mechanic_type,
            presentation={"title": "T", "phone_only": "PHONE-ONLY"},
        )
        for viewer in (Viewer(Audience.shared_display), Viewer(Audience.host)):
            view = build_run_view(registry, run, viewer)
            assert view.presentation == {}, mechanic_type
            assert "PHONE-ONLY" not in str(view), mechanic_type


def test_own_state_that_is_not_a_map_is_dropped() -> None:
    state = {"step": "input", "notes": [MARKER_A, MARKER_B]}
    view = build_run_view(
        _registry(), _run(state=state), Viewer(Audience.player, CHAR_A)
    )
    assert view.runtime_state == {"step": "input"}
    assert MARKER_A not in str(view) and MARKER_B not in str(view)


def test_player_without_a_character_id_is_treated_as_the_shared_display() -> None:
    view = build_run_view(_registry(), _run(), Viewer(Audience.player, None))
    assert view.runtime_state == {"step": "input"}
    assert view.presentation == {"title": "A title"}


@pytest.mark.parametrize("state", [None, "text", ["a"], 7])
def test_malformed_saved_state_sends_empty_state(state: Any) -> None:
    run = _run()
    run.clue_unlock_record = {"runtime_state": state}
    view = build_run_view(_registry(), run, Viewer(Audience.player, CHAR_A))
    assert view.runtime_state == {}


def test_missing_snapshot_pieces_send_nothing() -> None:
    run = SimpleNamespace(definition_snapshot=None, clue_unlock_record=None)
    view = build_run_view(_registry(), run, Viewer(Audience.player, CHAR_A))
    assert view.runtime_state == {}
    assert view.presentation == {}


def test_returned_objects_are_copies() -> None:
    run = _run()
    view = build_run_view(_registry(), run, Viewer(Audience.player, CHAR_A))
    view.runtime_state["step"] = "changed"
    view.runtime_state["notes"][CHAR_A] = "changed"
    view.presentation["title"] = "changed"
    assert run.clue_unlock_record["runtime_state"]["step"] == "input"
    assert run.clue_unlock_record["runtime_state"]["notes"][CHAR_A] == MARKER_A
    assert run.definition_snapshot["presentation"]["title"] == "A title"


def test_tell_me_something_true_declares_a_rule_that_keeps_its_prompt_off_the_tv() -> (
    None
):
    run = _run(
        mechanic_type="social-truth-bluff",
        state={
            "phase": "spotlight",
            "presence": {CHAR_A: True},
            "input_closed": True,
            "current_spotlight_index": 1,
            "spotlight_order": [CHAR_A, CHAR_B],
        },
        presentation={
            "title": "A title",
            "true_label": "Truth",
            "lie_label": "Lie",
            "prompt": "phone-only prompt",
            "added_later": "not declared",
        },
    )
    tv = build_run_view(default_registry(), run, Viewer(Audience.shared_display))
    player = build_run_view(default_registry(), run, Viewer(Audience.player, CHAR_A))
    assert tv.runtime_state == {
        "phase": "spotlight",
        "input_closed": True,
        "current_spotlight_index": 1,
    }
    assert tv.presentation == {
        "title": "A title",
        "true_label": "Truth",
        "lie_label": "Lie",
    }
    assert player.presentation["prompt"] == "phone-only prompt"


def test_router_gains_no_new_game_named_function() -> None:
    """Criterion 4: the shared path stays generic. Only today's three stay."""
    source = (
        Path(__file__).resolve().parents[2] / "api" / "routers" / "mini_games.py"
    ).read_text(encoding="utf-8")
    names = re.findall(r"^(?:async )?def (\w+)", source, flags=re.MULTILINE)
    game_named = {n for n in names if re.search(r"tmst|scene_sweep|truth|sweep", n)}
    allowed = {
        "_tmst_runtime_state",
        "_tmst_presence_map",
        "_tmst_current_target",
        "_tmst_has_submitted_input",
        "_tmst_has_submitted_vote",
        "_build_tmst_phase_state",
        "_scene_sweep_runtime_state",
        "_build_scene_sweep_phase_state",
        "_validate_tmst_submission_payload",
        "_ensure_tmst_phase_accepts_action",
    }
    assert game_named <= allowed, sorted(game_named - allowed)
