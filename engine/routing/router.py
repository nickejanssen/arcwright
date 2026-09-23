"""Provider-agnostic routing helpers for LLM-backed generation."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

import litellm
import structlog

ROUTING_TABLE_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "routing_table.json"
)
_ROUTING_TABLE: Dict[str, Dict[str, str]] = json.loads(ROUTING_TABLE_PATH.read_text())


@dataclass(frozen=True)
class ProviderCredential:
    """How one provider's credential reaches its SDK.

    ``env_var`` is what the SDK reads. ``deploy_slot`` is the provider-neutral
    name deploy infrastructure binds it under, or None when the provider has no
    allocated slot.
    """

    env_var: str
    deploy_slot: Optional[str] = None

    def accepted_env_vars(self) -> tuple[str, ...]:
        if self.deploy_slot is None:
            return (self.env_var,)
        return (self.env_var, self.deploy_slot)


# Deploy infrastructure binds LLM credentials under provider-neutral names
# (PRIMARY_LLM_API_KEY, SECONDARY_LLM_API_KEY) so no workflow or Secret Manager
# config outside this file has to name a provider. This is the one place,
# per AGENTS.md's provider-agnostic routing rule, allowed to translate those
# into the env vars each provider's SDK expects.
#
# Keyed by the provider id used in config/routing_table.json, so callers that
# only know the routing table can resolve what credential a route needs. The
# env var name is whatever that provider's SDK reads, which is not derivable
# from the provider id by any rule worth trusting: some providers do not use
# an {NAME}_API_KEY variable at all. Adding a provider to the routing table
# means adding it here too.
_PROVIDER_CREDENTIALS: Dict[str, ProviderCredential] = {
    "anthropic": ProviderCredential("ANTHROPIC_API_KEY", "PRIMARY_LLM_API_KEY"),
    "groq": ProviderCredential("GROQ_API_KEY", "SECONDARY_LLM_API_KEY"),
}


class UnmappedProviderError(ValueError):
    """A routing-table provider has no credential entry in this module."""


def _routing_table_providers(
    table: Optional[Dict[str, Dict[str, str]]] = None,
) -> list[str]:
    """Provider ids referenced by the active routing table, in sorted order."""
    source = _ROUTING_TABLE if table is None else table
    providers: set[str] = set()
    for tier_map in source.values():
        if not isinstance(tier_map, dict):
            continue
        for model in tier_map.values():
            if isinstance(model, str) and "/" in model:
                provider = model.split("/", 1)[0]
                if provider:
                    providers.add(provider)
    return sorted(providers)


def required_credential_env_vars(
    table: Optional[Dict[str, Dict[str, str]]] = None,
) -> list[tuple[str, ...]]:
    """Env var names that can supply each credential the routing table needs.

    One entry per provider the table references, each listing the names that
    satisfy it: the provider's own variable first, then its provider-neutral
    deploy slot where one exists. Callers outside this module use this to check
    an environment without naming a provider themselves.

    Raises UnmappedProviderError when the table references a provider this
    module has no entry for, rather than guessing a variable name.
    """
    requirements: list[tuple[str, ...]] = []
    for provider in _routing_table_providers(table):
        credential = _PROVIDER_CREDENTIALS.get(provider)
        if credential is None:
            raise UnmappedProviderError(
                f"routing table uses provider {provider!r}, which has no "
                f"credential entry in {Path(__file__).name}"
            )
        requirements.append(credential.accepted_env_vars())
    return requirements


def hydrate_provider_credentials(env: Optional[Dict[str, str]] = None) -> None:
    target = os.environ if env is None else env
    for credential in _PROVIDER_CREDENTIALS.values():
        slot_var = credential.deploy_slot
        if slot_var is None:
            continue
        if not target.get(credential.env_var) and target.get(slot_var):
            target[credential.env_var] = target[slot_var]


hydrate_provider_credentials()

# MVP cost rates — update only when provider pricing changes.
# All values are USD per token. Model keys must exactly match routing_table.json.
_COST_RATES: Dict[str, tuple[float, float]] = {
    # key: (cost_per_input_token, cost_per_output_token)
    "anthropic/claude-haiku-4-5-20251001": (0.00000025, 0.00000125),
    "anthropic/claude-sonnet-4-6": (0.000003, 0.000015),
    "groq/llama-3.1-8b-instant": (0.00000005, 0.00000008),
    "groq/llama-3.3-70b-versatile": (0.00000059, 0.00000079),
    "groq/gpt-oss-safeguard-20b": (0.00000020, 0.00000020),
}


@dataclass(frozen=True)
class RouteResult:
    content: str
    model_used: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    used_fallback: bool


_MIN_COST = Decimal("0.000001")


def compute_cost(model_used: str, input_tokens: int, output_tokens: int) -> Decimal:
    rates = _COST_RATES.get(model_used)
    if rates is None:
        raise ValueError(
            f"unknown model cost: {model_used!r} — add it to _COST_RATES in router.py"
        )
    raw = rates[0] * input_tokens + rates[1] * output_tokens
    quantized = Decimal(str(raw)).quantize(_MIN_COST)
    # Clamp sub-precision positive costs to the minimum representable value so
    # small pacing/safety calls don't appear free in per-session cost rollups.
    if raw > 0 and quantized == Decimal("0"):
        return _MIN_COST
    return quantized


def mark_stable_context_cacheable(
    messages: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Return a new list with the system message wrapped in Anthropic cache_control."""
    if not messages:
        return messages
    first = messages[0]
    if first.get("role") != "system" or not isinstance(first.get("content"), str):
        return messages
    new_first: Dict[str, Any] = dict(first)
    new_first["content"] = [
        {
            "type": "text",
            "text": first["content"],
            "cache_control": {"type": "ephemeral"},
        }
    ]
    return [new_first] + list(messages[1:])


def load_routing_table() -> Dict[str, Dict[str, str]]:
    return _ROUTING_TABLE


def resolve_model_key(task_type: str, quality_tier: str) -> str:
    routing_table = load_routing_table()
    return routing_table[task_type][quality_tier]


def resolve_fallback_model_key(task_type: str, quality_tier: str) -> Optional[str]:
    routing_table = load_routing_table()
    return routing_table[task_type].get(f"{quality_tier}_fallback")


async def _complete_with_model(
    model_key: str,
    messages: List[Dict[str, Any]],
    temperature: float,
) -> tuple[Any, int]:
    start = time.perf_counter()
    response = await litellm.acompletion(
        model=model_key,
        messages=messages,
        temperature=temperature,
    )
    end = time.perf_counter()
    return response, int((end - start) * 1000)


async def route_generation(
    task_type: str,
    quality_tier: str,
    messages: List[Dict[str, Any]],
    temperature: float = 0.7,
) -> RouteResult:
    cacheable_messages = mark_stable_context_cacheable(messages)
    model_key = resolve_model_key(task_type, quality_tier)
    fallback_key = resolve_fallback_model_key(task_type, quality_tier)

    try:
        response, latency_ms = await _complete_with_model(
            model_key=model_key,
            messages=cacheable_messages,
            temperature=temperature,
        )
        model_used = model_key
        used_fallback = False
    except Exception:
        if not fallback_key:
            raise
        response, latency_ms = await _complete_with_model(
            model_key=fallback_key,
            messages=cacheable_messages,
            temperature=temperature,
        )
        model_used = fallback_key
        used_fallback = True

    structlog.get_logger().debug(
        "route_generation_complete",
        task_type=task_type,
        quality_tier=quality_tier,
        model_used=model_used,
        used_fallback=used_fallback,
        latency_ms=latency_ms,
    )

    return RouteResult(
        content=response.choices[0].message.content,
        model_used=model_used,
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
        latency_ms=latency_ms,
        used_fallback=used_fallback,
    )
