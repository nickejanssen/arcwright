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
        claims = self._accepted_claims_by_object(submissions)

        completion_time_ms: dict[str, int] = {}
        decoys_claimed: dict[str, int] = {}
        real_object_claimed = False
        finder_character_id: UUID | None = None

        start_time = min((s.submitted_at for s in submissions), default=None)

        # Iterate the deduped, earliest-wins claims (not raw submissions) so
        # a rejected-but-flushed duplicate claim for an object_id someone
        # else already won can never overwrite the true winner's credit or
        # inflate a decoy count. See _accepted_claims_by_object for why raw
        # `submissions` can legitimately contain such rejected duplicates.
        # completion_time_ms is likewise derived only from these winning
        # claims, so a participant's completion time reflects an accepted
        # claim rather than a claim on-submission actually rejected.
        for submission in sorted(claims.values(), key=lambda s: s.submitted_at):
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
        slots_by_id = {slot["slot_id"]: slot for slot in self._object_slots(snapshot)}
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

        finalize_status = "completed" if len(claimed_ids) >= len(active_ids) else None
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
            key=lambda slot_id: sha256(f"{seed}:{slot_id}".encode("utf-8")).hexdigest(),
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
    def _accepted_claims_by_object(
        submissions: list[MiniGameSubmission],
    ) -> dict[str, MiniGameSubmission]:
        """Dedupe accepted submissions by object_id, keeping the earliest.

        `submit_action` (engine/mini_games/runtime.py) flushes a submission
        row with is_accepted=True before on_submission's own claim
        arbitration runs; a losing race for an already-claimed object_id
        still lands here with is_accepted=True even though on_submission
        rejected it via a raised ValueError. This dedup is what makes
        score() agree with the mechanic's own authoritative claimed_object_ids
        state instead of crediting whoever happens to sort last.
        """
        result: dict[str, MiniGameSubmission] = {}
        for submission in sorted(submissions, key=lambda s: s.submitted_at):
            object_id = submission.payload.get("object_id")
            if isinstance(object_id, str) and object_id not in result:
                result[object_id] = submission
        return result
