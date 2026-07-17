# Moodboard — Sim Reunion

> Wrapper: **Sci-Fi** · Mood: **Absurd-melancholic, uncanny-cheerful, goofy**
> Story-bible instances: uploaded-consciousness reunion, sim-world
> office party, afterlife lobby gathering, VR-holiday time-loop dinner,
> corporate-metaverse product launch.
> Launch skin: none in launch window.
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Draft — no image assets attached (per AW-267 scope: direction only).

## 1. The Pitch

Everyone here is a copy. Everyone here is *smiling*. Everyone here
signed a terms-of-service they didn't read. Sim Reunion is what
Nightcap looks like when it wants to be *Upload* by way of *The Good
Place* — pastel, mid-brightness, absurd, and *funny* in the exact
register of finding out the afterlife has a subscription tier. This is
the couch's *weird* option: cheerful and eerie in equal parts, and
watching an AI suspect get caught is *especially* delicious when the
whole world is an AI. Reads *high-concept sitcom* immediately.

## 2. Reference Set

Steal the specific thing.

- ***Upload* (2020–, Amazon)** — steal the *pastel-luxury-afterlife*
  aesthetic; the customer-support cheerfulness papering over the
  weirdness.
- ***The Good Place* (2016–2020)** — steal the *bureaucratic afterlife*
  staging; ensemble-in-a-neighborhood.
- ***Palm Springs* (2020)** — steal the *time-loop wedding-reception*
  warmth; how a repeating day looks.
- ***Black Mirror: San Junipero* (2016) / Hang the DJ (2017)** —
  steal the *simulated-idyll* palette; sunlit pastel that turns.
- ***Everything Everywhere All At Once* (2022)** — steal the
  *cheerful-cosmic-absurd* framing; permission to be goofy inside a
  serious story.
- ***Severance* (2022–, but the outie's Kier's-Enterprise scenes)** —
  steal the *corporate-utopian pastel* register.
- ***The Truman Show* (1998)** — steal the *sunlit-town-that-is-a-set*
  aesthetic.
- ***Wandavision* (2021)** — steal the *sitcom-formatted-uncanny*
  register — how the framing itself can be the joke.

## 3. The Look

- **Center stage:** a sun-lit courtyard, a mid-brightness event hall,
  a customer-service lobby, a repeating cocktail hour, a sitcom-styled
  dining room. Everything a little too *ideal*.
- **Cast rail:** portrait chips as *sim avatars* — soft-lit, mid-
  saturation, small "session-tier" microcopy under the name (Basic,
  Premium, Legacy).
- **Phones:** cards are TOS agreements, achievement banners, help-
  desk chat threads. Private cards are journal entries in the sim.
  Action cards are pop-up prompts styled like consent modals.

## 4. Palette Anchors

| Role (0069 token) | Anchor | The vibe |
| --- | --- | --- |
| `--theme-glow` | Pastel gold `#EAC97C` | Muted, midday, over-perfect. |
| `--narrator` | Warm off-white `#F5EFDF` | Product-marketing bright. |
| `--private` | Sky lavender `#B2A6D8` | The color of a UI in a happy app. |
| `--accuse` | Warning coral `#EE677A` | Bright pastel red. Reads *error state* against pastel. |
| `--ok` | Sunbleach mint `#7EDBAE` | Achievement-unlocked green. |

Warmth cue: **mid-brightness, ambient warm**. This is the *lightest*
of any wrapper — the base is still near-black at the outer edges to
respect the stage rule, but the center stage sits in a mid-value warm
pastel. Reads *daytime UI dream* against the dark stage frame.

## 5. Typography

- **Display face.** A rounded modern grotesk that reads *friendly-app*
  turned slightly *editorial*. Reference: *Manrope* (OFL) or a
  soft-optical *Fraunces* cut. Beat titles get a small icon-adjacent
  glyph (a checkmark, a bell) — used *once* per beat, never persistent.
- **UI face.** Inter (constant).
- **Voice rule.** Narrator never speaks Inter; UI never speaks the
  grotesk.

## 6. Material Vocabulary

- **Surfaces.** Mid-value pastel plaster, matte pastel plastic, soft
  fabric, terrazzo, brushed pastel-brass, warm laminate, cheerful
  signage, help-desk clipboard, subscription-tier lanyard, muted-holo
  hover-glow.
- **Card framings.** Identity cards render as sim-avatar cards with a
  tier microcopy. Private-event cards are journal entries in-sim.
  Action cards are consent-modal prompts.
- **Texture.** A faint gradient wash across the near-black outer stage;
  a subtle *very slight* pastel banding across the mid-value center.
- **Cast rail.** Names in the grotesk; portrait slot soft-cornered
  square with tier microcopy.

## 7. Motion Character

- **Cheerful, snappy, uncanny.** Motion is *product-tour smooth* — the
  animation quality of a happy consumer app. But held one beat too
  long, so it registers as *off*.
- **`seq-body`** is the sim glitching. Two frames of pastel banding,
  hard cut to base, silence beat, single line ("Marcus has been
  logged out."), resume with the pastel a shade less bright.
- **Ambient is a slow pastel gradient drift** across the center stage.
  Reduced motion holds it steady.

## 8. The Host — Vesper as the Customer-Experience Host

**See** [`the-host.md`](../the-host.md) for Vesper's bible. This is
Vesper at *maximum Caine* — her most unhinged register. The Amazing
Digital Circus end of her voice recipe is loudest here, and the
occasional grave shift *devastates* against this baseline.

- **Vesper's role tonight.** The sim's customer-experience host.
  Bright, cheerful, slightly-off in her politeness. Says every awful
  thing with a smile you can hear.
- **Register.** Sunny-product-marketing, faintly uncanny, absurd.
- **Cast-rail silhouette shape.** Soft-cornered sim-avatar square
  with a small "session-tier" microcopy under the name (Basic /
  Premium / Legacy).
- **Sample lines.**
  - *(Opening — full cheer.)* "Welcome, welcome, welcome to the
    reunion of the class of infinity! Everyone made it. Everyone is
    *radiant*. Everyone is, technically, still on the free trial. We
    are so glad you're here."
  - *(Beat turn, B2 — cheerful *devastation*.)* "Wonderful news!
    Marcus has been logged out. We are so sorry for the inconvenience.
    Our team is looking into it. In the meantime — the punch is still
    available."
  - *(Interrogation stinger — delighted.)* "Ms. Kent, our records
    indicate you were at yoga at nine. Our records also indicate yoga
    did not happen at nine. Isn't that *fun*?"
  - *(The Wink — full Caine.)* "You are on a couch! The couch has
    been *detected*! The couch is *welcome*! Your terms of service
    are, of course, also in effect. Please enjoy Nightcap."
  - *(Reveal — cheerful, then quiet.)* "It was in the terms of
    service. It has always been in the terms of service. Section
    fourteen point two! So exciting. — Marcus, in fairness, did
    click 'agree.'"

## 9. The Showcase Moment (`seq-truth`, Beat 6)

The pastel center-stage brightens by exactly one step. Cast sim-
avatars slide forward one at a time — narrator names what each
*almost* caught, ending on a sim-detail (the deleted save, the tier
upgrade, the audit log). The killer's avatar lands last; a pastel
banding glitch runs through the frame; the avatar tier microcopy
flips to `--accuse` ("STATUS: TERMINATED"); the last line lands in
the grotesk at full weight against a very dark base. The pastel
resumes as if nothing happened. Cut to superlatives.

## 10. Failure Modes (Do Not Ship)

- **Full horror pivot.** Uncanny is the register, not distress. The
  sim reveals bad things; it does not *harm* the player.
- **Meme-language UI copy.** The cheerful register comes from *voice*,
  not from millennial-app tropes.
- **Rainbow pastel wash.** Two pastels max in frame at once. Discipline
  in a bright wrapper is doubly important.
- **Actual customer-service brand imitation.** Brand-safe. No
  specific-brand check-marks or logos.

## 11. AW-268 Handoff Slots

- [ ] Reference image collection attached (film stills, product-launch
      photography, cheerful-app UI screenshots).
- [ ] Portrait treatment decided (sim-avatar soft-square recommended).
- [ ] Card framing SVGs authored (sim avatar, journal, consent modal).
- [ ] Background texture (pastel gradient drift) SVG or CSS.
- [ ] Sim-glitch treatment authored for `seq-body` and `seq-truth`
      (bounded, single occurrence, reduced-motion override — banding
      must default to *off* under reduced-motion for accessibility).
- [ ] Narrator voice fragments authored per 0068 §3.3 (brand-safe
      cheerful register; no real brand names in prompts).
- [ ] Contrast table per parent brief §5 (extra care — pastel base
      makes contrast harder; verify 7:1 narrator on stage).
- [ ] Reduced-motion parity screenshots per `seq-*`.
