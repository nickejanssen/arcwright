"""Tests for deterministic answer-content matching."""

from uuid import uuid4

from engine.case.models import AuthorizedFalsehood
from engine.characters.context import KnownFactContext
from engine.claims.matcher import match_answer_content


def _falsehood(topic: str = "location") -> AuthorizedFalsehood:
    return AuthorizedFalsehood(
        falsehood_id="lie.location.one",
        speaker_id="char-1",
        topic=topic,
        claim_text="I was on the terrace.",
        contradicted_by=["evidence.one"],
    )


def _known_fact(topic: str = "location") -> KnownFactContext:
    return KnownFactContext(
        fact_id=uuid4(),
        fact_type="case_fact",
        fact_content={"topic": topic, "detail": "the terrace"},
        confidence=1.0,
        provenance_chain=("char-1",),
        provenance_chain_length=1,
    )


def test_matcher_prefers_matching_authorized_falsehood() -> None:
    falsehood = _falsehood()
    result = match_answer_content(
        topic="location",
        falsehoods=[falsehood],
        known_facts=[_known_fact()],
    )
    assert result == falsehood


def test_matcher_falls_back_to_matching_known_fact() -> None:
    fact = _known_fact(topic="relationship")
    result = match_answer_content(
        topic="relationship",
        falsehoods=[_falsehood(topic="location")],
        known_facts=[fact],
    )
    assert result == fact


def test_matcher_returns_none_for_unknown_topic() -> None:
    result = match_answer_content(
        topic="possession",
        falsehoods=[_falsehood(topic="location")],
        known_facts=[_known_fact(topic="relationship")],
    )
    assert result is None


def test_matcher_is_stable_for_repeated_calls() -> None:
    falsehood = _falsehood()
    inputs = {
        "topic": "location",
        "falsehoods": [falsehood],
        "known_facts": [_known_fact()],
    }
    assert match_answer_content(**inputs) == match_answer_content(**inputs)
