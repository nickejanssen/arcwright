"""Fail when a provider or model name appears outside the two permitted files.

AGENTS.md confines provider and model names to config/routing_table.json and
engine/routing/router.py. The rule is commercial: names confined to two files
make switching providers a settings edit rather than a codebase hunt.

Test files are out of scope by design. A test of the router's environment
mapping must name the real variable to prove the mapping; importing the name
from the router would make the test pass whatever the router did.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SCAN_DIRS = ("engine", "api", "sdk", "dashboard", "config")
SCAN_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".yaml", ".yml"}

PERMITTED = {
    Path("config/routing_table.json"),
    Path("engine/routing/router.py"),
}

SKIP_DIR_PARTS = {"node_modules", "__pycache__", ".venv", "dist", "build", "tests"}

PATTERN = re.compile(
    r"\b(?:anthropic|groq|openai|cohere|mistral|bedrock|vertex|sonnet|haiku|opus)\b"
    r"|(?<![A-Za-z0-9])(?:claude-|gpt-|llama-|gemini-)",
    re.IGNORECASE,
)


def is_test_path(path: Path) -> bool:
    name = path.name
    return (
        name.startswith("test_")
        or name.endswith("_test.py")
        or ".test." in name
        or ".spec." in name
    )


def scan() -> list[str]:
    findings: list[str] = []
    for directory in SCAN_DIRS:
        base = ROOT / directory
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
                continue
            if SKIP_DIR_PARTS & set(path.parts):
                continue
            if is_test_path(path):
                continue
            rel = path.relative_to(ROOT)
            if rel in PERMITTED:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for number, line in enumerate(text.splitlines(), start=1):
                if PATTERN.search(line):
                    findings.append(f"{rel.as_posix()}:{number}: {line.strip()}")
    return findings


def main() -> int:
    findings = scan()
    if findings:
        print("provider-leak-check: provider or model name outside the permitted files")
        for finding in findings:
            print(f"  {finding}")
        print("\nPermitted: config/routing_table.json, engine/routing/router.py")
        return 1
    print("provider-leak-check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
