# 0068 — Game Experience Quality Bar

> Current version: v1.0
> Last updated: 2026-07-12
> Status: Draft (founder review → Approved)
> Author: Strategy/design session 2026-07-12
> Canonical path: docs/specs/0068-game-experience-quality-bar.md

## References

- `docs/story-bibles/nightcap-murder-mystery.md` (Sections 1–4; the story
  bible owns *what* Nightcap is — this spec owns *how good it must feel*)
- `docs/superpowers/specs/2026-07-12-arcwright-strategic-blueprint-design.md` §3
- `docs/prd/02-requirements.md` (success criteria: qualitative gate and
  personalization perception gate)
- `docs/roadmap/operations/fun-observation-rubric.md` (companion instrument)
- `docs/conventions/mini-game-authoring.md`
- ADR-0012 (authorial intent and per-beat emotional targets — the future
  engine home for several targets defined here)

## Overview

The MVP gates measure whether players *finished* and *wanted to come back*.
This spec defines the design standards that make those outcomes likely: what
"extremely fun," "high quality," and "beautiful" mean concretely, per moment,
in testable language. It is a **game-layer content and presentation spec**.
It requires no engine changes; everything here is implemented in arc content
(`nightcap/arc.json`), game-layer prompt configuration, web presentation, and
playtest instrumentation. Engine neutrality is preserved: nothing in this
spec becomes a platform capability.

Two constraints frame everything:

1. **Prompt and content-generation changes are a Hard Rule item** — where a
   standard below implies changing generation prompts, the standard is
   binding once this spec is Approved, and the implementation goes through
   normal review.
2. **Nothing here expands product scope.** The eight-beat structure, mini-game
   set, accusation mechanics, and v1/v1.1 boundaries are untouched. This spec
   raises the bar *inside* approved scope.

## In Scope

- Fun pillars and the per-beat quality bar for Nightcap v1.
- Content writing standards: character identity cards, clues, narrator voice.
- Killer experience standard.
- Mini-game feel standard (within the existing runtime).
- Aesthetic direction charter (input to M5-G visual identity work).
- Fun instrumentation: the observation rubric and its telemetry mapping.
- Quality principles for Daily Case and Monster RPG design phases.

## Out of Scope

- Engine or schema changes of any kind.
- New mini-games, new beats, new mechanics.
- Audio/music system (named below as a post-M6 candidate only).
- Continuity features (v1.1, D-051 boundary respected).
- Numeric pacing-engine tuning (owned by the pacing engine; this spec sets
  player-facing tempo *targets* the game layer requests, not engine internals).

---

## 1. Fun Pillars (Nightcap)

Every content, presentation, and tuning decision must serve at least one
pillar. A change that serves none is decoration; a change that damages one
needs a reason.

| # | Pillar | One-line test |
| --- | --- | --- |
| P1 | **Delicious suspicion** | Players accuse each other *unprompted* between beats |
| P2 | **Being someone** | Players speak in first person as their character without being told to |
| P3 | **The gasp** | At least one audible group reaction per session to a revelation |
| P4 | **Nobody left out** | Every player gets ≥1 private moment that only they could act on |
| P5 | **The room is the stage** | Eyes go up to the shared display at dramatic moments, down to phones for secrets — never confusion about where to look |

## 2. Moment Map: Per-Beat Quality Bar

The eight beats are fixed (story bible §4). For each: design intent, the
quality bar, and failure smells observable in rehearsals. The rubric doc
turns these into a tally sheet.

**B1 — The Arrival.** *Intent: put players inside someone else's skin fast.*
Bar: every player has read their identity card and can answer "who are you
and what do you want tonight?" within 3 minutes of joining; at least one
laugh or "ohhh no" during card reading. Failure smells: players read cards
silently and set phones down; players ask "wait, who am I?"; host explains
rules for more than 60 seconds.

**B2 — The Body.** *Intent: tonal turn — the party is now a crime scene, and
it's delightful.* Bar: the death lands as a staged shared-display moment
(full-screen, paced text, not a chat line); the room goes quiet, then erupts.
Failure smells: the murder announcement scrolls by; players miss it; nobody
looks up.

**B3 — The Opening Move.** *Intent: teach the verbs by doing, not by rules
text.* Bar: within this beat every player has done one investigative action
and knows the accusation-token rule (one token, whole night — the game's
core tension). Failure smells: any player still asking "what do I do?";
tokens explained but not felt.

**B4 — The Dig.** *Intent: the engine's personalization becomes visible —
clues start pointing at people in this room.* Bar: at least two clues
provoke table talk directed at a specific player; mini-game #1 lands here as
competition, not homework. Failure smells: clues read like generic flavor
text; players discuss the *game* instead of the *suspects*.

**B5 — The Thread.** *Intent: theories form; the killer starts sweating.*
Bar: at least one player states a theory aloud connecting ≥2 clues; the
killer has received ≥1 prompted action opportunity and taken it. Failure
smells: clue pile-up with no synthesis; killer passive because misdirection
costs more than it pays.

**B6 — The Reckoning.** *Intent: peak social pressure — this is the beat
people film.* Bar: accusations happen in a staged spotlight (named,
dramatic, on the shared display), never as a menu-click that resolves in
silence. Every accusation resolution changes the room's information state
visibly. Failure smells: accusation resolves in under 5 seconds of screen
time; a wrong accusation feels like a wasted turn instead of a story event.

**B7 — The Close.** *Intent: the last chance — make hesitation expensive and
courage rewarded.* Bar: remaining-token scarcity is visible to all; the beat
has a countdown quality. Failure smells: the session drifts here; players
don't realize the endgame has begun.

**B8 — The Truth.** *Intent: a reveal worth earning — narrative, personal,
filmed.* Bar: the reveal is a **story sequence, not a scoreboard**: the
narrator reconstructs the night, names what each player almost caught,
celebrates the killer's best deception, then lands the truth. Every player
is mentioned by character name at least once. Target length 90–150 seconds
of staged shared-display time. Failure smells: instant "The killer was X"
card; players checking phones during their own finale.

**Tempo rule (all beats):** no player-facing dead air longer than ~20
seconds — some surface (shared display or phone) should always be giving
somebody something to read, do, or suspect. Rehearsal observers time the
three longest gaps.

## 3. Content Writing Standards

### 3.1 Character identity cards (the first personalization proof)

Format bar — every generated identity card contains, in this order:
1. Name + evocative role tag ("Vivienne Ashford — the widow who arrived early").
2. Relationship to the victim in one sentence.
3. **One secret** ("You owe the victim money. Nobody here knows.").
4. **One want** for tonight (playable at the table, not backstory).
5. **One instruction** — a concrete verb the player can perform in the next
   ten minutes ("Find out why Marcus left the terrace at nine.").

Quality tests (all three must pass for every role slot in every theme):
- **Read-aloud test:** a stranger reading the card aloud sounds like a
  person, not a database row.
- **Actionability test:** the instruction can be performed without any
  further information.
- **Tension test:** the secret, if exposed, would change how the table
  treats this player.

### 3.2 Clues

Every clue must do all three: (a) **point** — implicate or exonerate a
specific character; (b) **be sayable** — phrased so a player can read it
aloud and start an argument; (c) **carry the world** — one concrete sensory
or period detail from the session's theme. No filler clues: if a clue exists
only to occupy a slot, cut the slot. False clues must be *fair*: after the
reveal, a player should be able to see why it was false ("the lipstick was
the wrong shade" — checkable in retrospect), never arbitrary.

### 3.3 Narrator voice

One persona per session, aesthetic-linked, consistent from first line to
last. Rules: addresses players only by character name; short lines on the
shared display (target ≤ 2 sentences per screen, legible from across a
room); dry wit allowed, mockery of players never; makes ≥2 callbacks per
session to intake-seed details (the cheapest personalization-perception
wins available). The narrator is the product's voice — treat narrator lines
with the same review severity as UI copy.

## 4. The Killer Experience Standard

Being the killer must be the *best* seat in the house, because "next time I
want to be the killer" is the replay engine.

- **The revelation moment** is staged like a gift: full-phone-screen private
  sequence — "It was you." — followed immediately by *what you know* (how,
  why) and *what to do next* (first misdirection suggestion). Never a plain
  status change.
- **Prompted actions are missions, not chores:** each has a stated payoff
  ("steer suspicion toward the Colonel — his alibi has a hole you know
  about") and a visible consequence when executed.
- **Losing is still winning:** The Truth beat must celebrate the killer's
  best move by name ("...and no one ever asked about the second glass —
  Vivienne made sure of that"). A caught killer should feel like the star of
  the story, not the loser of a quiz.

## 5. Mini-Game Feel Standard

Within the existing runtime (no new games), every mini-game moment meets:

1. **Instant response:** local input feedback under ~100ms (visual press
   states, optimistic UI) even when resolution is server-side.
2. **Legible stakes before play:** one line — what winning earns (clue
   access, standing) — shown before the timer starts.
3. **Countdown tension:** timers visible and dramatized in the final 5
   seconds on both surfaces.
4. **Spectacle resolution:** results land on the *shared display* as a
   moment (rankings revealed with rhythm, not dumped), because losing
   publicly and gracefully is party-game fuel.
5. **Short:** 90–120 seconds ceiling per mini-game round; the mystery is the
   game, mini-games are spice.

## 6. Aesthetic Direction Charter (input to M5-G)

> Execution-level detail (tokens, typography, color, layout, motion
> choreography, theme skins, refactor path) lives in
> `docs/specs/0069-nightcap-visual-design-system.md`. This section states
> the principles that spec implements.

Principles, so M5-G execution has a target instead of taste-by-committee:

- **Theme is the art director.** Era + occasion drive palette, type flavor,
  and narrator persona as one coherent set. Ship few themes finished rather
  than many themes thin (story bible already sets pre-produced-first).
- **TV typography:** shared display text legible at 3 meters; hierarchy of
  exactly three levels (narrator line / event title / supporting detail);
  no paragraph walls on the TV, ever.
- **Motion budget:** one dramatic staged transition per beat (the beat-turn
  is the drumbeat of the night); everything else restrained. Motion signals
  "something story-level happened" — spending it on button hovers deflates
  the reveals.
- **Phone surface is intimate:** private events styled as *yours* —
  letter/dossier/telegram framing per theme — visually distinct from public
  info so the privacy model is felt, not explained (supports P5 and the
  privacy-by-design requirement).
- **The reveal is the visual centerpiece:** B8 gets the largest share of
  presentation polish in any craft pass, then B2, then B6. Priority order is
  binding when time is short.
- **Audio (post-M6 candidate, not committed):** a five-stinger set (arrival,
  body, accusation, wrong-accusation, truth) is the highest-value minimal
  audio investment if/when audio enters scope. Logged here so M6 evidence
  can confirm or kill it. `[NOT APPROVED SCOPE]`

## 7. Fun Instrumentation

Human signals (collected via `docs/roadmap/operations/fun-observation-rubric.md`
at every rehearsal and qualifying session):
- Time-to-first-laugh; laughs/gasps per beat (tally);
- lean-in moments (phones down, bodies forward);
- unprompted in-character speech instances (P2);
- unprompted accusations between beats (P1);
- the three longest dead-air gaps (tempo rule);
- verbatim quote capture: anything a player says that references a
  personalized detail (this is the PRD personalization-perception evidence).

Telemetry mapping (existing signals, no new engine work): beat engagement
duration ↔ tempo rule; replay-intent indicator ↔ pillar outcome; pacing
intervention triggers ↔ B4–B7 drift. Human rubric and telemetry are
reviewed together after each session.

## 8. Sister-Game Quality Principles (design-phase inputs)

**Daily Case:** the fun atom is the *caught contradiction* — the player,
not the game, notices the suspect's story changed. Bar: every daily session
ends on a hook (small reveal or tension raise); contradiction payoffs are
player-earned (the ledger surfaces what the player flagged, it does not
auto-solve); the suspect has one voice, held for seven days. Five minutes
means five minutes — a session that runs long is a defect, not a bonus.

**Monster RPG:** the fun atom is *being witnessed* — companions visibly
shaped by what the player chose. Bar (for the Chat 8+ design phase): every
chapter ends at a narrative-meaningful close with a forward thread; at least
one companion reaction per chapter must reference a specific past player
choice. Latency and per-chapter cost budgets belong in the design brief from
day one (blueprint §3.4).

---

## Acceptance Criteria

This spec is satisfied for Nightcap v1 when:

1. All role slots in every shipped theme pass the three identity-card tests
   (§3.1) — verified by content review checklist.
2. Clue generation output passes the point/sayable/world checks (§3.2) on a
   sampled basis per theme — verified in content review + rehearsal
   observation.
3. B2, B6, and B8 are staged sequences on the shared display (not instant
   cards), with B8 meeting the story-sequence bar (§2) — verified by
   founder walkthrough.
4. The killer revelation and ≥1 prompted action meet §4 — verified by
   walkthrough + killer-player debrief question in the rubric.
5. Mini-game moments meet all five feel rules (§5) — verified on real
   devices during rehearsal.
6. The fun-observation rubric is completed for Rehearsal 1, Rehearsal 2, and
   all M6 qualifying sessions, and its findings are triaged with the blocker
   log.
7. Any prompt/content changes made to meet these bars went through the Hard
   Rules approval flow.

## Test Plan

- Content standards: reviewed via checklist during content/prompt PR review
  (extend `docs/conventions/review-checklist.md` reference when first used).
- Presentation standards: manual verification on real devices (phone +
  TV-distance display) during the founder solo smoke test and Rehearsal 1.
- Instrumentation: rubric completed at every human session; quotes and
  tallies committed alongside the blocker log.

## Risks / Unknowns

- Staged sequences (B2/B6/B8) add presentation work in `nightcap-web`;
  if Rehearsal 1 shows the current instant-card versions already land,
  scope the staging down rather than gold-plating. Evidence first.
- The tempo rule's 20-second ceiling is a hypothesis; Rehearsal 1 timing
  data sets the real number.
- Over-instrumenting a living room can kill the vibe it measures; the
  rubric is designed for one observer tallying quietly, not a lab.

## Open Questions

- Q: Should per-beat emotional targets from this spec's moment map become
  the authored-intent metadata when ADR-0012 (M5-H) is implemented? (Natural
  fit; decide at M5-H planning.)
- Q: Audio stinger set — post-M6 evidence decision (§6).
