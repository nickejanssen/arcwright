# Moodboard — Corporate

> Wrapper covered: **Corporate** — modern professional gatherings staged
> with production budget. Story-bible instances: tech billionaire's
> dinner party, influencer retreat, reality-TV show set between tapings,
> startup launch party, corporate off-site.
>
> Launch skin: **none in the launch window** (Séance 1928 and Orbital
> Gala 2087 ship first per spec 0069 §7). Direction lives here so that
> AW-268 can activate this wrapper when the enterprise wedge (D-046)
> lights up.
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Draft — no image assets attached (per AW-267 scope: direction only).

## 1. Reference Set

*Reference set is atmosphere and voice guidance; not source material to
reproduce. Nightcap generates its own cases inside this territory.*

- **Corporate satire ensembles.** *Succession* (2018–2023), *The Menu*
  (2022), *Triangle of Sadness* (2022), *Glass Onion* (2022, the
  "disruptor" wing). How professional politeness reads on a room already
  going wrong.
- **Prestige-hospitality staging.** Award-show sets, executive summit
  press events, brand launches at the Whitney or MoMA — engineered warmth,
  camera-ready surfaces, chairs that photograph well.
- **Reality-TV between tapings.** Behind-the-scenes documentary
  material — *Vanderpump Rules* reunion sets, *Bachelor* mansion prep. The
  aesthetic of a room designed to look candid.
- **Party-game format reference.** *Death by AI* (proof that AI-native
  party games scale) as delivery reference — brisk, phone-forward,
  socially punchy — without borrowing its visual language.

## 2. Palette Anchors

*Anchor values; skin PRs author actual palettes and override the 0069
semantic tokens in the wrapper skin file.*

| Role (0069 semantic token) | Anchor | Note |
| --- | --- | --- |
| `--theme-glow` | Warm neutral gold `#C8A664` | Engineered hospitality warmth — the color of a rented uplight. |
| `--narrator` | Cool cream `#E0DBCB` | The narrator's voice tint. Slightly cooler than the High Society ivory to read as *staged*, not lived-in. |
| `--private` | Slate blue `#7C97B4` | The "for your eyes only" phone framing. Reads document, not letter. |
| `--accuse` | Coral-red `#C24957` | Danger, accusation, the killer at reveal. Modern red, still muted enough to sit in a professional room without looking cartoon. |
| `--ok` | Sage `#7FA88C` | Success, safe. Reads *approved*, not celebratory. |

Warmth cue: **staged-warm**. Engineered warmth over polished neutral. The
light source is a rented lamp, not a fireplace. Cool secondary tones
(slate, glass) sit under the warm accents to keep the room from reading
domestic.

## 3. Typography Anchors

- **Display face (narrator, beat titles, reveal).** A curated modern
  serif or editorial sans that reads *considered* rather than *warm*.
  Reference registers: *Financier* (editorial serif), *Söhne Breit* /
  *Neue Haas Grotesk* (grotesk with weight to hold a stage). Skin PRs
  select an OFL face during AW-268 and run the contrast/legibility tests
  in the parent brief §5.
- **UI face.** Inter (constant across all wrappers).
- **Voice rule.** The narrator never speaks in Inter; the UI never speaks
  in the display face.

## 4. Material Vocabulary

- **Surfaces.** Matte black, polished stone, engineered wood, leather,
  glass, brushed steel, laminated paper, corporate linen. Textures that
  photograph well. Nothing that looks casually lived-in.
- **Card framing.** Identity cards render as press-kit bio slabs or
  photographed employee badges. Private event cards render as embargoed
  memos or signed NDAs. Action cards render as agenda items.
- **Texture.** A faint corporate-hospitality bokeh across the deep-black
  base — the suggestion of a room lit by production lighting rather than
  ambient. Reflective highlights on card edges.
- **Cast rail.** Names set in the display face, tighter tracking than
  High Society; portrait slots are square, badge-style when assets exist.

## 5. Motion Character

- **Crisp, on the beat.** Motion is deliberate, professionally cued, the
  quality of a live-broadcast package. No settle-drift. No candlelight
  sway.
- **Beat turns feel like broadcast wipes,** but *inside* the motion
  budget (0069 §6) — dim, title, hold, resume. Never a swipe transition
  in ms-terms; the *quality* is broadcast, the *timing* is 0069's.
- **The reveal (`seq-truth`) is press-conference clean.** Names land
  centered, one after the other. Killer's chip flips to `--accuse` on a
  hard cut. This is the wrapper's signature motion moment.

## 6. Narrator Voice Notes

- **Persona.** The mordant Ops lead who has watched this quarter go
  sideways before. Sees the theater of the room clearly. Not cynical —
  professional.
- **Vocabulary register.** Boardroom-adjacent, not boardroom-cliché.
  "Let's go around the room, if we're all still sitting." Never
  "synergize" as a punchline.
- **Line rhythm.** Slightly tighter than High Society; the room is
  polished, so the narrator can be too. Still ≤ 2 sentences on screen at
  once per 0068 §3.3.
- **Dry wit.** Yes, with a professional's discretion. Mockery of players:
  never.

## 7. Failure Modes (Do Not Ship)

- Startup-blue everything. The retired sky-blue accent stays retired. A
  Corporate wrapper is not a SaaS dashboard in disguise.
- Neutral to the point of forgettable. The wrapper still *tells a story*.
  Warmth cue and accent color must carry personality; a Corporate skin
  that reads "Office 365 memo" has failed.
- Executive caricature. Motivations are the story; a "greedy CEO" motif
  in the visual layer wastes the wrapper.
- Photographic textures pushed to the point of taking focus from the
  cast rail and stage.

## 8. AW-268 Handoff Slots

Filled by AW-268 during skin production. Left empty by AW-267.

- [ ] Reference image collection attached (broadcast stills, event
      photography, corporate hospitality references).
- [ ] Portrait treatment decided per this wrapper (badge-style
      recommended).
- [ ] Card framing SVGs authored.
- [ ] Background texture SVG or CSS gradient authored.
- [ ] Narrator voice fragments authored per 0068 §3.3.
- [ ] Contrast table per §5 of the parent brief.
- [ ] Reduced-motion parity screenshots per `seq-*`.
- [ ] Enterprise-wedge activation decision (D-046 dependency) recorded.
