"""Contract tests for the milestone artifact verifier.

This script gates milestone completion claims in CI
(see .github/workflows/verify-tasks.yml). A verifier that cannot fail would let
a milestone be marked done against an empty tree, so each test below removes
exactly one artifact and asserts the matching check goes red.

The synthetic tree is built from the artifacts the script names, then broken one
at a time; `repo_root` is redirected so none of this touches the real checkout.
"""

import pytest

from scripts import verify_tasks


def write(root, path, text=""):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


@pytest.fixture
def tree(monkeypatch, tmp_path):
    """A tree where every M1, M2 and M3 check passes."""
    monkeypatch.setattr(verify_tasks, "repo_root", lambda: str(tmp_path))

    for path in ("pyproject.toml", "Makefile", "engine/__init__.py", "api/__init__.py"):
        write(tmp_path, path)
    for directory in (
        "tests/arc",
        "tests/knowledge_graph",
        "tests/routing",
        "tests/safety",
    ):
        (tmp_path / directory).mkdir(parents=True)

    write(tmp_path, "alembic.ini")
    write(tmp_path, "migrations/versions/0001_initial.py")
    write(tmp_path, "migrations/versions/0002_knowledge.py")

    write(
        tmp_path,
        "engine/db/orm.py",
        "class GenerationLog:\n    pass\n\nclass Event:\n    content_text = None\n",
    )
    write(
        tmp_path,
        "engine/knowledge/graph.py",
        "def assert_knowledge():\n    pass\n\ndef get_character_knowledge():\n    pass\n",
    )
    write(tmp_path, "engine/routing/router.py", "def resolve_model_key():\n    pass\n")
    write(tmp_path, "engine/harness/runner.py", "KILLER_ASSIGNMENT_KEY = 'k'\n")
    write(tmp_path, "engine/harness/replay.py")
    write(tmp_path, "engine/harness/batch.py")

    write(tmp_path, "engine/arc/arc_definition.py")
    write(tmp_path, "nightcap/arc.json", "{}")
    write(tmp_path, "api/routers/sessions.py")
    write(
        tmp_path,
        "docs/architecture/11-telemetry.md",
        "## Five MVP Telemetry Signals\n",
    )
    return tmp_path


class TestHelpers:
    def test_contains_is_false_for_a_file_that_does_not_exist(self, tree):
        assert verify_tasks.contains("engine/nope.py", "anything") is False

    def test_contains_finds_a_token_in_an_existing_file(self, tree):
        assert verify_tasks.contains("engine/db/orm.py", "class GenerationLog") is True

    def test_file_exists_resolves_against_the_repo_root(self, tree):
        assert verify_tasks.file_exists("alembic.ini") is True
        assert verify_tasks.file_exists("absent.ini") is False


class TestM1Checks:
    def test_all_m1_checks_pass_on_a_complete_tree(self, tree):
        assert verify_tasks.run_checks("M1") == 0

    def test_aw_101_names_the_missing_scaffold_path(self, tree):
        (tree / "tests/routing").rmdir()
        ok, message = verify_tasks.check_aw_101()
        assert ok is False
        assert "tests/routing" in message

    def test_aw_102_104_rejects_a_missing_alembic_config(self, tree):
        (tree / "alembic.ini").unlink()
        assert verify_tasks.check_aw_102_104() == (False, "alembic.ini missing")

    def test_aw_102_104_rejects_a_versions_dir_without_both_migrations(self, tree):
        """Migration 0002 carries the knowledge graph tables. A tree with only
        0001 boots but has no knowledge state, which is the non-negotiable."""
        (tree / "migrations/versions/0002_knowledge.py").unlink()
        ok, message = verify_tasks.check_aw_102_104()
        assert ok is False
        assert "0001/0002" in message

    def test_aw_102_104_rejects_a_missing_versions_directory(self, tree):
        (tree / "migrations/versions/0001_initial.py").unlink()
        (tree / "migrations/versions/0002_knowledge.py").unlink()
        (tree / "migrations/versions").rmdir()
        assert verify_tasks.check_aw_102_104() == (
            False,
            "migrations/versions missing",
        )

    def test_aw_103_rejects_an_orm_without_the_generation_log_model(self, tree):
        write(tree, "engine/db/orm.py", "class Session:\n    pass\n")
        ok, message = verify_tasks.check_aw_103()
        assert ok is False
        assert "GenerationLog" in message

    def test_aw_105_106_names_each_missing_knowledge_function(self, tree):
        write(tree, "engine/knowledge/graph.py", "def assert_knowledge():\n    pass\n")
        ok, message = verify_tasks.check_aw_105_106()
        assert ok is False
        assert "def get_character_knowledge" in message
        assert "def assert_knowledge" not in message

    def test_aw_107_108_rejects_a_router_without_resolve_model_key(self, tree):
        """resolve_model_key is the abstraction rule 8 requires every model call
        to pass through."""
        write(tree, "engine/routing/router.py", "MODEL = 'hardcoded'\n")
        ok, message = verify_tasks.check_aw_107_108()
        assert ok is False
        assert "resolve_model_key" in message

    def test_aw_110_111_112_names_the_missing_harness_modules(self, tree):
        (tree / "engine/harness/replay.py").unlink()
        ok, message = verify_tasks.check_aw_110_111_112()
        assert ok is False
        assert "replay.py" in message


class TestMilestoneRuns:
    def test_a_broken_artifact_makes_the_m1_run_exit_two(self, tree, capsys):
        (tree / "engine/harness/batch.py").unlink()
        assert verify_tasks.run_checks("M1") == 2
        out = capsys.readouterr().out
        assert "AW-110/111/112: FAIL" in out
        assert "AW-103: OK" in out

    def test_m2_passes_and_fails_on_the_canonical_arc(self, tree):
        assert verify_tasks.run_checks("M2") == 0
        (tree / "nightcap/arc.json").unlink()
        assert verify_tasks.run_checks("M2") == 2

    def test_m2_accepts_either_arc_definition_module_name(self, tree):
        (tree / "engine/arc/arc_definition.py").unlink()
        assert verify_tasks.run_checks("M2") == 2
        write(tree, "engine/arc/models.py")
        assert verify_tasks.run_checks("M2") == 0

    def test_m3_passes_and_fails_on_the_content_event_model(self, tree):
        assert verify_tasks.run_checks("M3") == 0
        write(tree, "engine/db/orm.py", "class GenerationLog:\n    pass\n")
        assert verify_tasks.run_checks("M3") == 2

    def test_m3_fails_when_api_routers_has_no_python_modules(self, tree):
        (tree / "api/routers/sessions.py").unlink()
        assert verify_tasks.run_checks("M3") == 2

    def test_an_unknown_milestone_is_not_reported_as_a_pass(self, tree, capsys):
        """Exit 1 rather than 0: 'no checks defined' must never read as
        'milestone verified'."""
        assert verify_tasks.run_checks("M9") == 1
        assert "No automated checks defined" in capsys.readouterr().out


class TestAgainstTheRealRepository:
    def test_m1_verification_passes_on_this_checkout(self):
        """This is exactly what CI runs in verify-tasks.yml. If it goes red,
        the milestone claim it guards is no longer true."""
        assert verify_tasks.run_checks("M1") == 0
