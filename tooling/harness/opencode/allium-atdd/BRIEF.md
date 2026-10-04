# Brief: Allium + ATDD workflow for opencode (Flask spike)

Status: spike, not yet run. Outcome goes in `RETRO.md` beside this file.

You are setting up a lightweight spec-driven workflow in an existing Flask
repository and proving it on one feature. Read this whole brief before
touching anything. Where it says *ask*, stop and ask; do not guess.

## Why

Markdown specs for agents (spec-kit, Kiro, OpenSpec) are inferential
feedforward, the weakest quadrant in [tooling/approach.md](../../../approach.md):
an agent can ignore them and nobody notices until review. Two sources move
the check into the computational quadrants:

- **Allium** ([juxt/allium](https://github.com/juxt/allium)) makes the spec
  checkable: entities, `when/requires/ensures` rules, transition graphs and
  `open question` markers in a `.allium` file, validated by a CLI that also
  emits a list of test obligations (`allium plan`).
- **Optivem's ATDD** ([article](https://journal.optivem.com/p/spec-driven-development-make-specs))
  makes the tests honest: a four-layer test architecture (acceptance test →
  DSL → system driver → external-system driver), Red confirmed before Green,
  and every step a small reviewed commit.

We want the combination, not the full Allium plugin. Allium supplies the spec
and the obligation list; Optivem supplies the shape of the tests and the
commit cadence; opencode runs it. The CLI check and the failing-then-passing
tests are the guardrails; the four commands are the minimum prompt needed to
sequence them.

## Goal

By the end there should be, on a branch, with one commit per step:

1. A `.opencode/` directory containing the workflow (see *Deliverables*).
2. One `.allium` spec for one feature, passing `allium check`.
3. Acceptance tests generated from that spec in the four-layer shape,
   shown failing, then passing after implementation.
4. A short `AGENTS.md` section describing the loop for future sessions.

Keep it small. The point is to learn whether the loop is worth keeping, not
to build a framework.

## The repository

- Flask application. Discover the structure yourself; do not assume a layout.
- Python tooling is in transition between **uv** and **poetry**. Before
  running anything, work out which one is canonical today (lockfile present,
  CI uses it, README says so) and use only that one. If it is unclear,
  *ask*. Do not add a second tool or lockfile.
- Use the existing test runner and conventions (almost certainly pytest).
  Put new acceptance tests where the project's tests already live, under an
  `acceptance/` subdirectory unless a convention already exists.
- Check whether the code has an injectable clock or time seam before writing
  any temporal rule. If not, say so in the spec's open questions rather than
  testing with sleeps or by racing the wall clock.

## Prerequisites

- `allium` CLI on PATH (`brew tap juxt/allium && brew install allium`, or
  `cargo install allium-cli`, or a binary from
  [allium-tools releases](https://github.com/juxt/allium-tools/releases)).
  If it is missing, *ask* before continuing; the loop depends on `check` and
  `plan`.
- Read, in this order, from the Allium repo (raw GitHub, not the docs site):
  `skills/allium/references/recommended-loops.md`,
  `skills/propagate/SKILL.md`,
  `skills/distill/references/worked-examples.md` (Example 1 is Flask),
  and skim `skills/allium/references/language-reference.md` for the sections
  on entities, rules, transition graphs, invariants, config, open questions
  and surfaces.
- Read opencode's docs for commands, agents, skills and plugins from
  `packages/web/src/content/docs/` in [sst/opencode](https://github.com/sst/opencode)
  if the hosted docs are unreachable.

## Deliverables

### `.opencode/commands/`

Four Markdown commands. Each has a `description` and runs as a subagent
(`subtask: true`) so Allium syntax stays out of the main context.

| Command | Does | Stops when |
|---|---|---|
| `/spec <feature>` | Elicit (or `tend`) `specs/<feature>.allium`; run `allium check` and `allium analyse`; list open questions | Spec is clean and every open question has been put to the human |
| `/tests` | Run `allium plan`; map each obligation to a pytest test in the four-layer shape; commit each layer separately; run the suite and confirm the new tests **fail** | Every obligation is covered or reported uncovered with a reason; all new tests are red |
| `/implement` | Make the failing tests pass. May not edit anything under the acceptance test directory | Suite green |
| `/check` | Run tests, `allium check`, and a drift pass comparing each rule's `requires`/`ensures` to the code that implements it; print `N obligations, M covered, K uncovered` and any divergence | Always; it reports |

### `.opencode/skills/atdd-layers/SKILL.md`

Project-local conventions for the four layers, written for this repo once
you have seen it: package paths, naming, which driver each surface uses, how
fixtures are shared. Keep it under a page. Include a minimal example of each
layer in pytest:

- acceptance test: calls the DSL only, asserts on returned results, no HTTP,
  no selectors, no fixtures beyond the DSL;
- DSL: builder-style methods (`shop.place_order(quantity=5)`), returns plain
  result objects, no assertions;
- system driver: the Flask test client or `httpx`, behind a small protocol so
  a UI driver could replace it;
- external-system driver: `responses`/`respx` stubs or a fake class, also
  behind a protocol. If the feature has no external dependency, leave this
  layer as a documented placeholder rather than inventing one.

Use Hypothesis `RuleBasedStateMachine` for any entity with a transition graph,
one rule per edge; skip property tests otherwise.

### `.opencode/plugins/allium-check.ts`

A plugin that, on the `file.edited` event for `*.allium`, runs
`allium check <file>` and feeds the output back. Nothing else.

### `AGENTS.md`

Add a section of at most two paragraphs: the spec under `specs/` is
canonical; run the four commands in order; never weaken or edit a generated
acceptance test to make it pass, fix the spec and regenerate; escalate open
questions rather than resolving them silently. Link to this brief rather than
repeating it.

## Process

1. Explore the repo. Pick **one** feature for the spike. Prefer something with
   a small state machine (two to four states) and at most one external
   dependency. Propose it and *ask* before proceeding.
2. Write the workflow files above. Commit: `Add Allium/ATDD opencode workflow`.
3. Run `/spec`. Resolve open questions with the human. Commit the spec.
4. Run `/tests`. Four commits: acceptance tests, DSL, external driver (if
   any), system driver. Show the failing test output in the last commit
   message body.
5. Run `/implement`. Commit. Show the passing output.
6. Run `/check`. If it finds drift, fix the code (or, if the spec was wrong,
   `/spec` again and regenerate). Commit.
7. Write a short `RETRO.md` next to the spec: what the loop caught that a
   Markdown spec wouldn't have, where Allium or the four layers got in the
   way, and whether you'd keep each of the four commands. Be blunt.

## Guardrails

- Never edit a generated acceptance test to make it pass. If a test looks
  wrong, the spec is wrong: change the spec, regenerate.
- A new acceptance test that passes before any implementation is a defect
  (already covered, or vacuous). Resolve it before implementing.
- No magic numbers in code for anything the spec puts in `config`.
- Do not widen the spike: one feature, one spec, no refactors of unrelated
  code, no new dependencies beyond Hypothesis and an HTTP stubbing library if
  one is not already present.
- Stop and ask after 6 loop iterations or 2 iterations with no change in
  test counts or open questions.
- Do not install the Allium plugin or skills wholesale. We are deliberately
  using only the CLI and our own four commands.

## Report back

Finish with: the branch name, the commit list, the final
`N obligations, M covered, K uncovered` line, the open questions you had to
ask, and a link to `RETRO.md`.
