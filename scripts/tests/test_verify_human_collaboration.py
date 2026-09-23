"""Contract tests for the human-collaboration contract verifier.

This script is a CI gate (see .github/workflows/verify-tasks.yml). Its value is
entirely in what it refuses to let through: a doc that lost its required
section, a task file whose interaction profile was dropped, and above all an
AGENTS.md that drifted away from its Copilot mirror. Those are the cases below.

The tests point the verifier at a synthetic tree so they assert its logic rather
than the current state of the repo's docs.
"""

import pytest

from scripts import verify_human_collaboration as vhc

GUIDE = vhc.GUIDE_HEADING


@pytest.fixture
def tree(monkeypatch, tmp_path):
    monkeypatch.setattr(vhc, "ROOT", tmp_path)
    return tmp_path


def write(root, path, text):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


class TestCheckRequirements:
    def test_a_missing_file_is_reported_by_path(self, tree):
        failures = vhc.check_requirements({"docs/absent.md": ("token",)})
        assert failures == ["missing file: docs/absent.md"]

    def test_a_present_file_missing_its_token_is_reported(self, tree):
        """The real regression: the file survives a refactor but the section
        heading that carries the contract is quietly renamed away."""
        write(tree, "docs/agents/planner.md", "# Planner\n\nNo contract section.\n")
        failures = vhc.check_requirements(
            {"docs/agents/planner.md": ("Human Collaboration",)}
        )
        assert failures == [
            "docs/agents/planner.md: missing token 'Human Collaboration'"
        ]

    def test_every_missing_token_in_a_file_is_reported(self, tree):
        write(tree, "docs/a.md", "## Interaction Profiles\n")
        failures = vhc.check_requirements(
            {"docs/a.md": ("## Interaction Profiles", "## Approval Semantics")}
        )
        assert len(failures) == 1
        assert "## Approval Semantics" in failures[0]

    def test_a_satisfied_requirement_produces_no_failures(self, tree):
        write(tree, "docs/a.md", "## Interaction Profiles\n## Approval Semantics\n")
        assert (
            vhc.check_requirements(
                {"docs/a.md": ("## Interaction Profiles", "## Approval Semantics")}
            )
            == []
        )


class TestCheckMirror:
    """AGENTS.md and .github/copilot-instructions.md must stay identical from
    the Agent Operating Guide heading down. Copilot review reads only the
    mirror, so drift means Copilot enforces stale rules."""

    def test_identical_bodies_pass_despite_different_preambles(self, tree):
        body = f"{GUIDE}\n\nRule one.\nRule two.\n"
        write(tree, "AGENTS.md", "> canonical file preamble\n\n" + body)
        write(tree, ".github/copilot-instructions.md", "<!-- mirror -->\n\n" + body)
        assert vhc.check_mirror() == []

    def test_a_rule_added_to_agents_md_only_is_caught(self, tree):
        write(tree, "AGENTS.md", f"{GUIDE}\n\nRule one.\nRule two.\n")
        write(tree, ".github/copilot-instructions.md", f"{GUIDE}\n\nRule one.\n")
        assert vhc.check_mirror() == ["AGENTS.md and Copilot instruction bodies differ"]

    def test_a_missing_guide_heading_is_caught(self, tree):
        write(tree, "AGENTS.md", f"{GUIDE}\n\nRule one.\n")
        write(tree, ".github/copilot-instructions.md", "Rule one.\n")
        assert vhc.check_mirror() == [
            "instruction mirror is missing the Agent Operating Guide heading"
        ]


class TestInstructionBody:
    def test_drops_everything_above_the_guide_heading(self):
        text = f"preamble that may differ\n{GUIDE}\nshared rules\n"
        assert vhc.instruction_body(text) == f"{GUIDE}\nshared rules\n"

    def test_returns_empty_when_the_heading_is_absent(self):
        assert vhc.instruction_body("no heading here\n") == ""


class TestRun:
    def build_passing_tree(self, tree, extra_global=None, extra_retrofit=None):
        for path, tokens in vhc.GLOBAL_REQUIREMENTS.items():
            write(tree, path, "\n".join(tokens) + "\n")
        for path, tokens in vhc.RETROFIT_REQUIREMENTS.items():
            write(tree, path, "\n".join(tokens) + "\n")
        body = f"{GUIDE}\n\n## Human Collaboration Contract\n"
        write(tree, "AGENTS.md", body)
        write(tree, ".github/copilot-instructions.md", body)
        if extra_global:
            write(tree, *extra_global)
        if extra_retrofit:
            write(tree, *extra_retrofit)

    def test_a_complete_tree_passes_with_exit_zero(self, tree, capsys):
        self.build_passing_tree(tree)
        assert vhc.run("all") == 0
        assert "verification passed" in capsys.readouterr().out

    def test_a_broken_global_doc_exits_two(self, tree, capsys):
        self.build_passing_tree(tree)
        write(tree, "docs/agents/scribe.md", "# Scribe\n")
        assert vhc.run("global") == 2
        assert "docs/agents/scribe.md: missing token" in capsys.readouterr().out

    def test_a_broken_retrofit_task_exits_two(self, tree, capsys):
        self.build_passing_tree(tree)
        write(
            tree,
            "docs/roadmap/tasks/AW-273-rehearsal-1-execution.md",
            "# AW-273\n\nNo interaction profile line.\n",
        )
        assert vhc.run("retrofit") == 2
        assert "AW-273" in capsys.readouterr().out

    def test_the_global_phase_does_not_check_retrofit_files(self, tree):
        """Phase separation is the contract: the global gate runs on every PR
        and must not fail on a retrofit file that is still being backfilled."""
        self.build_passing_tree(tree)
        (tree / "docs/roadmap/tasks/AW-273-rehearsal-1-execution.md").unlink()
        assert vhc.run("global") == 0
        assert vhc.run("all") == 2

    def test_the_retrofit_phase_does_not_check_the_mirror(self, tree):
        self.build_passing_tree(tree)
        write(tree, ".github/copilot-instructions.md", f"{GUIDE}\n\ndrifted\n")
        assert vhc.run("retrofit") == 0
        assert vhc.run("global") == 2


class TestRequirementTablesMatchTheRepo:
    """The tables above are only useful if they name files that exist. This is
    the one test that reads the real tree, and it is what fails when a doc is
    moved or renamed without updating the verifier."""

    def test_every_required_path_exists_in_the_repository(self):
        missing = [
            path
            for path in (*vhc.GLOBAL_REQUIREMENTS, *vhc.RETROFIT_REQUIREMENTS)
            if not (vhc.ROOT / path).exists()
        ]
        assert missing == []
