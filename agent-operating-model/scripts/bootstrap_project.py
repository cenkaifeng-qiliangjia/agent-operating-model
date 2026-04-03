#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

SKILL_NAME = "agent-operating-model"
TEMPLATES = ("feature", "debug", "review")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Bootstrap repo-local CLAW/Codex instructions and optionally install "
            "this skill into a target project."
        )
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Path to the target repository or project directory.",
    )
    parser.add_argument(
        "--template",
        default="feature",
        choices=TEMPLATES,
        help="Instruction overlay style to generate.",
    )
    parser.add_argument(
        "--instructions-file",
        default="CLAW.md",
        choices=["CLAW.md", ".claw/instructions.md"],
        help="Repo-local instruction file to create or update.",
    )
    parser.add_argument(
        "--check",
        dest="checks",
        action="append",
        default=[],
        help="Verification command to include in the generated instructions. Repeatable.",
    )
    parser.add_argument(
        "--no-detect-checks",
        action="store_true",
        help="Disable auto-detection when no explicit --check flags are provided.",
    )
    parser.add_argument(
        "--extra-rule",
        action="append",
        default=[],
        help="Additional repo rule to append to the generated instructions. Repeatable.",
    )
    parser.add_argument(
        "--install-skill",
        default="link",
        choices=["link", "copy", "skip"],
        help=(
            "How to place the skill into <repo>/.codex/skills. "
            "'link' keeps the project tied to this working copy."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite conflicting targets instead of stopping.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).expanduser().resolve()
    skill_root = Path(__file__).resolve().parents[1]

    if not repo.exists() or not repo.is_dir():
        raise SystemExit(f"Target repo does not exist or is not a directory: {repo}")

    if repo == skill_root:
        raise SystemExit("Target repo cannot be the skill repository itself.")

    checks, check_note = resolve_checks(
        repo=repo,
        explicit_checks=args.checks,
        allow_detection=not args.no_detect_checks,
    )

    results: list[str] = []
    results.append(
        install_skill_overlay(
            repo=repo,
            skill_root=skill_root,
            install_mode=args.install_skill,
            force=args.force,
        )
    )
    results.append(
        write_instruction_overlay(
            repo=repo,
            instructions_file=args.instructions_file,
            template=args.template,
            checks=checks,
            extra_rules=args.extra_rule,
            force=args.force,
        )
    )
    results.append(check_note)

    print(f"Bootstrapped {repo}")
    for result in results:
        print(f"- {result}")
    print(
        f"- Next: open the project in Claw/Codex and use ${SKILL_NAME}, "
        "or run /skills and /memory to confirm discovery."
    )
    return 0


def resolve_checks(
    *,
    repo: Path,
    explicit_checks: list[str],
    allow_detection: bool,
) -> tuple[list[str], str]:
    if explicit_checks:
        return explicit_checks, f"Used {len(explicit_checks)} explicit check(s)"

    if not allow_detection:
        return [], "Check auto-detection disabled; left placeholder checks"

    checks = detect_checks(repo)
    if checks:
        return checks, f"Auto-detected {len(checks)} check(s): {', '.join(checks)}"
    return [], "No checks auto-detected; left placeholder checks"


def detect_checks(repo: Path) -> list[str]:
    detected: list[str] = []
    detected.extend(detect_node_checks(repo))
    detected.extend(detect_rust_checks(repo))
    detected.extend(detect_python_checks(repo))

    if not detected:
        detected.extend(detect_make_checks(repo))

    return dedupe(detected)[:5]


def detect_node_checks(repo: Path) -> list[str]:
    package_json = repo / "package.json"
    if not package_json.exists():
        return []

    try:
        data = json.loads(package_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        return []

    package_manager = detect_package_manager(repo)
    order = ["lint", "test", "typecheck", "build", "check"]
    checks: list[str] = []
    for name in order:
        if valid_script(scripts.get(name)):
            checks.append(format_script_command(package_manager, name))
    return checks


def detect_package_manager(repo: Path) -> str:
    if (repo / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (repo / "yarn.lock").exists():
        return "yarn"
    if (repo / "bun.lockb").exists() or (repo / "bun.lock").exists():
        return "bun"
    return "npm"


def valid_script(value: object) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip().lower()
    return normalized not in {"", "echo \"error: no test specified\" && exit 1"}


def format_script_command(package_manager: str, script_name: str) -> str:
    if package_manager == "npm":
        return f"npm run {script_name}"
    if package_manager == "bun":
        return f"bun run {script_name}"
    return f"{package_manager} {script_name}"


def detect_rust_checks(repo: Path) -> list[str]:
    if (repo / "Cargo.toml").exists():
        prefix = ""
    elif (repo / "rust" / "Cargo.toml").exists():
        prefix = "cd rust && "
    else:
        return []

    return [
        f"{prefix}cargo fmt --all --check",
        f"{prefix}cargo clippy --workspace --all-targets -- -D warnings",
        f"{prefix}cargo test --workspace",
    ]


def detect_python_checks(repo: Path) -> list[str]:
    pyproject = repo / "pyproject.toml"
    config_text = pyproject.read_text(encoding="utf-8") if pyproject.exists() else ""
    checks: list[str] = []

    has_pytest = (repo / "pytest.ini").exists() or "pytest" in config_text
    has_ruff = "ruff" in config_text or (repo / ".ruff.toml").exists()
    has_mypy = "mypy" in config_text or (repo / "mypy.ini").exists()
    has_tests_dir = (repo / "tests").is_dir()

    if has_ruff:
        checks.append("python3 -m ruff check .")
    if has_mypy:
        checks.append("python3 -m mypy .")
    if has_pytest:
        checks.append("python3 -m pytest")
    elif has_tests_dir:
        checks.append("python3 -m unittest discover -s tests -v")

    return checks


def detect_make_checks(repo: Path) -> list[str]:
    makefile = repo / "Makefile"
    if not makefile.exists():
        return []

    content = makefile.read_text(encoding="utf-8")
    targets = {"lint", "test", "build", "check"}
    checks: list[str] = []
    for target in ("lint", "test", "build", "check"):
        if re.search(rf"^{re.escape(target)}\s*:", content, flags=re.MULTILINE):
            checks.append(f"make {target}")
    return checks


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        output.append(value)
    return output


def install_skill_overlay(
    *,
    repo: Path,
    skill_root: Path,
    install_mode: str,
    force: bool,
) -> str:
    if install_mode == "skip":
        return "Skipped .codex/skills installation"

    target = repo / ".codex" / "skills" / SKILL_NAME
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() or target.is_symlink():
        if target.is_symlink() and target.resolve() == skill_root.resolve():
            return f"Skill link already up to date at {target}"
        if not force:
            raise SystemExit(
                f"Skill target already exists: {target}. Use --force to replace it."
            )
        remove_path(target)

    if install_mode == "link":
        target.symlink_to(skill_root, target_is_directory=True)
        return f"Linked skill into {target}"

    shutil.copytree(
        skill_root,
        target,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
    )
    return f"Copied skill into {target}"


def write_instruction_overlay(
    *,
    repo: Path,
    instructions_file: str,
    template: str,
    checks: list[str],
    extra_rules: list[str],
    force: bool,
) -> str:
    target = repo / instructions_file
    target.parent.mkdir(parents=True, exist_ok=True)
    content = render_instruction_overlay(
        template=template,
        checks=checks,
        extra_rules=extra_rules,
    )

    if target.exists():
        existing = target.read_text(encoding="utf-8")
        if existing == content:
            return f"Instruction overlay already up to date at {target}"
        if not force:
            raise SystemExit(
                f"Instruction file already exists: {target}. Use --force to replace it."
            )

    target.write_text(content, encoding="utf-8")
    return f"Wrote {template} instruction overlay to {target}"


def render_instruction_overlay(
    *,
    template: str,
    checks: list[str],
    extra_rules: list[str],
) -> str:
    title, rules = template_rules(template)
    lines = [title, ""]
    lines.extend(f"- {rule}" for rule in rules)
    lines.extend(["", "## Required checks"])

    if checks:
        lines.extend(f"- `{check}`" for check in checks)
    else:
        lines.append("- `<insert test/build/lint commands>`")

    if extra_rules:
        lines.extend(["", "## Project-specific rules"])
        lines.extend(f"- {rule}" for rule in extra_rules)

    lines.append("")
    return "\n".join(lines)


def template_rules(template: str) -> tuple[str, list[str]]:
    if template == "debug":
        return (
            "# Debugging rules",
            [
                f"Use ${SKILL_NAME} for debugging and root-cause analysis.",
                "Reproduce the issue or gather failure evidence before editing.",
                "Keep hypotheses explicit and separate from fixes.",
                "After a fix, rerun the failing path and the required checks.",
                "Escalate before destructive, externally visible, or shared-state actions.",
            ],
        )

    if template == "review":
        return (
            "# Review and verification rules",
            [
                f"Use ${SKILL_NAME} for review, hardening, and verification tasks.",
                "Stay read-only unless the user explicitly asks for fixes.",
                "Try to break the change before declaring it sound.",
                "Record meaningful verification as command -> observed result.",
                "Escalate before destructive, externally visible, or shared-state actions.",
            ],
        )

    return (
        "# Working rules",
        [
            f"Use ${SKILL_NAME} for non-trivial implementation, debugging, and verification tasks.",
            "Explore before editing.",
            "Keep changes tightly scoped to the requested outcome.",
            "Prefer modifying existing structures before introducing new abstractions.",
            "Escalate before destructive, externally visible, or shared-state actions.",
        ],
    )


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    shutil.rmtree(path)


if __name__ == "__main__":
    sys.exit(main())
