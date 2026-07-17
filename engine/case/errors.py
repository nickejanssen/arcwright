"""Exception types raised by the case-resolution module."""

from __future__ import annotations


class CaseResolutionError(Exception):
    """Raised when a case cannot be resolved (missing skeleton, bad seed, etc.)."""


class CaseInvariantError(CaseResolutionError):
    """Raised when a resolved case fails a runtime fairness invariant.

    Subclass of CaseResolutionError so callers can catch either. Emit
    the failing invariant name (``solvability`` or ``lie_falsifiability``)
    in the message plus enough seed-and-skeleton context to reproduce.
    """
