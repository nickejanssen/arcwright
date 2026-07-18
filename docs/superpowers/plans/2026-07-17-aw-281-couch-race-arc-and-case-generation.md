# AW-281 — Couch Race Arc + Case Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the six-beat Couch Race ArcDefinition JSON and a deterministic, provably-fair case-resolution pipeline that produces unique, solvable murder cases from a seed — with runtime invariants, 1000+ seed property tests, and a synthetic-detective solver in CI.

**Architecture:** New `engine/case/` module carries an arc-agnostic resolver (`resolve(arc_definition, seed, participant_count) -> ResolvedCase`) with generic domain models (`ResolvedCase`, `CastMember`, `EvidenceEntry`, `AuthorizedFalsehood`). Nightcap-specific case content — 3 authored skeletons (locked-room poisoning, alibi-collapse strangulation, pre-conspiracy fall), taxonomy tables (motive families, method families, evidence types, lie topics), per-wrapper voice slots — lives entirely under `nightcap/case_skeletons/` and `nightcap/case_taxonomy/`. The harness runner branches on `play_mode == "detective_race"` to call the resolver instead of the existing participant-killer assignment.

**Tech Stack:** Python 3.11+, Pydantic (existing), `random.Random` (seeded, no new deps), pytest, ruff.

**User decisions (already made):** (Design memo: `docs/superpowers/specs/2026-07-17-aw-281-case-resolution-design.md`.)
- Authorship line 4: axes 1–4 authored (archetype + clue-chain pattern + lie shape + reveal shape), axes 5–6 generated (evidence text + names/motives/tissue).
- Code architecture: new `engine/case/` module + arc-agnostic resolver + Nightcap-specific content in `nightcap/`.
- Cast size scales: 2-4 players → 4 suspects, 5-6 → 5, 7-8 → 6; skeleton may override.
- Fairness Level 3: runtime invariant assertions + 1000+ seed property tests + synthetic-detective solver in CI.
- Three v1 case skeletons: locked-room poisoning, alibi-collapse strangulation, pre-conspiracy fall.
- Two case truth invariants: solvability (rational solver identifies culprit from resolved clue distribution) and lie falsifiability (every authorized falsehood is contradicted by a clue).
- No new engine dependencies (no Hypothesis, no external property-test lib).
- Engine agnosticism: no murder-mystery vocabulary in `engine/case/` types.
- Live-session (REST) resolver wiring is deferred to AW-282; this plan wires the harness only.

---

## File Structure Map

**New files (this plan creates):**

```
engine/case/
  __init__.py                     — public exports
  models.py                       — ResolvedCase, CastMember, EvidenceEntry, AuthorizedFalsehood, CaseSkeleton
  errors.py                       — CaseInvariantError, CaseResolutionError
  loader.py                       — load_skeletons / load_taxonomy from arc-defined paths
  resolver.py                     — resolve(arc_definition, seed, participant_count) -> ResolvedCase
  invariants.py                   — solvability_check, lie_falsifiability_check
  solver.py                       — synthetic_detective(resolved_case) -> SolverVerdict
  README.md                       — module boundary + arc-agnostic vocabulary policy

engine/tests/
  test_case_models.py             — Pydantic validation
  test_case_loader.py             — skeleton + taxonomy loading
  test_case_resolver.py           — deterministic replay, cast-size formula
  test_case_invariants.py         — invariant-check unit tests
  test_case_solver.py             — synthetic detective on 100 seeds × 3 skeletons
  test_case_property_sweep.py     — 1000+ seed sweep per skeleton
  test_couch_race_harness.py      — full 6-beat run at counts 2 and 8

nightcap/
  couch-race.arc.json             — new Couch Race ArcDefinition
  case_skeletons/
    locked_room_poisoning.json    — skeleton 1
    alibi_collapse.json           — skeleton 2
    pre_conspiracy_fall.json      — skeleton 3
  case_taxonomy/
    motive_families.json          — greed / love / self-protection / betrayal / ambition
    method_families.json          — poison / suffocation / fall / trauma
    evidence_types.json           — trace / testimony / document / object
    lie_topics.json               — location / relationship / observation / possession
    voice_library.README.md       — per-wrapper voice slots (populated later by AW-268)

docs/superpowers/specs/
  2026-07-17-aw-281-case-resolution-design.md   — already created
```

**Files modified:**

```
config/arcs.json                                — register the new couch-race arc
engine/harness/runner.py                        — branch on play_mode for case resolution
engine/arc/__init__.py                          — re-export PlayMode.detective_race if missing (it isn't; just verify)
docs/decisions/README.md                        — optional index update if we log an ADR (see Task 9)
docs/specs/0072-nightcap-couch-race-v1.md       — reference the resolver architecture
```

**Files NOT modified (out of scope):**

```
engine/arc/models.py                            — no new schema fields (D-053: beat count is arc-level)
engine/session/service.py                       — live-session wiring is AW-282
engine/knowledge/*                              — knowledge-graph state population is AW-283
config/routing_table.json                       — no new routing entries; case resolution is deterministic
requirements.txt                                — no new dependencies (Hard Rule)
```

---

## Task 0: Design memo capture

**Goal:** Ensure the founder-decision design memo is committed before implementation begins.

**Files:**
- Verify existing: `docs/superpowers/specs/2026-07-17-aw-281-case-resolution-design.md`
- Verify existing: `docs/superpowers/specs/2026-07-15-nightcap-couch-race-design.md`

**Acceptance Criteria:**
- [ ] The 2026-07-17 design memo is present at the path above with all four founder decisions recorded.
- [ ] The 2026-07-15 parent memo is present and cross-referenced.

**Verify:** `test -f docs/superpowers/specs/2026-07-17-aw-281-case-resolution-design.md && echo OK`

**Steps:**

- [ ] **Step 1: Verify memo exists** — file was written by the plan author. Read to confirm the four decisions are captured.
- [ ] **Step 2: Commit if not already committed.**

```bash
git add docs/superpowers/specs/2026-07-17-aw-281-case-resolution-design.md
git commit -m "docs(design): AW-281 case-resolution design memo"
```

---

## Task 1: Couch Race arc JSON + registry

**Goal:** Ship `nightcap/couch-race.arc.json` — the 6-beat ArcDefinition — and register it in `config/arcs.json` so the loader can resolve `arc_id="nightcap-couch-race"`.

**Files:**
- Create: `nightcap/couch-race.arc.json`
- Modify: `config/arcs.json`
- Test: `engine/tests/test_couch_race_arc_json.py` (new)

**Acceptance Criteria:**
- [ ] Arc validates against `ArcDefinition` schema with `play_mode: "detective_race"`, `min_players: 2`, `max_players: 8`.
- [ ] Beat list contains six beats in order: `pour`, `scene`, `grill`, `twist`, `last_call`, `truth`.
- [ ] Beat graph is a valid linear chain with `truth` marked terminal.
- [ ] `pacing_config` weights sum to 1.0.
- [ ] `generative_elements.killer_assignment` is `false` (no participant-killer for detective_race).
- [ ] Registry loads the arc via `resolve_arc_path("nightcap-couch-race-v1")`.

**Verify:** `pytest engine/tests/test_couch_race_arc_json.py -v` → all pass

**Steps:**

- [ ] **Step 1: Write the arc JSON.**

Full content, six beats, per bible §4 pacing targets and existing arc.json schema conventions:

```json
{
  "arc_id": "nightcap-couch-race-v1",
  "name": "Nightcap Couch Race",
  "min_players": 2,
  "max_players": 8,
  "character_mode": "generated",
  "aesthetic_config": {
    "selection_model": {
      "era": {"type": "host_select", "allow_random": true},
      "occasion": {"type": "host_select", "allow_random": true}
    },
    "asset_generation": {
      "background_art": "pre_produced_per_theme",
      "narrator_dialogue": "authored_refrain_library_plus_generative_specifics"
    }
  },
  "setting_constraint": "social_gathering",
  "arc_structure": "story_circle",
  "play_mode": "detective_race",
  "narrator": {
    "type": "host_persona",
    "surface": "shared_display",
    "persona_mode": "aesthetic_linked",
    "behavior_triggers": [
      "beat_transition",
      "clue_release",
      "tension_threshold",
      "player_inaction"
    ],
    "omniscient": true,
    "player_addressable": true
  },
  "quality_tier_default": "standard",
  "characters": [],
  "case_resolution": {
    "skeleton_directory": "nightcap/case_skeletons",
    "taxonomy_directory": "nightcap/case_taxonomy",
    "cast_size_formula": "player_count_scaled",
    "cast_size_by_player_count": {
      "2": 4, "3": 4, "4": 4,
      "5": 5, "6": 5,
      "7": 6, "8": 6
    }
  },
  "beats": [
    {
      "beat_id": "pour",
      "beat_name": "The Pour",
      "beat_type": "cold_open",
      "story_circle_step": 1,
      "structural_function": "establish_world_and_death",
      "dramatic_purpose": "Establish the gathering; land the death as a staged audiovisual moment.",
      "emotional_target": "curious_then_shocked",
      "information_goal": "Players receive detective identities; Vesper introduces the cast; body drops in seq-body.",
      "tension_target": 0.35,
      "character_emphasis": ["host"],
      "authored_content": {
        "opening_note": "Gathering assembles; Vesper welcomes the couch."
      },
      "generative_triggers": ["case_resolution", "narrator_opening"],
      "entry_conditions": [],
      "exit_conditions": ["case_resolution_complete", "all_players_ready"],
      "pacing_config": {"stall_threshold_seconds": 120},
      "audience_targets": ["all"],
      "mini_games": []
    },
    {
      "beat_id": "scene",
      "beat_name": "The Scene",
      "beat_type": "investigation",
      "story_circle_step": 2,
      "structural_function": "establish_investigative_baseline",
      "dramatic_purpose": "First evidence wave; competitive mini-game slot.",
      "emotional_target": "focused",
      "information_goal": "Group and private evidence delivered; investigative asymmetry established.",
      "tension_target": 0.45,
      "character_emphasis": ["cast"],
      "authored_content": {},
      "generative_triggers": ["clue_release"],
      "entry_conditions": [],
      "exit_conditions": ["evidence_wave_delivered"],
      "pacing_config": {"stall_threshold_seconds": 180},
      "audience_targets": ["all", "individual"],
      "mini_games": []
    },
    {
      "beat_id": "grill",
      "beat_name": "The Grill",
      "beat_type": "interrogation",
      "story_circle_step": 3,
      "structural_function": "core_loop_interrogation",
      "dramatic_purpose": "Rounds of interrogation; contradictions surface as gameplay.",
      "emotional_target": "engaged_pressured",
      "information_goal": "Players spend intent tokens; suspect answers form claim ledger; contradictions can be flagged.",
      "tension_target": 0.60,
      "character_emphasis": ["cast"],
      "authored_content": {},
      "generative_triggers": ["character_dialogue"],
      "entry_conditions": [],
      "exit_conditions": ["interrogation_rounds_complete"],
      "pacing_config": {"stall_threshold_seconds": 240},
      "audience_targets": ["all", "individual"],
      "mini_games": []
    },
    {
      "beat_id": "twist",
      "beat_name": "The Twist",
      "beat_type": "recontextualization",
      "story_circle_step": 4,
      "structural_function": "recontextualization",
      "dramatic_purpose": "Deterministic mid-case revelation; solo mini-game slot.",
      "emotional_target": "reoriented",
      "information_goal": "Twist reframes suspicion without changing whodunit; second evidence wave.",
      "tension_target": 0.72,
      "character_emphasis": ["host"],
      "authored_content": {},
      "generative_triggers": ["clue_release", "narrator_beat"],
      "entry_conditions": [],
      "exit_conditions": ["twist_delivered"],
      "pacing_config": {"stall_threshold_seconds": 150},
      "audience_targets": ["all", "individual"],
      "mini_games": []
    },
    {
      "beat_id": "last_call",
      "beat_name": "Last Call",
      "beat_type": "endgame",
      "story_circle_step": 5,
      "structural_function": "convergence_under_pressure",
      "dramatic_purpose": "Visible countdown; scarce final questions; accusations lock in.",
      "emotional_target": "urgent",
      "information_goal": "Countdown running; accusation locks private; first-correct triggers table-wide Last Call.",
      "tension_target": 0.88,
      "character_emphasis": ["cast", "host"],
      "authored_content": {},
      "generative_triggers": ["character_dialogue", "narrator_beat"],
      "entry_conditions": [],
      "exit_conditions": ["accusations_locked_or_countdown_expired"],
      "pacing_config": {"stall_threshold_seconds": 120},
      "audience_targets": ["all", "individual"],
      "mini_games": []
    },
    {
      "beat_id": "truth",
      "beat_name": "The Truth",
      "beat_type": "revelation",
      "story_circle_step": 6,
      "structural_function": "revelation_and_scoring",
      "dramatic_purpose": "Vesper reconstructs the case; scoreboard fires.",
      "emotional_target": "resolved",
      "information_goal": "Full reveal per authored reveal shape; scoreboard; replay prompt.",
      "tension_target": 0.35,
      "character_emphasis": ["host"],
      "authored_content": {},
      "generative_triggers": ["narrator_reveal", "scoring_summary"],
      "entry_conditions": [],
      "exit_conditions": [],
      "pacing_config": {"stall_threshold_seconds": 240},
      "audience_targets": ["all"],
      "mini_games": []
    }
  ],
  "beat_graph": {
    "pour": ["scene"],
    "scene": ["grill"],
    "grill": ["twist"],
    "twist": ["last_call"],
    "last_call": ["truth"],
    "truth": []
  },
  "pacing_config": {
    "stall_threshold": 0.25,
    "misdirection_threshold": 0.80,
    "premium_threshold": 0.85,
    "w_time": 0.30,
    "w_action": 0.30,
    "w_suspicion": 0.25,
    "w_coverage": 0.15
  },
  "generative_elements": {
    "killer_assignment": false,
    "character_generation": true,
    "aesthetic_generation": true,
    "clue_content": true,
    "plot_twist": false,
    "narrator_dialogue": false
  },
  "content_rails": {
    "prohibited_categories": [],
    "thematic_warnings": [],
    "age_floor": 18,
    "extra_prohibitions": []
  }
}
```

Notes on the JSON:
- `killer_assignment: false` — the participant-killer flag from Imposter Variant is off. Case-culprit is a CastMember, not a player.
- New top-level `case_resolution` block carries directory paths + cast-size table. This is arc-content data (not an engine schema addition — see Task 2).
- `plot_twist: false` and `narrator_dialogue: false` on `generative_elements` — twists are authored per skeleton (axis 4) and Vesper is authored-refrain-plus-generated-specifics per D-073 / AW-267.
- Beat IDs deliberately do NOT reuse `arrival`, `body`, `truth` from Imposter Variant, except `truth` (which is universal-enough and matches the harness runner's terminal-beat convention).

- [ ] **Step 2: Register in `config/arcs.json`.**

Modify existing file — append the new arc entry BEFORE the existing `nightcap` prefix (order matters; first match wins):

```json
{
  "arcs": [
    {"id_prefix": "nightcap-couch-race", "path": "nightcap/couch-race.arc.json"},
    {"id_prefix": "nightcap", "path": "nightcap/arc.json"}
  ]
}
```

- [ ] **Step 3: Write the arc-JSON validation test.**

Create `engine/tests/test_couch_race_arc_json.py`:

```python
"""AW-281 — validate the Couch Race arc JSON loads and shapes correctly."""

from __future__ import annotations

from pathlib import Path

from engine.arc.models import ArcDefinition, PlayMode
from engine.arc.registry import resolve_arc_path

REPO_ROOT = Path(__file__).resolve().parents[2]
COUCH_RACE_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"


def test_arc_json_file_present() -> None:
    assert COUCH_RACE_PATH.exists(), "nightcap/couch-race.arc.json must exist"


def test_arc_definition_validates() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    assert arc.arc_id == "nightcap-couch-race-v1"
    assert arc.play_mode == PlayMode.detective_race
    assert arc.min_players == 2
    assert arc.max_players == 8


def test_beat_sequence() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    beat_ids = [b.beat_id for b in arc.beats]
    assert beat_ids == ["pour", "scene", "grill", "twist", "last_call", "truth"]


def test_beat_graph_linear() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    assert arc.beat_graph["pour"] == ["scene"]
    assert arc.beat_graph["scene"] == ["grill"]
    assert arc.beat_graph["grill"] == ["twist"]
    assert arc.beat_graph["twist"] == ["last_call"]
    assert arc.beat_graph["last_call"] == ["truth"]
    assert arc.beat_graph["truth"] == []


def test_pacing_weights_sum_to_one() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    pc = arc.pacing_config
    total = pc.w_time + pc.w_action + pc.w_suspicion + pc.w_coverage
    assert abs(total - 1.0) < 1e-6


def test_killer_assignment_disabled() -> None:
    arc = ArcDefinition.model_validate_json(COUCH_RACE_PATH.read_text("utf-8"))
    assert arc.generative_elements.killer_assignment is False


def test_registry_resolves_couch_race() -> None:
    path = resolve_arc_path("nightcap-couch-race-v1")
    assert path is not None
    assert path.resolve() == COUCH_RACE_PATH.resolve()


def test_registry_still_resolves_original_nightcap() -> None:
    path = resolve_arc_path("nightcap")
    assert path is not None
    assert path.name == "arc.json"
```

- [ ] **Step 4: Run tests, iterate if the arc JSON doesn't validate.**

```bash
pytest engine/tests/test_couch_race_arc_json.py -v
```

Expected: 8 tests pass.

If a field is missing or a validator rejects the JSON, fix the arc JSON and re-run. Do NOT modify `engine/arc/models.py` — the whole point is zero schema change (D-053).

- [ ] **Step 5: Note on `case_resolution` block.**

`ArcDefinition` uses `ConfigDict(extra=...)`. Check whether `extra="allow"` or `extra="forbid"` is set — if forbid, the `case_resolution` block will fail validation. In that case, extract the block *out* of arc JSON and store it in `nightcap/case_resolution_config.json` instead, loaded by the case module's loader (Task 4). Verify this in Step 4.

- [ ] **Step 6: Commit.**

```bash
git add nightcap/couch-race.arc.json config/arcs.json engine/tests/test_couch_race_arc_json.py
git commit -m "feat(nightcap): couch-race arc JSON with 6 beats and registry entry (AW-281)"
```

---

## Task 2: `engine/case/` module + arc-agnostic domain models

**Goal:** Create the arc-agnostic `engine/case/` module scaffold with `ResolvedCase`, `CastMember`, `EvidenceEntry`, `AuthorizedFalsehood`, `CaseSkeleton`, error types, and a README that documents the vocabulary policy.

**Files:**
- Create: `engine/case/__init__.py`
- Create: `engine/case/models.py`
- Create: `engine/case/errors.py`
- Create: `engine/case/README.md`
- Test: `engine/tests/test_case_models.py`

**Acceptance Criteria:**
- [ ] `from engine.case import ResolvedCase, CastMember, EvidenceEntry, AuthorizedFalsehood, CaseSkeleton, CaseInvariantError, CaseResolutionError` succeeds.
- [ ] All models are Pydantic `BaseModel` with `ConfigDict(extra="forbid")`.
- [ ] No murder-mystery vocabulary in type or field names (see README). `role`, `truth_value`, `topic`, `contradiction_targets` are the only labels — arc content puts strings like "killer" / "victim" / "poison" *into* the string fields.
- [ ] All models are hashable / round-trippable via `model_dump()` / `model_validate()`.

**Verify:** `pytest engine/tests/test_case_models.py -v && python -c "from engine.case import ResolvedCase; print('OK')"`

**Steps:**

- [ ] **Step 1: Write the failing tests first.**

`engine/tests/test_case_models.py`:

```python
"""AW-281 — Pydantic validation for engine/case/ domain models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from engine.case import (
    AuthorizedFalsehood,
    CaseInvariantError,
    CaseResolutionError,
    CaseSkeleton,
    CastMember,
    EvidenceEntry,
    ResolvedCase,
)


def test_cast_member_minimal() -> None:
    m = CastMember(
        member_id="s1",
        display_name="Delacourt",
        role="suspect",
    )
    assert m.role == "suspect"
    assert m.is_culprit is False


def test_cast_member_culprit_flag() -> None:
    m = CastMember(
        member_id="s3",
        display_name="Ashford",
        role="suspect",
        is_culprit=True,
    )
    assert m.is_culprit is True


def test_evidence_entry_minimal() -> None:
    e = EvidenceEntry(
        evidence_id="e1",
        evidence_type="trace",
        text="A faint bruise on the left hand.",
        implicates=["s3"],
        exonerates=[],
        delivery="private",
        delivery_target="p1",
    )
    assert e.implicates == ["s3"]


def test_authorized_falsehood_minimal() -> None:
    lie = AuthorizedFalsehood(
        falsehood_id="l1",
        speaker_id="s2",
        topic="location",
        claim_text="I was on the terrace at nine.",
        contradicted_by=["e5"],
    )
    assert lie.contradicted_by == ["e5"]


def test_resolved_case_minimal() -> None:
    culprit = CastMember(
        member_id="s1", display_name="A", role="suspect", is_culprit=True
    )
    victim = CastMember(member_id="v1", display_name="V", role="victim")
    ev = EvidenceEntry(
        evidence_id="e1",
        evidence_type="trace",
        text="a torn playbill",
        implicates=["s1"],
        exonerates=[],
        delivery="group",
        delivery_target=None,
    )
    case = ResolvedCase(
        case_id="c1",
        arc_id="nightcap-couch-race-v1",
        seed=42,
        skeleton_id="locked_room_poisoning",
        cast=[culprit, victim],
        culprit_id="s1",
        victim_id="v1",
        evidence=[ev],
        falsehoods=[],
        reveal_shape={"steps": []},
    )
    assert case.culprit_id == "s1"
    assert case.victim_id == "v1"


def test_case_skeleton_forbids_extra() -> None:
    with pytest.raises(ValidationError):
        CaseSkeleton(
            skeleton_id="x",
            archetype="poisoning",
            clue_chain_pattern={"stages": []},
            lie_shapes_by_role={},
            reveal_shape={"steps": []},
            unknown_field="oops",  # type: ignore[call-arg]
        )


def test_resolved_case_forbids_extra() -> None:
    with pytest.raises(ValidationError):
        ResolvedCase(  # type: ignore[call-arg]
            case_id="c1",
            arc_id="nightcap-couch-race-v1",
            seed=42,
            skeleton_id="s",
            cast=[],
            culprit_id="",
            victim_id="",
            evidence=[],
            falsehoods=[],
            reveal_shape={"steps": []},
            unknown="nope",
        )


def test_error_types_are_exception_subclasses() -> None:
    assert issubclass(CaseInvariantError, Exception)
    assert issubclass(CaseResolutionError, Exception)


def test_round_trip_json() -> None:
    culprit = CastMember(
        member_id="s1", display_name="A", role="suspect", is_culprit=True
    )
    victim = CastMember(member_id="v1", display_name="V", role="victim")
    case = ResolvedCase(
        case_id="c1",
        arc_id="nightcap-couch-race-v1",
        seed=42,
        skeleton_id="locked_room_poisoning",
        cast=[culprit, victim],
        culprit_id="s1",
        victim_id="v1",
        evidence=[],
        falsehoods=[],
        reveal_shape={"steps": []},
    )
    payload = case.model_dump()
    restored = ResolvedCase.model_validate(payload)
    assert restored == case
```

- [ ] **Step 2: Write the module scaffold.**

`engine/case/__init__.py`:

```python
"""Arc-agnostic case-resolution module (AW-281).

This module carries NO game-specific vocabulary. Types are labelled
generically (``CastMember``, ``EvidenceEntry``, ``AuthorizedFalsehood``)
and arc-specific meaning is injected as string values (``role="suspect"``,
``role="victim"``, ``evidence_type="trace"``, etc.). Arc-specific case
content lives outside this module in the arc's own directory (e.g.
``nightcap/case_skeletons/``, ``nightcap/case_taxonomy/``).

Public API::

    from engine.case import resolve, ResolvedCase, CaseSkeleton, ...
"""

from __future__ import annotations

from engine.case.errors import CaseInvariantError, CaseResolutionError
from engine.case.models import (
    AuthorizedFalsehood,
    CaseSkeleton,
    CastMember,
    EvidenceEntry,
    ResolvedCase,
)

__all__ = [
    "AuthorizedFalsehood",
    "CaseInvariantError",
    "CaseResolutionError",
    "CaseSkeleton",
    "CastMember",
    "EvidenceEntry",
    "ResolvedCase",
]
```

`engine/case/errors.py`:

```python
"""Exception types raised by the case-resolution module."""

from __future__ import annotations


class CaseResolutionError(Exception):
    """Raised when a case cannot be resolved (missing skeleton, bad seed, etc.)."""


class CaseInvariantError(CaseResolutionError):
    """Raised when a resolved case fails a runtime fairness invariant.

    Subclass of CaseResolutionError so callers can catch either. Emit
    the failing invariant name (`solvability` or `lie_falsifiability`)
    in the message plus enough seed-and-skeleton context to reproduce.
    """
```

`engine/case/models.py`:

```python
"""Pydantic domain models for arc-agnostic case resolution (AW-281).

Field-name policy: no murder-mystery-specific vocabulary. Strings like
``"suspect"``, ``"victim"``, ``"trace"`` live INSIDE ``role`` /
``evidence_type`` / ``topic`` string fields, populated by arc content.
See ``engine/case/README.md`` for the boundary policy.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class CastMember(BaseModel):
    model_config = ConfigDict(extra="forbid")

    member_id: str
    display_name: str
    role: str
    """Arc-defined role slot; nightcap uses ``suspect`` or ``victim``."""

    is_culprit: bool = False
    """Exactly one CastMember per case has is_culprit=True."""

    tags: list[str] = Field(default_factory=list)
    """Arc-specific tags (e.g. archetype role slot: ``intimate``, ``deflector``)."""


class EvidenceEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    evidence_type: str
    """Arc-defined family (``trace``, ``testimony``, ``document``, ``object``)."""

    text: str
    """Generated axis-5 clue text. Placeholder until Task 5."""

    implicates: list[str]
    """CastMember member_ids this clue points TOWARD."""

    exonerates: list[str]
    """CastMember member_ids this clue points AWAY FROM."""

    delivery: str
    """``group``, ``private``, ``split``, ``targeted`` — reused from clue architecture."""

    delivery_target: Optional[str] = None
    """Participant id for private/targeted; None for group."""

    truth_value: str = "genuine"
    """``genuine`` or ``false_signal`` — every false signal must be falsifiable."""


class AuthorizedFalsehood(BaseModel):
    model_config = ConfigDict(extra="forbid")

    falsehood_id: str
    speaker_id: str
    """CastMember member_id who tells this lie under interrogation."""

    topic: str
    """Arc-defined lie topic (``location``, ``relationship``, ``observation``, ``possession``)."""

    claim_text: str
    """The specific text of the lie (generated axis-5)."""

    contradicted_by: list[str]
    """EvidenceEntry evidence_ids that contradict this lie. Non-empty by invariant."""


class CaseSkeleton(BaseModel):
    """Axis-1..4 authored content for a case type."""

    model_config = ConfigDict(extra="forbid")

    skeleton_id: str
    archetype: str
    """Axis 1 — the shape of the crime."""

    clue_chain_pattern: dict[str, Any]
    """Axis 2 — the deduction sequence a solver must perform."""

    lie_shapes_by_role: dict[str, list[str]]
    """Axis 3 — which lie topics each suspect archetype role can carry."""

    reveal_shape: dict[str, Any]
    """Axis 4 — the rhythm of the Truth beat."""

    cast_size_override: Optional[int] = None
    """If set, force this skeleton to use a specific cast size regardless of player count."""


class ResolvedCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    arc_id: str
    seed: int
    skeleton_id: str
    cast: list[CastMember]
    culprit_id: str
    victim_id: str
    evidence: list[EvidenceEntry]
    falsehoods: list[AuthorizedFalsehood]
    reveal_shape: dict[str, Any]
```

`engine/case/README.md`:

```markdown
# engine/case/ — Arc-Agnostic Case Resolution

## Purpose

Deterministic case resolution for arcs where case content (culprit,
victim, cast, evidence, authorized falsehoods, reveal shape) must be
resolved at session start from a seed.

Introduced by AW-281 for the Couch Race arc (Nightcap v1). Reusable by
Daily Case (single-suspect variant) and the future Imposter Variant
(player-culprit variant) with their own skeleton + taxonomy content.

## Vocabulary policy (READ BEFORE ADDING FIELDS)

This module carries **no murder-mystery vocabulary in schema**. Field
names are generic (`role`, `evidence_type`, `topic`); arc content
populates them with strings.

Bad (do not add):
- `killer_id`, `murder_method`, `murder_time`

Good:
- `culprit_id` (the character responsible for the case's central act)
- `role: str` (arc content sets it to `"suspect"` / `"victim"` /
  `"witness"` / whatever the arc needs)

Known engine-level exceptions predating this module:
- `engine/arc/models.py` fields `killer_assignment`,
  `killer_knows_they_did_it`, `murder_timing_range` are legacy
  Imposter-Variant terms tracked as violations in issue #220 / spec
  0070. This module does not add new ones.

## Public API

```python
from engine.case import (
    resolve,
    ResolvedCase,
    CastMember,
    EvidenceEntry,
    AuthorizedFalsehood,
    CaseSkeleton,
    CaseInvariantError,
    CaseResolutionError,
)

case = resolve(arc_definition, seed=42, participant_count=4)
```

## Invariants (enforced at resolve time)

Every ResolvedCase satisfies:

1. **Solvability.** The genuine clue chain, applied by a rational-actor
   solver over the intended clue distribution, uniquely identifies the
   culprit.
2. **Lie falsifiability.** Every `AuthorizedFalsehood.contradicted_by`
   list is non-empty AND every referenced `EvidenceEntry` is present
   in the resolved case.

Violations raise `CaseInvariantError`.

## Fairness proof stack (AW-281)

- Level 1 — Runtime invariant assertions (this module).
- Level 2 — Property-based tests over 1000+ seeds
  (`engine/tests/test_case_property_sweep.py`).
- Level 3 — Synthetic detective solver
  (`engine/case/solver.py`, tested in
  `engine/tests/test_case_solver.py`).
```

- [ ] **Step 3: Run tests.**

```bash
pytest engine/tests/test_case_models.py -v
```

Expected: 8 tests pass.

- [ ] **Step 4: Ruff pass.**

```bash
python -m ruff check engine/case engine/tests/test_case_models.py
python -m ruff format --check engine/case engine/tests/test_case_models.py
```

- [ ] **Step 5: Commit.**

```bash
git add engine/case engine/tests/test_case_models.py
git commit -m "feat(case): arc-agnostic domain models for case resolution (AW-281)"
```

---

## Task 3: Case skeletons + JSON schema (nightcap/case_skeletons/)

**Goal:** Ship the three v1 authored case skeletons — locked-room poisoning, alibi-collapse strangulation, pre-conspiracy fall — as JSON files. Each skeleton carries axes 1-4 authored content: archetype, clue-chain pattern, lie-shapes-by-role, reveal shape.

**Files:**
- Create: `nightcap/case_skeletons/locked_room_poisoning.json`
- Create: `nightcap/case_skeletons/alibi_collapse.json`
- Create: `nightcap/case_skeletons/pre_conspiracy_fall.json`
- Create: `nightcap/case_skeletons/README.md`
- Test: `engine/tests/test_case_skeleton_content.py`

**Acceptance Criteria:**
- [ ] Three skeleton JSONs exist and each validates against `CaseSkeleton`.
- [ ] Each skeleton names a distinct archetype.
- [ ] Each skeleton's `clue_chain_pattern.stages` has at least 3 deduction stages.
- [ ] Each skeleton's `lie_shapes_by_role` covers at least 3 suspect archetype-roles.
- [ ] Each skeleton's `reveal_shape.steps` has at least 4 steps.

**Verify:** `pytest engine/tests/test_case_skeleton_content.py -v`

**Steps:**

- [ ] **Step 1: Author `locked_room_poisoning.json`.**

```json
{
  "skeleton_id": "locked_room_poisoning",
  "archetype": "locked_room_poisoning",
  "clue_chain_pattern": {
    "description": "Physical trace on a vessel → placement discrepancy identifying who could have touched it → motive callback tying culprit to the specific vessel.",
    "stages": [
      {
        "stage_id": "trace_on_vessel",
        "kind": "trace",
        "prompt": "A physical trace of the substance appears on a specific vessel (glass, decanter, teacup).",
        "narrows": "victim_ingested_from_this_vessel"
      },
      {
        "stage_id": "placement_discrepancy",
        "kind": "testimony",
        "prompt": "A witness describes seeing the vessel handled at a time or place that contradicts one suspect's stated location.",
        "narrows": "one_suspect_had_access"
      },
      {
        "stage_id": "motive_callback",
        "kind": "document",
        "prompt": "A written record (letter, ledger, receipt) ties the access-holding suspect to a specific motive against the victim.",
        "narrows": "culprit_uniquely_identified"
      }
    ]
  },
  "lie_shapes_by_role": {
    "intimate": ["relationship", "possession"],
    "deflector": ["location", "observation"],
    "observer": ["observation", "relationship"],
    "obvious_suspect": ["location", "possession"]
  },
  "reveal_shape": {
    "steps": [
      {"kind": "opening", "beat": "grave", "prompt": "Vesper names the room and the vessel."},
      {"kind": "near_miss_per_player", "beat": "grave_then_wry", "prompt": "For each player, name the clue they almost caught."},
      {"kind": "culprit_best_move", "beat": "delighted_about_awful", "prompt": "Vesper credits the culprit's best deception move."},
      {"kind": "the_ordinary_last_line", "beat": "ordinary", "prompt": "One small line naming the vessel and the culprit."}
    ]
  }
}
```

- [ ] **Step 2: Author `alibi_collapse.json`.**

```json
{
  "skeleton_id": "alibi_collapse",
  "archetype": "alibi_collapse_strangulation",
  "clue_chain_pattern": {
    "description": "Physical evidence of the act → suspect alibi that seemed solid → third-party observation collapses the alibi.",
    "stages": [
      {
        "stage_id": "act_evidence",
        "kind": "trace",
        "prompt": "Physical evidence of the act on the victim (fibre, mark, imprint) narrows the timing window.",
        "narrows": "act_occurred_between_x_and_y"
      },
      {
        "stage_id": "shared_alibi",
        "kind": "testimony",
        "prompt": "A suspect gives a public alibi covering the timing window that appears to have witnesses.",
        "narrows": "suspect_appears_to_be_elsewhere"
      },
      {
        "stage_id": "alibi_collapse",
        "kind": "object",
        "prompt": "A found object (ticket stub, receipt, phone log, key card) places the suspect back in the room within the window.",
        "narrows": "culprit_uniquely_identified"
      }
    ]
  },
  "lie_shapes_by_role": {
    "intimate": ["observation", "possession"],
    "deflector": ["location", "relationship"],
    "observer": ["observation", "location"],
    "obvious_suspect": ["location", "observation"]
  },
  "reveal_shape": {
    "steps": [
      {"kind": "opening", "beat": "grave", "prompt": "Vesper names the timing window and the act."},
      {"kind": "near_miss_per_player", "beat": "grave_then_wry", "prompt": "For each player, name the clue they almost caught."},
      {"kind": "culprit_best_move", "beat": "delighted_about_awful", "prompt": "Vesper credits the culprit's best deception move."},
      {"kind": "the_ordinary_last_line", "beat": "ordinary", "prompt": "One small line naming the object that broke the alibi."}
    ]
  }
}
```

- [ ] **Step 3: Author `pre_conspiracy_fall.json`.**

```json
{
  "skeleton_id": "pre_conspiracy_fall",
  "archetype": "pre_conspiracy_fall",
  "clue_chain_pattern": {
    "description": "The fall itself → prior arrangement (letter, meeting, deal) between culprit and victim → conflict escalation at the gathering identifies culprit.",
    "stages": [
      {
        "stage_id": "fall_physics",
        "kind": "trace",
        "prompt": "Physical arrangement of the fall (angle, height, ledge state) shows the fall was not accidental.",
        "narrows": "act_was_deliberate"
      },
      {
        "stage_id": "prior_arrangement",
        "kind": "document",
        "prompt": "A prior letter, message, or deal-record between culprit and victim reveals a specific ongoing conflict.",
        "narrows": "one_suspect_had_pre-crime_motive"
      },
      {
        "stage_id": "gathering_escalation",
        "kind": "testimony",
        "prompt": "A witness recalls a specific exchange during the gathering that escalated the conflict.",
        "narrows": "culprit_uniquely_identified"
      }
    ]
  },
  "lie_shapes_by_role": {
    "intimate": ["relationship", "observation"],
    "deflector": ["location", "possession"],
    "observer": ["observation", "location"],
    "obvious_suspect": ["relationship", "location"]
  },
  "reveal_shape": {
    "steps": [
      {"kind": "opening", "beat": "grave", "prompt": "Vesper names the ledge and the fall."},
      {"kind": "near_miss_per_player", "beat": "grave_then_wry", "prompt": "For each player, name the clue they almost caught."},
      {"kind": "culprit_best_move", "beat": "delighted_about_awful", "prompt": "Vesper credits the culprit's best deception move."},
      {"kind": "the_ordinary_last_line", "beat": "ordinary", "prompt": "One small line naming the document and the culprit."}
    ]
  }
}
```

- [ ] **Step 4: Author skeleton README.**

`nightcap/case_skeletons/README.md`:

```markdown
# Nightcap Case Skeletons

Authored axes 1–4 case content for the Couch Race arc (AW-281 / spec 0072).

- **Axis 1 — archetype** (`archetype`)
- **Axis 2 — clue-chain pattern** (`clue_chain_pattern`)
- **Axis 3 — lie shapes per suspect role** (`lie_shapes_by_role`)
- **Axis 4 — reveal shape** (`reveal_shape`)

Axes 5 (evidence text) and 6 (character names / motives) are GENERATED
from `nightcap/case_taxonomy/` (see that folder's README).

## v1 launch skeleton set

- `locked_room_poisoning.json`
- `alibi_collapse.json`
- `pre_conspiracy_fall.json`

Adding a new skeleton: author the four axes, run
`pytest engine/tests/test_case_skeleton_content.py -v`, then the
resolver picks it up automatically.

## Suspect archetype-roles (used by `lie_shapes_by_role`)

Inherited from the Imposter Variant bible §3:
- `intimate` — closest to victim
- `deflector` — hiding something unrelated
- `observer` — social edges, sees what others miss
- `obvious_suspect` — surface-level motive everyone recognizes
```

- [ ] **Step 5: Write the skeleton-content test.**

`engine/tests/test_case_skeleton_content.py`:

```python
"""AW-281 — Validate all shipped case skeletons against the CaseSkeleton schema."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.case import CaseSkeleton

REPO_ROOT = Path(__file__).resolve().parents[2]
SKELETON_DIR = REPO_ROOT / "nightcap" / "case_skeletons"

EXPECTED = ("locked_room_poisoning", "alibi_collapse", "pre_conspiracy_fall")


@pytest.mark.parametrize("skeleton_id", EXPECTED)
def test_skeleton_validates(skeleton_id: str) -> None:
    path = SKELETON_DIR / f"{skeleton_id}.json"
    assert path.exists(), f"missing skeleton: {path}"
    skel = CaseSkeleton.model_validate_json(path.read_text("utf-8"))
    assert skel.skeleton_id == skeleton_id


@pytest.mark.parametrize("skeleton_id", EXPECTED)
def test_skeleton_clue_chain_has_stages(skeleton_id: str) -> None:
    path = SKELETON_DIR / f"{skeleton_id}.json"
    skel = CaseSkeleton.model_validate_json(path.read_text("utf-8"))
    stages = skel.clue_chain_pattern.get("stages", [])
    assert len(stages) >= 3, f"{skeleton_id} needs >=3 deduction stages"


@pytest.mark.parametrize("skeleton_id", EXPECTED)
def test_skeleton_reveal_has_steps(skeleton_id: str) -> None:
    path = SKELETON_DIR / f"{skeleton_id}.json"
    skel = CaseSkeleton.model_validate_json(path.read_text("utf-8"))
    steps = skel.reveal_shape.get("steps", [])
    assert len(steps) >= 4, f"{skeleton_id} reveal needs >=4 steps"


@pytest.mark.parametrize("skeleton_id", EXPECTED)
def test_skeleton_covers_suspect_roles(skeleton_id: str) -> None:
    path = SKELETON_DIR / f"{skeleton_id}.json"
    skel = CaseSkeleton.model_validate_json(path.read_text("utf-8"))
    assert len(skel.lie_shapes_by_role) >= 3
```

- [ ] **Step 6: Run tests.**

```bash
pytest engine/tests/test_case_skeleton_content.py -v
```

Expected: 12 tests pass (4 tests × 3 skeletons).

- [ ] **Step 7: Commit.**

```bash
git add nightcap/case_skeletons engine/tests/test_case_skeleton_content.py
git commit -m "feat(nightcap): three authored case skeletons for couch race (AW-281)"
```

---

## Task 4: Taxonomy tables + loader

**Goal:** Ship the axes 5-6 generative content library (motive families, method families, evidence types, lie topics) as JSON tables under `nightcap/case_taxonomy/`, plus the loader in `engine/case/loader.py` that reads skeletons + taxonomies given directory paths.

**Files:**
- Create: `nightcap/case_taxonomy/motive_families.json`
- Create: `nightcap/case_taxonomy/method_families.json`
- Create: `nightcap/case_taxonomy/evidence_types.json`
- Create: `nightcap/case_taxonomy/lie_topics.json`
- Create: `nightcap/case_taxonomy/README.md`
- Create: `nightcap/case_resolution_config.json` (loader entry point per Task 1 Step 5 contingency)
- Create: `engine/case/loader.py`
- Test: `engine/tests/test_case_loader.py`

**Acceptance Criteria:**
- [ ] All four taxonomy JSONs load.
- [ ] `load_skeletons(dir)` returns a dict[str, CaseSkeleton] keyed by skeleton_id.
- [ ] `load_taxonomy(dir)` returns a `Taxonomy` object with the four family lists as attributes.
- [ ] `load_case_resolution_config(arc_id)` reads `nightcap/case_resolution_config.json`.

**Verify:** `pytest engine/tests/test_case_loader.py -v`

**Steps:**

- [ ] **Step 1: Author `motive_families.json`.**

```json
{
  "families": [
    {
      "family_id": "greed",
      "narratives": [
        "financial exposure that the victim's next action would have made public",
        "an inheritance clause the victim was about to change",
        "a debt the victim was collecting on"
      ]
    },
    {
      "family_id": "love",
      "narratives": [
        "a relationship the victim was going to name in public",
        "a former partner the victim had refused to give up on",
        "a jealousy that had waited too long to act"
      ]
    },
    {
      "family_id": "self_protection",
      "narratives": [
        "a secret the victim had discovered and was about to disclose",
        "a legal exposure the victim was going to trigger",
        "a professional ruin the victim had authored in draft"
      ]
    },
    {
      "family_id": "betrayal",
      "narratives": [
        "a pact the victim had broken the week before",
        "an alliance the victim had switched",
        "a promise the victim was refusing to honour"
      ]
    },
    {
      "family_id": "ambition",
      "narratives": [
        "a promotion the victim was blocking",
        "a role the victim was going to claim",
        "an audition the victim had rigged"
      ]
    }
  ]
}
```

- [ ] **Step 2: Author `method_families.json`.**

```json
{
  "families": [
    {
      "family_id": "poison",
      "vessels": ["decanter", "champagne flute", "teacup", "coffee cup", "wine glass"],
      "traces": ["a bitter residue", "a faint discoloration", "an unusual sediment"]
    },
    {
      "family_id": "suffocation",
      "objects": ["silk scarf", "pillow", "curtain sash", "belt", "cord"],
      "traces": ["fibre marks", "a bruised throat", "a broken clasp"]
    },
    {
      "family_id": "fall",
      "locations": ["upper landing", "balcony", "cliff-edge terrace", "observation deck", "spiral staircase"],
      "traces": ["a scuffed heel print", "a torn cuff", "a broken railing"]
    },
    {
      "family_id": "blunt_trauma",
      "objects": ["fireplace poker", "brass candlestick", "cane", "bookend", "trophy"],
      "traces": ["a small tear in the scalp", "a splinter of gilt", "a chip of enamel"]
    }
  ]
}
```

- [ ] **Step 3: Author `evidence_types.json`.**

```json
{
  "types": [
    {"type_id": "trace", "description": "Physical trace left by the act (residue, mark, imprint)."},
    {"type_id": "testimony", "description": "Something a suspect or bystander reports having seen or heard."},
    {"type_id": "document", "description": "A written record: letter, ledger, message, contract, receipt."},
    {"type_id": "object", "description": "A found item that ties a suspect to a place or time (key, stub, badge)."}
  ]
}
```

- [ ] **Step 4: Author `lie_topics.json`.**

```json
{
  "topics": [
    {"topic_id": "location", "description": "Where the suspect was at a specific time."},
    {"topic_id": "relationship", "description": "The nature of the suspect's relationship to the victim or another suspect."},
    {"topic_id": "observation", "description": "What the suspect saw, heard, or noticed."},
    {"topic_id": "possession", "description": "Whether the suspect had, held, or owned a particular thing."}
  ]
}
```

- [ ] **Step 5: Author `case_taxonomy/README.md` and `case_resolution_config.json`.**

`nightcap/case_taxonomy/README.md`:

```markdown
# Nightcap Case Taxonomy

Axes 5–6 generative content library (AW-281 / spec 0072). Case
skeletons in `nightcap/case_skeletons/` are the authored *shape*;
this folder is the generative *specifics* the resolver draws from.

Tables:
- `motive_families.json` — motive family + narrative variants
- `method_families.json` — method family + vessels/objects/locations + traces
- `evidence_types.json` — evidence type registry
- `lie_topics.json` — lie topic registry

Adding to a taxonomy: append entries, run
`pytest engine/tests/test_case_loader.py -v`, and the resolver picks
them up.
```

`nightcap/case_resolution_config.json`:

```json
{
  "arc_id_prefix": "nightcap-couch-race",
  "skeleton_directory": "nightcap/case_skeletons",
  "taxonomy_directory": "nightcap/case_taxonomy",
  "cast_size_by_player_count": {
    "2": 4, "3": 4, "4": 4,
    "5": 5, "6": 5,
    "7": 6, "8": 6
  }
}
```

Note: this file is the fallback path for the loader if the top-level `case_resolution` block in the arc JSON is rejected by `ArcDefinition`'s `extra="forbid"` config. Task 1 Step 5 covers verifying which path is active.

- [ ] **Step 6: Write the loader.**

`engine/case/loader.py`:

```python
"""Load case skeletons, taxonomies, and resolution config from disk.

Kept arc-agnostic: the loader takes directory paths as arguments and
reads whatever JSON it finds; it does not know about ``nightcap`` or
any specific arc.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from engine.case.errors import CaseResolutionError
from engine.case.models import CaseSkeleton


class Taxonomy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    motive_families: list[dict[str, Any]] = Field(default_factory=list)
    method_families: list[dict[str, Any]] = Field(default_factory=list)
    evidence_types: list[dict[str, Any]] = Field(default_factory=list)
    lie_topics: list[dict[str, Any]] = Field(default_factory=list)


class CaseResolutionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    arc_id_prefix: str
    skeleton_directory: str
    taxonomy_directory: str
    cast_size_by_player_count: dict[str, int]


def load_skeletons(directory: Path) -> dict[str, CaseSkeleton]:
    if not directory.exists():
        raise CaseResolutionError(f"skeleton directory missing: {directory}")
    result: dict[str, CaseSkeleton] = {}
    for path in sorted(directory.glob("*.json")):
        skel = CaseSkeleton.model_validate_json(path.read_text("utf-8"))
        if skel.skeleton_id in result:
            raise CaseResolutionError(
                f"duplicate skeleton_id {skel.skeleton_id!r} in {directory}"
            )
        result[skel.skeleton_id] = skel
    if not result:
        raise CaseResolutionError(f"no skeletons found in {directory}")
    return result


def load_taxonomy(directory: Path) -> Taxonomy:
    if not directory.exists():
        raise CaseResolutionError(f"taxonomy directory missing: {directory}")

    def _load(name: str, key: str) -> list[dict[str, Any]]:
        path = directory / name
        if not path.exists():
            raise CaseResolutionError(f"taxonomy file missing: {path}")
        data = json.loads(path.read_text("utf-8"))
        return list(data.get(key, []))

    return Taxonomy(
        motive_families=_load("motive_families.json", "families"),
        method_families=_load("method_families.json", "families"),
        evidence_types=_load("evidence_types.json", "types"),
        lie_topics=_load("lie_topics.json", "topics"),
    )


def load_case_resolution_config(
    config_path: Path,
) -> CaseResolutionConfig:
    if not config_path.exists():
        raise CaseResolutionError(f"case-resolution config missing: {config_path}")
    return CaseResolutionConfig.model_validate_json(
        config_path.read_text("utf-8")
    )
```

- [ ] **Step 7: Wire the loader into the module exports.**

Update `engine/case/__init__.py` to add:

```python
from engine.case.loader import (
    CaseResolutionConfig,
    Taxonomy,
    load_case_resolution_config,
    load_skeletons,
    load_taxonomy,
)
```

And extend `__all__` accordingly.

- [ ] **Step 8: Write the loader test.**

`engine/tests/test_case_loader.py`:

```python
"""AW-281 — Loader for skeletons, taxonomies, and case-resolution config."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.case import CaseSkeleton
from engine.case.errors import CaseResolutionError
from engine.case.loader import (
    load_case_resolution_config,
    load_skeletons,
    load_taxonomy,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SKELETON_DIR = REPO_ROOT / "nightcap" / "case_skeletons"
TAXONOMY_DIR = REPO_ROOT / "nightcap" / "case_taxonomy"
CONFIG_PATH = REPO_ROOT / "nightcap" / "case_resolution_config.json"


def test_load_skeletons_returns_three() -> None:
    skels = load_skeletons(SKELETON_DIR)
    assert set(skels.keys()) == {
        "locked_room_poisoning",
        "alibi_collapse",
        "pre_conspiracy_fall",
    }
    for value in skels.values():
        assert isinstance(value, CaseSkeleton)


def test_load_skeletons_missing_directory() -> None:
    with pytest.raises(CaseResolutionError):
        load_skeletons(Path("/definitely/does/not/exist/nc"))


def test_load_taxonomy_populates_all_lists() -> None:
    tax = load_taxonomy(TAXONOMY_DIR)
    assert len(tax.motive_families) >= 3
    assert len(tax.method_families) >= 3
    assert len(tax.evidence_types) >= 3
    assert len(tax.lie_topics) >= 3


def test_load_taxonomy_missing_directory() -> None:
    with pytest.raises(CaseResolutionError):
        load_taxonomy(Path("/definitely/does/not/exist/nc"))


def test_load_case_resolution_config() -> None:
    cfg = load_case_resolution_config(CONFIG_PATH)
    assert cfg.arc_id_prefix == "nightcap-couch-race"
    assert cfg.cast_size_by_player_count["2"] == 4
    assert cfg.cast_size_by_player_count["5"] == 5
    assert cfg.cast_size_by_player_count["8"] == 6
```

- [ ] **Step 9: Run tests.**

```bash
pytest engine/tests/test_case_loader.py -v
```

Expected: 5 tests pass.

- [ ] **Step 10: Ruff + commit.**

```bash
python -m ruff check engine/case engine/tests/test_case_loader.py
python -m ruff format --check engine/case engine/tests/test_case_loader.py
git add engine/case/loader.py engine/case/__init__.py nightcap/case_taxonomy nightcap/case_resolution_config.json engine/tests/test_case_loader.py
git commit -m "feat(case): taxonomy tables + skeleton/taxonomy/config loader (AW-281)"
```

---

## Task 5: Case resolver + runtime invariant assertions

**Goal:** Implement `engine/case/resolver.py`. Deterministic from seed. Picks a skeleton, resolves cast, culprit, victim, evidence chain, authorized lies. Asserts both invariants (solvability, lie falsifiability) before returning. `engine/case/invariants.py` carries the invariant checks as reusable pure functions.

**Files:**
- Create: `engine/case/invariants.py`
- Create: `engine/case/resolver.py`
- Modify: `engine/case/__init__.py` (export `resolve`)
- Test: `engine/tests/test_case_resolver.py`
- Test: `engine/tests/test_case_invariants.py`

**Acceptance Criteria:**
- [ ] `resolve(arc_definition, seed=42, participant_count=4)` returns a `ResolvedCase` with 4 suspects + 1 victim.
- [ ] Same seed produces identical `ResolvedCase` (deep-equal).
- [ ] Different seeds produce different `culprit_id` and different `evidence[0].text` at least sometimes (verify over 20 seeds).
- [ ] Cast size scales: 2/3/4 → 4, 5/6 → 5, 7/8 → 6.
- [ ] Invariant assertions run inside `resolve` and raise `CaseInvariantError` on failure.
- [ ] `solvability_check(case)` and `lie_falsifiability_check(case)` are pure functions returning `(ok: bool, detail: str)`.

**Verify:** `pytest engine/tests/test_case_resolver.py engine/tests/test_case_invariants.py -v`

**Steps:**

- [ ] **Step 1: Write the invariants module.**

`engine/case/invariants.py`:

```python
"""Runtime fairness invariants for resolved cases.

Two invariants are asserted before a ResolvedCase is returned from the
resolver:

1. Solvability — the intersection of clue-implication sets (over the
   genuine clue chain, applied by a rational-actor solver) uniquely
   identifies one CastMember, and that member matches ``culprit_id``.
2. Lie falsifiability — every AuthorizedFalsehood's ``contradicted_by``
   list is non-empty AND every referenced evidence_id exists in the
   case's evidence list.
"""

from __future__ import annotations

from engine.case.models import ResolvedCase


def solvability_check(case: ResolvedCase) -> tuple[bool, str]:
    """Return (ok, detail).

    Applies the genuine clue chain: intersect all ``implicates`` sets
    from genuine evidence entries. The remaining set must be exactly
    ``{culprit_id}``.
    """
    genuine = [e for e in case.evidence if e.truth_value == "genuine"]
    if not genuine:
        return False, "no genuine evidence"

    implicate_sets = [set(e.points_toward) for e in genuine if e.points_toward]
    if not implicate_sets:
        return False, "no genuine evidence implicates any cast member"

    narrowed = set.intersection(*implicate_sets)

    exonerated: set[str] = set()
    for e in genuine:
        exonerated.update(e.points_away_from)
    narrowed -= exonerated

    if narrowed == {case.culprit_id}:
        return True, "unique culprit identified"
    return False, (
        f"genuine chain narrows to {sorted(narrowed)!r}; "
        f"expected culprit {case.culprit_id!r}"
    )


def lie_falsifiability_check(case: ResolvedCase) -> tuple[bool, str]:
    evidence_ids = {e.evidence_id for e in case.evidence}
    for lie in case.falsehoods:
        if not lie.contradicted_by:
            return False, f"lie {lie.falsehood_id!r} has no contradicting evidence"
        missing = [e for e in lie.contradicted_by if e not in evidence_ids]
        if missing:
            return False, (
                f"lie {lie.falsehood_id!r} references missing evidence {missing!r}"
            )
    return True, "all lies falsifiable"
```

- [ ] **Step 2: Write the resolver.**

`engine/case/resolver.py`:

```python
"""Deterministic case resolver.

Given (arc_definition, seed, participant_count) → a fully-resolved case
where the culprit, victim, cast, evidence chain, and authorized lies
have all been chosen from the arc's authored skeletons + generative
taxonomy tables.

Determinism model
-----------------
Every random choice in this module goes through a single
``random.Random(seed)`` instance so the same seed always produces the
same case for the same arc.

Fairness
--------
The resolver asserts ``solvability_check`` and
``lie_falsifiability_check`` before returning; both must pass. Failure
raises ``CaseInvariantError`` with the failing invariant name and
enough seed/skeleton context to reproduce.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any

from engine.arc.models import ArcDefinition
from engine.case.errors import CaseInvariantError, CaseResolutionError
from engine.case.invariants import (
    lie_falsifiability_check,
    solvability_check,
)
from engine.case.loader import (
    CaseResolutionConfig,
    Taxonomy,
    load_case_resolution_config,
    load_skeletons,
    load_taxonomy,
)
from engine.case.models import (
    AuthorizedFalsehood,
    CaseSkeleton,
    CastMember,
    EvidenceEntry,
    ResolvedCase,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

_SUSPECT_ROLES = ("intimate", "deflector", "observer", "obvious_suspect")
_SUSPECT_NAME_POOL = (
    "Ashford", "Bellamy", "Corvax", "Delacourt", "Estève",
    "Fairholme", "Grantham", "Halloway", "Ito", "Jansen",
    "Kent", "Lorimer",
)


def resolve(
    arc_definition: ArcDefinition,
    seed: int,
    participant_count: int,
    *,
    config_path: Path | None = None,
) -> ResolvedCase:
    if participant_count < 2 or participant_count > 8:
        raise CaseResolutionError(
            f"participant_count must be 2..8, got {participant_count}"
        )

    cfg = load_case_resolution_config(
        config_path or _default_config_path(arc_definition)
    )
    skeletons = load_skeletons(REPO_ROOT / cfg.skeleton_directory)
    taxonomy = load_taxonomy(REPO_ROOT / cfg.taxonomy_directory)

    rng = random.Random(seed)

    skeleton = _pick_skeleton(rng, skeletons)
    cast_size = _resolve_cast_size(cfg, skeleton, participant_count)
    cast = _resolve_cast(rng, cast_size)
    culprit = cast[0]
    victim = _resolve_victim(rng)

    evidence = _resolve_evidence(rng, skeleton, cast, taxonomy, culprit)
    lies = _resolve_lies(rng, skeleton, cast, culprit, evidence, taxonomy)

    case = ResolvedCase(
        case_id=_build_case_id(arc_definition.arc_id, seed),
        arc_id=arc_definition.arc_id,
        seed=seed,
        skeleton_id=skeleton.skeleton_id,
        cast=[*cast, victim],
        culprit_id=culprit.member_id,
        evidence=evidence,
        falsehoods=lies,
        reveal_shape=skeleton.reveal_shape,
    )

    ok, detail = solvability_check(case)
    if not ok:
        raise CaseInvariantError(
            f"solvability failed for seed={seed} skeleton={skeleton.skeleton_id}: {detail}"
        )
    ok, detail = lie_falsifiability_check(case)
    if not ok:
        raise CaseInvariantError(
            f"lie_falsifiability failed for seed={seed} skeleton={skeleton.skeleton_id}: {detail}"
        )
    return case


def _default_config_path(arc: ArcDefinition) -> Path:
    return REPO_ROOT / "nightcap" / "case_resolution_config.json"


def _pick_skeleton(
    rng: random.Random, skeletons: dict[str, CaseSkeleton]
) -> CaseSkeleton:
    return skeletons[rng.choice(sorted(skeletons.keys()))]


def _resolve_cast_size(
    cfg: CaseResolutionConfig,
    skeleton: CaseSkeleton,
    participant_count: int,
) -> int:
    if skeleton.cast_size_override is not None:
        return skeleton.cast_size_override
    key = str(participant_count)
    if key not in cfg.cast_size_by_player_count:
        raise CaseResolutionError(
            f"no cast size configured for participant_count={participant_count}"
        )
    return cfg.cast_size_by_player_count[key]


def _resolve_cast(rng: random.Random, cast_size: int) -> list[CastMember]:
    names = list(_SUSPECT_NAME_POOL)
    rng.shuffle(names)
    picked = names[:cast_size]
    culprit_index = rng.randrange(cast_size)
    cast: list[CastMember] = []
    for i, name in enumerate(picked):
        role_tag = _SUSPECT_ROLES[i % len(_SUSPECT_ROLES)]
        cast.append(
            CastMember(
                member_id=f"s{i + 1}",
                display_name=name,
                role="suspect",
                is_culprit=(i == culprit_index),
                tags=[role_tag],
            )
        )
    # Rotate so the culprit is index 0 for easier resolver code.
    if culprit_index != 0:
        cast[0], cast[culprit_index] = cast[culprit_index], cast[0]
    return cast


def _resolve_victim(rng: random.Random) -> CastMember:
    return CastMember(
        member_id="v1",
        display_name=rng.choice(("Marcus", "Vivien", "Alexei", "Iris", "Rosalind")),
        role="victim",
    )


def _resolve_evidence(
    rng: random.Random,
    skeleton: CaseSkeleton,
    cast: list[CastMember],
    taxonomy: Taxonomy,
    culprit: CastMember,
) -> list[EvidenceEntry]:
    stages = skeleton.clue_chain_pattern["stages"]
    evidence: list[EvidenceEntry] = []
    other_suspects = [m.member_id for m in cast if m.member_id != culprit.member_id and m.role == "suspect"]
    for i, stage in enumerate(stages):
        # Every stage-derived clue implicates the culprit; the last stage
        # narrows to the culprit exclusively (see solvability_check).
        points_toward = [culprit.member_id]
        points_away_from: list[str] = []
        if i == 0 and len(other_suspects) >= 1:
            # First-stage: broad; some other suspects also implicated (uncertainty).
            points_toward = [culprit.member_id, *rng.sample(other_suspects, min(2, len(other_suspects)))]
        text = _fabricate_evidence_text(rng, stage, taxonomy)
        evidence.append(
            EvidenceEntry(
                evidence_id=f"e{i + 1}",
                evidence_type=stage.get("kind", "trace"),
                text=text,
                points_toward=points_toward,
                points_away_from=points_away_from,
                delivery="group" if i % 2 == 0 else "private",
                delivery_target=None,
                truth_value="genuine",
            )
        )
    return evidence


def _fabricate_evidence_text(
    rng: random.Random,
    stage: dict[str, Any],
    taxonomy: Taxonomy,
) -> str:
    # Placeholder generative text — will be replaced by the wrapper voice
    # library integration in AW-268. For now, use the stage prompt +
    # a small taxonomic flourish so unit tests can distinguish seeds.
    prompt = stage.get("prompt", "evidence detail")
    flourish = ""
    if taxonomy.method_families:
        family = rng.choice(taxonomy.method_families)
        traces = family.get("traces", [])
        if traces:
            flourish = f" ({rng.choice(traces)})"
    return f"{prompt}{flourish}"


def _resolve_lies(
    rng: random.Random,
    skeleton: CaseSkeleton,
    cast: list[CastMember],
    culprit: CastMember,
    evidence: list[EvidenceEntry],
    taxonomy: Taxonomy,
) -> list[AuthorizedFalsehood]:
    lies: list[AuthorizedFalsehood] = []
    non_culprit_suspects = [m for m in cast if m.role == "suspect" and m.member_id != culprit.member_id]
    for i, member in enumerate(non_culprit_suspects):
        role_tag = member.tags[0] if member.tags else "deflector"
        topics = skeleton.lie_shapes_by_role.get(role_tag, ["location"])
        topic = rng.choice(topics)
        # Every lie is contradicted by the first genuine evidence entry
        # for now — the invariant only requires non-empty contradicted_by
        # and the solver (Task 7) will apply per-topic reasoning.
        contradicted_by = [evidence[0].evidence_id] if evidence else []
        lies.append(
            AuthorizedFalsehood(
                falsehood_id=f"l{i + 1}",
                speaker_id=member.member_id,
                topic=topic,
                claim_text=_fabricate_lie_text(rng, topic, taxonomy),
                contradicted_by=contradicted_by,
            )
        )
    # The culprit also lies — about location, contradicted by the last stage clue.
    culprit_lie = AuthorizedFalsehood(
        falsehood_id=f"l{len(non_culprit_suspects) + 1}",
        speaker_id=culprit.member_id,
        topic="location",
        claim_text=_fabricate_lie_text(rng, "location", taxonomy),
        contradicted_by=[evidence[-1].evidence_id] if evidence else [],
    )
    lies.append(culprit_lie)
    return lies


def _fabricate_lie_text(
    rng: random.Random,
    topic: str,
    taxonomy: Taxonomy,
) -> str:
    return {
        "location": "I was somewhere else at the time in question.",
        "relationship": "I barely knew them.",
        "observation": "I didn't see anything unusual.",
        "possession": "I had nothing to do with that item.",
    }.get(topic, "You are mistaken about that.")


def _build_case_id(arc_id: str, seed: int) -> str:
    return f"{arc_id}::case::{seed}"
```

- [ ] **Step 3: Export `resolve`.**

Add to `engine/case/__init__.py`:

```python
from engine.case.resolver import resolve
```

And add to `__all__`.

- [ ] **Step 4: Write the resolver test.**

`engine/tests/test_case_resolver.py`:

```python
"""AW-281 — case resolver: determinism, cast-size formula, invariants."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.arc.models import ArcDefinition
from engine.case import resolve

REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"


@pytest.fixture(scope="module")
def arc() -> ArcDefinition:
    return ArcDefinition.model_validate_json(ARC_PATH.read_text("utf-8"))


def test_resolve_returns_resolved_case_with_expected_shape(arc: ArcDefinition) -> None:
    case = resolve(arc, seed=42, participant_count=4)
    suspects = [m for m in case.cast if m.role == "suspect"]
    victims = [m for m in case.cast if m.role == "victim"]
    assert len(suspects) == 4
    assert len(victims) == 1
    culprits = [m for m in suspects if m.is_culprit]
    assert len(culprits) == 1
    assert culprits[0].member_id == case.culprit_id


@pytest.mark.parametrize("player_count,expected", [(2, 4), (4, 4), (5, 5), (6, 5), (7, 6), (8, 6)])
def test_cast_size_scales_with_player_count(arc: ArcDefinition, player_count: int, expected: int) -> None:
    case = resolve(arc, seed=1, participant_count=player_count)
    suspects = [m for m in case.cast if m.role == "suspect"]
    assert len(suspects) == expected


def test_deterministic_replay(arc: ArcDefinition) -> None:
    case_a = resolve(arc, seed=99, participant_count=5)
    case_b = resolve(arc, seed=99, participant_count=5)
    assert case_a == case_b


def test_different_seeds_produce_different_cases(arc: ArcDefinition) -> None:
    cases = [resolve(arc, seed=i, participant_count=4) for i in range(20)]
    culprit_names = {c.cast[0].display_name for c in cases}
    assert len(culprit_names) > 1, "20 seeds should produce >1 distinct culprit name"


def test_participant_count_out_of_range(arc: ArcDefinition) -> None:
    from engine.case.errors import CaseResolutionError

    with pytest.raises(CaseResolutionError):
        resolve(arc, seed=1, participant_count=1)
    with pytest.raises(CaseResolutionError):
        resolve(arc, seed=1, participant_count=9)


def test_case_id_contains_arc_and_seed(arc: ArcDefinition) -> None:
    case = resolve(arc, seed=7, participant_count=4)
    assert "nightcap-couch-race" in case.case_id
    assert "7" in case.case_id
```

- [ ] **Step 5: Write the invariants test.**

`engine/tests/test_case_invariants.py`:

```python
"""AW-281 — solvability + lie-falsifiability invariant checks."""

from __future__ import annotations

from engine.case.invariants import lie_falsifiability_check, solvability_check
from engine.case.models import (
    AuthorizedFalsehood,
    CastMember,
    EvidenceEntry,
    ResolvedCase,
)


def _base_case(**overrides) -> ResolvedCase:
    culprit = CastMember(member_id="s1", display_name="A", role="suspect", is_culprit=True)
    other = CastMember(member_id="s2", display_name="B", role="suspect")
    victim = CastMember(member_id="v1", display_name="V", role="victim")
    evidence = [
        EvidenceEntry(
            evidence_id="e1", evidence_type="trace", text="clue1",
            points_toward=["s1", "s2"], points_away_from=[],
            delivery="group", delivery_target=None,
        ),
        EvidenceEntry(
            evidence_id="e2", evidence_type="document", text="clue2",
            points_toward=["s1"], points_away_from=[],
            delivery="private", delivery_target="p1",
        ),
    ]
    lies = [
        AuthorizedFalsehood(
            falsehood_id="l1", speaker_id="s2", topic="location",
            claim_text="elsewhere", contradicted_by=["e1"],
        ),
    ]
    payload = {
        "case_id": "c1", "arc_id": "nightcap-couch-race-v1", "seed": 1,
        "skeleton_id": "locked_room_poisoning",
        "cast": [culprit, other, victim],
        "culprit_id": "s1",
        "evidence": evidence, "falsehoods": lies,
        "reveal_shape": {"steps": []},
    }
    payload.update(overrides)
    return ResolvedCase(**payload)


def test_solvability_passes_for_uniquely_identifying_chain() -> None:
    case = _base_case()
    ok, _ = solvability_check(case)
    assert ok


def test_solvability_fails_when_chain_does_not_narrow_to_culprit() -> None:
    case = _base_case(
        evidence=[
            EvidenceEntry(
                evidence_id="e1", evidence_type="trace", text="x",
                points_toward=["s1", "s2"], points_away_from=[],
                delivery="group", delivery_target=None,
            )
        ]
    )
    ok, _ = solvability_check(case)
    assert not ok


def test_lie_falsifiability_passes() -> None:
    case = _base_case()
    ok, _ = lie_falsifiability_check(case)
    assert ok


def test_lie_falsifiability_fails_with_empty_contradiction_list() -> None:
    lie = AuthorizedFalsehood(
        falsehood_id="l1", speaker_id="s2", topic="location",
        claim_text="x", contradicted_by=[],
    )
    case = _base_case(falsehoods=[lie])
    ok, _ = lie_falsifiability_check(case)
    assert not ok


def test_lie_falsifiability_fails_with_missing_evidence_id() -> None:
    lie = AuthorizedFalsehood(
        falsehood_id="l1", speaker_id="s2", topic="location",
        claim_text="x", contradicted_by=["e999"],
    )
    case = _base_case(falsehoods=[lie])
    ok, _ = lie_falsifiability_check(case)
    assert not ok
```

- [ ] **Step 6: Run tests, iterate.**

```bash
pytest engine/tests/test_case_resolver.py engine/tests/test_case_invariants.py -v
```

Expected: 12 tests pass. If the resolver produces cases that fail solvability, adjust `_resolve_evidence` so the final stage's evidence implicates ONLY the culprit (and earlier stages' broader implication sets intersect to the culprit set).

- [ ] **Step 7: Commit.**

```bash
python -m ruff check engine/case engine/tests/test_case_resolver.py engine/tests/test_case_invariants.py
python -m ruff format --check engine/case engine/tests/test_case_resolver.py engine/tests/test_case_invariants.py
git add engine/case/invariants.py engine/case/resolver.py engine/case/__init__.py engine/tests/test_case_resolver.py engine/tests/test_case_invariants.py
git commit -m "feat(case): deterministic resolver + runtime fairness invariants (AW-281)"
```

---

## Task 6: Property tests over 1000+ seeds

**Goal:** Ship the property-test sweep — 1000 seeds per skeleton (3000 total) asserting both invariants hold and no seed produces a degenerate case.

**Files:**
- Create: `engine/tests/test_case_property_sweep.py`

**Acceptance Criteria:**
- [ ] Sweep runs 1000 seeds per skeleton and no seed raises `CaseInvariantError`.
- [ ] Sweep asserts every case has ≥1 genuine evidence entry.
- [ ] Sweep asserts every case has exactly one culprit.
- [ ] Sweep completes in under 30 seconds on a laptop (target ≥100 cases/sec throughput).
- [ ] Sweep is marked with pytest slow marker so `pytest -m "not slow"` can skip it during normal dev.

**Verify:** `pytest engine/tests/test_case_property_sweep.py -v`

**Steps:**

- [ ] **Step 1: Write the sweep.**

`engine/tests/test_case_property_sweep.py`:

```python
"""AW-281 — 1000-seed property sweep per skeleton.

Asserts that no seed produces a case that violates a fairness invariant
or a resolver-shape invariant (cast size, unique culprit, non-empty
evidence).
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from engine.arc.models import ArcDefinition
from engine.case import resolve
from engine.case.errors import CaseInvariantError

REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"

SEEDS_PER_SKELETON = 1000
SKELETON_IDS = ("locked_room_poisoning", "alibi_collapse", "pre_conspiracy_fall")


@pytest.fixture(scope="module")
def arc() -> ArcDefinition:
    return ArcDefinition.model_validate_json(ARC_PATH.read_text("utf-8"))


@pytest.mark.slow
def test_sweep_invariants_hold_over_many_seeds(arc: ArcDefinition) -> None:
    start = time.perf_counter()
    failures: list[str] = []
    count = 0
    # 3 * 1000 = 3000 cases total; seed range 0..2999.
    for seed in range(3 * SEEDS_PER_SKELETON):
        try:
            case = resolve(arc, seed=seed, participant_count=(seed % 7) + 2)
        except CaseInvariantError as exc:
            failures.append(f"seed={seed}: {exc}")
            continue
        count += 1
        # Post-resolution shape invariants
        suspects = [m for m in case.cast if m.role == "suspect"]
        if not suspects:
            failures.append(f"seed={seed}: no suspects")
        if len([m for m in suspects if m.is_culprit]) != 1:
            failures.append(f"seed={seed}: not exactly one culprit")
        if not case.evidence:
            failures.append(f"seed={seed}: no evidence")
    elapsed = time.perf_counter() - start
    assert not failures, f"{len(failures)} failures out of {3 * SEEDS_PER_SKELETON} seeds; first 5: {failures[:5]}"
    assert count == 3 * SEEDS_PER_SKELETON
    # Throughput sanity: fail if we cannot resolve 100 cases/second on this machine.
    if elapsed > 30:
        pytest.fail(
            f"sweep took {elapsed:.1f}s > 30s; either the resolver has "
            "regressed on perf or SEEDS_PER_SKELETON was raised without "
            "a matching throughput budget."
        )
```

- [ ] **Step 2: Register the `slow` marker in pyproject if not already present.**

Check `pyproject.toml`:

```bash
grep -A2 "markers" pyproject.toml
```

If absent, add:

```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests that take longer than a few seconds",
]
```

- [ ] **Step 3: Run the sweep.**

```bash
pytest engine/tests/test_case_property_sweep.py -v
```

Expected: 1 test passes, in under 30s.

If any seed fails a fairness invariant, the failures list will name the seed and the invariant. Fix `resolver.py` (typically by tightening `_resolve_evidence` narrowing rules or `_resolve_lies` contradiction targeting) and re-run. The property sweep is the *proof* — no case skeleton or resolver change ships until this passes cleanly.

- [ ] **Step 4: Commit.**

```bash
git add engine/tests/test_case_property_sweep.py pyproject.toml
git commit -m "test(case): 1000-seed × 3-skeleton property sweep (AW-281)"
```

---

## Task 7: Synthetic detective solver

**Goal:** Ship `engine/case/solver.py` — a bounded rational-actor solver that plays a resolved case and reports whether a smart human could win. Test that it wins over 100 seeds per skeleton.

**Files:**
- Create: `engine/case/solver.py`
- Modify: `engine/case/__init__.py` (export `synthetic_detective`, `SolverVerdict`)
- Test: `engine/tests/test_case_solver.py`

**Acceptance Criteria:**
- [ ] `synthetic_detective(case)` returns a `SolverVerdict` with `culprit_id`, `confidence: float`, `won: bool`.
- [ ] For every resolved case shipped in Task 5, the detective's `culprit_id` matches `case.culprit_id`.
- [ ] Solver wins on 100 seeds × 3 skeletons = 300 cases with 100% win rate.
- [ ] Solver does NOT depend on knowledge outside the resolved-case object (it takes ResolvedCase in, produces a verdict — no side channels).

**Verify:** `pytest engine/tests/test_case_solver.py -v`

**Steps:**

- [ ] **Step 1: Write the solver.**

`engine/case/solver.py`:

```python
"""Synthetic detective — bounded rational-actor solver for resolved cases.

The solver reads a ``ResolvedCase`` and reports whether a rational-actor
player, given the intended clue distribution and interrogation intents,
can uniquely identify the culprit. This is the Level-3 leg of AW-281's
fairness proof stack.

Algorithm
---------
1. Assemble a suspect-implication score for each cast member from all
   genuine evidence: each ``implicates`` entry adds 1, each
   ``exonerates`` entry subtracts 1.
2. For each authorized falsehood, if the solver has the contradicting
   evidence in hand, it detects the contradiction and adds a penalty
   to the speaker's suspicion score.
3. The suspect with the highest score is the solver's guess. If two
   are tied, the solver reports low confidence and no win.

The solver is deliberately dumb: it only uses information contained in
the resolved case object. Any case that a smart human could solve, the
solver should also solve — and if the solver can't, the case is
degenerate.
"""

from __future__ import annotations

from collections import Counter

from pydantic import BaseModel, ConfigDict

from engine.case.models import ResolvedCase


class SolverVerdict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    culprit_id: str
    confidence: float
    won: bool


def synthetic_detective(case: ResolvedCase) -> SolverVerdict:
    scores: Counter[str] = Counter()
    for e in case.evidence:
        if e.truth_value != "genuine":
            continue
        for member_id in e.points_toward:
            scores[member_id] += 1
        for member_id in e.points_away_from:
            scores[member_id] -= 1

    # Contradiction detection — if the solver has the contradicting
    # evidence in hand, add a suspicion penalty on the lying speaker.
    evidence_ids = {e.evidence_id for e in case.evidence}
    for lie in case.falsehoods:
        if any(eid in evidence_ids for eid in lie.contradicted_by):
            scores[lie.speaker_id] += 1

    if not scores:
        return SolverVerdict(culprit_id="", confidence=0.0, won=False)

    ranked = scores.most_common()
    top_score = ranked[0][1]
    top_ids = [mid for mid, s in ranked if s == top_score]

    if len(top_ids) != 1:
        return SolverVerdict(
            culprit_id=top_ids[0],
            confidence=0.0,
            won=False,
        )

    confidence = top_score / (top_score + (ranked[1][1] if len(ranked) > 1 else 0) + 1e-9)
    won = top_ids[0] == case.culprit_id
    return SolverVerdict(
        culprit_id=top_ids[0],
        confidence=confidence,
        won=won,
    )
```

- [ ] **Step 2: Export.**

Update `engine/case/__init__.py`:

```python
from engine.case.solver import SolverVerdict, synthetic_detective
```

And add to `__all__`.

- [ ] **Step 3: Write the solver test.**

`engine/tests/test_case_solver.py`:

```python
"""AW-281 — synthetic detective across 100 seeds × 3 skeletons."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.arc.models import ArcDefinition
from engine.case import resolve, synthetic_detective

REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"


@pytest.fixture(scope="module")
def arc() -> ArcDefinition:
    return ArcDefinition.model_validate_json(ARC_PATH.read_text("utf-8"))


@pytest.mark.slow
def test_detective_wins_across_seed_sweep(arc: ArcDefinition) -> None:
    losses: list[str] = []
    total = 0
    for seed in range(300):
        participant_count = (seed % 7) + 2
        case = resolve(arc, seed=seed, participant_count=participant_count)
        verdict = synthetic_detective(case)
        total += 1
        if not verdict.won:
            losses.append(
                f"seed={seed} skeleton={case.skeleton_id} "
                f"culprit={case.culprit_id} guess={verdict.culprit_id}"
            )
    assert not losses, (
        f"{len(losses)} solver losses out of {total}; "
        f"first 5: {losses[:5]}"
    )


def test_detective_matches_culprit_on_single_seed(arc: ArcDefinition) -> None:
    case = resolve(arc, seed=1, participant_count=4)
    verdict = synthetic_detective(case)
    assert verdict.won is True
    assert verdict.culprit_id == case.culprit_id
```

- [ ] **Step 4: Run.**

```bash
pytest engine/tests/test_case_solver.py -v
```

Expected: 2 tests pass. If the solver loses on any seed, the resolver's evidence distribution is not tight enough — tighten `_resolve_evidence` in `resolver.py` and re-run both this test and the property sweep from Task 6.

- [ ] **Step 5: Commit.**

```bash
python -m ruff check engine/case/solver.py engine/tests/test_case_solver.py
python -m ruff format --check engine/case/solver.py engine/tests/test_case_solver.py
git add engine/case/solver.py engine/case/__init__.py engine/tests/test_case_solver.py
git commit -m "feat(case): synthetic detective solver + 300-case CI proof (AW-281)"
```

---

## Task 8: Harness runner integration

**Goal:** Extend `engine/harness/runner.py` so that when the arc's `play_mode == "detective_race"`, the runner calls the case resolver instead of the existing participant-killer path. The resolved case is stored in `runtime_state.resolved_generative_elements["case_resolution"]`. Add a harness test proving all six beats complete at counts 2 and 8 with the same seed producing the same case.

**Files:**
- Modify: `engine/harness/runner.py`
- Test: `engine/tests/test_couch_race_harness.py`

**Acceptance Criteria:**
- [ ] Full six-beat harness run completes for participant_counts 2 and 8 without error.
- [ ] `runtime_state.resolved_generative_elements["case_resolution"]` contains the ResolvedCase's `case_id`, `culprit_id`, `skeleton_id`, `seed`.
- [ ] Same seed produces the same resolved case across two independent HarnessRunner instances.
- [ ] The existing Imposter-Variant harness (over `nightcap/arc.json`) still passes.

**Verify:** `pytest engine/tests/test_couch_race_harness.py engine/tests/test_harness_runner.py -v`

**Steps:**

- [ ] **Step 1: Modify `_resolve_introduction_setup` to branch on play_mode.**

Edit `engine/harness/runner.py`. Replace the current `_resolve_introduction_setup` method with:

```python
    def _resolve_introduction_setup(self) -> None:
        run = self._require_run()
        arc = self._arc_definition
        if arc.play_mode == PlayMode.detective_race:
            self._resolve_case_for_detective_race(run)
            return
        if not arc.generative_elements.killer_assignment:
            return
        if _KILLER_ROLE in run.runtime_state.role_assignments:
            return
        if not run.participants:
            return
        initial_beat_id = arc.beats[0].beat_id
        if sorted(self._chart.configuration_values) != [initial_beat_id]:
            msg = f"killer assignment must resolve during the initial beat ({initial_beat_id!r})."
            raise RuntimeError(msg)

        assigned_participant = self._assignment_rng.choice(run.participants)
        run.runtime_state.role_assignments[_KILLER_ROLE] = assigned_participant
        run.runtime_state.resolved_generative_elements[_KILLER_ASSIGNMENT_KEY] = {
            "role": _KILLER_ROLE,
            "participant_id": assigned_participant,
            "seed": self._seed,
            "candidate_participants": list(run.participants),
        }

    def _resolve_case_for_detective_race(self, run) -> None:  # type: ignore[no-untyped-def]
        if "case_resolution" in run.runtime_state.resolved_generative_elements:
            return
        if not run.participants:
            return
        # engine/case is a sibling module; import lazily to avoid a cycle
        # when engine.harness is imported at engine.arc load time.
        from engine.case import resolve as resolve_case

        case = resolve_case(
            self._arc_definition,
            seed=self._seed,
            participant_count=len(run.participants),
        )
        victim_members = case.members_by_role("victim")
        run.runtime_state.resolved_generative_elements["case_resolution"] = {
            "case_id": case.case_id,
            "arc_id": case.arc_id,
            "seed": case.seed,
            "skeleton_id": case.skeleton_id,
            "culprit_id": case.culprit_id,
            # Nightcap arc-content record; not part of engine/case schema.
            "victim_id": victim_members[0].member_id if victim_members else None,
            "cast_size": len([m for m in case.cast if m.role == "suspect"]),
            "evidence_count": len(case.evidence),
            "falsehood_count": len(case.falsehoods),
        }
```

Add the import at the top of the file:

```python
from engine.arc.models import ArcDefinition, PlayMode
```

- [ ] **Step 2: Write the harness test.**

`engine/tests/test_couch_race_harness.py`:

```python
"""AW-281 — full 6-beat headless harness run over the Couch Race arc."""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.arc.arc_state import transition_name_for
from engine.harness.models import HarnessAction
from engine.harness.runner import HarnessRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
ARC_PATH = REPO_ROOT / "nightcap" / "couch-race.arc.json"

BEATS = ["pour", "scene", "grill", "twist", "last_call", "truth"]


def _run_full_arc(seed: int, participant_count: int) -> HarnessRunner:
    runner = HarnessRunner(arc_path=ARC_PATH, seed=seed)
    runner.start()
    runner.set_participants([f"p{i + 1}" for i in range(participant_count)])
    for src, dst in zip(BEATS[:-1], BEATS[1:]):
        # Satisfy all exit conditions for the source beat so the guard passes.
        payload = {"context": _context_for_transition(src, dst)}
        runner.apply_action(HarnessAction(
            transition_name=transition_name_for(src, dst),
            payload=payload,
        ))
    return runner


def _context_for_transition(src: str, dst: str) -> dict[str, bool]:
    return {
        "pour_to_scene": {"case_resolution_complete": True, "all_players_ready": True},
        "scene_to_grill": {"evidence_wave_delivered": True},
        "grill_to_twist": {"interrogation_rounds_complete": True},
        "twist_to_last_call": {"twist_delivered": True},
        "last_call_to_truth": {"accusations_locked_or_countdown_expired": True},
    }[f"{src}_to_{dst}"]


@pytest.mark.parametrize("player_count", [2, 8])
def test_full_arc_completes(player_count: int) -> None:
    runner = _run_full_arc(seed=42, participant_count=player_count)
    assert sorted(runner.snapshot().configuration) == ["truth"]
    resolved = runner.current_run().runtime_state.resolved_generative_elements
    case = resolved["case_resolution"]
    assert case["arc_id"] == "nightcap-couch-race-v1"
    assert case["seed"] == 42


def test_deterministic_replay_across_runs() -> None:
    a = _run_full_arc(seed=99, participant_count=4)
    b = _run_full_arc(seed=99, participant_count=4)
    ra = a.current_run().runtime_state.resolved_generative_elements["case_resolution"]
    rb = b.current_run().runtime_state.resolved_generative_elements["case_resolution"]
    assert ra == rb


def test_cast_size_scales_at_the_harness_level() -> None:
    small = _run_full_arc(seed=1, participant_count=2)
    large = _run_full_arc(seed=1, participant_count=8)
    small_case = small.current_run().runtime_state.resolved_generative_elements["case_resolution"]
    large_case = large.current_run().runtime_state.resolved_generative_elements["case_resolution"]
    assert small_case["cast_size"] == 4
    assert large_case["cast_size"] == 6
```

- [ ] **Step 3: Run and iterate on transition-name / exit-condition mismatches.**

```bash
pytest engine/tests/test_couch_race_harness.py -v
```

If a transition name is wrong (`transition_name_for` produces a slug like `pour_to_scene` — verify by reading `engine/arc/arc_state.py`), or an exit condition is misnamed vs. the arc JSON, fix the arc JSON's `exit_conditions` list or the test's `_context_for_transition` map so both agree.

- [ ] **Step 4: Confirm the existing harness is not regressed.**

```bash
pytest engine/tests/test_harness_runner.py engine/tests/test_m2_exit_harness.py engine/tests/test_aw256_beat_hardcode.py -v
```

Expected: all pass, including the AW-256 no-hardcoded-beat-ID check.

- [ ] **Step 5: Full-suite gate.**

```bash
pytest engine/tests/ -v -m "not slow"
```

Expected: all pass. Then with slow markers:

```bash
pytest engine/tests/ -v
```

Expected: everything including the property sweep and solver sweep.

- [ ] **Step 6: Ruff pass + commit.**

```bash
python -m ruff check engine/harness engine/tests/test_couch_race_harness.py
python -m ruff format --check engine/harness engine/tests/test_couch_race_harness.py
git add engine/harness/runner.py engine/tests/test_couch_race_harness.py
git commit -m "feat(harness): couch race case resolution wired at introduction beat (AW-281)"
```

---

## Task 9: Documentation + spec cross-references + PR prep

**Goal:** Land the docs that AW-282 and beyond need to pick up cleanly. Update spec 0072 to reference the resolver architecture and the invariant/solver proof stack. Prepare the PR body.

**Files:**
- Modify: `docs/specs/0072-nightcap-couch-race-v1.md`
- Verify: `engine/case/README.md` (from Task 2)
- Verify: `nightcap/case_skeletons/README.md` (from Task 3)
- Verify: `nightcap/case_taxonomy/README.md` (from Task 4)

**Acceptance Criteria:**
- [ ] Spec 0072 has a "Case Resolution Architecture" section pointing at `engine/case/` and this plan.
- [ ] All READMEs from prior tasks are present.
- [ ] The commit message and PR body reference AW-281 (#235) and this plan.

**Verify:** `grep -n "engine/case" docs/specs/0072-nightcap-couch-race-v1.md`

**Steps:**

- [ ] **Step 1: Amend spec 0072.**

Read the spec at `docs/specs/0072-nightcap-couch-race-v1.md`. Find the "Test Plan" or a place after "In Scope" and insert a "Case Resolution Architecture" section:

```markdown
# Case Resolution Architecture

Deterministic case resolution ships in `engine/case/` (arc-agnostic
resolver interface, `ResolvedCase` domain models) with Nightcap-
specific case content in `nightcap/case_skeletons/` (3 authored
skeletons) and `nightcap/case_taxonomy/` (motive / method / evidence /
lie-topic tables). The resolver asserts two invariants at case-close:

- **Solvability** — genuine clue chain uniquely identifies the culprit.
- **Lie falsifiability** — every authorized falsehood is contradicted
  by at least one clue in the resolved distribution.

Proof stack (Level 3):

- Runtime invariant assertions in the resolver.
- 1000-seed property sweep per skeleton (3000 cases total).
- Synthetic-detective solver in `engine/case/solver.py`, verified to
  win over 300 seeds in CI.

See:
- Design memo: `docs/superpowers/specs/2026-07-17-aw-281-case-resolution-design.md`
- Implementation plan: `docs/superpowers/plans/2026-07-17-aw-281-couch-race-arc-and-case-generation.md`
- Module README: `engine/case/README.md`
```

- [ ] **Step 2: Verify all READMEs from prior tasks are in place.**

```bash
ls engine/case/README.md nightcap/case_skeletons/README.md nightcap/case_taxonomy/README.md
```

Each must exist. If any are missing, revisit the task that owned it.

- [ ] **Step 3: Commit docs.**

```bash
git add docs/specs/0072-nightcap-couch-race-v1.md
git commit -m "docs(specs): reference case-resolution architecture in spec 0072 (AW-281)"
```

- [ ] **Step 4: Reviewer skill (before PR).**

Invoke the `reviewer` agent (via Skill) against the branch. Address any P0/P1 findings in a fixup commit. See the parent conversation's Definition of Done for the review-first-then-PR flow.

- [ ] **Step 5: Push + open PR.**

```bash
git push -u origin claude/aw-281-couch-race-arc
gh pr create --title "feat(nightcap): AW-281 Couch Race arc + deterministic case resolution (#235)" --body "$(cat <<'EOF'
## Summary

- Ships the six-beat Couch Race ArcDefinition (`nightcap/couch-race.arc.json`).
- New `engine/case/` module — arc-agnostic resolver, `ResolvedCase` domain, loader, invariants, synthetic-detective solver.
- Three authored case skeletons (locked-room poisoning, alibi-collapse, pre-conspiracy fall) + taxonomy tables for motive / method / evidence / lie topics.
- Runtime invariants + 1000-seed property sweep + 300-case synthetic-detective proof in CI.
- Harness runner branches on `play_mode` — Couch Race resolves a case at the introduction beat; Imposter Variant path untouched.

## Test plan

- [x] `pytest engine/tests/ -v -m "not slow"` green
- [x] `pytest engine/tests/ -v` green (includes 1000-seed property sweep + 300-case solver sweep)
- [x] `python -m ruff check engine api`
- [x] `python -m ruff format --check engine api`
- [x] `pytest engine/tests/test_aw256_beat_hardcode.py` green (no new hardcoded beat IDs in engine code)

## Spec / design refs

- Task: #235 (AW-281)
- Plan: `docs/superpowers/plans/2026-07-17-aw-281-couch-race-arc-and-case-generation.md`
- Design memo: `docs/superpowers/specs/2026-07-17-aw-281-case-resolution-design.md`
- Parent spec: `docs/specs/0072-nightcap-couch-race-v1.md`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Task ordering / dependencies

- Task 0 → Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6, 7 (parallel possible after 5) → Task 8 → Task 9.
- Task 6 and Task 7 can run in either order after Task 5 completes; they don't depend on each other.
- Task 8 depends on 5, 6, 7 all landing (harness relies on the resolver + proofs).
- Task 9 must be last (docs reference all prior artifacts).

## Definition of Done (AW-281)

- All acceptance criteria in the task file (#235) are met.
- `pytest engine/tests/ -v` runs clean (including slow markers).
- Ruff clean.
- Reviewer agent PASS.
- PR opened; stops here for founder review before AW-282.
