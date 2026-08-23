---
name: problem-lenses
description: Nine lenses for analysing a problem before building it — Cynefin, impact mapping, Wardley mapping, specification by example, domain storytelling, event storming, domain-driven design, systems thinking, LeSS principles. Use whenever work is starting and the problem is not yet clear: vague or contested requirements, an unfamiliar domain, arguments about scope or approach, build-vs-buy calls, a bug or complaint that keeps coming back, teams hitting their numbers while delivery stays slow, or a request to frame a problem, run discovery, model a domain, find bounded contexts, map impacts, or work out what to build first. Routes to the one lens that answers the question actually blocking progress, rather than running all nine.
---

# Problem lenses

Nine ways of looking at a problem before committing to a solution. Each answers a
different question. The value is in picking the one that answers the question you are
actually stuck on — running all nine is the ceremony this repo exists to avoid.

Full technique, worked examples and failure modes: [lenses.md](lenses.md). Read the entry
for the lens you pick; don't read all nine.

## First: what kind of problem is it?

Cynefin comes before the others because it decides whether analysis is the right move at
all. Analysing a complex problem harder does not make it tractable; probing does.

| Domain | Cause and effect | What to do |
|---|---|---|
| Clear | Obvious | Apply the known answer. No lens needed |
| Complicated | Knowable with expertise | Analyse — this is where most lenses below earn their keep |
| Complex | Only visible afterwards | Run a safe-to-fail probe. A walking skeleton beats a workshop |
| Chaotic | None | Stabilise first, analyse later |
| Confused | You don't know which | The dangerous default — say so out loud, then split the problem |

The common mistake is treating a complex problem as complicated: more analysis, more
diagrams, more confident plans, and none of it survives contact. Full detail in
[lenses.md](lenses.md).

## Route by the question

| The question you're stuck on | Lens |
|---|---|
| Why are we doing this at all? What behaviour change would count as success? | Impact mapping |
| Where do we invest? What should we build, buy, or wait for? | Wardley mapping |
| How does this work actually happen today, and who does it? | Domain storytelling |
| What happens in this process over time, and where are the seams? | Event storming |
| What are the concepts really called, and where does one model stop being true? | Domain-driven design |
| What exactly does "done" mean for this rule? | Specification by example |
| Why does this keep coming back no matter what we fix? | Systems thinking |
| Are we optimising a part while the whole gets worse? Is the org the constraint? | LeSS principles |

If two rows fit, you have two problems — take the one that blocks the next slice.

## Picking well

The failure mode is reaching for the lens you like rather than the one that fits. Some
tells:

- Arguing about features → you have a goal problem, not a feature problem. Impact
  mapping. The argument usually dissolves once the behaviour change is named.
- Arguing about edge cases in the abstract → stop arguing and write the examples.
  Specification by example turns an opinion fight into a table you can check.
- Nobody can agree what a word means ("what counts as an *active* rider?") → DDD.
  Two definitions usually means two bounded contexts, not one confused team.
- The domain is unfamiliar and you're guessing → domain storytelling first. It is the
  gentlest lens: people tell you what they do, you draw it back at them.
- The process is known but tangled, and you suspect the boundaries are wrong → event
  storming.
- Every fix creates a new problem somewhere else → systems thinking. You are pushing
  on a symptom while a feedback loop pushes back.
- The debate is build vs buy, or "is this our differentiator?" → Wardley mapping.

## How they compose

They are not a pipeline, but some pairs are genuinely strong:

- **Impact mapping → specification by example.** The deliverable at the bottom of an
  impact map is the thing to write key examples for. Both are Adzic, and they meet here.
- **Domain storytelling → event storming.** Stories give you the vocabulary and the actors;
  event storming then puts the timeline and the boundaries on it.
- **Event storming → DDD.** Clusters of events and commands that share a common noun are
  aggregate candidates; the seams between clusters are bounded-context candidates.
- **Wardley mapping → systems thinking.** Both reason about the whole; Wardley adds
  evolution over time, which is what makes "we'll build our own" look different in year
  three.
- **Wardley mapping → DDD → team boundaries.** Susanne Kaiser's *Architecture for Flow*
  runs these as one chain: the map says where the differentiating work is, DDD draws the
  boundaries around it, and teams are then aligned to those boundaries rather than cutting
  across them. The third leg is Team Topologies, which this skill does not cover — LeSS
  principles below reach the same organisational question from the flow side.
- **LeSS principles ↔ systems thinking.** Related but not the same lens. Systems thinking
  looks for loops inside the system you're building; LeSS looks at whether the
  organisation building it is the constraint. If every fix needs three teams to agree, the
  loop you're hunting is an org chart.

Two flows worth knowing, one for each common starting point:

- **New product, unclear value**: impact mapping (why/who) → Wardley (where to invest) →
  spec by example (what done means for the first slice).
- **Existing system, unclear domain**: domain storytelling (how it works now) → event
  storming (timeline and seams) → DDD (language and boundaries).

Stop as soon as the next slice is obvious. The point of a lens is to unblock Decide, not to
produce a document.

## Keep it inside the loop

These lenses serve **Orient** in the OODA delivery loop (`practices/delivery-process.md` in
the ai-development repo). That has consequences worth holding onto:

- One lens, one artefact, then back to building. A walking skeleton usually teaches you
  more than a second workshop would.
- The artefact is scaffolding, not a deliverable. An impact map that stops being true is
  meant to be redrawn, not maintained.
- Prefer the lens that produces something executable. Key examples become tests, which is
  a computational control; a diagram is an inferential one that decays as context grows.
- If the analysis is longer than the slice it unblocks, you are building a spec workflow —
  the exact ceremony the guardrails thesis argues against, and the evidence there is that
  it buys almost nothing for a lot of wall-clock time.

## Handing off to the design skills

Analysis ends where construction begins. What each lens hands over:

| Lens output | Skill that picks it up |
|---|---|
| Ubiquitous language, domain terms | `naming` |
| Bounded contexts, context map | `coupling-analysis` |
| Aggregates, invariants | `validation-review`, `cupid-properties` |
| Key examples | `bug-magnet` and the stack testing skills |
| A chosen slice, ready to plan | `plan-eng-review` |
