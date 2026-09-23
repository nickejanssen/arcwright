"""Tests for the LiteLLM routing layer."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from engine.routing import RouteResult, route_generation
from engine.routing.router import (
    ROUTING_TABLE_PATH,
    UnmappedProviderError,
    compute_cost,
    hydrate_provider_credentials,
    required_credential_env_vars,
    resolve_fallback_model_key,
    resolve_model_key,
)

CHARACTER_STANDARD_MODEL = resolve_model_key("character_dialogue", "standard")
PACING_STANDARD_MODEL = resolve_model_key("pacing_decision", "standard")


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


async def test_route_generation_applies_prompt_caching_to_system_message() -> None:
    response = _mock_response()
    messages = [
        {"role": "system", "content": "arc context"},
        {"role": "user", "content": "go"},
    ]

    with (
        patch(
            "engine.routing.router.litellm.acompletion",
            new_callable=AsyncMock,
            return_value=response,
        ) as mock_completion,
        patch(
            "engine.routing.router.time.perf_counter",
            side_effect=[0.0, 0.1],
        ),
    ):
        await route_generation(
            task_type="character_dialogue",
            quality_tier="standard",
            messages=messages,
        )

    call_messages = mock_completion.call_args.kwargs["messages"]
    assert call_messages[0]["content"] == [
        {"type": "text", "text": "arc context", "cache_control": {"type": "ephemeral"}}
    ]
    assert call_messages[1] == {"role": "user", "content": "go"}
    # original list not mutated
    assert messages[0]["content"] == "arc context"


def test_compute_cost_nonzero_for_known_model() -> None:
    cost = compute_cost(CHARACTER_STANDARD_MODEL, 1000, 500)
    assert cost > Decimal("0")


def test_compute_cost_raises_for_unknown_model() -> None:
    with pytest.raises(ValueError, match="unknown model cost"):
        compute_cost("unknown/model-xyz", 100, 50)


def test_compute_cost_clamps_sub_precision_positive_cost_to_minimum() -> None:
    # The current pacing standard model is cheap enough that a 1-token call
    # rounds to zero without the minimum-cost clamp.
    cost = compute_cost(PACING_STANDARD_MODEL, 1, 1)
    assert cost == Decimal("0.000001")


def test_hydrate_provider_credentials_maps_generic_slots_to_provider_vars() -> None:
    env = {
        "PRIMARY_LLM_API_KEY": "anthropic-secret",
        "SECONDARY_LLM_API_KEY": "groq-secret",
    }

    hydrate_provider_credentials(env)

    assert env["ANTHROPIC_API_KEY"] == "anthropic-secret"
    assert env["GROQ_API_KEY"] == "groq-secret"


def test_hydrate_provider_credentials_does_not_override_existing_provider_var() -> None:
    env = {
        "PRIMARY_LLM_API_KEY": "generic-secret",
        "ANTHROPIC_API_KEY": "local-dev-secret",
    }

    hydrate_provider_credentials(env)

    assert env["ANTHROPIC_API_KEY"] == "local-dev-secret"


def test_hydrate_provider_credentials_is_a_noop_without_generic_slots() -> None:
    env: dict[str, str] = {}

    hydrate_provider_credentials(env)

    assert env == {}


def test_required_credential_env_vars_covers_every_routing_table_provider() -> None:
    requirements = required_credential_env_vars()

    assert requirements == [
        ("ANTHROPIC_API_KEY", "PRIMARY_LLM_API_KEY"),
        ("GROQ_API_KEY", "SECONDARY_LLM_API_KEY"),
    ]


def test_required_credential_env_vars_lists_the_deploy_slot_as_an_alternative() -> None:
    # The neutral slot is what deploy infrastructure binds, so an environment
    # that sets only the slot must count as satisfying the provider.
    for accepted in required_credential_env_vars():
        assert len(accepted) == 2
        provider_var, slot_var = accepted
        assert provider_var.endswith("_API_KEY")
        assert slot_var.endswith("_LLM_API_KEY")


def test_required_credential_env_vars_tracks_the_table_it_is_given() -> None:
    # A table using only one provider must not demand the other's credential.
    # A synthetic model name here (not one of the real configured models) keeps
    # this out of evals/cases/no_hardcoded_model_strings_outside_routing_layer.json,
    # which flags any real routing-table model string appearing outside the
    # routing layer.
    requirements = required_credential_env_vars(
        {"character_dialogue": {"standard": "groq/test-fixture-model"}}
    )

    assert requirements == [("GROQ_API_KEY", "SECONDARY_LLM_API_KEY")]


def test_required_credential_env_vars_rejects_an_unmapped_provider() -> None:
    # Guessing a variable name would send the operator hunting for a key no
    # SDK reads. Naming the file to edit is the useful failure.
    with pytest.raises(UnmappedProviderError) as exc:
        required_credential_env_vars(
            {"character_dialogue": {"standard": "newcomer/some-model"}}
        )

    assert "newcomer" in str(exc.value)
    assert "router.py" in str(exc.value)


def test_hydrate_and_required_credentials_agree_on_the_same_variables() -> None:
    # The two are one mapping: whatever hydrate writes must be what the
    # requirement check accepts, or a hydrated environment could still be
    # reported as missing its credentials.
    env = {"PRIMARY_LLM_API_KEY": "a", "SECONDARY_LLM_API_KEY": "b"}

    hydrate_provider_credentials(env)

    for accepted in required_credential_env_vars():
        assert any(env.get(name) for name in accepted)


def test_cost_rates_cover_all_routing_table_models() -> None:
    from engine.routing.router import _COST_RATES

    routing_table = json.loads(Path(ROUTING_TABLE_PATH).read_text())
    all_model_keys: set[str] = set()
    for tiers in routing_table.values():
        all_model_keys.update(tiers.values())

    missing = all_model_keys - set(_COST_RATES)
    assert not missing, (
        f"models in routing_table.json missing from _COST_RATES: {missing}"
    )
