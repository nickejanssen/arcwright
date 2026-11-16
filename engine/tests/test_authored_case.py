"""Written case format, fairness check and holdings (AW-324, spec 0093 A and B).

Uses only the made-up case in ``fixtures/authored_case/valid_case.json``. No
real case file is read. Database tests run on in-memory SQLite and no model
is involved anywhere.
"""

from __future__ import annotations

import copy
import json
import re
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.arc.models import ArcDefinition
from engine.arc.registry import load_arc_definition
from engine.case.authored import (
    RULE_NAMES,
    AuthoredCaseRefused,
    check_authored_case_file,
    check_case,
    full_report,
    load_authored_case,
    parse_authored_case,
    summary_report,
)
from engine.case.authored import __main__ as authored_cli
from engine.db.orm import Character, Event, Fact, KnowledgeState
from engine.db.testing import make_sqlite_session_factory
from engine.knowledge.graph import (
    assert_knowledge,
    get_character_knowledge,
    revoke_fact_in_session,
)
from engine.knowledge.holdings import CONCEPT_FACT_TYPE, concepts_held, grant_concept
from engine.session import case_seating
from engine.session.case_seating import CAST_SEATED_EVENT
from engine.session.service import SessionService, SessionStateError

ENGINE_DIR = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "authored_case"
VALID_CASE = FIXTURES / "valid_case.json"
BEATS = ["opening", "beat_one", "beat_two", "beat_three", "finale"]
LEDGER_TEXT = "The ledger shows a crate signed out at nine."

Raw = dict[str, Any]


def valid_raw() -> Raw:
    return json.loads(VALID_CASE.read_text(encoding="utf-8"))


def run_check(raw: Raw, budget: int = 6) -> Any:
    return check_case(parse_authored_case(raw), beat_order=BEATS, budget=budget)


def failed_rules(check: Any) -> list[str]:
    return [o.rule for o in check.outcomes if o.status == "fail"]


def find(raw: Raw, section: str, key: str, value: str) -> Raw:
    return next(item for item in raw[section] if item[key] == value)


# --- Each way to break the case, in exactly one way ---------------------------


def a1_duplicate_id(raw: Raw) -> None:
    raw["concepts"].append(copy.deepcopy(raw["concepts"][0]))


def a1_unknown_concept(raw: Raw) -> None:
    find(raw, "opportunities", "opportunity_id", "o_bench")["gives"].append("c_nope")


def a1_unknown_beat(raw: Raw) -> None:
    find(raw, "opportunities", "opportunity_id", "o_bench")["beats"] = ["beat_nope"]


def a1_unknown_answer(raw: Raw) -> None:
    raw["solution"][0]["accepted"][0]["value"] = "nobody"


def a2_one_route(raw: Raw) -> None:
    find(raw, "essential_truths", "truth_id", "t_how")["routes"].pop()


def a2_single_opportunity_on_every_route(raw: Raw) -> None:
    find(raw, "essential_truths", "truth_id", "t_who")["routes"][1]["concepts"] = [
        "c_ledger",
        "c_witness",
    ]


def a3_order_makes_it_unsolvable(raw: Raw) -> None:
    find(raw, "opportunities", "opportunity_id", "o_cellar")["beats"] = ["beat_one"]


def a4_nothing_exposes(raw: Raw) -> None:
    raw["deceptions"] = [
        d for d in raw["deceptions"] if d["concept_id"] != "c_how_false1"
    ]


def a4_exposer_unobtainable(raw: Raw) -> None:
    find(raw, "deceptions", "concept_id", "c_how_false1")["exposed_by"] = ["c_orphan"]


def a5_never_available(raw: Raw) -> None:
    raw["opportunities"].append(
        {
            "opportunity_id": "o_dead",
            "subject_id": "s_shed",
            "label": "Dead end",
            "content": "Never reachable.",
            "beats": ["beat_two"],
            "requires": ["c_orphan"],
            "cost": 1,
            "gives": ["c_note"],
        }
    )


def a5_thin_beat(raw: Raw) -> None:
    find(raw, "opportunities", "opportunity_id", "o_porter")["beats"] = [
        "beat_one",
        "beat_two",
    ]


def a6_answer_unobtainable(raw: Raw) -> None:
    raw["solution"][0]["accepted"].append({"value": "marlowe", "needs": ["c_orphan"]})


def a6_slot_too_easy(raw: Raw) -> None:
    find(raw, "cast", "cast_id", "quillby")["nameable"] = False


def a6_accepted_cast_not_selectable(raw: Raw) -> None:
    find(raw, "cast", "cast_id", "marlowe")["nameable"] = False


BREAKS: list[tuple[str, str, Callable[[Raw], None]]] = [
    ("A1", "duplicate_id", a1_duplicate_id),
    ("A1", "unknown_concept", a1_unknown_concept),
    ("A1", "unknown_beat", a1_unknown_beat),
    ("A1", "unknown_answer", a1_unknown_answer),
    ("A2", "one_route", a2_one_route),
    ("A2", "single_opportunity", a2_single_opportunity_on_every_route),
    ("A3", "order_makes_unsolvable", a3_order_makes_it_unsolvable),
    ("A4", "nothing_exposes", a4_nothing_exposes),
    ("A4", "exposer_unobtainable", a4_exposer_unobtainable),
    ("A5", "never_available", a5_never_available),
    ("A5", "thin_beat", a5_thin_beat),
    ("A6", "answer_unobtainable", a6_answer_unobtainable),
    ("A6", "slot_too_easy", a6_slot_too_easy),
    ("A6", "accepted_cast_not_selectable", a6_accepted_cast_not_selectable),
]
BREAK_IDS = [f"{rule}-{name}" for rule, name, _ in BREAKS]


# --- Part A: format, rules, reports --------------------------------------------


class TestValidCase:
    def test_valid_case_passes_every_rule_at_two_three_and_four_players(self) -> None:
        check = run_check(valid_raw())
        assert check.passed
        assert [o.status for o in check.outcomes] == ["pass"] * 6
        assert check.participant_counts == (2, 3, 4)

    def test_fewest_paid_choices_is_found_by_search(self) -> None:
        assert run_check(valid_raw()).min_paid_choices == 4

    def test_loading_the_same_file_twice_gives_equal_objects(self) -> None:
        first = load_authored_case(VALID_CASE, beat_order=BEATS)
        second = load_authored_case(VALID_CASE, beat_order=BEATS)
        assert first == second
        assert first is not second

    def test_every_rule_has_a_name(self) -> None:
        assert sorted(RULE_NAMES) == ["A0", "A1", "A2", "A3", "A4", "A5", "A6"]
        assert len(set(RULE_NAMES.values())) == 7


class TestRefusals:
    @pytest.mark.parametrize(("rule", "name", "mutate"), BREAKS, ids=BREAK_IDS)
    def test_each_broken_case_is_refused_with_that_rules_name(
        self, rule: str, name: str, mutate: Callable[[Raw], None], tmp_path: Path
    ) -> None:
        raw = valid_raw()
        mutate(raw)
        path = tmp_path / "case.json"
        path.write_text(json.dumps(raw), encoding="utf-8")
        with pytest.raises(AuthoredCaseRefused) as caught:
            load_authored_case(path, beat_order=BEATS)
        assert caught.value.rule == rule
        assert str(caught.value) == RULE_NAMES[rule]

    @pytest.mark.parametrize(("rule", "name", "mutate"), BREAKS, ids=BREAK_IDS)
    def test_only_the_intended_rule_fails(
        self, rule: str, name: str, mutate: Callable[[Raw], None]
    ) -> None:
        raw = valid_raw()
        mutate(raw)
        failures = failed_rules(run_check(raw))
        if name == "order_makes_unsolvable":
            assert failures[0] == rule
        else:
            assert failures == [rule]

    def test_true_concepts_count_as_wrong_answers_for_a_concept_slot(self) -> None:
        """A player may pick any concept they hold, so a true concept that is
        not the accepted answer is a wrong answer (spec 0094)."""
        raw = valid_raw()
        for concept in raw["concepts"]:
            concept["standing"] = "true"
        raw["deceptions"] = []
        assert run_check(raw).passed

    def test_a3_refuses_when_the_budget_is_too_small(self) -> None:
        assert run_check(valid_raw(), budget=4).passed
        check = run_check(valid_raw(), budget=3)
        assert failed_rules(check) == ["A3"]
        assert check.min_paid_choices is None

    def test_a3_problem_names_the_cost_for_the_author(self) -> None:
        check = run_check(valid_raw(), budget=3)
        a3 = next(o for o in check.outcomes if o.rule == "A3")
        assert a3.problem_count == 3
        assert "needs 4 paid choices, budget is 3" in a3.problems[0]

    def test_when_a1_fails_the_later_rules_are_not_run(self) -> None:
        raw = valid_raw()
        a1_duplicate_id(raw)
        check = run_check(raw)
        assert [o.status for o in check.outcomes][:2] == ["fail", "not_run"]
        assert {o.status for o in check.outcomes[1:]} == {"not_run"}

    def test_malformed_files_are_refused_by_name(self, tmp_path: Path) -> None:
        no_first = valid_raw()
        no_first["solution"][0]["shown_first"] = False
        missing = valid_raw()
        del missing["title"]
        cast_without_needs = valid_raw()
        cast_without_needs["solution"][0]["accepted"][0]["needs"] = []
        for index, raw in enumerate([no_first, missing, cast_without_needs]):
            with pytest.raises(AuthoredCaseRefused) as caught:
                parse_authored_case(raw)
            assert str(caught.value) == "malformed_file", index
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("{not json", encoding="utf-8")
        case, check = check_authored_case_file(bad_json, beat_order=BEATS)
        assert case is None
        assert failed_rules(check) == ["A0"]

    def test_malformed_report_never_carries_the_offending_value(self) -> None:
        raw = valid_raw()
        raw["format_version"] = "secret-version-text"
        with pytest.raises(AuthoredCaseRefused) as caught:
            parse_authored_case(raw)
        text = full_report(caught.value.check)
        assert "secret-version-text" not in text
        assert "format_version" in text


def _strings(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, dict):
        return {s for v in value.values() for s in _strings(v)}
    if isinstance(value, list):
        return {s for v in value for s in _strings(v)}
    return set()


class TestReports:
    @pytest.mark.parametrize(("rule", "name", "mutate"), BREAKS, ids=BREAK_IDS)
    def test_summary_prints_nothing_from_the_case_file(
        self, rule: str, name: str, mutate: Callable[[Raw], None]
    ) -> None:
        raw = valid_raw()
        mutate(raw)
        output = summary_report(run_check(raw))
        leaked = [s for s in _strings(raw) if len(s) > 2 and s in output]
        assert leaked == []
        assert RULE_NAMES[rule] in output
        assert "FAIL" in output

    def test_summary_for_the_valid_case_prints_nothing_from_the_case_file(self) -> None:
        raw = valid_raw()
        output = summary_report(run_check(raw))
        assert [s for s in _strings(raw) if len(s) > 2 and s in output] == []
        assert "Result: PASS" in output
        assert "Participant counts checked: 2, 3, 4" in output

    def test_summary_holds_names_pass_fail_and_counts(self) -> None:
        output = summary_report(run_check(valid_raw()))
        for rule, name in RULE_NAMES.items():
            if rule != "A0":
                assert f"{rule} {name}: PASS (checked" in output
        assert "problems 0)" in output

    def test_full_report_names_ids_for_the_author(self) -> None:
        raw = valid_raw()
        a1_unknown_concept(raw)
        check = run_check(raw)
        assert "c_nope" in full_report(check)
        assert "c_nope" not in summary_report(check)

    def test_command_line_prints_the_summary_by_default(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        arc = fixture_arc(VALID_CASE)
        monkeypatch.setattr(authored_cli, "load_arc_definition", lambda _id: arc)
        assert authored_cli.main([str(VALID_CASE), "--arc-id", "x"]) == 0
        out = capsys.readouterr().out
        assert "Result: PASS" in out
        assert "c_ledger" not in out
        assert authored_cli.main([str(VALID_CASE), "--arc-id", "x", "--full"]) == 0


# --- A made-up arc: the real couch-race file with its beats replaced -------------


def fixture_arc(case_path: Path | None) -> ArcDefinition:
    couch = ArcDefinition.model_validate_json(
        (ENGINE_DIR.parent / "nightcap" / "couch-race.arc.json").read_text("utf-8")
    )
    template = couch.beats[0].model_copy(
        update={
            "mini_games": None,
            "interaction_ids": [],
            "authored_content": None,
            "exit_conditions": [],
            "entry_conditions": [],
        }
    )
    beats = [template.model_copy(update={"beat_id": b, "beat_name": b}) for b in BEATS]
    graph = {a: [b] for a, b in zip(BEATS, BEATS[1:])} | {BEATS[-1]: []}
    return couch.model_copy(
        update={
            "arc_id": "fixture-arc-v1",
            "beats": beats,
            "beat_graph": graph,
            "interactions": [],
            "resource_effects": [],
            "obligations": [],
            "authorial_intent": None,
            "case_file": str(case_path) if case_path else None,
        }
    )


# --- Part B: what each participant holds ----------------------------------------


@pytest_asyncio.fixture()
async def db() -> AsyncIterator[AsyncSession]:
    engine, factory = await make_sqlite_session_factory()
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
    await engine.dispose()


async def make_session(db: AsyncSession, arc: ArcDefinition, players: int = 2) -> Any:
    svc = SessionService()
    created, _ = await svc.create_session(
        db, arc_id=arc.arc_id, host_account_id=uuid4()
    )
    characters: list[UUID] = []
    for _ in range(players):
        participant, _ = await svc.add_player(db, created.session_id)
        characters.append(participant.character_id)
    return svc, created.session_id, characters


@pytest.fixture()
def patched_arc(monkeypatch: pytest.MonkeyPatch) -> ArcDefinition:
    arc = fixture_arc(VALID_CASE)
    monkeypatch.setattr("engine.session.service.load_arc_definition", lambda _id: arc)
    return arc


class TestHoldings:
    @pytest.mark.asyncio
    async def test_a_granted_concept_is_held_by_that_participant_only(
        self, db: AsyncSession, patched_arc: ArcDefinition
    ) -> None:
        _, session_id, (alice, bob) = await make_session(db, patched_arc)
        assert await grant_concept(
            db,
            session_id=session_id,
            character_id=alice,
            concept_id="c_ledger",
            text=LEDGER_TEXT,
        )
        held_alice = await concepts_held(db, session_id=session_id, character_id=alice)
        held_bob = await concepts_held(db, session_id=session_id, character_id=bob)
        assert held_alice == {"c_ledger"}
        assert held_bob == frozenset()

    @pytest.mark.asyncio
    async def test_granting_twice_saves_nothing_the_second_time(
        self, db: AsyncSession, patched_arc: ArcDefinition
    ) -> None:
        _, session_id, (alice, _) = await make_session(db, patched_arc)
        assert await grant_concept(
            db,
            session_id=session_id,
            character_id=alice,
            concept_id="c_ledger",
            text=LEDGER_TEXT,
        )
        assert not await grant_concept(
            db,
            session_id=session_id,
            character_id=alice,
            concept_id="c_ledger",
            text=LEDGER_TEXT,
        )
        rows = await db.scalar(
            select(func.count())
            .select_from(KnowledgeState)
            .where(KnowledgeState.character_id == alice)
        )
        assert rows == 1

    @pytest.mark.asyncio
    async def test_a_concept_only_heard_is_not_held(
        self, db: AsyncSession, patched_arc: ArcDefinition
    ) -> None:
        _, session_id, (alice, bob) = await make_session(db, patched_arc)
        await grant_concept(
            db,
            session_id=session_id,
            character_id=alice,
            concept_id="c_ledger",
            text=LEDGER_TEXT,
        )
        await assert_knowledge(
            db,
            session_id=session_id,
            character_id=bob,
            fact_type=CONCEPT_FACT_TYPE,
            fact_content={"concept_id": "c_ledger", "text": LEDGER_TEXT},
            source_character_id=alice,
        )
        assert (
            await concepts_held(db, session_id=session_id, character_id=bob)
            == frozenset()
        )
        assert await concepts_held(db, session_id=session_id, character_id=alice) == {
            "c_ledger"
        }

    @pytest.mark.asyncio
    async def test_hearing_then_finding_it_yourself_counts_as_held(
        self, db: AsyncSession, patched_arc: ArcDefinition
    ) -> None:
        _, session_id, (alice, bob) = await make_session(db, patched_arc)
        await grant_concept(
            db,
            session_id=session_id,
            character_id=alice,
            concept_id="c_ledger",
            text=LEDGER_TEXT,
        )
        await assert_knowledge(
            db,
            session_id=session_id,
            character_id=bob,
            fact_type=CONCEPT_FACT_TYPE,
            fact_content={"concept_id": "c_ledger", "text": LEDGER_TEXT},
            source_character_id=alice,
        )
        assert await grant_concept(
            db,
            session_id=session_id,
            character_id=bob,
            concept_id="c_ledger",
            text=LEDGER_TEXT,
        )
        assert await concepts_held(db, session_id=session_id, character_id=bob) == {
            "c_ledger"
        }

    @pytest.mark.asyncio
    async def test_a_revoked_concept_is_no_longer_held(
        self, db: AsyncSession, patched_arc: ArcDefinition
    ) -> None:
        _, session_id, (alice, _) = await make_session(db, patched_arc)
        await grant_concept(
            db,
            session_id=session_id,
            character_id=alice,
            concept_id="c_ledger",
            text=LEDGER_TEXT,
        )
        fact_id = await db.scalar(select(Fact.fact_id))
        assert fact_id is not None
        await revoke_fact_in_session(db, session_id=session_id, fact_id=fact_id)
        assert (
            await concepts_held(db, session_id=session_id, character_id=alice)
            == frozenset()
        )

    @pytest.mark.asyncio
    async def test_reading_holdings_writes_no_event(
        self, db: AsyncSession, patched_arc: ArcDefinition
    ) -> None:
        _, session_id, (alice, _) = await make_session(db, patched_arc)
        before = await db.scalar(select(func.count()).select_from(Event))
        await concepts_held(db, session_id=session_id, character_id=alice)
        assert await db.scalar(select(func.count()).select_from(Event)) == before


class TestSessionStart:
    @pytest.mark.asyncio
    async def test_cast_knowledge_is_saved_into_the_graph_at_start(
        self, db: AsyncSession, patched_arc: ArcDefinition
    ) -> None:
        svc, session_id, _ = await make_session(db, patched_arc)
        await svc.start_session(db, session_id)
        payload = await db.scalar(
            select(Event.payload).where(Event.event_type == CAST_SEATED_EVENT)
        )
        assert payload is not None
        raw = valid_raw()
        for cast in raw["cast"]:
            character_id = UUID(payload["cast"][cast["cast_id"]])
            states = await get_character_knowledge(
                db, session_id=session_id, character_id=character_id
            )
            saved = {ks.fact.fact_content["concept_id"] for ks in states}
            assert saved == set(cast["knows"])
            # Generation copies fact content as it is, so the written text
            # must travel with the ID.
            texts = {c["concept_id"]: c["text"] for c in raw["concepts"]}
            for ks in states:
                content = ks.fact.fact_content
                assert content["text"] == texts[content["concept_id"]]
            profile = await db.scalar(
                select(Character.behavior_profile).where(
                    Character.character_id == character_id
                )
            )
            assert profile is not None
            assert profile["case_cast_id"] == cast["cast_id"]

    @pytest.mark.asyncio
    async def test_every_participant_is_given_the_opening_but_the_host_is_not(
        self, db: AsyncSession, patched_arc: ArcDefinition
    ) -> None:
        svc, session_id, players = await make_session(db, patched_arc, players=3)
        await svc.start_session(db, session_id)
        for character_id in players:
            held = await concepts_held(
                db, session_id=session_id, character_id=character_id
            )
            assert held == set(valid_raw()["opening"])
        participants = await svc.list_participants(db, session_id)
        host = next(p for p in participants if p.surface_type == "host")
        assert (
            await concepts_held(
                db, session_id=session_id, character_id=host.character_id
            )
            == frozenset()
        )

    @pytest.mark.asyncio
    async def test_seating_twice_changes_nothing(
        self, db: AsyncSession, patched_arc: ArcDefinition
    ) -> None:
        svc, session_id, _ = await make_session(db, patched_arc)
        await svc.start_session(db, session_id)
        case = load_authored_case(VALID_CASE, beat_order=BEATS)

        async def totals() -> tuple[int, int, int]:
            return (
                await db.scalar(select(func.count()).select_from(Character)) or 0,
                await db.scalar(select(func.count()).select_from(KnowledgeState)) or 0,
                await db.scalar(select(func.count()).select_from(Event)) or 0,
            )

        before = await totals()
        await case_seating.seat_authored_case(db, session_id=session_id, case=case)
        assert await totals() == before

    @pytest.mark.asyncio
    async def test_an_arc_with_no_case_file_starts_as_before(
        self, db: AsyncSession, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        arc = fixture_arc(None)
        monkeypatch.setattr(
            "engine.session.service.load_arc_definition", lambda _id: arc
        )
        svc, session_id, players = await make_session(db, arc)
        await svc.start_session(db, session_id)
        assert await db.scalar(select(func.count()).select_from(KnowledgeState)) == 0
        assert (
            await concepts_held(db, session_id=session_id, character_id=players[0])
            == frozenset()
        )

    @pytest.mark.asyncio
    async def test_an_unfair_case_stops_the_session_from_starting(
        self,
        db: AsyncSession,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        raw = valid_raw()
        a2_one_route(raw)
        path = tmp_path / "unfair.json"
        path.write_text(json.dumps(raw), encoding="utf-8")
        arc = fixture_arc(path)
        monkeypatch.setattr(
            "engine.session.service.load_arc_definition", lambda _id: arc
        )
        svc, session_id, _ = await make_session(db, arc)
        with pytest.raises(SessionStateError, match="truth_not_redundant"):
            await svc.start_session(db, session_id)


# --- Guards -----------------------------------------------------------------------


class TestGuards:
    def test_both_registered_arc_files_still_load_with_no_case_file(self) -> None:
        for arc_id in ("nightcap-v1", "nightcap-couch-race-v1"):
            arc = load_arc_definition(arc_id)
            assert arc is not None
            assert arc.case_file is None

    def test_new_engine_code_uses_no_game_word_and_calls_no_model(self) -> None:
        files = [
            *sorted((ENGINE_DIR / "case" / "authored").glob("*.py")),
            ENGINE_DIR / "knowledge" / "holdings.py",
            ENGINE_DIR / "session" / "case_seating.py",
        ]
        words = re.compile(
            r"suspect|accusation|killer|murder|detective|culprit|clue|victim"
            r"|contradiction|interrogation|nightcap|\bround",
            re.IGNORECASE,
        )
        model_use = re.compile(r"engine\.routing|litellm|anthropic|groq", re.IGNORECASE)
        for path in files:
            text = path.read_text(encoding="utf-8")
            assert words.findall(text) == [], path.name
            assert model_use.findall(text) == [], path.name
