# Skills

## Two phases

`analysis/` serves **Orient** — understanding a problem before committing to a solution.
`design/` and `testing/` serve **Act** — building the thing well. The handover is concrete:
analysis yields a ubiquitous language, bounded contexts and key examples, which are exactly
what `naming`, `coupling-analysis` and the testing skills consume.

Reaching for a design skill while the problem is still unclear is the common mistake, and it
produces a beautifully constructed answer to the wrong question.

## Mental model: guidance at altitudes

The design skills are complementary because each operates at a different **altitude** and
answers a different question. One meta layer sits above them all and acts as the tiebreaker.

| Altitude | Skill(s) | Question it answers |
|---|---|---|
| **Meta — any level** | `simple-design` (Beck's Four Rules) | Is this the simplest design that works? Which guidance wins when they conflict? |
| **Cross-cutting — any level** | `naming` | Does this identifier communicate as much as it could, given its scope and context? |
| Class / method (micro) | `software-design-principles` | Is this code well constructed? |
| Component / system (macro) | `cupid-properties` + stack skill (`cupid-python`, `cupid-java-spring-boot`) | Is this a good component to live with? |
| Between components | `coupling-analysis` | Are the dependencies between parts healthy? |

Kent Beck's Four Rules of Simple Design (passes the tests → reveals intention → no
duplication → fewest elements, in priority order) are **fractal** — they apply unchanged at
every altitude, and each altitude skill is an elaboration of them at one level. When rules
from different skills conflict in context, resolve with the four rules in priority order;
`simple-design/SKILL.md` maps each rule to its expression at each altitude.

Routing: writing or refactoring runs `software-design-principles` as the active
checklist, with `simple-design` deciding when to stop. Review leads with
`cupid-properties` (plus the stack skill for concrete evidence), then descends to
`software-design-principles` for findings inside specific classes. Boundary
questions go to `coupling-analysis`. Don't load every skill for every task — the
frontmatter descriptions encode the altitudes, and each skill says when to
escalate or descend.

## Skills

**Analysis (`analysis/`)**

| Skill | Purpose |
|---|---|
| `problem-lenses` | Nine problem-analysis lenses — Cynefin, impact mapping, Wardley mapping, spec by example, domain storytelling, event storming, DDD, systems thinking, LeSS principles. Routes by the question you're stuck on; Cynefin first, since it decides whether analysis helps at all |

**Design (`design/`)**

| Skill | Purpose |
|---|---|
| `simple-design` | Beck's Four Rules as meta-guidance and tiebreaker |
| `naming` | Technique for deriving names — calling-context, wishful thinking, domain types, scope-length |
| `software-design-principles` | Class/method construction rules (calisthenics, tell-don't-ask, SLAP) |
| `cupid/` | CUPID properties: generic core + Python and Java/Spring Boot stack skills ([README](design/cupid/README.md)) |
| `coupling-analysis` | Stub delegating to Khononov's [Modularity plugin](https://github.com/vladikk/modularity) |
| `validation-review` | Domain model validation review for Java/Spring/DDD (Design by Contract lens) |
| `plan-eng-review` | Interactive eng-manager-mode plan review before implementation |

**Testing (`testing/`)**

| Skill | Purpose |
|---|---|
| `bug-magnet` | Edge-case and bug-discovery prompts for testing |
| `groovy-spock-testing` | Groovy/Spock test DSL and fixture patterns |
| `java-junit5-testing` | Java/JUnit 5 BDD-style tests, assertion DSLs, test data builders |
| `kotlin-kotest-testing` | Kotlin/Kotest specs, matcher DSLs, data-driven testing |

**Writing (`writing/`)**

| Skill | Purpose |
|---|---|
| `notes/` | Session-notes system: wrap, ingest, lint ([README](writing/notes/README.md)) |
| `tropes` | Avoid AI writing tells — wraps the [tropes.fyi](https://tropes.fyi) catalogue |
| `plain-idiom` | Strip culture-bound idiom — US sports metaphor, war framing, management-speak |

`tropes` and `plain-idiom` are peers, not layers: same object (prose), different axis. A
draft can be trope-free and still read as a US management memo, or plain and still read as
AI-written, so run both on anything going to a wide audience. Catalogues live beside each
skill (`tropes.md`, `registers.md`); the `notes/` skills carry a subset via the
`writing-style.md` generated at sync time from
`writing/notes/references/writing-style.md`.

**Other**

| Skill | Purpose |
|---|---|
| `spring-boot-4-gradle-9-upgrade` | Task skill for the Spring Boot 4 / Gradle 9 migration |
| `spring-boot-configuration` | Where each value belongs, `@ConfigurationProperties` binding, startup validation, precedence, secrets |

Both sit in their own dir directly under `skills/` — a `spring-boot/` topic dir is worth making once a third accrues.
