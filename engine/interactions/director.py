from __future__ import annotations

import random
from collections.abc import Collection, Mapping, Sequence
from uuid import UUID

from engine.interactions.errors import (
    InteractionLifecycleError,
    InteractionLimitError,
    SelectionValidationError,
    WindowClosedError,
)
from engine.interactions.menu import build_option_menu
from engine.interactions.models import (
    InteractionDefinition,
    InteractionResolution,
    InteractionSelection,
    InteractionTarget,
    InteractionWindow,
    PublicInteractionGroup,
    ResolutionVisibility,
    WindowStatus,
)


class InteractionDirector:
    """Owns deterministic interaction windows for one authored definition."""

    def __init__(self, definition: InteractionDefinition, seed: int) -> None:
        self.definition = definition
        self.seed = seed
        self._windows: dict[str, InteractionWindow] = {}
        self._resolutions: dict[str, InteractionResolution] = {}
        self._spent_by_beat: dict[str, dict[UUID, int]] = {}

    def open_window(
        self,
        *,
        window_id: str,
        beat_id: str | None = None,
        round_index: int,
        participant_ids: Sequence[UUID],
        eligible_targets: Sequence[InteractionTarget],
        held_evidence_by_participant: Mapping[UUID, Collection[str]],
        authorized_knowledge_context_ref: str | None = None,
        claim_reference_ids: Sequence[str] = (),
        evidence_reference_ids: Sequence[str] = (),
    ) -> InteractionWindow:
        if window_id in self._windows:
            raise InteractionLifecycleError(f"window already exists: {window_id}")
        if not participant_ids:
            raise InteractionLimitError("at least one participant is required")
        try:
            allowance = self.definition.limit.selections_for(len(participant_ids))
        except ValueError as exc:
            raise InteractionLimitError(str(exc)) from exc
        if len(participant_ids) != len(set(participant_ids)):
            raise InteractionLimitError("participant IDs must be unique")
        if not eligible_targets:
            raise SelectionValidationError("at least one target is required")
        target_ids = [target.target_id for target in eligible_targets]
        if len(target_ids) != len(set(target_ids)):
            raise SelectionValidationError("target IDs must be unique")
        staged_target_id = random.Random(self.seed + round_index).choice(
            sorted(target_ids)
        )
        effective_beat_id = beat_id or self.definition.interaction_id
        spent = self._spent_by_beat.setdefault(effective_beat_id, {})
        menus = {
            participant_id: [
                option.option_id
                for option in build_option_menu(
                    self.definition,
                    held_evidence_by_participant.get(participant_id, set()),
                    evidence_start_index=round_index * 2,
                )
            ]
            for participant_id in participant_ids
        }
        window = InteractionWindow(
            window_id=window_id,
            interaction_id=self.definition.interaction_id,
            beat_id=effective_beat_id,
            round_index=round_index,
            participant_ids=list(participant_ids),
            eligible_targets=list(eligible_targets),
            menus_by_participant=menus,
            remaining_selections={
                participant_id: max(allowance - spent.get(participant_id, 0), 0)
                for participant_id in participant_ids
            },
            staged_target_id=staged_target_id,
            authorized_knowledge_context_ref=authorized_knowledge_context_ref,
            claim_reference_ids=tuple(claim_reference_ids),
            evidence_reference_ids=tuple(evidence_reference_ids),
        )
        self._windows[window_id] = window
        return window

    def menu_for(self, window_id: str, participant_id: UUID):
        window = self._get_window(window_id)
        try:
            option_ids = window.menus_by_participant[participant_id]
        except KeyError as exc:
            raise SelectionValidationError("participant is not in the window") from exc
        options = {option.option_id: option for option in self.definition.options}
        return [options[option_id].model_copy(deep=True) for option_id in option_ids]

    def submit_selection(
        self,
        *,
        window_id: str,
        participant_id: UUID,
        target_id: str,
        option_id: str,
        selection_id: str | None = None,
    ) -> InteractionSelection:
        window = self._get_window(window_id)
        if window.status is not WindowStatus.selecting:
            raise WindowClosedError(f"window is {window.status.value}")
        if participant_id not in window.menus_by_participant:
            raise SelectionValidationError("participant is not in the window")
        if target_id not in {target.target_id for target in window.eligible_targets}:
            raise SelectionValidationError("target is not eligible")
        if option_id not in window.menus_by_participant[participant_id]:
            raise SelectionValidationError("option is not available to participant")
        if selection_id is not None:
            existing = window.selections.get(selection_id)
            if existing is None or existing.participant_id != participant_id:
                raise SelectionValidationError(
                    "selection does not belong to participant"
                )
        else:
            if window.remaining_selections[participant_id] <= 0:
                raise InteractionLimitError("participant has no selections remaining")
            window.remaining_selections[participant_id] -= 1
            spent = self._spent_by_beat.setdefault(window.beat_id, {})
            spent[participant_id] = spent.get(participant_id, 0) + 1
            selection_id = (
                f"{window.window_id}:{participant_id}:{len(window.selections)}"
            )
        selection = InteractionSelection(
            selection_id=selection_id,
            participant_id=participant_id,
            target_id=target_id,
            option_id=option_id,
        )
        window.selections[selection.selection_id] = selection
        return selection

    def lock_window(
        self,
        *,
        window_id: str,
        allow_missing: bool = False,
    ) -> InteractionResolution:
        window = self._get_window(window_id)
        if window_id in self._resolutions:
            return self._resolutions[window_id]
        if window.status is not WindowStatus.selecting:
            raise InteractionLifecycleError(f"window is {window.status.value}")
        if not allow_missing:
            selected_participants = {
                selection.participant_id for selection in window.selections.values()
            }
            missing = set(window.participant_ids) - selected_participants
            if missing:
                raise InteractionLifecycleError(
                    "every participant must submit a selection"
                )
        window.status = WindowStatus.locked
        participant_order = list(window.participant_ids)
        offset = window.round_index % len(participant_order)
        rotated = participant_order[offset:] + participant_order[:offset]
        ordered = [
            selection
            for participant_id in rotated
            for selection in window.selections.values()
            if selection.participant_id == participant_id
        ]
        options = {option.option_id: option for option in self.definition.options}
        grouped: dict[tuple[str, str], list[str]] = {}
        private: list[InteractionSelection] = []
        for selection in ordered:
            grouped.setdefault((selection.target_id, selection.option_id), []).append(
                selection.selection_id
            )
            if (
                options[selection.option_id].resolution_visibility
                is ResolutionVisibility.private
            ):
                private.append(selection)
        public_groups = [
            PublicInteractionGroup(
                group_id=f"{window.window_id}:{target_id}:{option_id}",
                target_id=target_id,
                option_id=option_id,
                selection_ids=tuple(selection_ids),
            )
            for (target_id, option_id), selection_ids in grouped.items()
        ]
        resolution = InteractionResolution(
            window_id=window.window_id,
            round_index=window.round_index,
            beat_id=window.beat_id,
            ordered_selections=tuple(ordered),
            public_groups=tuple(public_groups),
            private_selections=tuple(private),
            authorized_knowledge_context_ref=window.authorized_knowledge_context_ref,
            claim_reference_ids=window.claim_reference_ids,
            evidence_reference_ids=window.evidence_reference_ids,
        )
        window.status = WindowStatus.resolved
        self._resolutions[window_id] = resolution
        return resolution

    def _get_window(self, window_id: str) -> InteractionWindow:
        try:
            return self._windows[window_id]
        except KeyError as exc:
            raise InteractionLifecycleError(f"unknown window: {window_id}") from exc
