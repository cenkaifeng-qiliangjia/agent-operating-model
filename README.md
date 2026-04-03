# Agent Operating Model

Public repository for the `agent-operating-model` skill package.

This repo now follows a cleaner split between:
- repo-level documentation for humans
- a canonical nested skill package for Codex/OpenClaw/Claw Code

## Repository layout

```text
.
├── README.md                    # Repo-level documentation
└── agent-operating-model/       # Canonical skill package
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/
    └── scripts/
```

The runtime skill package lives in [`agent-operating-model/`](./agent-operating-model/).

## What the skill does

This skill adds a stronger engineering operating model:
- define the task contract before acting
- separate `explore`, `plan`, `implement`, and `verify`
- control context growth
- pause before risky actions
- verify adversarially instead of rubber-stamping

It is most useful for non-trivial engineering work where you want an agent to behave more like a disciplined engineer than a fast autocomplete loop.

## Practical scenarios

1. Feature work
Use the skill to keep new implementation scoped and verification explicit.

2. Debugging
Use the skill to force evidence gathering and root-cause separation before patching.

3. Review or hardening
Use the skill to switch into adversarial validation and produce `command -> observed result`.

## Why this repo changed shape

Anthropic's skill guidance recommends keeping the repo root and the actual skill package separate. Earlier revisions of this project used the skill directory itself as the git repo root.

This repo now uses:
- a nested canonical skill package in [`agent-operating-model/`](./agent-operating-model/)
- a local compatibility symlink at `~/.codex/skills/agent-operating-model`

That preserves local auto-discovery while keeping the repository structure closer to the recommended layout.

## Use the canonical package

From this repo root, the main files are:
- [SKILL.md](./agent-operating-model/SKILL.md)
- [Claw compatibility](./agent-operating-model/references/claw-code-compatibility.md)
- [Claude-derived principles](./agent-operating-model/references/claude-code-derived-principles.md)
- [Delegation and verification prompts](./agent-operating-model/references/delegation-and-verification-prompts.md)
- [Test cases](./agent-operating-model/references/test-cases.md)
- [Evaluation overview](./eval/README.md)
- [Current capability assessment](./eval/current-assessment.md)

## Bootstrap a target project

```bash
python3 agent-operating-model/scripts/bootstrap_project.py \
  --repo /path/to/project
```

The helper can:
- auto-detect likely checks from common repo manifests
- generate `feature`, `debug`, or `review` instruction overlays
- link or copy the skill into a target repo

Example:

```bash
python3 agent-operating-model/scripts/bootstrap_project.py \
  --repo /path/to/project \
  --template debug \
  --check "pnpm test -- billing-webhook"
```

## Export a clean distribution package

```bash
python3 agent-operating-model/scripts/export_skill_package.py \
  --output /tmp/skill-dist \
  --force
```

This exports a clean installable package under `/tmp/skill-dist/agent-operating-model/`.

## Validation

```bash
python3 /Users/jerviscen/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  /Users/jerviscen/workspace/skills/agent-operating-model/agent-operating-model
```

## Semi-automated smoke evaluation

```bash
python3 eval/run_smoke_eval.py \
  --output-json eval/latest-smoke-report.json \
  --output-md eval/latest-smoke-report.md
```

Latest generated reports:
- [Smoke report (Markdown)](./eval/latest-smoke-report.md)
- [Smoke report (JSON)](./eval/latest-smoke-report.json)

## Current capability assessment

Current status: strong and publishable.

Current scorecard:
- Trigger precision: 8.5/10
- Instruction efficiency: 9.0/10
- Practicality: 9.0/10
- Portability: 8.5/10
- Verifiability: 8.5/10

Overall: 8.7/10

Why:
- the canonical nested package validates cleanly
- bootstrap smoke checks succeeded against temporary Node, Rust, and Python repos
- the skill now has explicit trigger cases, non-trigger cases, and a cleaner export path
- the latest semi-automated smoke run currently passes 7/7 checks

See [eval/current-assessment.md](./eval/current-assessment.md) for the full reasoning and current limits.

## Sources

This skill package was shaped by:
- Anthropic's public skill-building guidance
- the recovered Claude Code architectural analysis
- targeted review of `ultraworkers/claw-code` prompt, command, and tool surfaces
