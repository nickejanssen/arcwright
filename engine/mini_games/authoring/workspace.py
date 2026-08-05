"""Source-preserving local workspace for browser mini-game authoring."""

from __future__ import annotations

import os
import shutil
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid4

from engine.mini_games.authoring.models import (
    ArtifactVersionRef,
    MiniGameOnboardingRequest,
    MiniGameOnboardingSession,
    ReadinessState,
)

_METADATA_PREFIX = "session-v"
_METADATA_SUFFIX = ".json"


class LocalAuthoringWorkspace:
    """Own private imports and versioned metadata under an explicit root."""

    def create(
        self,
        request: MiniGameOnboardingRequest,
        root: Path,
    ) -> MiniGameOnboardingSession:
        root = root.resolve()
        source_path = self._static_source_path(request)
        if source_path is not None:
            self._validate_workspace_location(root, source_path)
            self._validate_source_tree(source_path)
            source_fingerprint = _sha256_tree(source_path)
        else:
            source_fingerprint = (
                request.source.source_sha256
                or sha256(request.source.source_ref.encode()).hexdigest()
            )

        session_id = uuid4()
        session_dir = self._session_dir(session_id, root)
        if session_dir.exists():
            raise FileExistsError(f"authoring session already exists: {session_id}")
        session_dir.mkdir(parents=True)

        private_source_ref: str | None = None
        if source_path is not None:
            private_source = session_dir / "source"
            shutil.copytree(source_path, private_source)
            private_source_ref = private_source.relative_to(root).as_posix()

        session = MiniGameOnboardingSession(
            session_id=session_id,
            request=request,
            state=ReadinessState.imported,
            source_fingerprint=source_fingerprint,
            private_source_ref=private_source_ref,
        )
        self.save(session, root)
        return session

    def load(self, session_id: UUID, root: Path) -> MiniGameOnboardingSession:
        root = root.resolve()
        session_dir = self._session_dir(session_id, root)
        if not session_dir.is_dir():
            raise FileNotFoundError(f"authoring session not found: {session_id}")

        versions = self._metadata_versions(session_dir)
        if not versions:
            raise FileNotFoundError(
                f"authoring session metadata not found: {session_id}"
            )
        return MiniGameOnboardingSession.model_validate_json(versions[-1].read_text())

    def save(self, session: MiniGameOnboardingSession, root: Path) -> None:
        root = root.resolve()
        session_dir = self._session_dir(session.session_id, root)
        if not session_dir.is_dir():
            raise FileNotFoundError(
                f"authoring session directory not found: {session.session_id}"
            )

        versions = self._metadata_versions(session_dir)
        if versions:
            existing = MiniGameOnboardingSession.model_validate_json(
                versions[-1].read_text()
            )
            if session.revision != existing.revision + 1:
                raise FileExistsError(
                    "authoring session revisions must be appended without overwrite"
                )
            self._validate_confirmed_artifacts(existing, session)
        elif session.revision != 1:
            raise ValueError("the first authoring session revision must be 1")

        destination = session_dir / self._metadata_name(session.revision)
        if destination.exists():
            raise FileExistsError(
                f"authoring metadata already exists: {destination.name}"
            )
        temporary = session_dir / f".{destination.name}.{uuid4().hex}.tmp"
        try:
            temporary.write_text(session.model_dump_json(indent=2))
            os.replace(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def _static_source_path(request: MiniGameOnboardingRequest) -> Path | None:
        if request.source.source_type != "static_bundle":
            return None
        source = Path(request.source.source_ref).resolve(strict=True)
        if not source.is_dir():
            raise ValueError("static bundle source_ref must identify a directory")
        return source

    @staticmethod
    def _validate_workspace_location(root: Path, source: Path) -> None:
        if root == source or root.is_relative_to(source):
            raise ValueError("authoring workspace cannot be inside imported source")

    @staticmethod
    def _validate_source_tree(source: Path) -> None:
        for path in source.rglob("*"):
            if path.is_symlink() and not path.resolve().is_relative_to(source):
                raise ValueError(f"imported source symlink escapes source root: {path}")

    @staticmethod
    def _session_dir(session_id: UUID, root: Path) -> Path:
        session_dir = (root / str(session_id)).resolve()
        if not session_dir.is_relative_to(root):
            raise ValueError("authoring session path escapes workspace root")
        return session_dir

    @staticmethod
    def _metadata_name(revision: int) -> str:
        return f"{_METADATA_PREFIX}{revision:06d}{_METADATA_SUFFIX}"

    @staticmethod
    def _metadata_versions(session_dir: Path) -> list[Path]:
        return sorted(session_dir.glob(f"{_METADATA_PREFIX}*{_METADATA_SUFFIX}"))

    @staticmethod
    def _validate_confirmed_artifacts(
        existing: MiniGameOnboardingSession,
        replacement: MiniGameOnboardingSession,
    ) -> None:
        artifact_fields = ("proposed_package", "proposed_adaptation")
        for field_name in artifact_fields:
            previous: ArtifactVersionRef | None = getattr(existing, field_name)
            if previous is not None and getattr(replacement, field_name) != previous:
                raise ValueError(
                    f"confirmed artifact cannot be overwritten: {field_name}"
                )
        if (
            existing.permission_receipt is not None
            and replacement.permission_receipt != existing.permission_receipt
        ):
            raise ValueError(
                "confirmed artifact cannot be overwritten: permission_receipt"
            )


def _sha256_tree(root: Path) -> str:
    digest = sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()
