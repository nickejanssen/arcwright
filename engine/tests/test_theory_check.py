"""The theory check (AW-326, spec 0094 Part H), the account text (D-138) and the
winner rule (Part I).

All are pure: no database, clock, router or order of arrival is needed to call
them. Uses only made-up IDs and the made-up fixture case.
"""

from __future__ import annotations

import inspect
import json
import random
from pathlib import Path
from typing import Any

import pytest

from engine.case.authored import (
    AuthoredCase,
    check_theories,
    parse_authored_case,
    split_account,
)
from engine.case.authored.rules import AuthoredCaseRefused
from engine.session.winner import decide_winners, placing, run_winners

VALID = Path(__file__).parent / "fixtures/authored_case/valid_case.json"
RIGHT = {"slot_who": "marlowe", "slot_how": "c_how_true"}


def case_data() -> dict[str, Any]:
    return json.loads(VALID.read_text("utf-8"))


def case() -> AuthoredCase:
    return parse_authored_case(case_data())


def standing(*tiers: list[str]) -> list[list[str]]:
    return [list(t) for t in tiers]


class TestTheoryCheck:
    def test_every_slot_right_solves_the_case(self) -> None:
        result = check_theories(case().solution, {"p1": RIGHT})["p1"]
        assert result.solved
        assert result.slots == (("slot_who", True), ("slot_how", True))

    def test_each_slot_is_judged_on_its_own(self) -> None:
        wrong_how = {"slot_who": "marlowe", "slot_how": "c_how_false1"}
        result = check_theories(case().solution, {"p1": wrong_how})["p1"]
        assert not result.solved
        assert result.slots == (("slot_who", True), ("slot_how", False))

    def test_a_player_with_no_theory_is_wrong_everywhere(self) -> None:
        result = check_theories(case().solution, {"p1": None})["p1"]
        assert not result.solved
        assert result.slots == (("slot_who", False), ("slot_how", False))

    def test_an_empty_slot_is_wrong(self) -> None:
        result = check_theories(case().solution, {"p1": {"slot_who": "marlowe"}})["p1"]
        assert not result.solved
        assert dict(result.slots)["slot_how"] is False

    def test_it_judges_every_player_in_one_call(self) -> None:
        results = check_theories(
            case().solution, {"p1": RIGHT, "p2": None, "p3": {"slot_who": "pinecone"}}
        )
        assert {p: r.solved for p, r in results.items()} == {
            "p1": True,
            "p2": False,
            "p3": False,
        }

    def test_same_inputs_give_equal_results_over_generated_theories(self) -> None:
        solution = case().solution
        rng = random.Random(326)
        pool = ["marlowe", "pinecone", "quillby", "c_how_true", "c_how_false1", ""]
        for _ in range(300):
            theories: dict[str, dict[str, str] | None] = {}
            for player in range(rng.randint(1, 6)):
                if rng.random() < 0.2:
                    theories[f"p{player}"] = None
                else:
                    theories[f"p{player}"] = {
                        slot.slot_id: rng.choice(pool)
                        for slot in solution
                        if rng.random() < 0.8
                    }
            first = check_theories(solution, theories)
            reversed_input = dict(reversed(list(theories.items())))
            assert first == check_theories(solution, theories)
            assert first == check_theories(solution, reversed_input)
            for player, answers in theories.items():
                want = answers is not None and all(
                    answers.get(s.slot_id) in {a.value for a in s.accepted}
                    for s in solution
                )
                assert first[player].solved is want

    def test_it_takes_nothing_but_the_slots_and_the_theories(self) -> None:
        assert list(inspect.signature(check_theories).parameters) == [
            "solution",
            "theories",
        ]


class TestAccountText:
    def test_the_account_is_optional(self) -> None:
        assert case().account is None

    def test_one_blank_per_slot_in_order_is_accepted(self) -> None:
        data = case_data() | {"account": "{slot_who} did it, by {slot_how}."}
        assert split_account(parse_authored_case(data).account or "") == [
            ("", "slot_who"),
            (" did it, by ", None),
            ("", "slot_how"),
            (".", None),
        ]

    @pytest.mark.parametrize(
        "text",
        [
            "{slot_how} then {slot_who}.",
            "{slot_who} only.",
            "{slot_who} {slot_who} {slot_how}.",
            "{slot_who} and {slot_nope}.",
            "{slot_who} {slot_how} {",
            "no blanks at all",
        ],
    )
    def test_any_other_account_is_refused(self, text: str) -> None:
        with pytest.raises(AuthoredCaseRefused):
            parse_authored_case(case_data() | {"account": text})


class TestWinnerRule:
    def test_nobody_solved_it_means_no_winner(self) -> None:
        result = decide_winners([], [standing(["a"], ["b"])])
        assert result.winners == ()
        assert result.decided_by == "no_solver"

    def test_one_solver_wins_whatever_the_mini_games_said(self) -> None:
        result = decide_winners(["b"], [standing(["a"], ["b"])])
        assert (result.winners, result.decided_by) == (("b",), "only_solver")

    def test_two_solvers_are_split_by_mini_games_won(self) -> None:
        standings = [
            standing(["a"], ["b", "c"]),
            standing(["b"], ["a", "c"]),
            standing(["b"], ["a", "c"]),
        ]
        result = decide_winners(["a", "b"], standings)
        assert (result.winners, result.decided_by) == (("b",), "mini_game_wins")

    def test_two_solvers_level_on_wins_are_split_by_placings(self) -> None:
        # a and b each win one run. Placings: a 1+3+2+2 = 8, b 2+1+3+3 = 9.
        standings = [
            standing(["a"], ["b"], ["c"]),
            standing(["b"], ["c"], ["a"]),
            standing(["c"], ["a"], ["b"]),
            standing(["c"], ["a"], ["b"]),
        ]
        result = decide_winners(["a", "b"], standings)
        assert (result.winners, result.decided_by) == (("a",), "mini_game_placings")

    def test_two_solvers_level_on_both_share_the_win(self) -> None:
        standings = [standing(["a"], ["b"]), standing(["b"], ["a"])]
        result = decide_winners(["b", "a"], standings)
        assert (result.winners, result.decided_by) == (("a", "b"), "shared")

    def test_no_finished_runs_leaves_several_solvers_sharing(self) -> None:
        result = decide_winners(["a", "b"], [])
        assert (result.winners, result.decided_by) == (("a", "b"), "shared")

    def test_a_run_that_separated_nobody_is_won_by_nobody(self) -> None:
        assert run_winners([["a", "b", "c"]]) == []
        result = decide_winners(["a", "b"], [standing(["a", "b", "c"])])
        assert result.decided_by == "shared"

    def test_a_tied_top_tier_counts_a_win_for_each(self) -> None:
        assert run_winners([["a", "b"], ["c"]]) == ["a", "b"]

    def test_a_player_missing_from_a_run_is_placed_after_its_last_tier(self) -> None:
        assert placing([["a"], ["b"]], "z") == 3

    def test_no_input_is_a_time_or_an_order_of_arrival(self) -> None:
        parameters = inspect.signature(decide_winners).parameters
        assert list(parameters) == ["solvers", "standings"]
        standings = [standing(["b"], ["a", "c"])]
        assert decide_winners(["a", "b"], standings) == decide_winners(
            ["b", "a"], standings
        )
