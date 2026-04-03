# Agent Operating Model

A portable engineering-behavior skill for Codex, OpenClaw, and Claw Code.

This skill does not add a new tool. It adds a stronger way of working:
- define the task contract before acting
- separate `explore`, `plan`, `implement`, and `verify`
- control context growth instead of dumping everything into the thread
- pause before risky actions
- verify adversarially instead of rubber-stamping

The skill package lives in [SKILL.md](./SKILL.md). The rest of this README is for humans browsing the repository.

## What it is good at

Use this skill when the task is non-trivial and you want the agent to behave more like a disciplined engineer than a fast autocomplete loop.

Typical wins:
- fewer unasked-for features
- less over-abstraction and speculative refactoring
- tighter change scope
- better subagent delegation
- stronger evidence before calling something "done"

## Real usage scenarios

### 1. Building a new feature

Prompt:

```text
Use $agent-operating-model to add audit logging to the admin user deletion flow.
Explore first, then plan, then implement, then verify.
```

Effect:
- the agent reads current code paths before editing
- the plan stays tied to the existing architecture
- the implementation is less likely to add side abstractions
- the final report is more likely to include real checks instead of a confident guess

### 2. Debugging a stubborn bug

Prompt:

```text
Use $agent-operating-model to debug why the billing webhook occasionally creates duplicate invoices.
Stay in explore mode until you have a root-cause hypothesis.
```

Effect:
- the agent resists patching symptoms too early
- investigation and implementation are separated
- failure evidence is surfaced before code changes start

### 3. Pre-PR hardening

Prompt:

```text
Use $agent-operating-model to review and verify this branch before I open a PR.
Assume the implementation may still be wrong.
```

Effect:
- the agent switches into adversarial verification
- it records `command -> observed result`
- it is more likely to produce a clear `PASS`, `FAIL`, or `PARTIAL` verdict

## Why Claw Code makes this skill better

After reviewing `ultraworkers/claw-code`, the main improvement is not "more rules." It is better fit with Claw's runtime:

- Claw can discover the skill from project `.codex/skills`, user `$CODEX_HOME/skills`, and `~/.codex/skills`.
- Claw injects `CLAW.md` and `.claw/instructions.md` into the prompt, so this skill can be reinforced at repo scope without bloating the core skill.
- Claw exposes compatible workflow entry points such as `/skills`, `/memory`, `/agents`, `/permissions`, and `/ultraplan`.
- Claw's tool surface has native structured primitives like `read_file`, `edit_file`, `write_file`, `glob_search`, `grep_search`, `Skill`, and `Agent`, which map well onto the skill's operating rules.

That makes this skill more practical in Claw Code than a generic prompt-only guideline.

More detail:
- [Claw compatibility](./references/claw-code-compatibility.md)
- [Claude-derived principles](./references/claude-code-derived-principles.md)
- [Delegation and verification prompts](./references/delegation-and-verification-prompts.md)
- [Test cases](./references/test-cases.md)

## Install

User-wide:

```bash
mkdir -p ~/.codex/skills
cp -R agent-operating-model ~/.codex/skills/
```

Project-local:

```bash
mkdir -p .codex/skills
cp -R agent-operating-model .codex/skills/
```

## Bootstrap a project

If you want a target repo to pick up this operating model quickly, use the included bootstrap helper:

```bash
python3 scripts/bootstrap_project.py \
  --repo /path/to/project
```

By default this:
- writes a minimal `CLAW.md`
- links this skill into `<repo>/.codex/skills/agent-operating-model`
- auto-detects likely checks from common repo files when it can

Useful variants:

```bash
python3 scripts/bootstrap_project.py \
  --repo /path/to/project \
  --template debug \
  --check "pnpm test -- billing-webhook" \
  --check "pnpm lint"
```

```bash
python3 scripts/bootstrap_project.py \
  --repo /path/to/project \
  --instructions-file .claw/instructions.md \
  --install-skill copy \
  --check "cargo fmt" \
  --check "cargo test"
```

```bash
python3 scripts/bootstrap_project.py \
  --repo /path/to/project \
  --template review \
  --install-skill skip \
  --extra-rule "Do not modify generated API clients directly."
```

## Validate and package

Quick structure validation:

```bash
python3 /Users/jerviscen/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

If you want a clean runtime package without repo-only docs like `README.md`, export one:

```bash
python3 scripts/export_skill_package.py \
  --output /tmp/skill-dist \
  --force
```

That produces `/tmp/skill-dist/agent-operating-model/` as a cleaner distribution artifact for direct installation.

## Suggested prompts

```text
Use $agent-operating-model to implement this change with explore -> plan -> implement -> verify.
```

```text
Use $agent-operating-model and stay read-only until you can explain the likely change points.
```

```text
Use $agent-operating-model to verify this work and try to break it before declaring success.
```
