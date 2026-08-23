# The lenses

## Contents

- [Cynefin](#cynefin) — what kind of problem is this, and does analysis even help
- [Impact mapping](#impact-mapping) — why are we doing this, whose behaviour must change
- [Wardley mapping](#wardley-mapping) — where to invest, build vs buy, what commoditises
- [Specification by example](#specification-by-example) — what "done" means for a rule
- [Domain storytelling](#domain-storytelling) — how the work happens today, and who does it
- [Event storming](#event-storming) — what happens over time, and where the seams are
- [Domain-driven design](#domain-driven-design) — what the concepts are called, where a model stops holding
- [Systems thinking](#systems-thinking) — why the problem keeps coming back
- [LeSS principles](#less-principles) — are we optimising the part or the whole
- [Sources](#sources)

One running example throughout: **an e-bike hire scheme**. The same problem seen seven
ways, so the difference between the lenses is visible rather than described.

Read the entry for the lens you picked in [SKILL.md](SKILL.md). Each links its canonical
source rather than transcribing it — a stale copy of someone else's method is worse than
a link, because it gets believed.

---

## Cynefin

**Answers:** what kind of problem is this, and does analysing it harder actually help?

Snowden's sense-making framework ([Cynefin.io](https://cynefin.io/wiki/Cynefin)). Five
domains, each with a different valid move — the point is that a method which works in one
domain fails in another:

| Domain | Relationship between cause and effect | Sequence | Practice |
|---|---|---|---|
| Clear | Obvious to anyone | sense → categorise → respond | Best practice |
| Complicated | Knowable, given expertise | sense → analyse → respond | Good practice |
| Complex | Only visible in hindsight | probe → sense → respond | Emergent |
| Chaotic | None discernible | act → sense → respond | Novel |
| Confused | You don't know which domain you're in | Split it up and place the pieces | — |

Two things worth holding onto. **Confused is the default**, not an edge case — most
arguments about approach are really two people placing the same problem in different
domains. And the Clear/Chaotic boundary is a **cliff**, not a border: complacency about
something "obvious" fails suddenly rather than gradually.

**Output:** an agreement about which domain the problem is in, and therefore which moves
are legitimate.

**Example.** "Riders abandon the app at payment." Treated as complicated, this becomes a
month of funnel analysis and a redesign. Placed in complex, it becomes four safe-to-fail
probes next week — one-tap wallets for twenty users, a price shown earlier, a saved card,
a different error message — and you keep whichever moves the number. Neither approach is
wrong in general; the question is which domain you are in, and nobody had asked.

**Fails when** it's used as a taxonomy for filing problems rather than a prompt for
choosing a move. The output should change what you do on Monday.

**Why it comes first:** analysis lenses are complicated-domain tools. In the complex
domain a walking skeleton is the probe, and it teaches you more than any workshop would —
which is the whole argument behind this repo's delivery loop.

---

## Impact mapping

**Answers:** why are we doing this, and whose behaviour must change for it to work?

A mind map four levels deep, in this order ([Adzic](https://www.impactmapping.org/)):

1. **Why** — one measurable goal. Not a feature. If it can't be measured, keep asking.
2. **Who** — actors who can move that number, named specifically. Include the ones who can
   *hurt* it.
3. **How** — the behaviour change you want from each actor. This is the level people skip,
   and skipping it is what turns a roadmap into a feature list.
4. **What** — deliverables you could build to cause that change. Each is a bet, and the map
   shows what it is betting on.

**Output:** a map whose leaves are optional. That is the point — you can cut a deliverable
and see exactly which assumption you are dropping.

**Example.** Goal: *weekday commuter trips +20% by Q3*. Actor: *commuters who own a car*.
Impact: *they choose a bike for the 8am trip into town*. Deliverables: guaranteed bike
reservation the night before; a covered dock near the station; a monthly pass cheaper than
parking. Three bets. The reservation bet assumes availability is what stops them — testable
in a week by reserving bikes manually for twenty volunteers.

**Fails when** the goal is really a deliverable in disguise ("launch the app"). Everything
below it becomes decoration, because no branch can be cut without cancelling the project.

---

## Wardley mapping

**Answers:** where should effort go, and what will this look like in three years?

Anchor on a user need, chain the components that meet it, then position each on evolution
([Wardley](https://learnwardleymapping.com/)):

- **Y axis — value chain.** User need at the top, each component below the thing it serves,
  down to invisible utilities. Height means visibility to the user, not importance.
- **X axis — evolution.** Genesis → Custom-built → Product → Commodity. Position is judged
  by how ubiquitous and well-understood a thing is, not how new it is to you.

Then read the map: build what's on the left and differentiating, buy what's on the right,
and expect everything to drift rightward whether you plan for it or not.

**Output:** a map you can argue with. Its value is that two people who disagree can now
point at *where* they disagree.

**Example.** Need: *get across town quickly*. Chain: hire app → reservation → fleet
availability → bike telemetry → GPS → power. Payments sit at commodity — building your own
is indefensible. Telemetry is product-stage and drifting right, so a custom build has maybe
two years of edge. Predictive rebalancing (guessing where bikes will be needed at 8am) is
genesis, and it is the only thing on the map a competitor cannot buy.

**Fails when** it becomes a one-off drawing. The map earns its keep by being redrawn when a
component moves and the strategy that depended on its position quietly stops working.

---

## Specification by example

**Answers:** what exactly does "done" mean for this rule?

Replace prose requirements with concrete examples, agreed with whoever knows the domain,
then keep them executable ([Adzic](https://gojko.net/books/specification-by-example/)):

1. Take one rule. Ask for a realistic example — real values, not `foo`.
2. Probe the boundaries: what changes the answer? Each answer is another example.
3. Cut ruthlessly to the **key examples** — the smallest set where removing any one loses a
   distinct case. Fifty examples of the same case is documentation debt.
4. Automate them so they fail when the rule changes. Unexecuted examples rot silently.

**Output:** a table that is simultaneously the specification, the acceptance criteria and
the test suite.

**Example.** Rule: *overnight hires are charged differently*. Ask for one case and the
disagreement surfaces immediately:

| Start | End | Charge | Why |
|---|---|---|---|
| 18:00 | 21:00 | 3 × hourly | Evening, under the cap |
| 18:00 | 09:00 | Overnight flat fee | Crosses 02:00 |
| 23:50 | 00:10 | 20 min hourly | Crosses midnight but not 02:00 |
| 18:00 | 09:00 next-but-one day | Overnight + day rate | Two nights |

Row three is the one that ends the argument. Half the room thought "overnight" meant
"crosses midnight"; the billing rule actually keys on 02:00.

**Fails when** examples are written after the code, by the people who wrote the code. Then
they document what was built rather than what was wanted, and agree with the bug.

---

## Domain storytelling

**Answers:** how does this work actually happen today, and who does it?

A domain expert tells a story; you draw it live in a pictographic language and read it back
([Hofer & Schwentner](https://domainstorytelling.org/)):

- **Actors** (who acts), **work objects** (what they act on), **activities** (arrows between
  them), with each sentence **numbered** so the story has an order.
- Read the story back aloud as sentences: *"1. The mechanic scans the bike's QR code."* If
  the expert winces, the model is wrong — and you find out in seconds.

Choose scope deliberately: coarse or fine grained, **as-is or to-be**, and pure domain or
including the systems people actually use. Mixing as-is and to-be in one story is the most
common way to confuse everyone.

**Output:** a picture the domain expert recognises as their job. That recognition is the
test.

**Example.** As-is, taking a bike out of service: *1. Rider reports a fault in the app.
2. System flags the bike. 3. Mechanic collects the bike from the dock. 4. Mechanic records
the repair in a spreadsheet. 5. Mechanic re-enables the bike in the admin tool.* Step 4 is
the find. The spreadsheet is invisible to every system, and it is where the parts-cost data
everyone wanted has been living all along.

**Fails when** it drifts into whiteboard design. The moment someone says "and then the
service would publish an event", you have stopped recording the domain and started
designing — which is a different lens.

---

## Event storming

**Answers:** what happens over time in this process, and where are the seams?

Sticky notes on a long wall, built up in a deliberate order
([Brandolini](https://www.eventstorming.com/)). Colours vary between practitioners; what
matters is consistency in the room:

| Note | Means |
|---|---|
| Orange | **Domain event** — something that happened, past tense: *Bike Unlocked* |
| Blue | **Command** — an intent to change state: *Unlock Bike* |
| Lilac | **Policy** — the reaction rule: *whenever X, do Y* |
| Yellow | **Aggregate** — what the commands and events cluster around |
| Green | **Read model** — the view someone needs to decide |
| Pink | **External system** |
| Red | **Hot spot** — disagreement, unknown, pain. These are the most valuable notes. |

Run it at the level that fits the question: **big picture** (whole business, find the
chaos), **process modelling** (one flow end to end), or **software design** (aggregates and
invariants).

Work outward from events: events → commands that cause them → policies that react →
aggregates the commands cluster around → boundaries between clusters.

**Output:** a timeline with hot spots marked, and candidate boundaries where the noun
changes.

**Example.** *Bike Reserved → Reservation Expired → Bike Unlocked → Trip Started → Trip
Ended → Bike Docked → Fault Reported → Bike Taken Out Of Service.* Two clusters emerge:
everything up to *Trip Ended* is about hiring; everything after *Fault Reported* is about
maintenance. A red hot spot lands on *Reservation Expired* — nobody in the room agrees how
long a reservation holds, and it turns out billing and operations have different answers.

**Fails when** it becomes a database-design session in disguise. If notes start naming
tables and foreign keys, the workshop stopped modelling the domain a while ago.

---

## Domain-driven design

**Answers:** what are the concepts really called, and where does one model stop being true?

For analysis, the strategic half is what matters ([Evans](https://www.domainlanguage.com/ddd/reference/)):

- **Ubiquitous language** — one language per context, used identically in conversation,
  code and tests. When a term needs translating between a person and the code, that gap is
  where bugs live.
- **Bounded context** — the boundary within which a model holds. The signal you've found
  one: the same word means different things on either side of it, and that is *fine*.
- **Context map** — how contexts relate, and who bends to whom: shared kernel,
  customer/supplier, conformist, anticorruption layer.
- **Core vs supporting vs generic** — where your differentiation actually is. This pairs
  naturally with a Wardley map, which answers the same question with evolution added.

**Output:** named contexts, an explicit language per context, and a map of the relationships
between them.

**Example.** "Bike" means three different things. In **Rentals** it is *a thing that can be
reserved and unlocked* (identity: the QR code). In **Maintenance** it is *an asset with a
service history* (identity: the frame number). In **Finance** it is *a depreciating capital
item*. Forcing one `Bike` class on all three produces an object with a service history, a
depreciation schedule and a lock state, which is three models wearing a trenchcoat. Three
contexts, with an anticorruption layer where Maintenance consumes Rentals events, keeps each
model honest.

**Fails when** teams adopt the tactical patterns — entities, repositories, aggregates —
without doing the strategic work. You get the ceremony of DDD with none of the payoff,
because the boundaries are still wrong.

---

## Systems thinking

**Answers:** why does this keep coming back no matter what we fix?

Look at structure rather than events. The behaviour you keep seeing is usually produced by
the system's own loops ([Meadows](https://donellameadows.org/systems-thinking-book/)):

- **Stocks and flows** — what accumulates, what drains it, and at what rate.
- **Feedback loops** — reinforcing (compounds; explains growth and collapse) and balancing
  (resists change; explains why your fix did nothing).
- **Delays** — the gap between action and effect. Long delays cause overcorrection, and
  overcorrection looks exactly like incompetence from the outside.
- **Leverage points** — Meadows' ordering, roughly: parameters are weak; feedback loops are
  stronger; goals and paradigms are strongest. Most effort goes into the weakest.

Useful question: *what would have to be true about the structure for this behaviour to be
the normal outcome?*

**Example.** Bikes pile up at the bottom of the hill every evening and the top station is
empty every morning. The reflex fix is a bigger rebalancing van — a parameter change, the
weakest lever, and the problem returns each night. The stock is *bikes at the top station*;
the outflow (gravity-assisted downhill trips) hugely exceeds the inflow. A £1 credit for
riding uphill changes the flow rather than compensating for it, and it works while the van
is asleep. Note also the delay: rebalancing at 6am means the 8am commuters see yesterday's
distribution, so operations always looks a day behind.

**Fails when** it stays abstract. A loop diagram nobody can attach a number or an anecdote
to is a picture of a feeling. Anchor each loop in something observed.

---

## LeSS principles

**Answers:** are we optimising a part while the whole gets worse, and is the organisation
itself the constraint?

The principles, not the framework ([LeSS](https://less.works/less/principles/overview)).
Sprints, a cross-team backlog and feature teams solve a multi-team coordination problem;
the principles underneath travel much further. The ones that do analytical work:

- **Systems thinking** — customers experience end-to-end cycle time, not how fast any one
  step ran. Local efficiency is not the goal and often opposes it.
- **Whole-product focus** — nobody buys half a product. A part that is finished while the
  whole is not is inventory, not progress.
- **Customer-centric** — value and waste are defined by the paying customer, not by the
  team that produced the artefact.
- **Queueing theory** — manage queue size, work-in-progress and variability rather than
  utilisation. A busy team and a fast team are different things.
- **More with LeSS** — fewer roles, artefacts and handoffs, not more process to manage the
  handoffs you already have.

Useful question: *whose local optimum is this, and what does it cost the whole?*

**Output:** a named local optimisation, and what it costs end to end.

**Example.** Bike-fault reports take nine days to resolve. Every team is hitting its
numbers: the app team ships promptly, maintenance closes tickets fast, data delivers
reports on time. The nine days are almost entirely queue — waiting for the weekly sync
where the three teams reconcile who owns a fault. Each team is locally efficient and the
whole is slow, so no team's dashboard shows the problem. The fix is a boundary change, not
a productivity push.

**Fails when** it's used to argue for adopting LeSS. As a lens the question is about flow
and whole-product thinking; the Scrum-at-scale mechanics are a separate decision that
needs a multi-team problem to justify it.

**Overlaps with systems thinking**, deliberately. That lens hunts feedback loops inside
the system you're building; this one asks whether the organisation building it is the
loop. When a fix keeps failing because three teams must agree, you are in this entry, not
that one.

---

## Sources

- Gojko Adzic, *Impact Mapping* (2012) and *Specification by Example* (2011)
- Simon Wardley, [*Wardley Maps*](https://medium.com/wardleymaps) (CC-licensed)
- Stefan Hofer & Henning Schwentner, *Domain Storytelling* (2021)
- Alberto Brandolini, [*Introducing EventStorming*](https://www.eventstorming.com/book/)
- Eric Evans, *Domain-Driven Design* (2003); Vaughn Vernon, *Implementing DDD* (2013)
- Donella Meadows, *Thinking in Systems* (2008)
- Dave Snowden, [Cynefin](https://cynefin.io/wiki/Cynefin); Snowden & Boone, "A Leader's
  Framework for Decision Making", *HBR* (2007)
- Craig Larman & Bas Vodde, [LeSS principles](https://less.works/less/principles/overview)
- Susanne Kaiser, *Architecture for Flow* (2025) — Wardley mapping, DDD and Team
  Topologies as one chain
