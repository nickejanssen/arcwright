import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "guard_kb_agents", ROOT / "scripts" / "hooks" / "guard_kb_agents.py"
)
assert spec is not None and spec.loader is not None
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

AGENT = "safety-sme"


def event(tool, agent=AGENT, **tool_input):
    value = {"tool_name": tool, "tool_input": tool_input, "cwd": str(ROOT)}
    if agent is not None:
        value["agent_type"] = agent
    return value


def test_knows_the_emitted_agents():
    assert AGENT in guard.kb_agents()


def test_main_session_and_other_agents_are_untouched():
    assert (
        guard.verdict(event("Read", agent=None, file_path="engine/session/service.py"))
        is None
    )
    assert guard.verdict(event("Bash", agent="reviewer", command="git log")) is None


def test_reads_inside_the_kb_root_and_index_lock():
    assert (
        guard.verdict(event("Read", file_path="docs/architecture/10-content-safety.md"))
        is None
    )
    assert (
        guard.verdict(event("Read", file_path=str(ROOT / "docs" / "README.md"))) is None
    )
    assert guard.verdict(event("Read", file_path="team-ai/index.lock")) is None


def test_cannot_read_the_answer_key_or_code():
    assert guard.verdict(event("Read", file_path="team-ai/evals/live-probes.yaml"))
    assert guard.verdict(event("Read", file_path="engine/session/service.py"))
    assert guard.verdict(event("Read", file_path="docs/../engine/session/service.py"))


def test_search_must_name_a_path_inside_the_kb_root():
    assert (
        guard.verdict(event("Grep", pattern="namespace: safety", path="docs")) is None
    )
    assert guard.verdict(event("Grep", pattern="namespace: safety"))
    assert guard.verdict(event("Glob", pattern="**/*.yaml", path="team-ai"))


def test_bash_only_for_the_search_command_alone():
    ok = 'python scripts/team_ai_cli.py search "safety layers" --root team-ai --namespace safety --k 8'
    assert guard.verdict(event("Bash", command=ok)) is None
    assert guard.verdict(
        event("Bash", command="python scripts/roadmap_status.py --milestone M5")
    )
    assert guard.verdict(event("Bash", command=ok + " && git log"))
    assert guard.verdict(event("Bash", command="git log --oneline"))
