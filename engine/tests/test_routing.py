"""Tests for the LiteLLM routing layer."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from engine.routing import RouteResult, route_generation
from engine.routing.router import (
    ROUTING_TABLE_PATH,
    resolve_fallback_model_key,
    resolve_model_key,
)


def _mock_response(
    *,
    content: str = "generated text",
    prompt_tokens: int = 11,
    completion_tokens: int = 7,
) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content),
            )
        ],
        usage=SimpleNamespace(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        ),
    )


async def test_route_generation_uses_correct_model_from_table() -> None:
    expected_model = resolve_model_key("character_dialogue", "standard")
    response = _mock_response()

    with (
        patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
            return_value=response,
        ) as mock_completion,
        patch(
            "engine.routing.router.time.perf_counter",
            side_effect=[10.0, 10.25],
        ),
    ):
        await route_generation(
            task_type="character_dialogue",
            quality_tier="standard",
            messages=[{"role": "user", "content": "hello"}],
        )

    mock_completion.assert_awaited_once_with(
        model=expected_model,
        messages=[{"role": "user", "content": "hello"}],
        temperature=0.7,
    )


async def test_route_generation_returns_result_with_latency_and_tokens() -> None:
    response = _mock_response(
        content="route me",
        prompt_tokens=13,
        completion_tokens=17,
    )

    with (
        patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
            return_value=response,
        ),
        patch(
            "engine.routing.router.time.perf_counter",
            side_effect=[20.0, 20.125],
        ),
    ):
        result = await route_generation(
            task_type="character_dialogue",
            quality_tier="standard",
            messages=[{"role": "system", "content": "hi"}],
        )

    assert result == RouteResult(
        content="route me",
        model_used=resolve_model_key("character_dialogue", "standard"),
        input_tokens=13,
        output_tokens=17,
        latency_ms=125,
        used_fallback=False,
    )


async def test_route_generation_falls_back_on_primary_failure() -> None:
    primary_model = resolve_model_key("character_dialogue", "standard")
    fallback_model = resolve_fallback_model_key("character_dialogue", "standard")
    assert fallback_model is not None

    response = _mock_response(content="fallback result")

    with (
        patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
            side_effect=[Exception("primary failed"), response],
        ) as mock_completion,
        patch(
            "engine.routing.router.time.perf_counter",
            side_effect=[1.0, 2.0, 2.25],
        ),
    ):
        result = await route_generation(
            task_type="character_dialogue",
            quality_tier="standard",
            messages=[{"role": "user", "content": "fallback please"}],
        )

    assert mock_completion.await_count == 2
    assert mock_completion.await_args_list[0].kwargs["model"] == primary_model
    assert mock_completion.await_args_list[1].kwargs["model"] == fallback_model
    assert result.used_fallback is True
    assert result.model_used == fallback_model
    assert result.content == "fallback result"
    assert result.latency_ms == 250


async def test_route_generation_propagates_when_no_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    primary_model = resolve_model_key("character_dialogue", "standard")
    patched_table = {
        "character_dialogue": {
            "standard": primary_model,
            "premium": resolve_model_key("character_dialogue", "premium"),
            "premium_fallback": resolve_fallback_model_key(
                "character_dialogue", "premium"
            )
            or "",
        }
    }
    monkeypatch.setattr("engine.routing.router._ROUTING_TABLE", patched_table)

    with patch(
        "engine.routing.router.litellm.acompletion",
        new_callable=AsyncMock,
        side_effect=RuntimeError("primary failed"),
    ):
        with pytest.raises(RuntimeError, match="primary failed"):
            await route_generation(
                task_type="character_dialogue",
                quality_tier="standard",
                messages=[{"role": "user", "content": "no fallback"}],
            )


async def test_route_generation_marks_used_fallback_false_on_clean_call() -> None:
    response = _mock_response()

    with (
        patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
            return_value=response,
        ),
        patch(
            "engine.routing.router.time.perf_counter",
            side_effect=[3.0, 3.03],
        ),
    ):
        result = await route_generation(
            task_type="character_dialogue",
            quality_tier="standard",
            messages=[{"role": "assistant", "content": "clean"}],
        )

    assert result.used_fallback is False


def test_routing_table_contains_all_task_types() -> None:
    routing_table = json.loads(Path(ROUTING_TABLE_PATH).read_text())
    expected_task_types = {
        "character_dialogue",
        "narrative_generation",
        "pacing_decision",
        "knowledge_inference",
        "safety_classification",
        "killer_assignment",
        "narrator_bridge",
    }
    expected_tier_keys = {
        "standard",
        "premium",
        "standard_fallback",
        "premium_fallback",
    }

    assert set(routing_table) == expected_task_types
    for task_type in expected_task_types:
        assert expected_tier_keys.issubset(routing_table[task_type])


def test_resolve_model_key_raises_on_unknown_task_type() -> None:
    with pytest.raises(KeyError):
        resolve_model_key("nonexistent", "standard")


def test_engine_routing_exports_route_result_and_route_generation() -> None:
    from engine.routing import RouteResult as exported_route_result
    from engine.routing import route_generation as exported_route_generation

    assert exported_route_result is RouteResult
    assert exported_route_generation is route_generation
