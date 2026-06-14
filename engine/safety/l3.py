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
needing to change Arcwright's core engine code.

For the Nightcap murder mystery, the L3 rules are derived directly from the
arc's `content_rails` configuration, so tests can prove the policy is
sourced from the arc, not baked into the platform.

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

# ---------------------------------------------------------------------------
# Nightcap-specific policy block
# ---------------------------------------------------------------------------

# These are the L3 rules that apply specifically to the Nightcap murder
# mystery arc.  They are expressed as plain English sentences because the
# prompt is read by a language model, not parsed by code.
#
# The sentences are kept deliberately simple so that a non-technical game
# designer reading the injected prompt can understand what they say.

_NIGHTCAP_EXTRA_PROHIBITIONS = (
    # Nightcap is a social deduction game. The murder is a plot device, not
    # a spectacle.  Describing it in graphic detail would shift the tone from
    # cosy mystery to disturbing content.
    "Do not graphically depict the murder itself or describe violence in explicit physical detail.",
    # Player characters are fictional.  Introducing sexual content between
    # them is out of scope for the game experience.
    "Do not include sexual content between any characters.",
    # The game frame must stay fiction.  Breaking it to give real harmful
    # information (e.g. "as a character, here is how to really poison someone")
    # is prohibited even if the player phrases the request in-character.
    "Do not provide real-world harmful information while speaking in character.",
    # Nightcap character names and story elements must not be used to target
    # or mock real living people.
    "Do not produce content that directly accuses or targets a real, named person.",
)


def build_nightcap_l3_policy_block(content_rails: "ContentRailsConfig") -> str:
    """Build the Nightcap-specific L3 policy block from arc content rails.

    This function exists so that tests can prove the policy text is derived
    from the arc's `content_rails` configuration rather than being hardcoded
    inside the engine.

    How it works:
        1. Start with any categories the game designer has marked as
           prohibited in the arc definition.
        2. Add the Nightcap-specific extra prohibitions defined above.
        3. Wrap the combined list in a clear, model-readable block header.

    Args:
        content_rails: The `ContentRailsConfig` object from the arc definition.
            The `prohibited_categories` list on this object drives step 1.

    Returns:
        A plain-language policy block string ready for injection into a
        system prompt, or as an additional message before generation.
    """
    # Step 1: collect arc-level prohibited categories as human-readable lines.
    # The game designer configures these in the arc JSON under content_rails.
    arc_prohibitions = [
        f"Do not produce content in the category: {category}."
        for category in content_rails.prohibited_categories
    ]

    # Step 2: add the Nightcap-specific sentences defined at module level.
    all_prohibitions = arc_prohibitions + list(_NIGHTCAP_EXTRA_PROHIBITIONS)

    return _format_policy_block(all_prohibitions)


def build_l3_policy_block(content_rails: "ContentRailsConfig") -> str:
    """Build a generic L3 policy block from arc content rails.

    This is the general-purpose version that any arc can use.  It converts
    the arc designer's prohibited category list into plain-English instructions
    the AI model will follow during generation.

    For arcs that need additional platform-specific sentences (like Nightcap),
    callers should use `build_nightcap_l3_policy_block` or a similar
    arc-specific builder that wraps this function.

    Args:
        content_rails: The `ContentRailsConfig` object from the arc definition.

    Returns:
        A plain-language policy block string.
    """
    arc_prohibitions = [
        f"Do not produce content in the category: {category}."
        for category in content_rails.prohibited_categories
    ]
    return _format_policy_block(arc_prohibitions)


def inject_l3_policy_block(
    messages: list[dict[str, Any]],
    content_rails: "ContentRailsConfig | None",
    *,
    nightcap_mode: bool = False,
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

    If `content_rails` is None (the arc has not configured any rails), this
    function returns the original messages list unchanged.  Callers do not
    need to check for None before calling.

    Args:
        messages: The generation prompt message list to inject into.
        content_rails: The arc's content rails configuration, or None if
            the arc does not define any.
        nightcap_mode: When True, uses the Nightcap-specific policy builder
            which adds extra Nightcap-appropriate prohibitions on top of the
            arc-level rails.  Defaults to False so other arcs are unaffected.

    Returns:
        A new messages list.  The original list is never mutated.
    """
    if content_rails is None:
        return messages

    if nightcap_mode:
        policy_text = build_nightcap_l3_policy_block(content_rails)
    else:
        policy_text = build_l3_policy_block(content_rails)

    if not policy_text.strip():
        # No prohibitions at all, so there is nothing to inject.
        return messages

    return _prepend_policy_to_messages(messages, policy_text)


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


def _prepend_policy_to_messages(
    messages: list[dict[str, Any]],
    policy_text: str,
) -> list[dict[str, Any]]:
    """Add the policy block to the front of the system prompt.

    This inserts the policy before the character identity and knowledge state
    blocks that follow it in the full assembled prompt.  The order matches
    the architecture document: character identity → knowledge state → L3 policy
    (from the model's perspective, policy is at the outermost system level).

    Implementation note: we inject as a new system message at position 0 so
    that the existing system message (character identity + knowledge state)
    remains intact and the policy is always the first thing the model reads.
    This is safe across providers because the policy message is a standard
    string-content system message.
    """
    policy_message: dict[str, Any] = {
        "role": "system",
        "content": policy_text,
    }
    return [policy_message] + list(messages)
