"""Every `**Implemented by:**` reference in docs/ must name code that exists.

Architecture documents describe components in design vocabulary ("session
coordinator"); the code uses its own names (`advance_live_session_on_input`).
The Implemented-by lines bridge the two, so a reader searching the design's
words can find the implementation instead of concluding it is absent. A bridge
that points at a renamed or deleted symbol is worse than none, so this fails the
build when one does.

References take the form `path/to/file.py::Name` or `path/to/file.py::Class.method`.
A line may instead name a document, such as the spec that delivers a decision, as
a backticked repository path; that file must exist.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
LINE = re.compile(r"^\*\*Implemented by:\*\*(.*)$", re.M)
REFERENCE = re.compile(r"`([\w./-]+\.py)::([\w.]+)`")
PATH = re.compile(r"`([\w./-]+\.\w+)`")


def defines(path: Path, dotted: str) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    scope: list[ast.stmt] = tree.body
    parts = dotted.split(".")
    for depth, name in enumerate(parts):
        found = next(
            (
                node
                for node in scope
                if isinstance(
                    node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
                )
                and node.name == name
            ),
            None,
        )
        if found is None:
            return False
        if depth < len(parts) - 1:
            if not isinstance(found, ast.ClassDef):
                return False
            scope = found.body
    return True


def check(docs: Path = DOCS, root: Path = ROOT) -> tuple[int, list[str]]:
    checked = 0
    problems: list[str] = []
    for doc in sorted(docs.rglob("*.md")):
        text = doc.read_text(encoding="utf-8")
        for line in LINE.finditer(text):
            refs = REFERENCE.findall(line.group(1))
            paths = PATH.findall(line.group(1))
            rel = doc.relative_to(root).as_posix()
            if not refs and not paths:
                problems.append(
                    f"{rel}: Implemented-by line names no `file.py::Symbol` or path"
                )
            for path in paths:
                checked += 1
                if not (root / path).is_file():
                    problems.append(f"{rel}: {path} does not exist")
            for file, symbol in refs:
                checked += 1
                target = root / file
                if not target.is_file():
                    problems.append(f"{rel}: {file} does not exist")
                elif not defines(target, symbol):
                    problems.append(f"{rel}: {file} defines no {symbol}")
    return checked, problems


def main() -> int:
    checked, problems = check()
    for problem in problems:
        print(problem)
    if problems:
        print(f"implemented-by-check: {len(problems)} broken reference(s)")
        return 1
    print(f"implemented-by-check: OK ({checked} references)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
