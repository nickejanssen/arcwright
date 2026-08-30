from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SKILL_NAMES = (
    "arcwright-playtest-steward",
    "arcwright-playtest-harness",
    "arcwright-playtest-research",
    "arcwright-playtest-publishing",
)

REQUIRED_SECTIONS = (
    "## When To Use",
    "## Operating Contract",
    "## Workflow",
    "## Evidence And Stop Conditions",
)

BANNED_MODEL_OR_PROVIDER_LITERALS = (
    "anthropic/",
    "groq/",
    "openai/",
    "claude-",
    "gpt-",
    "gemini-",
    "llama-",
    "mistral",
    "fireworks",
    "together ai",
    "litellm",
)


def read_skill(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_canonical_playtest_skills_have_platform_neutral_contracts():
    for skill_name in SKILL_NAMES:
        path = REPO_ROOT / "docs" / "skills" / skill_name / "SKILL.md"

        body = read_skill(path)
        lowered = body.lower()

        assert body.startswith("---\n")
        assert f"name: {skill_name}" in body
        assert "description:" in body
        for section in REQUIRED_SECTIONS:
            assert section in body
        assert "docs/README.md" in body
        assert "scripts/playtest_tool.py" in body
        assert "explicit approval" in lowered
        assert "evidence" in lowered
        assert "canonical" in lowered
        assert not any(
            literal in lowered for literal in BANNED_MODEL_OR_PROVIDER_LITERALS
        )


def test_playtest_steward_is_router_not_creative_author():
    body = read_skill(
        REPO_ROOT / "docs" / "skills" / "arcwright-playtest-steward" / "SKILL.md"
    ).lower()

    assert "organizer and router" in body
    assert "not an autonomous creative author" in body
    assert "reviewed commands" in body
    assert "metadata-only scaffold" in body


def test_agent_launchers_are_thin_and_point_to_canonical_skills():
    for skill_name in SKILL_NAMES:
        path = REPO_ROOT / ".agents" / "skills" / skill_name / "SKILL.md"

        body = read_skill(path)

        assert f"name: {skill_name}" in body
        assert f"docs/skills/{skill_name}/SKILL.md" in body
        assert "thin launcher" in body.lower()
        assert "## Workflow" not in body
        assert "## Operating Contract" not in body
        assert len(body.splitlines()) <= 12
