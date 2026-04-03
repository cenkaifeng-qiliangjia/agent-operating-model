#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SKILL_NAME = "agent-operating-model"


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
            checks=args.checks,
            extra_rules=args.extra_rule,
            force=args.force,
        )
    )

    print(f"Bootstrapped {repo}")
    for result in results:
        print(f"- {result}")
    print(
        f"- Next: open the project in Claw/Codex and use ${SKILL_NAME}, "
        "or run /skills and /memory to confirm discovery."
    )
    return 0


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
    checks: list[str],
    extra_rules: list[str],
    force: bool,
) -> str:
    target = repo / instructions_file
    target.parent.mkdir(parents=True, exist_ok=True)
    content = render_instruction_overlay(checks=checks, extra_rules=extra_rules)

    if target.exists():
        existing = target.read_text(encoding="utf-8")
        if existing == content:
            return f"Instruction overlay already up to date at {target}"
        if not force:
            raise SystemExit(
                f"Instruction file already exists: {target}. Use --force to replace it."
            )

    target.write_text(content, encoding="utf-8")
    return f"Wrote instruction overlay to {target}"


def render_instruction_overlay(*, checks: list[str], extra_rules: list[str]) -> str:
    lines = [
        "# Working rules",
        "",
        f"- Use ${SKILL_NAME} for non-trivial implementation, debugging, and verification tasks.",
        "- Explore before editing.",
        "- Keep changes tightly scoped to the requested outcome.",
        "- Escalate before destructive, externally visible, or shared-state actions.",
        "",
        "## Required checks",
    ]

    if checks:
        lines.extend(f"- `{check}`" for check in checks)
    else:
        lines.append("- `<insert test/build/lint commands>`")

    if extra_rules:
        lines.extend(["", "## Project-specific rules"])
        lines.extend(f"- {rule}" for rule in extra_rules)

    lines.append("")
    return "\n".join(lines)


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    shutil.rmtree(path)


if __name__ == "__main__":
    sys.exit(main())
