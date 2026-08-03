from pathlib import Path

import pytest

from engine.mini_games.authoring import MiniGameOnboardingService

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "browser_minigames" / "tmst-canary"


@pytest.fixture
def onboarding_service() -> MiniGameOnboardingService:
    return MiniGameOnboardingService()


@pytest.fixture
def tmst_browser_source() -> Path:
    return FIXTURE_ROOT


def test_tmst_canary_requires_one_destination_and_only_high_impact_questions(
    onboarding_service,
    tmst_browser_source,
):
    analysis = onboarding_service.analyze(
        source=tmst_browser_source,
        destination_game_id="nightcap-couch-race-v1",
    )
    assert analysis.recommended_path == "destination_first"
    assert analysis.destination_game_id == "nightcap-couch-race-v1"
    assert {item.key for item in analysis.confirmations} == {
        "story_affordance",
        "participation_model",
        "result_meaning",
        "placement_authority",
    }
