# Moodboard — Sci-Fi

> Wrapper covered: **Sci-Fi** — speculative or future-set gatherings.
> Story-bible-adjacent instances: orbital gala, colony summit, sim-world
> reunion, generation-ship dinner. Absurdist near-future variants (Y2K
> reissue party, retrofuture cocktail lounge) sit here as well when their
> palette warrants it.
>
> Launch skin: **Orbital Gala 2087** (spec 0069 §7B).
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Draft — no image assets attached (per AW-267 scope: direction only).

## 1. Reference Set

*Reference set is atmosphere and voice guidance; not source material to
reproduce. Nightcap generates its own cases inside this territory.*

- **Sci-fi ensemble mysteries.** *Glass Onion* (2022 — the disruptor
  wing's cool-glass staging), *Outland* (1981), *Sunshine* (2007), *The
  Martian* (2015) as production-design references for lived-in future
  interiors. Rooms that feel *engineered*, not *imagined*.
- **Cool-light theatricality.** *Blade Runner 2049* (2017) for how UV
  and haze read as light. *Ex Machina* (2014) for how a small cast in a
  cool-lit room can feel like a party interrupted. *Severance* (2022–)
  for engineered warmth against cool base.
- **Retrofuture registers.** Late-Kubrick, *2001*'s hospitality wing — how
  future gatherings can still be *catered*. *The Fifth Element* (1997) for
  how absurdity can sit inside high production design.
- **Party-game format reference.** Netflix's Knives Out TV party game
  (2024) as market context only — the killer-among-players lane is the
  Imposter Variant's, not Couch Race's, and the visual language here is
  Nightcap's own.

## 2. Palette Anchors

*Anchor values; skin PRs author actual palettes and override the 0069
semantic tokens in the wrapper skin file.*

| Role (0069 semantic token) | Anchor | Note |
| --- | --- | --- |
| `--theme-glow` | Ultraviolet `#9D7BFF` | The wrapper's light source. UV, plasma, holographic accent. |
| `--narrator` | Cool white `#EAF0FF` | The narrator's voice tint. Reads *ship-log*. |
| `--private` | Ice `#A3C6E0` | The "for your eyes only" phone framing. Reads *encrypted*, not *letter*. |
| `--accuse` | Alarm-coral `#FF4D6D` | Danger, accusation, the killer at reveal. Bright enough to read on ice, muted enough to sit in a hospitality room. |
| `--ok` | Mint-teal `#5FDAB8` | Success, safe. Reads *systems nominal*, not celebratory. |

Warmth cue: **cool-source**. Every wrapper decision in this family biases
toward UV, chrome, plasma, holographic accent. Warm light (a red
emergency lamp, a candle in a memorial scene) is a highlight, never a
base.

## 3. Typography Anchors

- **Display face (narrator, beat titles, reveal).** A wide grotesk that
  holds weight at TV distance. Reference: *Space Grotesk* (OFL). Skin PRs
  may substitute another OFL wide grotesk or engineered mono-serif hybrid
  if it holds the contrast requirement at 28px and stays legible when
  letterspaced for beat titles.
- **UI face.** Inter (constant across all wrappers).
- **Voice rule.** The narrator never speaks in Inter; the UI never speaks
  in the display face.

## 4. Material Vocabulary

- **Surfaces.** Matte polymer, brushed chrome, translucent glass,
  anodized aluminum, holographic film, backlit acrylic. Textures read
  *engineered* — nothing organic reads as a base surface.
- **Card framing.** Identity cards render as security badges or
  crew-manifest entries. Private event cards render as encrypted
  transmissions or personal terminal readouts. Action cards render as
  console prompts.
- **Texture.** A faint starfield or glass reflection across the
  deep-black base; ambient chromatic aberration at the edges of card
  framings. Never a screensaver.
- **Cast rail.** Names set in the display face, wider tracking; portrait
  slots are hex badges when assets exist. Suspect stage motion may show a
  scan-line overlay while a suspect is answering.

## 5. Motion Character

- **Drift and settle.** Elements arrive from off-stage on a low-friction
  motion — the suggestion of zero-g or a smooth robotic mount. Never
  bouncy. Never keyframed cute.
- **The exception is `seq-body` (Beat 1 in Couch Race — the cold-open
  death, per D-071 arc).** Death still snaps. Even in the future, sudden
  is sudden.
- **The reveal (`seq-truth`) is data-forensics.** Timeline reconstructs
  in a linear pass; a suspect's chip re-labels from *witness* to
  *responsible* on a hard cut. Killer chip flips to `--accuse` with a
  chromatic-shift accent. This is the wrapper's signature motion moment.

## 6. Narrator Voice Notes

- **Persona.** The ship-log voice that has seen worse and is
  unimpressed. Calibrated, precise, dry — the register of a captain
  logging events after the fact.
- **Vocabulary register.** Future-*flavored*, not future-*cliché*. "The
  observation lounge has gone quiet, which is usually a sign." Never "By
  the stars!" or "Great Scott!"
- **Line rhythm.** Slightly clipped compared to High Society. The
  narrator has a system to report to. Still ≤ 2 sentences on screen at
  once per 0068 §3.3.
- **Dry wit.** Yes, with a technician's understatement. Mockery of
  players: never.

## 7. Failure Modes (Do Not Ship)

- Neon-everywhere. UV and plasma are *sources* against the deep-black
  base, not full-screen wash. A cyberpunk billboard aesthetic overwhelms
  the cast rail and kills contrast on narrator lines.
- Sci-fi caricature. Bulky helmets, silver jumpsuits, blaster iconography
  in the UI. The wrapper is speculative-realistic, not costume-realistic.
- HUD overload. The wrapper's engineered feel does not license
  data-dashboard chrome; the stage is still one thing at a time.
- Ambient audio design without narrator distinction. When AW-268 attaches
  the stinger set (0068 §6), the reveal stinger must still sit under the
  narrator's line, not over it.

## 8. AW-268 Handoff Slots

Filled by AW-268 during skin production. Left empty by AW-267.

- [ ] Reference image collection attached (film stills, spacecraft-set
      photography, engineered-interior stills).
- [ ] Portrait treatment decided per this wrapper (hex-badge recommended).
- [ ] Card framing SVGs authored.
- [ ] Background texture SVG or CSS gradient authored.
- [ ] Narrator voice fragments authored per 0068 §3.3.
- [ ] Contrast table per §5 of the parent brief.
- [ ] Reduced-motion parity screenshots per `seq-*`.
