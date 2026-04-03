# Current Capability Assessment

Date: 2026-04-03

## Summary

Current status: strong and publishable.

This skill is no longer just a prompt overlay. It now combines:
- a concise canonical skill package
- Claw/Codex/OpenClaw compatibility guidance
- project bootstrap tooling
- a clean export path
- repo-level evaluation criteria

## Scorecard

- Trigger precision: 8.5/10
- Instruction efficiency: 9.0/10
- Practicality: 9.0/10
- Portability: 8.5/10
- Verifiability: 8.5/10

Overall: 8.7/10

## Why these scores

### Trigger precision: 8.5/10

Strengths:
- The frontmatter description clearly states what the skill does and when to use it.
- The reference test cases include both trigger and non-trigger examples.

Current limit:
- We still do not have repeated live harness runs showing how often agents trigger the skill appropriately across multiple hosts.

### Instruction efficiency: 9.0/10

Strengths:
- The runtime package is split into `SKILL.md`, `references/`, and `scripts/`.
- The repo now separates repo-level docs from the canonical nested skill package.

Current limit:
- The skill still spans several references because it covers multiple hosts and bootstrap behavior.

### Practicality: 9.0/10

Strengths:
- `bootstrap_project.py` can install or link the skill into a target repo.
- The bootstrap helper can infer likely checks and generate `feature`, `debug`, or `review` overlays.
- `export_skill_package.py` creates a clean distribution artifact.

Current limit:
- There is not yet an installer that publishes directly to a remote marketplace or registry.

### Portability: 8.5/10

Strengths:
- The skill is written to be host-aware rather than Claude-tool-specific.
- It explicitly maps onto Claw Code's prompt, command, and tool surfaces.
- It remains usable from the existing `~/.codex/skills/agent-operating-model` path through a symlink.

Current limit:
- Host runtimes still differ in permissions, hooks, and orchestration depth; the skill can only emulate those behaviors, not recreate them.

### Verifiability: 8.5/10

Strengths:
- The canonical package validates cleanly with `quick_validate.py`.
- Bootstrap smoke checks succeeded against temporary Node, Rust, and Python repos.
- Clean package export succeeded.

Current limit:
- We do not yet have automated end-to-end output comparisons against baseline agents on real engineering tasks.

## Evidence gathered

Validated successfully:
- canonical nested skill package passes `quick_validate.py`
- local auto-discovery symlink resolves correctly
- Node-style bootstrap infers `pnpm lint`, `pnpm test`, and `pnpm build`
- Rust-style bootstrap infers `cargo fmt`, `cargo clippy`, and `cargo test`
- Python-style bootstrap infers `ruff` and `pytest`
- export script produces a clean package without repo-only README content
- latest smoke evaluation currently passes 7/7 checks

## What this skill is best at right now

- Making complex engineering tasks more disciplined
- Improving repo onboarding via project-local `CLAW.md` or `.claw/instructions.md`
- Raising the floor on verification quality
- Giving Codex/OpenClaw/Claw Code a more stable operating model

## What is still missing

- Baseline-vs-skill comparisons on repeated real tasks
- Host-specific outcome captures from Codex, OpenClaw, and Claw Code
- A richer installer or publishing workflow
