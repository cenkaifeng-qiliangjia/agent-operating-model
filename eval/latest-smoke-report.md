# Latest Smoke Report

- Repo root: `/Users/jerviscen/workspace/skills/agent-operating-model`
- Skill root: `/Users/jerviscen/workspace/skills/agent-operating-model/agent-operating-model`
- Passed: 7
- Failed: 0
- Skipped: 0

## quick_validate

- Status: `pass`
- Summary: Canonical nested skill package validates cleanly

```text
Skill is valid!
```

## local_symlink

- Status: `pass`
- Summary: Local auto-discovery entry resolves to canonical nested package

```text
/Users/jerviscen/.codex/skills/agent-operating-model -> /Users/jerviscen/workspace/skills/agent-operating-model/agent-operating-model
```

## bootstrap_node

- Status: `pass`
- Summary: Node bootstrap infers pnpm checks and writes feature overlay

```text
# Working rules

- Use $agent-operating-model for non-trivial implementation, debugging, and verification tasks.
- Explore before editing.
- Keep changes tightly scoped to the requested outcome.
- Prefer modifying existing structures before introducing new abstractions.
- Escalate before destructive, externally visible, or shared-state actions.

## Required checks
- `pnpm lint`
- `pnpm test`
- `pnpm build`
```

## bootstrap_rust_review

- Status: `pass`
- Summary: Rust review bootstrap infers cargo checks and renders review overlay

```text
# Review and verification rules

- Use $agent-operating-model for review, hardening, and verification tasks.
- Stay read-only unless the user explicitly asks for fixes.
- Try to break the change before declaring it sound.
- Record meaningful verification as command -> observed result.
- Escalate before destructive, externally visible, or shared-state actions.

## Required checks
- `cd rust && cargo fmt --all --check`
- `cd rust && cargo clippy --workspace --all-targets -- -D warnings`
- `cd rust && cargo test --workspace`
```

## bootstrap_python_debug

- Status: `pass`
- Summary: Python debug bootstrap infers Ruff/Pytest checks and renders debug overlay

```text
# Debugging rules

- Use $agent-operating-model for debugging and root-cause analysis.
- Reproduce the issue or gather failure evidence before editing.
- Keep hypotheses explicit and separate from fixes.
- After a fix, rerun the failing path and the required checks.
- Escalate before destructive, externally visible, or shared-state actions.

## Required checks
- `python3 -m ruff check .`
- `python3 -m pytest`
```

## bootstrap_copy_mode

- Status: `pass`
- Summary: Copy mode vendors the skill and writes .claw/instructions.md

```text
# Review and verification rules

- Use $agent-operating-model for review, hardening, and verification tasks.
- Stay read-only unless the user explicitly asks for fixes.
- Try to break the change before declaring it sound.
- Record meaningful verification as command -> observed result.
- Escalate before destructive, externally visible, or shared-state actions.

## Required checks
- `cargo test`

## Project-specific rules
- Do not edit generated files by hand.
```

## export_package

- Status: `pass`
- Summary: Clean export includes runtime files and omits repo-only README

```text
SKILL.md
agents/openai.yaml
references/claude-code-derived-principles.md
references/claw-code-compatibility.md
references/delegation-and-verification-prompts.md
references/test-cases.md
scripts/bootstrap_project.py
scripts/export_skill_package.py
```
