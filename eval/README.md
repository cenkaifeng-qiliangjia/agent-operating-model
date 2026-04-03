# Evaluation

This directory keeps repo-level evaluation assets for the `agent-operating-model` skill.

The canonical runtime package stays under [`../agent-operating-model/`](../agent-operating-model/). Evaluation lives here so the skill package itself stays lean.

## What we evaluate

We evaluate the skill along five dimensions:
- Trigger precision
- Instruction efficiency
- Practicality
- Portability
- Verifiability

These dimensions mirror the repo's current purpose:
- act as a useful behavior overlay
- remain lightweight in context
- travel cleanly across Codex, OpenClaw, and Claw Code
- stay testable over time

## Evaluation sources

We use three evidence types:

1. Structure validation
- `quick_validate.py` against the canonical nested package

2. Behavior-oriented fixtures
- trigger and non-trigger cases in [`../agent-operating-model/references/test-cases.md`](../agent-operating-model/references/test-cases.md)

3. Tooling smoke checks
- bootstrap helper against temporary Node, Rust, and Python repos
- clean export package generation
- local auto-discovery symlink integrity

## Current assessment

See [current-assessment.md](./current-assessment.md).

## How to extend this

Good next steps:
- add baseline comparisons against a non-skill workflow
- add repeated prompts with observed outputs from Codex/OpenClaw/Claw Code
- add regression criteria for bootstrap heuristics
