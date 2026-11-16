"""Check a written case from the command line.

    python -m engine.case.authored <case.json> --arc-id <arc id>

Prints the summary (rule names, pass or fail, counts only), which is safe to
read when the case must stay unspoiled. ``--full`` prints the author's report
with IDs, so only the case's author should use it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from engine.arc.registry import load_arc_definition
from engine.case.authored.loader import check_authored_case_file
from engine.case.authored.reports import full_report, summary_report
from engine.case.authored.rules import DEFAULT_CHOICE_BUDGET


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a written case.")
    parser.add_argument("case_file", type=Path)
    parser.add_argument("--arc-id", required=True)
    parser.add_argument("--budget", type=int, default=DEFAULT_CHOICE_BUDGET)
    parser.add_argument(
        "--full", action="store_true", help="author's report; prints case IDs"
    )
    args = parser.parse_args(argv)

    arc = load_arc_definition(args.arc_id)
    if arc is None:
        print(f"unknown arc id: {args.arc_id}", file=sys.stderr)
        return 2
    _, check = check_authored_case_file(
        args.case_file,
        beat_order=[beat.beat_id for beat in arc.beats],
        budget=args.budget,
    )
    print(full_report(check) if args.full else summary_report(check))
    return 0 if check.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
