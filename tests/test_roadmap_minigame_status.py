import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_minigame_roadmap_scope_matches_the_authoritative_hierarchy() -> None:
    # Status is not asserted here: it lives on GitHub (D-109) and is reported by
    # scripts/roadmap_status.py. The markdown owns scope, which is what this checks.
    index = json.loads(
        (REPO_ROOT / "docs/roadmap/index.json").read_text(encoding="utf-8")
    )
    epics = {item["id"]: item for item in index["epics"]}
    assert set(f"AW-{number}" for number in range(287, 293)).issubset(
        epics["M5-I"]["tasks"]
    )
    superseded = (
        REPO_ROOT / "docs/roadmap/tasks/AW-254-first-production-nightcap-mini-game.md"
    ).read_text(encoding="utf-8")
    assert "**Scope note:** Superseded" in superseded
    tasks = {item["id"]: item for item in index["tasks"]}
    assert (
        tasks["AW-288"]["title"]
        == "Tell Me Something True Couch Race Activation, Placement, And Pacing"
    )
    assert (
        tasks["AW-289"]["title"] == "The Interrogation Room Last Call Pressure Capstone"
    )
    m5_i = (
        REPO_ROOT
        / "docs/roadmap/epics/M5-I-nightcap-couch-race-arc-and-interrogation.md"
    ).read_text(encoding="utf-8")
    assert "[AW-287: Nightcap Leverage Advantages And Sabotages]" in m5_i
    assert (
        "[AW-288: Tell Me Something True Couch Race Activation, Placement, And Pacing]"
        in m5_i
    )
    assert "[AW-289: The Interrogation Room Last Call Pressure Capstone]" in m5_i
    m6 = (
        REPO_ROOT / "docs/roadmap/milestones/M6-first-qualifying-sessions.md"
    ).read_text(encoding="utf-8")
    assert "six-beat" in m6
    assert "2–8 players" in m6
