"""Application service for local browser mini-game onboarding."""

from __future__ import annotations

import re
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

_ANALYSIS_UNCERTAINTY = (
    "Browser source does not reveal gameplay intent; confirm story_affordance.",
    "Browser controls do not establish a participation model; confirm participation_model.",
    "Observed result fields do not establish gameplay or story meaning; confirm result_meaning.",
    "Published bridge events and preview authority flags do not grant runtime or placement authority; confirm placement_authority.",
)

_HTML_SUFFIXES = frozenset({".htm", ".html"})
_JAVASCRIPT_SUFFIXES = frozenset({".cjs", ".js", ".mjs"})
_BUTTON_PATTERN = re.compile(r"<button\b(?P<attributes>[^>]*)>", re.IGNORECASE)
_ATTRIBUTE_PATTERN = re.compile(
    r"\b(?P<name>id|class|data-value)\s*=\s*(?P<quote>[\"'])"
    r"(?P<value>.*?)"
    r"(?P=quote)",
    re.IGNORECASE,
)
_PUBLISH_PATTERN = re.compile(r"\bpublish\(\s*[\"'](?P<event>[^\"']+)[\"']")
_NON_AUTHORITATIVE_PATTERN = re.compile(
    r"\bauthoritative\s*:\s*false\b",
    re.IGNORECASE,
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
        evidence = _inspect_browser_source(source)
        return OnboardingAnalysis(
            recommended_path=(
                "destination_first" if destination_game_id else "reusable_first"
            ),
            destination_game_id=destination_game_id,
            confirmations=_HIGH_IMPACT_CONFIRMATIONS,
            evidence=evidence,
            uncertainty=_ANALYSIS_UNCERTAINTY,
        )


def _inspect_browser_source(source: Path) -> tuple[str, ...]:
    files = sorted(
        (path for path in source.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(source).as_posix(),
    )
    html_files = [path for path in files if path.suffix.lower() in _HTML_SUFFIXES]
    javascript_files = [
        path for path in files if path.suffix.lower() in _JAVASCRIPT_SUFFIXES
    ]
    asset_files = [
        path
        for path in files
        if path not in html_files and path not in javascript_files
    ]

    html_source = "\n".join(_read_source_text(path) for path in html_files)
    javascript_source = "\n".join(_read_source_text(path) for path in javascript_files)
    controls = _button_controls(html_source)
    bridge_events = sorted(
        {match.group("event") for match in _PUBLISH_PATTERN.finditer(javascript_source)}
    )
    bridge_transports = [
        transport
        for transport in ("CustomEvent", "postMessage")
        if transport in javascript_source
    ]
    authority_observation = (
        "authoritative=false"
        if _NON_AUTHORITATIVE_PATTERN.search(javascript_source)
        else "not observed"
    )

    return (
        _describe_paths("HTML documents", html_files, source),
        _describe_paths("JavaScript sources", javascript_files, source),
        _describe_paths("Other assets", asset_files, source),
        _describe_values("HTML controls", controls),
        _describe_values("Published bridge events", bridge_events),
        _describe_values("Bridge transports", bridge_transports),
        f"Observed preview result field: {authority_observation}",
    )


def _read_source_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _button_controls(html_source: str) -> list[str]:
    controls: list[str] = []
    for match in _BUTTON_PATTERN.finditer(html_source):
        attributes = {
            attribute.group("name").lower(): attribute.group("value")
            for attribute in _ATTRIBUTE_PATTERN.finditer(match.group("attributes"))
        }
        if control_id := attributes.get("id"):
            controls.append(control_id)
        elif "input" in attributes.get("class", "").split():
            value = attributes.get("data-value")
            controls.append(f"input[{value}]" if value else "input")
        else:
            controls.append("button")
    return controls


def _describe_paths(label: str, paths: list[Path], root: Path) -> str:
    values = [path.relative_to(root).as_posix() for path in paths]
    return _describe_values(label, values)


def _describe_values(label: str, values: list[str]) -> str:
    return f"{label}: {', '.join(values) if values else 'none'}"
