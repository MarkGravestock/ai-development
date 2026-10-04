---
description: Implement until the locked specs and the gate pass (phase 2)
agent: build
---

Load the `executable-specs` skill and run its phase 2.

Lock status and failing examples right now:
!`uv run python scripts/spec_lock.py check 2>&1 | tail -5`
!`uv run pytest tests/acceptance -q --no-header -p no:randomly 2>&1 | tail -15`

If the lock check above is not clean, stop and report it before changing anything.
