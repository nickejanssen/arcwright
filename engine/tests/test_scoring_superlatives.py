from datetime import datetime, timezone

from engine.scoring.models import AccusationAttempt, AccusationOutcome
from engine.scoring.superlatives import compute_superlatives


def _attempt(player_id: str, outcome: AccusationOutcome, points: int):
    return AccusationAttempt(
        session_id="session-1",
        accuser_participant_id=player_id,
        beat_id="grill",
        accused_cast_member_id="cast-1",
        outcome=outcome,
        catches_banked_at_submission=0,
        points_awarded=points,
    )


def test_superlatives_choose_clear_winners():
    result = compute_superlatives(
        [
            _attempt("p1", AccusationOutcome.correct, 200),
            _attempt("p2", AccusationOutcome.wrong, -40),
            _attempt("p2", AccusationOutcome.wrong, -60),
            _attempt("p3", AccusationOutcome.wrong, -20),
        ],
        confirmed_catches_by_player={
            "p1": [datetime(2026, 7, 19, 12, 5, tzinfo=timezone.utc)] * 3,
            "p2": [datetime(2026, 7, 19, 12, 6, tzinfo=timezone.utc)] * 2,
            "p3": [],
        },
        evidence_by_player={"p1": 4, "p2": 1, "p3": 1},
    )

    assert result == {
        "best_interrogator": "p1",
        "lie_detector": "p1",
        "most_confidently_wrong": "p2",
    }


def test_lie_detector_tie_breaks_by_earliest_catch():
    result = compute_superlatives(
        [],
        confirmed_catches_by_player={
            "p1": [datetime(2026, 7, 19, 12, 5, tzinfo=timezone.utc)] * 2,
            "p2": [datetime(2026, 7, 19, 12, 4, tzinfo=timezone.utc)] * 2,
        },
        evidence_by_player={"p1": 0, "p2": 0},
    )

    assert result["lie_detector"] == "p2"


def test_most_confidently_wrong_tie_breaks_by_penalty_then_id():
    accusations = [
        _attempt("p1", AccusationOutcome.wrong, -20),
        _attempt("p1", AccusationOutcome.wrong, -20),
        _attempt("p2", AccusationOutcome.wrong, -60),
        _attempt("p2", AccusationOutcome.wrong, -40),
    ]
    result = compute_superlatives(
        accusations,
        confirmed_catches_by_player={},
        evidence_by_player={"p1": 0, "p2": 0},
    )

    assert result["most_confidently_wrong"] == "p2"


def test_superlatives_are_reproducible():
    inputs = (
        [_attempt("p1", AccusationOutcome.wrong, -20)],
        {"p1": 1, "p2": 0},
        {"p1": 2, "p2": 5},
    )

    assert compute_superlatives(*inputs) == compute_superlatives(*inputs)
