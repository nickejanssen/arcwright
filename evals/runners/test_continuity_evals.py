"""Continuity and coherence eval suite (AW-272, spec 0066, ADR-0012).

Deterministic checks only (v1) over session generation logs:

1. Knowledge-leak: a generated character output referencing the payload of
   a fact outside the character's knowledge state at generation time.
2. Contradiction: a generated character output referencing a fact the
   character held with a superseding revocation at generation time (the
   revoke operation, architecture 04 §4.3).

Matching reuses the runtime leak guard's normalization helpers
(engine.characters.dialogue) so the eval and the in-engine constraint
agree on what counts as a reference.

Known v1 limitation (documented per spec 0066): fact-payload string
matching misses paraphrased leaks. The classifier upgrade is the
ADR-0012 watchpoint open question.

Thresholds load from evals/continuity_thresholds.json and are adjustable
without code changes. The report is written to
evals/reports/continuity_eval_report.json in the spec 0066 format.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from engine.characters.dialogue import (
    _contains_normalized_phrase,
    _fact_value_strings,
    _normalize_text,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
THRESHOLDS_PATH = REPO_ROOT / "evals" / "continuity_thresholds.json"
REPORTS_DIR = REPO_ROOT / "evals" / "reports"
REPORT_PATH = REPORTS_DIR / "continuity_eval_report.json"

REPORT_NOTES = (
    "Deterministic v1 checks: fact-payload string matching misses "
    "paraphrased leaks (ADR-0012 watchpoint)."
)


# ---------------------------------------------------------------------------
# Session log model
#
# Plain data structures so the evaluator runs identically over a recorded
# session export or a freshly generated synthetic batch.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GenerationRecord:
    """One generated character output plus its generation-time knowledge state.

    Mirrors what the engine logs on every dialogue event: the content text
    and the knowledge_constraint payload (known/unknown fact ids at
    generation time), plus the fact ids the character held revoked.
    """

    character_id: str
    content_text: str
    known_fact_ids: tuple[str, ...]
    unknown_fact_ids: tuple[str, ...]
    revoked_fact_ids: tuple[str, ...] = ()


@dataclass
class SessionLog:
    session_id: str
    fact_content_by_id: dict[str, Any]
    generations: list[GenerationRecord] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Deterministic checks
# ---------------------------------------------------------------------------


def _references_fact(content_text: str, fact_content: Any) -> bool:
    normalized_dialogue = _normalize_text(content_text)
    for phrase in _fact_value_strings(fact_content):
        if _contains_normalized_phrase(normalized_dialogue, _normalize_text(phrase)):
            return True
    return False


def count_knowledge_leaks(session: SessionLog, record: GenerationRecord) -> int:
    """Count facts outside the character's knowledge state that the output references."""
    return sum(
        1
        for fact_id in record.unknown_fact_ids
        if fact_id in session.fact_content_by_id
        and _references_fact(record.content_text, session.fact_content_by_id[fact_id])
    )


def count_contradictions(session: SessionLog, record: GenerationRecord) -> int:
    """Count references to facts the character held with a superseding revocation."""
    return sum(
        1
        for fact_id in record.revoked_fact_ids
        if fact_id in session.fact_content_by_id
        and _references_fact(record.content_text, session.fact_content_by_id[fact_id])
    )


def evaluate_session(session: SessionLog) -> dict[str, Any]:
    leaks = 0
    contradictions = 0
    for record in session.generations:
        leaks += count_knowledge_leaks(session, record)
        contradictions += count_contradictions(session, record)
    return {
        "session_id": session.session_id,
        "knowledge_leaks": leaks,
        "contradictions": contradictions,
        "generations_checked": len(session.generations),
    }


def evaluate_batch(batch_id: str, sessions: list[SessionLog]) -> dict[str, Any]:
    session_results = [evaluate_session(session) for session in sessions]
    generations_checked = sum(r["generations_checked"] for r in session_results)
    total_leaks = sum(r["knowledge_leaks"] for r in session_results)
    return {
        "batch_id": batch_id,
        "notes": REPORT_NOTES,
        "sessions": session_results,
        "aggregate": {
            "knowledge_leak_rate": (
                total_leaks / generations_checked if generations_checked else 0.0
            ),
            "contradiction_count": sum(r["contradictions"] for r in session_results),
        },
    }


def load_thresholds(path: Path = THRESHOLDS_PATH) -> dict[str, float]:
    return json.loads(path.read_text(encoding="utf-8"))


def batch_passes_thresholds(
    report: dict[str, Any], thresholds: dict[str, float]
) -> bool:
    aggregate = report["aggregate"]
    return (
        aggregate["knowledge_leak_rate"] <= thresholds["knowledge_leak_rate_max"]
        and aggregate["contradiction_count"] <= thresholds["contradiction_count_max"]
    )


def write_report(report: dict[str, Any]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Synthetic session batch
#
# Deterministic (seeded) sessions shaped like real session logs: characters
# hold some facts, lack others, and every generation is composed from the
# facts the character actually knows — unless a defect is injected.
# ---------------------------------------------------------------------------

_FACT_POOL = [
    ("timeline", {"detail": "the study door was locked from inside"}),
    ("motive", {"detail": "the victim rewrote the will last week"}),
    ("alibi", {"detail": "the gardener was in the greenhouse at nine"}),
    ("weapon", {"detail": "the letter opener is missing from the desk"}),
    ("secret", {"detail": "two guests arrived together but claim otherwise"}),
    ("observation", {"detail": "muddy footprints stop at the library window"}),
]


def build_synthetic_session(
    seed: int,
    *,
    inject_leak: bool = False,
    inject_contradiction: bool = False,
) -> SessionLog:
    rng = random.Random(seed)
    fact_content_by_id = {
        f"fact-{index}": {"fact_type": fact_type, "content": content}
        for index, (fact_type, content) in enumerate(_FACT_POOL)
    }
    fact_ids = list(fact_content_by_id)
    session = SessionLog(
        session_id=f"synthetic-{seed}",
        fact_content_by_id=fact_content_by_id,
    )

    for character_index in range(3):
        shuffled = fact_ids.copy()
        rng.shuffle(shuffled)
        known = tuple(shuffled[:3])
        unknown = tuple(shuffled[3:5])
        revoked = tuple(shuffled[5:])

        known_detail = fact_content_by_id[known[0]]["content"]["detail"]
        content_text = f"As I said before, {known_detail}, and I stand by it."
        session.generations.append(
            GenerationRecord(
                character_id=f"char-{character_index}",
                content_text=content_text,
                known_fact_ids=known,
                unknown_fact_ids=unknown,
                revoked_fact_ids=revoked,
            )
        )

    if inject_leak:
        # A character states the payload of a fact outside its knowledge state.
        target = session.generations[0]
        leaked_detail = fact_content_by_id[target.unknown_fact_ids[0]]["content"][
            "detail"
        ]
        session.generations[0] = GenerationRecord(
            character_id=target.character_id,
            content_text=f"Everyone should know that {leaked_detail}.",
            known_fact_ids=target.known_fact_ids,
            unknown_fact_ids=target.unknown_fact_ids,
            revoked_fact_ids=target.revoked_fact_ids,
        )

    if inject_contradiction:
        # A character repeats a fact it holds with a superseding revocation.
        target = session.generations[1]
        revoked_detail = fact_content_by_id[target.revoked_fact_ids[0]]["content"][
            "detail"
        ]
        session.generations[1] = GenerationRecord(
            character_id=target.character_id,
            content_text=f"I am certain {revoked_detail}, nothing has changed.",
            known_fact_ids=target.known_fact_ids,
            unknown_fact_ids=target.unknown_fact_ids,
            revoked_fact_ids=target.revoked_fact_ids,
        )

    return session


# ---------------------------------------------------------------------------
# Eval tests (acceptance criteria, spec 0066)
# ---------------------------------------------------------------------------


def test_seeded_leak_is_detected() -> None:
    """True-positive: a deliberate injected leak is counted."""
    session = build_synthetic_session(7, inject_leak=True)
    result = evaluate_session(session)
    assert result["knowledge_leaks"] >= 1


def test_seeded_contradiction_is_detected() -> None:
    """True-positive: a repeated revoked fact counts as a contradiction."""
    session = build_synthetic_session(7, inject_contradiction=True)
    result = evaluate_session(session)
    assert result["contradictions"] >= 1


def test_clean_session_reports_zero() -> None:
    """False-positive guard: clean sessions report no leaks or contradictions."""
    for seed in range(5):
        result = evaluate_session(build_synthetic_session(seed))
        assert result["knowledge_leaks"] == 0
        assert result["contradictions"] == 0
        assert result["generations_checked"] == 3


def test_batch_aggregation_and_report() -> None:
    """Batch over 10 synthetic sessions produces the spec report and passes."""
    sessions = [build_synthetic_session(seed) for seed in range(10)]
    report = evaluate_batch("synthetic-clean-batch", sessions)

    assert len(report["sessions"]) == 10
    assert report["aggregate"]["knowledge_leak_rate"] == 0.0
    assert report["aggregate"]["contradiction_count"] == 0
    assert set(report["sessions"][0]) == {
        "session_id",
        "knowledge_leaks",
        "contradictions",
        "generations_checked",
    }

    thresholds = load_thresholds()
    assert batch_passes_thresholds(report, thresholds)

    write_report(report)
    written = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    assert written["batch_id"] == "synthetic-clean-batch"
    assert "notes" in written


def test_defective_batch_fails_default_thresholds() -> None:
    """A batch containing an injected leak fails the shipped thresholds."""
    sessions = [build_synthetic_session(seed) for seed in range(9)]
    sessions.append(build_synthetic_session(99, inject_leak=True))
    report = evaluate_batch("synthetic-defect-batch", sessions)

    assert report["aggregate"]["knowledge_leak_rate"] > 0.0
    assert not batch_passes_thresholds(report, load_thresholds())


def test_thresholds_configurable_without_code_changes(tmp_path: Path) -> None:
    """Loosening the thresholds file flips the verdict with no code change."""
    sessions = [build_synthetic_session(99, inject_leak=True)]
    report = evaluate_batch("synthetic-lenient-batch", sessions)
    assert not batch_passes_thresholds(report, load_thresholds())

    lenient = tmp_path / "thresholds.json"
    lenient.write_text(
        json.dumps({"knowledge_leak_rate_max": 1.0, "contradiction_count_max": 100}),
        encoding="utf-8",
    )
    assert batch_passes_thresholds(report, load_thresholds(lenient))
