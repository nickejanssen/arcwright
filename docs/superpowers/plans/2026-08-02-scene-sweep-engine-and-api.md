# Scene Sweep — Package, Engine Plugin & API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a working, fully-tested backend for the Scene Sweep hidden-object mini-game (content package, engine plugin, API exposure) with zero web/TypeScript work — verifiable end-to-end via `pytest` alone.

**Architecture:** A new `evidence-search-race` mechanic plugin, following the exact `StatefulMechanicPlugin` pattern `SocialTruthBluffPlugin` already proves out (`engine/mini_games/plugins/_social_truth_bluff.py`). One object on the authored board is deterministically designated "real" per round (derived from the snapshot's seed alone, so `score()` can re-derive it without needing `state`); the rest are decoys. Claims race first-tap-wins; the round always runs to full exhaustion or deadline. A new `nightcap/mini_games/scene-sweep/` content package supplies the archetype pool and object-slot layout. The API layer gets `SceneSweep*` schema classes mirroring the existing `Tmst*` pattern in `api/schemas/__init__.py` and `api/routers/mini_games.py`.

**Tech Stack:** Python 3.11+, FastAPI, Pydantic, SQLAlchemy async, pytest (existing stack, no new dependencies).

**User decisions (already made):** Founder-approved design at `docs/superpowers/specs/2026-08-02-nightcap-scene-sweep-mini-game-design.md` — race-to-claim, single hidden real object revealed only at round end, round never ends early, 90-120s ceiling (105s), object count scales 5-8 by player count (4-8 players), difficulty scales with player count only (no tiers), P4 fairness knowingly not enforced, beat/arc placement and final art out of scope. This plan additionally covers only the backend (package + engine + API); web rendering (TypeScript) is a separate follow-up plan written after this one lands, since the phone/TV renderer's data contract depends on the concrete API shape this plan defines. Leverage-economy integration (AW-287, referenced by decisions D-093/D-094) is explicitly **not** part of this plan — it was not discussed in the design session and would be new cross-module scope requiring its own approval; flagged here so it is not silently assumed either way.

---

## Scope note: product-approval record

Per `AGENTS.md`'s Product Scope Approval Rules, mini-games are protected v1 scope under D-058, but a new mechanic still needs durable approval evidence in canonical docs before it's treated as build scope — this repo enforces that rule actively (see `docs/product/decisions-log.csv` entries D-095/D-096, both recorded for exactly this reason during live founder sessions). Task 1 below records that evidence. Do not skip it.

## File Structure

**Create:**
- `nightcap/mini_games/scene-sweep/manifest.json` — package identity
- `nightcap/mini_games/scene-sweep/definitions/0.1.0.json` — authored rules, content, and generation constraints
- `engine/mini_games/plugins/_evidence_search_race.py` — the mechanic plugin
- `engine/tests/test_evidence_search_race_runtime.py` — plugin-level unit tests (mirrors `test_social_truth_bluff_runtime.py`)
- `engine/tests/test_scene_sweep_runtime_integration.py` — full async-DB integration tests via `MiniGameRuntime` (mirrors `test_mini_game_runtime.py`'s fixture pattern)
- `api/tests/test_scene_sweep_api.py` — API-layer tests (mirrors the TMST test classes in `api/tests/test_mini_games_api.py`)

**Modify:**
- `docs/product/decisions-log.csv` — append decision D-098
- `engine/mini_games/plugins/__init__.py` — register `EvidenceSearchRacePlugin` in `default_registry()`
- `api/schemas/__init__.py` — add `SceneSweep*` classes, widen `MiniGameRunResponse.phase_state`'s discriminated union
- `api/routers/mini_games.py` — add Scene Sweep dispatch alongside the existing TMST dispatch (both surfaces coexist; neither replaces the other)

No engine capability changes: `engine/mini_games/runtime.py`, `engine/mini_games/models.py`, and `engine/mini_games/resolver.py` are read-only references for this plan, never edited.

---

## Task 1: Record the product-scope decision

**Goal:** Add a decisions-log entry recording founder approval of Scene Sweep as new v1 mini-game scope, following the exact precedent of D-095/D-096.

**Files:**
- Modify: `docs/product/decisions-log.csv`

**Acceptance Criteria:**
- [ ] A new row is appended with `Decision` id `D-098`, matching the CSV's existing 6-column format (`Decision,Date,Rationale,Section,Status,Tags`).
- [ ] The row cites the design doc path, the mechanic's core shape (race-to-claim, single hidden real object, revealed at round end), and explicitly notes Leverage-economy integration was not decided.
- [ ] `git diff` shows only an appended line — no existing rows touched.

**Verify:** `git diff docs/product/decisions-log.csv` → shows exactly one new appended line, no other changes.

**Steps:**

- [ ] **Step 1: Append the decision row**

Open `docs/product/decisions-log.csv` and append this exact line (matching the file's existing quoting convention — fields containing commas are wrapped in double quotes):

```csv
D-098 Scene Sweep hidden-object mini-game approved as new v1 mechanic (evidence-search-race),"August 2, 2026","Founder-directed brainstorming session (2026-08-02) approved a new Nightcap mini-game: a shared-board hidden-object hunt. Players independently pan a wide illustrated scene on their phone (TV shows the full scene at once); claims race first-tap-wins and broadcast live but unlabeled. Exactly one object on the board is genuine evidence each round; the rest are decoys drawn from a 10-entry investigative-archetype pool (the murder weapon, the motive, the alibi breaker, etc.) rather than literal prop names. The round never ends early on the real object being claimed — it always runs to the full 90-120s deadline or full board exhaustion, and the truth is withheld until one staged shared-display reveal at the end. Object count scales 5-8 with player count (4-8 players); difficulty scales with player count only, no separate tiers. Spec 0068's P4 fairness pillar is knowingly not enforced for this game (founder's explicit trade-off for spectacle over guaranteed personal claims). Full design: docs/superpowers/specs/2026-08-02-nightcap-scene-sweep-mini-game-design.md. This decision covers the mechanic, content, and runtime design only. Leverage-economy integration (AW-287, D-093/D-094) was not discussed in this session and is explicitly not decided by this record either way; a future task must seek its own approval before wiring Scene Sweep's behavioral outputs into the Leverage economy. Beat/arc placement is likewise out of scope here, consistent with AW-249's own convention of deferring binding decisions to a later task.",Product / Nightcap,Committed,"nightcap, mini-games, scene-sweep, evidence-search-race, D-098"
```

- [ ] **Step 2: Verify the diff is additive only**

Run: `git diff docs/product/decisions-log.csv`
Expected: a single new line added at the end of the file, no other lines changed.

- [ ] **Step 3: Commit**

```bash
git add docs/product/decisions-log.csv
git commit -m "docs(product): record D-098 Scene Sweep mini-game approval"
```

---

## Task 2: Author the Scene Sweep content package

**Goal:** Produce a valid `nightcap/mini_games/scene-sweep/` package that loads and validates through the existing AW-249 schema, carrying the archetype pool, object-slot layout, and clue contract the plugin will consume.

**Files:**
- Create: `nightcap/mini_games/scene-sweep/manifest.json`
- Create: `nightcap/mini_games/scene-sweep/definitions/0.1.0.json`
- Test: `engine/tests/test_mini_game_models.py` (extend with a Scene Sweep load test, following that file's existing per-package test pattern for crime-scene-smash/evidence-locker-402/tell-me-something-true)

**Acceptance Criteria:**
- [ ] `load_mini_game_package(Path("nightcap/mini_games/scene-sweep"))` succeeds without raising.
- [ ] `manifest.game_id == "scene-sweep"` and matches the directory name (loader requirement).
- [ ] `definition.content_mode == ContentMode.hybrid`, and both `authored_content` and `generation_constraints` are present (schema requires both for `hybrid`).
- [ ] `definition.clue_fallback.clue_variant == ClueVariant.reduced`.
- [ ] `authored_content["clues"]` contains exactly one entry tagged `"reduced"` and one entry NOT tagged `"reduced"` — since hybrid content-merging only fills placeholder text and never restructures authored keys, this same two-entry shape carries through unchanged into `resolved_content["clues"]` once a real session resolves the package. This is the mechanism by which `_extract_authored_clues` in `engine/mini_games/runtime.py` delivers both entries on success and only the reduced one on fallback (verified by reading that function: on `ClueVariant.full` it returns every entry in the list unconditionally; on `ClueVariant.reduced` it returns only entries tagged `"reduced"`). Do not "fix" this into a single-entry list — it is the correct shape for "reduced is a guaranteed subset of full."
- [ ] `lifecycle == "draft"` (this package is not bound into any arc by this plan; per AW-249 convention, draft/playtest packages stay out of the production catalog).

**Verify:** `pytest engine/tests/test_mini_game_models.py -k scene_sweep -v` → PASS

**Steps:**

- [ ] **Step 1: Write `manifest.json`**

```json
{
  "schema_version": "1.0",
  "game_id": "scene-sweep",
  "title": "Scene Sweep",
  "lifecycle": "draft",
  "current_version": "0.1.0",
  "definition_path": "definitions/0.1.0.json",
  "asset_paths": []
}
```

- [ ] **Step 2: Write `definitions/0.1.0.json`**

```json
{
  "schema_version": "1.0",
  "game_id": "scene-sweep",
  "version": "0.1.0",
  "mechanic_type": "evidence-search-race",
  "participation_mode": "individual",
  "content_mode": "hybrid",
  "min_players": 4,
  "max_players": 8,
  "duration_seconds": 105,
  "rules": {
    "theme": "Nightcap clue-gated hidden-object evidence search",
    "surface": "phone (pannable viewport) + shared display (full scene) + host",
    "board_mode": "shared-coordinate-space race-to-claim",
    "single_real_object": true,
    "round_end_condition": "deadline expiry or every active object on the board claimed, whichever comes first; claiming the real object never ends the round early",
    "claim_rule": "first accepted submission for a given object_id wins; later submissions for the same object_id are rejected",
    "reveal_timing": "the real/decoy identity of every claim is withheld from all surfaces until round finalization",
    "object_count_by_player_count": {
      "4": 5,
      "5": 6,
      "6": 7,
      "7": 8,
      "8": 8
    },
    "player_count_behavior": {
      "4": "5 total objects on the board, 1 real",
      "5": "6 total objects on the board, 1 real",
      "6": "7 total objects on the board, 1 real",
      "7": "8 total objects on the board, 1 real",
      "8": "8 total objects on the board, 1 real"
    },
    "failure_policy": {
      "unclaimed_real_object_at_deadline": "reduced clue via clue_fallback",
      "duplicate_claim": "rejected, no clue effect, no behavioral credit"
    },
    "replay_variance": [
      "which object slots are active this round",
      "which archetype is designated real",
      "run seed for deterministic slot and real-object selection"
    ],
    "playtest_calibration": {
      "duration_seconds_status": "estimate",
      "object_count_status": "estimate",
      "rationale": "The 90-120s ceiling (105s) and the per-player-count object counts are starting estimates from design, not yet playtested.",
      "follow_up": "Recalibrate duration and object density after a real session, same posture Tell Me Something True's own duration_seconds already carries."
    }
  },
  "authored_content": {
    "package_summary": "A Nightcap hidden-object hunt: the shared display shows a full illustrated scene, each phone pans an independent viewport into the same coordinate space, and players race to claim objects. Exactly one is real evidence; the rest are decoys drawn from the same investigative-archetype pool. The truth is withheld until one staged reveal at the end.",
    "backgrounds": [
      {
        "background_id": "the-study",
        "label": "The Study"
      }
    ],
    "object_slots": [
      {"slot_id": "slot-1", "background_id": "the-study", "archetype": "murder-weapon", "position": {"x": 0.12, "y": 0.30}},
      {"slot_id": "slot-2", "background_id": "the-study", "archetype": "motive", "position": {"x": 0.34, "y": 0.22}},
      {"slot_id": "slot-3", "background_id": "the-study", "archetype": "alibi-breaker", "position": {"x": 0.48, "y": 0.55}},
      {"slot_id": "slot-4", "background_id": "the-study", "archetype": "forgery", "position": {"x": 0.62, "y": 0.62}},
      {"slot_id": "slot-5", "background_id": "the-study", "archetype": "struggle", "position": {"x": 0.80, "y": 0.70}},
      {"slot_id": "slot-6", "background_id": "the-study", "archetype": "secret-correspondence", "position": {"x": 0.90, "y": 0.15}},
      {"slot_id": "slot-7", "background_id": "the-study", "archetype": "missing-piece", "position": {"x": 0.20, "y": 0.75}},
      {"slot_id": "slot-8", "background_id": "the-study", "archetype": "witness-trace", "position": {"x": 0.70, "y": 0.35}}
    ],
    "clues": [
      {
        "clue_id": "scene-sweep-evidence-summary",
        "variant": "reduced",
        "content": {
          "text": "[generated: a short, partial description of what the search revealed about the case — sufficient on its own for the investigation to proceed]"
        }
      },
      {
        "clue_id": "scene-sweep-evidence-detail",
        "variant": "full",
        "content": {
          "text": "[generated: the complete identity and significance of the real evidence object, naming who it implicates and how, drawn from this session's resolved case data]"
        }
      }
    ],
    "surface_contract": {
      "phone": "pannable viewport into the scene, a minimap showing current position, and the archetype-name list with checkmarks as objects are claimed by anyone",
      "shared_display": "the entire scene always visible at once, live unlabeled claim markers, collective progress, and the end-of-round staged reveal",
      "host": "progress and fallback visibility without revealing which object is real before the reveal fires"
    },
    "fallback_contract": {
      "behavior": "If the deadline passes before the real object is claimed, the round finalizes with the reduced clue only. No object's real/decoy status is ever revealed before this point.",
      "shared_display_line": "Six objects. Time's up. Whatever mattered in this room is still in this room.",
      "host_line": "Deadline reached before the real object was claimed. Reduced clue released; advance when ready.",
      "player_device_line": "Time. The room moves on, and so does the case.",
      "clue_outcome": "reduced"
    },
    "diegetic_wrappers": {
      "high-society": {
        "title": "The Search",
        "narrator_intro": "Someone tidied this room in a hurry. Find what they didn't want found — or find nothing at all, which is its own kind of answer.",
        "narrator_reveal_success": "The room gives up its secret. {finder} was the one holding it, whether they knew it or not."
      },
      "corporate": {
        "title": "The Audit",
        "narrator_intro": "Somewhere in this office is the one thing that wasn't supposed to survive the reorg. Find it before the record does.",
        "narrator_reveal_success": "Audit complete. {finder} pulled the one file that matters."
      },
      "sci-fi": {
        "title": "The Sweep",
        "narrator_intro": "Scan the compartment. One reading matters; the rest are noise the ship generated to keep you busy.",
        "narrator_reveal_success": "Signal isolated. {finder}'s scan was the one that mattered."
      }
    }
  },
  "generation_constraints": {
    "tone": ["tense", "playful", "investigative"],
    "allowed_session_personalization": [
      "which archetype is real for this round",
      "the specific in-fiction identity of each object per theme",
      "decoy reveal quips",
      "narrator intro and reveal lines per theme"
    ],
    "resolution_contract": {
      "real_object_id": "the generated content payload must include a new top-level key real_object_id whose value is exactly one of authored_content.object_slots[].slot_id, chosen because that slot's archetype corresponds to a real, already-resolved fact in this session's case (e.g. pick the murder-weapon slot only if the case's actual weapon fact naturally maps to that archetype); this is a selection among existing authored slots, never an invented new slot",
      "real_archetype_source": "the identity and clue text for the resolved real evidence object must be drawn from this session's actual generated case data (killer, weapon, motive, etc.) supplied via session_context; the model must never invent case facts independently",
      "clue_text_source": "the clues[].content.text placeholder markers (bracketed [generated: ...] text) must be filled from that same resolved case data, never generic filler, and must be consistent with whichever slot real_object_id names"
    },
    "surface_rules": {
      "shared_display": "never reveal which claimed object is real or decoy before the staged reveal",
      "phone": "may show only the archetype-label list and the claiming player's own claim acknowledgement",
      "host": "may show progress and fallback state without revealing which object is real"
    },
    "runtime_boundaries": [
      "Python owns object slot selection and which slot is designated real",
      "Python owns claim arbitration and the deadline",
      "Python owns success/fallback determination and clue release",
      "Python owns behavioral output computation"
    ],
    "safety": [
      "object identities and clue text must come from resolved case and character data only",
      "no real-world player identity facts",
      "no protected-trait inference",
      "no graphic violence"
    ]
  },
  "behavioral_outputs": [
    {
      "key": "completion-time-ms",
      "description": "Elapsed time from round start until this participant's claim was accepted, if any.",
      "value_type": "integer",
      "scope": "participant",
      "derived": false
    },
    {
      "key": "decoys-claimed",
      "description": "Count of decoy (non-real) objects claimed by this participant.",
      "value_type": "integer",
      "scope": "participant",
      "derived": false
    },
    {
      "key": "real-object-claimed",
      "description": "Whether the real evidence object was claimed by anyone before the round ended.",
      "value_type": "boolean",
      "scope": "run",
      "derived": false
    }
  ],
  "clue_fallback": {
    "delay_seconds": 20,
    "clue_variant": "reduced",
    "host_override": true
  }
}
```

- [ ] **Step 3: Add a load test**

Open `engine/tests/test_mini_game_models.py`, find the existing per-package test for `tell-me-something-true` (or `evidence-locker-402`) and add a sibling test following the exact same shape:

```python
def test_scene_sweep_package_loads_and_validates() -> None:
    loaded = load_mini_game_package(
        Path("nightcap/mini_games/scene-sweep")
    )
    assert loaded.manifest.game_id == "scene-sweep"
    assert loaded.definition.mechanic_type == "evidence-search-race"
    assert loaded.definition.content_mode is ContentMode.hybrid
    assert loaded.definition.authored_content is not None
    assert loaded.definition.generation_constraints is not None
    assert loaded.definition.clue_fallback.clue_variant is ClueVariant.reduced

    clues = loaded.definition.authored_content["clues"]
    reduced = [c for c in clues if c["variant"] == "reduced"]
    full = [c for c in clues if c["variant"] != "reduced"]
    assert len(reduced) == 1
    assert len(full) == 1
```

Use whatever `Path`, `ContentMode`, `ClueVariant`, and `load_mini_game_package` imports already exist at the top of `test_mini_game_models.py` — do not add duplicate imports if they're already present from the other package tests in that file.

- [ ] **Step 4: Run the test**

Run: `pytest engine/tests/test_mini_game_models.py -k scene_sweep -v`
Expected: `1 passed`

- [ ] **Step 5: Commit**

```bash
git add nightcap/mini_games/scene-sweep/ engine/tests/test_mini_game_models.py
git commit -m "feat(nightcap): author Scene Sweep content package"
```

---

## Task 3: Implement the `evidence-search-race` mechanic plugin

**Goal:** A `StatefulMechanicPlugin` implementation that selects the round's object board, arbitrates claims, and scores success/fallback outcomes — fully unit-tested at the plugin level, mirroring `_social_truth_bluff.py`'s pattern exactly.

**Files:**
- Create: `engine/mini_games/plugins/_evidence_search_race.py`
- Test: `engine/tests/test_evidence_search_race_runtime.py`

**Acceptance Criteria:**
- [ ] `validate_payload` accepts `{"action": "claim", "object_id": "<slot_id>"}` and rejects anything else.
- [ ] The real object is derivable purely from `snapshot` (no `state`/`participants` dependency) — primarily by reading a generation-supplied `resolved_content["real_object_id"]` (proven by a test that supplies it and confirms the plugin uses that exact value, never a different one), falling back to a deterministic seeded-hash pick over all authored `object_slots` only when no such value is present (proven by a test that calls the fallback derivation twice and gets the same slot_id both times).
- [ ] `initialize_state` selects an active-object subset sized by `object_count_by_player_count[str(len(participants))]` (clamped to `[4, 8]`), always including the pre-designated real slot, and broadcasts an `all`-audience event carrying the slot list (archetype + position) but never which slot is real.
- [ ] `on_submission` rejects (raises `ValueError`) a claim on an `object_id` not in the round's active set, and rejects a second claim on an already-claimed `object_id`.
- [ ] `on_submission` sets `finalize_status="completed"` once every active object has been claimed (board exhaustion) — never early-exits just because the real object specifically was claimed.
- [ ] `on_deadline_expired` sets `finalize_status="timed_out"` unconditionally (no phases to advance, unlike TMST).
- [ ] `score` returns an outcome dict containing `real-object-claimed` (bool), `completion-time-ms` per participant who claimed something, and `decoys-claimed` per participant — all derived purely from `snapshot` + `submissions`.
- [ ] Every `MechanicEventDirective` payload the plugin emits validates against a corresponding new `SceneSweep*Payload` schema class (written in Task 5) — this test is added in Task 5 once those classes exist; Task 3's tests validate plugin behavior only, not schema conformance.

**Verify:** `pytest engine/tests/test_evidence_search_race_runtime.py -v` → all tests PASS

**Steps:**

- [ ] **Step 1: Write the plugin**

```python
"""Deterministic runtime plugin for the evidence-search-race mechanic.

Scene Sweep is a shared-board hidden-object race. Exactly one authored
object slot is deterministically designated "real" per round; the rest are
decoys. Claims race first-tap-wins. The round never finalizes early just
because the real object was claimed — it always runs to full board
exhaustion or the deadline, whichever comes first.

The real slot is derived purely from the resolved snapshot (never from
mutable `state`), because `score()` is called without `state` or
`participants` and must re-derive everything deterministically — the same
constraint Tell Me Something True's spotlight-order derivation already
satisfies for its own mechanic.
"""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from typing import Any
from uuid import UUID

from engine.db.orm import MiniGameSubmission
from engine.events.models import AudienceTarget, EventCategory
from engine.mini_games.resolver import ResolvedMiniGameSnapshot
from engine.mini_games.runtime import MechanicEventDirective, MechanicProgress

MECHANIC_TYPE = "evidence-search-race"

_OBJECT_COUNT_BY_PLAYER_COUNT = {4: 5, 5: 6, 6: 7, 7: 8, 8: 8}


class EvidenceSearchRacePlugin:
    mechanic_type: str = MECHANIC_TYPE

    def validate_payload(self, payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise ValueError("payload must be a JSON object")
        if payload.get("action") != "claim":
            raise ValueError("evidence-search-race only accepts action=claim")
        object_id = payload.get("object_id")
        if not isinstance(object_id, str) or not object_id.strip():
            raise ValueError("claim submissions require a non-empty object_id")

    def is_threshold_met(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
    ) -> bool:
        # Board exhaustion is decided inside on_submission (which has access
        # to the round's active-object state); this always returns False,
        # the same deferral pattern SocialTruthBluffPlugin uses.
        return False

    def score(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
    ) -> dict[str, Any]:
        real_object_id = self._real_object_id(snapshot)
        claims = self._claims(submissions)

        completion_time_ms: dict[str, int] = {}
        decoys_claimed: dict[str, int] = {}
        real_object_claimed = False
        finder_character_id: UUID | None = None

        start_time = min((s.submitted_at for s in submissions), default=None)

        for submission in submissions:
            object_id = submission.payload.get("object_id")
            key = str(submission.character_id)
            if start_time is not None:
                elapsed = submission.submitted_at - start_time
                completion_time_ms[key] = int(elapsed.total_seconds() * 1000)
            if object_id == real_object_id:
                real_object_claimed = True
                finder_character_id = submission.character_id
            else:
                decoys_claimed[key] = decoys_claimed.get(key, 0) + 1

        return {
            "real-object-claimed": real_object_claimed,
            "finder-character-id": str(finder_character_id)
            if finder_character_id is not None
            else None,
            "completion-time-ms": completion_time_ms,
            "decoys-claimed": decoys_claimed,
            "claimed-object-ids": list(claims.keys()),
        }

    def initialize_state(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        *,
        participants: list[tuple[UUID, UUID]],
        now: datetime,
    ) -> MechanicProgress:
        active_ids = self._select_active_object_ids(snapshot, len(participants))
        slots_by_id = {
            slot["slot_id"]: slot for slot in self._object_slots(snapshot)
        }
        board_event = MechanicEventDirective(
            category=EventCategory.state_transition,
            event_type="scene_sweep_board_started",
            target_audience=AudienceTarget.all,
            payload={
                "phase": "active",
                "objects": [
                    {
                        "object_id": object_id,
                        "archetype": slots_by_id[object_id]["archetype"],
                        "position": slots_by_id[object_id]["position"],
                    }
                    for object_id in active_ids
                ],
            },
        )
        return MechanicProgress(
            state={"active_object_ids": active_ids, "claimed_object_ids": []},
            events=(board_event,),
        )

    def on_submission(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        *,
        state: dict[str, Any],
        participants: list[tuple[UUID, UUID]],
        submission: MiniGameSubmission,
        accepted_submissions: list[MiniGameSubmission],
        now: datetime,
    ) -> MechanicProgress:
        active_ids: list[str] = list(state.get("active_object_ids", []))
        claimed_ids: list[str] = list(state.get("claimed_object_ids", []))
        object_id = submission.payload.get("object_id")

        if object_id not in active_ids:
            raise ValueError(f"object_id {object_id!r} is not on this round's board")
        if object_id in claimed_ids:
            raise ValueError(f"object_id {object_id!r} has already been claimed")

        claimed_ids.append(object_id)
        next_state = dict(state)
        next_state["claimed_object_ids"] = claimed_ids

        claim_event = MechanicEventDirective(
            category=EventCategory.state_transition,
            event_type="scene_sweep_object_claimed",
            target_audience=AudienceTarget.all,
            payload={"object_id": object_id, "claimed_count": len(claimed_ids)},
        )

        finalize_status = (
            "completed" if len(claimed_ids) >= len(active_ids) else None
        )
        return MechanicProgress(
            state=next_state,
            finalize_status=finalize_status,
            events=(claim_event,),
        )

    def on_deadline_expired(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        *,
        state: dict[str, Any],
        participants: list[tuple[UUID, UUID]],
        accepted_submissions: list[MiniGameSubmission],
        now: datetime,
    ) -> MechanicProgress:
        return MechanicProgress(state=dict(state), finalize_status="timed_out")

    # ------------------------------------------------------------------
    # Deterministic derivation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _seed(snapshot: ResolvedMiniGameSnapshot) -> str:
        resolved_seed = snapshot.resolved_content.get("run_seed")
        if isinstance(resolved_seed, str) and resolved_seed:
            return resolved_seed
        return snapshot.game_id

    @staticmethod
    def _object_slots(snapshot: ResolvedMiniGameSnapshot) -> list[dict[str, Any]]:
        slots = snapshot.resolved_content.get("object_slots", [])
        return [slot for slot in slots if isinstance(slot, dict)]

    def _ordered_slot_ids(self, snapshot: ResolvedMiniGameSnapshot) -> list[str]:
        seed = self._seed(snapshot)
        slot_ids = [slot["slot_id"] for slot in self._object_slots(snapshot)]
        return sorted(
            slot_ids,
            key=lambda slot_id: sha256(
                f"{seed}:{slot_id}".encode("utf-8")
            ).hexdigest(),
        )

    def _real_object_id(self, snapshot: ResolvedMiniGameSnapshot) -> str | None:
        """Return the slot_id designated real for this round.

        Primary path: the content-resolution step (AW-250) is expected to
        write `real_object_id` into resolved_content, chosen from this
        session's actual generated case data — this is what makes "which
        archetype is real" mean something in the story, not just a random
        pick (per the design doc's non-negotiable: the model may dress up
        resolved state, it may never invent it independently, but *which*
        already-resolved case fact this round highlights is exactly the
        kind of session-specific choice the generation step is for).

        Fallback path: if resolved_content carries no `real_object_id`
        (authored-only fixtures, or tests that build a snapshot directly
        from authored_content without running content resolution), fall
        back to a deterministic seeded-hash pick over all authored slots so
        the plugin stays fully testable without a live generation call.
        """
        supplied = snapshot.resolved_content.get("real_object_id")
        valid_ids = {slot["slot_id"] for slot in self._object_slots(snapshot)}
        if isinstance(supplied, str) and supplied in valid_ids:
            return supplied
        ordered = self._ordered_slot_ids(snapshot)
        return ordered[0] if ordered else None

    def _select_active_object_ids(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        participant_count: int,
    ) -> list[str]:
        ordered = self._ordered_slot_ids(snapshot)
        if not ordered:
            return []
        clamped_count = min(8, max(4, participant_count))
        target = _OBJECT_COUNT_BY_PLAYER_COUNT.get(clamped_count, len(ordered))
        target = min(target, len(ordered))
        real_id = self._real_object_id(snapshot)
        # The real object (generation-supplied or hash-fallback) must always
        # be on the board; fill the remaining slots from the deterministic
        # hash order, excluding the real one to avoid a duplicate.
        decoys = [slot_id for slot_id in ordered if slot_id != real_id]
        active = ([real_id] if real_id is not None else []) + decoys
        return active[:target]

    @staticmethod
    def _claims(submissions: list[MiniGameSubmission]) -> dict[str, MiniGameSubmission]:
        result: dict[str, MiniGameSubmission] = {}
        for submission in submissions:
            object_id = submission.payload.get("object_id")
            if isinstance(object_id, str):
                result[object_id] = submission
        return result
```

- [ ] **Step 2: Write the plugin-level test file**

```python
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

import pytest

from engine.mini_games.loader import load_mini_game_package
from engine.mini_games.plugins._evidence_search_race import EvidenceSearchRacePlugin
from engine.mini_games.resolver import ResolvedMiniGameSnapshot

T0 = datetime(2026, 8, 2, 20, 0, 0, tzinfo=timezone.utc)
PACKAGE_PATH = (
    Path(__file__).resolve().parents[2]
    / "nightcap"
    / "mini_games"
    / "scene-sweep"
)
PARTICIPANTS_4 = [
    (UUID(int=1), UUID(int=101)),
    (UUID(int=2), UUID(int=102)),
    (UUID(int=3), UUID(int=103)),
    (UUID(int=4), UUID(int=104)),
]


def load_snapshot(*, run_seed: str = "fixture-seed") -> ResolvedMiniGameSnapshot:
    loaded = load_mini_game_package(PACKAGE_PATH)
    definition = loaded.definition
    resolved_content = dict(definition.authored_content or {})
    resolved_content["run_seed"] = run_seed
    return ResolvedMiniGameSnapshot(
        game_id=definition.game_id,
        definition_version=definition.version,
        source_content_mode=definition.content_mode,
        mechanic_type=definition.mechanic_type,
        participation_mode=definition.participation_mode.value,
        min_players=definition.min_players,
        max_players=definition.max_players,
        duration_seconds=definition.duration_seconds,
        rules=definition.rules,
        behavioral_outputs=tuple(definition.behavioral_outputs),
        clue_fallback=definition.clue_fallback,
        resolved_content=resolved_content,
    )


def make_submission(
    *,
    submission_id: str,
    character_id: UUID,
    object_id: str,
    submitted_at: datetime,
) -> "FakeSubmission":
    return FakeSubmission(
        submission_id=submission_id,
        character_id=character_id,
        payload={"action": "claim", "object_id": object_id},
        submitted_at=submitted_at,
    )


class FakeSubmission:
    """Minimal stand-in for engine.db.orm.MiniGameSubmission's read surface."""

    def __init__(
        self,
        *,
        submission_id: str,
        character_id: UUID,
        payload: dict,
        submitted_at: datetime,
    ) -> None:
        self.submission_id = submission_id
        self.character_id = character_id
        self.payload = payload
        self.submitted_at = submitted_at


def test_scene_sweep_registered_and_package_passes_strict_validation() -> None:
    loaded = load_mini_game_package(PACKAGE_PATH)
    assert loaded.definition.mechanic_type == EvidenceSearchRacePlugin.mechanic_type


def test_validate_payload_accepts_valid_claim() -> None:
    plugin = EvidenceSearchRacePlugin()
    plugin.validate_payload({"action": "claim", "object_id": "slot-1"})


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"action": "vote"},
        {"action": "claim"},
        {"action": "claim", "object_id": ""},
        {"action": "claim", "object_id": 5},
    ],
)
def test_validate_payload_rejects_invalid_shapes(payload: dict) -> None:
    plugin = EvidenceSearchRacePlugin()
    with pytest.raises(ValueError):
        plugin.validate_payload(payload)


def test_real_object_id_uses_generation_supplied_value_when_present() -> None:
    """Proves the case-grounded path: when content resolution (AW-250) has
    written real_object_id into resolved_content, the plugin must use that
    exact value rather than its own seeded-hash fallback — this is what
    makes "which archetype is real" mean something in the actual case,
    per the design doc's non-negotiable that the mini-game never invents
    this independently of resolved session state.
    """
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-generation-supplied")
    valid_slot_ids = [slot["slot_id"] for slot in plugin._object_slots(snapshot)]
    # Deliberately pick whichever slot the hash fallback would NOT pick, so
    # a test that accidentally ignored the supplied value would fail loudly.
    fallback_pick = plugin._real_object_id(
        load_snapshot(run_seed="seed-generation-supplied")
    )
    forced_choice = next(
        slot_id for slot_id in valid_slot_ids if slot_id != fallback_pick
    )
    resolved_content = dict(snapshot.resolved_content)
    resolved_content["real_object_id"] = forced_choice
    snapshot_with_generation = snapshot.model_copy(
        update={"resolved_content": resolved_content}
    )

    assert plugin._real_object_id(snapshot_with_generation) == forced_choice


def test_real_object_id_falls_back_to_hash_when_not_supplied() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-no-generation")
    assert "real_object_id" not in snapshot.resolved_content
    real_id = plugin._real_object_id(snapshot)
    assert real_id in {slot["slot_id"] for slot in plugin._object_slots(snapshot)}


def test_real_object_id_is_deterministic_across_calls() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-a")
    first = plugin._real_object_id(snapshot)
    second = plugin._real_object_id(snapshot)
    assert first is not None
    assert first == second


def test_real_object_id_changes_with_seed() -> None:
    plugin = EvidenceSearchRacePlugin()
    seeds_and_results = {
        seed: plugin._real_object_id(load_snapshot(run_seed=seed))
        for seed in ("seed-a", "seed-b", "seed-c", "seed-d", "seed-e")
    }
    # Not asserting a specific distribution, just that seed changes the pick
    # for at least one pair (guards against an accidental constant return).
    assert len(set(seeds_and_results.values())) > 1


def test_initialize_state_includes_real_object_in_active_set() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-init")
    real_id = plugin._real_object_id(snapshot)

    progress = plugin.initialize_state(
        snapshot, participants=PARTICIPANTS_4, now=T0
    )

    active_ids = progress.state["active_object_ids"]
    assert len(active_ids) == 5  # 4 players -> 5 objects per rules table
    assert real_id in active_ids
    assert len(progress.events) == 1
    assert progress.events[0].event_type == "scene_sweep_board_started"
    for obj in progress.events[0].payload["objects"]:
        assert "archetype" in obj and "position" in obj


def test_on_submission_rejects_object_not_on_board() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-reject")
    progress = plugin.initialize_state(
        snapshot, participants=PARTICIPANTS_4, now=T0
    )
    off_board = next(
        slot["slot_id"]
        for slot in plugin._object_slots(snapshot)
        if slot["slot_id"] not in progress.state["active_object_ids"]
    )
    submission = make_submission(
        submission_id="s1",
        character_id=PARTICIPANTS_4[0][0],
        object_id=off_board,
        submitted_at=T0,
    )
    with pytest.raises(ValueError, match="not on this round's board"):
        plugin.on_submission(
            snapshot,
            state=progress.state,
            participants=PARTICIPANTS_4,
            submission=submission,  # type: ignore[arg-type]
            accepted_submissions=[submission],  # type: ignore[list-item]
            now=T0,
        )


def test_on_submission_rejects_double_claim() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-double")
    progress = plugin.initialize_state(
        snapshot, participants=PARTICIPANTS_4, now=T0
    )
    object_id = progress.state["active_object_ids"][0]
    first = make_submission(
        submission_id="s1",
        character_id=PARTICIPANTS_4[0][0],
        object_id=object_id,
        submitted_at=T0,
    )
    first_progress = plugin.on_submission(
        snapshot,
        state=progress.state,
        participants=PARTICIPANTS_4,
        submission=first,  # type: ignore[arg-type]
        accepted_submissions=[first],  # type: ignore[list-item]
        now=T0,
    )
    second = make_submission(
        submission_id="s2",
        character_id=PARTICIPANTS_4[1][0],
        object_id=object_id,
        submitted_at=T0 + timedelta(seconds=1),
    )
    with pytest.raises(ValueError, match="already been claimed"):
        plugin.on_submission(
            snapshot,
            state=first_progress.state,
            participants=PARTICIPANTS_4,
            submission=second,  # type: ignore[arg-type]
            accepted_submissions=[first, second],  # type: ignore[list-item]
            now=T0,
        )


def test_board_exhaustion_sets_finalize_status_completed() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-exhaust")
    progress = plugin.initialize_state(
        snapshot, participants=PARTICIPANTS_4, now=T0
    )
    active_ids = list(progress.state["active_object_ids"])
    state = dict(progress.state)
    accepted: list[FakeSubmission] = []
    last_progress = None
    for index, object_id in enumerate(active_ids):
        submission = make_submission(
            submission_id=f"s{index}",
            character_id=PARTICIPANTS_4[index % len(PARTICIPANTS_4)][0],
            object_id=object_id,
            submitted_at=T0 + timedelta(seconds=index),
        )
        accepted.append(submission)
        last_progress = plugin.on_submission(
            snapshot,
            state=state,
            participants=PARTICIPANTS_4,
            submission=submission,  # type: ignore[arg-type]
            accepted_submissions=list(accepted),  # type: ignore[list-item]
            now=T0 + timedelta(seconds=index),
        )
        state = dict(last_progress.state)

    assert last_progress is not None
    assert last_progress.finalize_status == "completed"


def test_claiming_real_object_alone_does_not_finalize_early() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-no-early-exit")
    real_id = plugin._real_object_id(snapshot)
    progress = plugin.initialize_state(
        snapshot, participants=PARTICIPANTS_4, now=T0
    )
    submission = make_submission(
        submission_id="s1",
        character_id=PARTICIPANTS_4[0][0],
        object_id=real_id,
        submitted_at=T0,
    )
    result = plugin.on_submission(
        snapshot,
        state=progress.state,
        participants=PARTICIPANTS_4,
        submission=submission,  # type: ignore[arg-type]
        accepted_submissions=[submission],  # type: ignore[list-item]
        now=T0,
    )
    assert result.finalize_status is None


def test_on_deadline_expired_always_times_out() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-deadline")
    progress = plugin.initialize_state(
        snapshot, participants=PARTICIPANTS_4, now=T0
    )
    result = plugin.on_deadline_expired(
        snapshot,
        state=progress.state,
        participants=PARTICIPANTS_4,
        accepted_submissions=[],
        now=T0 + timedelta(seconds=105),
    )
    assert result.finalize_status == "timed_out"


def test_score_reports_success_when_real_object_claimed() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-score-success")
    real_id = plugin._real_object_id(snapshot)
    finder = PARTICIPANTS_4[2][0]
    submission = make_submission(
        submission_id="s1",
        character_id=finder,
        object_id=real_id,
        submitted_at=T0 + timedelta(seconds=10),
    )
    outcome = plugin.score(snapshot, [submission])  # type: ignore[list-item]
    assert outcome["real-object-claimed"] is True
    assert outcome["finder-character-id"] == str(finder)


def test_score_reports_fallback_when_real_object_never_claimed() -> None:
    plugin = EvidenceSearchRacePlugin()
    snapshot = load_snapshot(run_seed="seed-score-fallback")
    progress = plugin.initialize_state(
        snapshot, participants=PARTICIPANTS_4, now=T0
    )
    decoy_id = next(
        object_id
        for object_id in progress.state["active_object_ids"]
        if object_id != plugin._real_object_id(snapshot)
    )
    submission = make_submission(
        submission_id="s1",
        character_id=PARTICIPANTS_4[0][0],
        object_id=decoy_id,
        submitted_at=T0 + timedelta(seconds=5),
    )
    outcome = plugin.score(snapshot, [submission])  # type: ignore[list-item]
    assert outcome["real-object-claimed"] is False
    assert outcome["finder-character-id"] is None
    assert outcome["decoys-claimed"][str(PARTICIPANTS_4[0][0])] == 1
```

- [ ] **Step 3: Run the tests**

Run: `pytest engine/tests/test_evidence_search_race_runtime.py -v`
Expected: all tests PASS. If `FakeSubmission` type mismatches cause mypy complaints later (Task-3 tests use a lightweight stand-in, not the real ORM class, matching how a fast plugin-level unit test avoids DB setup), that is expected and acceptable for this file — the real ORM class is exercised in Task 4's integration tests instead.

- [ ] **Step 4: Commit**

```bash
git add engine/mini_games/plugins/_evidence_search_race.py engine/tests/test_evidence_search_race_runtime.py
git commit -m "feat(mini-games): implement evidence-search-race plugin"
```

---

## Task 4: Register the plugin and add full runtime integration tests

**Goal:** Wire `EvidenceSearchRacePlugin` into the closed `MechanicRegistry`, and prove the full async lifecycle (create → start → concurrent claims → finalize) works against a real SQLite-backed `MiniGameRuntime`, including the mandatory `assert_knowledge` invariant.

**Files:**
- Modify: `engine/mini_games/plugins/__init__.py`
- Create: `engine/tests/test_scene_sweep_runtime_integration.py`

**Acceptance Criteria:**
- [ ] `default_registry()` includes `EvidenceSearchRacePlugin` alongside the three existing plugins.
- [ ] A full-lifecycle test proves: `create_run` → `start_run` (emits `scene_sweep_board_started`) → `submit_action` for every active object → auto-finalizes with `status="completed"` → the resolved clue (both entries, since success uses `ClueVariant.full`) is asserted into the knowledge graph for every eligible participant, and delivered via `private_delivery` events.
- [ ] A concurrent-claim test proves that of two submissions for the same `object_id`, the second raises `RunStateError` and the mechanic's own `claimed_object_ids` state (the authoritative record, not the submission row's `is_accepted` flag — see the test's docstring for why those can diverge) contains that object exactly once.
- [ ] A fallback test proves: the deadline expires with the real object never claimed → `status="timed_out"` → only the reduced-tagged clue is asserted/delivered.
- [ ] Both success and fallback paths are exercised at 4 and 8 participants (four test functions total for this axis, or one parametrized test — engineer's choice, but all four combinations must run).

**Verify:** `pytest engine/tests/test_scene_sweep_runtime_integration.py -v` → all tests PASS, plus `pytest engine/tests/ -k mini_game -q` still passes (no regression to the other three games' registry-dependent tests).

**Steps:**

- [ ] **Step 1: Register the plugin**

In `engine/mini_games/plugins/__init__.py`, add the import and registration:

```python
from engine.mini_games.plugins._evidence_locker_breach import EvidenceLockerBreachPlugin
from engine.mini_games.plugins._evidence_search_race import EvidenceSearchRacePlugin
from engine.mini_games.plugins._match_3_clue_race import Match3ClueRacePlugin
from engine.mini_games.plugins._social_truth_bluff import SocialTruthBluffPlugin
from engine.mini_games.runtime import MechanicRegistry


def default_registry() -> MechanicRegistry:
    """Return the standard closed registry with all approved mechanic plugins."""
    return MechanicRegistry(
        [
            Match3ClueRacePlugin(),
            EvidenceLockerBreachPlugin(),
            SocialTruthBluffPlugin(),
            EvidenceSearchRacePlugin(),
        ]
    )


__all__ = [
    "EvidenceLockerBreachPlugin",
    "EvidenceSearchRacePlugin",
    "Match3ClueRacePlugin",
    "SocialTruthBluffPlugin",
    "default_registry",
]
```

- [ ] **Step 2: Write the integration test file**

```python
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import (
    Account,
    Character,
    Fact,
    KnowledgeState,
    Session,
    SessionParticipant,
)
from engine.db.testing import make_sqlite_session_factory, patch_metadata_for_sqlite
from engine.events.bus import SessionEventBus
from engine.mini_games.loader import load_mini_game_package
from engine.mini_games.plugins import default_registry
from engine.mini_games.resolver import ResolvedMiniGameSnapshot
from engine.mini_games.runtime import MiniGameRuntime

patch_metadata_for_sqlite()

T0 = datetime(2026, 8, 2, 20, 0, 0, tzinfo=timezone.utc)
PACKAGE_PATH = (
    Path(__file__).resolve().parents[2]
    / "nightcap"
    / "mini_games"
    / "scene-sweep"
)


def load_snapshot(*, run_seed: str) -> ResolvedMiniGameSnapshot:
    loaded = load_mini_game_package(PACKAGE_PATH)
    definition = loaded.definition
    resolved_content = dict(definition.authored_content or {})
    resolved_content["run_seed"] = run_seed
    return ResolvedMiniGameSnapshot(
        game_id=definition.game_id,
        definition_version=definition.version,
        source_content_mode=definition.content_mode,
        mechanic_type=definition.mechanic_type,
        participation_mode=definition.participation_mode.value,
        min_players=definition.min_players,
        max_players=definition.max_players,
        duration_seconds=definition.duration_seconds,
        rules=definition.rules,
        behavioral_outputs=tuple(definition.behavioral_outputs),
        clue_fallback=definition.clue_fallback,
        resolved_content=resolved_content,
    )


@pytest.fixture
async def db() -> AsyncSession:
    _, factory = await make_sqlite_session_factory()
    async with factory() as sess:
        yield sess


async def _setup_session_with_participants(
    db: AsyncSession,
    count: int,
) -> tuple[UUID, list[UUID]]:
    account_id = uuid4()
    session_id = uuid4()
    db.add(Account(account_id=account_id, firebase_uid=f"uid-{account_id}"))
    await db.flush()
    db.add(
        Session(
            session_id=session_id,
            arc_id="arc-1",
            status="active",
            host_account_id=account_id,
            current_beat_id="beat-1",
            quality_tier="standard",
            player_count=count,
        )
    )
    char_ids: list[UUID] = []
    for _ in range(count):
        char_id = uuid4()
        char_ids.append(char_id)
        db.add(Character(character_id=char_id, behavior_profile={}))
    await db.flush()
    for char_id in char_ids:
        db.add(
            SessionParticipant(
                session_id=session_id,
                character_id=char_id,
                join_token=f"tok-{char_id}",
                surface_type="phone",
                is_ai_controlled=False,
            )
        )
    await db.flush()
    return session_id, char_ids


def make_runtime(db: AsyncSession, *, clock_time: datetime = T0) -> MiniGameRuntime:
    return MiniGameRuntime(
        db,
        SessionEventBus(),
        default_registry(),
        clock=lambda: clock_time,
    )


async def _assert_no_leftover_clock_drift() -> None:
    return None


@pytest.mark.parametrize("participant_count", [4, 8])
async def test_full_success_path_asserts_knowledge_for_every_participant(
    db: AsyncSession,
    participant_count: int,
) -> None:
    session_id, char_ids = await _setup_session_with_participants(
        db, participant_count
    )
    snapshot = load_snapshot(run_seed=f"seed-success-{participant_count}")
    runtime = make_runtime(db)

    run = await runtime.create_run(session_id, snapshot)
    run = await runtime.start_run(run.run_id)

    # Discover the round's active object ids from the plugin directly, since
    # the runtime doesn't expose them on the ORM row except via clue_unlock_record.
    from engine.mini_games.plugins._evidence_search_race import (
        EvidenceSearchRacePlugin,
    )

    plugin = EvidenceSearchRacePlugin()
    active_ids = list(run.clue_unlock_record["runtime_state"]["active_object_ids"])

    for index, object_id in enumerate(active_ids):
        submitter = char_ids[index % len(char_ids)]
        run = await runtime.submit_action(
            run.run_id,
            f"sub-{index}",
            submitter,
            {"action": "claim", "object_id": object_id},
        )

    run = await runtime.get_active_run(session_id)
    assert run is None  # terminal runs are excluded from get_active_run

    from sqlalchemy import select as sql_select
    from engine.db.orm import MiniGameRun as MiniGameRunOrm

    result = await db.execute(
        sql_select(MiniGameRunOrm).where(MiniGameRunOrm.session_id == session_id)
    )
    finished = result.scalar_one()
    assert finished.status == "completed"
    assert finished.behavioral_outputs["real-object-claimed"] is True

    # Knowledge is split across two tables: Fact (session-scoped, shared
    # across whoever knows it) and KnowledgeState (the character-to-fact
    # link `assert_knowledge` creates one row of per eligible character).
    # Success delivers both clue entries (full-mode returns every entry in
    # the authored clues list), so expect exactly 2 distinct Facts.
    facts_result = await db.execute(select(Fact).where(Fact.session_id == session_id))
    facts = list(facts_result.scalars().all())
    assert len(facts) == 2

    states_result = await db.execute(
        select(KnowledgeState).where(KnowledgeState.session_id == session_id)
    )
    states = list(states_result.scalars().all())
    assert len(states) == 2 * participant_count

    characters_per_fact: dict[UUID, set[UUID]] = {}
    for state in states:
        characters_per_fact.setdefault(state.fact_id, set()).add(state.character_id)
    for fact_id, known_by in characters_per_fact.items():
        assert known_by == set(char_ids)


@pytest.mark.parametrize("participant_count", [4, 8])
async def test_fallback_path_delivers_only_reduced_clue(
    db: AsyncSession,
    participant_count: int,
) -> None:
    session_id, char_ids = await _setup_session_with_participants(
        db, participant_count
    )
    snapshot = load_snapshot(run_seed=f"seed-fallback-{participant_count}")
    runtime = make_runtime(db, clock_time=T0)

    run = await runtime.create_run(session_id, snapshot)
    run = await runtime.start_run(run.run_id)

    # No submissions; advance the clock past the deadline and check timeout.
    late_runtime = make_runtime(db, clock_time=run.deadline + timedelta(seconds=1))
    await late_runtime.check_timeout(run.run_id)

    from sqlalchemy import select as sql_select
    from engine.db.orm import MiniGameRun as MiniGameRunOrm

    result = await db.execute(
        sql_select(MiniGameRunOrm).where(MiniGameRunOrm.session_id == session_id)
    )
    finished = result.scalar_one()
    assert finished.status == "timed_out"
    assert finished.behavioral_outputs["real-object-claimed"] is False

    # Fallback (ClueVariant.reduced) returns only entries tagged "reduced" —
    # exactly one Fact, shared across every eligible participant's
    # KnowledgeState row.
    facts_result = await db.execute(select(Fact).where(Fact.session_id == session_id))
    facts = list(facts_result.scalars().all())
    assert len(facts) == 1
    assert facts[0].fact_content["variant"] == "reduced"

    states_result = await db.execute(
        select(KnowledgeState).where(KnowledgeState.session_id == session_id)
    )
    states = list(states_result.scalars().all())
    assert len(states) == participant_count
    assert {state.character_id for state in states} == set(char_ids)


async def test_concurrent_double_claim_accepts_exactly_one(
    db: AsyncSession,
) -> None:
    """Proves the mechanic's authoritative state — not raw submission-row
    is_accepted flags — reflects exactly one true claim per object.

    Note on a platform-wide quirk this test deliberately works around: when
    a StatefulMechanicPlugin's on_submission raises ValueError for a
    conflict (here, claiming an already-claimed object), the runtime has
    already flushed the submission row with is_accepted=True (payload shape
    was valid) *before* on_submission runs — the ValueError becomes a
    RunStateError raised to the caller, not a rejection recorded on the row.
    Tell Me Something True's own conflict paths (double-input, wrong-phase
    vote) already behave identically. So the correct assertion is: the
    second call raises, and the mechanic's own claimed_object_ids state
    (not the DB row's is_accepted flag) contains the object exactly once.
    """
    session_id, char_ids = await _setup_session_with_participants(db, 4)
    snapshot = load_snapshot(run_seed="seed-concurrent")
    runtime = make_runtime(db)

    run = await runtime.create_run(session_id, snapshot)
    run = await runtime.start_run(run.run_id)
    active_ids = list(run.clue_unlock_record["runtime_state"]["active_object_ids"])
    target_object_id = active_ids[0]

    first = await runtime.submit_action(
        run.run_id, "sub-a", char_ids[0], {"action": "claim", "object_id": target_object_id}
    )
    assert first.is_accepted is True

    from engine.mini_games.runtime import RunStateError

    with pytest.raises(RunStateError):
        await runtime.submit_action(
            run.run_id,
            "sub-b",
            char_ids[1],
            {"action": "claim", "object_id": target_object_id},
        )

    from sqlalchemy import select as sql_select
    from engine.db.orm import MiniGameRun as MiniGameRunOrm

    result = await db.execute(
        sql_select(MiniGameRunOrm).where(MiniGameRunOrm.run_id == run.run_id)
    )
    reloaded = result.scalar_one()
    claimed_ids = reloaded.clue_unlock_record["runtime_state"]["claimed_object_ids"]
    assert claimed_ids.count(target_object_id) == 1
```

- [ ] **Step 3: Run the tests**

Run: `pytest engine/tests/test_scene_sweep_runtime_integration.py -v`
Expected: all tests PASS.

Run: `pytest engine/tests/ -k mini_game -q`
Expected: no regressions in the other three games' tests.

- [ ] **Step 4: Commit**

```bash
git add engine/mini_games/plugins/__init__.py engine/tests/test_scene_sweep_runtime_integration.py
git commit -m "feat(mini-games): register evidence-search-race and add integration tests"
```

---

## Task 5: Expose Scene Sweep phase state through the API

**Goal:** Add `SceneSweep*` schema classes mirroring the existing `Tmst*` pattern, widen `MiniGameRunResponse.phase_state`'s discriminated union, and add router dispatch so `GET /v1/sessions/{id}/mini-games/active` (and its `/display` sibling) return a Scene Sweep-appropriate view that never leaks which object is real before the reveal.

**Files:**
- Modify: `api/schemas/__init__.py`
- Modify: `api/routers/mini_games.py`
- Create: `api/tests/test_scene_sweep_api.py`

**Note on scope:** `MiniGameRuntime.get_active_run` (in `engine/mini_games/runtime.py`, not modified by this plan) explicitly excludes terminal statuses (`completed`, `timed_out`, `cancelled`) — both `GET /active` and `GET /active/display` only ever return non-terminal runs. That means there is no REST phase-state concept for "the round just ended and here's who found what" — the staged reveal is delivered through the `mini_game_finalized` ContentEvent the shared runtime *already* publishes unconditionally in `_finalize_run` for every mechanic, no new work required. This task therefore only adds phase state for the in-progress ("active") board, not a "revealed" state — do not add a `SceneSweepRevealedPhaseState` or otherwise try to make completed runs visible through these two GET endpoints; that would require changing `get_active_run`'s filtering, which is out of this plan's scope.

**Acceptance Criteria:**
- [ ] `SceneSweepBoardPhaseState` (phase=`"active"`) exposes: `deadline_at`, the active object list (`object_id`, `archetype`, `position`), and `claimed_object_ids` — but never a `real_object_id` or any field indicating which claim was real.
- [ ] `MiniGameRunResponse.phase_state`'s type becomes `Optional[Union[TmstInputPhaseState, TmstSpotlightPhaseState, SceneSweepBoardPhaseState]]` (discriminated on `phase`) — TMST's existing phase literals (`"input"`, `"spotlight"`) and Scene Sweep's new one (`"active"`) do not collide.
- [ ] `submit_mini_game_action` validates Scene Sweep payloads (`{"action": "claim", "object_id": str}`) the same way it already validates TMST payloads, returning 422 on malformed shape.
- [ ] A test proves the `/active` endpoint response for an in-progress Scene Sweep run contains no field that would leak the real object's identity (the plugin-level events already withhold this per Task 3, but this test locks the API contract too, since that's the layer a future web renderer will actually read).
- [ ] Every existing TMST test in `api/tests/test_mini_games_api.py` still passes unmodified (this change is additive to the union, not a replacement).

**Verify:** `pytest api/tests/test_scene_sweep_api.py api/tests/test_mini_games_api.py -v` → all PASS

**Steps:**

- [ ] **Step 1: Add the schema classes**

In `api/schemas/__init__.py`, add these classes immediately after `TmstScoreboardReadyPayload` and before the existing `TmstPhaseState` union declaration:

```python
class SceneSweepObjectState(BaseModel):
    object_id: str
    archetype: str
    position: dict[str, float]


class SceneSweepBoardStartedPayload(BaseModel):
    phase: Literal["active"]
    objects: list[SceneSweepObjectState]


class SceneSweepObjectClaimedPayload(BaseModel):
    object_id: str
    claimed_count: int = Field(ge=0)


class SceneSweepBoardPhaseState(BaseModel):
    phase: Literal["active"]
    deadline_at: Optional[datetime] = None
    objects: list[SceneSweepObjectState]
    claimed_object_ids: list[str]
```

Then change the union declaration from:

```python
TmstPhaseState = Annotated[
    Union[TmstInputPhaseState, TmstSpotlightPhaseState],
    Field(discriminator="phase"),
]
```

to a renamed, widened union (keep `TmstPhaseState` as a backward-compatible alias so nothing else that imports it breaks):

```python
MiniGamePhaseState = Annotated[
    Union[
        TmstInputPhaseState,
        TmstSpotlightPhaseState,
        SceneSweepBoardPhaseState,
    ],
    Field(discriminator="phase"),
]
TmstPhaseState = MiniGamePhaseState
```

Then change `MiniGameRunResponse.phase_state`'s type annotation from `Optional[TmstPhaseState]` to `Optional[MiniGamePhaseState]` (functionally identical after the alias above, but names the field by what it actually is now — multiple games' phase states, not just TMST's).

Also add a Scene Sweep submission payload type, mirroring the TMST pattern, right after `TmstSubmissionPayload`/`TMST_SUBMISSION_PAYLOAD_ADAPTER`:

```python
class SceneSweepClaimActionPayload(BaseModel):
    action: Literal["claim"]
    object_id: str = Field(min_length=1, max_length=64)


SCENE_SWEEP_SUBMISSION_PAYLOAD_ADAPTER: TypeAdapter[SceneSweepClaimActionPayload] = (
    TypeAdapter(SceneSweepClaimActionPayload)
)
```

- [ ] **Step 2: Add router dispatch**

In `api/routers/mini_games.py`, add a game-id constant next to `_TMST_GAME_ID`:

```python
_SCENE_SWEEP_GAME_ID = "scene-sweep"
```

Add the schema imports to the existing `from api.schemas import (...)` block:

```python
    SceneSweepBoardPhaseState,
    SceneSweepClaimActionPayload,
    SceneSweepObjectState,
    SCENE_SWEEP_SUBMISSION_PAYLOAD_ADAPTER,
```

Add a phase-state builder function, placed right after `_build_tmst_phase_state`:

```python
def _scene_sweep_runtime_state(run: MiniGameRun) -> dict[str, Any]:
    record = dict(run.clue_unlock_record or {})
    state = record.get("runtime_state")
    if isinstance(state, dict):
        return state
    return {}


def _build_scene_sweep_phase_state(
    run: MiniGameRun,
) -> SceneSweepBoardPhaseState | None:
    # get_active_run (engine/mini_games/runtime.py) already excludes terminal
    # statuses before a run ever reaches here, so this only needs to handle
    # the in-progress board; the reveal itself travels via the
    # mini_game_finalized ContentEvent, not this REST response. The status
    # guard below is defensive only, matching how _build_tmst_phase_state
    # returns None for any phase it doesn't recognize.
    if run.status != "active":
        return None

    state = _scene_sweep_runtime_state(run)
    active_ids = state.get("active_object_ids", [])
    claimed_ids = state.get("claimed_object_ids", [])
    if not isinstance(active_ids, list):
        return None

    definition_snapshot = run.definition_snapshot or {}
    slots_by_id = {
        slot["slot_id"]: slot
        for slot in definition_snapshot.get("resolved_content", {}).get(
            "object_slots", []
        )
        if isinstance(slot, dict)
    }

    return SceneSweepBoardPhaseState(
        phase="active",
        deadline_at=run.deadline,
        objects=[
            SceneSweepObjectState(
                object_id=object_id,
                archetype=slots_by_id.get(object_id, {}).get("archetype", ""),
                position=slots_by_id.get(object_id, {}).get(
                    "position", {"x": 0.0, "y": 0.0}
                ),
            )
            for object_id in active_ids
            if object_id in slots_by_id
        ],
        claimed_object_ids=list(claimed_ids)
        if isinstance(claimed_ids, list)
        else [],
    )
```

Update `_build_tmst_phase_state`'s call sites (both in `get_active_mini_game` and `get_active_mini_game_display`) to dispatch on game_id instead of assuming TMST. Replace this pattern (it appears twice, once per endpoint):

```python
        phase_state=_build_tmst_phase_state(
            run,
            claims=claims,
            character_id=character_id,
            participant_character_ids=participant_character_ids,
        )
        if run.game_id == _TMST_GAME_ID
        else None,
```

with:

```python
        phase_state=_build_phase_state_for_game(
            run,
            claims=claims,
            character_id=character_id,
            participant_character_ids=participant_character_ids,
        ),
```

(and the analogous replacement using `display_claims` in `get_active_mini_game_display`), then add the small dispatcher function near the other `_build_*` helpers:

```python
def _build_phase_state_for_game(
    run: MiniGameRun,
    *,
    claims: JwtClaims,
    character_id: UUID | None,
    participant_character_ids: list[UUID],
) -> Any:
    if run.game_id == _TMST_GAME_ID:
        return _build_tmst_phase_state(
            run,
            claims=claims,
            character_id=character_id,
            participant_character_ids=participant_character_ids,
        )
    if run.game_id == _SCENE_SWEEP_GAME_ID:
        return _build_scene_sweep_phase_state(run)
    return None
```

Finally, extend `submit_mini_game_action` to validate Scene Sweep payloads the same way it already validates TMST ones. Change:

```python
    action_payload: dict[str, Any] = body.payload
    if run.game_id == _TMST_GAME_ID:
        validated = _validate_tmst_submission_payload(body.payload)
        _ensure_tmst_phase_accepts_action(run, validated)
        action_payload = validated.model_dump()
```

to:

```python
    action_payload: dict[str, Any] = body.payload
    if run.game_id == _TMST_GAME_ID:
        validated = _validate_tmst_submission_payload(body.payload)
        _ensure_tmst_phase_accepts_action(run, validated)
        action_payload = validated.model_dump()
    elif run.game_id == _SCENE_SWEEP_GAME_ID:
        try:
            validated_claim = cast(
                SceneSweepClaimActionPayload,
                SCENE_SWEEP_SUBMISSION_PAYLOAD_ADAPTER.validate_python(body.payload),
            )
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        action_payload = validated_claim.model_dump()
```

- [ ] **Step 3: Write the API test file**

This mirrors `api/tests/test_mini_games_api.py`'s own `db_factory`/`client` fixtures and its `_seed_tmst_session_and_run` helper shape exactly (same file structure: module-level `_SESSION_ID`/`_PART_ID`/`_CHAR_ID`/`_OTHER_PART_ID`/`_OTHER_CHAR_ID` constants, a `_player_claims`/`_host_claims` pair, a `db_factory` fixture that creates an in-memory SQLite engine and runs `Base.metadata.create_all`, and a `client` fixture that overrides `require_player_jwt`/`require_player_or_host_jwt`/`require_host_jwt`/`get_async_session`).

```python
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.testclient import TestClient

from api.auth import (
    JwtClaims,
    require_host_jwt,
    require_player_jwt,
    require_player_or_host_jwt,
)
from api.main import app
from api.schemas import SceneSweepBoardPhaseState
from engine.db import get_async_session
from engine.db.orm import (
    Account,
    Base,
    Character,
    MiniGameRun,
    MiniGameSubmission,
    Session,
    SessionParticipant,
)
from engine.db.testing import patch_metadata_for_sqlite
from engine.mini_games.loader import load_mini_game_package
from engine.mini_games.models import ContentMode
from engine.mini_games.resolver import ResolvedMiniGameSnapshot

patch_metadata_for_sqlite()

_SESSION_ID = uuid4()
_PART_ID = uuid4()
_CHAR_ID = uuid4()
_OTHER_PART_ID = uuid4()
_OTHER_CHAR_ID = uuid4()
_HOST_PART_ID = uuid4()


def _player_claims(
    session_id: UUID = _SESSION_ID, player_id: UUID = _PART_ID
) -> JwtClaims:
    return JwtClaims(
        uid="player-uid", session_id=session_id, player_id=player_id, role="player"
    )


def _host_claims(session_id: UUID = _SESSION_ID) -> JwtClaims:
    return JwtClaims(
        uid="host-uid", session_id=session_id, player_id=_HOST_PART_ID, role="host"
    )


@pytest_asyncio.fixture()
async def db_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        await engine.dispose()


@pytest.fixture()
def client(db_factory: async_sessionmaker[AsyncSession]) -> Iterator[TestClient]:
    async def _override_db() -> AsyncIterator[AsyncSession]:
        async with db_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[require_player_jwt] = lambda: _player_claims()
    app.dependency_overrides[require_player_or_host_jwt] = lambda: _player_claims()
    app.dependency_overrides[require_host_jwt] = lambda: _host_claims()
    app.dependency_overrides[get_async_session] = _override_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def _scene_sweep_snapshot_dict(*, run_seed: str) -> dict[str, Any]:
    from pathlib import Path

    package_path = (
        Path(__file__).resolve().parents[2]
        / "nightcap"
        / "mini_games"
        / "scene-sweep"
    )
    loaded = load_mini_game_package(package_path)
    definition = loaded.definition
    resolved_content = dict(definition.authored_content or {})
    resolved_content["run_seed"] = run_seed
    snap = ResolvedMiniGameSnapshot(
        game_id=definition.game_id,
        definition_version=definition.version,
        source_content_mode=ContentMode.hybrid,
        mechanic_type=definition.mechanic_type,
        participation_mode=definition.participation_mode.value,
        min_players=definition.min_players,
        max_players=definition.max_players,
        duration_seconds=definition.duration_seconds,
        rules=definition.rules,
        behavioral_outputs=tuple(definition.behavioral_outputs),
        clue_fallback=definition.clue_fallback,
        resolved_content=resolved_content,
    )
    return snap.model_dump(mode="json")


async def _seed_scene_sweep_session_and_run(
    factory: async_sessionmaker[AsyncSession],
    *,
    status: str,
    active_object_ids: list[str],
    claimed_object_ids: list[str],
    submissions: list[dict[str, Any]] | None = None,
) -> tuple[UUID, UUID]:
    async with factory() as db:
        account_id = uuid4()
        db.add(Account(account_id=account_id, firebase_uid="host-firebase-uid"))
        await db.flush()

        db.add(
            Session(
                session_id=_SESSION_ID,
                arc_id="nightcap-v1",
                status="active",
                host_account_id=account_id,
                current_beat_id="beat-1",
                quality_tier="standard",
                player_count=4,
            )
        )
        db.add(Character(character_id=_CHAR_ID, behavior_profile={}))
        db.add(Character(character_id=_OTHER_CHAR_ID, behavior_profile={}))
        await db.flush()

        db.add(
            SessionParticipant(
                participant_id=_PART_ID,
                session_id=_SESSION_ID,
                character_id=_CHAR_ID,
                join_token="tok-player",
                surface_type="phone",
                is_ai_controlled=False,
            )
        )
        db.add(
            SessionParticipant(
                participant_id=_OTHER_PART_ID,
                session_id=_SESSION_ID,
                character_id=_OTHER_CHAR_ID,
                join_token="tok-other",
                surface_type="phone",
                is_ai_controlled=False,
            )
        )
        await db.flush()

        run_id = uuid4()
        db.add(
            MiniGameRun(
                run_id=run_id,
                session_id=_SESSION_ID,
                game_id="scene-sweep",
                definition_version="0.1.0",
                definition_snapshot=_scene_sweep_snapshot_dict(
                    run_seed="api-test-seed"
                ),
                status=status,
                revision=0,
                started_at=datetime.now(tz=timezone.utc),
                deadline=datetime(2026, 8, 2, 21, 0, tzinfo=timezone.utc),
                clue_unlock_record={
                    "runtime_state": {
                        "active_object_ids": active_object_ids,
                        "claimed_object_ids": claimed_object_ids,
                    }
                },
            )
        )
        if submissions:
            for submission in submissions:
                db.add(
                    MiniGameSubmission(
                        run_id=run_id,
                        submission_id=submission["submission_id"],
                        character_id=submission["character_id"],
                        submitted_at=submission.get(
                            "submitted_at", datetime.now(tz=timezone.utc)
                        ),
                        payload=submission["payload"],
                        is_accepted=submission.get("is_accepted", True),
                        rejection_reason=submission.get("rejection_reason"),
                    )
                )
        await db.commit()

    return _SESSION_ID, run_id


class TestSceneSweepPhaseState:
    def test_active_phase_state_never_reveals_real_object(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """The /active response for an in-progress run must not contain any
        field naming which object is real — the API-layer lock on top of the
        plugin-level withholding already proven in Task 3.
        """
        session_id, _run_id = asyncio.run(
            _seed_scene_sweep_session_and_run(
                db_factory,
                status="active",
                active_object_ids=["slot-1", "slot-2", "slot-3", "slot-4", "slot-5"],
                claimed_object_ids=["slot-2"],
            )
        )

        resp = client.get(f"/v1/sessions/{session_id}/mini-games/active")

        assert resp.status_code == 200
        body = resp.json()
        raw_text = resp.text
        assert "real_object_id" not in raw_text
        assert "is_real" not in raw_text

        phase_state = SceneSweepBoardPhaseState.model_validate(body["phase_state"])
        assert phase_state.phase == "active"
        assert phase_state.claimed_object_ids == ["slot-2"]
        assert len(phase_state.objects) == 5
        for obj in phase_state.objects:
            assert obj.archetype
            assert set(obj.position.keys()) == {"x", "y"}

    def test_shared_display_view_also_withholds_real_object(
        self,
        client: TestClient,
        db_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """Same withholding guarantee via the unauthenticated display path
        (GET /active/display), which the TV surface will actually call.
        """
        session_id, _run_id = asyncio.run(
            _seed_scene_sweep_session_and_run(
                db_factory,
                status="active",
                active_object_ids=["slot-1", "slot-2", "slot-3", "slot-4", "slot-5"],
                claimed_object_ids=[],
            )
        )

        resp = client.get(f"/v1/sessions/{session_id}/mini-games/active/display")

        assert resp.status_code == 200
        assert "real_object_id" not in resp.text
        assert "is_real" not in resp.text
        phase_state = SceneSweepBoardPhaseState.model_validate(
            resp.json()["phase_state"]
        )
        assert phase_state.phase == "active"
        assert phase_state.claimed_object_ids == []
```

Task 2's own schema test already covers the fallback-variant assertion, so this file does not need a separate `ClueVariant` check.

- [ ] **Step 4: Run the tests**

Run: `pytest api/tests/test_scene_sweep_api.py api/tests/test_mini_games_api.py -v`
Expected: all PASS, including every pre-existing TMST test (proves the union widening didn't break anything).

- [ ] **Step 5: Commit**

```bash
git add api/schemas/__init__.py api/routers/mini_games.py api/tests/test_scene_sweep_api.py
git commit -m "feat(api): expose Scene Sweep phase state and submission validation"
```

---

## Self-Review Notes (for the implementing engineer)

Every step in this plan is written as complete, ready-to-run code — nothing here is a scaffold to fill in. Three corrections were made during the plan's own self-review that are worth knowing about going in, since they diverge from a first-pass reading of the design doc or a naive implementation:

1. **"Which archetype is real" is generation-supplied, not randomly picked.** The design doc requires this choice to be grounded in the session's actual case data. `_real_object_id` (Task 3) reads `resolved_content["real_object_id"]` first — a value the content-resolution/generation step is expected to write — and only falls back to a deterministic seeded hash when that's absent (authored-only fixtures, unit tests). Do not simplify this back down to "just hash it" — that would silently drop the case-grounding requirement.
2. **Rejected double-claims don't show up as `is_accepted=False`.** A `StatefulMechanicPlugin.on_submission` that raises `ValueError` for a conflict does so *after* the runtime has already flushed the submission row with `is_accepted=True` — the same behavior Tell Me Something True's own conflict paths already have. The mechanic's own `claimed_object_ids` state (not the submission row) is the authoritative record of what actually got claimed. Task 4's concurrent-claim test checks that state directly, not row flags — don't "fix" it to check `is_accepted` instead, that would make the test wrong, not the code.
3. **There is no REST "revealed" phase state, on purpose.** `MiniGameRuntime.get_active_run` excludes terminal runs, so `GET /active` and `GET /active/display` can never surface a completed round. The staged reveal travels through the `mini_game_finalized` ContentEvent the shared runtime already publishes for every mechanic — Task 5 only adds phase state for the in-progress board. Do not add a "revealed" schema/endpoint path back in without first changing `get_active_run`'s filtering, which is out of this plan's scope.

Additionally:
- The double-claim SQLite query pattern in Task 4 mirrors what's already proven working in `test_mini_game_runtime.py` and `test_mini_games_api.py` (in-memory SQLite via `patch_metadata_for_sqlite`); no new query patterns were introduced.
- This plan does not touch `engine/mini_games/runtime.py`, `models.py`, or `resolver.py` — if a task here seems to require changing one of those, stop and re-read Task 3's "Deterministic derivation helpers" section; the design deliberately avoids needing engine changes by keeping all Scene Sweep-specific state derivable from `snapshot` + `submissions` alone.
- Web rendering (TypeScript, `nightcap-web/`) is out of scope for every task in this plan. Do not create a `client/renderer.ts` for Scene Sweep here — that's the next plan, written after this one's API shape is settled and stable.
