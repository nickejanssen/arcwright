"""Require a knowledge-state query before every AI character generation.

AGENTS.md: "Knowledge state queries are mandatory before every AI character
generation (non-negotiable)."

Four call sites in engine/ generate text outside the routing module. Only the
two passing task_type="character_dialogue" produce character speech;
narrative_generation (mini-game resolution) and narrator_bridge (narration) are
not characters and must not be caught by this rule.

The check walks the AST rather than matching text, so a call split across lines
or renamed via keyword order is still seen.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "engine"

GUARDED_TASK_TYPE = "character_dialogue"
GENERATE_NAMES = {"generate", "route_generation"}
KNOWLEDGE_QUERY = "build_character_generation_context"
SKIP_DIR_PARTS = {"__pycache__", "tests"}


def call_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def is_guarded_generation(node: ast.Call) -> bool:
    if call_name(node) not in GENERATE_NAMES:
        return False
    for keyword in node.keywords:
        if keyword.arg == "task_type" and isinstance(keyword.value, ast.Constant):
            return keyword.value.value == GUARDED_TASK_TYPE
    return False


def direct_call(statement: ast.stmt) -> ast.Call | None:
    value: ast.AST | None = None
    if isinstance(statement, ast.Expr):
        value = statement.value
    elif isinstance(statement, (ast.Assign, ast.AnnAssign, ast.Return)):
        value = statement.value
    if isinstance(value, (ast.Await, ast.YieldFrom)):
        value = value.value
    return value if isinstance(value, ast.Call) else None


def check_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int | None:
    """Require context and generation calls as unconditional direct statements."""
    context_seen = False
    for statement in node.body:
        call = direct_call(statement)
        if call is None:
            continue
        if call_name(call) == KNOWLEDGE_QUERY:
            context_seen = True
        elif is_guarded_generation(call) and not context_seen:
            return call.lineno
    return None


def scan() -> list[str]:
    problems: list[str] = []
    for path in sorted(ENGINE.rglob("*.py")):
        if SKIP_DIR_PARTS & set(path.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                line = check_function(node)
                if line is not None:
                    problems.append(
                        f"{rel}:{line}: {node.name}() generates character dialogue "
                        f"without calling {KNOWLEDGE_QUERY}() first"
                    )
    return problems


def main() -> int:
    problems = scan()
    if problems:
        print("knowledge-query-guard: failed")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("knowledge-query-guard: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
