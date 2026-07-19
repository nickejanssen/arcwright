# Moodboard  -  Orbital Gala 2087

> Wrapper: **Sci-Fi** · Mood: **Chrome opulence, weightless, spooky-elegant**
> Story-bible instances: orbital gala, luxury space-station dinner,
> corporate-summit off-world, first-class shuttle reception, colony
> anniversary ball.
> Launch skin: **Orbital Gala 2087** (spec 0069 §7B).
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Approved (AW-267 v1.0, see docs/product/aw267-discovery-and-checkpoints.md).

## 1. The Pitch

Earth is a blue line outside the window. The champagne is in a
zero-g globe. Someone floats past the observation deck, and they
should not be that still. Orbital Gala 2087 is what Nightcap looks
like when it wants to be *Blade Runner 2049* by way of *Passengers*  -
chrome, ultraviolet, quiet, and full of people who paid a fortune to
be somewhere no one can reach them. The couch loves this one because
it's *space*: the frame is immediately unmistakable, and the reveal
gets to happen against a planet.

## 2. Reference Set

Steal the specific thing.

- ***Blade Runner 2049* (2017)**  -  steal the *palette confidence*:
  ultraviolet, warm amber pockets on cool base, water reflections.
- ***Passengers* (2016)**  -  steal the *cruise-ship-in-space*: how
  luxury looks in vacuum; corridors and ballrooms with view-of-stars.
- ***2001: A Space Odyssey* (1968)**  -  steal the *hospitality wing*:
  Pan-Am shuttle interior; measured, expensive, sinister-by-restraint.
- ***Foundation* (2021–, Apple)**  -  steal the *floating-city
  grandeur*: how scale reads on a TV.
- ***Star Trek: Discovery* (2017–, formal ballroom scenes)**  -  steal
  the *diegetic uniform / high-collar* silhouette for portraits.
- ***Denis Villeneuve, general** (*Dune*, *Arrival*)  -  steal the
  *reverent long takes*: the confidence to hold on empty rooms.
- ***Elysium* (2013)**  -  steal the *class-geometry-in-orbit*: who is
  allowed on which deck.
- ***Ad Astra* (2019)**  -  steal the *cold professionalism* against
  vast dark.

## 3. The Look

- **Center stage:** an observation lounge, a floating garden, a
  ballroom under a dome, an airlock-adjacent salon. Planet reflected
  in glass and floor. Chrome bar. Zero-g flourishes on tableware only.
- **Cast rail:** portrait chips as *diplomatic credentials*  -  hex
  badge silhouette, cool UV rim.
- **Phones:** cards are boarding passes, credentialed dossiers,
  encrypted transmissions. Private cards have a scanline shimmer.
  Action cards are protocol prompts.

## 4. Palette Anchors

| Role (0069 token) | Anchor | The vibe |
| --- | --- | --- |
| `--theme-glow` | Ultraviolet `#9D7BFF` | Plasma, holographic accent, gala uplight. |
| `--narrator` | Cool ivory `#EAF0FF` | Ship-log voice. Never warm. |
| `--private` | Ice `#A3C6E0` | Encrypted-transmission blue. |
| `--accuse` | Alarm coral `#FF4D6D` | Bright enough on ice; muted enough to sit in a hospitality room. |
| `--ok` | Mint-teal `#5FDAB8` | *Systems nominal*, not celebratory. |

Warmth cue: **cool-source, planetary**. UV and plasma are the *lights*.
Warm light exists as an ember (a lantern in a memorial scene, an
emergency lamp)  -  a highlight, never a base.

## 5. Typography

- **Display face.** A wide grotesk that holds weight at TV distance.
  Reference: *Space Grotesk* (OFL). Beat titles carry generous
  tracking. Reveal moment can dial optical size up.
- **UI face.** Inter (constant).
- **Voice rule.** Narrator never speaks Inter; UI never speaks the
  grotesk.

## 6. Material Vocabulary

- **Surfaces.** Matte polymer, brushed chrome, translucent glass,
  anodized aluminum, holographic film, backlit acrylic, dark
  carbon-lace, deep-space void through glass.
- **Card framings.** Identity cards render as diplomatic credentials
  with a hex-badge silhouette. Private-event cards are encrypted
  transmissions with a scanline. Action cards are protocol prompts.
- **Texture.** A faint starfield across the near-black base; a
  suggestion of glass-reflection along card edges.
- **Cast rail.** Names in the grotesk, wide tracking; portrait slot
  hex-badge when assets exist. Suspect-stage motion may include a
  quiet scan-line overlay while a suspect is answering.

## 7. Motion Character

- **Drift and settle.** Elements arrive on low-friction motion  -
  zero-g, or a smooth robotic mount. Never bouncy.
- **`seq-body`** still snaps. Sudden is sudden even in space. The
  station lights dim to emergency-red for half a second, snap back to
  cool base, silence beat, single line, resume.
- **Ambient is a slow starfield parallax** at the whisper line  -  one
  star crosses per beat. Reduced motion holds the field still.

## 8. The Host  -  Vesper as the Ship's Log

**See** [`the-host.md`](../the-host.md) for Vesper's bible. This is
Vesper's *coolest* register  -  the shift is small and precise.

- **Vesper's role tonight.** The ship-log voice. The station's
  hospitality concierge, or the AI that isn't the station AI.
  Calibrated, precise, dry  -  the register of a captain logging
  events after the fact. Not sinister; *unimpressed*.
- **Register.** Clipped, professional, slightly-amused. Vesper
  making formal ship's log entries because it amuses her to do so.
- **Cast-rail silhouette shape.** Hex-badge with a cool UV rim.
- **Sample lines.**
  - *(Opening  -  formal, warm underneath.)* "Vesper, log. Time,
    twenty-oh-seven ship-standard. All guests aboard, all guests
    accounted for, all guests in high spirits. Champagne is in
    zero-g globes. Marcus is on his third. Recording."
  - *(Beat turn, B2.)* "Vesper, log. The observation lounge has
    depressurized  -  conversationally. Mr. Marcus is unresponsive.
    The station is not."
  - *(Interrogation stinger.)* "Ms. Kent's suit log shows her in the
    solarium at nineteen-oh-five. The station's log does not. One of
    them, statistically, is lying."
  - *(The Wink.)* "Vesper, log. The couch is present. Recording.
    Continuing."
  - *(Reveal.)* "Vesper, log. It was in the airlock cycle. It has
    been in the airlock cycle since the shuttle docked.  -  Marcus,
    I am afraid, filed the request."

## 9. The Showcase Moment (`seq-truth`, Beat 6)

The ballroom lights drop. Earth rotates slowly in the observation
window. Cast credentials slide forward one at a time  -  the narrator
names what each *almost* caught, ending on a station-detail (the
maintenance ticket, the guest list, the sealed shuttle log). The
killer's credential lifts to center; its hex badge re-rings to
`--accuse` with a chromatic-shift halo; the last line lands in the
grotesk at full weight against planet-dark black. The airlock cycle
completes. Cut to superlatives.

## 10. Failure Modes (Do Not Ship)

- **Cyberpunk billboard wash.** UV is a *source*, not a full-screen
  neon flood. Save that for *Neon Noir*  -  this wrapper is the *quiet*
  end of Sci-Fi.
- **HUD overload.** No data-dashboard chrome; the stage is still one
  thing at a time. No scan-lines on non-suspect frames.
- **Costume-space caricature.** No silver jumpsuit iconography, no
  blaster imagery.
- **Ambient audio cluttering the narrator.** When AW-268 attaches
  audio (0068 §6), the reveal stinger must sit *under* the narrator's
  line, not over it.

## 11. AW-268 Handoff Slots

- [ ] Reference image collection attached (film stills, spacecraft-set
      photography, engineered-interior stills).
- [ ] Portrait treatment decided (hex-badge recommended).
- [ ] Card framing SVGs authored (diplomatic credential, encrypted
      transmission, protocol prompt).
- [ ] Background texture (starfield / glass reflection) SVG or CSS.
- [ ] Starfield-parallax ambient rule authored (period, direction,
      reduced-motion override).
- [ ] Suspect-stage scan-line treatment authored (bounded to
      `seq-spotlight` only).
- [ ] Narrator voice fragments authored per 0068 §3.3.
- [ ] Contrast table per parent brief §5.
- [ ] Reduced-motion parity screenshots per `seq-*`.
