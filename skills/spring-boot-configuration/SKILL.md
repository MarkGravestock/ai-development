---
name: spring-boot-configuration
description: Use when adding or reviewing Spring Boot configuration - application.yaml/properties, @ConfigurationProperties, @Value, profiles, environment variables, ConfigMaps, secrets, Spring Cloud Config - or when config is wrong at runtime rather than at startup, a property silently binds to a default, or you need to know which property source won. Covers where each value belongs, type-safe binding, startup validation, precedence, and the deterministic checks that replace review comments.
---

# Spring Boot Configuration

## Overview

Four properties make a configuration strategy sound:

1. Configuration is separate from code.
2. The application **fails to start** when required configuration is missing or invalid.
3. Every default can be overridden per deployment, without a rebuild.
4. Secrets come from a secrets manager, never from the repository.

Most Spring Boot config bugs are a failure of (2): the value was missing, `int` bound to
`0`, the app started, and a payment timed out at 3am instead of at boot.

Adapted from [Spring Boot Configuration Management Best Practices](https://blog.jetbrains.com/idea/2026/08/spring-boot-configuration-management-best-practices/) (JetBrains, 2026).

## Start here

| Task | Sections, in order |
|---|---|
| Adding a configuration value | Where each value belongs → Bind with `@ConfigurationProperties` → Fail at startup |
| Reviewing config in a PR or codebase | Review pass (last section) — it starts with a grep, then routes each finding |
| "The env var isn't working" | Environment variables: the name derivation |
| "Which file set this value?" | Precedence: which source wins |
| Standing up a new service | Guardrails first → Where each value belongs → Deployment shapes |
| Config broke in production but not locally | Precedence → Profiles → Secrets |

---

## Guardrails first

Configuration is unusually amenable to deterministic checks. Install these before
reading the rest; prose only covers what they cannot judge.

| Check | Tool | Catches |
|---|---|---|
| Property metadata + IDE completion | `spring-boot-configuration-processor` (annotationProcessor) | Typo'd property names, unknown keys |
| Startup validation | `spring-boot-starter-validation` + `@Validated` on every `@ConfigurationProperties` | Missing/out-of-range values, at boot not at 3am |
| Config contract tests | `ApplicationContextRunner` | Invalid config that *doesn't* fail startup |
| Deprecated/renamed keys on upgrade | `spring-boot-properties-migrator` (temporary runtime dep) | Silently ignored keys after a Boot upgrade |
| Secrets in git | `gitleaks` / `git-secrets` pre-commit + CI | Keys, tokens, connection strings |
| `@Value` sprawl | ArchUnit rule (below) | Config scattered across services |

```java
// ArchUnit: @Value belongs in configuration classes, nowhere else
@ArchTest
static final ArchRule value_annotations_live_in_config =
    noFields().that().areDeclaredInClassesThat().resideOutsideOfPackage("..config..")
        .should().beAnnotatedWith(Value.class)
        .because("bind configuration with @ConfigurationProperties, not scattered @Value");
```

---

## Where each value belongs

| Category | Example | Lives in |
|---|---|---|
| Application defaults | timeouts, retry limits, page sizes, feature defaults | `application.yaml` **inside the jar** |
| Deployment configuration | database hosts, service URLs, queue names, pool sizes | Env vars / ConfigMap, supplied by the platform |
| Secrets | passwords, API keys, certificates, private keys | Secrets manager (Vault, AWS/GCP/Azure), mounted or fetched |
| Behaviour switches | which beans are wired (embedded broker vs real) | Profile |

The first three are the split that matters; the fourth is Spring-specific and is the one
teams most often abuse (see Profiles below).

Defaults ship with the code so the app runs with nothing set. Everything a deployment
changes must be overridable **without a rebuild** — which is exactly what the precedence
ladder below buys you.

```yaml
# application.yaml (in the jar) — safe defaults, no secrets, no env names
myapp:
  payment:
    base-url: https://sandbox.payments.example.com
    connect-timeout: 2s
    max-retries: 3
```

---

## Bind with @ConfigurationProperties, not @Value

`@Value` gives you a `String` typed by hope, no validation, no grouping, no IDE metadata,
and one more class coupled to a property name. Use it only for a genuine one-off
(`@Value("${spring.application.name}")` in a log line).

```java
// ✅ Type-safe, grouped, validated, immutable — records bind by constructor
@ConfigurationProperties("myapp.payment")
@Validated
public record PaymentProperties(
        @NotBlank String baseUrl,
        @NotNull @DurationMin(millis = 100) Duration connectTimeout,
        @NotNull @Min(0) @Max(10) Integer maxRetries,
        @DefaultValue("false") boolean sandbox,
        @NotNull @Valid Circuit circuit) {

    public record Circuit(
            @NotNull @Positive Integer failureThreshold,
            @NotNull Duration resetTimeout) {}
}
```

```java
// ❌ Same config, four ways to get it wrong
@Service
class PaymentClient {
    @Value("${myapp.payment.base-url}") String baseUrl;          // no validation
    @Value("${myapp.payment.connect-timeout:2000}") long timeout; // unit? ms? s?
}
```

Register once, not per class:

```java
@SpringBootApplication
@ConfigurationPropertiesScan      // finds every @ConfigurationProperties record
class Application { }
```

`@EnableConfigurationProperties(PaymentProperties.class)` is the alternative when you want
the binding explicit (and it is what tests use).

**Rules that pay for themselves:**

- Bind to a **record** — immutable, constructor binding, no setters to leave half-populated.
  `@ConstructorBinding` is unnecessary when there is a single constructor.
- Use **domain types**, not `String`/`long`: `Duration` (`2s`, `PT2S`), `DataSize` (`10MB`),
  `URI`, enums, `Period`. Spring binds them; you stop guessing units.
- Nest with `@Valid`, or nested constraints are not evaluated.
- Group by concern (`myapp.payment.*`), not by class.

---

## Fail at startup, not at 3am

`@Validated` on the properties class turns a missing value into a boot failure with the
offending property named. Without it, the annotations are decoration.

```
Binding to target ... failed:
    Property: myapp.payment.base-url
    Value: "null"
    Reason: must not be blank
```

Validation only runs if `spring-boot-starter-validation` is on the classpath. Without it
the annotations bind and do nothing — no error, no warning.

**Use wrapper types when absence must be distinguished from a Java default.** A missing
value binds `int` to `0` and `boolean` to `false`, and whether that is caught depends on
whether your range excludes the default:

```java
@NotNull @Min(0) Integer maxRetries   // ✅ missing → startup failure
@Min(1) @Max(5) int retries           // ✅ missing → 0, which fails @Min(1)
@Min(0) int maxRetries                // ❌ missing → silently 0, and 0 is legal
boolean sandbox                       // ❌ missing → silently false, indistinguishable
```

So the primitive is safe only when the valid range excludes `0` (or `false`). When zero is
a legitimate value, the type has to carry the absence — `Integer` + `@NotNull`.

Intentional defaults are explicit, not implicit:

```java
@DefaultValue("3") @Min(0) @Max(10) int maxRetries   // ✅ 3 when unset, and it's readable
```

Cross-field rules that no single constraint expresses go in `@AssertTrue`:

```java
@AssertTrue(message = "read-timeout must be at least connect-timeout")
boolean isTimeoutOrderingSane() {
    return readTimeout.compareTo(connectTimeout) >= 0;
}
```

---

## Precedence: which source wins

Simplified ladder, lowest to highest — the sources that actually appear in deployments:

```
application.properties / application.yaml (in the jar)   ← lowest
  ↓  profile-specific files (application-prod.yaml)
  ↓  config files outside the jar (./config/, spring.config.import)
  ↓  OS environment variables
  ↓  Java system properties (-D)
  ↓  command-line arguments (--myapp.payment.max-retries=5)   ← highest
```

Later wins, so a deployment can always override the jar without touching it. The full
order (devtools, `SPRING_APPLICATION_JSON`, `@TestPropertySource`, JNDI, `@PropertySource`)
is in the Spring Boot reference under *Externalized Configuration*; reach for it only when
debugging a genuine surprise.

**Debugging "which source set this?"** — IntelliJ IDEA shows the resolved value as an
inlay hint next to the property; selecting the hint names the source supplying it and
whether another source overrides it. It also navigates between a property declaration, the
`@ConfigurationProperties` member it binds to, and every usage — for your own properties
that navigation is driven by the metadata `spring-boot-configuration-processor` generates,
which is the second reason to keep it on the annotation processor path. At runtime, `/actuator/configprops` and `/actuator/env` give the same answer;
both must be secured and value-sanitised in production:

```yaml
management:
  endpoint:
    configprops.show-values: when-authorized
    env.show-values: when-authorized
```

---

## Environment variables: the name derivation

Spring derives the env var name from the canonical property name: **replace dots with
underscores, remove dashes, uppercase**.

| Property | Environment variable |
|---|---|
| `myapp.payment.base-url` | `MYAPP_PAYMENT_BASEURL` |
| `myapp.payment.connect-timeout` | `MYAPP_PAYMENT_CONNECTTIMEOUT` |
| `myapp.servers[0].host` | `MYAPP_SERVERS_0_HOST` |
| `spring.datasource.url` | `SPRING_DATASOURCE_URL` |

The dash disappears. `MYAPP_PAYMENT_CONNECT_TIMEOUT` binds nothing, silently, and the app
starts on the default — the single most common "the env var isn't working" bug. Derive the
name in three steps rather than by eye, because the wrong one looks right:

1. Start from the **canonical** property name (kebab-case, as written in `application.yaml`).
2. Dots → underscores; dashes → **deleted**, not replaced; `[0]` → `_0_`.
3. Uppercase the result.

When an env var appears to have no effect, work the loop rather than guessing: check
`/actuator/env` (or IntelliJ's inlay hint) for what the property actually resolved to and
which source supplied it — if the property is absent entirely, the name is wrong; if it
resolved from `application.yaml`, something higher in the ladder is not reaching the
process.

Relaxed binding accepts `base-url`, `baseUrl` or `base_url` in files. **Write kebab-case
in YAML, consistently** — the metadata, the docs and the derivation above all key on the
canonical name.

---

## Profiles: for wiring, not for environments

Profiles select *beans and behaviour*. They are a poor container for per-environment
values, and a terrible one for secrets.

```yaml
# ✅ profile changes what is wired
spring:
  config:
    activate:
      on-profile: local
myapp:
  payment:
    base-url: http://localhost:8081     # local stub, not a secret, safe in git
```

```yaml
# ❌ application-prod.yaml — production topology and credentials in the repo
myapp:
  payment:
    base-url: https://payments.internal.acme.com
    api-key: sk_live_9f3c...
```

- Keep production behaviour on the **default** path; profiles then describe deviations
  (`local`, `test`), and a missing `SPRING_PROFILES_ACTIVE` degrades to correct.
- No profile-per-customer, profile-per-region explosion. That is deployment data, so it
  belongs in env vars or a ConfigMap.
- `spring.profiles.group` composes profiles; use it rather than a profile list per env.
- Never make security depend on a profile being absent (`@Profile("!prod")` on a bean that
  disables auth is one typo from production).

---

## Secrets

Passwords, API keys, certificates and private keys never enter source control, encrypted
or otherwise. Use Vault, AWS Secrets Manager, Google Secret Manager, Azure Key Vault, or
the platform equivalent.

Prefer **mounted files over env vars** — env vars leak through process listings, crash
dumps and child processes, and cannot be rotated without a restart. Spring reads a mounted
directory directly:

```yaml
spring:
  config:
    import: "optional:configtree:/etc/secrets/"   # file name → property, contents → value
```

```
/etc/secrets/myapp.payment.api-key      # one secret per file, mounted by the platform
```

Anything binding a secret gets `@NotBlank` like everything else, so a broken mount fails
the boot instead of producing a 401 storm. Keep the value out of logs and out of
`toString()` — records print every component, so a secret in a record is a secret in your
logs the first time someone logs the properties object.

---

## Deployment shapes

| Architecture | Approach |
|---|---|
| Monolith | Shared defaults in the app, profile files only where genuinely needed, deployment overrides via env vars |
| Container platform (Kubernetes) | Defaults in the app, per-deployment values in a **ConfigMap**, secrets in a Secret or CSI-mounted from a secrets manager |
| Microservices | **Spring Cloud Config Server** to centralise, version and govern configuration across services; `spring.config.import: configserver:` on each client |

There is no single right answer — pick for the deployment you have, and keep the
defaults-in-the-app half constant across all three.

A volume-mounted ConfigMap reads through the same `configtree:` mechanism as mounted
secrets — file name is the property, file contents is the value:

```yaml
spring:
  config:
    import: "optional:configtree:/etc/config/"   # ConfigMap, volume mounted
```

Mounted secrets use the same mechanism at a different path (see Secrets below). Mounting
beats env vars for both: values update without rebuilding the pod spec, and no secret
lands in the process environment.

---

## Test the configuration

Config that only fails in production is untested code. `ApplicationContextRunner` boots the
binding alone, in milliseconds, with no Spring context.

```java
class PaymentPropertiesTest {

    private final ApplicationContextRunner runner = new ApplicationContextRunner()
            .withUserConfiguration(EnablePaymentProperties.class);

    @Test
    void fails_to_start_when_base_url_is_missing() {
        runner.withPropertyValues("myapp.payment.connect-timeout=2s")
              .run(context -> assertThat(context)
                      .getFailure()
                      .hasMessageContaining("myapp.payment.base-url"));
    }

    @Test
    void binds_durations_and_nested_groups() {
        runner.withPropertyValues(
                      "myapp.payment.base-url=https://payments.test",
                      "myapp.payment.connect-timeout=2s",
                      "myapp.payment.max-retries=4",
                      "myapp.payment.circuit.failure-threshold=5",
                      "myapp.payment.circuit.reset-timeout=30s")
              .run(context -> assertThat(context.getBean(PaymentProperties.class))
                      .returns(Duration.ofSeconds(2), PaymentProperties::connectTimeout)
                      .returns(5, p -> p.circuit().failureThreshold()));
    }

    @EnableConfigurationProperties(PaymentProperties.class)
    static class EnablePaymentProperties { }
}
```

Worth having as well: one `@SpringBootTest` per profile that only asserts the context
loads. It catches the profile whose YAML has drifted out of shape, for the cost of a boot.

---

## Review pass

Deterministic first, judgement second — the greps find most of it in seconds:

```bash
grep -rn "@Value" --include=*.java src/main/                 # 1. binding scattered outside config
grep -rln "@ConfigurationProperties" --include=*.java src/   # 2. then check each for @Validated
grep -rniE "password|secret|api-?key|token" src/main/resources/  # 3. secrets in the repo
ls src/main/resources/application-*.y*ml 2>/dev/null       # 4. profile files — read each for env data
```

Then read each properties class against this table. A row is a finding only if the value
is genuinely required — an optional knob with a documented default is fine as it is.

| Smell | Fix |
|---|---|
| `@Value` outside a config class | Bind a `@ConfigurationProperties` record |
| `@ConfigurationProperties` without `@Validated` | Add it, plus constraints on every field |
| Constraints present but `spring-boot-starter-validation` missing | Add the starter — the annotations are inert without it |
| `int`/`boolean` for a required value, where `0`/`false` is legal | `Integer`/`Boolean` + `@NotNull`, or a range that excludes the default (`@Min(1)`), or `@DefaultValue` |
| `long timeoutMillis` | `Duration` |
| Nested properties class without `@Valid` | Add `@Valid` — nested constraints are otherwise skipped |
| Production URL or credential in `application-prod.yaml` | Env var / ConfigMap; secret to the secrets manager |
| Env var that "doesn't work" | Check dash removal: `connect-timeout` → `CONNECTTIMEOUT` |
| Profile carrying environment data | Move to env vars; keep profiles for bean wiring |
| Secret in a record that gets logged | Keep secrets out of `toString()`; sanitise actuator endpoints |
| Config change requiring a rebuild | It is a default in the wrong place |

Report findings as `file:line` + the row that matched. If the same row fires across many
classes, say so once and name the pattern rather than listing every instance — the fix is
the same edit repeated.
