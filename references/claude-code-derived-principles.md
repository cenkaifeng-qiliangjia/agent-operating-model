# Claude-Code-derived principles

This reference distills the portable lessons from the PDF analysis of Claude Code's recovered source structure. The goal is not to copy Anthropic's product surface. The goal is to import the behaviors that reliably improve agent quality in Codex/OpenClaw.

## Core idea

Claude Code appears strong because it behaves like an operating model, not a single prompt.

Portable pillars:
- Prompt architecture, not prompt sprawl
- Explicit behavior rules, not improvised taste
- Tool governance, not raw function calling
- Context budgeting, not unlimited transcript growth
- Role separation, not one blurred mega-agent
- Verification as an adversarial activity, not a polite rubber stamp

## What ports cleanly into a skill

These patterns survive translation into Codex/OpenClaw:

1. Task contract first
- Define objective, non-goals, constraints, and definition of done before editing.

2. Execution discipline
- Do not add unasked-for features.
- Do not over-abstract simple code.
- Read before editing.
- Report truthfully about what was and was not verified.

3. Context as a budget
- Keep reusable rules stable.
- Load heavy context only when needed.
- Summarize findings instead of dragging raw output forward.

4. Tool grammar
- Prefer the most semantic tool available.
- Use shell for shell-shaped work, not as the universal hammer.
- Parallelize independent reads and checks.

5. Role separation
- Split work into explore, plan, implement, and verify.
- If subagents exist, specialize them.
- If they do not, simulate specialization as sequential modes in one thread.

6. Adversarial verification
- Try to break the result.
- Run checks that match the surface area that changed.
- Record command and observed result.

## What does not port directly

Some Claude Code strengths live in runtime code, not in instructions alone:

- Prompt cache boundaries
- Hook-enforced permission control
- Automatic input validation layers
- MCP instruction injection
- Transcript, telemetry, and cleanup infrastructure
- Background task lifecycle management

A skill cannot recreate these systems. It can only emulate their intent:
- Keep stable rules stable
- Pause before risky actions
- Validate inputs mentally before running commands
- Separate noisy side work from the main thread
- Treat verification and reporting as explicit phases

## Translation matrix

Claude concept -> Skill-level translation

- Dynamic system prompt assembly -> Keep a stable core loop and inject only task-local context in the live plan
- Prompt cache boundary -> Avoid repeating long reusable guidance; summarize and reference instead
- Explore agent -> Use a read-only discovery pass
- Plan agent -> Produce a step sequence and critical files before edits
- Verification agent -> Run a dedicated break-it pass with an explicit verdict
- Skill workflow packaging -> Load this skill and its references only when the task needs stricter operating rules
- Tool runtime governance -> Perform a manual preflight, then execute, then verify

## Why this matters

The PDF's biggest lesson is that Claude Code does not leave "good behavior" to chance. It writes those habits into the system.

That is the point of this skill:
- institutionalize useful habits
- reduce behavior drift
- improve trustworthiness on non-trivial engineering work

Use this reference when you need the rationale behind a rule in `SKILL.md`.
