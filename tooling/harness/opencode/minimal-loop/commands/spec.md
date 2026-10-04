---
description: Write a feature as failing example tests for review (phase 1)
agent: build
---

Load the `executable-specs` skill and run its phase 1 for: $ARGUMENTS

Current acceptance suite:
!`uv run pytest tests/acceptance -q --no-header -p no:randomly 2>&1 | tail -15`

Stop after presenting the examples and open questions. Do not lock them.
