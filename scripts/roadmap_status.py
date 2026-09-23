"""Live roadmap status: markdown scope joined to GitHub state.

D-109: GitHub is authoritative for whether a task is open or closed; the roadmap
markdown is authoritative for what a task is and which milestone it belongs to.
This joins the two and reports every place they disagree, so nobody has to read
a stale status line or correlate titles by hand.

Tasks and epics map to issues through `github.issue_number` in
docs/roadmap/index.json, a task falling back to an issue titled `AW-NNN:` when it
records no number. Milestone state comes from GitHub's milestones.

    python scripts/roadmap_status.py                 # every milestone
    python scripts/roadmap_status.py --milestone M5  # one milestone
    python scripts/roadmap_status.py --json
    python scripts/roadmap_status.py --apply-milestones   # edits GitHub

`--apply-milestones` sets each mismatched task or epic issue's GitHub milestone to
the one the markdown records, skipping any issue titled for a different task. It
changes GitHub, so it runs only when asked.
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
    # False when the recorded issue is titled for a different task: the mapping
    # is suspect, so nothing is written to GitHub on its strength.
    trusted: bool = True


@dataclass
class Report:
    tasks: list[TaskStatus]
    untracked_issues: list[dict]
    problems: list[str]
    epics: list[TaskStatus] = field(default_factory=list)
    milestones: list[dict] = field(default_factory=list)


def milestone_id(title: str | None) -> str | None:
    """GitHub milestone titles read `M5: Hardening + ...`; the id is before the colon."""
    if not title:
        return None
    return title.split(":", 1)[0].strip()


def _join(
    entry: dict,
    by_number: dict[int, dict],
    by_prefix: dict[str, list[dict]],
    mapped: set[int],
) -> TaskStatus:
    number = (entry.get("github") or {}).get("issue_number")
    status = TaskStatus(
        entry["id"], entry["title"], entry["milestone"], None, None, None
    )
    if number is None:
        candidates = by_prefix.get(entry["id"], [])
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
        return status

    mapped.add(issue["number"])
    status.issue = issue["number"]
    status.state = issue["state"].lower()
    status.github_milestone = milestone_id((issue.get("milestone") or {}).get("title"))
    prefix = AW_PREFIX.match(issue["title"])
    if prefix and prefix.group(1) != entry["id"]:
        status.trusted = False
        status.problems.append(f"issue #{issue['number']} is titled {prefix.group(1)}")
    if status.github_milestone != entry["milestone"]:
        status.problems.append(
            f"GitHub milestone {status.github_milestone or 'none'}, "
            f"markdown says {entry['milestone']}"
        )
    return status


def reconcile(
    index: dict, issues: list[dict], github_milestones: list[dict] | None = None
) -> Report:
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

    mapped: set[int] = set()
    tasks = [_join(task, by_number, by_prefix, mapped) for task in index["tasks"]]
    epics = [
        _join(epic, by_number, by_prefix, mapped)
        for epic in index.get("epics", [])
        if "title" in epic and "milestone" in epic
    ]
    # An epic's issue is known to the index even when its entry is incomplete.
    mapped |= {
        epic["github"]["issue_number"]
        for epic in index.get("epics", [])
        if (epic.get("github") or {}).get("issue_number")
    }
    by_id = {milestone_id(m["title"]): m for m in github_milestones or []}
    milestones = []
    for entry in index.get("milestones", []):
        found = by_id.get(entry["id"])
        milestones.append(
            {
                "id": entry["id"],
                "title": entry.get("title", ""),
                "state": found["state"] if found else None,
                "open_issues": found.get("open_issues") if found else None,
                "closed_issues": found.get("closed_issues") if found else None,
            }
        )
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
    return Report(tasks, untracked, problems, epics, milestones)


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


def fetch_milestones() -> list[dict]:
    result = subprocess.run(
        ["gh", "api", "repos/{owner}/{repo}/milestones?state=all&per_page=100"],
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
    )
    return json.loads(result.stdout)


def render(report: Report, milestone: str | None) -> str:
    lines: list[str] = []
    groups: dict[str, list[TaskStatus]] = {}
    for task in report.tasks:
        if milestone is None or task.milestone == milestone:
            groups.setdefault(task.milestone, []).append(task)
    states = {m["id"]: m for m in report.milestones}
    epics_by_milestone: dict[str, list[TaskStatus]] = {}
    for epic in report.epics:
        epics_by_milestone.setdefault(epic.milestone, []).append(epic)
    for name in sorted(groups):
        members = groups[name]
        github = states.get(name)
        if github and github["state"]:
            lines.append(
                f"{name} on GitHub: milestone {github['state']}, "
                f"{github['open_issues']} open and {github['closed_issues']} closed issues"
            )
        elif github:
            lines.append(f"{name} on GitHub: no milestone found")
        for epic in sorted(epics_by_milestone.get(name, []), key=lambda e: e.id):
            ref = f"#{epic.issue}" if epic.issue else "-"
            lines.append(
                f"  epic {epic.id:6} {ref:6} {epic.state or 'none':6}  {epic.title[:54]}"
            )
            for problem in epic.problems:
                lines.append(f"           ! {problem}")
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


def milestone_edits(report: Report, milestone: str | None) -> list[TaskStatus]:
    """Tasks and epics whose GitHub milestone should be set from the markdown."""
    edits = []
    for task in [*report.tasks, *report.epics]:
        if task.issue is None or task.github_milestone == task.milestone:
            continue
        if milestone is not None and task.milestone != milestone:
            continue
        if not task.trusted:
            print(f"skip {task.id}: #{task.issue} is titled for another task")
            continue
        edits.append(task)
    return edits


def apply_milestones(report: Report, milestone: str | None) -> int:
    titles = {
        milestone_id(m["title"]): m["title"]
        for m in fetch_milestones()
        if milestone_id(m["title"])
    }
    changed = 0
    for task in milestone_edits(report, milestone):
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
        milestones = fetch_milestones()
    except (OSError, subprocess.CalledProcessError) as error:
        print(
            f"roadmap-status: cannot read GitHub issues ({error}); is gh installed and "
            "authenticated?",
            file=sys.stderr,
        )
        return 2
    report = reconcile(index, issues, milestones)

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
