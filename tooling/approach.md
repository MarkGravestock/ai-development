# The approach

## Control taxonomy

Böckeler's model, used throughout this repo. Every control is either:

- **computational** (machine-run, deterministic — compilers, linters, tests) or
  **inferential** (prompts, agent reviewers), and
- **feedforward** (steers before or during generation) or **feedback**
  (verifies after).

Computational controls are free at inference time and hold regardless of how
much context has accumulated. Inferential controls consume the model's
attention budget and decay as context grows. Default to computational; where
only inferential will do, keep it to the smallest high-signal set.

- <https://martinfowler.com/articles/harness-engineering.html>
- <https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html>

## Why not a software factory

Prompt-heavy frameworks sit almost entirely in inferential feedforward, the
weakest quadrant.

A paired comparison across five production repos found the full multi-phase
spec workflow scored +0.05 on a 5-point composite over a plain baseline, at
roughly 70% more wall-clock time. Adding deterministic discovery and validation
hooks bought about three times that gain for a fraction of the cost, and
validation hooks outperformed discovery hooks. Blinded human reviewers did not
reproduce the LLM judge's ranking.

- <https://arxiv.org/abs/2604.05278> — the paired comparison
- <https://arxiv.org/abs/2607.02389> — lightweight CLI plus substrate
  constraints outperforming richer agentic scaffolding
- Chroma's context-rot work — instruction adherence degrades with input length
  on every frontier model tested

Known limits of that evidence: small n, heavy reliance on LLM-as-judge, and
measured on models that will be superseded within months. The direction is
consistent across studies; the magnitude is not settled. Treat vendor-published
multiples with the scepticism their commercial framing deserves.

## Where ceremony does earn its keep

- Greenfield work with no conventions for the agent to ground against
- Contexts where the artefact trail is itself a deliverable (audit, compliance)
- Multi-session state, though a `docs/` directory and a good agent instructions
  file recover most of this
- Teams with inconsistent prompting discipline, where structure levels output

Worth adopting regardless of position on the rest: pre-phase repo grounding
before touching unfamiliar code.

## Consequences for this repo

- Tiny always-loaded instruction file; everything else loaded on demand
- Skills open by running the gauntlet, then spend model attention only on what
  tools cannot judge — design intent, naming, missing cases, security reasoning
- Every new rule gets one question first: can a tool enforce this instead? How to answer it as problems recur: [growing-guardrails.md](../practices/growing-guardrails.md).
