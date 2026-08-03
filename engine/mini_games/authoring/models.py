"""Shared contracts for browser mini-game authoring sessions."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

_SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
_SEMVER_PATTERN = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"
_SHA256_PATTERN = r"^[a-f0-9]{64}$"
_NAMESPACED_KEY_PATTERN = r"^[a-z0-9]+(?:[.-][a-z0-9]+)+$"
_CONFIRMATION_KEY_PATTERN = r"^[a-z][a-z0-9_]*$"

Slug = Annotated[str, Field(pattern=_SLUG_PATTERN)]
SemVer = Annotated[str, Field(pattern=_SEMVER_PATTERN)]
Sha256 = Annotated[str, Field(pattern=_SHA256_PATTERN)]
NamespacedKey = Annotated[str, Field(pattern=_NAMESPACED_KEY_PATTERN)]


class ArtifactVersionRef(BaseModel):
    """Immutable reference to one exact authoring artifact version."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    artifact_id: Slug
    version: SemVer
    sha256: Sha256


class BrowserImportSource(BaseModel):
    """Approved browser source intake contract from spec 0080."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_type: Literal["static_bundle", "hosted_url"]
    source_ref: str = Field(min_length=1, max_length=2048)
    source_sha256: Sha256 | None = None
    source_access: Literal["build_only", "source_and_build"]


class MiniGameOnboardingRequest(BaseModel):
    """One browser mini-game onboarding request."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source: BrowserImportSource
    destination_game_id: str | None = Field(default=None, pattern=_SLUG_PATTERN)
    hosting_preference: Literal["managed", "external"] = "managed"
    cohort: Literal["first_time", "returning"]


class OnboardingConfirmation(BaseModel):
    """A high-impact authoring fact that requires a user decision."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    key: str = Field(pattern=_CONFIRMATION_KEY_PATTERN)
    prompt: str = Field(min_length=1)
    confirmed_value: str | None = None


class OnboardingAnalysis(BaseModel):
    """Inspectable authoring analysis without runtime authority."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    recommended_path: Literal["destination_first", "reusable_first"]
    destination_game_id: str | None = Field(default=None, pattern=_SLUG_PATTERN)
    confirmations: tuple[OnboardingConfirmation, ...]
    evidence: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()


class GenerationPermissionReceipt(BaseModel):
    """Approved generation permission contract from spec 0079."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    receipt_id: str = Field(min_length=1, max_length=256)
    destination_game_id: str = Field(pattern=_SLUG_PATTERN)
    adaptation_id: str = Field(pattern=_SLUG_PATTERN)
    approved_categories: tuple[
        Literal["code", "art", "animation", "audio", "copy", "configuration"],
        ...,
    ]
    denied_asset_refs: tuple[str, ...] = ()
    remember_for_project: bool = False
    approved_by: str = Field(min_length=1, max_length=256)
    approved_at: datetime


class ReadinessState(str, Enum):
    """Progressive readiness states from spec 0080."""

    imported = "imported"
    reusable = "reusable"
    playtest_ready = "playtest_ready"
    production_ready = "production_ready"


class ReadinessEvidence(BaseModel):
    """One privacy-safe readiness observation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: str
    category: NamespacedKey
    status: Literal["pass", "fail", "not_run", "blocked", "human_review"]
    summary: str
    artifact_refs: tuple[str, ...] = ()
    observed_at: datetime | None = None


class MiniGameReadinessReport(BaseModel):
    """Progressive readiness report from spec 0080."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    report_id: str
    package_ref: ArtifactVersionRef
    adaptation_ref: ArtifactVersionRef | None
    current_state: ReadinessState
    state_label: str
    state_explanation: str
    next_action: str | None
    estimated_next_action_minutes: int | None = Field(default=None, ge=0)
    blockers: tuple[str, ...]
    evidence: tuple[ReadinessEvidence, ...]
    first_time_elapsed_ms: int | None = Field(default=None, ge=0)
    returning_elapsed_ms: int | None = Field(default=None, ge=0)


class MiniGameOnboardingSession(BaseModel):
    """Versioned local record for resumable browser onboarding."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    session_id: UUID
    revision: int = Field(default=1, ge=1)
    request: MiniGameOnboardingRequest
    state: ReadinessState
    source_fingerprint: Sha256
    private_source_ref: str | None = None
    original_source_unchanged: Literal[True] = True
    analysis: OnboardingAnalysis | None = None
    proposed_package: ArtifactVersionRef | None = None
    proposed_adaptation: ArtifactVersionRef | None = None
    permission_receipt: GenerationPermissionReceipt | None = None
    readiness_report: MiniGameReadinessReport | None = None
