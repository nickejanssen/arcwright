import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "checks" / "implemented_by_check.py"
spec = importlib.util.spec_from_file_location("implemented_by_check", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def tree(tmp_path, doc_line):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "mod.py").write_text(
        "class Service:\n    async def advance(self):\n        pass\n\ndef helper():\n    pass\n",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "arch.md").write_text(f"## 1 Thing\n\n{doc_line}\n", encoding="utf-8")
    return docs


def test_the_repository_references_resolve():
    checked, problems = module.check()
    assert problems == []
    assert checked > 0


def test_resolves_a_method_and_a_function(tmp_path):
    docs = tree(
        tmp_path,
        "**Implemented by:** `pkg/mod.py::Service.advance`, `pkg/mod.py::helper`.",
    )
    assert module.check(docs, tmp_path) == (2, [])


def test_fails_on_a_renamed_symbol(tmp_path):
    docs = tree(tmp_path, "**Implemented by:** `pkg/mod.py::Service.coordinate`.")
    _, problems = module.check(docs, tmp_path)
    assert problems == ["docs/arch.md: pkg/mod.py defines no Service.coordinate"]


def test_fails_on_a_missing_file(tmp_path):
    docs = tree(tmp_path, "**Implemented by:** `pkg/gone.py::helper`.")
    _, problems = module.check(docs, tmp_path)
    assert problems == ["docs/arch.md: pkg/gone.py does not exist"]


def test_fails_on_a_line_with_no_reference(tmp_path):
    docs = tree(tmp_path, "**Implemented by:** the session service.")
    _, problems = module.check(docs, tmp_path)
    assert "names no `file.py::Symbol` or path" in problems[0]


def test_accepts_a_document_path_that_exists(tmp_path):
    docs = tree(tmp_path, "**Implemented by:** `docs/arch.md`")
    assert module.check(docs, tmp_path) == (1, [])


def test_fails_on_a_document_path_that_does_not_exist(tmp_path):
    docs = tree(tmp_path, "**Implemented by:** `docs/specs/9999-gone.md`")
    _, problems = module.check(docs, tmp_path)
    assert problems == ["docs/arch.md: docs/specs/9999-gone.md does not exist"]
