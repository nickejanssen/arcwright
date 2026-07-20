"""Tests for the authored interaction topic tag used by AW-283."""

from engine.interactions.models import InteractionOption


def test_interaction_option_accepts_optional_topic_tag() -> None:
    option = InteractionOption(
        option_id="observe",
        prompt_key="interaction.observe",
        topic="observation",
    )
    assert option.topic == "observation"
