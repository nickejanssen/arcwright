import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "guard_kb_agents", ROOT / "scripts" / "hooks" / "guard_kb_agents.py"
)
assert spec is not None and spec.loader is not None
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

SEARCH = "python scripts/team_ai_cli.py search"


def event(tool, agent="safety-sme", **tool_input):
    value = {"tool_name": tool, "tool_input": tool_input, "cwd": str(ROOT)}
    if agent is not None:
        value["agent_type"] = agent
    return value


def allowed(tool, agent="safety-sme", **tool_input):
    return guard.verdict(event(tool, agent, **tool_input)) is None


def test_knows_each_agent_and_its_namespaces():
    agents = guard.kb_agents()
    assert agents["safety-sme"] == {"safety"}
    assert agents["product-roadmap-sme"] == {"product-roadmap"}


def test_main_session_and_other_agents_are_untouched():
    assert allowed("Read", agent=None, file_path="engine/session/service.py")
    assert allowed("Bash", agent="reviewer", command="git log")


def test_reads_its_own_documents_and_index_lock():
    assert allowed("Read", file_path="docs/architecture/10-content-safety.md")
    assert allowed(
        "Read", file_path=str(ROOT / "docs/architecture/10-content-safety.md")
    )
    assert allowed("Read", file_path="team-ai/index.lock")


def test_cannot_read_outside_the_kb_or_its_own_namespace():
    assert not allowed("Read", file_path="team-ai/evals/live-probes.yaml")
    assert not allowed("Read", file_path="engine/session/service.py")
    assert not allowed("Read", file_path="docs/../engine/session/service.py")
    # Another specialist's document, and an excluded archive document.
    assert not allowed("Read", file_path="docs/architecture/06-model-routing.md")
    assert not allowed(
        "Read", file_path="docs/archive/nightcap-story-bibles/nightcap-couch-race.md"
    )


def test_search_lists_files_across_the_kb_but_content_only_from_its_own():
    assert allowed("Grep", pattern="namespace: safety", path="docs")
    assert allowed("Glob", pattern="**/*.md", path="docs/architecture")
    assert not allowed("Grep", pattern="namespace: safety")
    assert not allowed("Glob", pattern="**/*.yaml", path="team-ai")
    assert not allowed("Grep", pattern="Couch", path="docs/archive")
    assert not allowed("Grep", pattern="L1", path="docs", output_mode="content")
    assert allowed(
        "Grep",
        pattern="L1",
        path="docs/architecture/10-content-safety.md",
        output_mode="content",
    )


def test_bash_only_for_the_search_command_in_its_own_namespace():
    agent = "product-roadmap-sme"
    ok = f'{SEARCH} "open tasks" --root team-ai --namespace product-roadmap --k 8'
    assert allowed("Bash", agent, command=ok)
    assert allowed("Bash", agent, command=f'cd "{ROOT}" && {ok}')
    assert not allowed("Bash", agent, command=f'{SEARCH} "safety" --root team-ai --k 8')
    assert not allowed(
        "Bash", agent, command=f'{SEARCH} "x" --root team-ai --namespace nightcap --k 8'
    )
    assert not allowed(
        "Bash",
        agent,
        command=f'{SEARCH} "x" --root elsewhere --namespace product-roadmap',
    )
    assert not allowed("Bash", agent, command=ok + " && git log")
    assert not allowed("Bash", agent, command=f'cd "{ROOT / "engine"}" && {ok}')
    assert not allowed(
        "Bash", agent, command="python scripts/roadmap_status.py --milestone M5"
    )
    assert not allowed("Bash", agent, command=ok.replace("python ", "python3 "))


def test_refusal_names_the_exact_command_and_rules_out_a_missing_interpreter():
    reason = guard.verdict(
        event("Bash", "nightcap-sme", command="python3 scripts/x.py")
    )
    assert "Python is available" in reason
    assert "--root team-ai --namespace nightcap --k 8" in reason


def test_a_trailing_stderr_redirect_is_accepted_but_nothing_else_is():
    agent = "nightcap-sme"
    ok = f'{SEARCH} "players" --root team-ai --namespace nightcap --k 8'
    assert allowed("Bash", agent, command=ok + " 2>&1")
    assert not allowed("Bash", agent, command=ok + " 2>&1 | head")
    assert not allowed("Bash", agent, command=ok + " > out.txt")
