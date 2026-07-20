# AW-284 Race Scoring And Accusation State — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This plan was written by a planning-only session with no execution access — it was not spot-checked against a live implementation run. Task 1 is a mandatory grounding step; if what it finds contradicts an assumption baked into a later task, stop and resolve that specific mismatch before proceeding, rather than forcing the rest of the plan to fit.

**Goal:** Implement deterministic race scoring (evidence, contradiction catches, accusation accuracy weighted by earliness) and accusation state (private submissions, beat-scoped lockout/penalty, first-correct triggers table-wide Last Call, countdown expiry, all-players-locked-early) per the founder-approved design.

**Architecture:** New module `engine/scoring/` (models, calculator, resolver, events — mirrors `engine/claims/`'s and `engine/resources/`'s file shape). Accusation attempts get a dedicated DB table (`accusations`), same pattern and rationale as D-078's `claims`/`contradiction_flags` tables — this is gameplay-critical, replay-reproducible state, not incidental telemetry. Score computation is a set of pure functions (`engine/scoring/calculator.py`) with no DB access, so the point math in Tables 1-4 is directly unit-testable against the design doc's own worked scenarios. The early-Last-Call trigger requires arc-content changes to `nightcap/couch-race.arc.json` (AW-281, already merged) plus session-orchestration logic — not an `engine/arc/` code change.

**Tech Stack:** Python 3.11+, Pydantic v2, SQLAlchemy 2.0 async ORM, Alembic migrations, pytest, pytest-asyncio.

**User decisions (already made) — do not re-litigate these, they are settled:**
- Accusations open from The Grill onward, not gated to Last Call.
- Wrong-accusation lockout and penalty escalate across Grill → Twist → Last Call and again on repeat offenses by the same player (Table 3).
- Five accusation features locked in, momentum-weighted accusation bonus (Table 2) is primary: chain-reaction Last Call (Table 4), The Last Word (one free change during Last Call), escalating lockout, and Suspect Lock (private, zero-score, reveal-narrated).
- Beat-scoped parameters live in arc configuration data, not engine constants.
- Accusation tie-break is server-authoritative receipt timestamp, first-received-correct-accusation wins (closes D-077's flagged AW-284 question, issue #238).
- Momentum multiplier keys only off AW-283's `contradiction_confirmed` outcome events, never a raw flag attempt.
- Accusation submission is server-gated on current lockout state; a submission during an active lockout is rejected, not silently dropped.
- No raw numeric score or dimension name (evidence/contradiction/accusation) may appear in any player-facing event before the reveal (Truth beat) — every pre-reveal scoring event is an animated sting plus race-track motion, per presentation_hints.
- Full tuning tables, worked scenarios, and endgame walkthroughs: `docs/superpowers/specs/2026-07-19-aw284-race-scoring-design.md`.
- Full discovery record: `docs/product/aw284-discovery-and-checkpoints.md`.

---

## File Structure

- `migrations/versions/000N_add_accusations_table.py` — new `accusations` and `suspect_locks` tables. **N is not fixed** — AW-283's own plan proposes migration `0006`; whichever of AW-283/AW-284 executes first claims `0006`, the other must chain after it as the next number. Task 1 grounds the real head.
- `engine/db/orm.py` — add `Accusation` and `SuspectLock` classes (append, do not restructure existing classes).
- `engine/scoring/__init__.py` — empty.
- `engine/scoring/models.py` — Pydantic DTOs: `AccusationOutcome`, `AccusationAttempt`, `ScoreBreakdown`.
- `engine/scoring/errors.py` — `ScoringError` base, `AccusationLockedOutError`, `AlreadyCorrectError`.
- `engine/scoring/calculator.py` — pure deterministic point-math functions implementing design doc Tables 1-4.
- `engine/scoring/resolver.py` — `AccusationResolver`: DB-backed submission, lockout enforcement, tie-break, Suspect Lock.
- `engine/scoring/events.py` — `ContentEvent` factories: pre-reveal animated stings + race-track motion, reveal-time full breakdown.
- `engine/scoring/superlatives.py` — pure functions computing the three named superlatives at session end.
- `engine/telemetry/scoring.py` — payload builders + `record_*` DB recorders, mirrors `engine/telemetry/obligations.py`.
- `nightcap/couch-race.arc.json` — rename `grill`/`twist` exit conditions, add the `grill -> last_call` shortcut edge (design doc Section 8).
- Orchestration wiring — exact file location grounded in Task 1 (likely `engine/session/service.py` or a new thin module alongside `engine/session/obligations.py`; do not guess ahead of Task 1's finding).
- `engine/tests/test_scoring_models.py`, `test_scoring_calculator.py`, `test_scoring_resolver.py`, `test_scoring_events.py`, `test_scoring_superlatives.py`, `test_scoring_integration.py`, `test_scoring_naming_contract.py`, `test_telemetry_scoring.py`.

---

## Task 1: Ground the real integration points

**Goal:** Answer the integration questions this plan cannot fully resolve without live grounding access, so later tasks build against what actually exists, not assumptions.

**Files:** Read-only.

**Acceptance Criteria:**
- [ ] Exact current Alembic head confirmed (`alembic heads`); if AW-283's `0006_add_claims_and_contradiction_flags` migration has already landed, this plan's migration becomes `0007` and must set `down_revision` accordingly instead of chaining off `0005_add_obligations_table`.
- [ ] AW-283's real, shipped `engine/claims/` module interface confirmed if AW-283 has executed by grounding time (`ClaimRecord`, `ContradictionOutcome`, `FlagResult`, table/column names) — if AW-283 has NOT executed yet, confirm that explicitly and report it as a blocking cross-task dependency (Task 5 needs a real `contradiction_flags` table to query for momentum; it cannot query a table that doesn't exist yet).
- [ ] Exact mechanism identified for how evidence delivery is tracked today (grep `EvidenceEntry`, `visible_evidence_for`, and any existing "evidence delivered" telemetry event in `engine/` and `engine/telemetry/`) — Task 4's evidence-points calculation needs a real signal to count against, not an invented one.
- [ ] Exact mechanism identified for how a completed mini-game result reaches session state today (grep `engine/mini_games/` runtime and `engine/telemetry/resources.py`-adjacent mini-game telemetry, if any) — Task 4's mini-game-points conversion (15-40 range) needs the real result shape.
- [ ] Exact orchestrator call site identified where `ArcStateChart` beat-advance events (`advance_*`) are actually invoked in a live session (grep `advance_` usage and `ArcStateChart(` construction across `engine/harness/` and `engine/session/`) — Task 6's orchestration logic must be added at this real call site, not a new parallel one.
- [ ] Confirm how a session's `ResolvedCase` (culprit, motive/method facts) is loaded/attached to a live session (check `engine/case/loader.py` and its callers) — Task 5's correctness check needs this.
- [ ] Confirm the participant/session ID types used at the harness/session boundary (UUID vs str) by reading `engine/session/models.py` and one real caller.

**Verify:** N/A (grounding task).

**Steps:**

- [ ] **Step 1:** Run `alembic heads` and read the latest 2-3 files in `migrations/versions/` to confirm the real current head.
- [ ] **Step 2:** `grep -rn "class Claim\|class ContradictionFlag" engine/db/orm.py` and, if present, read `engine/claims/` in full. If absent, read the AW-283 plan (`docs/superpowers/plans/2026-07-19-aw283-suspect-answer-generation.md`) as the best-available interface contract and flag explicitly that Task 5 is building against a planned-but-unexecuted interface.
- [ ] **Step 3:** `grep -rn "EvidenceEntry\|visible_evidence_for" engine/ --include=*.py | grep -v test` and read the matching delivery-tracking code in full.
- [ ] **Step 4:** Read `engine/mini_games/plugins/*.py` (at least one) and any mini-game result/telemetry code to find the real result shape.
- [ ] **Step 5:** `grep -rn "advance_\|ArcStateChart(" engine/harness/ engine/session/ --include=*.py | grep -v test` and read the real call site in full.
- [ ] **Step 6:** Read `engine/case/loader.py` and its callers.
- [ ] **Step 7:** No commit — grounding only. Write findings as a short note in your task report; Tasks 2, 4, 5, and 6 depend on this note directly.

---

## Task 2: `Accusation` and `SuspectLock` schema (migration + ORM)

**Goal:** Add the accusations and suspect_locks tables, following D-078's precedent (dedicated indexed schema for gameplay-critical, replay-reproducible state).

**Files:**
- Create: `migrations/versions/000N_add_accusations_table.py` (N per Task 1's grounding)
- Modify: `engine/db/orm.py`

**Acceptance Criteria:**
- [ ] `alembic upgrade head` applies cleanly.
- [ ] `alembic downgrade -1` cleanly reverses it.
- [ ] `Accusation` and `SuspectLock` ORM classes match the migration exactly, column-for-column.
- [ ] `submitted_at` is server-default `now()` (server-authoritative timestamp — never client-supplied), matching the locked tie-break decision.
- [ ] `suspect_locks` has a unique constraint on `(session_id, participant_id)` — one working theory per player, overwritable in place, per design doc Section 6 ("freely overwritable").

**Verify:** `alembic upgrade head && alembic downgrade -1 && alembic upgrade head`

**Steps:**

- [ ] **Step 1:** Confirm the down_revision per Task 1's finding.

- [ ] **Step 2: Write the migration**

```python
# migrations/versions/000N_add_accusations_table.py
"""add_accusations_table

Revision ID: 000N_add_accusations_table
Revises: <per Task 1 grounding>
Create Date: 2026-07-19

Adds the accusations table (AW-284). Accusation attempts are gameplay-
critical, replay-reproducible state that the reveal accounting and
superlative computation both read after the fact, so they get a dedicated
indexed schema rather than the generic events table -- same rationale as
D-078's claims/contradiction_flags tables.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID as PGUUID

revision = "000N_add_accusations_table"
down_revision = "<per Task 1 grounding>"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accusations",
        sa.Column(
            "accusation_id",
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "session_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("sessions.session_id"),
            nullable=False,
        ),
        sa.Column(
            "accuser_participant_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("session_participants.participant_id"),
            nullable=False,
        ),
        sa.Column("beat_id", sa.Text(), nullable=False),
        sa.Column("accused_cast_member_id", sa.Text(), nullable=False),
        sa.Column("motive_correct", sa.Boolean(), nullable=True),
        sa.Column("method_correct", sa.Boolean(), nullable=True),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("catches_banked_at_submission", sa.Integer(), nullable=False),
        sa.Column("points_awarded", sa.Integer(), nullable=False),
        sa.Column("repeat_offense_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lockout_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("used_last_word", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("triggered_last_call", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_accusations_session_id_accuser",
        "accusations",
        ["session_id", "accuser_participant_id"],
    )
    op.create_index(
        "ix_accusations_session_id_outcome_submitted_at",
        "accusations",
        ["session_id", "outcome", "submitted_at"],
    )

    op.create_table(
        "suspect_locks",
        sa.Column(
            "suspect_lock_id",
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "session_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("sessions.session_id"),
            nullable=False,
        ),
        sa.Column(
            "participant_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("session_participants.participant_id"),
            nullable=False,
        ),
        sa.Column("suspect_cast_member_id", sa.Text(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_unique_constraint(
        "uq_suspect_locks_session_participant",
        "suspect_locks",
        ["session_id", "participant_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_suspect_locks_session_participant", "suspect_locks", type_="unique"
    )
    op.drop_table("suspect_locks")
    op.drop_index("ix_accusations_session_id_outcome_submitted_at", table_name="accusations")
    op.drop_index("ix_accusations_session_id_accuser", table_name="accusations")
    op.drop_table("accusations")
```

- [ ] **Step 3: Add the `Accusation` and `SuspectLock` ORM classes** to `engine/db/orm.py`, appended after the last class in the file. Match the migration's columns exactly; follow `Obligation`'s structural pattern (same `Mapped`/`mapped_column` conventions — read `class Obligation(Base):` in full first, do not guess the pattern). `SuspectLock` needs a `UniqueConstraint("session_id", "participant_id")` in its `__table_args__`, matching the migration's unique constraint — an "overwrite" is an UPDATE against this constraint, not an INSERT-only append like `Accusation`.

- [ ] **Step 4:** Run: `alembic upgrade head` then `alembic downgrade -1` then `alembic upgrade head` again — confirm no errors at each step.

- [ ] **Step 5: Commit**

```bash
git add migrations/versions/000N_add_accusations_table.py engine/db/orm.py
git commit -m "feat(scoring): add accusations and suspect_locks tables"
```

---

## Task 3: Scoring Pydantic DTOs

**Goal:** Define the in-process data shapes `engine/scoring/` operates on, separate from the ORM rows.

**Files:**
- Create: `engine/scoring/__init__.py` (empty)
- Create: `engine/scoring/models.py`
- Test: `engine/tests/test_scoring_models.py`

**Acceptance Criteria:**
- [ ] `AccusationOutcome` is a closed enum: `correct`, `wrong`.
- [ ] `AccusationAttempt` carries every field needed to record a submission and its result, `ConfigDict(extra="forbid")`.
- [ ] `ScoreBreakdown` carries per-dimension totals (`evidence_points`, `catch_points`, `accusation_points`, `motive_bonus`, `method_bonus`, `total`) — this type is only ever populated for reveal-time use (Task 7 enforces it never appears in a pre-reveal event payload).

**Verify:** `pytest engine/tests/test_scoring_models.py -v`

**Steps:**

- [ ] **Step 1: Write the failing tests**

```python
# engine/tests/test_scoring_models.py
import pytest
from pydantic import ValidationError
from engine.scoring.models import AccusationAttempt, AccusationOutcome, ScoreBreakdown


def test_accusation_attempt_defaults():
    attempt = AccusationAttempt(
        session_id="s1",
        accuser_participant_id="p1",
        beat_id="grill",
        accused_cast_member_id="marcus",
        outcome=AccusationOutcome.wrong,
        catches_banked_at_submission=0,
        points_awarded=-20,
    )
    assert attempt.motive_correct is None
    assert attempt.method_correct is None
    assert attempt.repeat_offense_count == 0
    assert attempt.used_last_word is False
    assert attempt.triggered_last_call is False


def test_accusation_attempt_rejects_extra_fields():
    with pytest.raises(ValidationError):
        AccusationAttempt(
            session_id="s1", accuser_participant_id="p1", beat_id="grill",
            accused_cast_member_id="marcus", outcome=AccusationOutcome.wrong,
            catches_banked_at_submission=0, points_awarded=-20,
            unexpected_field="nope",
        )


def test_score_breakdown_totals_are_explicit_not_derived():
    breakdown = ScoreBreakdown(
        evidence_points=40, catch_points=150, accusation_points=169,
        motive_bonus=25, method_bonus=0, total=384,
    )
    assert breakdown.total == 384
```

- [ ] **Step 2:** Run — expect FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Write the implementation**

```python
# engine/scoring/models.py
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AccusationOutcome(str, Enum):
    correct = "correct"
    wrong = "wrong"


class AccusationAttempt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1)
    accuser_participant_id: str = Field(min_length=1)
    beat_id: str = Field(min_length=1)
    accused_cast_member_id: str = Field(min_length=1)
    outcome: AccusationOutcome
    catches_banked_at_submission: int = Field(ge=0)
    points_awarded: int
    motive_correct: bool | None = None
    method_correct: bool | None = None
    repeat_offense_count: int = Field(default=0, ge=0)
    lockout_until: datetime | None = None
    used_last_word: bool = False
    triggered_last_call: bool = False
    accusation_id: str | None = None
    submitted_at: datetime | None = None


class ScoreBreakdown(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_points: int = Field(ge=0)
    catch_points: int = Field(ge=0)
    accusation_points: int
    motive_bonus: int = Field(ge=0)
    method_bonus: int = Field(ge=0)
    total: int
```

- [ ] **Step 4:** Run — expect PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/scoring/__init__.py engine/scoring/models.py engine/tests/test_scoring_models.py
git commit -m "feat(scoring): accusation and score-breakdown schemas"
```

---

## Task 4: Deterministic score calculator (Tables 1-4)

**Goal:** Pure functions implementing every number in the design doc's Tables 1-4, unit-tested directly against the design doc's own three worked scenarios so the math is provably right, not just plausible.

**Files:**
- Create: `engine/scoring/errors.py`
- Create: `engine/scoring/calculator.py`
- Test: `engine/tests/test_scoring_calculator.py`

**Acceptance Criteria:**
- [ ] `evidence_points(count)` returns `count * 10` (Table 1).
- [ ] `momentum_multiplier(catches_banked)` returns the exact Table 2 curve: 0→0.0, 1→0.10, 2→0.20, 3→0.30, 4→0.40, 5+→0.50 (capped).
- [ ] `accusation_base_value(beat_id, beat_progress_fraction)` continuously interpolates between the three Table 1 anchor points (200 at Grill start, ~130 at Twist midpoint, 60 at Last Call floor) — not a 3-tier step function. Test both anchor points exactly and at least one interpolated midpoint.
- [ ] `wrong_accusation_cost(beat_id, repeat_offense_count)` returns the exact Table 3 lockout/penalty pair, with the `×1.5` escalation applied per repeat offense (compounding, i.e. offense 2 is ×1.5, offense 3 is ×1.5² , etc. — design doc doesn't cap the exponent, so don't invent a cap not in the doc).
- [ ] `chain_reaction_countdown(remaining_seconds, additional_correct_count)` applies Table 4's compounding −20% per additional correct accusation, floored at 30 seconds.
- [ ] The three design-doc scenarios (Careful Detective = 384, Lucky Early Guesser = 210, Reckless Accuser = 56) are each reproduced exactly by composing these functions in a single integration-style unit test per scenario — this is the plan's primary proof that "catches dominant" actually holds in code, not just in the design doc's prose.
- [ ] Every function is pure (no DB, no I/O) and deterministic — repeated calls with identical inputs produce identical outputs (test this directly).

**Verify:** `pytest engine/tests/test_scoring_calculator.py -v`

**Steps:**

- [ ] **Step 1: Write the failing tests**

```python
# engine/tests/test_scoring_calculator.py
import pytest
from engine.scoring.calculator import (
    evidence_points,
    momentum_multiplier,
    accusation_base_value,
    motive_method_bonus,
    wrong_accusation_cost,
    chain_reaction_countdown,
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
    # Twist midpoint anchor per the design doc: ~130
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
    assert second_penalty == -60  # -40 * 1.5


def test_chain_reaction_countdown_compounds_and_floors():
    after_first = chain_reaction_countdown(remaining_seconds=100, additional_correct_count=1)
    after_second = chain_reaction_countdown(remaining_seconds=100, additional_correct_count=2)
    assert after_first == 80
    assert after_second == 64  # 100 * 0.8 * 0.8
    floored = chain_reaction_countdown(remaining_seconds=100, additional_correct_count=10)
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
```

- [ ] **Step 2:** Run — expect FAIL (`ModuleNotFoundError`).

- [ ] **Step 3:** Write `engine/scoring/errors.py`:

```python
from __future__ import annotations


class ScoringError(Exception):
    """Base error for deterministic scoring and accusation-state failures."""


class AccusationLockedOutError(ScoringError):
    """Raised when an accusation is submitted while the player's lockout is active."""


class AlreadyCorrectError(ScoringError):
    """Raised when a player who already has a recorded correct accusation submits another."""
```

- [ ] **Step 4: Implement `engine/scoring/calculator.py`**

```python
# engine/scoring/calculator.py
"""Pure, deterministic point-math functions implementing the AW-284
design doc's Tables 1-4
(docs/superpowers/specs/2026-07-19-aw284-race-scoring-design.md).

No DB access, no I/O. Every function is a straightforward computation over
its arguments so results are reproducible under deterministic replay
(AW-284 acceptance criteria).
"""

from __future__ import annotations

EVIDENCE_POINT_VALUE = 10
CATCH_POINT_VALUE = 50

_MOMENTUM_TABLE = {0: 0.0, 1: 0.10, 2: 0.20, 3: 0.30, 4: 0.40}
_MOMENTUM_CAP = 0.50

# Table 1 accusation-value anchors: (beat_id, progress_fraction) -> value.
# beat_progress_fraction is 0.0 at the beat's start, 1.0 at its end.
_ACCUSATION_ANCHORS: list[tuple[str, float, int]] = [
    ("grill", 0.0, 200),
    ("twist", 0.5, 130),
    ("last_call", 1.0, 60),
]

# Table 3: beat_id -> (lockout_rounds, base_penalty)
_WRONG_ACCUSATION_COST: dict[str, tuple[float, int]] = {
    "grill": (1.0, -20),
    "twist": (1.5, -40),
    "last_call": (1.0, -60),  # "rest of Last Call" is applied by the caller, not this table
}
_ESCALATION_FACTOR = 1.5

_CHAIN_REACTION_CUT = 0.20
_CHAIN_REACTION_FLOOR_SECONDS = 30


def evidence_points(count: int) -> int:
    return count * EVIDENCE_POINT_VALUE


def momentum_multiplier(catches_banked: int) -> float:
    if catches_banked >= 5:
        return _MOMENTUM_CAP
    return _MOMENTUM_TABLE[catches_banked]


def accusation_base_value(beat_id: str, *, beat_progress_fraction: float) -> int:
    """Continuous earliness-decay curve across the three Table 1 anchors.

    Anchors are ordered by overall session position (Grill start -> Twist
    midpoint -> Last Call end); this function linearly interpolates between
    the two anchors whose beat_id/progress bracket the given point, using
    the anchor list's fixed ordering as the session timeline.
    """
    anchor_index = next(
        i for i, (bid, _, _) in enumerate(_ACCUSATION_ANCHORS) if bid == beat_id
    )
    _, frac, value = _ACCUSATION_ANCHORS[anchor_index]
    if beat_progress_fraction <= frac or anchor_index == 0:
        if anchor_index == 0:
            lo = _ACCUSATION_ANCHORS[0]
            hi = _ACCUSATION_ANCHORS[1]
        else:
            lo = _ACCUSATION_ANCHORS[anchor_index - 1]
            hi = _ACCUSATION_ANCHORS[anchor_index]
    else:
        if anchor_index == len(_ACCUSATION_ANCHORS) - 1:
            lo = _ACCUSATION_ANCHORS[anchor_index - 1]
            hi = _ACCUSATION_ANCHORS[anchor_index]
        else:
            lo = _ACCUSATION_ANCHORS[anchor_index]
            hi = _ACCUSATION_ANCHORS[anchor_index + 1]
    lo_bid, lo_frac, lo_val = lo
    hi_bid, hi_frac, hi_val = hi
    if lo_bid == hi_bid and lo_frac == hi_frac:
        return lo_val
    span = hi_frac - lo_frac
    t = 0.0 if span == 0 else (beat_progress_fraction - lo_frac) / span
    t = max(0.0, min(1.0, t))
    return round(lo_val + (hi_val - lo_val) * t)


def motive_method_bonus(*, motive_correct: bool, method_correct: bool) -> int:
    bonus = 0
    if motive_correct:
        bonus += 25
    if method_correct:
        bonus += 25
    return bonus


def wrong_accusation_cost(
    beat_id: str, *, repeat_offense_count: int
) -> tuple[float, int]:
    """Returns (lockout_rounds, penalty) for a wrong accusation, per Table 3.

    repeat_offense_count is the number of PRIOR wrong accusations this
    player has already made this session (0 for the first offense).
    """
    base_lockout, base_penalty = _WRONG_ACCUSATION_COST[beat_id]
    escalation = _ESCALATION_FACTOR**repeat_offense_count
    return (base_lockout * escalation, round(base_penalty * escalation))


def chain_reaction_countdown(
    remaining_seconds: float, *, additional_correct_count: int
) -> float:
    """Table 4: each additional correct accusation compounds a -20% cut,
    floored at 30 seconds so the countdown can never hit zero this way."""
    value = remaining_seconds
    for _ in range(additional_correct_count):
        value *= 1 - _CHAIN_REACTION_CUT
    return max(value, _CHAIN_REACTION_FLOOR_SECONDS)
```

- [ ] **Step 5:** Run tests, iterate until PASS. If the interpolation math doesn't land exactly on the Twist-midpoint test's `125 <= value <= 135` band, adjust `accusation_base_value`'s interpolation, not the test — the anchors are fixed by the design doc.

- [ ] **Step 6: Commit**

```bash
git add engine/scoring/errors.py engine/scoring/calculator.py engine/tests/test_scoring_calculator.py
git commit -m "feat(scoring): deterministic point-math calculator (Tables 1-4)"
```

---

## Task 5: Accusation resolver — submission, lockout, tie-break, Suspect Lock

**Goal:** `AccusationResolver`: record a submission (DB-backed), enforce server-side lockout gating, apply the calculator, detect first-correct via server-authoritative tie-break, and manage the private Suspect Lock.

**Files:**
- Create: `engine/scoring/resolver.py`
- Test: `engine/tests/test_scoring_resolver.py`

**Acceptance Criteria:**
- [ ] `submit_accusation` raises `AccusationLockedOutError` (does not silently reject) if the accusing participant currently has an unexpired `lockout_until` from a prior `Accusation` row — this is the server-side defense-in-depth gate, independent of any client-side button state.
- [ ] `submit_accusation` raises `AlreadyCorrectError` if the accusing participant already has a `correct` `Accusation` row this session (a player who already won can't submit again).
- [ ] A wrong accusation persists an `Accusation` row with `outcome=wrong`, the correct beat-scoped `points_awarded` and `lockout_until` (via `calculator.wrong_accusation_cost`, escalated by that player's prior wrong-accusation count this session), and `repeat_offense_count` set from a real DB count of that player's prior wrong accusations — not a caller-supplied value.
- [ ] A correct accusation persists an `Accusation` row with `outcome=correct`, `points_awarded` computed from `calculator.accusation_base_value` × `(1 + momentum_multiplier(catches_banked))` plus `calculator.motive_method_bonus`, where `catches_banked` is a real DB count of `contradiction_confirmed` events attributed to this player since their last `Accusation` row (or session start if none) — this is the cross-module read into AW-283's claims/contradiction_flags tables identified in Task 1.
- [ ] The first correct accusation (by server `submitted_at`, not client time) sets `triggered_last_call=True` on its own row and is the only row ever marked `True` for a session.
- [ ] **Chain Reaction wiring (design doc Table 4):** every correct accusation *after* the first (by submission order) calls `calculator.chain_reaction_countdown` against the session's current remaining Last Call time and persists the compressed value back to session state (the same session-context mechanism `engine/arc/arc_state.py` already uses via `update_context`/`get_context` — read Task 1's orchestration-call-site finding for how remaining countdown time is tracked today, or add a `last_call_remaining_seconds` context key if none exists). This is what makes Task 4's pure function actually observable in a live session, not just unit-tested in isolation.
- [ ] **Last Word first-use flow:** a wrong accusation submitted during Last Call sets `lockout_until` per Table 3 as normal, but if this is the player's *first* wrong Last-Call submission (`used_last_word` was `False` beforehand), the resolver additionally allows exactly one more Last-Call submission from that player by NOT treating their existing lockout as blocking — implement this by setting `used_last_word=True` on that first wrong-in-Last-Call row and having the lockout check treat "has an unexpired lockout AND `used_last_word=True` already on a prior row this beat" as the actual block condition, rather than blocking on any lockout unconditionally during Last Call. A second wrong Last-Call submission (this player's `used_last_word` already `True`) is blocked normally by `AccusationLockedOutError`.
- [ ] `set_suspect_lock` upserts a `SuspectLock` row (Task 2) keyed on `(session_id, participant_id)` — private, zero-score, no `Accusation` row created (it is not an accusation attempt), freely overwritable by calling it again.

**Verify:** `pytest engine/tests/test_scoring_resolver.py -v`

**Steps:**

- [ ] **Step 1:** Re-read Task 1's grounding note for the real `ResolvedCase` loading mechanism, the real claims/contradiction_flags table shape (or the AW-283 plan's proposed shape if AW-283 hasn't executed), and how session-context values like `last_call_remaining_seconds` should be tracked/persisted (reuse `session_context` per `engine/arc/arc_state.py` if that's accessible from this resolver's call site, otherwise a new column on the `sessions` row or a dedicated small table — ground this rather than guessing). If Task 1 found AW-283 hasn't executed and no `contradiction_flags` table exists yet, STOP and report BLOCKED — momentum computation has no real data to query, and this is a genuine cross-task dependency gap, not something to route around with a fake table.
- [ ] **Step 2:** Write failing tests using the same async-DB test fixture pattern already established in `engine/tests/test_obligations.py` (reuse it, don't invent a new one) — cover: successful wrong accusation with correct lockout/penalty; successful correct accusation with correct momentum-weighted points; `AccusationLockedOutError` on a submission during active lockout; `AlreadyCorrectError` on a second submission after already-correct; first-correct-wins tie-break with two near-simultaneous correct submissions from different players (assert only one has `triggered_last_call=True`, and it's the one with the earlier `submitted_at`); Chain Reaction compression on a second correct accusation (assert the persisted remaining-countdown value matches `calculator.chain_reaction_countdown`'s output); Last Word consumption (a first wrong Last-Call submission sets `used_last_word=True` and does NOT block a follow-up submission; a second wrong Last-Call submission raises `AccusationLockedOutError`); `set_suspect_lock` upsert behavior (calling it twice for the same player replaces the single row, verified by row count staying at 1).
- [ ] **Step 3:** Implement `AccusationResolver` with `async def submit_accusation(self, db_session, *, session_id, accuser_participant_id, beat_id, beat_progress_fraction, accused_cast_member_id, motive_correct, method_correct) -> AccusationAttempt` and `async def set_suspect_lock(self, db_session, *, session_id, participant_id, suspect_cast_member_id) -> None`. Correctness (is `accused_cast_member_id` actually the culprit) is checked against the session's `ResolvedCase.culprit_id` per Task 1's grounding — this resolver does not decide correctness itself, it queries the already-resolved case truth (architecture principle 2: AI/engine never decides case truth, it only reads it).
- [ ] **Step 4:** Run tests, iterate until PASS.
- [ ] **Step 5:** Run the full suite `pytest engine/tests/ -q` to confirm no regressions.
- [ ] **Step 6: Commit**

```bash
git add engine/scoring/resolver.py engine/tests/test_scoring_resolver.py
git commit -m "feat(scoring): accusation resolver with server-side lockout gating and tie-break"
```

---

## Task 6: Early Last Call trigger — arc-content change and orchestration

**Goal:** Realize design doc Section 8's corrected mechanism: rename `grill`/`twist` exit conditions to "beat over, any reason" flags, add the `grill -> last_call` shortcut edge, and wire the orchestration logic that sets the right flags and invokes the right transition event for the right reason.

**Files:**
- Modify: `nightcap/couch-race.arc.json`
- Modify or create: the orchestration call site found in Task 1 (do not invent a new parallel one)
- Test: `engine/tests/test_scoring_integration.py` (new file — this is the first test spanning `engine/arc/` beat transitions and `engine/scoring/`)

**Acceptance Criteria:**
- [ ] `nightcap/couch-race.arc.json`: `grill.exit_conditions` renamed from `["interrogation_rounds_complete"]` to `["grill_exit_ready"]`; `twist.exit_conditions` renamed from `["twist_delivered"]` to `["twist_exit_ready"]`; `grill`'s beat_graph entry gains `last_call` as a second target (`"grill": ["twist", "last_call"]`); `last_call.entry_conditions` and `twist.entry_conditions` remain **empty, unchanged** (design doc Section 8, step 3 — do not add a distinguishing flag there, it would break normal Twist completion).
- [ ] Orchestration code sets `grill_exit_ready`/`twist_exit_ready` to `True` for either normal completion or a first-correct-accusation landing during that beat, and separately tracks (in application state, not arc context) which cause fired.
- [ ] On normal completion, the orchestrator calls `advance_grill_to_twist` (or `advance_twist_to_last_call`); on a first-correct accusation, it calls `advance_grill_to_last_call` (or the equivalent already-existing `advance_twist_to_last_call` if the accusation lands during Twist — no new edge needed there).
- [ ] A dedicated test asserts the orchestrator invokes the *correct* event for *each* cause — not just that some transition fires. Per the known StateChart silent-guard behavior, also assert on post-call `current_state`/`session_context`, not just that the call didn't raise.
- [ ] `accusations_locked_or_countdown_expired` (last_call's own exit condition, unchanged from AW-281) is computed `True` in both of its distinct cases: natural countdown expiry, AND all remaining eligible players simultaneously locked out with no live path to submit another accusation (Endgame Path 3) — these must be two distinct test cases, not one collapsed into the other.

**Verify:** `pytest engine/tests/test_scoring_integration.py -v`

**Steps:**

- [ ] **Step 1:** Re-read Task 1's grounding note for the real orchestrator call site.
- [ ] **Step 2:** Edit `nightcap/couch-race.arc.json`'s `beats` array: rename `grill`'s `exit_conditions` entry and `twist`'s `exit_conditions` entry as specified above.
- [ ] **Step 3:** Edit `nightcap/couch-race.arc.json`'s `beat_graph`: change `"grill": ["twist"]` to `"grill": ["twist", "last_call"]`.
- [ ] **Step 4:** Run `pytest engine/tests/test_arc_state.py -v` and any existing arc-loading/validation tests — confirm the renamed conditions don't break arc-schema validation (the schema validates condition strings as opaque identifiers per architecture principle 3, so this should be safe, but verify directly rather than assuming).
- [ ] **Step 5:** At the real orchestrator call site (Task 1), add the logic that sets `grill_exit_ready` true on normal `interrogation_rounds_complete`, ALSO sets it true (plus records the "why" separately) the moment `AccusationResolver.submit_accusation` returns a correct outcome during Grill, and analogously for `twist_exit_ready`. Then calls the correct `advance_*` event based on the tracked cause.
- [ ] **Step 6:** Write the failing integration tests: (a) normal completion fires `advance_grill_to_twist`, session ends up in the `twist` state; (b) a correct accusation during Grill fires `advance_grill_to_last_call`, session ends up in the `last_call` state, `twist` content is skipped; (c) the "wrong event for the wrong reason" guard test — attempt to call `advance_grill_to_last_call` when only normal completion has occurred (no correct accusation), assert the guard does NOT let it silently succeed (per the known silent-guard behavior, assert the state did not change, since the call itself will not raise).
- [ ] **Step 7:** Write the two `accusations_locked_or_countdown_expired` test cases (natural expiry vs. all-players-locked-early) — these are also acceptance criteria for Task 10's fuller end-path suite, but land the underlying condition-computation logic here since it's part of this task's orchestration wiring.
- [ ] **Step 8:** Run tests, iterate until PASS. Run `pytest engine/tests/ -q` to confirm zero regressions on existing arc-state tests.
- [ ] **Step 9: Commit**

```bash
git add nightcap/couch-race.arc.json <orchestration file from Step 1> engine/tests/test_scoring_integration.py
git commit -m "feat(scoring): early Last Call trigger via renamed exit conditions and grill->last_call shortcut"
```

---

## Task 7: `ContentEvent` factories — animated stings, race track, reveal breakdown

**Goal:** Build the presentation-hint-driven events per design doc Section 2: no raw numbers or dimension names before the reveal, full breakdown only at Truth.

**Files:**
- Create: `engine/scoring/events.py`
- Test: `engine/tests/test_scoring_events.py`

**Acceptance Criteria:**
- [ ] `build_scoring_sting_event` (evidence found, catch confirmed, or accusation outcome) never includes a raw point value or a dimension name (`"evidence"`, `"contradiction"`, `"accusation"`) as a payload key or value before the reveal — explicit allowlist assertion, treated as a leak guard, mirroring AW-283's own `contradicted_by`-leak test style.
- [ ] `build_scoring_sting_event` always sets non-empty `presentation_hints` (at minimum `animation_hint` and `voice_hint`) — an event with default/empty hints is a bug, not a valid output.
- [ ] `build_race_track_position_event` carries only a relative position/motion value (e.g. a normalized 0.0-1.0 progress float or ordinal rank), never a per-dimension breakdown and never the accusation-specific component in isolation (would leak accusation proximity).
- [ ] `build_reveal_score_breakdown_event` (Truth beat only) is the one place a full `ScoreBreakdown` (Task 3) may appear in a payload — target audience `AudienceTarget.all` per the story bible's public reveal.

**Verify:** `pytest engine/tests/test_scoring_events.py -v`

**Steps:**

- [ ] **Step 1:** Read `engine/resources/events.py` and `engine/claims/events.py` (or the AW-283 plan's Task 5 code if not yet executed) for the exact `ContentEvent` construction style to mirror.
- [ ] **Step 2:** Write failing tests: (a) sting-event payload key allowlist excludes any raw numeric score field and any of the three dimension-name strings; (b) sting-event `presentation_hints` is never the default empty `PresentationHints()`; (c) race-track event payload has exactly one position/motion field, no per-dimension keys; (d) reveal-breakdown event payload contains a `ScoreBreakdown`-shaped dict and targets `AudienceTarget.all`.
- [ ] **Step 3:** Implement all three factories in `engine/scoring/events.py`, following the imports style (`from engine.events.models import AudienceTarget, ContentEvent, EventCategory, PresentationHints`).
- [ ] **Step 4:** Run tests, iterate until PASS.
- [ ] **Step 5: Commit**

```bash
git add engine/scoring/events.py engine/tests/test_scoring_events.py
git commit -m "feat(scoring): presentation-hint-driven scoring events, no pre-reveal score leaks"
```

---

## Task 8: Telemetry

**Goal:** Payload builders + DB recorders for accusation attempts and momentum-relevant catch counts, mirroring `engine/telemetry/obligations.py`'s pattern.

**Files:**
- Create: `engine/telemetry/scoring.py`
- Test: `engine/tests/test_telemetry_scoring.py`

**Acceptance Criteria:**
- [ ] `engine/telemetry/scoring.py` mirrors `engine/telemetry/obligations.py` exactly: pure payload builders + `async def record_*` recorders writing `Event` ORM rows (the generic `events` table is correct here — this is telemetry, not gameplay-critical replay state, which is what the dedicated `accusations` table from Task 2 is for).
- [ ] `build_accusation_submitted_payload` may include the raw outcome and points (telemetry is not player-facing, unlike Task 7's events) but must still exclude anything that would identify another player's private Suspect Lock.
- [ ] A `record_accusation_submitted` recorder is called from the resolver (Task 5) on every submission, correct or wrong.

**Verify:** `pytest engine/tests/test_telemetry_scoring.py -v`

**Steps:**

- [ ] **Step 1:** Read `engine/telemetry/obligations.py` in full as the template.
- [ ] **Step 2:** Write payload builders: `build_accusation_submitted_payload`, `build_last_call_triggered_payload`.
- [ ] **Step 3:** Write the matching `async def record_*` recorders.
- [ ] **Step 4:** Wire `record_accusation_submitted` into `AccusationResolver.submit_accusation` (Task 5) — modify `engine/scoring/resolver.py` to call it.
- [ ] **Step 5:** Run tests, iterate until PASS.
- [ ] **Step 6: Commit**

```bash
git add engine/telemetry/scoring.py engine/tests/test_telemetry_scoring.py engine/scoring/resolver.py
git commit -m "feat(scoring): telemetry payload builders for accusation attempts"
```

---

## Task 9: Superlative computation

**Goal:** Pure functions computing Best Interrogator, Lie Detector, and Most Confidently Wrong at session end, from data Tasks 2/5/8 already capture.

**Files:**
- Create: `engine/scoring/superlatives.py`
- Test: `engine/tests/test_scoring_superlatives.py`

**Acceptance Criteria:**
- [ ] `compute_superlatives(accusations, confirmed_catches_by_player, evidence_by_player) -> dict[str, str]` returns exactly the three keys `best_interrogator`, `lie_detector`, `most_confidently_wrong`, each mapped to a participant id, computed deterministically from the input data (no DB access inside this function — same pure-function discipline as Task 4).
- [ ] `lie_detector` is the participant with the most confirmed catches (ties broken by earliest catch timestamp — deterministic, not arbitrary).
- [ ] `most_confidently_wrong` is the participant with the most wrong `Accusation` rows (ties broken by total penalty magnitude, then participant id, for full determinism).
- [ ] Reproducible under identical input data (test this directly — same inputs, same outputs, called twice).

**Verify:** `pytest engine/tests/test_scoring_superlatives.py -v`

**Steps:**

- [ ] **Step 1:** Write failing tests with small, hand-constructed input fixtures (3-4 synthetic players) covering: a clear winner per category; an explicit tie-break case for `lie_detector` and `most_confidently_wrong`.
- [ ] **Step 2:** Implement `engine/scoring/superlatives.py`.
- [ ] **Step 3:** Run tests, iterate until PASS.
- [ ] **Step 4: Commit**

```bash
git add engine/scoring/superlatives.py engine/tests/test_scoring_superlatives.py
git commit -m "feat(scoring): deterministic superlative computation"
```

---

## Task 10: End-path integration tests — all three required paths plus passive-player coverage

**Goal:** Prove, via headless harness runs, that all three endgame paths (design doc Section 10) are independently reachable and deterministic, plus the passive-player abuse-mitigation coverage from the discovery record.

**Files:**
- Modify: `engine/tests/test_scoring_integration.py` (extends Task 6's file)

**Acceptance Criteria:**
- [ ] **Path 1 (first-correct → table lock-in → Truth):** a synthetic session where one player submits a correct accusation during Grill; assert the session reaches `last_call` via the shortcut (not via normal Twist completion), Chain Reaction correctly compresses the countdown when a second player also submits correct, and the session ultimately reaches `truth`.
- [ ] **Path 2 (countdown expiry, nobody correct):** a synthetic session where every accusation submitted is wrong (or none are submitted); assert normal linear progression through all beats, `last_call`'s countdown runs its full configured length, and `accusations_locked_or_countdown_expired` becomes true only via the expiry branch.
- [ ] **Path 3 (all-players-locked-early):** a synthetic session where every remaining eligible player becomes simultaneously locked out (used their Last Word on a wrong guess) with time still remaining on the countdown; assert `accusations_locked_or_countdown_expired` becomes true immediately via the all-locked branch, distinctly from Path 2's test (both must exist as separate test functions, not one parametrized case that could hide a bug in either branch).
- [ ] **Passive-player coverage:** a synthetic session where at least one player never submits any accusation at all; assert this does not prevent Paths 1, 2, or 3 from resolving (run as a variant of each).
- [ ] All four scenarios run through the real `AccusationResolver` (Task 5) and the real arc-state transitions (Task 6), not mocked shortcuts.

**Verify:** `pytest engine/tests/test_scoring_integration.py -v`

**Steps:**

- [ ] **Step 1:** Check `engine/tests/` and `engine/harness/` for the established headless-harness-run pattern used by AW-281's own "batch harness run of 10 headless Couch Race sessions" acceptance criterion — reuse that harness entry point rather than hand-rolling a new one.
- [ ] **Step 2:** Write the four scenarios as described above, each asserting on real StateChart `current_state`/beat and real `Accusation`/`Obligation`-equivalent DB rows, not just in-memory booleans.
- [ ] **Step 3:** Run tests, iterate until PASS.
- [ ] **Step 4:** Run `pytest engine/tests/ -q` to confirm zero regressions across the full suite.
- [ ] **Step 5: Commit**

```bash
git add engine/tests/test_scoring_integration.py
git commit -m "test(scoring): all three endgame paths plus passive-player coverage"
```

---

## Task 11: Generic-naming enforcement and full suite

**Goal:** Prove `engine/scoring/` and `engine/telemetry/scoring.py` carry no Nightcap-specific identifiers, matching the same precedent AW-287/AW-283 established.

**Files:**
- Create: `engine/tests/test_scoring_naming_contract.py` (mirrors `engine/tests/test_resources_naming_contract.py` exactly)

**Acceptance Criteria:**
- [ ] Naming-contract test passes against the real, final `engine/scoring/` and `engine/telemetry/scoring.py` files.
- [ ] `pytest engine/tests/ -v` fully green.
- [ ] `python -m ruff check engine api` and `python -m ruff format --check engine api` clean.
- [ ] `pytest evals/runners/test_routing_evals.py -q` still passes (this task shouldn't touch routing, but confirm nothing broke).

**Verify:** `pytest engine/tests/ -v && python -m ruff check engine api && python -m ruff format --check engine api`

**Steps:**

- [ ] **Step 1:** Write the naming-contract test, adapting `test_resources_naming_contract.py`'s exact AST-walking structure — include `engine/telemetry/scoring.py` in scope from the start (per the AW-283 plan's own lesson: `engine/telemetry/resources.py` was originally missed and had to be added as an afterthought — don't repeat that gap here).
- [ ] **Step 2:** Run it against the real files; fix any violation found (do not weaken the test to pass).
- [ ] **Step 3:** Run the full suite and lint commands from Verify above.
- [ ] **Step 4: Commit**

```bash
git add engine/tests/test_scoring_naming_contract.py
git commit -m "test(scoring): generic-naming enforcement for engine/scoring and engine/telemetry/scoring"
```

- [ ] **Step 5:** This is the implementation's stopping point. Per the completion pattern already established by AW-283/AW-287, do NOT record founder sign-off or open the PR from this task — that happens only after the founder reviews an implemented thin slice and explicitly approves it. Report final state (full suite output, naming-contract result) back to whoever is coordinating the handoff to that review step.
