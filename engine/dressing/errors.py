from __future__ import annotations


class DressingError(Exception):
    """Base error for dressing lookup failures."""


class DressingPackNotAuthored(DressingError):
    """Raised when a declared wrapper has no authored pack content."""


class UnknownWrapper(DressingError):
    """Raised when a wrapper id is outside the declared wrapper set."""


class DressingRegistryError(DressingError):
    """Raised when registry configuration is missing, malformed, or unmatched."""
