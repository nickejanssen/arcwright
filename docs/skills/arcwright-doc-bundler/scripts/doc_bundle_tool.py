"""Build and validate Arcwright documentation bundle scaffolds."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


SKIPPED_DIR_PARTS = {
    ".agents",
    ".claude",
    ".codex",
    ".cursor",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".vscode",
    "docs-bundles",
    "node_modules",
    "__pycache__",
}

ALLOWED_SUFFIXES = {".csv", ".json", ".md", ".toml", ".txt", ".yaml", ".yml"}

STALE_PATH_PATTERNS = [
    r"07-Story-Bible-Murder-Mystery",
    r"09-Story-Bible-Monster",
    r"docs[\\/]+07-",
    r"docs[\\/]+09-",
]

SECRET_PATTERNS = [
    r"(^|[^A-Za-z0-9])sk-[A-Za-z0-9_-]{16,}",
    r"(?i)api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9_-]{8,}",
    r"(?i)secret\s*[:=]\s*['\"]?[A-Za-z0-9_-]{8,}",
    r"(?i)token\s*[:=]\s*['\"]?[A-Za-z0-9_-]{8,}",
]

MODEL_PATTERNS = [
    r"(?i)\b(model|provider)\s*[:=]\s*['\"][^'\"]+['\"]",
]

CANONICAL_REMINDER = "Return to canonical repo docs before implementation."


@dataclass(frozen=True)
class BundleMode:
    name: str
    output: str
    title: str
    purpose: str
    include_globs: tuple[str, ...]


MODES: dict[str, BundleMode] = {
    "product": BundleMode(
        name="product",
        output="bundle-A-product-strategy.md",
        title="Bundle A: Product Strategy",
        purpose="Product, business, roadmap, scope, and decision context for AI agents.",
        include_globs=(
            "AGENTS.md",
            "docs/README.md",
            "docs/prd/*.md",
            "docs/product/*.md",
            "docs/product/*.csv",
            "docs/roadmap/00-overview.md",
            "docs/roadmap/index.json",
            "docs/roadmap/milestones/*.md",
            "docs/decisions/*.md",
        ),
    ),
    "architecture": BundleMode(
        name="architecture",
        output="bundle-B-architecture-specs.md",
        title="Bundle B: Architecture And Specs",
        purpose="Architecture, specs, ADRs, conventions, and implementation contracts for AI agents.",
        include_globs=(
            "AGENTS.md",
            "docs/README.md",
            "docs/architecture/*.md",
            "docs/specs/*.md",
            "docs/decisions/*.md",
            "docs/conventions/*.md",
            "docs/skills/*/SKILL.md",
            "docs/skills/*/references/*.md",
        ),
    ),
    "narrative": BundleMode(
        name="narrative",
        output="bundle-C-narrative.md",
        title="Bundle C: Narrative",
        purpose="Story bible, Nightcap, Monster RPG, and narrative scope context for AI agents.",
        include_globs=(
            "AGENTS.md",
            "docs/README.md",
            "docs/story-bibles/*.md",
            "docs/prd/03-scope.md",
            "docs/product/decisions-log.csv",
            "docs/product/open-questions-log.csv",
            "docs/decisions/0006-nightcap-continuity-v11.md",
        ),
    ),
    "live-code": BundleMode(
        name="live-code",
        output="live-code-state.md",
        title="Live Code State",
        purpose="Current branch, repo health, known blockers, tests, and implementation state.",
        include_globs=(
            "AGENTS.md",
            "docs/README.md",
            "docs/roadmap/index.json",
            "docs/roadmap/milestones/M1-deterministic-platform-core.md",
            "docs/specs/*.md",
            "docs/decisions/*.md",
            "docs/architecture/supplemental-schemas.md",
            "docs/architecture/15-development-guide.md",
        ),
    ),
}


PERSONAS: dict[str, BundleMode] = {
    "product-lead": BundleMode(
        name="persona",
        output="persona-product-lead.md",
        title="Persona Bundle: Product Lead",
        purpose="Context for a product leadership lens focused on strategy, portfolio, scope, roadmap, and proof signals.",
        include_globs=(
            "AGENTS.md",
            "docs/README.md",
            "docs/agents/expert-personas.md",
            "docs/prd/*.md",
            "docs/product/*.md",
            "docs/product/*.csv",
            "docs/roadmap/00-overview.md",
            "docs/roadmap/index.json",
            "docs/roadmap/milestones/*.md",
            "docs/decisions/*.md",
            "docs/story-bibles/README.md",
        ),
    ),
    "storyteller": BundleMode(
        name="persona",
        output="persona-storyteller.md",
        title="Persona Bundle: Storyteller",
        purpose="Context for a narrative craft lens focused on story quality, Nightcap, Monster RPG, and narrative engine affordances.",
        include_globs=(
            "AGENTS.md",
            "docs/README.md",
            "docs/agents/expert-personas.md",
            "docs/story-bibles/*.md",
            "docs/prd/01-overview.md",
            "docs/prd/02-requirements.md",
            "docs/prd/03-scope.md",
            "docs/architecture/03-arc-execution.md",
            "docs/architecture/04-knowledge-graph.md",
            "docs/architecture/07-character-behavior.md",
            "docs/product/decisions-log.csv",
            "docs/product/open-questions-log.csv",
            "docs/decisions/0006-nightcap-continuity-v11.md",
        ),
    ),
    "developer-stakeholder": BundleMode(
        name="persona",
        output="persona-developer-stakeholder.md",
        title="Persona Bundle: Developer Stakeholder",
        purpose="Context for a customer engineer or design-partner lens focused on API, SDK, integrations, reliability, and adoption friction.",
        include_globs=(
            "AGENTS.md",
            "docs/README.md",
            "docs/agents/expert-personas.md",
            "docs/prd/01-overview.md",
            "docs/prd/03-scope.md",
            "docs/architecture/08-event-system.md",
            "docs/architecture/09-developer-api.md",
            "docs/architecture/15-development-guide.md",
            "docs/specs/*api*.md",
            "docs/specs/*sdk*.md",
            "docs/specs/*event*.md",
            "docs/roadmap/index.json",
            "docs/roadmap/tasks/AW-217-*.md",
            "docs/roadmap/tasks/AW-218-*.md",
            "docs/roadmap/tasks/AW-219-*.md",
            "docs/roadmap/tasks/AW-225-*.md",
        ),
    ),
    "engineering-architecture": BundleMode(
        name="persona",
        output="persona-engineering-architecture.md",
        title="Persona Bundle: Engineering Architecture",
        purpose="Context for a CTO or principal architect lens focused on determinism, cost, architecture, ADRs, specs, and live blockers.",
        include_globs=(
            "AGENTS.md",
            "docs/README.md",
            "docs/agents/expert-personas.md",
            "docs/architecture/*.md",
            "docs/specs/*.md",
            "docs/decisions/*.md",
            "docs/conventions/*.md",
            "docs/roadmap/index.json",
            "docs/roadmap/milestones/M1-deterministic-platform-core.md",
        ),
    ),
    "business-ceo-advisor": BundleMode(
        name="persona",
        output="persona-business-ceo-advisor.md",
        title="Persona Bundle: Business CEO Advisor",
        purpose="Context for a founder, CEO, investor, or business-advisor lens focused on strategy, GTM, value locus, wedge, and proof gates.",
        include_globs=(
            "AGENTS.md",
            "docs/README.md",
            "docs/agents/expert-personas.md",
            "docs/prd/*.md",
            "docs/product/*.md",
            "docs/product/*.csv",
            "docs/architecture/12-build-plan.md",
            "docs/architecture/13-cost-model.md",
            "docs/roadmap/00-overview.md",
            "docs/roadmap/index.json",
            "docs/roadmap/milestones/*.md",
            "docs/decisions/*.md",
            "docs/story-bibles/README.md",
        ),
    ),
}

PERSONA_ALIASES = {
    "advisor": "business-ceo-advisor",
    "architect": "engineering-architecture",
    "architecture": "engineering-architecture",
    "business": "business-ceo-advisor",
    "ceo": "business-ceo-advisor",
    "cto": "engineering-architecture",
    "customer-engineer": "developer-stakeholder",
    "developer": "developer-stakeholder",
    "devrel": "developer-stakeholder",
    "engineering": "engineering-architecture",
    "investor": "business-ceo-advisor",
    "narrative": "storyteller",
    "product": "product-lead",
    "story": "storyteller",
}


def repo_root_from(start: Path) -> Path:
    current = start.resolve()
    for path in (current, *current.parents):
        if (path / "AGENTS.md").exists() and (path / "docs" / "README.md").exists():
            return path
    raise SystemExit("Could not find repo root with AGENTS.md and docs/README.md")


def run_git(root: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"
    return result.stdout.strip() or "unavailable"


def rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def display_path(path: Path, root: Path) -> str:
    try:
        return rel(path, root)
    except ValueError:
        return path.resolve().as_posix()


def is_allowed(path: Path, root: Path) -> bool:
    relative = path.resolve().relative_to(root.resolve())
    parts = set(relative.parts)
    if parts & SKIPPED_DIR_PARTS:
        return False
    if "archive" in relative.parts and "notion-export" in relative.parts:
        return False
    return path.is_file() and path.suffix.lower() in ALLOWED_SUFFIXES


def collect_files(root: Path, patterns: tuple[str, ...]) -> list[Path]:
    seen: set[Path] = set()
    files: list[Path] = []
    for pattern in patterns:
        matches = sorted(root.glob(pattern))
        for path in matches:
            if path in seen or not is_allowed(path, root):
                continue
            seen.add(path)
            files.append(path)
    return files


def custom_patterns(task_goal: str) -> tuple[str, ...]:
    goal = task_goal.lower()
    patterns = ["AGENTS.md", "docs/README.md", "docs/roadmap/index.json"]
    keyword_map = {
        "api": ["docs/architecture/09-developer-api.md", "docs/specs/*api*.md"],
        "arc": ["docs/architecture/03-arc-execution.md", "docs/specs/*arc*.md"],
        "character": ["docs/architecture/07-character-behavior.md", "docs/specs/*character*.md"],
        "cost": ["docs/architecture/13-cost-model.md", "docs/conventions/ai-cost-policy.md"],
        "event": ["docs/architecture/08-event-system.md", "docs/specs/*event*.md"],
        "knowledge": ["docs/architecture/04-knowledge-graph.md", "docs/specs/*knowledge*.md"],
        "migration": ["docs/architecture/supplemental-schemas.md", "docs/specs/*migration*.md"],
        "nightcap": ["docs/story-bibles/nightcap-murder-mystery.md", "docs/specs/*nightcap*.md"],
        "routing": ["docs/architecture/06-model-routing.md", "docs/specs/*routing*.md"],
        "safety": ["docs/architecture/10-content-safety.md", "docs/specs/*safety*.md"],
        "schema": ["docs/architecture/supplemental-schemas.md", "docs/specs/*schema*.md"],
        "telemetry": ["docs/architecture/11-telemetry.md", "docs/specs/*telemetry*.md"],
    }
    for keyword, additions in keyword_map.items():
        if keyword in goal:
            patterns.extend(additions)
    patterns.extend(["docs/product/decisions-log.csv", "docs/product/open-questions-log.csv"])
    return tuple(dict.fromkeys(patterns))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def redact(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS + MODEL_PATTERNS:
        redacted = re.sub(pattern, "[redacted]", redacted, flags=re.IGNORECASE)
    return redacted


def summary_cues(path: Path, root: Path, max_lines: int = 10) -> list[str]:
    text = read_text(path)
    lines: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith(">") or stripped.startswith("**Status**"):
            lines.append(redact(stripped))
        if len(lines) >= max_lines:
            break
    if not lines:
        lines.append("No Markdown headings or metadata found. Review source directly if needed.")
    return [f"- `{rel(path, root)}`: {line}" for line in lines]


def live_code_notes(root: Path) -> list[str]:
    status = run_git(root, ["status", "--short", "--branch"])
    branch = run_git(root, ["branch", "--show-current"])
    return [
        f"- Current branch: `{branch}`",
        "- Current git status:",
        "```text",
        status,
        "```",
        "- Run the repo-relevant checks for the task and replace this note with exact commands and outcomes.",
        "- If CI is available through the host platform, summarize current failing or passing checks with links.",
    ]


def write_bundle(root: Path, mode: BundleMode, files: list[Path], output_dir: Path, task_goal: str | None, token_budget: int | None) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / mode.output
    generated = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    commit = run_git(root, ["rev-parse", "HEAD"])
    lines = [
        f"# {mode.title}",
        "",
        f"Generated: {generated}",
        f"Source git commit: `{commit}`",
        "",
        "Source-of-truth warning: This bundle is generated context, not canonical documentation. Return to canonical repo docs before implementation.",
        "",
        "## Purpose And Intended AI Use",
        "",
        mode.purpose,
    ]
    if task_goal:
        lines.extend(["", f"Task goal: {task_goal}"])
    if token_budget:
        lines.extend(["", f"Requested token budget: {token_budget}"])
    lines.extend(
        [
            "",
            "## Manifest",
            "",
            *[f"- `{rel(path, root)}`" for path in files],
            "",
            "## Compact Summaries With Citations",
            "",
            "Use these summary cues as a starting point. Tighten them into task-specific synthesis when an agent is preparing a final handoff bundle.",
            "",
        ]
    )
    for path in files:
        lines.extend([f"### `{rel(path, root)}`", "", *summary_cues(path, root), ""])
    if mode.name == "live-code":
        lines.extend(["## Current Code State", "", *live_code_notes(root), ""])
    lines.extend(
        [
            "## Open Questions And Unresolved Risks",
            "",
            "- Review `docs/product/open-questions-log.csv` for product questions before treating any unresolved item as decided.",
            "- Regenerate this bundle after documentation or code changes. Stale bundles recreate stale context risk.",
            "- Product-scope commitments require durable evidence in `docs/product/decisions-log.csv` plus an ADR or approved spec when applicable.",
            "",
            "## Explicit Exclusions",
            "",
            "- `docs/archive/notion-export/` skipped by default.",
            "- `docs-bundles/` skipped because generated bundles are not source of truth.",
            "- Local agent state directories skipped, including `.claude/`, `.codex/`, `.cursor/`, `.vscode/`, and `.agents/`.",
            "- Binary files, images, caches, and dependency folders skipped.",
            "",
            "## Validation",
            "",
            "- Confirm manifest paths are canonical current docs or required root instructions.",
            "- Confirm no stale root Notion export paths or stale story bible filenames appear.",
            "- Confirm no concrete provider or model strings, secret values, or local agent files are included.",
            f"- {CANONICAL_REMINDER}",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def build(args: argparse.Namespace) -> int:
    root = repo_root_from(Path(args.repo_root or Path.cwd()))
    output_dir = root / args.output_dir
    modes = list(MODES.values()) if args.mode == "all" else [mode_from_args(args)]
    written: list[Path] = []
    for mode in modes:
        files = collect_files(root, mode.include_globs)
        path = write_bundle(root, mode, files, output_dir, args.task_goal, args.token_budget)
        written.append(path)
    for path in written:
        print(display_path(path, root))
    return 0


def mode_from_args(args: argparse.Namespace) -> BundleMode:
    if args.mode == "persona":
        if not args.persona:
            raise SystemExit("persona mode requires --persona")
        persona_key = normalize_persona(args.persona)
        mode = PERSONAS[persona_key]
        if args.output:
            return BundleMode(
                name=mode.name,
                output=args.output,
                title=mode.title,
                purpose=mode.purpose,
                include_globs=mode.include_globs,
            )
        return mode
    if args.mode == "custom":
        if not args.task_goal:
            raise SystemExit("custom mode requires --task-goal")
        budget = args.token_budget or "unspecified"
        return BundleMode(
            name="custom",
            output=args.output or "custom-task-brief.md",
            title="Custom Task Brief",
            purpose=f"Smallest relevant canonical context for a custom task with token budget {budget}.",
            include_globs=custom_patterns(args.task_goal),
        )
    return MODES[args.mode]


def normalize_persona(persona: str) -> str:
    key = persona.strip().lower().replace("_", "-").replace(" ", "-")
    key = PERSONA_ALIASES.get(key, key)
    if key not in PERSONAS:
        valid = ", ".join(sorted(PERSONAS))
        raise SystemExit(f"unknown persona '{persona}'. Valid personas: {valid}")
    return key


def extract_manifest_paths(text: str) -> list[str]:
    in_manifest = False
    paths: list[str] = []
    for line in text.splitlines():
        if line.strip() == "## Manifest":
            in_manifest = True
            continue
        if in_manifest and line.startswith("## "):
            break
        if in_manifest:
            match = re.search(r"`([^`]+)`", line)
            if match:
                paths.append(match.group(1))
    return paths


def validate_file(path: Path) -> list[str]:
    text = read_text(path)
    issues: list[str] = []
    manifest_paths = extract_manifest_paths(text)
    if "Generated:" not in text:
        issues.append("missing generated date")
    if "Source git commit:" not in text:
        issues.append("missing source git commit")
    if CANONICAL_REMINDER not in text:
        issues.append("missing canonical docs reminder")
    for pattern in STALE_PATH_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            issues.append(f"stale or archived path pattern found: {pattern}")
    for manifest_path in manifest_paths:
        lowered = manifest_path.lower()
        if "docs/archive/notion-export" in lowered:
            issues.append(f"archive path in manifest: {manifest_path}")
        if lowered.startswith("docs-bundles/") or lowered.startswith(".agents/"):
            issues.append(f"generated or local agent path in manifest: {manifest_path}")
        if any(lowered.startswith(f"{part}/") for part in [".claude", ".codex", ".cursor", ".vscode"]):
            issues.append(f"local agent path in manifest: {manifest_path}")
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, text):
            issues.append(f"secret-looking value found: {pattern}")
    for pattern in MODEL_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            issues.append(f"provider or model string found: {pattern}")
    return issues


def validate(args: argparse.Namespace) -> int:
    any_issues = False
    for raw in args.paths:
        path = Path(raw)
        if not path.exists():
            print(f"{raw}: missing")
            any_issues = True
            continue
        issues = validate_file(path)
        if issues:
            any_issues = True
            print(f"{raw}: FAIL")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"{raw}: OK")
    return 1 if any_issues else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build bundle scaffold")
    build_parser.add_argument("--mode", choices=[*MODES.keys(), "all", "custom", "persona"], required=True)
    build_parser.add_argument("--repo-root")
    build_parser.add_argument("--output-dir", default="docs-bundles")
    build_parser.add_argument("--output", help="Output filename for custom or persona mode")
    build_parser.add_argument("--persona", help="Persona slug or alias for persona mode")
    build_parser.add_argument("--task-goal")
    build_parser.add_argument("--token-budget", type=int)
    build_parser.set_defaults(func=build)

    validate_parser = subparsers.add_parser("validate", help="Validate generated bundles")
    validate_parser.add_argument("paths", nargs="+")
    validate_parser.set_defaults(func=validate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
