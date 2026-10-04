# Growing the guardrails

The gauntlet should grow from evidence, not up front. When the same problem turns up a
second time, in review, in an agent's output, against a spec or as an escaped bug, it stops
being a review comment and becomes a candidate rule. Each rule closes off one recurring
mistake for good, at no inference cost, and the set only gets tighter.

## The loop

1. **Spot the repeat.** Second occurrence, not first: one-offs don't earn a rule. Tag the
   finding where it happened (a `guardrail-candidate` issue label is enough) so the second
   one is noticed.
2. **Remove before you detect.** Can a type, a library or generated code make the mistake
   impossible? `NewType`, `Literal` and `Protocol` signatures, a sanctioned client
   ([dependencies.md](dependencies.md)) or codegen from a spec all beat a rule that
   catches it afterwards.
3. **Pick the cheapest tool that can express it** (ladder below). Config beats a pattern
   rule; a pattern rule beats a plugin.
4. **Write the rule test first**: one snippet that must be flagged, one that must not.
   A rule without tests becomes noise or silence the first time someone refactors it.
5. **Make the message the fix.** Agents act on the error text, so say what to do instead and
   point at the sanctioned path, not just what is wrong.
6. **Gate it in `poe check`**, never as a warning. For existing violations, suppress each
   with an inline reason and let the count only fall; never relax the rule to reach green.
7. **Retire** rules made redundant by a type, a library or a built-in lint rule.

## The ladder (Python)

| Shape of the problem | Tool | Cost to add |
|---|---|---|
| "Never import or call X" | Ruff `banned-api` (rule `TID251`), message per entry | Config |
| "Layer A must not depend on B" | import-linter contracts (layers, forbidden, independence) | Config |
| Syntactic pattern in some paths ("no wall clock in `domain/`", "`httpx` calls need `timeout=`") | [ast-grep](https://ast-grep.github.io/guide/project/lint-rule) YAML rule, tests via `ast-grep test` | One YAML file plus tests |
| Data-flow or security pattern ("user input reaches SQL") | Semgrep CE, or [Opengrep](https://github.com/opengrep/opengrep) for cross-function taint | YAML; rule tests via annotated fixtures |
| Needs Python logic, scope awareness or an autofix | [Fixit](https://fixit.readthedocs.io/) local rule (LibCST), valid and invalid examples built in | A Python class |
| A property of the codebase as a whole | A pytest test that walks modules or uses `ast` | A test |
| Structured specs and config | JSON Schema via check-jsonschema | Schema |
| Prose specs and guidelines (terms, banned phrasing) | [Vale](https://vale.sh/) style rules | YAML |

Ruff has no custom-rule API ([astral-sh/ruff#283](https://github.com/astral-sh/ruff/issues/283)),
and pyright has no plugins, so custom rules sit beside them, not inside them. flake8 plugins
are a dead end once Ruff replaces flake8.

**Default to ast-grep** for anything beyond config. It's a single binary with YAML rules and
a built-in test runner. It also covers Java, so one rule style serves both stacks. Escalate
to Opengrep or Semgrep for taint analysis, and to Fixit only when the rule needs real
Python.

## Example

The second time domain code read the wall clock (see `test-strategy-review`), it became:

```yaml
# rules/no-wall-clock-in-domain.yml
id: no-wall-clock-in-domain
language: python
severity: error
message: Domain code must not read the wall clock.
note: "Take `now: Callable[[], datetime]` as a parameter and pass a FakeClock in tests."
files: ["src/*/domain/**/*.py"]
rule:
  any:
    - pattern: datetime.now($$$)
    - pattern: datetime.utcnow()
    - pattern: time.time()
```

```yaml
# rule-tests/no-wall-clock-in-domain-test.yml
id: no-wall-clock-in-domain
valid:
  - "expires = now() + ttl"
invalid:
  - "expires = datetime.now(UTC) + ttl"
  - "started = time.time()"
```

`ast-grep test` checks the rule; `ast-grep scan` exits non-zero on a hit, so it slots into
`poe check` as one more step.

## Java equivalents

Same ladder: banned APIs via forbidden-apis signature files or Checkstyle `IllegalImport`, layers via ArchUnit,
patterns via ast-grep or PMD XPath rules, logic via a custom Error Prone `BugPattern`.
