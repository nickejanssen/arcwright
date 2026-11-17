import os
import subprocess
import sys
from pathlib import Path

from scripts import team_ai_cli

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "team_ai_cli.py"


def test_local_cli_is_preferred_over_sibling_checkout(tmp_path, monkeypatch):
    checkout = tmp_path / "arcwright"
    local = checkout / "team-ai" / "runtime" / "dist" / "cli.js"
    sibling = tmp_path / "team-ai" / "dist" / "cli.js"
    for path in (local, sibling):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    monkeypatch.delenv("TEAM_AI_CLI", raising=False)
    monkeypatch.setattr(
        team_ai_cli, "__file__", str(checkout / "scripts" / "team_ai_cli.py")
    )
    monkeypatch.setattr(team_ai_cli, "_main_checkout", lambda: checkout)
    assert team_ai_cli.find_cli() == local


def test_override_is_preferred_over_local_cli(tmp_path, monkeypatch):
    checkout = tmp_path / "arcwright"
    local = checkout / "team-ai" / "runtime" / "dist" / "cli.js"
    local.parent.mkdir(parents=True)
    local.write_text("", encoding="utf-8")
    override = tmp_path / "override.js"
    override.write_text("", encoding="utf-8")
    monkeypatch.setenv("TEAM_AI_CLI", str(override))
    monkeypatch.setattr(
        team_ai_cli, "__file__", str(checkout / "scripts" / "team_ai_cli.py")
    )
    assert team_ai_cli.find_cli() == override


def test_linked_worktree_cannot_override_main_checkout_runtime(tmp_path, monkeypatch):
    main = tmp_path / "main"
    worktree = tmp_path / "worktree"
    trusted = main / "team-ai" / "runtime" / "dist" / "cli.js"
    untrusted = worktree / "team-ai" / "runtime" / "dist" / "cli.js"
    for path in (trusted, untrusted):
        path.parent.mkdir(parents=True)
        path.write_text("", encoding="utf-8")
    monkeypatch.delenv("TEAM_AI_CLI", raising=False)
    monkeypatch.setattr(
        team_ai_cli, "__file__", str(worktree / "scripts" / "team_ai_cli.py")
    )
    monkeypatch.setattr(team_ai_cli, "_main_checkout", lambda: main)
    assert team_ai_cli.find_cli() == trusted
    trusted.unlink()
    assert team_ai_cli.find_cli() is None


def test_unresolved_linked_worktree_does_not_trust_its_local_runtime(
    tmp_path, monkeypatch
):
    worktree = tmp_path / "worktree"
    local = worktree / "team-ai" / "runtime" / "dist" / "cli.js"
    local.parent.mkdir(parents=True)
    local.write_text("", encoding="utf-8")
    (worktree / ".git").write_text("gitdir: missing", encoding="utf-8")
    monkeypatch.delenv("TEAM_AI_CLI", raising=False)
    monkeypatch.setattr(
        team_ai_cli, "__file__", str(worktree / "scripts" / "team_ai_cli.py")
    )
    monkeypatch.setattr(team_ai_cli, "_main_checkout", lambda: None)
    assert team_ai_cli.find_cli() is None


def test_resolves_from_this_checkout():
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--path"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert out.returncode == 0, out.stderr
    assert Path(out.stdout.strip()).exists()


def test_env_override_wins(tmp_path):
    fake = tmp_path / "cli.js"
    fake.write_text("", encoding="utf-8")
    env = {**os.environ, "TEAM_AI_CLI": str(fake)}
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--path"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=env,
    )
    assert out.stdout.strip() == str(fake)


def test_missing_cli_exits_nonzero_without_raising(tmp_path):
    env = {**os.environ, "TEAM_AI_CLI": str(tmp_path / "absent.js")}
    out = subprocess.run(
        [sys.executable, str(SCRIPT), "--path"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=env,
    )
    assert out.returncode != 0
    assert "Traceback" not in out.stderr


def test_wrapper_ignores_modules_in_its_worktree_scripts_directory(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    wrapper = scripts / SCRIPT.name
    wrapper.write_bytes(SCRIPT.read_bytes())
    (scripts / "subprocess.py").write_text(
        'raise RuntimeError("worktree module executed")\n', encoding="utf-8"
    )
    out = subprocess.run(
        [sys.executable, str(wrapper), "--path"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, out.stderr
    assert Path(out.stdout.strip()).exists()


def kb_instance(tmp_path):
    instance = tmp_path / "team-ai"
    instance.mkdir()
    (instance / "index.lock").write_bytes(
        (ROOT / "team-ai" / "index.lock").read_bytes()
    )
    docs = tmp_path / "docs"
    docs.mkdir()
    return instance, docs


def write_kb_doc(docs, name, namespace, body):
    (docs / f"{name}.md").write_text(
        f"---\nid: {namespace}.{name}\nnamespace: {namespace}\ntitle: Retrieval fixture\n"
        "owner: test\nstatus: active\nreview_by: '2027-01-01'\n"
        "sensitivity: internal\nsource: authored\ntags: []\nsupersedes: []\n---\n"
        f"# Retrieval fixture\n\n{body}\n",
        encoding="utf-8",
    )


def test_search_explains_plain_search_fallback_until_the_index_is_built(tmp_path):
    instance, docs = kb_instance(tmp_path)
    write_kb_doc(docs, "worktree-proof", "safety", "Quicksilver is a known test term.")
    base = [sys.executable, str(SCRIPT)]
    root = ["--root", str(instance)]
    search = [*base, "search", "quicksilver", *root, "--namespace", "safety", "--json"]
    missing = subprocess.run(
        search, cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    assert missing.returncode != 0
    assert "index not built" in missing.stderr
    assert "Use plain search" in missing.stderr
    assert not (instance / ".team-ai" / "index.sqlite").exists()

    built = subprocess.run(
        [*base, "reindex", *root],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert built.returncode == 0, built.stderr
    ranked = subprocess.run(
        search, cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    assert ranked.returncode == 0, ranked.stderr
    assert "worktree-proof.md" in ranked.stdout
    assert "Use plain search" not in ranked.stderr


def test_specialist_search_returns_owned_hits_when_other_namespaces_dominate(tmp_path):
    instance, docs = kb_instance(tmp_path)
    for index in range(40):
        write_kb_doc(docs, f"noise-{index}", "strategy", "reconstruction " * 12)
    for index in range(10):
        write_kb_doc(
            docs, f"owned-{index}", "safety", "reconstruction and its safeguards"
        )
    for index in range(70):
        write_kb_doc(
            docs, f"filler-{index}", "strategy", "Scoring and session controls."
        )

    base = [sys.executable, str(SCRIPT)]
    root = ["--root", str(instance)]
    built = subprocess.run(
        [*base, "reindex", *root], cwd=ROOT, capture_output=True, text=True
    )
    assert built.returncode == 0, built.stderr
    result = subprocess.run(
        [*base, "search", "reconstruction", *root, "--namespace", "safety", "--k", "8"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    hits = result.stdout.splitlines()
    assert len(hits) == 8
    assert all("owned-" in hit for hit in hits)
