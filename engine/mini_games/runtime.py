"""Deterministic mini-game runtime.

Architecture:
  docs/decisions/0009-mini-game-runtime-boundary.md
  docs/architecture/03-arc-execution.md §3.4 (human arc primacy)
  docs/architecture/04-knowledge-graph.md §4.3 (knowledge assertion invariant)
  docs/architecture/05-session-persistence.md §5.2 (persistence model)
  docs/architecture/08-event-system.md §8.1 (surface agnosticism)

Invariants (non-negotiable, per AGENTS.md):
  - Python exclusively decides lifecycle, validity, scoring, outcome, and clue release.
  - Deadlines are set from the injected clock at create_run time; client timestamps
    are never trusted.
  - Submission IDs are caller-supplied idempotency keys deduplicated per run.
  - Optimistic concurrency via revision counter on mini_game_runs.
  - assert_knowledge is called for every unlocked fact before the run is committed.
  - Surface-agnostic ContentEvent emission only; no rendering logic here.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from typing import Any, Protocol, cast, runtime_checkable
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from engine.db.orm import MiniGameRun, MiniGameSubmission
from engine.events.bus import SessionEventBus
from engine.events.models import AudienceTarget, ContentEvent, EventCategory
from engine.knowledge.graph import assert_knowledge
from engine.mini_games.models import BehavioralScope, ClueVariant, DelayedClueFallback
from engine.mini_games.resolver import ResolvedMiniGameSnapshot

# ---------------------------------------------------------------------------
# Clock abstraction — injected so no test touches wall time.
# ---------------------------------------------------------------------------

Clock = Callable[[], datetime]


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class MiniGameRuntimeError(Exception):
    """Base for all runtime errors raised by this module."""


class UnknownMechanicTypeError(MiniGameRuntimeError):
    """Raised when a mechanic_type is not registered. Rejects before run creation."""


class RunStateError(MiniGameRuntimeError):
    """Raised when a lifecycle operation is invalid for the current run state."""


class RevisionConflictError(MiniGameRuntimeError):
    """Raised when an optimistic concurrency write conflicts with a concurrent update."""


class DerivedOutputValidationError(MiniGameRuntimeError):
    """Raised when a derived behavioral output has no non-derived sibling in scope."""


# ---------------------------------------------------------------------------
# Mechanic plugin protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class MechanicPlugin(Protocol):
    """Contract every mechanic plugin must satisfy.

    Mechanic-specific scoring implementations are out of scope for AW-251.
    Plugins provide the dispatch slot; implementations ship as separate tasks.
    """

    mechanic_type: str

    def validate_payload(self, payload: dict[str, Any]) -> None:
        """Raise ValueError if the payload shape is invalid for this mechanic."""
        ...

    def is_threshold_met(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
    ) -> bool:
        """Return True if scoring threshold is met and the run should finalize."""
        ...

    def score(
        self,
        snapshot: ResolvedMiniGameSnapshot,
        submissions: list[MiniGameSubmission],
    ) -> dict[str, Any]:
        """Return the scoring outcome dict. Called only on finalization."""
        ...


# ---------------------------------------------------------------------------
# Mechanic registry — closed; unknown types rejected at runtime resolution.
# ---------------------------------------------------------------------------


class MechanicRegistry:
    """Closed registry of approved mechanic plugins.

    Unknown mechanic_type values are rejected before any run is created (AC7).
    """

    def __init__(self, plugins: Sequence[MechanicPlugin]) -> None:
        self._registry: dict[str, MechanicPlugin] = {}
        for plugin in plugins:
            self._registry[plugin.mechanic_type] = plugin

    def get(self, mechanic_type: str) -> MechanicPlugin:
        plugin = self._registry.get(mechanic_type)
        if plugin is None:
            registered = sorted(self._registry)
            raise UnknownMechanicTypeError(
                f"mechanic_type {mechanic_type!r} is not registered. "
                f"Registered types: {registered}"
            )
        return plugin


# ---------------------------------------------------------------------------
# Behavioral output validation (AC8)
# ---------------------------------------------------------------------------


def _validate_behavioral_outputs(snapshot: ResolvedMiniGameSnapshot) -> None:
    """Reject a derived output if no non-derived sibling in the same scope exists.

    Validation is against the resolved definition snapshot (not authoring time).
    """
    non_derived_scopes: set[BehavioralScope] = {
        o.scope for o in snapshot.behavioral_outputs if not o.derived
    }
    for output in snapshot.behavioral_outputs:
        if output.derived and output.scope not in non_derived_scopes:
            raise DerivedOutputValidationError(
                f"behavioral output {output.key!r} is derived but no non-derived "
                f"sibling exists in scope {output.scope.value!r}"
            )


# ---------------------------------------------------------------------------
# Clue unlock helpers
# ---------------------------------------------------------------------------

_MINI_GAME_FACT_TYPE = "mini_game_clue"


def _build_clue_unlock_entry(
    clue: dict[str, Any],
    *,
    release_type: str,
    host_account_id: UUID | None = None,
    timestamp: datetime,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "clue_id": clue.get("clue_id", ""),
        "release_type": release_type,
        "variant": clue.get("variant", "full"),
        "timestamp": timestamp.isoformat(),
    }
    if host_account_id is not None:
        entry["host_account_id"] = str(host_account_id)
    return entry


async def _assert_clue_knowledge(
    db: AsyncSession,
    *,
    session_id: UUID,
    clue: dict[str, Any],
    eligible_character_ids: list[UUID],
) -> None:
    """Call assert_knowledge for every eligible character for a single clue.

    This is the mandatory platform invariant from docs/architecture/04-knowledge-graph.md §4.3.
    It cannot be skipped for performance or any other reason.
    """
    fact_content = {
        "clue_id": clue.get("clue_id", ""),
        "variant": clue.get("variant", "full"),
        "content": clue.get("content", {}),
    }
    for character_id in eligible_character_ids:
        await assert_knowledge(
            db,
            session_id=session_id,
            character_id=character_id,
            fact_type=_MINI_GAME_FACT_TYPE,
            fact_content=fact_content,
        )


# ---------------------------------------------------------------------------
# Main runtime
# ---------------------------------------------------------------------------

_TERMINAL_STATUSES = frozenset({"completed", "timed_out", "cancelled"})
_PAUSED_STATUS = "paused"


class MiniGameRuntime:
    """Deterministic mini-game lifecycle manager.

    All state transitions are Python-authoritative. TypeScript renders only.
    Pass a ``clock`` callable (returning UTC datetime) so tests never touch
    wall time.
    """

    def __init__(
        self,
        db: AsyncSession,
        bus: SessionEventBus,
        registry: MechanicRegistry,
        *,
        clock: Clock = _utcnow,
    ) -> None:
        self._db = db
        self._bus = bus
        self._registry = registry
        self._clock = clock

    # ------------------------------------------------------------------
    # create_run
    # ------------------------------------------------------------------

    async def create_run(
        self,
        session_id: UUID,
        resolved_snapshot: ResolvedMiniGameSnapshot,
    ) -> MiniGameRun:
        """Create a pending run from a resolved snapshot.

        Validates mechanic_type against the closed registry (AC7) and
        behavioral outputs for derived-sibling constraint (AC8) before
        inserting any row.
        """
        # AC7: reject unknown mechanic_type before run is created
        self._registry.get(resolved_snapshot.mechanic_type)

        # AC8: validate derived outputs against the snapshot
        _validate_behavioral_outputs(resolved_snapshot)

        now = self._clock()
        from datetime import timedelta

        deadline = now + timedelta(seconds=resolved_snapshot.duration_seconds)

        run = MiniGameRun(
            session_id=session_id,
            game_id=resolved_snapshot.game_id,
            definition_version=resolved_snapshot.definition_version,
            definition_snapshot=resolved_snapshot.model_dump(mode="json"),
            status="pending",
            revision=0,
            started_at=None,
            deadline=deadline,
            paused_at=None,
            pause_deadline_remaining_seconds=None,
            completed_at=None,
            cancelled_at=None,
            outcome=None,
            behavioral_outputs=None,
            clue_unlock_record={},
        )
        self._db.add(run)
        await self._db.flush()
        return run

    # ------------------------------------------------------------------
    # start_run
    # ------------------------------------------------------------------

    async def start_run(self, run_id: UUID) -> MiniGameRun:
        """Transition pending → active. Emits a game-start ContentEvent."""
        run = await self._load_run(run_id)
        if run.status != "pending":
            raise RunStateError(
                f"start_run requires status=pending, got {run.status!r}"
            )

        now = self._clock()
        await self._increment_revision(run)
        run.status = "active"
        run.started_at = now
        await self._db.flush()

        snapshot = self._decode_snapshot(run)
        await self._publish(
            run,
            category=EventCategory.state_transition,
            event_type="mini_game_started",
            target_audience=AudienceTarget.all,
            payload={
                "game_id": run.game_id,
                "mechanic_type": snapshot.mechanic_type,
                "deadline": run.deadline.isoformat() if run.deadline else None,
                "duration_seconds": snapshot.duration_seconds,
            },
        )
        return run

    # ------------------------------------------------------------------
    # submit_action
    # ------------------------------------------------------------------

    async def submit_action(
        self,
        run_id: UUID,
        submission_id: str,
        character_id: UUID,
        payload: dict[str, Any],
    ) -> MiniGameSubmission:
        """Validate and record a player submission. Idempotent on submission_id.

        - If the run deadline has passed, triggers timeout path first.
        - Concurrent submissions are serialized via revision increment.
        - Duplicate submission_id returns the existing record unchanged.
        """
        run = await self._load_run(run_id)

        if run.status != "active":
            raise RunStateError(
                f"submit_action requires status=active, got {run.status!r}"
            )

        now = self._clock()

        # Check for timeout before processing submission
        if run.deadline and now > run.deadline:
            await self._finalize_run(run, status="timed_out")
            raise RunStateError(
                "submission rejected: run deadline exceeded and run timed out"
            )

        # Idempotency: return existing record for duplicate submission_id
        existing = await self._find_submission(run_id, submission_id)
        if existing is not None:
            return existing

        snapshot = self._decode_snapshot(run)
        plugin = self._registry.get(snapshot.mechanic_type)

        # Validate payload and record acceptance/rejection
        rejection_reason: str | None = None
        is_accepted = True
        try:
            plugin.validate_payload(payload)
        except (ValueError, TypeError) as exc:
            rejection_reason = str(exc)
            is_accepted = False

        # Acquire optimistic lock by bumping revision
        await self._increment_revision(run)

        submission = MiniGameSubmission(
            run_id=run_id,
            submission_id=submission_id,
            character_id=character_id,
            submitted_at=now,
            payload=payload,
            is_accepted=is_accepted,
            rejection_reason=rejection_reason,
            scored_at=None,
        )
        self._db.add(submission)
        await self._db.flush()

        # Check scoring threshold after accepted submission
        if is_accepted:
            accepted = await self._load_accepted_submissions(run_id)
            if plugin.is_threshold_met(snapshot, accepted):
                await self._finalize_run(run, status="completed")

        return submission

    # ------------------------------------------------------------------
    # check_timeout
    # ------------------------------------------------------------------

    async def check_timeout(self, run_id: UUID) -> MiniGameRun | None:
        """Externally-driven timeout check. Returns the updated run if timed out."""
        run = await self._load_run(run_id)
        if run.status != "active":
            return None
        if run.deadline and self._clock() > run.deadline:
            await self._finalize_run(run, status="timed_out")
            return run
        return None

    # ------------------------------------------------------------------
    # pause_run / resume_run
    # ------------------------------------------------------------------

    async def pause_run(self, run_id: UUID) -> MiniGameRun:
        """Capture remaining deadline and freeze the run in paused state (AC3)."""
        run = await self._load_run(run_id)
        if run.status != "active":
            raise RunStateError(f"pause_run requires status=active, got {run.status!r}")

        now = self._clock()
        if run.deadline:
            remaining = max(0.0, (run.deadline - now).total_seconds())
        else:
            remaining = 0.0

        await self._increment_revision(run)
        run.status = _PAUSED_STATUS
        run.paused_at = now
        run.pause_deadline_remaining_seconds = remaining
        await self._db.flush()
        return run

    async def resume_run(self, run_id: UUID) -> MiniGameRun:
        """Restore active state; adjust deadline forward by pause duration (AC3)."""
        run = await self._load_run(run_id)
        if run.status != _PAUSED_STATUS:
            raise RunStateError(
                f"resume_run requires status=paused, got {run.status!r}"
            )

        from datetime import timedelta

        now = self._clock()
        remaining = run.pause_deadline_remaining_seconds or 0.0
        new_deadline = now + timedelta(seconds=remaining)

        await self._increment_revision(run)
        run.status = "active"
        run.deadline = new_deadline
        run.paused_at = None
        run.pause_deadline_remaining_seconds = None
        await self._db.flush()

        snapshot = self._decode_snapshot(run)
        await self._publish(
            run,
            category=EventCategory.state_transition,
            event_type="mini_game_resumed",
            target_audience=AudienceTarget.all,
            payload={
                "game_id": run.game_id,
                "mechanic_type": snapshot.mechanic_type,
                "deadline": new_deadline.isoformat(),
                "remaining_seconds": remaining,
            },
        )
        return run

    # ------------------------------------------------------------------
    # override_clue_release
    # ------------------------------------------------------------------

    async def override_clue_release(
        self,
        run_id: UUID,
        clues: list[dict[str, Any]],
        host_account_id: UUID,
    ) -> MiniGameRun:
        """Release clues immediately outside the scoring path. Logs the override (AC4).

        The host may override regardless of run state except cancelled.
        """
        run = await self._load_run(run_id)
        if run.status == "cancelled":
            raise RunStateError(
                "override_clue_release is not allowed on a cancelled run"
            )

        now = self._clock()
        eligible_character_ids = await self._eligible_character_ids(run.session_id)

        unlock_record: dict[str, Any] = dict(run.clue_unlock_record or {})
        overrides: list[dict[str, Any]] = list(unlock_record.get("overrides", []))

        for clue in clues:
            # Mandatory knowledge assertion (platform invariant, §4.3)
            await _assert_clue_knowledge(
                self._db,
                session_id=run.session_id,
                clue=clue,
                eligible_character_ids=eligible_character_ids,
            )
            entry = _build_clue_unlock_entry(
                clue,
                release_type="host_override",
                host_account_id=host_account_id,
                timestamp=now,
            )
            overrides.append(entry)

            await self._publish(
                run,
                category=EventCategory.private_delivery,
                event_type="mini_game_clue_unlocked",
                target_audience=AudienceTarget.all,
                payload={
                    "clue_id": clue.get("clue_id", ""),
                    "release_type": "host_override",
                    "variant": clue.get("variant", "full"),
                },
            )

        unlock_record["overrides"] = overrides
        await self._increment_revision(run)
        run.clue_unlock_record = unlock_record
        await self._db.flush()
        return run

    # ------------------------------------------------------------------
    # Internal: finalization
    # ------------------------------------------------------------------

    async def _finalize_run(
        self,
        run: MiniGameRun,
        *,
        status: str,
    ) -> None:
        """Score, release clues, assert knowledge, emit events, transition to terminal.

        Called when threshold is met (status=completed) or deadline expires
        (status=timed_out). Knowledge assertion is mandatory before commit (§4.3).
        """
        snapshot = self._decode_snapshot(run)
        plugin = self._registry.get(snapshot.mechanic_type)
        submissions = await self._load_accepted_submissions(run.run_id)

        outcome = plugin.score(snapshot, submissions)

        now = self._clock()
        eligible_character_ids = await self._eligible_character_ids(run.session_id)

        clues_to_unlock: list[dict[str, Any]] = []
        release_type: str

        if status == "timed_out":
            fallback: DelayedClueFallback = snapshot.clue_fallback
            authored_clues = _extract_authored_clues(snapshot, fallback.clue_variant)
            clues_to_unlock = authored_clues
            release_type = (
                "fallback_reduced"
                if fallback.clue_variant is ClueVariant.reduced
                else "fallback_full"
            )
        else:
            clues_to_unlock = _extract_authored_clues(snapshot, ClueVariant.full)
            release_type = "scoring_unlock"

        unlock_record: dict[str, Any] = dict(run.clue_unlock_record or {})
        unlocked: list[dict[str, Any]] = list(unlock_record.get("unlocked", []))

        for clue in clues_to_unlock:
            # Mandatory knowledge assertion for every clue × every eligible character
            await _assert_clue_knowledge(
                self._db,
                session_id=run.session_id,
                clue=clue,
                eligible_character_ids=eligible_character_ids,
            )
            entry = _build_clue_unlock_entry(
                clue,
                release_type=release_type,
                timestamp=now,
            )
            unlocked.append(entry)

            await self._publish(
                run,
                category=EventCategory.private_delivery,
                event_type="mini_game_clue_unlocked",
                target_audience=AudienceTarget.all,
                payload={
                    "clue_id": clue.get("clue_id", ""),
                    "release_type": release_type,
                    "variant": clue.get("variant", "full"),
                },
            )

        unlock_record["unlocked"] = unlocked
        if status == "timed_out":
            unlock_record["fallback_type"] = release_type

        behavioral_outputs = _compute_behavioral_outputs(snapshot, submissions, outcome)

        await self._increment_revision(run)
        run.status = status
        run.outcome = outcome
        run.behavioral_outputs = behavioral_outputs
        run.clue_unlock_record = unlock_record
        if status == "completed":
            run.completed_at = now
        else:
            run.completed_at = now  # timed_out also records completion time

        # Mark submissions as scored
        for sub in submissions:
            sub.scored_at = now

        await self._db.flush()

        await self._publish(
            run,
            category=EventCategory.state_transition,
            event_type="mini_game_finalized",
            target_audience=AudienceTarget.all,
            payload={
                "game_id": run.game_id,
                "status": status,
                "release_type": release_type,
                "clues_released": len(clues_to_unlock),
            },
        )

    # ------------------------------------------------------------------
    # Internal: helpers
    # ------------------------------------------------------------------

    async def _load_run(self, run_id: UUID) -> MiniGameRun:
        result = await self._db.execute(
            select(MiniGameRun).where(MiniGameRun.run_id == run_id)
        )
        run = result.scalar_one_or_none()
        if run is None:
            raise MiniGameRuntimeError(f"run {run_id} not found")
        return run

    async def _find_submission(
        self,
        run_id: UUID,
        submission_id: str,
    ) -> MiniGameSubmission | None:
        result = await self._db.execute(
            select(MiniGameSubmission).where(
                MiniGameSubmission.run_id == run_id,
                MiniGameSubmission.submission_id == submission_id,
            )
        )
        return result.scalar_one_or_none()

    async def _load_accepted_submissions(
        self, run_id: UUID
    ) -> list[MiniGameSubmission]:
        result = await self._db.execute(
            select(MiniGameSubmission)
            .where(
                MiniGameSubmission.run_id == run_id,
                MiniGameSubmission.is_accepted.is_(True),
            )
            .order_by(MiniGameSubmission.submitted_at)
        )
        return list(result.scalars().all())

    async def _increment_revision(self, run: MiniGameRun) -> None:
        """Atomically increment revision via a WHERE-guarded UPDATE (optimistic lock).

        Raises RevisionConflictError if the expected revision no longer matches,
        indicating a concurrent modification. The caller must retry or surface the
        conflict.
        """
        expected = run.revision
        cursor = cast(
            CursorResult[Any],
            await self._db.execute(
                update(MiniGameRun)
                .where(
                    MiniGameRun.run_id == run.run_id,
                    MiniGameRun.revision == expected,
                )
                .values(revision=expected + 1)
            ),
        )
        if cursor.rowcount == 0:
            raise RevisionConflictError(
                f"revision conflict on run {run.run_id}: "
                f"expected revision {expected} but it was already updated"
            )
        run.revision = expected + 1

    async def _eligible_character_ids(self, session_id: UUID) -> list[UUID]:
        """Return all character IDs that are participants in the session."""
        from engine.db.orm import SessionParticipant

        result = await self._db.execute(
            select(SessionParticipant.character_id).where(
                SessionParticipant.session_id == session_id
            )
        )
        return list(result.scalars().all())

    async def _publish(
        self,
        run: MiniGameRun,
        *,
        category: EventCategory,
        event_type: str,
        target_audience: AudienceTarget,
        payload: dict[str, Any],
    ) -> None:
        from engine.events.models import PresentationHints

        event = ContentEvent(
            session_id=run.session_id,
            timestamp=self._clock(),
            category=category,
            event_type=event_type,
            target_audience=target_audience,
            payload=payload,
            presentation_hints=PresentationHints(),
        )
        await self._bus.publish(event)

    @staticmethod
    def _decode_snapshot(run: MiniGameRun) -> ResolvedMiniGameSnapshot:
        return ResolvedMiniGameSnapshot.model_validate(run.definition_snapshot)


# ---------------------------------------------------------------------------
# Clue extraction from snapshot
# ---------------------------------------------------------------------------


def _extract_authored_clues(
    snapshot: ResolvedMiniGameSnapshot,
    variant: ClueVariant,
) -> list[dict[str, Any]]:
    """Extract clues from the resolved content for the given variant.

    The resolved_content dict may carry a ``clues`` list where each entry
    has a ``variant`` key (``"full"`` or ``"reduced"``) and a ``clue_id``.
    For ``ClueVariant.full``, all clues are returned.
    For ``ClueVariant.reduced``, only entries explicitly tagged ``"reduced"``
    are returned (solvability guarantee: reduced subset must remain sufficient).
    """
    raw_clues = snapshot.resolved_content.get("clues", [])
    if not isinstance(raw_clues, list):
        return []

    result: list[dict[str, Any]] = []
    for clue in raw_clues:
        if not isinstance(clue, dict):
            continue
        clue_variant = clue.get("variant", "full")
        if variant is ClueVariant.full:
            result.append(clue)
        elif clue_variant == "reduced":
            result.append(clue)
    return result


# ---------------------------------------------------------------------------
# Behavioral output computation (AC5, AC8)
# ---------------------------------------------------------------------------


def _compute_behavioral_outputs(
    snapshot: ResolvedMiniGameSnapshot,
    submissions: list[MiniGameSubmission],
    outcome: dict[str, Any],
) -> dict[str, Any]:
    """Build the session-scoped behavioral output record.

    Derived outputs are validated against non-derived siblings in the same scope
    (AC8). In v1, behavioral outputs are session-scoped observations only;
    they do not feed killer assignment or cross-session analysis (AC5).
    """
    non_derived_scopes: set[BehavioralScope] = {
        o.scope for o in snapshot.behavioral_outputs if not o.derived
    }

    outputs: dict[str, Any] = {}
    for declaration in snapshot.behavioral_outputs:
        if declaration.derived and declaration.scope not in non_derived_scopes:
            # Already caught at create_run time; guard defensively here too.
            raise DerivedOutputValidationError(
                f"behavioral output {declaration.key!r} is derived but no "
                f"non-derived sibling exists in scope {declaration.scope.value!r}"
            )
        # Pull value from outcome dict if present; otherwise None.
        outputs[declaration.key] = outcome.get(declaration.key)

    return outputs
