# Python specifics for test-strategy-review

Where each general check from `SKILL.md` shows up in a pytest codebase. Tool choices
follow `practices/guardrails-catalogue.md` in the source repo.

Check what the project already wires up before recommending more. Projects generated from
[python-templates](https://github.com/MarkGravestock/python-templates) have a `poe check`
gauntlet, and the missing pieces usually arrive as its `testing-*` mix-ins (factories,
property, mutation, containers): recommend the mix-in by name rather than hand-rolling it.

## Correctness

| Smell | What to look for | Fix |
|---|---|---|
| Can't fail | `pytest.raises(Exception)` or no `match=`; `assert mock.called` only | Narrow exception type plus `match=`; assert on the outcome |
| Mock drift | `Mock()` / `MagicMock()` without a spec accepts any attribute | `create_autospec(...)` or `spec_set=`; better, an in-memory fake (`cosmic-python`) |
| Patching internals | `mock.patch("pkg.module._helper")` | Inject the dependency; patch only at a boundary |
| Time and randomness | `datetime.now()`, `time.time()`, `random`, `uuid4()` inside logic; `sleep` in tests | Inject a clock or RNG (`cupid-python`, and Controllable clock below) |
| Shared state | `scope="session"` or `"module"` fixtures returning mutable objects | Function scope, or immutable values |
| Order dependence | Passes in file order only | Run with [pytest-randomly](https://github.com/pytest-dev/pytest-randomly) |
| Unseeded generated data | Faker, factory_boy or `random` values differ per run, so failures don't reproduce | pytest-randomly also reseeds `random`, Faker and factory_boy per test and prints the seed |
| Silently skipped | `skipif` on Docker or an env var means CI can go green without running the test | Confirm in the CI log or JUnit XML that integration tests ran on at least one job |
| Tests that assert nothing | Coverage high, confidence low | [mutmut](https://github.com/boxed/mutmut) on changed or risky modules (`testing-mutation` mix-in); read the surviving mutants, not just the score |

## Completeness

- **Property-based**: [Hypothesis](https://github.com/HypothesisWorks/hypothesis) for
  parsers, value objects, round-trips (`decode(encode(x)) == x`), and invariants
  (`testing-property` mix-in). Properties of the domain, not of the standard library.
- **Adapters**: [testcontainers-python](https://github.com/testcontainers/testcontainers-python)
  for databases and brokers, marked `integration` (`testing-containers` mix-in).
- **Contracts and APIs**: Pact-Python or schemathesis, per the guardrails catalogue.
- **CLI entry points**: drive `main(argv)` and assert on exit code plus `capsys` output.
- **Gates**: `coverage` `fail_under` as a tripwire;
  [diff-cover](https://github.com/Bachmann1234/diff_cover) to hold the line on new code.
- **Markers**: `slow` and `integration` are registered and used, and CI runs them
  somewhere, even if the fast local loop deselects them.

## Controllable clock

- Domain code takes `now: Callable[[], datetime]`, defaulting to `lambda: datetime.now(UTC)`
  (the shape `cupid-python` recommends). Tests pass a fake that satisfies the same callable
  shape structurally, so the domain never imports from tests.
- The fake starts at a fixed, timezone-aware instant and moves only when told: `advance()`
  for elapsed time, `set()` for jumps. Refuse naive datetimes.
- Test the boundary exactly: one microsecond before, at, and after.
- Long-running code that also waits: inject the sleep alongside the clock, so the fake can
  advance instead of blocking.
- Third-party code that reads the clock and can't be given one:
  [time-machine](https://github.com/adamchainz/time-machine) (or
  [freezegun](https://github.com/spulec/freezegun)) at that edge only. Patching time
  everywhere hides the missing seam.
- python-templates' `testing-clock` mix-in, where available, provides a ready-made
  `FakeClock` and an example.

## Understandability

- **Names**: `test_<rule in domain words>` (`test_blank_name_is_rejected`). Group by
  behaviour with test classes or modules when a unit has many rules, the pytest
  counterpart of `@Nested` in `java-junit5-testing`.
- **Tables**: `@pytest.mark.parametrize` with `ids=` or `pytest.param(..., id=...)`, so
  each row names its partition.
- **Fixtures**: pytest fixtures for lifecycle (connections, temp dirs, fakes); factories
  for data. Keep `conftest.py` for genuinely shared lifecycle, not one-off data.
- **Object Mother and Builder**: plain factory functions with keyword defaults are often
  enough. For larger models, [factory_boy](https://github.com/FactoryBoy/factory_boy)
  (`testing-factories` mix-in) maps directly: the `Factory` is the builder, subclasses and
  `Trait`s are the named Object Mother variants, `SubFactory` builds aggregates, and
  [Faker](https://github.com/joke2k/faker) fills values the test doesn't care about.
  Override in the test the value the rule depends on, never assert on a faked value, and
  seed so failures reproduce.
- **Assertions**: plain `assert` (pytest rewrites them); extract a domain assertion helper
  when the same multi-line check recurs.
- **Lint**: Ruff's `PT` (flake8-pytest-style) rules catch many structural smells mechanically.
