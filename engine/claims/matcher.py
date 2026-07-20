"""Deterministic matching of question topics to answer content."""

from __future__ import annotations

from collections.abc import Sequence

from engine.case.models import AuthorizedFalsehood
from engine.characters.context import KnownFactContext


def match_answer_content(
    *,
    topic: str,
    falsehoods: Sequence[AuthorizedFalsehood],
    known_facts: Sequence[KnownFactContext],
) -> AuthorizedFalsehood | KnownFactContext | None:
    """Return the first authorized falsehood or known fact matching ``topic``.

    Falsehoods take precedence over facts so authored lie content is selected
    deterministically whenever a speaker has one for the asked topic.
    """
    for falsehood in falsehoods:
        if falsehood.topic == topic:
            return falsehood

    for fact in known_facts:
        fact_topic = fact.fact_content.get("topic")
        if (isinstance(fact_topic, str) and fact_topic == topic) or (
            fact_topic is None and fact.fact_type == topic
        ):
            return fact

    return None
