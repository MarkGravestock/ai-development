---
name: cosmic-python
description: Structure or review Python services using the Cosmic Python (Architecture Patterns with Python) approach - domain model, repository, service layer, unit of work, domain events and message bus. Use when designing a new Python service or module with real domain logic, deciding where logic belongs, or reviewing layering and test strategy. Not for scripts or simple CRUD.
---

# Cosmic Python

Layering and persistence-ignorance for Python services. Detail lives in the book,
[Architecture Patterns with Python](https://www.cosmicpython.com/book/preface.html);
this skill only fixes the conventions to apply and where to look.

**Altitude:** component/system, between `cupid-properties` (is this a good
component?) and `coupling-analysis` (are the dependencies healthy?). `simple-design`
is the tiebreaker: if the domain is thin, skip layers and say so.

## Layout and dependency direction

Dependencies point inwards only: `entrypoints -> service_layer -> domain`, and
`adapters -> domain`. The domain imports nothing from other layers or from
frameworks/ORMs.

```
src/<pkg>/
  domain/         # entities, value objects, aggregates, events, commands
  service_layer/  # handlers, UoW abstraction, message bus
  adapters/       # repository/UoW implementations, ORM mapping, external clients
  entrypoints/    # HTTP/CLI/queue consumers - thin, build a command and call the bus
  bootstrap.py    # composition root
tests/{unit,integration,e2e}/
```

Enforce the arrows with a tool, not a prompt:
[import-linter](https://import-linter.readthedocs.io/) layers/forbidden contracts
in CI.

## Rules

- **Domain model** ([ch. 1](https://www.cosmicpython.com/book/chapter_01_domain_model.html)):
  behaviour on entities and aggregates; value objects immutable (frozen dataclasses);
  no I/O, no ORM base classes.
- **Aggregate** ([ch. 7](https://www.cosmicpython.com/book/chapter_07_aggregate.html)):
  the consistency boundary. One repository per aggregate, reference others by id,
  change one aggregate per transaction.
- **Repository** ([ch. 2](https://www.cosmicpython.com/book/chapter_02_repository.html)):
  abstract port (`add`, `get`); implementations in `adapters/`; an in-memory fake for tests.
- **Service layer** ([ch. 4](https://www.cosmicpython.com/book/chapter_04_service_layer.html)):
  one handler per command: load, call domain, commit. No web or ORM types in signatures.
- **Unit of Work** ([ch. 6](https://www.cosmicpython.com/book/chapter_06_uow.html)):
  context manager owning the transaction and exposing repositories; commit explicitly.
- **Events and message bus** ([ch. 8](https://www.cosmicpython.com/book/chapter_08_events_and_message_bus.html)):
  aggregates record events; the bus dispatches after commit. Side effects and
  cross-aggregate work go in event handlers.
- **Wiring** ([ch. 13](https://www.cosmicpython.com/book/chapter_13_dependency_injection.html)):
  in `bootstrap.py`, not via globals or concrete imports in handlers.

## Testing

- Mostly fast unit tests through the service layer with fake repository/UoW; a few
  integration tests per adapter; a handful of e2e tests
  ([ch. 5](https://www.cosmicpython.com/book/chapter_05_high_gear_low_gear.html)).
- Domain model tests use no fakes at all.
- Test behaviour via commands and handlers, not internals.

## Review checklist

- Does any `domain/` import fail the layering check?
- Can every handler be tested with only fakes?
- Is each transaction one aggregate?
- Is any entrypoint doing business logic?
- Is the structure earning its keep, or is it ceremony for a thin domain?
