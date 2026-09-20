"""Verify that claimed approval evidence points at records that exist.

Two checks:

1. Reference integrity: every D-NNN and ADR-NNNN reference under docs/specs/
   and docs/roadmap/ resolves to a real record.
2. Declared evidence: specs and roadmap tasks added in this change set carry a
   `scope_evidence` front-matter field naming their approval record, or the
   literal `none` meaning the document claims no new product scope.

Detecting a scope claim is reading comprehension and out of reach for a
plain script; verifying a claimed citation is not, and catches the realistic
failure: an agent inventing a plausible decision id.

Two things this must get right, both found by building it:
  - Decision ids sit as a prefix inside the CSV's quoted `Decision` column, so
    the CSV must be parsed. A line-based grep falsely reports 10 failures,
    including the heavily-cited D-034.
  - Citations are inconsistently zero-padded (D-45 against D-045).
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DECISIONS_CSV = ROOT / "docs" / "product" / "decisions-log.csv"
ADR_DIR = ROOT / "docs" / "decisions"
SCAN_DIRS = (ROOT / "docs" / "specs", ROOT / "docs" / "roadmap")

DECISION_REF = re.compile(r"\bD-(\d+)\b")
ADR_REF = re.compile(r"\bADR[- ]?(\d{4})\b")
ADR_PATH_REF = re.compile(r"docs/decisions/(\d{4})-")
FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)
SCOPE_EVIDENCE = re.compile(r"^scope_evidence:\s*(.+?)\s*$", re.MULTILINE)


def normalise(number: str) -> str:
    return f"D-{int(number):03d}"


def known_decision_ids() -> set[str]:
    ids: set[str] = set()
    with DECISIONS_CSV.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            match = re.match(r"\s*D-(\d+)", row.get("Decision") or "")
            if match:
                ids.add(normalise(match.group(1)))
    return ids


def known_adr_ids() -> set[str]:
    return {path.name[:4] for path in ADR_DIR.glob("[0-9][0-9][0-9][0-9]-*.md")}


def markdown_files() -> list[Path]:
    files: list[Path] = []
    for directory in SCAN_DIRS:
        if directory.exists():
            files.extend(sorted(directory.rglob("*.md")))
    return files


def check_references() -> list[str]:
    decisions, adrs = known_decision_ids(), known_adr_ids()
    problems: list[str] = []
    for path in markdown_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT).as_posix()
        for number in DECISION_REF.findall(text):
            if normalise(number) not in decisions:
                problems.append(
                    f"{rel}: cites D-{number}, which is not in decisions-log.csv"
                )
        for number in set(ADR_REF.findall(text)) | set(ADR_PATH_REF.findall(text)):
            if number not in adrs:
                problems.append(
                    f"{rel}: cites ADR {number}, which has no file in docs/decisions/"
                )
    return problems


def added_files(base: str) -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=A", f"{base}...HEAD"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=True,
        ).stdout
    except subprocess.CalledProcessError:
        return []
    paths = []
    for line in out.splitlines():
        path = ROOT / line.strip()
        if path.suffix == ".md" and any(
            str(path).startswith(str(d)) for d in SCAN_DIRS
        ):
            paths.append(path)
    return paths


def check_declared_evidence(base: str) -> list[str]:
    decisions, adrs = known_decision_ids(), known_adr_ids()
    problems: list[str] = []
    for path in added_files(base):
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        front = FRONT_MATTER.search(text)
        field = SCOPE_EVIDENCE.search(front.group(1)) if front else None
        if field is None:
            problems.append(
                f"{rel}: new document has no `scope_evidence` field "
                f"(name the approving record, or `none` if it claims no new product scope)"
            )
            continue
        value = field.group(1).strip().strip("\"'")
        if value.lower() == "none":
            continue
        cited = False
        for number in DECISION_REF.findall(value):
            cited = True
            if normalise(number) not in decisions:
                problems.append(
                    f"{rel}: scope_evidence cites D-{number}, which does not exist"
                )
        for number in set(ADR_REF.findall(value)) | set(ADR_PATH_REF.findall(value)):
            cited = True
            if number not in adrs:
                problems.append(
                    f"{rel}: scope_evidence cites ADR {number}, which does not exist"
                )
        if not cited:
            problems.append(
                f"{rel}: scope_evidence names no D-NNN or ADR reference and is not `none`"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base", default=None, help="base ref for the added-files check"
    )
    parser.add_argument(
        "--explain", default=None, help="report whether one id resolves"
    )
    args = parser.parse_args()

    if args.explain:
        match = DECISION_REF.search(args.explain)
        if match:
            target = normalise(match.group(1))
            print(
                f"{args.explain} -> {target}: "
                f"{'resolved' if target in known_decision_ids() else 'NOT FOUND'}"
            )
            return 0
        print(f"{args.explain}: not a decision id")
        return 1

    problems = check_references()
    if args.base:
        problems += check_declared_evidence(args.base)

    if problems:
        print("scope-evidence-check: failed")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("scope-evidence-check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
