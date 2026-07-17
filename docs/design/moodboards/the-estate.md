# Moodboard — The Estate

> Wrapper: **Corporate** · Mood: **Glossy, contemporary, quietly menacing**
> Story-bible instances: contemporary wealthy-host dinner, billionaire
> compound weekend, gallery opening at a private residence, retreat at
> a rented estate.
> Launch skin: none in launch window.
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Draft — no image assets attached (per AW-267 scope: direction only).

## 1. The Pitch

A house that was on Architectural Digest last month. A dinner that
started with a signed menu. Someone with a lot of money invited a lot
of people who *depend* on that money, and now one of them is dead. The
Estate is what Nightcap looks like when it wants to be *Glass Onion* by
way of *The Menu* — sleek, expensive, satisfying to look at, and
sharpening every second. Absolutely the couch's favorite for a Friday
night. Reads *prestige TV* immediately.

## 2. Reference Set

Steal the specific thing.

- ***Glass Onion* (2022)** — steal the *modern-glass compound*: how
  wealth photographs when it wants to be seen; the interior of Miles
  Bron's guesthouse.
- ***The Menu* (2022)** — steal the *plated-dinner-as-theatre* framing;
  the exact use of black on white on dish.
- ***Triangle of Sadness* (2022)** — steal the *yacht-and-terrace
  wealth* with an undertone; sunset over expensive water.
- ***Saltburn* (2023)** — steal the *English-country contemporary
  wealth*: modern art in a Georgian house.
- ***Succession* (2018–2023, Tuscany episodes)** — steal the *terrace
  ensemble* framing: how power sits around a table.
- ***The White Lotus* season 1 (2021)** — steal the *hospitality
  labour visible in the frame*: staff at the edge of every shot.
- ***Parasite* (2019)** — steal the *architecture as class geometry*;
  where in the house each person actually stands.
- ***Big Little Lies* (2017–2019)** — steal the *cliffside modern*
  interior; how coastal light reads on marble.

## 3. The Look

- **Center stage:** a contemporary architectural interior — glass wall,
  poured concrete, single expensive artwork, one long table. Ocean or
  city off-frame, reflected in glass.
- **Cast rail:** portrait chips as press-kit photographs on matte black,
  name in a modern editorial serif.
- **Phones:** cards are gallery-tag stock or embossed hospitality menus.
  Private cards look like a signed NDA. Action cards are agenda-item
  lines from a printed dossier.

## 4. Palette Anchors

| Role (0069 token) | Anchor | The vibe |
| --- | --- | --- |
| `--theme-glow` | Warm brass `#B89466` | Uplights, brushed metal, engineered warmth. |
| `--narrator` | Alabaster `#EDE8DA` | Considered. Reads *stationery*, not *paper*. |
| `--private` | Slate `#6C7784` | The color of a modern art wall. Discreet. |
| `--accuse` | Modern claret `#A63A45` | Contemporary red. Reads *aperitivo*, not *wound*. |
| `--ok` | Eucalyptus `#7FA98C` | Botanical-modern. Reads *centerpiece*, not *garden*. |

Warmth cue: **staged-warm over polished neutral**. The base is
near-black; the light source is a *rented lamp*, not a fireplace.

## 5. Typography

- **Display face.** A modern editorial serif with confidence. Reference:
  a *Fraunces* soft-optical cut, or an OFL *EB Garamond*-modernized
  register. Skin PRs verify at 28px TV floor.
- **UI face.** Inter (constant).
- **Voice rule.** Narrator never speaks Inter; UI never speaks the
  editorial serif.

## 6. Material Vocabulary

- **Surfaces.** Poured concrete, walnut, brushed brass, matte glass,
  Belgian linen, blackened steel, single-block marble.
- **Card framings.** Identity cards render as press-kit photo stock on
  matte black. Private-event cards are signed correspondence with a
  monogram. Action cards are printed dossier lines.
- **Texture.** A faint architectural photograph grain; a suggestion of
  bokeh from off-frame candlelight.
- **Cast rail.** Names in the editorial serif on matte black. Portrait
  slot square with tight framing.

## 7. Motion Character

- **Deliberate, on the beat.** Motion is professionally cued — the
  quality of a broadcast package. No settle-drift. No candlelight sway.
- **`seq-body`** is a hard cut. The evening's music stops between
  syllables. Silence beat. Single line. Resume.
- **Ambient chrome is *reflection*.** A subtle glint moves once,
  slowly, along the cast rail hairlines — light traveling across glass.
  Reduced motion drops it.

## 8. The Host — Vesper as the House's Private Curator

**See** [`the-host.md`](../the-host.md) for Vesper's bible.

- **Vesper's role tonight.** The house's private curator, or the
  host's Chief of Staff. Warm to the guests, ruthless about the room.
  Names the vintage, the vineyard, the architect.
- **Register.** Considered, adult, mildly amused, quietly ruthless.
- **Cast-rail silhouette shape.** Press-kit square photograph on
  matte black, name in editorial serif beneath.
- **Sample lines.**
  - *(Opening — jubilant, understated.)* "Everyone is here. The
    Delacourts have brought the Bordeaux. The house has brought its
    best china. Marcus, our host, has brought the artist he flew in
    from Rome. It is going to be a *lovely* evening. Almost."
  - *(Beat turn, B2.)* "Dessert is delayed. Marcus is in the study.
    Marcus is not, technically, alive."
  - *(Interrogation stinger.)* "Ms. Kent would like the couch to know
    she was on the terrace at nine. Two other people were also on the
    terrace at nine. They disagree — politely, but firmly."
  - *(The Wink.)* "The couch, tonight, has been provided with excellent
    lighting and, I trust, an appropriate beverage. I do not judge.
    Well. I judge a little. Please continue."
  - *(Reveal.)* "It was in the salt. It has always been in the salt.
    The menu, in fairness, did list it. — Not in so many words."

## 9. The Showcase Moment (`seq-truth`, Beat 6)

The stage light drops to a single warm uplight. One by one the cast
rail portraits step forward into the light — the narrator names what
each *almost* caught, ending on a plated-dinner detail (the second
glass, the wrong-side fork, the salt cellar). The killer's portrait
comes up last; its frame re-tints to `--accuse` in a single
photograph-flash beat; the last line lands in the editorial serif at
full weight against poured-concrete black. Cut to superlatives.

## 10. Failure Modes (Do Not Ship)

- **Instagram-luxury preset.** No sponsored-post rose gold. Wealth in
  the frame reads *architectural*, not *lifestyle*.
- **Corporate-lobby beige.** The frame stays specific — one artwork,
  one table, one uplight direction. Empty polish is not the point.
- **Villain-CEO shorthand.** Motivation is the story, not the visual.
  No Succession-fan-service caricature; no Big Tech Bad on the wall.
- **Overlit stage.** If the room is bright enough that shadow does not
  do work, the shot is failing. Warm points on near-black.

## 11. AW-268 Handoff Slots

- [ ] Reference image collection attached (film stills, architectural
      photography, luxury hospitality references).
- [ ] Portrait treatment decided (press-kit square recommended).
- [ ] Card framing SVGs authored (press stock, monogram, dossier).
- [ ] Background texture (architectural bokeh) SVG or CSS.
- [ ] Reflection ambient rule authored (period, direction, reduced-motion
      override).
- [ ] Narrator voice fragments authored per 0068 §3.3.
- [ ] Contrast table per parent brief §5.
- [ ] Reduced-motion parity screenshots per `seq-*`.
