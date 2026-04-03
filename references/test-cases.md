# Skill test cases

Use these cases to evaluate whether the skill follows the Anthropic-style skill best practices around triggering, non-triggering, and functional behavior.

## Trigger cases

These should trigger the skill or make it obviously useful:

1. `Use $agent-operating-model to add audit logging to the account deletion flow.`
Expected:
- establish explore -> plan -> implement -> verify
- keep scope narrow
- report concrete checks

2. `Use $agent-operating-model to debug why the checkout webhook sometimes double-charges users. Stay read-only until you have a root-cause hypothesis.`
Expected:
- stay in explore mode first
- separate investigation from implementation
- avoid speculative fixes

3. `Use $agent-operating-model to verify this branch before I open a PR.`
Expected:
- switch into adversarial verification
- produce `command -> observed result`
- emit `PASS`, `FAIL`, or `PARTIAL`

4. `Wire this repo up for Claw Code so it picks up the operating model automatically.`
Expected:
- use `scripts/bootstrap_project.py`
- create repo-local instructions
- explain how `/skills` or `/memory` can confirm discovery

5. `Bootstrap this repo for debugging with $agent-operating-model and generate the right local instructions.`
Expected:
- choose or recommend `--template debug`
- preserve repo-local instruction brevity
- include checks that fit the repo

## Non-trigger cases

These should usually not need the skill:

1. `Translate this paragraph into Korean.`
Expected:
- no heavy operating-model overlay

2. `What is 17 * 24?`
Expected:
- direct answer, no explore/plan/verify ceremony

3. `Summarize the README I pasted below.`
Expected:
- simple summarization flow

## Functional checks

When the skill is used, verify these outcomes:

- The agent does not add unasked-for features.
- The agent reads code before editing code.
- The agent distinguishes between exploration, planning, implementation, and verification.
- The final answer states what was actually verified and what remains unproven.
- Risky actions are treated as pauses, not shortcuts.

## Bootstrap checks

For `scripts/bootstrap_project.py`, validate:

1. `link` mode
- creates `<repo>/.codex/skills/agent-operating-model` as a symlink
- writes `CLAW.md` by default

2. `copy` mode
- copies the skill directory into the repo
- can write `.claw/instructions.md`

3. inferred checks
- if no `--check` flags are provided, the script should populate likely commands when the repo exposes them clearly

4. overwrite protection
- existing targets should stop the script unless `--force` is provided

5. template rendering
- `feature` should emphasize scoped implementation
- `debug` should emphasize evidence and rerunning the failing path
- `review` should emphasize read-only verification and command -> observed result

## Baseline rubric

Score the skill against these criteria:

- Trigger precision: does it activate on the right tasks?
- Instruction efficiency: does `SKILL.md` stay concise while references carry details?
- Practicality: does it help the agent do the work, not just describe philosophy?
- Portability: does it translate cleanly across Codex, OpenClaw, and Claw Code?
- Verifiability: can you observe improved outcomes in concrete tasks?
