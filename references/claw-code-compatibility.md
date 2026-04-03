# Claw Code compatibility

This note translates the skill into Claw Code's current runtime model.

## What the Claw Code source changes

From `ultraworkers/claw-code`:
- `rust/crates/runtime/src/prompt.rs` loads ancestor instruction files such as `CLAW.md`, `CLAW.local.md`, `.claw/CLAW.md`, and `.claw/instructions.md`.
- The same prompt builder injects git status, git diff, runtime config, and instruction files into the dynamic part of the system prompt.
- `rust/crates/commands/src/lib.rs` lists first-class commands such as `/skills`, `/agents`, `/memory`, `/permissions`, `/config`, and `/ultraplan`.
- `rust/crates/commands/src/lib.rs` also shows Claw can load skills from project `.codex/skills`, user `$CODEX_HOME/skills`, user `~/.codex/skills`, and legacy project `.claw/commands`.
- `rust/crates/tools/src/lib.rs` shows the native tool names the model sees: `read_file`, `write_file`, `edit_file`, `glob_search`, `grep_search`, `Skill`, `Agent`, `TodoWrite`, `ToolSearch`, `WebSearch`, and more.

This means the best way to strengthen the skill for Claw Code is:
- keep the skill itself concise and portable
- add repo-local reinforcement through `CLAW.md` when needed
- speak in Claw-native command and tool names

## Recommended operating pattern in Claw Code

1. Install or place the skill where Claw can find it
- user-wide: `~/.codex/skills/agent-operating-model`
- project-local: `<repo>/.codex/skills/agent-operating-model`

2. Use the skill explicitly for non-trivial work
- `Use $agent-operating-model to implement this feature.`
- `Use $agent-operating-model and stay in explore mode first.`

3. Reinforce project-specific rules with a short `CLAW.md`
- Do not duplicate the whole skill.
- Add only the repo-critical deltas: architecture boundaries, required checks, forbidden shortcuts, deployment constraints.

4. Use Claw's command surface to keep the workflow visible
- `/skills` to confirm discovery
- `/memory` to inspect loaded instruction files
- `/agents` if agent helpers are configured
- `/permissions` before risky work
- `/ultraplan` when planning needs deeper sequencing

## Bootstrap helper

This skill now includes `scripts/bootstrap_project.py` so you do not have to hand-write the repo overlay each time.

Example:

```bash
python3 scripts/bootstrap_project.py \
  --repo /path/to/project \
  --check "pnpm lint" \
  --check "pnpm test"
```

What it does:
- writes a minimal `CLAW.md` or `.claw/instructions.md`
- installs the skill into `<repo>/.codex/skills/agent-operating-model`
- defaults to a symlink for fast local iteration

Useful modes:
- `--install-skill link` keeps the target repo tracking your local working copy
- `--install-skill copy` vendors a standalone snapshot into the target repo
- `--install-skill skip` writes only the repo-local instruction overlay
- `--force` replaces conflicting targets

## Minimal `CLAW.md` pattern

Use this in a target repo when you want Claw Code to reinforce the skill without copying all of it:

```md
# Working rules

- Use $agent-operating-model for non-trivial implementation, debugging, and validation tasks.
- Explore before editing.
- Keep changes tightly scoped.
- Run the required project checks before claiming success:
  - <insert test/build/lint commands>
- Escalate before destructive or externally visible actions.
```

## Tool translation cheat sheet

Skill principle -> Claw-native tool surface

- structured read -> `read_file`
- structured write -> `write_file`
- structured edit -> `edit_file`
- file discovery -> `glob_search`
- content search -> `grep_search`
- explicit skill load -> `Skill`
- helper delegation -> `Agent`
- task tracking -> `TodoWrite`
- capability discovery -> `ToolSearch`

## Practical improvement over the first version

The original skill mainly improved agent behavior in a host-agnostic way.
After reading Claw Code, the stronger version is:
- easier for Claw to discover
- easier to reinforce at repo scope
- easier to operationalize with Claw commands and tool names

That is the biggest real gain from the source review.
