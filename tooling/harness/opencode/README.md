# opencode: two-tier setup on OpenRouter

A cheap tier for token-heavy read-only work, a strong tier for everything that needs
judgement, and the spend cap enforced outside the harness.

Applies principles 1, 3 and 4 from [../README.md](../README.md). Setup takes about an
evening. No plugins.

Model choices live in [models.md](./models.md). Working examples in
[examples/](./examples). The lightest spec-driven loop (examples as tests, locked once reviewed, two commands)
is in [minimal-loop/](./minimal-loop/README.md). A heavier spike (Allium spec plus
four-layer ATDD tests, four commands) is in [allium-atdd/BRIEF.md](./allium-atdd/BRIEF.md).

## Step 1 — Two OpenRouter keys

Create two keys in the OpenRouter dashboard, each with a credit limit, a daily reset, and a
guardrail restricting it to an allowlist of models.

| Key | Allowlist | Starting cap |
| --- | --- | --- |
| `or-cheap` | cheap tier only | £3/day |
| `or-heavy` | strong tier only | £5/day |

This is the enforcement point. An over-budget or off-allowlist request is rejected before it
reaches the provider, so it costs nothing and no prompt can route around it. The daily reset
matters more than the amount: a runaway loop costs one day's cap and then stops.

Note all keys draw on one account balance. Per-key limits cap each key; they don't reserve
funds. Keep enough credit on the account to cover both.

Reference: [per-key limits](https://openrouter.ai/docs/api_reference/limits),
[spend controls](https://openrouter.ai/blog/tutorials/team-spend-controls-setup/).

For provisioning beyond a couple of keys, see the
[Management API](https://openrouter.ai/docs/guides/overview/auth/management-api-keys) —
a separate credential that manages keys and cannot make inference calls. Not needed for two.

```bash
export OPENROUTER_CHEAP_KEY=sk-or-...
export OPENROUTER_HEAVY_KEY=sk-or-...
```

To check burn without opening the dashboard, `GET /api/v1/key` with the key itself returns
its own limit, reset and remaining balance.

## Step 2 — Two providers

Same endpoint, two keys. This is what makes the tier boundary real rather than conventional:
the cheap agent physically cannot bill the strong tier.

See [examples/opencode.jsonc](./examples/opencode.jsonc).

Each model entry needs `capabilities` and `limit` declared. opencode applies defaults for
custom models but can't infer a server's real context window or tool support. Field names and
shape: [Models](https://opencode.ai/v2/docs/models).

The docs have forked into [V1](https://opencode.ai/docs/) and
[V2](https://opencode.ai/v2/docs). Everything here is V2. Most third-party writeups are V1,
where the config uses `agent` singular and a `permission` object rather than an array, and
declares `tool_call` and `reasoning` flat on the model instead of inside `capabilities`.

## Step 3 — Three agents

In `~/.config/opencode/agents/`, or `.opencode/agents/` to scope to a project. See
[examples/agents/](./examples/agents).

**`explore`** overrides the built-in read-only agent onto the cheap tier. This is where the
token volume sits, so it's most of the saving, and it can't do damage because its tool set is
already read-only.

**`cheap`** is a primary agent for mechanical work: renames, test scaffolding, docs, config
edits. It's the `Tab` target.

**`build`** stays on the strong tier as the default. It coordinates, judges what comes back
from subagents, and does the edits when it doesn't delegate. A cheap model here is a false
economy: it runs on every message and its mistakes are the expensive kind.

Set `steps` on every agent. On the final allowed step opencode drops the tools and asks for a
summary, which is the one runaway brake that lives in config rather than in a prompt.

Also worth knowing: a subagent runs with its own permissions, not a restricted copy of its
parent's. A locked-down orchestrator can dispatch to something with wider access.

## Step 4 — One line of prompt

In `AGENTS.md`:

```markdown
Before implementing, delegate codebase exploration to @explore.
```

The only instruction here a model can ignore, and the cost of it being ignored is "slightly
more expensive", not "wrong". Everything load-bearing is enforced elsewhere. Per principle 1,
that's the test for whether a prompt instruction is acceptable.

## Using it

- Sessions start in `build` on the strong tier.
- `Tab` / `Shift+Tab` cycles to `cheap` when you know the task is mechanical.
- `@explore find where X is configured` sends a read-only sweep to the cheap tier.

Escalation is a keystroke rather than a model's judgement. You know whether the task is hard.

## Review after a month

Look at the split between the two keys in the OpenRouter activity dashboard.

- `or-cheap` barely used — the delegation line isn't working, or you aren't reaching for
  `Tab`. Fix the habit before adding machinery.
- `or-heavy` at its cap daily — either the cap is unrealistic or something specific is
  burning tokens. Find out which before raising it.
- Neither near its cap — this was over-thought. Collapse to one tier.

## Deliberately not doing

**A classifier that picks a model per prompt.** The `chat.model` hook doesn't exist
([#18793](https://github.com/anomalyco/opencode/issues/18793) is open), so it would be built
on `chat.params`, which isn't designed for it. Worse, a one-line prompt can mean a one-file
change or a three-module refactor, so a misfiring classifier hands the hardest task to the
cheapest model. The subagent boundary is a better signal because the work has already been
scoped by then.

**[opencode-model-router](https://github.com/marco-jardim/opencode-model-router).** Worth
reading, particularly its use of `tool.execute.after` to append a call-count banner inside
tool results, where a model can't ignore it the way it ignores a system prompt. That's a good
illustration of principle 1. But it's GPL-3.0, thinly maintained, and its tier presets name
specific models, so it fails principle 4.

**A cheap coordinator.** See Step 3.

## What survives

Portable across harnesses: the two-key spend cap (it's OpenRouter's, not opencode's), the
agent-per-role structure, the skills bundle.

Not portable: model IDs, plugin APIs, config field names. All isolated in
[models.md](./models.md) and [examples/](./examples).
