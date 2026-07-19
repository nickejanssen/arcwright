# AW-283 Suspect Answer Generation And Contradiction Detection — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This plan was written by a planning-only session with no execution access — it was not spot-checked against a live implementation run. Task 1 is a mandatory grounding step; if what it finds contradicts an assumption baked into a later task, stop and resolve that specific mismatch before proceeding, rather than forcing the rest of the plan to fit.

**Goal:** Generate suspect answers through the existing knowledge-constrained dialogue pipeline (spec 0071), rendering authorized lies deterministically alongside true answers; record every answer as a claim with real DB provenance; detect contradictions deterministically (possession-gated: a flag confirms only if the claim is an authorized lie AND the flagging player already holds contradicting evidence); and wire Rattle the Witness (AW-287) into the existing `social_pressure` mechanism.

**Architecture:** New module `engine/claims/` (evidence, models, matcher, resolver, events — mirrors `engine/resources/`'s file shape) plus `engine/telemetry/claims.py` (mirrors `engine/telemetry/obligations.py`/`resources.py`). Unlike AW-282/287, this task needs real DB persistence (`Claim`, `ContradictionFlag` ORM tables) because claim provenance must survive to feed the end-of-session reveal — this was an explicit founder decision (D-078, see `docs/product/decisions-log.csv`) made because claims are this platform's headline differentiated mechanic and future consumer (AW-272 evals, Daily Case), not incidental telemetry, so they get their own indexed, queryable schema rather than being folded into the generic `events` table. Evidence possession uses the existing generic knowledge graph via the D-079 primitives in `engine/claims/evidence.py`; AW-280 remains responsible for release timing and audience decisions. The dialogue generation itself extends the existing `engine/characters/dialogue.py` pipeline (spec 0071) — it does not replace it. `AuthorizedFalsehood` (`engine/case/models.py`, already shipped by AW-281) is the source of truth for lie content; this task's job is wiring it into generation and detection, not inventing new lie content.

**Tech Stack:** Python 3.11+, Pydantic v2, SQLAlchemy 2.0 async ORM, Alembic migrations, pytest, pytest-asyncio.

**User decisions (already made) — do not re-litigate these, they are settled:**
- Suspect-answer tone: naturalistic, character/wrapper-specific; truths and lies share the same register (`docs/product/aw283-discovery-and-checkpoints.md`).
- Lies carry a subtle delivery tell (flavor only); catches are always decided by the deterministic evidence check, never by the tell.
- Catch mechanic: a player flags a statement (no evidence-pairing UI); the engine checks it, not the player.
- **Catch gating is possession-gated**: a confirmed catch requires (a) the claim matches an `AuthorizedFalsehood`, AND (b) the flagging player has already been delivered at least one of its `contradicted_by` evidence entries.
- **Claim-versus-claim is not a separate mechanism**: a delivered claim can populate a `testimony`-type `EvidenceEntry`; contradiction-by-testimony reuses the same claim-versus-evidence check as contradiction-by-physical-evidence.
- **Repeat-question lies render `claim_text` verbatim** every time (only surrounding delivery language may vary) — no paraphrase drift.
- **Rattle the Witness reuses the existing `social_pressure`/`crumble_threshold` mechanism** (`engine/characters/dialogue.py`) as a per-question boost — it is not a new independent modifier.
- **AW-283 emits outcome-only events** (`contradiction_confirmed` / `contradiction_rejected`, no score value attached); AW-284 owns all scoring.
- **Simultaneous-flag tie-break**: deterministic first-received-flag-wins now. A tie-break minigame is deferred to post-Rehearsal-1 design (issue #254, D-077) — do not build it as part of this task.
- Target ~3s p95 answer-generation latency on fast-tier routing; reuse the existing `mark_stable_context_cacheable` prompt-caching mechanism (`engine/routing/router.py`) — do not build new caching.
- **Claims get a dedicated DB schema** (`claims`, `contradiction_flags` tables), not the generic `events` table (D-078) — this was an explicit, founder-delegated architecture decision, not an assumption; the rationale is recorded in D-078 and should not be revisited without a new founder conversation.
- Full sample review, including concrete example claims and contradiction cases: `docs/superpowers/specs/2026-07-19-aw283-answer-generation-design.md`.

---

## File Structure

- `migrations/versions/0006_add_claims_and_contradiction_flags.py` — new tables.
- `engine/db/orm.py` — add `Claim`, `ContradictionFlag` classes (append, do not restructure existing classes).
- `engine/claims/__init__.py` — empty.
- `engine/claims/models.py` — Pydantic DTOs: `ClaimRecord`, `ContradictionOutcome`, `FlagResult`.
- `engine/claims/errors.py` — `ClaimError` base, `ClaimNotFoundError`, `AlreadyResolvedError`.
- `engine/claims/matcher.py` — deterministic question→fact/falsehood matching (no AI judgment call).
- `engine/claims/resolver.py` — `ClaimResolver`: record claim (DB-backed), detect contradiction (possession-gated), tie-break.
- `engine/claims/events.py` — `ContentEvent` factories, mirrors `engine/resources/events.py`.
- `engine/telemetry/claims.py` — payload builders + `record_*` DB recorders, mirrors `engine/telemetry/obligations.py`.
- `engine/tests/test_claims_models.py`, `test_claims_matcher.py`, `test_claims_resolver.py`, `test_claims_events.py`, `test_claims_integration.py`, `test_claims_naming_contract.py`, `test_telemetry_claims.py`.
- Modify `engine/characters/context.py` — extend `CharacterGenerationContext` with authorized-falsehood data (exact shape decided in Task 6, after Task 1's grounding).
- Modify `engine/characters/dialogue.py` — extend `build_dialogue_messages` with a lie-rendering prompt block (Task 6).

---

## Task 1: Evidence-delivery / knowledge-state integration (resolved)

**Goal:** Bridge a case `EvidenceEntry` to the existing knowledge graph so
possession-gated contradiction checks can ask whether a participant currently
holds a delivered evidence entry.

**Files:**
- Create: `engine/claims/evidence.py`
- Create: `engine/claims/__init__.py`
- Test: `engine/tests/test_claims_evidence.py`

**Resolution:** Evidence delivery uses the existing generic knowledge APIs. The
new `record_evidence_delivery` primitive resolves `SessionParticipant` by both
`session_id` and `participant_id`, obtains its `character_id`, and calls
`assert_knowledge` with `fact_type="evidence_delivered"` and
`fact_content={"evidence_id": evidence.evidence_id, "evidence_type": evidence.evidence_type}`.
There is no separate evidence-to-fact lookup table: the evidence ID remains in
the fact content, while the generic `Fact.fact_id` identifies the stored fact.
The `participant_has_evidence` primitive resolves the same participant, calls
`get_character_knowledge`, and checks active `evidence_delivered` fact content
for any requested evidence ID.

AW-280 remains planned and owns clue-release composition and timing. This
integration does not invent a release scheduler; its delivery primitive is the
explicit seam for the eventual release path to record each delivery.

**Acceptance Criteria:**
- [x] Evidence delivery resolves participant to character and creates a
  `KnowledgeState` through `assert_knowledge`.
- [x] Evidence possession queries use `get_character_knowledge` and active fact
  content, with no duplicate knowledge API.
- [x] The implementation is covered by focused async SQLite tests for recording,
  positive and negative possession checks, and empty requested IDs.

**Verify:** `pytest engine/tests/test_claims_evidence.py -q`

**Steps:**

- [x] Read `engine/knowledge/graph.py`, `engine/db/orm.py`, and the knowledge
  graph architecture contract.
- [x] Add failing tests for the two evidence primitives.
- [x] Implement the minimal `engine/claims/evidence.py` bridge.
- [x] Run the focused tests and confirm they pass.

---

## Task 2: `Claim` and `ContradictionFlag` schema (migration + ORM)

**Goal:** Add the two new tables per D-078's explicit approval.

**Files:**
- Create: `migrations/versions/0006_add_claims_and_contradiction_flags.py`
- Modify: `engine/db/orm.py`

**Acceptance Criteria:**
- [ ] `alembic upgrade head` applies cleanly on a fresh DB.
- [ ] `alembic downgrade -1` cleanly reverses it.
- [ ] `Claim` and `ContradictionFlag` ORM classes match the migration exactly (column-for-column).

**Verify:** `alembic upgrade head && alembic downgrade -1 && alembic upgrade head`

**Steps:**

- [ ] **Step 1:** Confirm the current migration head: `alembic heads` (expected: `0005_add_obligations_table`, per the file already in `migrations/versions/`; if a newer migration exists, use that as `down_revision` instead — do not silently skip a head you find).

- [ ] **Step 2: Write the migration**

```python
# migrations/versions/0006_add_claims_and_contradiction_flags.py
"""add_claims_and_contradiction_flags

Revision ID: 0006_add_claims_and_contradiction_flags
Revises: 0005_add_obligations_table
Create Date: 2026-07-19

Adds the claims and contradiction_flags tables (AW-283, D-078). Claims
are this platform's headline differentiated mechanic ("suspects remember
what they said") and a labeled ground-truth source for AW-272 evals, so
they get a dedicated indexed schema rather than the generic events table.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

revision = "0006_add_claims_and_contradiction_flags"
down_revision = "0005_add_obligations_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "claims",
        sa.Column(
            "claim_id",
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
            "speaker_character_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("characters.character_id"),
            nullable=False,
        ),
        sa.Column(
            "asker_participant_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("session_participants.participant_id"),
            nullable=True,
        ),
        sa.Column("round_index", sa.Integer(), nullable=False),
        sa.Column("beat_id", sa.Text(), nullable=False),
        sa.Column("interaction_window_id", sa.Text(), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column(
            "referenced_fact_ids",
            JSONB,
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "is_authorized_lie",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("falsehood_id", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_claims_session_id_speaker",
        "claims",
        ["session_id", "speaker_character_id"],
    )
    op.create_index(
        "ix_claims_session_id_beat",
        "claims",
        ["session_id", "beat_id"],
    )

    op.create_table(
        "contradiction_flags",
        sa.Column(
            "flag_id",
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "claim_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("claims.claim_id"),
            nullable=False,
        ),
        sa.Column(
            "session_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("sessions.session_id"),
            nullable=False,
        ),
        sa.Column(
            "flagged_by_participant_id",
            PGUUID(as_uuid=True),
            sa.ForeignKey("session_participants.participant_id"),
            nullable=False,
        ),
        sa.Column("outcome", sa.Text(), nullable=False),
        sa.Column("evidence_id_used", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_contradiction_flags_claim_id",
        "contradiction_flags",
        ["claim_id"],
    )
    op.create_index(
        "ix_contradiction_flags_session_id",
        "contradiction_flags",
        ["session_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_contradiction_flags_session_id", table_name="contradiction_flags")
    op.drop_index("ix_contradiction_flags_claim_id", table_name="contradiction_flags")
    op.drop_table("contradiction_flags")
    op.drop_index("ix_claims_session_id_beat", table_name="claims")
    op.drop_index("ix_claims_session_id_speaker", table_name="claims")
    op.drop_table("claims")
```

- [ ] **Step 3: Add the ORM classes** to `engine/db/orm.py`, appended after the `Obligation` class (end of file). Match the migration's columns exactly; follow the `Obligation` class immediately above it as the structural template (same import style, same `Mapped`/`mapped_column` conventions already used in that file — read `class Obligation(Base):` in full before writing, do not guess the pattern).

- [ ] **Step 4:** Run: `alembic upgrade head` then `alembic downgrade -1` then `alembic upgrade head` again — confirm no errors at each step.

- [ ] **Step 5: Commit**

```bash
git add migrations/versions/0006_add_claims_and_contradiction_flags.py engine/db/orm.py
git commit -m "feat(claims): add claims and contradiction_flags tables (D-078)"
```

---

## Task 3: Claim/contradiction Pydantic DTOs

**Goal:** Define the in-process data shapes `engine/claims/` operates on, separate from the ORM rows (mirrors how `engine/resources/models.py` is separate from `engine/db/orm.py`).

**Files:**
- Create: `engine/claims/__init__.py` (empty)
- Create: `engine/claims/models.py`
- Test: `engine/tests/test_claims_models.py`

**Acceptance Criteria:**
- [ ] `ClaimRecord`, `ContradictionOutcome`, `FlagResult` all defined with `ConfigDict(extra="forbid")`.
- [ ] `ClaimRecord.is_authorized_lie` defaults `False`; `falsehood_id` defaults `None`.
- [ ] `ContradictionOutcome` is a closed enum: `confirmed`, `rejected`.

**Verify:** `pytest engine/tests/test_claims_models.py -v`

**Steps:**

- [ ] **Step 1: Write the failing tests**

```python
# engine/tests/test_claims_models.py
import pytest
from pydantic import ValidationError
from engine.claims.models import ClaimRecord, ContradictionOutcome, FlagResult


def test_claim_record_defaults_not_a_lie():
    claim = ClaimRecord(
        speaker_id="char-1",
        asker_id="p1",
        round_index=1,
        beat_id="grill",
        interaction_window_id="w1",
        claim_text="I was on the terrace.",
    )
    assert claim.is_authorized_lie is False
    assert claim.falsehood_id is None


def test_claim_record_rejects_extra_fields():
    with pytest.raises(ValidationError):
        ClaimRecord(
            speaker_id="char-1", asker_id="p1", round_index=1,
            beat_id="grill", interaction_window_id="w1", claim_text="x",
            unexpected_field="nope",
        )


def test_flag_result_confirmed_requires_evidence_id():
    result = FlagResult(
        claim_id="claim-1",
        outcome=ContradictionOutcome.confirmed,
        evidence_id_used="evidence.coat_check_ticket",
    )
    assert result.outcome is ContradictionOutcome.confirmed
    assert result.evidence_id_used == "evidence.coat_check_ticket"


def test_flag_result_rejected_has_no_evidence_id():
    result = FlagResult(claim_id="claim-1", outcome=ContradictionOutcome.rejected)
    assert result.evidence_id_used is None
```

- [ ] **Step 2:** Run — expect FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Write the implementation**

```python
# engine/claims/models.py
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ContradictionOutcome(str, Enum):
    confirmed = "confirmed"
    rejected = "rejected"


class ClaimRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    speaker_id: str = Field(min_length=1)
    asker_id: str | None = None
    round_index: int = Field(ge=0)
    beat_id: str = Field(min_length=1)
    interaction_window_id: str = Field(min_length=1)
    claim_text: str = Field(min_length=1)
    referenced_fact_ids: tuple[str, ...] = ()
    is_authorized_lie: bool = False
    falsehood_id: str | None = None
    claim_id: str | None = None
    created_at: datetime | None = None


class FlagResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim_id: str = Field(min_length=1)
    outcome: ContradictionOutcome
    evidence_id_used: str | None = None
```

- [ ] **Step 4:** Run — expect PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/claims/__init__.py engine/claims/models.py engine/tests/test_claims_models.py
git commit -m "feat(claims): claim and contradiction-outcome schemas"
```

---

## Task 4: Deterministic question-to-fact/falsehood matcher

**Goal:** Given an asked `InteractionOption` (AW-282) and a speaker's known facts + authorized falsehoods, deterministically decide what content the answer should draw on — no AI judgment call.

**Files:**
- Create: `engine/claims/errors.py`
- Create: `engine/claims/matcher.py`
- Test: `engine/tests/test_claims_matcher.py`

**Acceptance Criteria:**
- [ ] Given a set of `AuthorizedFalsehood`s for a speaker and an asked option's authored topic tag, the matcher deterministically returns the matching falsehood if one exists for that topic, else `None`.
- [ ] Given no falsehood match, the matcher checks known facts by the same topic-matching rule and returns the matching fact reference if one exists, else a generic "no specific knowledge" signal.
- [ ] Matching is pure data lookup — no randomness, no model call, same inputs always produce the same output (test this directly with a repeated-call equality assertion).

**Verify:** `pytest engine/tests/test_claims_matcher.py -v`

**Design note — topic matching:** `AuthorizedFalsehood.topic` is one of `location`, `relationship`, `observation`, `possession` (`engine/case/models.py`). AW-282's `InteractionOption` (`engine/interactions/models.py`) does not currently carry a topic tag — check whether one needs adding there (a small, additive field, not a breaking change) or whether `prompt_key` already encodes topic in a parseable way (e.g. `prompt_key="ask_location"`). Ground this against real `nightcap/couch-race.arc.json` `interactions` authoring before writing the implementation — if `InteractionOption` needs a new `topic` field, that's an `engine/interactions/models.py` change (AW-282's module, already shipped) and should be called out explicitly as a cross-task modification in your task report, not silently done.

**Steps:**

- [ ] **Step 1:** Read `nightcap/couch-race.arc.json`'s `interactions` section and `engine/interactions/models.py`'s `InteractionOption` to determine the actual topic-matching mechanism available today.
- [ ] **Step 2:** Write `engine/claims/errors.py`:

```python
from __future__ import annotations


class ClaimError(Exception):
    """Base error for deterministic claim recording and contradiction-detection failures."""


class ClaimNotFoundError(ClaimError):
    """Raised when a flag references a claim_id with no matching recorded claim."""


class AlreadyResolvedError(ClaimError):
    """Raised when a flag targets a claim that already has a confirmed contradiction (tie-break)."""
```

- [ ] **Step 3:** Write failing tests for the matcher based on real `AuthorizedFalsehood`/`KnownFactContext`-shaped fixtures (use the exact field names from `engine/case/models.py` and `engine/characters/context.py` — do not invent a different shape).
- [ ] **Step 4:** Implement `engine/claims/matcher.py` with a function `match_answer_content(*, topic: str, falsehoods: Sequence[AuthorizedFalsehood], known_facts: Sequence[KnownFactContext]) -> AuthorizedFalsehood | KnownFactContext | None`.
- [ ] **Step 5:** Run tests, iterate until PASS.
- [ ] **Step 6: Commit**

```bash
git add engine/claims/errors.py engine/claims/matcher.py engine/tests/test_claims_matcher.py
git commit -m "feat(claims): deterministic question-to-fact/falsehood matcher"
```

---

## Task 5: `ContentEvent` factories for claim/contradiction outcomes

**Goal:** Build outcome-only `ContentEvent`s (no score values) for claim recording and contradiction outcomes, per the confirmed AW-283/AW-284 boundary.

**Files:**
- Create: `engine/claims/events.py`
- Test: `engine/tests/test_claims_events.py`

**Acceptance Criteria:**
- [ ] `build_claim_recorded_event` always uses `AudienceTarget.all` (an answer is always a public interrogation moment, matching AW-282's public-answer routing) and never includes `is_authorized_lie`/`falsehood_id` in its payload (Must Not Do: never expose lie markers pre-reveal).
- [ ] `build_contradiction_outcome_event` uses `AudienceTarget.all` (catches resolve publicly on the TV by default, per the confirmed brief) and carries `outcome` (confirmed/rejected) but **no score value** — scoring is AW-284's job.

**Verify:** `pytest engine/tests/test_claims_events.py -v`

**Steps:**

- [ ] **Step 1:** Read `engine/resources/events.py` in full for the exact `ContentEvent` construction pattern to mirror (same `AudienceTarget`/`EventCategory` imports, same factory-function style).
- [ ] **Step 2:** Write failing tests asserting: (a) `build_claim_recorded_event`'s payload keys never include `is_authorized_lie` or `falsehood_id` (explicit allowlist assertion — this is a Must Not Do, treat the test as a leak guard, not a style check); (b) `build_contradiction_outcome_event`'s payload never includes a numeric score/point field.
- [ ] **Step 3:** Implement both factories in `engine/claims/events.py`, following `engine/resources/events.py`'s exact style (same imports: `from engine.events.models import AudienceTarget, ContentEvent, EventCategory`).
- [ ] **Step 4:** Run tests, iterate until PASS.
- [ ] **Step 5: Commit**

```bash
git add engine/claims/events.py engine/tests/test_claims_events.py
git commit -m "feat(claims): outcome-only ContentEvent factories, no score values in payload"
```

---

## Task 6: Dialogue generation integration — render known facts and authorized lies

**Goal:** Extend the existing spec-0071 dialogue pipeline so a generated answer can draw on an `AuthorizedFalsehood` (rendered with a subtle tell, verbatim `claim_text` on repeat asks) as well as `KnownFactContext` (unchanged from today), and so Rattle the Witness can boost `social_pressure` for one specific question.

**Grounding resolution:** The current `Session` ORM has no persisted `ResolvedCase` attachment; case resolution is held by its owning runtime (for example, the harness). Task 6 therefore adds an explicit optional authorized-falsehood input to context/dialogue assembly rather than inventing a new schema or hidden lookup. The caller that owns a resolved case supplies the sequence, and the default remains empty for existing callers.

**Files:**
- Modify: `engine/characters/context.py` — extend `CharacterGenerationContext` with an `authorized_falsehoods: tuple[AuthorizedFalsehoodContext, ...]` field (new small dataclass mirroring `KnownFactContext`'s shape: `falsehood_id`, `topic`, `claim_text`, `contradicted_by` — do NOT expose `contradicted_by` to the prompt itself, only to the internal claim-recording step; keep prompt-visible and detection-only data separated at the type level if that's cleaner, your call, but the boundary must exist).
- Modify: `engine/characters/dialogue.py` — extend `build_dialogue_messages` to render a lie block when `matcher.match_answer_content` (Task 4) resolves to an `AuthorizedFalsehood` for this question; extend `generate_character_dialogue`'s caller contract so `social_pressure` can be boosted by an active Rattle the Witness effect (the boost computation lives in the caller, per Task 8 — this task only needs to confirm the existing `social_pressure: float | None` parameter is sufficient, or extend it if not).

**Acceptance Criteria:**
- [ ] When the matcher resolves an `AuthorizedFalsehood`, the generated dialogue renders `claim_text` — verbatim, not paraphrased — with a wrapper prompt instruction for a subtle delivery tell (per the confirmed brief). Test this by asserting the exact `claim_text` string appears in the rendered output (not just "a similar phrase").
- [ ] A second call for the same falsehood (simulating a re-ask) renders the identical `claim_text` again — test this explicitly with two calls and an equality assertion on the extracted claim content.
- [ ] `find_unknown_fact_leak` (existing, `engine/characters/dialogue.py`) still passes unmodified for the known/unknown-fact leak-detection case — do not weaken or bypass it while adding the lie path.
- [ ] The prompt-visible lie block never includes `contradicted_by` evidence IDs (that data is detection-only, consumed by `engine/claims/resolver.py` in Task 7, never sent to the model).

**Verify:** `pytest engine/tests/test_character_dialogue.py engine/tests/test_character_generation_context.py -v` (existing spec-0071 test files — must stay green) plus new tests you add to those same files for the lie-rendering path (do not create a parallel test file for this — it belongs with the existing dialogue tests since it extends that pipeline directly).

**Steps:**

- [ ] **Step 1:** Read `engine/characters/dialogue.py`'s `build_dialogue_messages`, `_format_known_block`, `_format_not_known_block`, `_format_pressure_block` in full, and `engine/characters/context.py`'s `CharacterGenerationContext`/`KnownFactContext`/`build_character_generation_context` in full — this task modifies both files and must match their existing patterns exactly, not introduce a divergent style.
- [ ] **Step 2:** Design and add `AuthorizedFalsehoodContext` to `engine/characters/context.py`, following `KnownFactContext`'s `@dataclass(frozen=True)` pattern.
- [ ] **Step 3:** Extend `build_character_generation_context` to populate `authorized_falsehoods` — this requires loading the session's `ResolvedCase.falsehoods` filtered to `speaker_id == character_id` (confirm exactly how a session's `ResolvedCase` is loaded/cached today — check `engine/case/loader.py` and how AW-281's resolved case gets attached to a session, do not assume a mechanism that doesn't exist).
- [ ] **Step 4:** Write a new `_format_lie_block` function in `dialogue.py` mirroring `_format_known_block`'s style, instructing verbatim `claim_text` rendering plus the subtle-tell guidance from the confirmed brief ("slightly less specific, slightly too smooth, or a small hedge — never a substitute for the deterministic check, the tell is flavor only").
- [ ] **Step 5:** Wire `_format_lie_block` into `build_dialogue_messages`, called only when the matcher (Task 4) resolves an `AuthorizedFalsehood` for the current question — pass the matcher's result in as a parameter, do not have `dialogue.py` re-implement matching logic itself (single responsibility: matcher decides *what*, dialogue renders *how*).
- [ ] **Step 6:** Write the new tests (verbatim rendering, repeat-ask consistency, no `contradicted_by` leak into the prompt) into the existing test files per the Verify command above.
- [ ] **Step 7:** Run the full existing spec-0071 test suite plus your additions — confirm zero regressions on the pre-existing tests.
- [ ] **Step 8: Commit**

```bash
git add engine/characters/context.py engine/characters/dialogue.py engine/tests/test_character_dialogue.py engine/tests/test_character_generation_context.py
git commit -m "feat(characters): render authorized lies verbatim in the dialogue pipeline (AW-283)"
```

---

## Task 7: Contradiction resolver — possession-gated detection and tie-break

**Goal:** Implement `ClaimResolver`: record a claim (DB-backed), and resolve a flag against it (possession-gated, deterministic, first-received-wins tie-break).

**Grounding resolution:** The claim ledger stores the authorized-lie marker and falsehood ID, while the current session schema does not persist the resolved case's `contradicted_by` catalog. `ClaimResolver` therefore receives the caller-owned, speaker-scoped `AuthorizedFalsehood` sequence explicitly and combines it with the D-079 knowledge-graph possession query; it must not invent a case lookup, assume cast member IDs are character UUIDs, or duplicate evidence state. The resolver locks the claim row before checking confirmed flags so concurrent flags serialize first-received-wins.

**Files:**
- Create: `engine/claims/resolver.py`
- Test: `engine/tests/test_claims_resolver.py`

**Acceptance Criteria:**
- [ ] `record_claim` persists a `Claim` row (via the ORM model from Task 2) and returns a `ClaimRecord` (Task 3) with `claim_id`/`created_at` populated from the DB.
- [ ] `resolve_flag` on a claim that is NOT an authorized lie rejects deterministically (`ContradictionOutcome.rejected`, `evidence_id_used=None`) — the false-positive guard.
- [ ] `resolve_flag` on a claim that IS an authorized lie, where the flagging participant has NOT been delivered any of its `contradicted_by` evidence (per Task 1's grounding), rejects the same way — internally distinguishable (log which case it was) but identical player-facing event shape, per the confirmed brief ("never exposed pre-reveal").
- [ ] `resolve_flag` on a claim that IS an authorized lie, where the flagging participant HAS been delivered at least one `contradicted_by` evidence entry, confirms (`ContradictionOutcome.confirmed`, `evidence_id_used` set to the specific evidence that justified it).
- [ ] A second `resolve_flag` call on an already-confirmed claim raises `AlreadyResolvedError` (or returns a deterministic rejected-as-already-caught result — pick one and test it explicitly; recommend raising, since the caller (a live session handler) needs to distinguish "this is a genuine new flag" from "someone else already caught this," and a raised error makes that branch explicit rather than silently returning a rejection that looks identical to a false flag).
- [ ] Every `resolve_flag` call persists a `ContradictionFlag` row.

**Verify:** `pytest engine/tests/test_claims_resolver.py -v`

**Steps:**

- [ ] **Step 1:** Read Task 1's grounding note (from your own task history or the plan's Task 1 report) for the exact evidence-possession query. The D-079 `engine/claims/evidence.py` primitives are the sanctioned possession check; AW-280 owns release timing and audience decisions, not this delivery-tracking primitive, so do not add a second state path or wait for an AW-280 call site.
- [ ] **Step 2:** Write failing tests using an in-memory or test-DB-backed fixture (check `engine/tests/test_obligations.py` or `engine/tests/test_telemetry_resources.py` for this codebase's established async-DB test fixture pattern — reuse it, don't invent a new one).
- [ ] **Step 3:** Implement `ClaimResolver` with `async def record_claim(self, db_session: AsyncSession, *, claim: ClaimRecord) -> ClaimRecord` and `async def resolve_flag(self, db_session: AsyncSession, *, claim_id: str, flagging_participant_id: str) -> FlagResult`.
- [ ] **Step 4:** Run tests, iterate until PASS.
- [ ] **Step 5:** Run the full suite `pytest engine/tests/ -q` to confirm no regressions.
- [ ] **Step 6: Commit**

```bash
git add engine/claims/resolver.py engine/tests/test_claims_resolver.py
git commit -m "feat(claims): possession-gated contradiction detection with first-flag-wins tie-break"
```

---

## Task 8: Rattle the Witness integration (AW-287 consumption)

**Goal:** Wire an active Rattle the Witness effect (`engine/resources/`, AW-287) into a `social_pressure` boost for the one question it targets.

**Files:**
- Create or modify: a thin orchestration point that, given a resolved `EffectActivation` with `effect_key == "sabotage.rattle_the_witness"` targeting the current question's speaker, computes a boosted `social_pressure` value to pass into `generate_character_dialogue` (Task 6). Exact file location depends on Task 1/6 findings about where session-level answer generation is actually orchestrated today (likely `engine/session/service.py` or a new thin `engine/claims/` orchestration function — ground this against the real call site before deciding, do not invent a new top-level module for a few lines of glue code).
- Test: append to `engine/tests/test_claims_integration.py` (new file, since this is the first genuinely end-to-end test spanning `engine/resources/` + `engine/claims/` + `engine/characters/`).

**Acceptance Criteria:**
- [ ] When a Rattle the Witness `EffectActivation` targets the current question, `social_pressure` passed to `generate_character_dialogue` is measurably higher than the baseline (session-level) value for that call only — not persisted as a change to the character's ongoing baseline pressure.
- [ ] When no Rattle the Witness effect is active, `social_pressure` passes through unchanged from whatever the existing session-level computation already produces (`engine/characters/initiative.py`) — this task must not change baseline pressure behavior for the non-Leverage case.
- [ ] The specific boost amount is a tuning parameter — pick a reasonable starting value (e.g., enough to guarantee crossing `crumble_threshold` if the character was already close) and note in a comment that Rehearsal 1 telemetry should retune it, matching the pattern already used for AW-287's bank-cap/protected-floor values.

**Verify:** `pytest engine/tests/test_claims_integration.py -v`

**Steps:**

- [ ] **Step 1:** Read `engine/characters/initiative.py`'s `speaker_pressure`/`character_pressure` computation (lines ~413, ~605 per earlier grounding) to find the exact baseline-pressure call site this task boosts on top of.
- [ ] **Step 2:** Write a failing integration test: activate a `sabotage.rattle_the_witness` effect via `engine/resources/` against a target character, then call the generation path and assert the `social_pressure` value used is higher than a control call with no active effect.
- [ ] **Step 3:** Implement the boost computation and wire it into the real call site found in Step 1.
- [ ] **Step 4:** Run tests, iterate until PASS.
- [ ] **Step 5: Commit**

```bash
git add <files found in Step 1/3> engine/tests/test_claims_integration.py
git commit -m "feat(claims): Rattle the Witness boosts per-question social_pressure (AW-287 consumption)"
```

---

## Task 9: Telemetry — claim recording and contradiction outcomes, plus p95 latency

**Goal:** Payload builders + DB recorders for claim/contradiction telemetry, and answer-generation p95 latency recording.

**Files:**
- Create: `engine/telemetry/claims.py`
- Test: `engine/tests/test_telemetry_claims.py`
- Modify: wherever answer generation is timed (the same orchestration point from Task 8) to record latency.

**Acceptance Criteria:**
- [ ] `engine/telemetry/claims.py` mirrors `engine/telemetry/obligations.py`'s pattern exactly (pure payload builders + `async def record_*` recorders writing `Event` ORM rows — reuses the existing generic `events` table for telemetry, which is the correct use of that table per D-078's own reasoning: telemetry is exactly what `events` is for; only the gameplay-critical claim/flag *state* gets the dedicated tables from Task 2).
- [ ] Telemetry payloads for claim recording never include `is_authorized_lie`/`falsehood_id` (same leak-guard as Task 5's `ContentEvent`, but this is the separate telemetry write path — do not assume one guard covers both).
- [ ] Answer-generation latency (start of `generate_character_dialogue` call to receipt of result) is recorded per call; a p95 is computable from the recorded values (test by recording N synthetic latencies and computing p95 over them, proving the aggregation query/method works — not asserting a specific p95 number, since that depends on real model latency this plan can't control).

**Verify:** `pytest engine/tests/test_telemetry_claims.py -v`

**Steps:**

- [ ] **Step 1:** Read `engine/telemetry/obligations.py` and `engine/telemetry/resources.py` (both already exist) side by side; follow whichever's payload-key-allowlist test style is cleaner to replicate exactly.
- [ ] **Step 2:** Write payload builders: `build_claim_recorded_payload`, `build_contradiction_outcome_payload`, `build_answer_latency_payload`.
- [ ] **Step 3:** Write the matching `async def record_*` recorders.
- [ ] **Step 4:** Wire latency timing into the Task 8 orchestration point (wrap the `generate_character_dialogue` call with a timer, call `record_answer_latency` after).
- [ ] **Step 5:** Run tests, iterate until PASS.
- [ ] **Step 6: Commit**

```bash
git add engine/telemetry/claims.py engine/tests/test_telemetry_claims.py <orchestration file from Task 8>
git commit -m "feat(claims): telemetry payload builders and answer-generation latency recording"
```

---

## Task 10: Generic-naming enforcement, full suite, and AW-272 eval batch

**Goal:** Prove `engine/claims/` and `engine/telemetry/claims.py` carry no Nightcap-specific identifiers, and run the AW-272 continuity eval batch against a Couch Race synthetic batch (per the task's own Acceptance Criteria and Tests/Verification sections).

**Files:**
- Create: `engine/tests/test_claims_naming_contract.py` (mirrors `engine/tests/test_resources_naming_contract.py` exactly — same AST-walking approach; forbidden-term list should include game/character-vocabulary terms this module might have accidentally absorbed, e.g. any character names used in test fixtures must stay confined to string literals, never identifiers — check against the same convention `test_resources_naming_contract.py` already established, including the `engine/telemetry/resources.py` coverage-gap lesson from that task: make sure `engine/telemetry/claims.py` is in scope from the start this time, not added as an afterthought).

**Acceptance Criteria:**
- [ ] Naming-contract test passes against the real, final `engine/claims/` and `engine/telemetry/claims.py` files.
- [ ] `pytest engine/tests/ -v` fully green.
- [ ] `python -m ruff check engine api` and `python -m ruff format --check engine api` clean.
- [ ] `pytest evals/runners/test_routing_evals.py -q` still passes (routing changes, if any were made, must not break the existing routing eval suite).
- [ ] AW-272 continuity eval batch runs against a Couch Race synthetic batch and reports zero knowledge leaks on a clean seed — find the actual eval runner (`grep -rn "AW-272\|continuity_eval" evals/` and `docs/` for the runner's real invocation) and run it for real; if it doesn't exist yet as a runnable command, report that gap explicitly rather than claiming this AC is met.

**Verify:** `pytest engine/tests/ -v && python -m ruff check engine api && python -m ruff format --check engine api`

**Steps:**

- [ ] **Step 1:** Write the naming-contract test, adapting `test_resources_naming_contract.py`'s exact structure.
- [ ] **Step 2:** Run it against the real files; fix any violation found (do not weaken the test to pass — if it finds a real leak, fix the leak, matching the precedent from AW-287 Task 7 where this exact test type caught a real bug).
- [ ] **Step 3:** Run the full suite and lint commands from Verify above.
- [ ] **Step 4:** Locate and run the AW-272 eval batch per the Acceptance Criteria above.
- [ ] **Step 5: Commit**

```bash
git add engine/tests/test_claims_naming_contract.py
git commit -m "test(claims): generic-naming enforcement for engine/claims and engine/telemetry/claims"
```

- [ ] **Step 6:** This is the implementation's stopping point. Per the completion roadmap, do NOT record founder sign-off or open the PR from this task — that happens only after the founder reviews an implemented thin slice and explicitly approves it (the same non-skippable gate AW-287 went through). Report your final state (full suite output, naming-contract result, AW-272 eval result) back to whoever is coordinating the handoff to that review step.
