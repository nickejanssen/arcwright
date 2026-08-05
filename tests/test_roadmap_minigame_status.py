import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _status(path: str) -> str:
    content = (REPO_ROOT / path).read_text(encoding="utf-8")
    match = re.search(r"^\*\*Status:\*\* (.+)$", content, re.MULTILINE)
    assert match, f"missing status in {path}"
    return match.group(1).strip()


def test_minigame_roadmap_statuses_match_the_authoritative_hierarchy() -> None:
    index = json.loads(
        (REPO_ROOT / "docs/roadmap/index.json").read_text(encoding="utf-8")
    )
    epics = {item["id"]: item for item in index["epics"]}
    milestones = {item["id"]: item for item in index["milestones"]}

    assert (
        _status(
            "docs/roadmap/tasks/AW-287-nightcap-leverage-advantages-and-sabotages.md"
        )
        == "Complete"
    )
    assert (
        _status("docs/roadmap/tasks/AW-254-first-production-nightcap-mini-game.md")
        == "Superseded"
    )
    assert (
        _status("docs/roadmap/tasks/AW-285-couch-race-tv-and-phone-rendering.md")
        == "Complete — accepted Phase 1 structural scope"
    )
    assert (
        _status(
            "docs/roadmap/tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md"
        )
        == "Planned"
    )
    assert (
        _status(
            "docs/roadmap/tasks/AW-288-couch-race-mini-game-beat-coverage-and-tmst-acceleration.md"
        )
        == "Planned"
    )
    assert (
        _status("docs/roadmap/epics/M4-E-nightcap-mini-game-interaction-layer.md")
        == "Complete"
    )
    assert (
        _status("docs/roadmap/epics/M5-I-nightcap-couch-race-arc-and-interrogation.md")
        == "Active"
    )
    assert epics["M5-I"]["status"] == "active"
    assert set(f"AW-{number}" for number in range(287, 293)).issubset(
        epics["M5-I"]["tasks"]
    )
    assert milestones["M6"]["status"] == "planned"
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
