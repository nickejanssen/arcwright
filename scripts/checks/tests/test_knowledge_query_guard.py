import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "checks" / "knowledge_query_guard.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT
    )


def test_passes_on_clean_tree():
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr


def test_does_not_flag_non_character_generation():
    result = run()
    assert "resolver.py" not in result.stdout
    assert "bridge.py" not in result.stdout


def test_flags_unguarded_character_generation():
    planted = ROOT / "engine" / "characters" / "_guard_probe.py"
    planted.write_text(
        "from engine.routing import generate\n\n"
        "async def speak(db, session_id):\n"
        "    return await generate(db, session_id=session_id, "
        'task_type="character_dialogue", messages=[])\n',
        encoding="utf-8",
    )
    try:
        result = run()
        assert result.returncode != 0
        assert "_guard_probe.py" in result.stdout
        assert "speak" in result.stdout
    finally:
        planted.unlink()


@pytest.mark.parametrize(
    "shape_name, shape",
    list(
        {
            "if": "    if True:\n        build_character_generation_context(db)\n",
            "try": "    try:\n        build_character_generation_context(db)\n    except Exception:\n        pass\n",
            "while": "    while False:\n        build_character_generation_context(db)\n",
            "for": "    for item in []:\n        build_character_generation_context(db)\n",
            "with": "    with lock:\n        build_character_generation_context(db)\n",
            "nested_function": "    def helper():\n        build_character_generation_context(db)\n",
        }.items()
    ),
)
def test_does_not_treat_non_dominating_context_as_a_guard(shape_name, shape):
    planted = ROOT / "engine" / "characters" / "_guard_probe.py"
    planted.write_text(
        "from engine.routing import generate\n"
        "from engine.characters.context import build_character_generation_context\n\n"
        "async def speak(db):\n"
        f"{shape}"
        '    return await generate(db, task_type="character_dialogue", messages=[])\n',
        encoding="utf-8",
    )
    try:
        result = run()
        assert result.returncode != 0
        assert "_guard_probe.py" in result.stdout
        assert "speak" in result.stdout
    finally:
        planted.unlink()
