from scripts.roadmap_status import milestone_edits, milestone_id, reconcile, render


def task(aw, milestone="M5", number=None, title="A task"):
    value = {"id": aw, "title": title, "milestone": milestone}
    if number is not None:
        value["github"] = {"issue_number": number}
    return value


def issue(number, title, state="OPEN", milestone="M5: Hardening"):
    return {
        "number": number,
        "title": title,
        "state": state,
        "milestone": {"title": milestone} if milestone else None,
    }


def test_status_comes_from_github_not_markdown():
    # The task file may still say Planned; the issue is what decides.
    report = reconcile(
        {"tasks": [task("AW-272", number=204)]},
        [issue(204, "AW-272: Continuity eval", state="CLOSED")],
    )
    assert report.tasks[0].state == "closed"
    assert report.tasks[0].problems == []


def test_falls_back_to_the_title_prefix_when_index_records_no_number():
    report = reconcile({"tasks": [task("AW-105")]}, [issue(9, "AW-105: Setup")])
    found = report.tasks[0]
    assert found.issue == 9
    assert "found #9 by title prefix" in found.problems[0]


def test_reports_a_task_with_no_issue():
    report = reconcile({"tasks": [task("AW-288")]}, [])
    assert report.tasks[0].state is None
    assert report.tasks[0].problems == ["no GitHub issue"]


def test_markdown_milestone_wins_and_mismatch_is_reported():
    report = reconcile(
        {"tasks": [task("AW-277", milestone="M5", number=227)]},
        [issue(227, "AW-277: Narrator dialogue", milestone=None)],
    )
    assert report.tasks[0].problems == ["GitHub milestone none, markdown says M5"]


def test_lists_github_work_the_roadmap_index_does_not_know():
    # index.json is a closed world: it cannot list work created outside it.
    report = reconcile(
        {"tasks": [task("AW-272", number=204)]},
        [
            issue(204, "AW-272: Continuity eval"),
            issue(137, "Harden session resume"),
            issue(
                134, "AW-248: Knowledge graph bridge", state="CLOSED", milestone=None
            ),
            issue(500, "Unrelated chore", milestone=None),
        ],
    )
    assert {i["number"] for i in report.untracked_issues} == {137, 134}


def test_flags_an_issue_titled_for_a_different_task():
    report = reconcile(
        {"tasks": [task("AW-274", number=220)]},
        [issue(220, "AW-275: Something else")],
    )
    assert "issue #220 is titled AW-275" in report.tasks[0].problems


def test_flags_duplicate_title_prefixes():
    report = reconcile({"tasks": []}, [issue(1, "AW-300: a"), issue(2, "AW-300: b")])
    assert report.problems == ["AW-300 is the title prefix of several issues: #1, #2"]


def test_milestone_id_reads_the_prefix_before_the_colon():
    assert milestone_id("M5: Hardening + Proof Prerequisites") == "M5"
    assert milestone_id(None) is None


def test_render_counts_from_github_state():
    report = reconcile(
        {"tasks": [task("AW-1", number=1), task("AW-2", number=2), task("AW-3")]},
        [issue(1, "AW-1: a", state="CLOSED"), issue(2, "AW-2: b")],
    )
    text = render(report, "M5")
    assert "M5: 3 tasks in markdown - 1 closed, 1 open, 1 with no issue" in text


def test_epic_issues_recorded_in_the_index_are_not_untracked():
    report = reconcile(
        {"tasks": [], "epics": [{"id": "M5-A", "github": {"issue_number": 48}}]},
        [
            issue(48, "[Epic] M5-A: Safety"),
            issue(201, "M5-H: Narrative Fidelity Layer"),
        ],
    )
    assert [i["number"] for i in report.untracked_issues] == [201]


def test_never_edits_the_milestone_of_an_issue_titled_for_another_task():
    report = reconcile(
        {"tasks": [task("AW-274", milestone="M5", number=220)]},
        [issue(220, "AW-275: Something else", milestone=None)],
    )
    assert report.tasks[0].trusted is False
    assert milestone_edits(report, None) == []


def test_reports_epic_issue_state_and_corrects_its_milestone():
    report = reconcile(
        {
            "tasks": [],
            "epics": [
                {
                    "id": "M5-I",
                    "title": "Couch Race",
                    "milestone": "M5",
                    "github": {"issue_number": 234},
                }
            ],
        },
        [issue(234, "M5-I Epic: Couch Race", milestone=None)],
    )
    assert report.epics[0].state == "open"
    assert [e.id for e in milestone_edits(report, "M5")] == ["M5-I"]


def test_milestone_state_comes_from_github():
    report = reconcile(
        {
            "tasks": [task("AW-1", number=1)],
            "milestones": [{"id": "M5", "title": "Hardening"}],
        },
        [issue(1, "AW-1: a")],
        [
            {
                "title": "M5: Hardening",
                "state": "open",
                "open_issues": 21,
                "closed_issues": 19,
            }
        ],
    )
    assert report.milestones == [
        {
            "id": "M5",
            "title": "Hardening",
            "state": "open",
            "open_issues": 21,
            "closed_issues": 19,
        }
    ]
    assert "M5 on GitHub: milestone open, 21 open and 19 closed issues" in render(
        report, "M5"
    )
