from __future__ import annotations

from datetime import datetime

from engine.resources.errors import (
    ActivationNotFoundError,
    InsufficientBalanceError,
    TargetIneligibleError,
)
from engine.resources.models import (
    EffectActivation,
    EffectDefinition,
    EffectFamily,
    ResourceBalance,
)


class ResourceResolver:
    """Owns balance state, targeting eligibility, and deterministic effect application."""

    def __init__(self) -> None:
        self._balances: dict[str, ResourceBalance] = {}
        self._activations: list[EffectActivation] = []
        self._currently_protected_target: str | None = None
        self._offensive_modifiers_by_window: dict[str, int] = {}
        self._info_control_targets_this_beat: dict[tuple[str, str], int] = {}
        # Keyed by the activator's player id — the player who armed the
        # counterplay effect. One-time-use: consumed by counter_and_reveal_source.
        self._armed_counterplay: dict[str, EffectActivation] = {}

    def set_balance(self, balance: ResourceBalance) -> None:
        self._balances[balance.player_id] = balance

    def get_balance(self, player_id: str) -> ResourceBalance:
        return self._balances[player_id]

    def grant(
        self,
        *,
        player_id: str,
        amount: int,
        source: str | None,
        beat_id: str,
        now: datetime,
    ) -> ResourceBalance:
        """Credit a player's balance (mini-game reward or protected earn path).

        Bounded above by ``bank_cap`` so no earn path — mini-game win streak or
        otherwise — can grow a balance without limit. ``source`` and ``beat_id``
        are accepted for parity with ``ResourceGrant`` (and future telemetry
        callers) but do not affect the bounded-credit computation itself.
        """
        del source, beat_id, now
        if amount <= 0:
            raise ValueError("grant amount must be positive")
        balance = self._balances[player_id]
        new_amount = min(balance.current_amount + amount, balance.bank_cap)
        updated = balance.model_copy(update={"current_amount": new_amount})
        self._balances[player_id] = updated
        return updated

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
        if effect.requires_target and target_id is None:
            raise TargetIneligibleError(f"{effect.effect_key} requires a target")

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

        if effect.family == EffectFamily.counterplay:
            self._armed_counterplay[activator_id] = activation

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
        raise ActivationNotFoundError(
            f"no unresolved activation for window {window_id}"
        )

    def counter_and_reveal_source(
        self, *, countering_activator_id: str, countered_window_id: str, now: datetime
    ) -> EffectActivation:
        """Counter-effect exception: reveal the countered sabotage's source immediately, private to the countering player, bypassing normal per-question reveal timing.

        Requires that ``countering_activator_id`` has an armed (unused)
        counterplay-family activation, and that the countered sabotage
        actually targeted that player — otherwise any player could deanonymize
        any saboteur without having activated a counterplay effect themselves.
        Consumes the armed counterplay on success (one-time-use).
        """
        if countering_activator_id not in self._armed_counterplay:
            raise TargetIneligibleError(
                f"{countering_activator_id} has no armed counterplay effect"
            )

        for i, activation in enumerate(self._activations):
            if activation.interaction_window_id == countered_window_id:
                if activation.target_id != countering_activator_id:
                    raise TargetIneligibleError(
                        f"window {countered_window_id} was not targeted at "
                        f"{countering_activator_id}"
                    )
                del self._armed_counterplay[countering_activator_id]
                revealed = activation.model_copy(update={"source_reveal_at": now})
                self._activations[i] = revealed
                return revealed
        raise ActivationNotFoundError(
            f"no activation to counter for window {countered_window_id}"
        )
