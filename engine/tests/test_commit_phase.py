"""Last Call: the private theory form, drafts and the lock (AW-326, spec 0094 Part G).

Uses only the made-up case in ``fixtures/authored_case/valid_case.json``. Its
two solution slots are ``slot_who`` (a cast slot; ``marlowe`` is accepted) and
``slot_how`` (a concept slot; ``c_how_true`` is accepted; ``c_how_false1`` and
``c_how_false2`` are misleading). The arc's last beat is one ``commit`` phase.
No model is called.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
import pytest_asyncio
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.arc.models import ArcDefinition
from engine.db.orm import Decision
from engine.db.testing import make_sqlite_session_factory
from engine.events.models import AudienceTarget
from engine.knowledge.graph import assert_knowledge
from engine.knowledge.holdings import concepts_held, grant_concept
from engine.session import commit_phase
from engine.session.phases import (
    RoundError,
    current_phase,
    freeze_phase,
    host_move_on,
    lock_theory,
    mark_ready,
    read_theory_form,
    round_view,
    save_theory_draft,
    thaw_phase,
    tick,
)
from engine.tests.rounds_support import (
    VALID_CASE,
    Recorder,
    Seated,
    at,
    phased_arc,
    private_to,
    reach_phase,
    seat_session,
)

COMMIT_SECONDS = 120
ENTERED = 100
DEADLINE = ENTERED + COMMIT_SECONDS
RIGHT = {"slot_who": "marlowe", "slot_how": "c_how_true"}


@pytest_asyncio.fixture()
async def factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine, session_factory = await make_sqlite_session_factory()
    try:
        yield session_factory
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def db(
    factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with factory() as session:
        try:
            yield session
        finally:
            await session.rollback()


def commit_arc(case_path: Path | None = VALID_CASE) -> ArcDefinition:
    return phased_arc(
        case_path=case_path,
        phases={"finale": [{"kind": "commit", "seconds": COMMIT_SECONDS}]},
    )


async def at_commit(
    db: AsyncSession,
    registered: Callable[[ArcDefinition], None],
    *,
    players: int = 2,
    arc: ArcDefinition | None = None,
) -> tuple[Seated, Recorder]:
    arc = arc or commit_arc()
    registered(arc)
    seated = await seat_session(db, arc, players=players)
    rec = Recorder()
    await tick(db, seated.session_id, at(0), rec)
    await reach_phase(db, seated, "finale", "commit", at(ENTERED), rec)
    return seated, rec


async def grant(db: AsyncSession, seated: Seated, who: int, concept: str) -> None:
    await grant_concept(
        db,
        session_id=seated.session_id,
        character_id=seated.characters[who],
        concept_id=concept,
        text=f"text of {concept}",
    )


async def draft(
    db: AsyncSession,
    seated: Seated,
    who: int,
    answers: dict[str, str],
    proof: str | None = None,
    rec: Recorder | None = None,
    now: float = ENTERED + 5,
) -> commit_phase.Theory:
    return await save_theory_draft(
        db, seated.session_id, seated.participants[who], answers, proof, at(now), rec
    )


async def lock(
    db: AsyncSession,
    seated: Seated,
    who: int,
    rec: Recorder | None = None,
    now: float = ENTERED + 10,
) -> commit_phase.Theory:
    return await lock_theory(
        db, seated.session_id, seated.participants[who], at(now), rec
    )


async def form(
    db: AsyncSession, seated: Seated, who: int, now: float = ENTERED + 1
) -> commit_phase.TheoryForm:
    return await read_theory_form(
        db, seated.session_id, seated.participants[who], at(now)
    )


async def rows(db: AsyncSession, session_id: UUID) -> int:
    count = await db.scalar(
        select(func.count())
        .select_from(Decision)
        .where(
            Decision.session_id == session_id,
            Decision.decision_type.in_(["theory_draft", "theory_lock"]),
        )
    )
    return int(count or 0)


async def phase_ended_by(db: AsyncSession, seated: Seated) -> str | None:
    state = await current_phase(db, seated.session_id)
    assert state is not None and state.phase == "commit"
    return state.reason if state.status == "ended" else None


class TestArcFile:
    def test_a_commit_phase_comes_after_a_bridge(self) -> None:
        phased_arc(
            phases={
                "finale": [
                    {"kind": "bridge", "seconds": 5},
                    {"kind": "commit", "seconds": 30},
                ]
            }
        )

    def test_a_commit_phase_cannot_come_before_a_scene(self) -> None:
        with pytest.raises(ValidationError):
            phased_arc(
                phases={
                    "finale": [
                        {"kind": "commit", "seconds": 30},
                        {"kind": "scene", "seconds": 5},
                    ]
                }
            )

    def test_a_commit_phase_needs_a_written_case(self) -> None:
        with pytest.raises(ValidationError, match="case_file"):
            phased_arc(
                case_path=None,
                phases={"finale": [{"kind": "commit", "seconds": 30}]},
            )

    def test_a_commit_phase_carries_no_written_lines(self) -> None:
        with pytest.raises(ValidationError):
            phased_arc(
                phases={
                    "finale": [
                        {
                            "kind": "commit",
                            "seconds": 30,
                            "lines": [{"text": "x", "hints": {}}],
                        }
                    ]
                }
            )


class TestTheForm:
    @pytest.mark.asyncio
    async def test_it_shows_the_slots_and_what_the_player_may_pick(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        await grant(db, seated, 0, "c_how_true")
        await grant(db, seated, 0, "c_how_false1")
        shown = await form(db, seated, 0)
        assert shown.open
        assert [s.slot_id for s in shown.slots] == ["slot_who", "slot_how"]
        who, how = shown.slots
        assert [o.value for o in who.options] == ["marlowe", "pinecone", "quillby"]
        # Every concept held is on offer, true and misleading alike, by label.
        assert {o.value for o in how.options} == {
            "c_open_a",
            "c_open_b",
            "c_how_true",
            "c_how_false1",
        }
        assert [o.label.casefold() for o in how.options] == sorted(
            o.label.casefold() for o in how.options
        )
        assert {o.value for o in shown.proof_options} == {o.value for o in how.options}

    @pytest.mark.asyncio
    async def test_the_offer_carries_no_mark_of_right_or_wrong(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        await grant(db, seated, 0, "c_how_true")
        await grant(db, seated, 0, "c_how_false1")
        text = repr(await form(db, seated, 0))
        for word in ("misleading", "standing", "accepted", "solved", "right"):
            assert word not in text

    @pytest.mark.asyncio
    async def test_the_offer_does_not_depend_on_the_accepted_answers(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        tmp_path: Path,
    ) -> None:
        data: dict[str, Any] = json.loads(VALID_CASE.read_text("utf-8"))
        data["solution"][0]["accepted"] = [
            {"value": "pinecone", "needs": ["c_gate_log"]}
        ]
        data["solution"][1]["accepted"] = [{"value": "c_how_false1", "needs": []}]
        other = tmp_path / "other_case.json"
        other.write_text(json.dumps(data), "utf-8")

        offers = []
        for path in (VALID_CASE, other):
            seated, _ = await at_commit(db, registered, arc=commit_arc(case_path=path))
            await grant(db, seated, 0, "c_how_true")
            await grant(db, seated, 0, "c_how_false1")
            shown = await form(db, seated, 0)
            offers.append(
                [(s.slot_id, s.options) for s in shown.slots] + [shown.proof_options]
            )
        assert offers[0] == offers[1]

    @pytest.mark.asyncio
    async def test_the_account_text_comes_split_into_text_and_blanks(
        self,
        db: AsyncSession,
        registered: Callable[[ArcDefinition], None],
        tmp_path: Path,
    ) -> None:
        data: dict[str, Any] = json.loads(VALID_CASE.read_text("utf-8"))
        data["account"] = "{slot_who} took it, by {slot_how}."
        path = tmp_path / "account_case.json"
        path.write_text(json.dumps(data), "utf-8")
        seated, _ = await at_commit(db, registered, arc=commit_arc(case_path=path))
        shown = await form(db, seated, 0)
        assert [(p.text, p.slot_id) for p in shown.account] == [
            ("", "slot_who"),
            (" took it, by ", None),
            ("", "slot_how"),
            (".", None),
        ]

    @pytest.mark.asyncio
    async def test_a_case_without_an_account_gives_an_empty_one(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        assert (await form(db, seated, 0)).account == ()

    @pytest.mark.asyncio
    async def test_it_is_closed_and_empty_outside_the_phase(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        arc = commit_arc()
        registered(arc)
        seated = await seat_session(db, arc, players=2)
        await tick(db, seated.session_id, at(0), Recorder())
        shown = await form(db, seated, 0, now=1)
        assert not shown.open
        assert shown.slots == () and shown.account == ()
        assert shown.theory.state == "none"

    @pytest.mark.asyncio
    async def test_a_stranger_cannot_read_a_form(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        with pytest.raises(RoundError) as refused:
            await read_theory_form(db, seated.session_id, UUID(int=7), at(ENTERED))
        assert refused.value.code == "not_a_participant"


class TestDrafts:
    @pytest.mark.asyncio
    async def test_a_draft_can_be_saved_changed_and_read_back(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        await grant(db, seated, 0, "c_how_true")
        first = await draft(db, seated, 0, {"slot_who": "pinecone"})
        second = await draft(db, seated, 0, RIGHT, proof="c_how_true")
        assert (first.revision, second.revision) == (1, 2)
        saved = (await form(db, seated, 0)).theory
        assert saved.state == "drafting"
        assert saved.answers == RIGHT
        assert saved.proof == "c_how_true"

    @pytest.mark.asyncio
    async def test_saving_what_is_already_saved_changes_nothing(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec = await at_commit(db, registered)
        await draft(db, seated, 0, {"slot_who": "marlowe"}, rec=rec)
        before = (await rows(db, seated.session_id), len(rec.events))
        again = await draft(db, seated, 0, {"slot_who": "marlowe"}, rec=rec)
        assert again.revision == 1
        assert (await rows(db, seated.session_id), len(rec.events)) == before

    @pytest.mark.asyncio
    async def test_a_draft_reads_the_same_after_everything_is_rebuilt(
        self,
        factory: async_sessionmaker[AsyncSession],
        registered: Callable[[ArcDefinition], None],
    ) -> None:
        async with factory() as db:
            seated, _ = await at_commit(db, registered)
            await grant(db, seated, 0, "c_how_true")
            await draft(db, seated, 0, RIGHT, proof="c_how_true")
            await db.commit()
        async with factory() as fresh:
            shown = await form(fresh, seated, 0, now=ENTERED + 50)
        assert shown.theory.answers == RIGHT
        assert shown.theory.proof == "c_how_true"
        assert shown.seconds_left == pytest.approx(COMMIT_SECONDS - 50)

    @pytest.mark.asyncio
    async def test_a_draft_may_be_partial(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        saved = await draft(db, seated, 0, {"slot_who": "quillby"})
        assert saved.answers == {"slot_who": "quillby"}

    @pytest.mark.asyncio
    async def test_a_concept_not_held_is_refused(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        with pytest.raises(RoundError) as refused:
            await draft(db, seated, 0, {"slot_how": "c_how_true"})
        assert refused.value.code == "concept_not_held"
        assert await rows(db, seated.session_id) == 0

    @pytest.mark.asyncio
    async def test_a_concept_only_heard_is_not_held(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        await assert_knowledge(
            db,
            session_id=seated.session_id,
            character_id=seated.characters[0],
            fact_type="concept",
            fact_content={"concept_id": "c_how_true", "text": "heard"},
            source_character_id=seated.characters[1],
        )
        assert "c_how_true" not in await concepts_held(
            db, session_id=seated.session_id, character_id=seated.characters[0]
        )
        with pytest.raises(RoundError) as refused:
            await draft(db, seated, 0, {"slot_how": "c_how_true"})
        assert refused.value.code == "concept_not_held"
        shown = await form(db, seated, 0)
        assert "c_how_true" not in {o.value for o in shown.slots[1].options}

    @pytest.mark.asyncio
    async def test_a_cast_member_the_case_does_not_allow_is_refused(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        for answer in ("storyteller", "nobody"):
            with pytest.raises(RoundError) as refused:
                await draft(db, seated, 0, {"slot_who": answer})
            assert refused.value.code == "answer_not_offered"

    @pytest.mark.asyncio
    async def test_an_unknown_slot_is_refused(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        with pytest.raises(RoundError) as refused:
            await draft(db, seated, 0, {"slot_nope": "marlowe"})
        assert refused.value.code == "unknown_slot"

    @pytest.mark.asyncio
    async def test_one_players_holdings_do_not_open_another_players_offer(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        await grant(db, seated, 0, "c_how_true")
        with pytest.raises(RoundError):
            await draft(db, seated, 1, {"slot_how": "c_how_true"})

    @pytest.mark.asyncio
    async def test_saving_outside_the_phase_is_refused(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        arc = commit_arc()
        registered(arc)
        seated = await seat_session(db, arc, players=2)
        await tick(db, seated.session_id, at(0), Recorder())
        with pytest.raises(RoundError) as refused:
            await draft(db, seated, 0, {"slot_who": "marlowe"}, now=1)
        assert refused.value.code == "not_in_commit_phase"

    @pytest.mark.asyncio
    async def test_saving_after_the_deadline_is_refused_before_the_tick(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        with pytest.raises(RoundError) as refused:
            await draft(db, seated, 0, {"slot_who": "marlowe"}, now=DEADLINE)
        assert refused.value.code == "phase_time_up"


class TestTheProof:
    @pytest.mark.asyncio
    async def test_the_proof_is_saved_and_locked_with_the_draft(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        await grant(db, seated, 0, "c_how_true")
        await grant(db, seated, 0, "c_ledger")
        await draft(db, seated, 0, RIGHT, proof="c_ledger")
        locked = await lock(db, seated, 0)
        assert (locked.state, locked.proof) == ("locked", "c_ledger")
        assert (await form(db, seated, 0)).theory.proof == "c_ledger"

    @pytest.mark.asyncio
    async def test_a_proof_not_held_is_refused(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        with pytest.raises(RoundError) as refused:
            await draft(db, seated, 0, {"slot_who": "marlowe"}, proof="c_ledger")
        assert refused.value.code == "proof_not_held"

    @pytest.mark.asyncio
    async def test_a_misleading_concept_may_be_the_proof(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        await grant(db, seated, 0, "c_how_false1")
        saved = await draft(db, seated, 0, {}, proof="c_how_false1")
        assert saved.proof == "c_how_false1"

    @pytest.mark.asyncio
    async def test_a_lock_without_a_proof_is_allowed(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        await grant(db, seated, 0, "c_how_true")
        await draft(db, seated, 0, RIGHT)
        locked = await lock(db, seated, 0)
        assert (locked.state, locked.proof) == ("locked", None)

    @pytest.mark.asyncio
    async def test_a_complete_draft_without_a_proof_is_locked_at_the_end(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        await grant(db, seated, 0, "c_how_true")
        await draft(db, seated, 0, RIGHT)
        await tick(db, seated.session_id, at(DEADLINE), Recorder())
        assert (await form(db, seated, 0, now=DEADLINE + 1)).theory.state == "locked"


class TestTheLock:
    @pytest.mark.asyncio
    async def test_a_lock_with_an_empty_slot_is_refused(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        await draft(db, seated, 0, {"slot_who": "marlowe"})
        with pytest.raises(RoundError) as refused:
            await lock(db, seated, 0)
        assert refused.value.code == "theory_incomplete"
        assert (await form(db, seated, 0)).theory.state == "drafting"

    @pytest.mark.asyncio
    async def test_a_lock_with_no_draft_is_refused(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        with pytest.raises(RoundError) as refused:
            await lock(db, seated, 0)
        assert refused.value.code == "theory_incomplete"

    @pytest.mark.asyncio
    async def test_after_a_lock_a_save_or_a_lock_is_refused_and_changes_nothing(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec = await at_commit(db, registered, players=3)
        await grant(db, seated, 0, "c_how_true")
        await draft(db, seated, 0, RIGHT)
        await lock(db, seated, 0)
        before = (await rows(db, seated.session_id), len(rec.events))
        with pytest.raises(RoundError) as saved:
            await draft(db, seated, 0, {"slot_who": "pinecone"}, rec=rec)
        with pytest.raises(RoundError) as again:
            await lock(db, seated, 0, rec=rec)
        assert saved.value.code == again.value.code == "theory_locked"
        assert (await rows(db, seated.session_id), len(rec.events)) == before
        assert (await form(db, seated, 0)).theory.answers == RIGHT

    @pytest.mark.asyncio
    async def test_a_locked_form_is_not_open(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered, players=3)
        await grant(db, seated, 0, "c_how_true")
        await draft(db, seated, 0, RIGHT)
        await lock(db, seated, 0)
        assert not (await form(db, seated, 0)).open
        assert (await form(db, seated, 1)).open


async def solve(db: AsyncSession, seated: Seated, who: int) -> None:
    await grant(db, seated, who, "c_how_true")
    await draft(db, seated, who, RIGHT)


class TestHowThePhaseEnds:
    @pytest.mark.asyncio
    async def test_it_ends_when_everyone_has_locked(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        for who in (0, 1):
            await solve(db, seated, who)
        await lock(db, seated, 0)
        assert await phase_ended_by(db, seated) is None
        await lock(db, seated, 1)
        assert await phase_ended_by(db, seated) == "locked"

    @pytest.mark.asyncio
    async def test_it_ends_when_the_countdown_reaches_zero(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        await tick(db, seated.session_id, at(DEADLINE - 1), Recorder())
        assert await phase_ended_by(db, seated) is None
        await tick(db, seated.session_id, at(DEADLINE), Recorder())
        assert await phase_ended_by(db, seated) == "time"

    @pytest.mark.asyncio
    async def test_it_ends_when_the_host_moves_on(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        await host_move_on(db, seated.session_id, at(ENTERED + 10), Recorder())
        assert await phase_ended_by(db, seated) == "host"

    @pytest.mark.asyncio
    async def test_a_complete_unlocked_draft_is_locked_as_it_stands(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec = await at_commit(db, registered, players=3)
        await solve(db, seated, 0)
        await draft(db, seated, 1, {"slot_who": "marlowe"})  # not complete
        await tick(db, seated.session_id, at(DEADLINE), rec)
        assert (await form(db, seated, 0, now=DEADLINE + 1)).theory.state == "locked"
        assert (await form(db, seated, 0, now=DEADLINE + 1)).theory.answers == RIGHT
        # A partial draft, and no draft at all, are recorded as no theory.
        assert (await form(db, seated, 1, now=DEADLINE + 1)).theory.state == "no_theory"
        assert (await form(db, seated, 2, now=DEADLINE + 1)).theory.state == "no_theory"
        assert (await form(db, seated, 1, now=DEADLINE + 1)).theory.answers == {}
        # The owner is told; nobody else.
        told = [e for e in private_to(rec.events, seated.participants[0])]
        assert [
            e.payload["state"] for e in told if e.event_type == "theory_locked"
        ] == ["locked"]

    @pytest.mark.asyncio
    async def test_the_same_holds_when_the_host_moves_on(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        await solve(db, seated, 0)
        await host_move_on(db, seated.session_id, at(ENTERED + 10), Recorder())
        assert (await form(db, seated, 0, now=ENTERED + 11)).theory.state == "locked"
        assert (await form(db, seated, 1, now=ENTERED + 11)).theory.state == "no_theory"

    @pytest.mark.asyncio
    async def test_a_second_tick_adds_nothing(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec = await at_commit(db, registered)
        await solve(db, seated, 0)
        await tick(db, seated.session_id, at(DEADLINE), rec)
        saved = (await rows(db, seated.session_id), len(rec.events))
        await tick(db, seated.session_id, at(DEADLINE + 1), rec)
        assert (await rows(db, seated.session_id), len(rec.events)) == saved

    @pytest.mark.asyncio
    async def test_nobody_doing_anything_reaches_the_end_on_the_clock(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered, players=4)
        await tick(db, seated.session_id, at(DEADLINE), Recorder())
        assert await phase_ended_by(db, seated) == "time"
        for who in range(4):
            assert (await form(db, seated, who, now=DEADLINE + 1)).theory.state == (
                "no_theory"
            )

    @pytest.mark.asyncio
    async def test_ready_does_not_end_it(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        with pytest.raises(RoundError) as refused:
            await mark_ready(
                db, seated.session_id, seated.participants[0], at(ENTERED + 1)
            )
        assert refused.value.code == "phase_not_ready_able"


class TestPause:
    @pytest.mark.asyncio
    async def test_pause_and_resume_keep_the_time_left(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered)
        await freeze_phase(db, seated.session_id, at(ENTERED + 30))
        paused = await form(db, seated, 0, now=ENTERED + 500)
        assert not paused.open
        assert paused.seconds_left == pytest.approx(COMMIT_SECONDS - 30)
        assert paused.slots  # the form stays on screen while paused
        with pytest.raises(RoundError) as refused:
            await draft(db, seated, 0, {"slot_who": "marlowe"}, now=ENTERED + 500)
        assert refused.value.code == "phase_not_running"
        await thaw_phase(db, seated.session_id, at(ENTERED + 500))
        resumed = await form(db, seated, 0, now=ENTERED + 510)
        assert resumed.open
        assert resumed.seconds_left == pytest.approx(COMMIT_SECONDS - 30 - 10)


class TestWhatIsToldToWhom:
    @pytest.mark.asyncio
    async def test_a_draft_and_a_lock_go_to_their_owner_only(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec = await at_commit(db, registered, players=3)
        start = len(rec.events)
        await solve(db, seated, 0)
        await draft(db, seated, 0, RIGHT, proof="c_how_true", rec=rec)
        await lock(db, seated, 0, rec=rec)
        await draft(db, seated, 1, {"slot_who": "quillby"}, rec=rec)
        new = rec.events[start:]
        secrets = ("marlowe", "c_how_true", "quillby")
        for event in new:
            body = json.dumps(event.payload)
            if event.event_type in ("theory_draft_saved", "theory_locked"):
                assert event.target_audience is AudienceTarget.specific_player
                assert event.target_player_id in seated.participants
            else:
                assert not any(s in body for s in secrets), event.event_type
        assert {e.event_type for e in new} == {
            "theory_draft_saved",
            "theory_locked",
            "theory_lock_progress",
        }
        # Every draft or lock event went to the player it belongs to.
        for event in new:
            if event.event_type == "theory_draft_saved":
                assert "marlowe" in json.dumps(event.payload) or "quillby" in (
                    json.dumps(event.payload)
                )
        owners = {
            "marlowe": seated.participants[0],
            "quillby": seated.participants[1],
        }
        for event in new:
            for word, owner in owners.items():
                if word in json.dumps(event.payload):
                    assert event.target_player_id == owner

    @pytest.mark.asyncio
    async def test_the_shared_screen_and_host_learn_only_who_has_locked(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec = await at_commit(db, registered, players=3)
        start = len(rec.events)
        await solve(db, seated, 0)
        await lock(db, seated, 0, rec=rec)
        progress = [
            e for e in rec.events[start:] if e.event_type == "theory_lock_progress"
        ]
        assert {e.target_audience for e in progress} == {
            AudienceTarget.shared_display,
            AudienceTarget.host_only,
        }
        for event in progress:
            assert event.payload == {
                "participant_id": str(seated.participants[0]),
                "locked_count": 1,
                "player_count": 3,
            }

    @pytest.mark.asyncio
    async def test_the_public_round_view_counts_locks(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered, players=3)
        await solve(db, seated, 0)
        await lock(db, seated, 0)
        view = await round_view(db, seated.session_id, at(ENTERED + 20))
        assert (view.phase, view.ready_count, view.player_count) == ("commit", 1, 3)

    @pytest.mark.asyncio
    async def test_nothing_in_the_phase_says_whether_anything_is_right(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, rec = await at_commit(db, registered, players=2)
        await solve(db, seated, 0)
        await draft(db, seated, 1, {"slot_who": "pinecone"}, rec=rec)
        await lock(db, seated, 0, rec=rec)
        await tick(db, seated.session_id, at(DEADLINE), rec)
        for event in rec.events:
            body = json.dumps(event.payload).casefold()
            for word in ("right", "wrong", "solved", "correct", "winner"):
                assert word not in body, (event.event_type, word)
        view = await round_view(db, seated.session_id, at(DEADLINE + 1))
        assert "right" not in repr(view).casefold()


class TestOpeningForALatePlayer:
    @pytest.mark.asyncio
    async def test_everyone_holds_the_opening_when_the_phase_begins(
        self, db: AsyncSession, registered: Callable[[ArcDefinition], None]
    ) -> None:
        seated, _ = await at_commit(db, registered, players=3)
        for who in range(3):
            held = await concepts_held(
                db, session_id=seated.session_id, character_id=seated.characters[who]
            )
            assert {"c_open_a", "c_open_b"} <= held
