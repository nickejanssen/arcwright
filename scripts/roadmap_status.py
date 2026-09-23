"""Live roadmap status: markdown scope joined to GitHub state.

D-109: GitHub is authoritative for whether a task is open or closed; the roadmap
markdown is authoritative for what a task is and which milestone it belongs to.
This joins the two and reports every place they disagree, so nobody has to read
a stale status line or correlate titles by hand.

Tasks map to issues through `github.issue_number` in docs/roadmap/index.json,
falling back to an issue titled `AW-NNN:` for a task that records no number.

    python scripts/roadmap_status.py                 # every milestone
    python scripts/roadmap_status.py --milestone M5  # one milestone
    python scripts/roadmap_status.py --json
    python scripts/roadmap_status.py --apply-milestones   # edits GitHub

`--apply-milestones` sets each mismatched issue's GitHub milestone to the one the
markdown records. It changes GitHub, so it runs only when asked.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "roadmap" / "index.json"
AW_PREFIX = re.compile(r"^(AW-\d+):")


@dataclass
class TaskStatus:
    id: str
    title: str
    milestone: str
    issue: int | None
    state: str | None
    github_milestone: str | None
    problems: list[str] = field(default_factory=list)


@dataclass
class Report:
    tasks: list[TaskStatus]
    untracked_issues: list[dict]
    problems: list[str]


def milestone_id(title: str | None) -> str | None:
    """GitHub milestone titles read `M5: Hardening + ...`; the id is before the colon."""
    if not title:
        return None
    return title.split(":", 1)[0].strip()


def reconcile(index: dict, issues: list[dict]) -> Report:
    by_number = {issue["number"]: issue for issue in issues}
    by_prefix: dict[str, list[dict]] = {}
    for issue in issues:
        match = AW_PREFIX.match(issue["title"])
        if match:
            by_prefix.setdefault(match.group(1), []).append(issue)

    problems = [
        f"{aw} is the title prefix of several issues: "
        + ", ".join(f"#{i['number']}" for i in found)
        for aw, found in sorted(by_prefix.items())
        if len(found) > 1
    ]

    tasks: list[TaskStatus] = []
    mapped: set[int] = set()
    for task in index["tasks"]:
        number = (task.get("github") or {}).get("issue_number")
        status = TaskStatus(
            task["id"], task["title"], task["milestone"], None, None, None
        )
        if number is None:
            candidates = by_prefix.get(task["id"], [])
            if len(candidates) == 1:
                number = candidates[0]["number"]
                status.problems.append(
                    f"index.json records no issue; found #{number} by title prefix"
                )
        issue = by_number.get(number) if number is not None else None
        if issue is None:
            status.problems.append(
                "no GitHub issue" if number is None else f"issue #{number} not found"
            )
            tasks.append(status)
            continue

        mapped.add(issue["number"])
        status.issue = issue["number"]
        status.state = issue["state"].lower()
        status.github_milestone = milestone_id(
            (issue.get("milestone") or {}).get("title")
        )
        prefix = AW_PREFIX.match(issue["title"])
        if prefix and prefix.group(1) != task["id"]:
            status.problems.append(
                f"issue #{issue['number']} is titled {prefix.group(1)}"
            )
        if status.github_milestone != task["milestone"]:
            status.problems.append(
                f"GitHub milestone {status.github_milestone or 'none'}, "
                f"markdown says {task['milestone']}"
            )
        tasks.append(status)

    # Epics are recorded in the index too; their issues are known, not untracked.
    mapped |= {
        epic["github"]["issue_number"]
        for epic in index.get("epics", [])
        if (epic.get("github") or {}).get("issue_number")
    }
    untracked = [
        {
            "number": issue["number"],
            "title": issue["title"],
            "state": issue["state"].lower(),
            "milestone": milestone_id((issue.get("milestone") or {}).get("title")),
        }
        for issue in issues
        if issue["number"] not in mapped
        and (
            AW_PREFIX.match(issue["title"])
            or (issue.get("milestone") or {}).get("title")
        )
    ]
    return Report(tasks, untracked, problems)


def fetch_issues() -> list[dict]:
    result = subprocess.run(
        [
            "gh",
            "issue",
            "list",
            "--state",
            "all",
            "--limit",
            "2000",
            "--json",
            "number,title,state,milestone",
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
    )
    return json.loads(result.stdout)


def fetch_milestone_titles() -> dict[str, str]:
    result = subprocess.run(
        ["gh", "api", "repos/{owner}/{repo}/milestones?state=all&per_page=100"],
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
    )
    titles = [m["title"] for m in json.loads(result.stdout)]
    return {milestone_id(title): title for title in titles if milestone_id(title)}


def render(report: Report, milestone: str | None) -> str:
    lines: list[str] = []
    groups: dict[str, list[TaskStatus]] = {}
    for task in report.tasks:
        if milestone is None or task.milestone == milestone:
            groups.setdefault(task.milestone, []).append(task)
    for name in sorted(groups):
        members = groups[name]
        closed = sum(1 for t in members if t.state == "closed")
        opened = sum(1 for t in members if t.state == "open")
        untracked = sum(1 for t in members if t.state is None)
        lines.append(
            f"{name}: {len(members)} tasks in markdown - {closed} closed, {opened} open"
            + (f", {untracked} with no issue" if untracked else "")
        )
        for task in sorted(members, key=lambda t: (t.state != "open", t.id)):
            ref = f"#{task.issue}" if task.issue else "-"
            lines.append(
                f"  {task.id:8} {ref:6} {task.state or 'none':6}  {task.title[:60]}"
            )
            for problem in task.problems:
                lines.append(f"           ! {problem}")
    extra = [
        i
        for i in report.untracked_issues
        if milestone is None or i["milestone"] == milestone
    ]
    if extra:
        lines.append("")
        lines.append("On GitHub but not in docs/roadmap/index.json:")
        for issue in extra:
            lines.append(
                f"  #{issue['number']:<5} {issue['state']:6} {issue['milestone'] or '-':4} "
                f"{issue['title'][:66]}"
            )
    for problem in report.problems:
        lines.append(f"! {problem}")
    return "\n".join(lines)


def apply_milestones(report: Report, milestone: str | None) -> int:
    titles = fetch_milestone_titles()
    changed = 0
    for task in report.tasks:
        if task.issue is None or task.github_milestone == task.milestone:
            continue
        if milestone is not None and task.milestone != milestone:
            continue
        title = titles.get(task.milestone)
        if title is None:
            print(f"skip {task.id}: no GitHub milestone for {task.milestone}")
            continue
        subprocess.run(
            ["gh", "issue", "edit", str(task.issue), "--milestone", title],
            check=True,
            cwd=ROOT,
            capture_output=True,
        )
        print(
            f"#{task.issue} {task.id}: milestone {task.github_milestone or 'none'} -> {title}"
        )
        changed += 1
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--milestone", help="limit to one milestone id, e.g. M5")
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    parser.add_argument(
        "--apply-milestones",
        action="store_true",
        help="set GitHub milestones from the markdown (changes GitHub)",
    )
    args = parser.parse_args(argv)

    index = json.loads(INDEX.read_text(encoding="utf-8"))
    try:
        issues = fetch_issues()
    except (OSError, subprocess.CalledProcessError) as error:
        print(
            f"roadmap-status: cannot read GitHub issues ({error}); is gh installed and "
            "authenticated?",
            file=sys.stderr,
        )
        return 2
    report = reconcile(index, issues)

    if args.apply_milestones:
        changed = apply_milestones(report, args.milestone)
        print(f"roadmap-status: {changed} milestone(s) updated")
        return 0
    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(render(report, args.milestone))
    return 0


if __name__ == "__main__":
    sys.exit(main())
