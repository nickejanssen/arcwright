"""Errors raised by claim recording and contradiction detection."""

from __future__ import annotations


class ClaimError(Exception):
    """Base error for deterministic claim recording and contradiction detection failures."""


class ClaimNotFoundError(ClaimError):
    """Raised when a flag references a claim ID with no matching recorded claim."""


class AlreadyResolvedError(ClaimError):
    """Raised when a flag targets a claim with a confirmed contradiction."""
