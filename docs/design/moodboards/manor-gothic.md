# Moodboard — Manor Gothic

> Wrapper: **High Society** · Mood: **Spooky, elegant, unsettled**
> Story-bible instances: Victorian manor dinner, Edwardian country
> weekend, family-estate reading of the will, memorial gathering.
> Launch skin: none in launch window (Séance 1928 is High Society's
> launch instance).
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Draft — no image assets attached (per AW-267 scope: direction only).

## 1. The Pitch

The house is older than everyone in it. The wallpaper knows what
happened. Rain on the windows. Wet stone. A cousin nobody invited.
Manor Gothic is what Nightcap looks like when it wants to be *Crimson
Peak* by way of *Wednesday* — moody, funny in a dry way, unsettled but
never cruel. The couch loves this one because it feels like *Clue* the
movie: the storm, the manor, the ensemble, the reveal in the study.

## 2. Reference Set

Steal the specific thing.

- ***Crimson Peak* (2015)** — steal the *architecture as character*:
  ceilings that read as complicit, a house that breathes.
- ***Wednesday* (2022–)** — steal the *dry-comic gothic*: the ability to
  land a joke in a room this dark; the confident silhouette.
- ***The Haunting of Bly Manor* (2020)** — steal the *ensemble grief*:
  a group of people orbiting a room they should have left.
- ***Rebecca* (2020 and 1940)** — steal the *scale*: staircases,
  windows, the way distance in a hall reads as social distance.
- ***Gosford Park* (2001)** — steal the *class geometry*: upstairs vs.
  downstairs staged inside the same shot.
- ***Clue* (1985)** — steal the *ensemble-in-a-manor comedy*: the
  reveal-in-the-library shot; the door montage; the pace.
- ***Only Murders in the Building* (2021–)** — steal the *modern-warm
  gothic*: how a dark palette can still feel *cozy*.
- ***The Fall of the House of Usher* (2023, Netflix)** — steal the
  *staged theatricality of the reveal*; how mood carries the plot.

## 3. The Look

- **Center stage:** a manor interior — the study, the great hall, the
  landing, the conservatory. Tall windows with weather in them. Deep
  shadow at the edges of the frame.
- **Cast rail:** black-oval silhouettes with a gilt hairline, or a small
  Victorian daguerreotype card when portraits exist.
- **Phones:** letters on cream stock. Private cards use a black wax seal.
  Action cards are corner-marked as coming from a specific room of the
  house ("the study," "the library").

## 4. Palette Anchors

| Role (0069 token) | Anchor | The vibe |
| --- | --- | --- |
| `--theme-glow` | Cold gilt `#B8955A` | Wall sconces, gaslight, tarnished ormolu. |
| `--narrator` | Bone `#DAD3C4` | Cool cream. Reads *paper*, not *ivory*. |
| `--private` | Storm slate `#7C8B9F` | Rain on a window. A note passed between wings. |
| `--accuse` | Dried-blood burgundy `#5E1B26` | Older red. Reads *stain*, not *fresh*. |
| `--ok` | Moss `#5E876A` | Damp botanical. Reads *conservatory*, not *garden*. |

Warmth cue: **warm-source under weather**. Warm light exists (sconces,
fires) but the frame keeps a cool overtone from rain, from stone, from
the outside pressing in.

## 5. Typography

- **Display face.** A high-contrast serif with weight — an OFL cut of a
  Bodoni or Didone-adjacent register. Reference: *Playfair Display*
  (OFL). Verify legibility at 28px TV floor.
- **UI face.** Inter (constant).
- **Voice rule.** Narrator never speaks Inter; UI never speaks the
  gothic display face.

## 6. Material Vocabulary

- **Surfaces.** Dark wood paneling, cracked plaster, wet stone, aged
  leather, brass door handles, cameo silhouettes, black wax, cream
  paper, moss under glass.
- **Card framings.** Identity cards are engraved on cream stock with a
  black seal. Private-event cards are folded letters with a broken seal.
  Action cards are labelled with a room of the house.
- **Texture.** A faint rain overlay at the whisper line only. A subtle
  vignette that darkens the edges. Never a photographed haunted-house
  filter.
- **Cast rail.** Names set in the display face on black; small daguerre-
  otype portrait slot in a gilt hairline when assets exist.

## 7. Motion Character

- **Draw the curtain.** Beat-turns feel like a heavy velvet dropping —
  slow dim, held silence, resume. Elements enter *sliding* rather than
  landing.
- **`seq-body` is a sudden opening of a door** — the stage snaps darker,
  the rain seems to get louder for the silence beat, then a single line.
- **A distant chime marks accusations.** Ambient hairline on the cast
  rail pulses once, quietly, on `seq-spotlight` open. Reduced motion
  drops the pulse and holds the frame.

## 8. The Host — Vesper as the House's Housekeeper

**See** [`the-host.md`](../the-host.md) for Vesper's bible. This board
names her role in this wrapper.

- **Vesper's role tonight.** The housekeeper who has been here longer
  than anyone can remember. Not spooky. *Certain*. She has already
  worked out who did it and is choosing when to say so.
- **Register.** Cool, precise, unshockable, faintly amused at the
  guests' disbelief. Vesper's most contained voice — the shift lands
  harder against this baseline.
- **Cast-rail silhouette shape.** Daguerreotype portrait in a gilt
  hairline oval on black.
- **Sample lines.**
  - *(Opening — jubilant, quiet.)* "The house is in good spirits
    tonight. The east wing is warm — someone remembered to lay a
    fire. Someone else, I am afraid, has remembered too much."
  - *(Beat turn, B2 — grave.)* "The east wing has always been cold.
    This is not, tonight, the reason."
  - *(Interrogation stinger.)* "Mrs. Halloway would like the record
    to show she has never been in the study. The record is uncertain.
    The record is often uncertain about Mrs. Halloway."
  - *(The Wink.)* "You are watching this from a room I cannot see. I
    have decided to imagine it as warm and well-lit. Do continue."
  - *(Reveal.)* "The house has known since the portrait was hung. It
    has been patient about telling us. — He was in the library. Of
    course he was."

## 9. The Showcase Moment (`seq-truth`, Beat 6)

The rain gets louder. The whisper line dims to black. One by one the
suspect chips slide back into their frames along the cast rail; the
narrator names the room where each was really standing at nine. When
the killer's chip is named, the gilt hairline around its frame turns
`--accuse`; the storm outside cuts to silence; the last line lands in
the display face at full weight against the wet-stone base. Curtain.

## 10. Failure Modes (Do Not Ship)

- **Halloween store gothic.** No cobwebs, no jump scares, no plastic
  candelabra. The mood is *unsettled*, not *spooky-costume*.
- **Grimdark washout.** The frame stays legible. If the narrator line
  hits under 7:1 contrast on the base, the frame is too dark.
- **Excess weather.** Rain is a hint, not a screensaver. Ambient overlay
  stays on the whisper line only.
- **Comic-book vampire fonts.** The display face is editorial gothic,
  not Halloween-Party font.

## 11. AW-268 Handoff Slots

- [ ] Reference image collection attached (film stills, interior
      photography, gothic manor architecture).
- [ ] Portrait treatment decided (daguerreotype recommended).
- [ ] Card framing SVGs authored (sealed letter, engraved card, room
      badge).
- [ ] Background texture (wet stone / storm vignette) SVG or CSS.
- [ ] Rain whisper-line overlay authored (period, opacity, reduced-motion
      override).
- [ ] Distant chime cue slot named for `seq-spotlight` (audio in AW-268
      per 0068 §6).
- [ ] Narrator voice fragments authored per 0068 §3.3.
- [ ] Contrast table per parent brief §5.
- [ ] Reduced-motion parity screenshots per `seq-*`.
