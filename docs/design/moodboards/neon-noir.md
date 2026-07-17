# Moodboard — Neon Noir

> Wrapper: **Sci-Fi** · Mood: **Cyberpunk, rain-lit, moody-crime**
> Story-bible instances: cyberpunk-nightclub after-hours, private-room
> ramen bar, penthouse over a wet city, corporate-arcology executive
> suite, hacker-collective loft.
> Launch skin: none in launch window.
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Draft — no image assets attached (per AW-267 scope: direction only).

## 1. The Pitch

It's raining. It's always raining. Someone at this table has been
paying off someone in this city for a long time and now they can't
find the person they've been paying. Neon Noir is what Nightcap looks
like when it wants to be *Blade Runner* by way of *Cyberpunk 2077* —
wet neon, translucent umbrellas, one warm light source in a cold
frame, and a private booth where the deal is going wrong. The couch
loves this one because it looks *dangerous*: it reads *crime film*
before it reads *party game*, and the interrogation lands hard against
it.

## 2. Reference Set

Steal the specific thing.

- ***Blade Runner* (1982)** — steal the *rain-neon* palette: the exact
  reds and cyans of a wet street; the way umbrellas glow.
- ***Blade Runner 2049* (2017)** — steal the *warm pocket in a cold
  frame*: one Vegas amber against Wallace-cool blue.
- ***Ghost in the Shell* (1995 anime + 2017)** — steal the *silhouette
  discipline*: a face in a booth, half-lit, decisive.
- ***Altered Carbon* (2018–2020)** — steal the *executive-suite noir*:
  penthouse over a bad city.
- ***Cyberpunk: Edgerunners* (2022)** — steal the *tonal balance*: it
  can be flashy and *emotional*; that's what pulls the couch in.
- ***John Wick* (2014–)** — steal the *hotel-as-neutral-ground*
  aesthetic; the Continental staging.
- ***Only God Forgives* (2013) / *Drive* (2011)** — steal the
  *magenta-and-brake-light* neon; the composure inside a threat.
- ***Cowboy Bebop* (1998) — jazz-noir bar scenes** — steal the *booth-
  interrogation* framing.

## 3. The Look

- **Center stage:** a rain-slicked booth, a hotel corridor, a night
  market table, a corporate-arcology suite. Neon signage as the light.
  One warm interior light (a paper lantern, a cigarette, a lamp on a
  desk).
- **Cast rail:** portrait chips as *ID scans* — cyan-outlined hex or
  soft-rounded rectangle, name in a technical grotesk.
- **Phones:** cards are hotel-key cards, encrypted comms, private
  message threads. Private cards have a wet-neon reflection edge.
  Action cards are terminal prompts.

## 4. Palette Anchors

| Role (0069 token) | Anchor | The vibe |
| --- | --- | --- |
| `--theme-glow` | Vegas amber `#F4A94E` | The single warm light in the frame. |
| `--narrator` | Cool paper `#E4EAF2` | Faint hologram-white. |
| `--private` | Neon cyan `#3ED0F0` | Wet-neon signage, translucent umbrella. |
| `--accuse` | Blood magenta `#E23F72` | Bright noir red-pink. Reads *neon crime*. |
| `--ok` | Terminal green `#3BD48F` | The one status light that's working. |

Warmth cue: **cool-flood, warm pocket**. The frame is *cool overall*;
one small warm source pulls the eye. This is the wrapper's signature
frame discipline — *never* two warm lights on stage at once.

## 5. Typography

- **Display face.** A technical grotesk or engineered mono-serif
  hybrid. Reference: *Space Grotesk* (OFL) or an OFL wide grotesk with
  monospaced digits. Beat titles carry chromatic-aberration on the
  reveal frame only.
- **UI face.** Inter (constant).
- **Voice rule.** Narrator never speaks Inter; UI never speaks the
  grotesk.

## 6. Material Vocabulary

- **Surfaces.** Wet asphalt, translucent umbrella, neon-tube glass,
  black leather booth, chrome bar, sushi-counter cypress, hologram
  paper, brass hotel key, water-beaded metal.
- **Card framings.** Identity cards render as ID scans with a cyan
  outline. Private-event cards are encrypted comms with a wet reflection.
  Action cards are terminal prompts.
- **Texture.** A faint rain overlay across the near-black base; a
  faint chromatic-aberration edge on the reveal frame.
- **Cast rail.** Names in the grotesk; portrait slot cyan-outlined
  rectangle. Suspect-stage may show a subtle sensor-lock reticle when
  a suspect is answering.

## 7. Motion Character

- **Cold precision, then a warm cut-in.** Motion is *considered*.
  Beat-turn is a slow neon fade. `seq-spotlight` cross-cuts to the
  warm-lantern pocket.
- **`seq-body`** is the neon buzzing off. The cyan floods out; a
  single warm pixel remains for the silence beat; single line lands;
  resume as the neon comes back on.
- **Ambient is falling rain** at the whisper line — very short period,
  low amplitude. Reduced motion holds the frame steady.

## 8. The Narrator

- **Persona.** The hotel concierge who has seen worse. Or the fixer
  who's been paid to watch. Calm, laconic, faintly amused, decisive.
- **Register.** Noir-adjacent, precise, dry.
- **Sample lines.**
  - *(Beat turn, B2.)* "The rain hasn't stopped. Marcus has. This is
    the kind of night where those two things are almost always related."
  - *(Interrogation stinger.)* "Kent says she was at the noodle bar
    at nine. The noodle bar has never heard of her."
  - *(Reveal.)* "It was in the hotel-key ledger. It was in the ledger
    the entire evening."

## 9. The Showcase Moment (`seq-truth`, Beat 6)

The cyan floods out slowly. One warm lantern remains on stage. Cast
ID scans slide up one at a time — narrator names what each *almost*
caught, ending on a noir-detail (the key-card swipe, the payment
timestamp, the wet umbrella left in the wrong room). The killer's
ID scan lifts to center; the cyan outline snaps to `--accuse` on the
hard-cut line; chromatic aberration blooms once, then settles; the
last line lands in the grotesk at full weight against wet-asphalt
black. The rain resumes. Cut to superlatives.

## 10. Failure Modes (Do Not Ship)

- **Every-color neon wash.** *Two* neons max in frame at any time.
  Discipline is the wrapper's signature.
- **Cyberpunk-outfit shorthand.** No mohawk-and-goggle portraits by
  default. Portraits are ID-scans; costume is *authored*, not chrome.
- **Rain screensaver.** The rain overlay lives on the whisper line
  only. It never fills the frame.
- **Glowing UI everywhere.** Cyan is a *source* on select framing;
  regular chrome stays quiet.

## 11. AW-268 Handoff Slots

- [ ] Reference image collection attached (film stills, cyberpunk
      concept art, night-city photography).
- [ ] Portrait treatment decided (cyan-outlined ID scan recommended).
- [ ] Card framing SVGs authored (ID scan, encrypted comms with wet
      reflection, terminal prompt).
- [ ] Background texture (rain / wet asphalt) SVG or CSS.
- [ ] Chromatic-aberration reveal treatment authored (bounded to reveal
      moment only).
- [ ] Rain-overlay ambient rule authored (period, opacity, reduced-motion
      override).
- [ ] Suspect-stage sensor-lock reticle authored (bounded to
      `seq-spotlight`).
- [ ] Narrator voice fragments authored per 0068 §3.3.
- [ ] Contrast table per parent brief §5 (verify narrator ivory reads
      7:1 over cool-flood backgrounds).
- [ ] Reduced-motion parity screenshots per `seq-*`.
