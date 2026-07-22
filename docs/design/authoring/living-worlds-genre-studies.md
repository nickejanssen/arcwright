# Living-Story Genre Studies — Creature Companion & Couch Co-op

> Current version: v0.1 DRAFT — founder-directed discovery (D-083)
> Last updated: 2026-07-19
> Status: Draft, awaiting founder review. Not build scope; the
> future-proofing ledgers below are requirements *observations* for
> architecture awareness, not authorized engine work.
> Canonical path: docs/design/authoring/living-worlds-genre-studies.md
> Authority: `docs/story-bibles/monster-rpg.md` v1.0 (study 1 builds
> on committed canon); reference lineage for study 2: It Takes Two,
> Split Fiction, A Way Out, Unravel 2.
> Purpose: prove, creatively, that the platform's primitive carries
> the two contemplated future game types — and record what each will
> ask of the engine so today's decisions don't foreclose them.

---

# Study 1 — The Creature-Companion RPG

## What The Primitive Becomes Here

The Monster RPG bible already contains the radical sentence: creatures
*witness* the player's choices and become uniquely shaped by what they
witness. On any other stack that's a design aspiration. On this one
it is a *query*: a creature's personality at any moment is a
deterministic function of its provenance chain — every event it saw,
when, and what it meant. The knowledge graph stops being a constraint
system and becomes **the growth system.**

## The Witness Ledger (creative mechanics of memory)

What makes a companion feel alive is not that it remembers — it's
*what kind of thing* it remembers. Proposed authored taxonomy for
witnessed events (the author writes the categories and their
behavioral gravity; sessions fill them):

- **Kindnesses under cost.** The player gave something up for someone.
  Heaviest positive weight — and the creature remembers the *cost*,
  not the gift.
- **Cruelty opposed / cruelty witnessed.** Per the bible's moral
  frame, the player never authors cruelty — but they choose whether
  to stand against it. A creature that watched you walk past
  something is different, forever, from one that watched you stop.
- **Promises.** Small ones. The creature was there when you told the
  ferryman you'd return. It notices the day you do — and the season
  you don't.
- **Defeats taken well or badly.** Sport-battles are non-lethal; what
  a companion learns from losing beside you is how *you* lose.
- **The unshared moment.** Something only this creature saw. The
  bible's uniqueness promise made concrete: no two players' Emberling
  is the same because no two Emberlings *were there* for the same
  life.

**Sample of the feel** (a companion's behavior surfacing memory —
composed language, resolved facts):

> Bramble won't cross the rope bridge tonight. Not stubbornness —
> she's looking at you, then the river. It takes a moment: the last
> time you crossed here, two winters ago, you promised the ferryman
> you'd come back for the festival. Bramble was on your shoulder when
> you said it. The festival is tomorrow.

No line of that is scripted. Every fact in it is a provenance query.
That is the H2 product in one paragraph.

## Future-Proofing Ledger (what this genre asks of the engine)

1. **Knowledge decay and salience.** H1 sessions are hours; a life is
   years of story-time. The graph needs (eventually) salience
   weighting and memory *texture* — what fades, what crystallizes,
   what returns when triggered. Schema-clean now: provenance already
   timestamps everything; salience is a computed layer, not a
   migration.
2. **Story-time vs. wall-clock.** Persistent world clock decoupled
   from session time; the platform's session model must not assume
   session == story episode. (Bible already flags story-time; the
   engine seam to protect is event timestamps carrying both clocks.)
3. **Character state as derived view.** A companion's personality =
   f(provenance chain). Demands cheap materialized views over long
   chains — an indexing problem, not an architecture problem, *if*
   chains stay append-only. They must stay append-only.
4. **Cross-session continuity as default** (Nightcap's D-051
   continuity is the fast-follow seed of this).
5. **Solo-adaptive pacing** — shared with Daily Case; the engine's
   pacing signals must never assume a group.

# Study 2 — Couch Co-op (the It Takes Two lane)

## What The Primitive Becomes Here

The co-op masterpieces (It Takes Two, A Way Out, Split Fiction,
Unravel 2) all monetize one design law: **two players, asymmetric
information and ability, forced interdependence.** Today that
asymmetry is hand-built — every puzzle authored twice, every "you see
this, they see that" scripted per room. Which is why there are four
great co-op story games a decade, not four hundred.

Arcwright generalizes the law: asymmetric knowledge is *literally what
the knowledge graph does.* Give two players different provenance and
every conversation becomes a mechanic; the puzzle is each other. The
authored spine guarantees the drama; the runtime personalizes who
holds which half of every truth.

## Worked Mini-Exemplar — "THE LONG THAW" (non-crime, two-player)

*(Also serves as the second authoring exemplar: no crime, no
mystery — a relationship story with weather.)*

**Premise (one page, author-written):** Two estranged siblings return
to their grandmother's mountain cottage to close it up for the last
winter. A storm seals them in for three days. The cottage is full of
their childhood — and their grandmother, it turns out, left the house
*arranged*: objects, letters, and unfinished tasks deliberately placed
to make her grandchildren finish their oldest argument before the
road clears.

**The dial:** the sibling relationship's wound is authored (anchor);
which memories surface, which objects carry them, and what the
grandmother arranged varies per playthrough (axes). The storm is the
clock; the reconciliation beats are the spine; whether it *lands* as
forgiveness, understanding, or honest goodbye is played, not scripted.

**Asymmetry as the core loop:** each sibling receives private
memories — the same childhood events, remembered differently, because
the knowledge graph gives each player a different provenance for the
same facts. Progress requires *telling each other* — out loud, on the
couch — and the engine listens for the reconciled record:

> **Player 1 (private):** You remember the lake dock: the day she let
> you take the boat alone. You were nine. Your brother stayed home.
> He always stayed home.
> **Player 2 (private):** You remember the lake dock: the day of the
> boat, you asked to come. Dad said no — someone had to help with the
> nets. You watched from the window. You never told anyone you asked.

Neither memory is false. The *union* is the story. The grandmother's
arrangement (deterministic, resolved at session start) is built so
that only the union opens the next room of the house — Unravel 2's
rope, rebuilt out of knowledge instead of yarn.

**Vesper note:** this genre wants no host. The narrator is the house
and the weather — presentation hints and refrain shapes without a
persona. The platform's narrator layer must therefore support
*personaless* voice. (Future-proofing item 4.)

## Future-Proofing Ledger (co-op)

1. **Per-player private channels as first-class** — already true
   (Nightcap phones). Protect it as surfaces multiply.
2. **Reconciliation events**: the engine needs a native event for
   "players merged private knowledge" (today: claims/flags; tomorrow:
   shared-understanding records). Schema-adjacent to the claim
   ledger — the co-op genre is the claim ledger pointed at intimacy
   instead of interrogation.
3. **Joint pacing**: tension signals over a *pair*, detecting the
   couch talking (good stall) vs. stuck (bad stall). Sensor-agnostic
   today, richer signals later (frontier-vision room-sense seam).
4. **Personaless narration**: voice layer must run with persona
   detached — refrain discipline without a host character.
5. **Session handoff for two** — co-op continuity (pause Tuesday,
   resume Friday) rides the same continuity infrastructure as H2's
   life-chapters. One build, three genres.

# The Cross-Genre Truth (why this is one platform)

Four genres now studied — party mystery, daily interrogation,
creature life, co-op intimacy. The same short list carries all four:

| Primitive | Mystery | Daily Case | Creature RPG | Co-op |
| --- | --- | --- | --- | --- |
| Knowledge provenance | lies you can catch | claims that accumulate | memory that shapes character | asymmetry that forces talk |
| Deterministic truth | case fairness | week-long fairness | world history | the grandmother's arrangement |
| Authored spine + rails | six beats | seven days | life chapters | three-day storm |
| Refrain voice discipline | the host | the handler | world barks | the personaless house |
| Private channels | detective phones | one device | companion bond | sibling memories |

Nothing on that list is genre code. That's the platform argument in
one table — and the reason "make it easy to create games" is
credible: authors pick a row's *meaning*, never rebuild its machinery.

## Review Notes for the Founder

- Study 1's witness taxonomy is proposed canon-compatible extension
  material for the Monster RPG bible — if the categories feel right,
  they belong in a future bible revision (your call, renewable model).
- The Long Thaw is deliberately the *anti-crime* exemplar: if the
  platform story convinces on grief-and-weather, no one can call the
  engine a whodunit machine again. It's also, honestly, a game I
  believe in — flag if you want it kept as a real candidate rather
  than an exhibit.
- The two future-proofing ledgers name **zero build-now items** —
  every entry is either already-true, schema-clean, or a seam to
  protect. The single decision with present-day teeth: **provenance
  chains stay append-only, forever.** That one rule is what keeps
  every horizon reachable.
