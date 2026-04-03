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

## 人话版

装上这个 skill 之后，最直接的效果不是“模型突然变聪明了”，而是它做事会更像一个靠谱工程师。

你通常会看到这些变化：
- 不会一上来就乱改代码，先读上下文，再动手。
- 不容易顺手加一堆你没要的东西，scope 会更收敛。
- 更愿意把工作拆成探索、实现、验证几个阶段，而不是想到哪写到哪。
- 改完不会只说“应该好了”，而是更倾向真的跑检查、给出证据。
- 做复杂任务时更稳，尤其是调 bug、做 review、接手陌生仓库的时候。

如果用更直白的话说，它提升的是“做事方式”：
- 少跑偏
- 少瞎改
- 少过度设计
- 多验证
- 多一点工程纪律

它最适合的场景是：
- 新功能开发，希望代理改得准一点、少扩 scope
- 排查 bug，希望代理先找根因，不要靠猜
- 提交前 review，希望代理更像 QA 或 reviewer，而不是实现者自我感觉良好
- 接手陌生项目，希望代理先建立 repo 规则和检查入口

## 这些能力模型本来没有吗

有，很多强一点的模型本来就“可能”会表现出其中一部分能力。

比如不装这个 skill，它也可能会：
- 先读代码再改
- 尽量少改
- 自己分步骤
- 跑一些测试

但问题通常不是“会不会”，而是“稳不稳”。

这个 skill 的价值不是凭空创造新能力，而是把这些原本可能出现、也可能不出现的好行为，尽量变成更稳定、更高频的默认行为。它更像是在给代理补一套工作纪律和执行框架。

所以更准确的理解是：
- 不装 skill：有时会这样做，有时不会，比较看 prompt、上下文、任务复杂度和当时状态
- 装了 skill：更容易持续这样做，尤其在复杂任务、长任务、陌生仓库里更明显

如果用一句话概括：
- 它不是把模型“变成另一个模型”
- 它是让模型“更稳定地用更好的方式工作”

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
