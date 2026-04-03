# Delegation and verification prompts

Use these templates when the task benefits from explicit specialization or a stronger validation contract.

## Fresh-agent brief

Use for a helper that does not inherit the current context.

```text
Goal:
Why it matters:
Scope:
Relevant files or artifacts:
Constraints:
Non-goals:
Already ruled out:
Allowed actions:
Expected output:
```

Guidance:
- Include enough context for independent judgment.
- Include exact files, functions, commands, or failure modes whenever possible.
- Do not ask the helper to rediscover the task definition.

## Fork-like brief

Use for a helper that benefits from inheriting current context.

```text
Continue from the current context and focus only on:
- Task:
- Deliverable:
- Constraints:
- Do not:
```

Good fits:
- Read-heavy exploration
- Noisy intermediate analysis
- Parallel investigation that should not pollute the main thread

Bad fits:
- Vague "see what you find"
- Tasks whose output is the decision itself instead of supporting evidence

## Explore brief

```text
Map the relevant code paths for <problem>.
Stay read-only.
Return:
- key files
- current behavior
- likely change points
- open questions
```

## Plan brief

```text
Stay read-only.
Produce a step-by-step implementation plan for <goal>.
Include:
- affected files
- edge cases
- risks
- critical files for implementation
```

## Verification brief

```text
Assume the implementation may be wrong.
Try to break <change>.
Run the most relevant checks.
Return:
- checks run
- command and observed result for each check
- edge-case probes
- VERDICT: PASS, FAIL, or PARTIAL
```

## Verification matrix

Change type -> Minimum evidence

- Frontend -> browser behavior, broken assets, console or network errors, key user flow
- Backend or API -> real request and response, status code, error path when relevant
- CLI -> stdout, stderr, exit code
- Refactor -> unchanged public behavior and touched call sites
- Data or migration -> forward path, rollback path, assumptions about existing data

## Final report skeleton

```text
Outcome:
What changed:
Checks:
- <command> -> <observed result>
Adversarial probe:
- <probe> -> <observed result>
Open risks:
VERDICT: PASS | FAIL | PARTIAL
```

Use this reference when you need tighter prompt wording than the main `SKILL.md` provides.
