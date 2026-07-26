# From Story To Arc — A Worked Example

> Current version: v0.1 DRAFT — founder-directed platform discovery
> Last updated: 2026-07-19
> Status: Draft, awaiting founder review. Not build scope; no arc,
> schema, or engine work is authorized by this document.
> Canonical path: docs/design/authoring/story-to-arc-exemplar.md
> Purpose: the first creative artifact for the platform pillar
> "make it easy to create games and integrate great stories." Shows —
> in an author's own materials, end to end — how a human-written story
> becomes a runnable arc, using a deliberately non-mystery genre.
> Audience: future arc authors (internal first, third-party later),
> and anyone who needs proof the platform is not a mystery engine.

---

## The Premise (What The Author Starts With)

**THE LAST POUR** — a one-night heist story.

> Tonight is the retirement party of Aurelio Marsh, the city's most
> beloved hotelier — and the last night his private vault sits behind
> a security system that gets decommissioned at dawn. The players are
> the crew. They were invited as guests. They intend to leave as
> legends. The house AI, the staff, the other guests, and Marsh
> himself go about the party in real time; the crew must work the
> room, run the plan, and adapt when it breaks — because it always
> breaks.

One page. That is genuinely all an author needs to begin — the
platform's job is to make everything that follows *structured*, not to
make it *big*.

## Authoring Step 1 — The Spine (Beats)

The author writes the experience's fixed skeleton: what MUST happen,
in what order, and what each beat is *for*. Beat count is arc-level,
chosen by the author, not the platform.

| Beat | Structural function | The author's one-line intent |
| --- | --- | --- |
| 1. The Invitation | establish world + crew + goal | "Everyone knows the plan. Nobody knows the whole plan." |
| 2. Working the Room | infiltration; social play | "Charm is a tool. Every conversation is a pick or a tell." |
| 3. The Complication | the plan breaks — deterministically | "Something the crew relied on is gone. Adapt or abort." |
| 4. The Run | execution under pressure | "Split attention: half the crew performs normalcy, half performs the job." |
| 5. The Squeeze | escalation; the almost-caught | "One person can save it. It's never who planned it." |
| 6. The Walk-Out | resolution + accounting | "Whatever happened — walk out like nothing did. Then find out what you actually got away with." |

Note what the author has NOT written: no dialogue, no floor plans, no
guard schedules, no vault contents. Those are runtime-varied. The
*shape* is sacred; the *furniture* changes every session.

## Authoring Step 2 — The Dial (Authored vs. Generative, Per Element)

The platform's core authoring act: for each story element, the author
declares who owns it — the author (fixed forever), the case generator
(resolved fresh each session, then locked), or the runtime layer
(composed live from resolved state). Nothing else on the platform asks
the author to think about AI at all.

| Element | Owner | The author's reasoning |
| --- | --- | --- |
| Beat structure and functions | **Authored** | The heist rhythm IS the story. Never varies. |
| The mark (Marsh), his character bible | **Authored** | The emotional anchor. A great character is written, not rolled. |
| The venue's layout and security systems | **Generated at session start** | Replay demands a new geography every night; fairness demands it be fixed before play begins. |
| The complication (what breaks in Beat 3) | **Generated at session start, from an authored menu** | The author writes 12 great complications; the generator picks and dresses one. Authored quality, generated surprise. |
| Crew roles and their private plan-knowledge | **Generated per player count** | Compartmentalization scales 2–8; the *principle* (nobody knows everything) is authored. |
| Staff and guest AI characters | **Generated within authored constraint rails** | The author defines archetype rails ("a security chief who is proud, not stupid"); generation fills the person. |
| All narrator and character dialogue | **Runtime, composed from resolved state** | Live play needs live language — but only ever *about* facts already resolved. |
| The payout accounting (what you got away with) | **Deterministic from session events** | The ending must be earned, auditable, and argument-proof. |

This table — one per arc — is the whole authored-versus-generative
contract. An author who can fill it in can build on this platform.

## Authoring Step 3 — Constraint Rails (What Generation May Never Do)

The author writes prohibitions with the same care as content. From the
exemplar's rails:

- The complication may change the *route*, never the *goal*.
- No generated character may unmask the crew unprompted; suspicion
  must trace to observable player action (the fairness principle,
  genre-translated: in a mystery it makes clues sufficient; in a
  heist it makes getting caught *deserved*).
- Marsh is never the villain. The party is genuinely in his honor;
  the crew's relationship to that fact is the story's heart.
- Alarm state escalates on a fixed ladder (0 calm → 1 curious →
  2 searching → 3 lockdown); events can climb it, nothing can skip it,
  and every climb is announced diegetically.

## Authoring Step 4 — Character Sheets (One Model, Any Behavior Source)

Every character — player or AI — is the same object: identity,
personality, goals, knowledge state, relationships. The author writes
the important ones fully and writes *rails* for the generated ones.

**Authored (excerpt) — Aurelio Marsh, the mark:**

> Sixty-eight. Built the Meridian from one bad bar. Knows every
> employee's name and most of their debts — he's paid a few, quietly.
> Tonight he is happy, and being happy makes him talkative, and being
> talkative makes him wander — which makes him the crew's biggest
> hazard and the story's conscience. **Goal:** a perfect last night.
> **Knows:** the vault's old combination, which he has told exactly
> one person, once, drunk. **Never:** suspicious first. Marsh trusts.
> That is the point of Marsh.

**Rail (complete) — The Security Chief archetype:**

> Proud, not stupid. Treats the system's decommissioning as a personal
> insult. Wants one flawless final shift. Warms to anyone who respects
> the craft; cools fast on flattery. Knowledge: the patrol schedule
> (full), the vault mechanism (partial), the guest list (annotated).

The generation layer casts a person onto the rail — name, face, voice,
history — and the knowledge graph enforces what they can ever say.
The author never writes "AI instructions." The author writes people.

## Authoring Step 5 — Voice (The Refrain Discipline)

The narrator's line library follows the platform's authored-refrains /
generated-specifics discipline. The author writes the shapes; runtime
fills only slots. Three exemplar refrains to show the genre range:

**Beat 3 drop (the complication lands):**
> The plan survived contact with the evening for {{minutes}} minutes. A personal best, I'm told. {{complication_object}} is gone — and the night, as of now, is improvising.

**Alarm ladder climb (1 → 2):**
> The staff have stopped refilling glasses in the east room. Small thing. It is not a small thing.

**The walk-out (ending shape, any outcome):**
> Doors. Coats. Goodnights. Whatever you are carrying, carry it the way you carried it in — like it weighs nothing. Marsh is waving. Wave back.

## What The Platform Did (And Never Asked The Author To Do)

- Session state, beat transitions, alarm ladder: deterministic
  engine execution of the author's spine and rails.
- Who-knows-what: the knowledge graph, enforced before every line any
  character speaks — compartmentalized plan knowledge is *literally*
  the same infrastructure as mystery clue provenance.
- Casting, venue, complication dressing: generation inside authored
  rails, resolved and frozen at session start.
- Live language: composed from resolved state, in the authored voice,
  slots only.
- Cost: classification and pacing on small models, generation routed
  by quality tier — the author never sees a model name. (Author-facing
  promise; the routing table is the platform's problem.)

**The pitch, compressed:** the author wrote one page of premise, six
beat intents, one ownership table, four rails, two character sheets,
and a line library. The platform turns that into infinite coherent
nights. That is the product.

## Review Notes for the Founder

- This is a *creative exemplar*, not an arc spec. If you approve the
  direction, its natural successors are (1) an authoring-guide doc
  series in this directory, and (2) eventually The Last Pour as a real
  ArcDefinition — both renewable-model work, neither authorized yet.
- The ownership table (Step 2) is, I'd argue, the single most
  investor-legible artifact in the repo: it makes "configurable
  composition" concrete in one screen.
- Deliberate choices to probe: Marsh as un-villainable (rails as
  *story protection*, not just safety), and the alarm ladder as the
  genre-translation of deterministic case truth. If these feel right,
  the platform story generalizes; if they feel forced, tell me where.
