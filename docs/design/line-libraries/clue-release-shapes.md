# Clue Release Content Shapes — Discovery Packet (AW-280)

> Current version: v0.1 DRAFT — discovery material, NOT a locked direction
> Last updated: 2026-07-19
> Status: Awaiting founder direction selection (AW-280 creative-collaboration
> contract requires founder discovery; founder was unavailable this session,
> so per the human-collaboration contract this stops at reversible research)
> Canonical path: docs/design/line-libraries/clue-release-shapes.md
> Feeds: AW-280 (clue release content)
> Wrapper used for samples: Séance 1928

## What This Is And Is Not

Three candidate clue-writing directions, each with samples across the
four delivery types (group, private, split, targeted) plus red-herring
and failure examples. **No direction is chosen.** The founder picks one
(or blends) in the AW-280 discovery interview; then a full clue-shape
library gets authored against the winner.

Fixed constraints all three directions share (from AW-280, non-negotiable):

- Every clue points toward or away from a specific suspect; provenance
  traces to resolved case truth. Language composition never invents or
  alters truth.
- Red herrings are authorized lies, deterministically falsifiable after
  the reveal.
- Clues must be **sayable aloud** — a player reads a private clue to the
  couch in one breath and it survives the retelling (this is how private
  information enters the social game).
- Evidence-to-intent unlocks come from resolved state; the clue text
  only *announces* them.

---

## Direction A — "The Object Speaks" (world-forward)

Clues are physical things described with sensory specificity. The
inference is left to the player; the object never editorializes.
Closest to *Knives Out*: the donut hole is just a donut hole until you
see it.

**Sample — group (TV, The Scene):**
> The fireplace has been lit twice tonight. Once with wood. Once, briefly, with paper — a corner survived: heavy stock, cream, a wax seal broken along the fold.

**Sample — private (phone, The Scene):**
> Only you noticed: {{suspect}}'s gloves are on the hall table. Kid leather, still buttoned. Nobody takes off buttoned gloves quickly — and nobody buttons them again while frightened.

**Sample — split (two phones, complementary halves):**
> *(Half 1)* The decanter on the sideboard is missing its stopper.
> *(Half 2)* There is a crystal stopper in the conservatory. It does not match the conservatory.

**Sample — targeted (unlocks an intent):**
> The telegram in {{victim}}'s coat was sent at {{time}} — from the post desk *inside this house*. — *Unlocks: press {{suspect}} on their whereabouts at {{time}}.*

**Authorized red herring (falsifiable):**
> A second wine glass sits near the body, lipstick on the rim. *(Truth ledger: planted by {{suspect_2}} to implicate; the shade matches no one present — checkable against the cast dossier after reveal.)*

**Failure example (breaks the direction):**
> ~~"A suspicious glass suggests someone else was there!"~~ — editorializes ("suspicious," "suggests"), does the player's inference for them, names no checkable detail.

- **Strengths:** maximum immersion; clues feel *found*, not served; retell beautifully aloud.
- **Risks:** highest comprehension floor; a tired couch may miss the point of an unglossed object; hardest to generate fairly at runtime (specificity must still trace to the clue web).

## Direction B — "Testimony And Rumor" (voice-forward)

Clues arrive as things *people* said or saw — staff whispers, an
overheard line, a suspect's own contradiction surfacing. The social
web is the evidence. Closest to *Poirot*: the housemaid saw something.

**Sample — group (TV, The Grill):**
> The kitchen has been talking. The evening's second course was delayed — because someone asked the cook, at {{time}}, to re-warm a plate that had already been served. The cook remembers the hands, not the face.

**Sample — private (phone):**
> You were near the cloakroom earlier. You heard it clearly: {{suspect}}, low, urgent — "not until the toast, do you understand me?" You did not hear the answer.

**Sample — split:**
> *(Half 1)* The valet swears {{suspect}} never left the parlor.
> *(Half 2)* The parlor has a service door. The valet cannot see it from his post.

**Sample — targeted (unlocks an intent):**
> {{suspect_2}} mentioned "the argument by the fountain" to three separate guests — but claims not to have gone outside. — *Unlocks: confront {{suspect_2}} with the fountain.*

**Authorized red herring (falsifiable):**
> A guest insists they saw {{suspect}} burning papers at midnight. *(Truth ledger: the guest is mistaken — it was the butler disposing of menus; butler's testimony and the menu ash are both in the resolved web.)*

**Failure example:**
> ~~"Someone says {{suspect}} is probably the killer."~~ — hearsay with no checkable anchor, no provenance, accuses directly instead of evidencing.

- **Strengths:** feeds the interrogation loop directly (testimony begs to be tested against suspects); easiest to make sayable; naturally social.
- **Risks:** can blur with suspect dialogue (two voices of "people said things"); heavy testimony load makes the clue web feel like gossip rather than evidence.

## Direction C — "The Detective's Ledger" (analysis-forward)

Clues arrive pre-framed as entries in an investigation — timestamped,
cross-referenced, gaps made explicit. The game shows its bones
elegantly. Closest to the *Obra Dinn* / case-board fantasy.

**Sample — group (TV, The Scene):**
> ENTRY 4 — {{location}}, {{time}}. Window latched from inside. Door key accounted for. Whoever left this room left it through the house.

**Sample — private (phone):**
> ENTRY 7 (yours alone) — {{suspect}}'s account of {{time}} leaves nine minutes unclaimed. Nine minutes is not long. It was long enough.

**Sample — split:**
> *(Half 1)* ENTRY 9a — The cellar logs six bottles brought up tonight.
> *(Half 2)* ENTRY 9b — The sideboard holds five.

**Sample — targeted (unlocks an intent):**
> ENTRY 12 — {{evidence}} carries two sets of fingermarks. One belongs to {{victim}}. — *Unlocks: demand {{suspect}} account for touching {{evidence}}.*

**Authorized red herring (falsifiable):**
> ENTRY 6 — A muddied bootprint by the terrace door, pointing in. *(Truth ledger: the gardener's, from before the party; the gardener's departure time is in the resolved web.)*

**Failure example:**
> ~~"ENTRY 8 — {{suspect}} is lying about something."~~ — a conclusion, not an observation; unfalsifiable; does the game's job for it.

- **Strengths:** clearest fairness signal (players *see* the case being built); lowest comprehension floor; gaps-made-explicit is a strong hook for question intents.
- **Risks:** coolest register — fights the Séance warmth; the ledger frame is a *system* voice, and Nightcap's rule is the narrator has one voice and the UI another (this becomes a third).

## Recommendation (advisory only — founder picks)

**A as the spine, B as the release valve.** Objects for scene/twist
waves (immersion peaks), testimony for grill-phase releases (feeds
interrogation directly). Hold C's *discipline* (every clue names a
checkable anchor) as a writing rule inside A and B rather than as a
surface register — that keeps the fairness without the third voice.

## D-070 Presentation Hints (applies to any direction)

| Delivery | Hints suggestion |
| --- | --- |
| Group (TV) | `moment: evidence-wave`, `style: exhibit`, `dwell: long` |
| Private (phone) | `style: telegram` or `style: field-note`, `reveal: fast` |
| Split | `style: torn-page`, marks its half as `1-of-2` |
| Targeted+unlock | `style: exhibit-tag`, `unlock-flourish: true` |

## Founder Interview Questions (for the AW-280 discovery pass)

1. Which direction (or blend) — and does the recommendation hold?
2. How hard may red herrings bite? (Current samples implicate real
   suspects; alternative: herrings only muddy timelines, never point.)
3. Should private clues *ever* be duds (realism) or always matter
   (respect for scarce attention)? Recommendation: always matter.
4. Sayability bar: one breath (current) or up to three sentences?
