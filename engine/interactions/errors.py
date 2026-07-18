from __future__ import annotations


class InteractionError(Exception):
    """Base error for deterministic interaction lifecycle failures."""


class WindowClosedError(InteractionError):
    """Raised when a selection is submitted after a window is locked."""


class InteractionLimitError(InteractionError):
    """Raised when a participant has no selection allowance remaining."""


class SelectionValidationError(InteractionError):
    """Raised when a selection does not match the open interaction window."""


class InteractionLifecycleError(InteractionError):
    """Raised when a window cannot transition to the requested state."""
