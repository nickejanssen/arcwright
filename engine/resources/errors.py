from __future__ import annotations


class ResourceError(Exception):
    """Base error for deterministic resource/effect resolution failures."""


class InsufficientBalanceError(ResourceError):
    """Raised when a spend would exceed available balance or breach the protected floor."""


class TargetIneligibleError(ResourceError):
    """Raised when a target fails a targeting-eligibility guardrail check."""


class UnknownEffectError(ResourceError):
    """Raised when an effect_key has no registered EffectDefinition."""


class ActivationNotFoundError(ResourceError):
    """Raised when no unresolved EffectActivation matches the requested window.

    Distinct from UnknownEffectError: this is a lookup failure against
    already-recorded activations (e.g. resolving or countering a window that
    was never activated, or was already resolved), not a missing
    EffectDefinition registration.
    """
