"""Tests for Layer 2 safety classification helpers."""

from __future__ import annotations

from engine.safety import (
    L2_BLOCK_SENTINEL,
    NEUTRAL_L2_BRIDGE,
    build_l2_blocked_route_result,
    build_l2_classification_messages,
    build_l2_classification_payload,
    parse_l2_classification,
)


def test_build_l2_classification_messages_includes_policy_context() -> None:
    messages = [{"role": "user", "content": "A fictional suspect hides a clue."}]

    result = build_l2_classification_messages(
        messages,
        safety_policy_context={"permitted": ["fictional mystery"]},
    )

    assert result[0]["role"] == "system"
    assert result[1]["role"] == "user"
    assert "fictional mystery" in result[1]["content"]
    assert "A fictional suspect hides a clue." in result[1]["content"]


def test_parse_l2_classification_allowed_json() -> None:
    result = parse_l2_classification(
        '{"blocked": false, "confidence": 0.92, "category": "permitted"}'
    )

    assert result.blocked is False
    assert result.confidence == 0.92
    assert result.category == "permitted"
    assert result.code == "l2_allowed"


def test_parse_l2_classification_blocked_json() -> None:
    result = parse_l2_classification(
        '{"blocked": true, "confidence": 0.88, "category": "real_world_harm"}'
    )

    assert result.blocked is True
    assert result.confidence == 0.88
    assert result.category == "real_world_harm"
    assert result.code == "l2_real_world_harm"


def test_parse_l2_classification_fails_closed_on_malformed_output() -> None:
    result = parse_l2_classification("not json")

    assert result.blocked is True
    assert result.confidence == 0.0
    assert result.category == "unknown"
    assert result.code == "l2_unknown"


def test_l2_payload_excludes_raw_classifier_output() -> None:
    result = parse_l2_classification(
        '{"blocked": true, "confidence": 0.8, "category": "real_world_harm"}'
    )

    payload = build_l2_classification_payload(result)

    assert payload == {
        "layer": "L2",
        "blocked": True,
        "confidence": 0.8,
        "category": "real_world_harm",
        "code": "l2_real_world_harm",
        "source": "generation_messages",
    }


def test_l2_blocked_route_result_is_non_provider_sentinel() -> None:
    result = build_l2_blocked_route_result()

    assert result.content == NEUTRAL_L2_BRIDGE
    assert result.model_used == L2_BLOCK_SENTINEL
    assert result.input_tokens == 0
    assert result.output_tokens == 0
    assert result.latency_ms == 0
    assert result.used_fallback is False
