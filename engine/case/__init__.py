"""Arc-agnostic case-resolution module (AW-281).

This module carries NO game-specific vocabulary. Types are labelled
generically (``CastMember``, ``EvidenceEntry``, ``AuthorizedFalsehood``)
and arc-specific meaning is injected as string values (``role="suspect"``,
``role="victim"``, ``evidence_type="trace"``, etc.). Arc-specific case
content lives outside this module in the arc's own directory (e.g.
``nightcap/case_skeletons/``, ``nightcap/case_taxonomy/``).

Public API::

    from engine.case import resolve, ResolvedCase, CaseSkeleton, ...
"""

from __future__ import annotations

from engine.case.errors import CaseInvariantError, CaseResolutionError
from engine.case.models import (
    AuthorizedFalsehood,
    CaseSkeleton,
    CastMember,
    EvidenceEntry,
    ResolvedCase,
)

__all__ = [
    "AuthorizedFalsehood",
    "CaseInvariantError",
    "CaseResolutionError",
    "CaseSkeleton",
    "CastMember",
    "EvidenceEntry",
    "ResolvedCase",
]
