---
name: test-strategy-review
description: Review a codebase's tests and testing strategy for gaps, correctness and understandability. Stack-neutral meta-skill that sits above the stack testing skills (pytest, JUnit 5, Kotest, Spock). Use when asked "what tests are we missing", "is our testing strategy any good", "review these tests", "can we trust this suite", before relying on agent-written tests, or when a bug got through a green build. Python specifics are in python.md beside this file.
---

# Test strategy review

Answers three questions, in priority order:

1. **Correct** — does each test actually verify the behaviour it claims to? A test that
   cannot fail is worse than no test: it buys false confidence.
2. **Complete** — does the suite as a whole cover the risks that matter, at the right level?
3. **Understandable** — can a reader tell what rule each test protects, and why it failed?

This is the testing counterpart of `simple-design`: it judges and routes, it doesn't
prescribe syntax. For *how to write* the tests it recommends, hand off:

| Need | Skill |
|---|---|
| Edge cases for one module | `bug-magnet` |
| Python / pytest idioms | `python.md` (this directory) |
| Java, Kotlin, Groovy idioms | `java-junit5-testing`, `kotlin-kotest-testing`, `groovy-spock-testing` |
| Test levels for a layered Python service | `cosmic-python` |
| Deterministic tooling (mutation, coverage, property tests) | `practices/guardrails-catalogue.md` in the source repo |
| Key examples from the problem space | `problem-lenses` (specification by example) |

Vocabulary: Kent Beck's [Test Desiderata](https://testdesiderata.com/). Properties trade
off against each other; name the trade-off rather than pretending all twelve are achievable.

## Procedure

1. **Map the risk first, then the tests.** What would hurt if it broke: money, data loss,
   security, a contract other teams depend on, the core domain rule? List the top risks
   before opening a test file, so you review against risk rather than against coverage.
2. **Inventory the suite.** For each test location: level (domain unit / use-case with
   fakes / adapter integration / contract / end-to-end), kind (example, table,
   property, characterisation), runtime, and what runs in CI on every push.
3. **Check correctness** on a sample weighted towards the top risks (checklist below).
   Where a mutation tool is available, run it on the risky modules: surviving mutants are
   evidence, opinion is not.
4. **Check completeness** against the risk list (checklist below).
5. **Check understandability** on the same sample.
6. **Report** in the format at the end. Recommend the smallest change that closes each gap.

## Correctness — tests that lie

- **Cannot fail**: no assertion; asserting on a value the test itself set up; asserting
  a mock was called with what the test told it to return; `try`/`except` that swallows the
  failure; an exception check broad enough to catch the wrong error.
- **Oracle copied from the implementation**: the expected value is computed with the same
  logic as production code. Prefer literal expected values or independent properties.
- **Tests structure, not behaviour**: breaks on a refactor that changes nothing observable
  (Beck: *structure-insensitive*), or asserts private state. Test through the public
  interface the caller uses.
- **Over-mocked**: the unit under test is surrounded by mocks so only wiring is verified.
  Prefer real collaborators or in-memory fakes and mock only at architectural boundaries.
  Don't mock types you don't own (Freeman and Pryce, *Growing Object-Oriented Software*):
  wrap them and test the wrapper against the real thing.
- **Non-deterministic**: wall-clock time, randomness, ordering, network, shared mutable
  fixtures, sleeps. Flaky tests are a correctness defect, not an infrastructure one.
- **Order-dependent**: passes alone, fails in a different order (or the reverse).
- **Silently skipped**: a skip condition (missing Docker, env var, platform) means CI can
  pass without running it. A test that never runs in CI counts as missing.
- **Wrong side of the boundary**: only the happy path; boundaries tested on one side; error
  paths asserted only as "raises something".
- **Parametrised padding**: table rows that exercise the same partition; each row should
  sit in a different equivalence class or on a boundary.

## Completeness — strategy gaps

Shape the suite like the [practical test pyramid](https://martinfowler.com/articles/practical-test-pyramid.html):
many fast, isolated tests; fewer integration tests; a handful end-to-end. Then check:

- **Each top risk has at least one test that would fail if it broke**, at the cheapest
  level that can detect it.
- **Domain rules** are tested without I/O.
- **Use cases / service layer** are tested with fakes for persistence and external calls.
- **Every adapter** (DB, queue, HTTP client, file format) has an integration test against
  the real thing or a faithful container, not a mock of itself.
- **Contracts** with other services are checked by a contract or schema test, not by
  hoping both sides agree.
- **Wide input spaces** (parsers, money, dates, serialisation round-trips) have
  property-based tests, not just examples.
- **Legacy or untested code** about to change has characterisation tests first.
- **Non-functional risks** that actually matter here (performance, concurrency,
  resilience, security) have at least one targeted check. Skip the ones that don't.
- **Regression**: every escaped bug got a test that failed before the fix.
- **Feedback loop**: the fast suite is fast enough to run on every save; slow tests are
  marked and run in CI rather than skipped.
- **Gates are deterministic**: coverage is a tripwire, not a target; mutation score on
  changed code is the stronger signal that tests assert something.

Don't recommend levels the system doesn't need. A CLI with no I/O doesn't need contract
tests. `simple-design` rule 4 applies to suites too.

## Understandability — tests as specification

- **Name states the rule**, in domain language, so a failing test name alone says what
  broke ("rejects a hold when the patron is at the limit", not `test_hold_2`).
- **One behaviour per test**; several asserts are fine if they describe one outcome.
- **Given / when / then is visible**, by blocks, blank lines or nesting. Setup that varies
  between tests is in the test, not hidden in a distant shared fixture.
- **Relevant detail shown, irrelevant detail hidden**: Object Mother plus Test Data
  Builder (or the stack equivalent) supplies defaults; the test states only what matters
  to this rule.
- **No logic in tests**: no loops or conditionals deciding what to assert. Use a table.
- **Assertions read in domain terms** and fail with a message that explains the cause
  (Beck: *specific*).
- **Layout mirrors the code** so the test for a unit is findable.

## Report format

```
## Summary
<2–4 lines: overall trust in the suite, the biggest gap, the first thing to do>

## Risks vs coverage
| Risk | Covered by | Level | Gap |

## Findings
### Correctness | Completeness | Understandability
- [high|medium|low] <finding> — <file:line evidence> — <smallest fix> — <skill to use>

## What's working
<keep it short; name the practices to preserve>
```

Severity: **high** = a top risk is untested or a test can't fail; **medium** = a gap or a
flaky/structure-sensitive test on important code; **low** = readability.
