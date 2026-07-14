"""Layer 3 in-generation policy injection helpers.

What this module does and why it exists
----------------------------------------
This is the "rules in the prompt" safety layer. Before the AI writes any
character dialogue or narration, the engine adds a plain-language block to
the prompt that tells the AI exactly what it must not write, no matter what
a player asks or what the story setup looks like.

Think of it like the instructions a human game master receives before
running a murder mystery event: "here are the topics you must never touch,
here is how to steer away from them politely."

The rules come from the game designer's arc definition (the `content_rails`
field), not from hardcoded platform defaults. This means a third-party
developer building a different game can set their own L3 rules without
needing to change Arcwright's core engine code. Experience-specific
prohibition sentences live in the arc's `content_rails.extra_prohibitions`
list, so the engine stays game-agnostic while every game keeps full control
of its own policy text.

L3 is the cheapest and most customisable safety layer. It sits after the
deterministic L1 hard stops and the AI-based L2 classification, and it is
injected into every main generation call that is not itself a safety
classification call.

Architecture reference: docs/architecture/10-content-safety.md S10.4
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from engine.arc.models import ContentRailsConfig

# ---------------------------------------------------------------------------
# Sentinel values
# ---------------------------------------------------------------------------

NEUTRAL_L3_BRIDGE = "The narrator gently steers the scene in a different direction."
"""Fallback text returned when L3 blocks a generation call.

This keeps the session alive for players. They see a smooth narrative
redirect rather than an error or an abrupt silence.
"""

L3_BLOCK_SENTINEL = "l3_policy_block"
"""Identifier placed in the model_used field when L3 prevents a generation.

This sentinel never contains a real provider or model name.  Its presence in
a generation log tells operators that the content was blocked by the in-prompt
policy layer, not by the classifier (L2) or a hard stop (L1).
"""

# Platform minimum policy: the four unconditional L1 hard-stop categories
# expressed as plain-language instructions for the main language model.
# These are injected when no arc-specific content_rails are provided, so
# L3 always runs as a backstop even before the arc coordinator is wired up.
# They mirror L1 (which blocks at the input layer) but act at the generation
# layer as additional protection for the same categories.
_PLATFORM_MINIMUM_PROHIBITIONS = (
    "Do not produce sexual content involving anyone under 18.",
    "Do not produce content targeting a real, named, living individual with harmful intent.",
    "Do not provide detailed instructions for real-world violence or weapons construction.",
    "Do not produce content designed to facilitate real-world harm outside the fictional frame.",
)


def build_l3_policy_block(content_rails: "ContentRailsConfig") -> str:
    """Build the L3 policy block from arc content rails.

    Converts the arc designer's prohibited category list into plain-English
    instructions, then appends the arc's `extra_prohibitions` sentences
    verbatim.  Everything in the block is sourced from the arc definition,
    so any game — first-party or third-party — controls its own policy text
    without engine changes.

    Args:
        content_rails: The `ContentRailsConfig` object from the arc definition.

    Returns:
        A plain-language policy block string ready for injection into a
        system prompt, or "" when the rails define no prohibitions at all.
    """
    arc_prohibitions = [
        f"Do not produce content in the category: {category}."
        for category in content_rails.prohibited_categories
    ]
    all_prohibitions = arc_prohibitions + list(content_rails.extra_prohibitions)
    return _format_policy_block(all_prohibitions)


def inject_l3_policy_block(
    messages: list[dict[str, Any]],
    content_rails: "ContentRailsConfig | None",
) -> list[dict[str, Any]]:
    """Return a new messages list with the L3 policy block inserted.

    This function is the main integration point called by the generation
    pipeline.  It takes the list of messages that would normally be sent to
    the AI model and prepends a policy block so the model reads the rules
    before it reads the story context and generates a response.

    The policy block is added as a system message at the beginning of the
    message list.  If a system message already exists, the policy block is
    prepended to its text content so the model sees one combined system
    prompt.  This avoids creating duplicate system messages, which some
    providers do not support.

    If `content_rails` is None, the platform minimum policy block is injected
    (the four unconditional L1 categories expressed as plain-language
    instructions).  Callers do not need to check for None before calling.

    Args:
        messages: The generation prompt message list to inject into.
        content_rails: The arc's content rails configuration, or None when
            no arc has been wired up yet.  When None, the platform minimum
            policy is used so L3 always runs.

    Returns:
        A new messages list.  The original list is never mutated.
    """
    if content_rails is None:
        # No arc-specific rails provided. Inject the platform minimum so
        # L3 always runs, even before the arc coordinator is wired up.
        policy_text = _format_policy_block(list(_PLATFORM_MINIMUM_PROHIBITIONS))
        return _inject_policy_into_messages(messages, policy_text)

    policy_text = build_l3_policy_block(content_rails)

    if not policy_text.strip():
        # No prohibitions at all, so there is nothing to inject.
        return messages

    return _inject_policy_into_messages(messages, policy_text)


def build_l3_blocked_route_result() -> "RouteResult":  # type: ignore[name-defined]  # noqa: F821
    """Return a sentinel RouteResult that represents an L3 block.

    This is used when the caller detects that the assembled messages would
    violate L3 policy even after L2 classification passed.  In practice,
    L3 works through prompt injection rather than blocking, but this
    sentinel is available if a future caller needs to signal a hard stop at
    the L3 level.

    The sentinel uses no real model, costs nothing, and returns a neutral
    bridge message the player can see.
    """
    from engine.routing.router import RouteResult

    return RouteResult(
        content=NEUTRAL_L3_BRIDGE,
        model_used=L3_BLOCK_SENTINEL,
        input_tokens=0,
        output_tokens=0,
        latency_ms=0,
        used_fallback=False,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _format_policy_block(prohibitions: list[str]) -> str:
    """Wrap a list of prohibition sentences in a policy block header.

    The header and footer delimiters make it easy for the AI model to
    recognise that these are rules it must follow, not story content.
    They also make it easy for a human reading the prompt to find where
    the policy block starts and ends.
    """
    if not prohibitions:
        return ""
    lines = ["[CONTENT POLICY - YOU MUST FOLLOW THESE RULES]"]
    lines.extend(prohibitions)
    lines.append("[END CONTENT POLICY]")
    return "\n".join(lines)


def _inject_policy_into_messages(
    messages: list[dict[str, Any]],
    policy_text: str,
) -> list[dict[str, Any]]:
    """Append the policy block to the system prompt, preserving prompt caching.

    Policy is appended to the content of the first system message so the
    complete system prompt (character identity + knowledge state + L3 policy)
    stays in a single message.  The generation router passes messages to
    `mark_stable_context_cacheable()`, which wraps `messages[0]` with
    Anthropic's `cache_control`.  Merging the policy into that message means
    the stable character/knowledge context stays in the cached region rather
    than being displaced by the policy block.

    The architecture places L3 policy after the character identity and
    knowledge state blocks (docs/architecture/10-content-safety.md §10.4),
    which appending to the end of the system message achieves.

    If the system message content is not a plain string (e.g. it is already
    in content-block format from a prior `cache_control` wrap), a new system
    message is inserted at position 0 as a safe fallback.  In that case
    caching of the original context is preserved because its block remains
    intact at position 1.
    """
    result = list(messages)
    for i, msg in enumerate(result):
        if msg.get("role") == "system":
            existing = msg.get("content", "")
            if not isinstance(existing, str):
                # Content already in block format, so insert a new system message
                # rather than mutating the block list.
                result.insert(0, {"role": "system", "content": policy_text})
                return result
            result[i] = {**msg, "content": f"{existing}\n\n{policy_text}"}
            return result
    # No system message found, so create one at the front.
    result.insert(0, {"role": "system", "content": policy_text})
    return result
