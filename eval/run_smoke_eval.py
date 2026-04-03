#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable


@dataclass
class CheckResult:
    name: str
    status: str
    summary: str
    details: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run semi-automated smoke evaluation for the agent-operating-model repo."
    )
    parser.add_argument("--output-json", help="Write structured results to this JSON file.")
    parser.add_argument("--output-md", help="Write a Markdown summary to this file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    skill_root = repo_root / "agent-operating-model"

    checks: list[Callable[[Path, Path], CheckResult]] = [
        check_quick_validate,
        check_local_symlink,
        check_bootstrap_node,
        check_bootstrap_rust_review,
        check_bootstrap_python_debug,
        check_bootstrap_copy_mode,
        check_export_package,
    ]

    results = [check(repo_root, skill_root) for check in checks]
    summary = {
        "repo_root": str(repo_root),
        "skill_root": str(skill_root),
        "passed": sum(result.status == "pass" for result in results),
        "failed": sum(result.status == "fail" for result in results),
        "skipped": sum(result.status == "skip" for result in results),
        "results": [asdict(result) for result in results],
    }

    output = render_console_summary(summary)
    print(output)

    if args.output_json:
        output_json = Path(args.output_json).expanduser().resolve()
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if args.output_md:
        output_md = Path(args.output_md).expanduser().resolve()
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(render_markdown_summary(summary), encoding="utf-8")

    return 1 if summary["failed"] else 0


def check_quick_validate(repo_root: Path, skill_root: Path) -> CheckResult:
    validator = Path.home() / ".codex/skills/.system/skill-creator/scripts/quick_validate.py"
    if not validator.exists():
        return CheckResult(
            name="quick_validate",
            status="skip",
            summary="quick_validate.py not found in local Codex installation",
            details=str(validator),
        )

    completed = run_command(["python3", str(validator), str(skill_root)])
    if completed.returncode == 0:
        return CheckResult(
            name="quick_validate",
            status="pass",
            summary="Canonical nested skill package validates cleanly",
            details=completed.stdout.strip(),
        )
    return CheckResult(
        name="quick_validate",
        status="fail",
        summary="Canonical nested skill package failed validation",
        details=completed.stderr.strip() or completed.stdout.strip(),
    )


def check_local_symlink(repo_root: Path, skill_root: Path) -> CheckResult:
    local_path = Path.home() / ".codex/skills/agent-operating-model"
    if not local_path.exists():
        return CheckResult(
            name="local_symlink",
            status="skip",
            summary="No local auto-discovery entry at ~/.codex/skills/agent-operating-model",
            details=str(local_path),
        )

    try:
        resolved = local_path.resolve()
    except OSError as exc:
        return CheckResult(
            name="local_symlink",
            status="fail",
            summary="Local auto-discovery entry exists but could not be resolved",
            details=str(exc),
        )

    if resolved == skill_root:
        return CheckResult(
            name="local_symlink",
            status="pass",
            summary="Local auto-discovery entry resolves to canonical nested package",
            details=f"{local_path} -> {resolved}",
        )

    return CheckResult(
        name="local_symlink",
        status="fail",
        summary="Local auto-discovery entry points somewhere else",
        details=f"{local_path} -> {resolved}",
    )


def check_bootstrap_node(repo_root: Path, skill_root: Path) -> CheckResult:
    with tempfile.TemporaryDirectory(prefix="aom-node-") as temp_dir:
        repo = Path(temp_dir)
        (repo / "package.json").write_text(
            json.dumps(
                {
                    "scripts": {
                        "lint": "eslint .",
                        "test": "vitest run",
                        "build": "vite build",
                    }
                }
            ),
            encoding="utf-8",
        )
        (repo / "pnpm-lock.yaml").write_text("lockfileVersion: 9\n", encoding="utf-8")

        completed = run_command(
            ["python3", str(skill_root / "scripts/bootstrap_project.py"), "--repo", str(repo)]
        )
        content = (repo / "CLAW.md").read_text(encoding="utf-8")
        expected = ["`pnpm lint`", "`pnpm test`", "`pnpm build`"]
        missing = [item for item in expected if item not in content]
        if completed.returncode == 0 and not missing:
            return CheckResult(
                name="bootstrap_node",
                status="pass",
                summary="Node bootstrap infers pnpm checks and writes feature overlay",
                details=content.strip(),
            )
        return CheckResult(
            name="bootstrap_node",
            status="fail",
            summary="Node bootstrap did not infer the expected checks",
            details=(completed.stdout + "\n" + completed.stderr + "\n" + content).strip(),
        )


def check_bootstrap_rust_review(repo_root: Path, skill_root: Path) -> CheckResult:
    with tempfile.TemporaryDirectory(prefix="aom-rust-") as temp_dir:
        repo = Path(temp_dir)
        (repo / "rust").mkdir(parents=True, exist_ok=True)
        (repo / "rust/Cargo.toml").write_text("[workspace]\nmembers = []\n", encoding="utf-8")

        completed = run_command(
            [
                "python3",
                str(skill_root / "scripts/bootstrap_project.py"),
                "--repo",
                str(repo),
                "--template",
                "review",
                "--install-skill",
                "skip",
            ]
        )
        content = (repo / "CLAW.md").read_text(encoding="utf-8")
        expected = [
            "`cd rust && cargo fmt --all --check`",
            "`cd rust && cargo clippy --workspace --all-targets -- -D warnings`",
            "`cd rust && cargo test --workspace`",
            "Stay read-only unless the user explicitly asks for fixes.",
        ]
        missing = [item for item in expected if item not in content]
        if completed.returncode == 0 and not missing:
            return CheckResult(
                name="bootstrap_rust_review",
                status="pass",
                summary="Rust review bootstrap infers cargo checks and renders review overlay",
                details=content.strip(),
            )
        return CheckResult(
            name="bootstrap_rust_review",
            status="fail",
            summary="Rust review bootstrap did not match expectations",
            details=(completed.stdout + "\n" + completed.stderr + "\n" + content).strip(),
        )


def check_bootstrap_python_debug(repo_root: Path, skill_root: Path) -> CheckResult:
    with tempfile.TemporaryDirectory(prefix="aom-python-") as temp_dir:
        repo = Path(temp_dir)
        (repo / "tests").mkdir(parents=True, exist_ok=True)
        (repo / "pyproject.toml").write_text(
            "[tool.ruff]\nline-length = 100\n\n[tool.pytest.ini_options]\naddopts = \"-q\"\n",
            encoding="utf-8",
        )

        completed = run_command(
            [
                "python3",
                str(skill_root / "scripts/bootstrap_project.py"),
                "--repo",
                str(repo),
                "--template",
                "debug",
                "--install-skill",
                "skip",
            ]
        )
        content = (repo / "CLAW.md").read_text(encoding="utf-8")
        expected = [
            "`python3 -m ruff check .`",
            "`python3 -m pytest`",
            "Reproduce the issue or gather failure evidence before editing.",
        ]
        missing = [item for item in expected if item not in content]
        if completed.returncode == 0 and not missing:
            return CheckResult(
                name="bootstrap_python_debug",
                status="pass",
                summary="Python debug bootstrap infers Ruff/Pytest checks and renders debug overlay",
                details=content.strip(),
            )
        return CheckResult(
            name="bootstrap_python_debug",
            status="fail",
            summary="Python debug bootstrap did not match expectations",
            details=(completed.stdout + "\n" + completed.stderr + "\n" + content).strip(),
        )


def check_bootstrap_copy_mode(repo_root: Path, skill_root: Path) -> CheckResult:
    with tempfile.TemporaryDirectory(prefix="aom-copy-") as temp_dir:
        repo = Path(temp_dir)
        completed = run_command(
            [
                "python3",
                str(skill_root / "scripts/bootstrap_project.py"),
                "--repo",
                str(repo),
                "--instructions-file",
                ".claw/instructions.md",
                "--install-skill",
                "copy",
                "--template",
                "review",
                "--check",
                "cargo test",
                "--extra-rule",
                "Do not edit generated files by hand.",
            ]
        )
        copied_skill = repo / ".codex/skills/agent-operating-model/SKILL.md"
        instructions = repo / ".claw/instructions.md"
        if (
            completed.returncode == 0
            and copied_skill.exists()
            and instructions.exists()
            and "Do not edit generated files by hand." in instructions.read_text(encoding="utf-8")
        ):
            return CheckResult(
                name="bootstrap_copy_mode",
                status="pass",
                summary="Copy mode vendors the skill and writes .claw/instructions.md",
                details=instructions.read_text(encoding="utf-8").strip(),
            )
        return CheckResult(
            name="bootstrap_copy_mode",
            status="fail",
            summary="Copy mode did not produce the expected repo overlay",
            details=(completed.stdout + "\n" + completed.stderr).strip(),
        )


def check_export_package(repo_root: Path, skill_root: Path) -> CheckResult:
    with tempfile.TemporaryDirectory(prefix="aom-export-") as temp_dir:
        output_root = Path(temp_dir)
        completed = run_command(
            [
                "python3",
                str(skill_root / "scripts/export_skill_package.py"),
                "--output",
                str(output_root),
                "--force",
            ]
        )
        exported_root = output_root / "agent-operating-model"
        readme_path = exported_root / "README.md"
        skill_path = exported_root / "SKILL.md"
        if completed.returncode == 0 and skill_path.exists() and not readme_path.exists():
            files = sorted(
                str(path.relative_to(exported_root))
                for path in exported_root.rglob("*")
                if path.is_file()
            )
            return CheckResult(
                name="export_package",
                status="pass",
                summary="Clean export includes runtime files and omits repo-only README",
                details="\n".join(files),
            )
        return CheckResult(
            name="export_package",
            status="fail",
            summary="Export package did not match expectations",
            details=(completed.stdout + "\n" + completed.stderr).strip(),
        )


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def render_console_summary(summary: dict) -> str:
    lines = ["Smoke evaluation summary"]
    lines.append(f"Passed: {summary['passed']}")
    lines.append(f"Failed: {summary['failed']}")
    lines.append(f"Skipped: {summary['skipped']}")
    lines.append("")
    for result in summary["results"]:
        lines.append(f"[{result['status'].upper()}] {result['name']}: {result['summary']}")
    return "\n".join(lines)


def render_markdown_summary(summary: dict) -> str:
    lines = ["# Latest Smoke Report", ""]
    lines.append(f"- Repo root: `{summary['repo_root']}`")
    lines.append(f"- Skill root: `{summary['skill_root']}`")
    lines.append(f"- Passed: {summary['passed']}")
    lines.append(f"- Failed: {summary['failed']}")
    lines.append(f"- Skipped: {summary['skipped']}")
    lines.append("")
    for result in summary["results"]:
        lines.append(f"## {result['name']}")
        lines.append("")
        lines.append(f"- Status: `{result['status']}`")
        lines.append(f"- Summary: {result['summary']}")
        lines.append("")
        lines.append("```text")
        lines.append(result["details"].strip() or "(no details)")
        lines.append("```")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    sys.exit(main())
