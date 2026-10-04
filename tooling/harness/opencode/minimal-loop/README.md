# Minimal loop: executable specs plus guardrails

The lightest workflow that gets from a feature idea to running specs with agents
kept on track. Two commands, the three agents from [../README.md](../README.md), and
deterministic checks doing the enforcement. No plugins, no spec framework.

```
/spec <feature>  →  human reviews examples  →  poe lock-specs  →  /implement  →  poe check
                                                                       ↑ repeat findings: promote-to-guardrail
```

| Piece | Where | Enforces |
|---|---|---|
| Examples as acceptance tests against a DSL | `executable-specs` skill | What "done" means, in runnable form |
| Lock on reviewed specs | python-templates `spec-lock` mix-in | Specs can't be edited to reach green; `lock` refuses examples that already pass |
| The gauntlet | python-templates base plus mix-ins | Everything a tool can judge |
| Spend and runaway limits | Two capped keys and `steps` on each agent | Cost, without prompts |

## Set up

1. Generate the project from python-templates and add the `spec-lock` mix-in.
2. Install skills with `uv run poe sync` in this repo.
3. Copy [commands/](./commands) to `.opencode/commands/` in the project, and the agents
   from [../examples/agents/](../examples/agents).
4. Add to the project's `AGENTS.md`:

   ```markdown
   Features go through /spec then /implement (`executable-specs` skill). Specs in
   tests/acceptance/ are locked once reviewed: never edit one to make it pass; if it
   looks wrong, stop and say why. Work is done when `uv run poe check` passes.
   ```

`/spec` runs on `build` (strong tier) because writing good examples is judgement.
`/implement` does too, delegating searches to `explore` and chores to `cheap`. Neither
runs as a subtask: both need the conversation with you.

## Deliberately not added

- A planner, reviewer or tester agent. The examples are the plan, the gauntlet is the
  review, and the lock keeps the tests honest. Use `code-review` on demand.
- Orchestration plugins and spec frameworks. They add inferential ceremony and tie the
  workflow to one plugin API.
- Allium. [../allium-atdd/BRIEF.md](../allium-atdd/BRIEF.md) is the upgrade path once
  plain examples show their limits (state machines, obligations you keep missing).

The commands are the only opencode-specific part. In Claude Code the same two prompts
go in `.claude/commands/`; the skill, the lock and the gate are unchanged.
