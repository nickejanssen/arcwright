import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CASES_DIR = REPO_ROOT / "evals" / "cases"
REPORTS_DIR = REPO_ROOT / "evals" / "reports"
REPORT_PATH = REPORTS_DIR / "routing_eval_report.json"


def load_case(case_name: str) -> dict:
    return json.loads((CASES_DIR / f"{case_name}.json").read_text())


def load_routing_table(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text())


def iter_repo_files() -> list[Path]:
    return [
        path
        for path in REPO_ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and "__pycache__" not in path.parts
        and "node_modules" not in path.parts
        and "dist" not in path.parts
        and path.suffix not in {".pyc"}
    ]


def write_report(results: list[dict]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "passed": sum(1 for result in results if result["passed"]),
        "failed": sum(1 for result in results if not result["passed"]),
        "results": results,
    }
    REPORT_PATH.write_text(json.dumps(summary, indent=2))


def evaluate_required_tasks_case() -> dict:
    case = load_case("routing_table_required_tasks")
    routing_table = load_routing_table(case["input"]["routing_table_path"])
    required_tasks = case["input"]["required_tasks"]

    missing_tasks = [task for task in required_tasks if task not in routing_table]
    missing_tiers = {
        task: [
            tier
            for tier in ("standard", "premium")
            if tier not in routing_table.get(task, {})
        ]
        for task in required_tasks
        if any(
            tier not in routing_table.get(task, {}) for tier in ("standard", "premium")
        )
    }

    passed = not missing_tasks and not missing_tiers
    return {
        "case_id": case["id"],
        "passed": passed,
        "details": {
            "missing_tasks": missing_tasks,
            "missing_tiers": missing_tiers,
        },
    }


def evaluate_provider_policy_case() -> dict:
    case = load_case("routing_table_provider_policy")
    routing_table = load_routing_table(case["input"]["routing_table_path"])
    allowed_prefixes = tuple(case["input"]["allowed_provider_prefixes"])

    invalid_entries = []
    empty_entries = []
    for task_type, tiers in routing_table.items():
        for tier_name, model_name in tiers.items():
            if not model_name:
                empty_entries.append({"task_type": task_type, "tier": tier_name})
                continue
            if not model_name.startswith(allowed_prefixes):
                invalid_entries.append(
                    {"task_type": task_type, "tier": tier_name, "model": model_name}
                )

    passed = not invalid_entries and not empty_entries
    return {
        "case_id": case["id"],
        "passed": passed,
        "details": {
            "invalid_entries": invalid_entries,
            "empty_entries": empty_entries,
        },
    }


def evaluate_fallback_case() -> dict:
    case = load_case("routing_table_fallbacks")
    routing_table = load_routing_table(case["input"]["routing_table_path"])

    missing_fallbacks = {
        task: [
            fallback_key
            for fallback_key in ("standard_fallback", "premium_fallback")
            if not routing_table.get(task, {}).get(fallback_key)
        ]
        for task in routing_table
        if any(
            not routing_table.get(task, {}).get(fallback_key)
            for fallback_key in ("standard_fallback", "premium_fallback")
        )
    }

    passed = not missing_fallbacks
    return {
        "case_id": case["id"],
        "passed": passed,
        "details": {
            "missing_fallbacks": missing_fallbacks,
        },
    }


def evaluate_no_hardcoded_models_case() -> dict:
    case = load_case("no_hardcoded_model_strings_outside_routing_layer")
    routing_table = load_routing_table(case["input"]["routing_table_path"])
    excluded_prefixes = tuple(case["input"]["exclude_paths"])
    include_roots = tuple(case["input"]["include_roots"])
    configured_models = {
        model_name
        for tiers in routing_table.values()
        for model_name in tiers.values()
        if model_name
    }

    matches = []
    for file_path in iter_repo_files():
        rel_path = file_path.relative_to(REPO_ROOT).as_posix()
        if not rel_path.startswith(include_roots):
            continue
        if rel_path.startswith(excluded_prefixes):
            continue
        try:
            contents = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for model_name in configured_models:
            if model_name in contents:
                matches.append({"path": rel_path, "model": model_name})

    passed = not matches
    return {
        "case_id": case["id"],
        "passed": passed,
        "details": {
            "matches": matches,
        },
    }


def run_routing_evals() -> list[dict]:
    results = [
        evaluate_required_tasks_case(),
        evaluate_provider_policy_case(),
        evaluate_fallback_case(),
        evaluate_no_hardcoded_models_case(),
    ]
    write_report(results)
    return results


def test_routing_eval_cases_pass() -> None:
    results = run_routing_evals()
    failed = [result for result in results if not result["passed"]]
    assert not failed, json.dumps(failed, indent=2)
