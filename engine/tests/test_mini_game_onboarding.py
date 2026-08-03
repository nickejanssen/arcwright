import shutil
from hashlib import sha256
from pathlib import Path
from uuid import UUID

import pytest

from engine.mini_games.authoring import (
    ArtifactVersionRef,
    BrowserImportSource,
    LocalAuthoringWorkspace,
    MiniGameOnboardingRequest,
    MiniGameOnboardingService,
)
from engine.mini_games.authoring import workspace as workspace_module

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "browser_minigames" / "tmst-canary"


@pytest.fixture
def onboarding_service() -> MiniGameOnboardingService:
    return MiniGameOnboardingService()


@pytest.fixture
def tmst_browser_source() -> Path:
    return FIXTURE_ROOT


@pytest.fixture
def import_source(tmp_path: Path, tmst_browser_source: Path) -> Path:
    source = tmp_path / "source"
    shutil.copytree(tmst_browser_source, source)
    return source


@pytest.fixture
def onboarding_request(import_source: Path) -> MiniGameOnboardingRequest:
    return MiniGameOnboardingRequest(
        source=BrowserImportSource(
            source_type="static_bundle",
            source_ref=str(import_source),
            source_access="source_and_build",
        ),
        destination_game_id="nightcap-couch-race-v1",
        cohort="first_time",
    )


def sha256_tree(root: Path) -> str:
    digest = sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def test_tmst_canary_requires_one_destination_and_only_high_impact_questions(
    onboarding_service,
    tmst_browser_source,
):
    analysis = onboarding_service.analyze(
        source=tmst_browser_source,
        destination_game_id="nightcap-couch-race-v1",
    )
    assert analysis.recommended_path == "destination_first"
    assert analysis.destination_game_id == "nightcap-couch-race-v1"
    assert {item.key for item in analysis.confirmations} == {
        "story_affordance",
        "participation_model",
        "result_meaning",
        "placement_authority",
    }


def test_import_copies_to_private_workspace_and_preserves_source(
    onboarding_service: MiniGameOnboardingService,
    onboarding_request: MiniGameOnboardingRequest,
    import_source: Path,
    tmp_path: Path,
):
    workspace = tmp_path / "workspace"
    before = sha256_tree(import_source)

    session = onboarding_service.start(
        onboarding_request,
        workspace_root=workspace,
    )

    assert sha256_tree(import_source) == before
    assert session.private_source_ref is not None
    assert sha256_tree(workspace / session.private_source_ref) == before
    assert session.original_source_unchanged is True
    assert session.state == "imported"


def test_onboarding_session_resumes_from_versioned_artifacts(
    onboarding_service: MiniGameOnboardingService,
    onboarding_request: MiniGameOnboardingRequest,
    tmp_path: Path,
):
    workspace = tmp_path / "workspace"
    first = onboarding_service.start(
        onboarding_request,
        workspace_root=workspace,
    )

    resumed = onboarding_service.load(
        first.session_id,
        workspace_root=workspace,
    )

    assert resumed == first


def test_import_rejects_workspace_inside_source(
    onboarding_service: MiniGameOnboardingService,
    onboarding_request: MiniGameOnboardingRequest,
    import_source: Path,
):
    with pytest.raises(ValueError, match="workspace cannot be inside"):
        onboarding_service.start(
            onboarding_request,
            workspace_root=import_source / "workspace",
        )


def test_import_rejects_source_symlink_escape(
    onboarding_service: MiniGameOnboardingService,
    onboarding_request: MiniGameOnboardingRequest,
    import_source: Path,
    tmp_path: Path,
):
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        (import_source / "escape").symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlinks unavailable: {exc}")

    with pytest.raises(ValueError, match="symlink escapes source root"):
        onboarding_service.start(
            onboarding_request,
            workspace_root=tmp_path / "workspace",
        )


def test_workspace_rejects_session_path_escape(
    monkeypatch: pytest.MonkeyPatch,
    onboarding_request: MiniGameOnboardingRequest,
    tmp_path: Path,
):
    session_id = UUID("00000000-0000-0000-0000-000000000001")
    monkeypatch.setattr(workspace_module, "uuid4", lambda: session_id)
    root = tmp_path / "workspace"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    try:
        (root / str(session_id)).symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlinks unavailable: {exc}")

    with pytest.raises(ValueError, match="path escapes workspace root"):
        LocalAuthoringWorkspace().create(onboarding_request, root)


def test_workspace_rejects_duplicate_session_id(
    monkeypatch: pytest.MonkeyPatch,
    onboarding_request: MiniGameOnboardingRequest,
    tmp_path: Path,
):
    session_id = UUID("00000000-0000-0000-0000-000000000002")
    monkeypatch.setattr(workspace_module, "uuid4", lambda: session_id)
    workspace = LocalAuthoringWorkspace()
    root = tmp_path / "workspace"
    workspace.create(onboarding_request, root)

    with pytest.raises(FileExistsError, match="session already exists"):
        workspace.create(onboarding_request, root)


def test_workspace_rejects_confirmed_artifact_overwrite(
    onboarding_request: MiniGameOnboardingRequest,
    tmp_path: Path,
):
    workspace = LocalAuthoringWorkspace()
    root = tmp_path / "workspace"
    first = workspace.create(onboarding_request, root)
    confirmed = ArtifactVersionRef(
        artifact_id="tmst-package",
        version="0.1.0",
        sha256="1" * 64,
    )
    second = first.model_copy(update={"revision": 2, "proposed_package": confirmed})
    workspace.save(second, root)
    replacement = second.model_copy(
        update={
            "revision": 3,
            "proposed_package": confirmed.model_copy(update={"sha256": "2" * 64}),
        }
    )

    with pytest.raises(ValueError, match="confirmed artifact cannot be overwritten"):
        workspace.save(replacement, root)
