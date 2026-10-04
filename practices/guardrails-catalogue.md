# Guardrails catalogue

Computational controls only. **Feedforward** constrains generation;
**feedback** verifies output. Tool choices below are current defaults, not
commitments — check the bundles for what is actually wired up.

| Category | Type | Java | Python |
|---|---|---|---|
| Formatting (auto-fix) | Feedforward | Spotless, google-java-format | Ruff format |
| Linting | Feedback | Error Prone, PMD, Checkstyle, SpotBugs | Ruff, Pylint |
| Static typing | Feedback | javac; NullAway or Checker Framework for nullness | mypy strict, Pyright |
| Runtime contracts | Feedback | Objects.requireNonNull, Bean Validation | Pydantic, beartype, icontract |
| Architecture rules | Feedback | ArchUnit, Spring Modulith verify() | import-linter, Tach |
| API compatibility | Feedback | japicmp, Revapi | griffe, mypy stubtest |
| Contract testing | Feedback | Pact-JVM, Spring Cloud Contract | Pact-Python, schemathesis |
| Property-based testing | Feedback | jqwik | Hypothesis |
| Mutation testing | Feedback | PIT, incremental mode | mutmut, cosmic-ray |
| Coverage gates | Feedback | JaCoCo violationRules | coverage.py fail_under, diff-cover |
| Custom rules (grown from repeat findings) | Feedback | forbidden-apis, ArchUnit, PMD XPath, Error Prone BugPattern | Ruff banned-api, ast-grep, Opengrep/Semgrep, Fixit |
| Complexity budgets | Feedback | PMD cyclomatic rules | Ruff mccabe, xenon |
| Dead code | Feedback | unused-deps reports, Qodana | vulture, deptry |
| Security SAST | Feedback | SpotBugs + FindSecBugs, Semgrep | Bandit, Semgrep |
| Secrets scanning | Feedback | gitleaks (language-agnostic) | gitleaks |
| Schema and config | Feedforward | Flyway/Liquibase validate, @ConfigurationProperties validation | Pydantic Settings, check-jsonschema |
| Codegen from spec | Feedforward | OpenAPI Generator, Avro, Protobuf | datamodel-code-generator, Protobuf |
| Commit gates | Feedback | pre-commit, commitlint | pre-commit |
| Build hermeticity | Feedforward | Gradle config cache, dependency locking | uv lockfiles, tox/nox pinned envs |
| Sandboxing | Feedforward | Devcontainers, read-only mounts, egress limits | Same |

Dependency and supply-chain controls: see [dependencies.md](dependencies.md).
Adding rules as problems recur: see [growing-guardrails.md](growing-guardrails.md).

## Highest leverage for agentic work

Auto-fix formatters give the best return per hour spent: run one as a hook
rather than a check and style drift becomes impossible rather than merely
reviewable.

Mutation testing catches what coverage cannot. Agents readily produce tests
that assert nothing, and only PIT or mutmut will notice; gate it on changed
files to keep the cost tolerable.

Python has no compiler enforcing structure, so import-linter's declared layer
contracts are the only thing standing between an agent and architectural
drift. Set them up before the first agent session, not after.

Codegen from spec turns hallucinated APIs into compile or type errors:
generating DTOs and clients from OpenAPI or Avro converts an inferential
failure mode into a computational one.

## Stack asymmetry

Java gets a great deal free from the compiler, so marginal effort goes on
architecture and semantics: ArchUnit, PIT, japicmp. Python starts with nothing
deterministic, so strict typing plus Ruff plus import-linter is the floor
before anything else is worth adding.
