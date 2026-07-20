import pytest

from engine.scoring.calculator import (
    accusation_base_value,
    chain_reaction_countdown,
    evidence_points,
    momentum_multiplier,
    motive_method_bonus,
    wrong_accusation_cost,
)


def test_evidence_points():
    assert evidence_points(4) == 40
    assert evidence_points(0) == 0


@pytest.mark.parametrize(
    "catches,expected",
    [(0, 0.0), (1, 0.10), (2, 0.20), (3, 0.30), (4, 0.40), (5, 0.50), (9, 0.50)],
)
def test_momentum_multiplier(catches, expected):
    assert momentum_multiplier(catches) == expected


def test_accusation_base_value_anchors():
    assert accusation_base_value("grill", beat_progress_fraction=0.0) == 200
    assert accusation_base_value("last_call", beat_progress_fraction=1.0) == 60


def test_accusation_base_value_interpolates_not_steps():
    value = accusation_base_value("twist", beat_progress_fraction=0.5)
    assert 125 <= value <= 135


def test_motive_method_bonus():
    assert motive_method_bonus(motive_correct=True, method_correct=True) == 50
    assert motive_method_bonus(motive_correct=True, method_correct=False) == 25
    assert motive_method_bonus(motive_correct=False, method_correct=False) == 0


def test_wrong_accusation_cost_grill_first_offense():
    lockout_rounds, penalty = wrong_accusation_cost("grill", repeat_offense_count=0)
    assert lockout_rounds == 1
    assert penalty == -20


def test_wrong_accusation_cost_escalates_on_repeat():
    _, first_penalty = wrong_accusation_cost("twist", repeat_offense_count=0)
    _, second_penalty = wrong_accusation_cost("twist", repeat_offense_count=1)
    assert first_penalty == -40
    assert second_penalty == -60


def test_chain_reaction_countdown_compounds_and_floors():
    after_first = chain_reaction_countdown(
        remaining_seconds=100, additional_correct_count=1
    )
    after_second = chain_reaction_countdown(
        remaining_seconds=100, additional_correct_count=2
    )
    assert after_first == 80
    assert after_second == 64
    floored = chain_reaction_countdown(
        remaining_seconds=100, additional_correct_count=10
    )
    assert floored == 30


def test_scenario_a_careful_detective():
    evidence = evidence_points(4)
    catches = 3 * 50
    momentum = momentum_multiplier(3)
    accusation = accusation_base_value("twist", beat_progress_fraction=0.5)
    bonus = motive_method_bonus(motive_correct=True, method_correct=False)
    accusation_total = round(accusation * (1 + momentum)) + bonus
    assert evidence == 40
    assert catches == 150
    assert accusation_total == 194
    assert evidence + catches + accusation_total == 384


def test_scenario_b_lucky_early_guesser():
    evidence = evidence_points(1)
    catches = 0 * 50
    momentum = momentum_multiplier(0)
    accusation = accusation_base_value("grill", beat_progress_fraction=0.0)
    accusation_total = round(accusation * (1 + momentum))
    assert evidence + catches + accusation_total == 210


def test_scenario_c_reckless_accuser():
    evidence = evidence_points(2)
    _, wrong1_penalty = wrong_accusation_cost("grill", repeat_offense_count=0)
    _, wrong2_penalty = wrong_accusation_cost("twist", repeat_offense_count=1)
    catches = 1 * 50
    momentum = momentum_multiplier(1)
    accusation = accusation_base_value("last_call", beat_progress_fraction=1.0)
    accusation_total = round(accusation * (1 + momentum))
    total = evidence + wrong1_penalty + wrong2_penalty + catches + accusation_total
    assert total == 56


def test_functions_are_pure_and_deterministic():
    a = accusation_base_value("twist", beat_progress_fraction=0.5)
    b = accusation_base_value("twist", beat_progress_fraction=0.5)
    assert a == b
