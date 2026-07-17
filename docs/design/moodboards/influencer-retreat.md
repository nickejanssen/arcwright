# Moodboard — Influencer Retreat

> Wrapper: **Corporate** · Mood: **Goofy-shiny, tropical, over-produced**
> Story-bible instances: influencer retreat, brand-activation weekend,
> reality-TV show set between tapings, bachelorette weekend at a rented
> villa, luxury wellness retreat.
> Launch skin: none in launch window.
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Draft — no image assets attached (per AW-267 scope: direction only).

## 1. The Pitch

A brand paid for the villa. Someone paid to be here. Someone paid *not*
to be here. Everyone is on camera all the time — except when they're
not, which is when the interesting things happen. Influencer Retreat is
what Nightcap looks like when it wants to be *The White Lotus* by way
of *Bachelor in Paradise* — sun, cocktails, over-produced smiles,
lipstick on a champagne flute, and one person face-down in the plunge
pool. This is the couch's *fun-loud* option. Reads *instantly*
attractive: everyone knows this show already, they just don't know who
did it.

## 2. Reference Set

Steal the specific thing.

- ***The White Lotus* (2021, 2022)** — steal the *destination-luxury
  ensemble* framing; the exact way sun hits a lounge chair.
- ***Bachelor in Paradise* (2014–)** — steal the *torch-and-cocktail*
  staging; how "confessional" framing looks.
- ***Vanderpump Rules* (2013–)** — steal the *reality-cast body
  language*: everyone posed for the reveal that hasn't happened yet.
- ***Bodies Bodies Bodies* (2022)** — steal the *phone-lit party
  aesthetic*; a room lit by screens.
- ***The Menu* (2022, opening)** — steal the *arrival-at-luxury* moment.
- ***Emily in Paris* (2020–, aesthetic only)** — steal the *editorial
  saturation*; how a brand-shoot palette works on screen.
- ***Fyre* (2019, cautionary reference)** — steal the *staging of
  performed authenticity*; the *pretending* is the joke.
- ***Selling Sunset* (2019–)** — steal the *architectural real-estate
  glamour*; how a house is presented as content.

## 3. The Look

- **Center stage:** a resort terrace, a private plunge pool, a
  brand-styled sitting room, a tiki bar. Tropical light. Fringe curtains
  moving in the breeze.
- **Cast rail:** portrait chips as *content thumbnails* — soft-rounded
  rectangles, faces framed in warm sunlight, small brand-tag microcopy.
- **Phones:** cards are Polaroids, brand-collab briefs, tour riders.
  Private cards look like DMs or draft posts. Action cards are
  brand-partnership assignment sheets.

## 4. Palette Anchors

| Role (0069 token) | Anchor | The vibe |
| --- | --- | --- |
| `--theme-glow` | Sunset coral `#F4A874` | Golden-hour spray-tan light. |
| `--narrator` | Cream `#F3E9D3` | Editorial magazine cream. |
| `--private` | Ocean teal `#4A9AA8` | Plunge-pool water. |
| `--accuse` | Lipstick `#D0435B` | Bright *editorial* red. Reads *cover shoot*, not *wound*. |
| `--ok` | Palm `#5AA76B` | Palm-shadow green. |

Warmth cue: **golden-hour, always on**. This is the *warmest* of any
wrapper — the frame is bright, tropical, saturated, and the base stays
near-black to keep contrast honest at TV distance.

## 5. Typography

- **Display face.** A rounded editorial serif or a bright modern
  grotesk that photographs *inviting*. Reference: *Fraunces* soft
  optical cut, or an OFL rounded grotesk like *Manrope*. Beat titles
  can carry a small emoji-adjacent glyph (a palm silhouette) as a
  decorative flourish *once* — not persistent.
- **UI face.** Inter (constant).
- **Voice rule.** Narrator never speaks Inter; UI never speaks the
  editorial face.

## 6. Material Vocabulary

- **Surfaces.** Terracotta, rattan, teak, brushed brass, linen, sun-
  bleached cotton, pool tile, palm leaf, glass-fronted mini-bar,
  ring-light glare.
- **Card framings.** Identity cards render as Polaroid stock with a
  brand-tag pin. Private-event cards look like DMs or draft posts.
  Action cards are collab briefs.
- **Texture.** A faint sun-flare across the near-black base; a
  suggestion of ring-light bloom around portrait frames.
- **Cast rail.** Names in the editorial serif; portrait slot
  soft-cornered rectangle; small brand-tag microcopy under the name
  when relevant.

## 7. Motion Character

- **Chirpy, warm, snappy.** Elements arrive with a slight bounce — but
  a *disciplined* bounce, one wave, not cartoon. Beat-turn dim is fast.
- **`seq-body`** is the fastest hard cut in the whole system. Music
  cuts. Palm shadow freezes. Silence beat is long. Single line lands in
  editorial. Resume with the sun a shade lower.
- **Ambient is a palm-shadow drift** across the whisper line — very
  slow parallax, low amplitude. Reduced motion holds it steady.

## 8. The Narrator

- **Persona.** The producer of the show inside the show. Warm on
  camera, sharp off camera. Names the brand, names the fee, names the
  guest who wouldn't sign the release.
- **Register.** Bright, editorial, faintly sardonic.
- **Sample lines.**
  - *(Beat turn, B2.)* "The five-part story-arc has stalled. That's
    because Marcus is in the plunge pool, and Marcus is not, per
    contract, permitted to be face-down."
  - *(Interrogation stinger.)* "Ms. Kent would like the couch to
    understand that at nine she was doing yoga. There is not a mat in
    the frame."
  - *(Reveal.)* "It was in the wellness shot. It was always in the
    wellness shot."

## 9. The Showcase Moment (`seq-truth`, Beat 6)

Ring-light bloom fades to a single warm spot. The cast rail Polaroids
tumble one at a time into center — narrator names what each *almost*
caught, ending on a content-detail (the deleted post, the sponsored
tag, the follower count that spiked). The killer's Polaroid lands
last, brand-tag flickering to `--accuse`; the palm shadow behind
freezes; the last line lands in the editorial face at full weight
against pool-tile black. Cut to superlatives.

## 10. Failure Modes (Do Not Ship)

- **Corporate cringe.** The register is *warm-cynical*, not
  mean-spirited. The comedy is the *setup*, not the participants'
  humiliation. Story-bible §11 world rules unchanged.
- **Fyre-parody meme.** The influence reference is *tonal*, not
  costume. No specific-brand fake logos.
- **Emoji everywhere.** One decorative glyph on a beat title,
  maximum. Emoji-language in UI copy stays out.
- **Blown-out sunset.** Saturation is *directed*; the frame must still
  hit contrast on narrator lines. If the golden hour eats the
  narrator's voice, the shot is failing.

## 11. AW-268 Handoff Slots

- [ ] Reference image collection attached (reality-TV stills, resort
      photography, editorial magazine spreads).
- [ ] Portrait treatment decided (Polaroid soft-corner recommended).
- [ ] Card framing SVGs authored (Polaroid, DM, collab brief).
- [ ] Background texture (sun flare / ring-light bloom) SVG or CSS.
- [ ] Palm-shadow ambient rule authored (period, amplitude,
      reduced-motion override).
- [ ] Narrator voice fragments authored per 0068 §3.3 (brand-safe
      voice — no real brand names inside prompts).
- [ ] Contrast table per parent brief §5 (extra care because glow is
      warm on cream — verify 7:1 narrator on stage).
- [ ] Reduced-motion parity screenshots per `seq-*`.
