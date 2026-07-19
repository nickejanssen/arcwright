from __future__ import annotations

from datetime import datetime

from engine.resources.errors import InsufficientBalanceError, TargetIneligibleError
from engine.resources.models import EffectActivation, EffectDefinition, ResourceBalance


class ResourceResolver:
    """Owns balance state, targeting eligibility, and deterministic effect application."""

    def __init__(self) -> None:
        self._balances: dict[str, ResourceBalance] = {}
        self._activations: list[EffectActivation] = []
        self._currently_protected_target: str | None = None
        self._offensive_modifiers_by_window: dict[str, int] = {}
        self._info_control_targets_this_beat: dict[tuple[str, str], int] = {}

    def set_balance(self, balance: ResourceBalance) -> None:
        self._balances[balance.player_id] = balance

    def get_balance(self, player_id: str) -> ResourceBalance:
        return self._balances[player_id]

    def activate(
        self,
        *,
        effect: EffectDefinition,
        activator_id: str,
        target_id: str | None,
        window_id: str,
        beat_id: str,
        now: datetime,
    ) -> EffectActivation:
        balance = self._balances[activator_id]
        if balance.current_amount - effect.cost < 0:
            raise InsufficientBalanceError(
                f"{activator_id} cannot afford {effect.effect_key}"
            )
        if balance.current_amount - effect.cost < balance.protected_floor:
            raise InsufficientBalanceError(
                f"{activator_id} spend would breach protected floor"
            )

        if target_id is not None and effect.is_offensive:
            if target_id == self._currently_protected_target:
                raise TargetIneligibleError(
                    f"{target_id} is under post-target protection"
                )
            if self._offensive_modifiers_by_window.get(window_id, 0) >= 1:
                raise TargetIneligibleError(
                    f"window {window_id} already carries an offensive modifier"
                )
            if effect.is_information_control:
                key = (target_id, beat_id)
                if self._info_control_targets_this_beat.get(key, 0) >= 1:
                    raise TargetIneligibleError(
                        f"{target_id} already received an information-control sabotage this beat"
                    )

        self._balances[activator_id] = balance.model_copy(
            update={"current_amount": balance.current_amount - effect.cost}
        )

        if target_id is not None and effect.is_offensive:
            self._offensive_modifiers_by_window[window_id] = (
                self._offensive_modifiers_by_window.get(window_id, 0) + 1
            )
            if effect.is_information_control:
                key = (target_id, beat_id)
                self._info_control_targets_this_beat[key] = (
                    self._info_control_targets_this_beat.get(key, 0) + 1
                )
            self._currently_protected_target = target_id

        activation = EffectActivation(
            effect_key=effect.effect_key,
            activator_id=activator_id,
            target_id=target_id,
            interaction_window_id=window_id,
        )
        self._activations.append(activation)
        return activation

    def open_new_window(self) -> None:
        """Call when a new interaction window opens — clears any standing post-target protection."""
        self._currently_protected_target = None

    def resolve_activation(self, *, window_id: str, now: datetime) -> EffectActivation:
        for i, activation in enumerate(self._activations):
            if (
                activation.interaction_window_id == window_id
                and activation.resolved_at is None
            ):
                resolved = activation.model_copy(
                    update={"resolved_at": now, "source_reveal_at": now}
                )
                self._activations[i] = resolved
                return resolved
        raise ValueError(f"no unresolved activation for window {window_id}")

    def counter_with_sting_operation(
        self, *, sting_activator_id: str, countered_window_id: str, now: datetime
    ) -> EffectActivation:
        """Sting Operation's exception: reveal the countered sabotage's source immediately, private to the Sting Operation user."""
        for i, activation in enumerate(self._activations):
            if activation.interaction_window_id == countered_window_id:
                revealed = activation.model_copy(update={"source_reveal_at": now})
                self._activations[i] = revealed
                return revealed
        raise ValueError(f"no activation to counter for window {countered_window_id}")
