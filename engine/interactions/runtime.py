from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from datetime import datetime
from typing import Any
from uuid import UUID

from engine.arc.models import ArcDefinition
from engine.events.models import ContentEvent
from engine.interactions.director import InteractionDirector
from engine.interactions.errors import (
    InteractionLifecycleError,
    SelectionValidationError,
)
from engine.interactions.events import (
    build_private_feedback_event,
    build_public_answer_event,
)
from engine.interactions.models import (
    InteractionSelection,
    InteractionTarget,
    InteractionWindow,
)


class InteractionRuntime:
    """Arc-backed interaction round state machine and event boundary."""

    def __init__(
        self,
        *,
        arc_definition: ArcDefinition,
        session_id: UUID,
        seed: int,
    ) -> None:
        self.arc_definition = arc_definition
        self.session_id = session_id
        self._directors = {
            definition.interaction_id: InteractionDirector(definition, seed=seed)
            for definition in arc_definition.interactions
        }
        self._window_directors: dict[str, InteractionDirector] = {}

    def open_window(
        self,
        *,
        beat_id: str,
        window_id: str,
        round_index: int,
        participant_ids: Sequence[UUID],
        eligible_targets: Sequence[InteractionTarget],
        held_evidence_by_participant: Mapping[UUID, Collection[str]],
        interaction_id: str | None = None,
        authorized_knowledge_context_ref: str | None = None,
        claim_reference_ids: Sequence[str] = (),
        evidence_reference_ids: Sequence[str] = (),
    ) -> InteractionWindow:
        beat = next(
            (beat for beat in self.arc_definition.beats if beat.beat_id == beat_id),
            None,
        )
        if beat is None:
            raise SelectionValidationError(f"unknown beat: {beat_id}")
        available_ids = beat.interaction_ids
        if interaction_id is None:
            if len(available_ids) != 1:
                raise InteractionLifecycleError(
                    "beat must reference exactly one interaction or provide interaction_id"
                )
            interaction_id = available_ids[0]
        if interaction_id not in available_ids:
            raise SelectionValidationError("interaction is not configured for beat")
        try:
            director = self._directors[interaction_id]
        except KeyError as exc:
            raise InteractionLifecycleError(
                "interaction definition is missing"
            ) from exc
        window = director.open_window(
            window_id=window_id,
            beat_id=beat_id,
            round_index=round_index,
            participant_ids=participant_ids,
            eligible_targets=eligible_targets,
            held_evidence_by_participant=held_evidence_by_participant,
            authorized_knowledge_context_ref=authorized_knowledge_context_ref,
            claim_reference_ids=claim_reference_ids,
            evidence_reference_ids=evidence_reference_ids,
        )
        self._window_directors[window_id] = director
        return window

    def submit_selection(
        self,
        *,
        window_id: str,
        participant_id: UUID,
        target_id: str,
        option_id: str,
        selection_id: str | None = None,
    ) -> InteractionSelection:
        director = self._director_for_window(window_id)
        return director.submit_selection(
            window_id=window_id,
            participant_id=participant_id,
            target_id=target_id,
            option_id=option_id,
            selection_id=selection_id,
        )

    def resolve_window(
        self,
        *,
        window_id: str,
        timestamp: datetime,
        answer_payload_by_group: Mapping[str, dict[str, Any]] | None = None,
        feedback_payload_by_selection: Mapping[str, dict[str, Any]] | None = None,
        actor_id: UUID | None = None,
        allow_missing: bool = False,
    ) -> list[ContentEvent]:
        director = self._director_for_window(window_id)
        resolution = director.lock_window(
            window_id=window_id, allow_missing=allow_missing
        )
        answers = answer_payload_by_group or {}
        feedback = feedback_payload_by_selection or {}
        events = [
            build_public_answer_event(
                session_id=self.session_id,
                group=group,
                answer_payload=answers.get(group.group_id, {}),
                timestamp=timestamp,
                actor_id=actor_id,
            )
            for group in resolution.public_groups
        ]
        events.extend(
            build_private_feedback_event(
                session_id=self.session_id,
                selection=selection,
                feedback_payload=feedback.get(selection.selection_id, {}),
                timestamp=timestamp,
            )
            for selection in resolution.ordered_selections
        )
        return events

    def _director_for_window(self, window_id: str) -> InteractionDirector:
        try:
            return self._window_directors[window_id]
        except KeyError as exc:
            raise InteractionLifecycleError(f"unknown window: {window_id}") from exc
