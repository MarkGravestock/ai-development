---
name: executable-specs
description: Lightest spec-first loop for agent work - write the feature as failing example tests against a small DSL, have a human review and lock them, then implement until the gate is green without touching the locked specs. Use when starting a feature or behaviour change, when asked to "spec this", "write acceptance tests first", "implement against the spec", or when a /spec or /implement command invokes it. Pairs with python-templates' spec-lock mix-in.
---

# Executable specs

The spec is a set of examples that run. No separate spec document, no spec
framework. Two phases, with a human review and a deterministic lock between
them. Background: `practices/delivery-process.md` (thin slices) and
`tooling/approach.md` (computational over inferential) in the source repo.

## Phase 1: spec

1. Restate the feature as rules in the domain's words, and list open questions.
   Ask the human about anything ambiguous; don't resolve it silently.
2. For each rule, write examples in `tests/acceptance/`: one test per example,
   Given / When / Then, names stating the rule. Cover each rule's boundary and
   at least one failure path. Use `bug-magnet` for edge cases on risky rules.
3. Write the examples against the DSL (`tests/acceptance/dsl.py`): extend its
   vocabulary only as far as the examples need. Specs never touch HTTP, the
   database or internals; drivers in `tests/drivers/` do.
4. Run them. **Every new example must fail**, for the reason you expect (missing
   behaviour, not an import or typo error). An example that passes already is
   vacuous or already covered: fix or drop it.
5. Stop. Show the human the examples and the open questions. The human locks
   them (`uv run poe lock-specs`); never run the lock yourself.

## Phase 2: implement

1. Make the locked examples pass by changing production code and drivers.
   `tests/acceptance/` (apart from `conftest.py` wiring) is read-only: the gate
   fails if a locked spec changes.
2. Keep the inner loop fast: run the acceptance file, then unit tests for what you
   touched. Add unit tests for logic the examples don't pin down.
3. Finish only when the full gate passes (`uv run poe check`).
4. If an example looks wrong, stop and say why. The fix is a reviewed spec change
   and re-lock by the human, not an edit to make it pass.

## Rules

- One thin slice per spec: the smallest set of examples that proves the next
  assumption (walking skeleton first).
- Time-dependent rules use an injected clock (`test-strategy-review` python.md).
- A problem that recurs across slices goes to `promote-to-guardrail`.
- Use `explore` (cheap tier) for codebase searching in both phases.
