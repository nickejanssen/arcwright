"""Application service for local browser mini-game onboarding."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from engine.mini_games.authoring.models import (
    MiniGameOnboardingRequest,
    MiniGameOnboardingSession,
    OnboardingAnalysis,
    OnboardingConfirmation,
)
from engine.mini_games.authoring.workspace import LocalAuthoringWorkspace

_HIGH_IMPACT_CONFIRMATIONS = (
    OnboardingConfirmation(
        key="story_affordance",
        prompt="What story purpose should this mini-game serve?",
    ),
    OnboardingConfirmation(
        key="participation_model",
        prompt="How should players participate?",
    ),
    OnboardingConfirmation(
        key="result_meaning",
        prompt="What should the result mean for players and story?",
    ),
    OnboardingConfirmation(
        key="placement_authority",
        prompt="Who may decide where this mini-game appears?",
    ),
)


class MiniGameOnboardingService:
    """Coordinate the local authoring workspace without runtime authority."""

    def __init__(self, workspace: LocalAuthoringWorkspace | None = None) -> None:
        self._workspace = workspace or LocalAuthoringWorkspace()

    def start(
        self,
        request: MiniGameOnboardingRequest,
        *,
        workspace_root: Path,
    ) -> MiniGameOnboardingSession:
        return self._workspace.create(request, workspace_root)

    def load(
        self,
        session_id: UUID,
        *,
        workspace_root: Path,
    ) -> MiniGameOnboardingSession:
        return self._workspace.load(session_id, workspace_root)

    def analyze(
        self,
        *,
        source: Path,
        destination_game_id: str | None,
    ) -> OnboardingAnalysis:
        if not source.is_dir():
            raise ValueError("browser source must identify a directory")
        return OnboardingAnalysis(
            recommended_path=(
                "destination_first" if destination_game_id else "reusable_first"
            ),
            destination_game_id=destination_game_id,
            confirmations=_HIGH_IMPACT_CONFIRMATIONS,
            uncertainty=(
                "Gameplay intent and high-impact authoring fields require confirmation.",
            ),
        )
