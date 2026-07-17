# Moodboard — Colony Post

> Wrapper: **Sci-Fi** · Mood: **Frontier, lived-in, tense-technical**
> Story-bible instances: off-world colony summit, mining-station
> holiday dinner, terraforming-crew reunion, generation-ship galley,
> outer-belt research outpost.
> Launch skin: none in launch window.
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Draft — no image assets attached (per AW-267 scope: direction only).

## 1. The Pitch

Six weeks from the nearest ship. Recycled air. Everyone here signed
the same contract. Nobody signed up for this. Colony Post is what
Nightcap looks like when it wants to be *The Expanse* by way of
*Alien* (crew scenes) — lived-in, engineered, tense, *earned*. The
couch loves this one because it feels like *real people in real
trouble*; the interrogation lands with the weight of a place where you
can't just leave.

## 2. Reference Set

Steal the specific thing.

- ***The Expanse* (2015–2022)** — steal the *worked-in ship interior*:
  scratches on the wall, warning stickers, coffee ring on a console.
- ***Alien* (1979, crew scenes)** — steal the *dinner-table framing*
  before the room goes wrong; how a galley feels under humming lights.
- ***For All Mankind* (2019–, lunar base)** — steal the *frontier-
  hospitality* aesthetic; how a colony *tries* to feel homey.
- ***Silo* (2023–)** — steal the *industrial-vertical* interior; the
  suggestion of a much larger structure off-frame.
- ***Outland* (1981)** — steal the *space-mining-noir* palette: warm
  amber warning lights against cold-blue engineering.
- ***Prospect* (2018)** — steal the *helmet-off intimacy* around a
  meal; the wrap-cloth wardrobe.
- ***Sunshine* (2007, mess-hall scenes)** — steal the *golden
  interior-warmth-in-vacuum* discipline.
- ***Firefly* (2002, common-room scenes)** — steal the *found-family
  around a table* — the ensemble geometry.

## 3. The Look

- **Center stage:** a galley table, a common room, an observation
  window with an unfamiliar sky, a hydroponics bay. Warm interior
  amber against cold engineering blue.
- **Cast rail:** portrait chips as *crew-manifest thumbnails* — grid-
  ruled, name + role + tour-count microcopy.
- **Phones:** cards look like crew-manifest entries, mission logs,
  requisition slips. Private cards have a personal-log framing with a
  timestamp. Action cards are a shift-rotation prompt.

## 4. Palette Anchors

| Role (0069 token) | Anchor | The vibe |
| --- | --- | --- |
| `--theme-glow` | Amber warning `#E68E3B` | The one warm light in the module. |
| `--narrator` | Cool crew paper `#DDE4E7` | Log-page white. |
| `--private` | Engineering teal `#4A8E9B` | Cool console blue. |
| `--accuse` | Emergency crimson `#C44148` | The alarm strip on the wall. |
| `--ok` | Life-support green `#5FBB86` | *Vitals nominal*. |

Warmth cue: **cool base, one warm pocket**. Almost the same rule as
Neon Noir, but where Neon Noir's warm pocket is *a light*, here it's
*a person* — the frame stays warm at the head of a table where a real
crew is trying to hold together.

## 5. Typography

- **Display face.** An engineered wide grotesk or mono-adjacent
  register. Reference: *Space Grotesk* or an OFL mono-hybrid. Beat
  titles carry a small mission-clock timestamp treatment beneath.
- **UI face.** Inter (constant). Slightly monospace-flavored digit
  set on countdowns.
- **Voice rule.** Narrator never speaks Inter; UI never speaks the
  grotesk.

## 6. Material Vocabulary

- **Surfaces.** Powder-coated steel, engineered composite, worked-in
  vinyl seat, coffee-stained laminate, warning sticker, wire trellis,
  hydroponic root, tool-belt canvas, welded seam, warm woolen throw.
- **Card framings.** Identity cards render as crew-manifest thumbnails
  with role and tour-count. Private-event cards are personal-log
  entries with a timestamp. Action cards are shift-rotation prompts.
- **Texture.** A faint console-screen phosphor glow at the whisper
  line; a suggestion of steam / humidity at the top of the stage.
- **Cast rail.** Names in the grotesk; portrait slot rectangular with
  a tiny role-tag below.

## 7. Motion Character

- **Deliberate, weight-bearing.** Motion feels *heavy* — the way things
  move under half a gee. Beat-turn is a slow bulkhead-light dim.
- **`seq-body`** is a klaxon-strobe two-frame flash to `--accuse`,
  hard cut to base, silence beat (the ventilation fans are audible in
  the absence), single line, resume with the amber pocket a shade
  cooler than before.
- **Ambient is a slow console phosphor** flicker at the whisper line —
  low amplitude, long period. Reduced motion holds it steady.

## 8. The Host — Vesper as the Station Chief

**See** [`the-host.md`](../the-host.md) for Vesper's bible.

- **Vesper's role tonight.** The station's Chief. Or the AI concierge
  that's *not* the station AI — a warmer register. Speaks like
  someone who has filed this kind of incident report before and is
  going to file another one in the morning.
- **Register.** Adult, precise, quietly resigned. The Jackman-Logan
  end of Vesper's range against a lived-in room.
- **Cast-rail silhouette shape.** Crew-manifest thumbnail with role
  and tour-count microcopy beneath the name.
- **Sample lines.**
  - *(Opening — warm, procedural.)* "Ship's evening. All crew off
    shift. Kent is in hydroponics. Delacourt is on the observation
    deck. Marcus, as ever, is at his own dinner table. Coffee is
    still hot. Continuing."
  - *(Beat turn, B2.)* "The mess-hall is quiet. Marcus is at his
    usual seat. Marcus is, per the vitals monitor, not sleeping."
  - *(Interrogation stinger.)* "Kent's suit log shows she was in
    hydroponics at nineteen-oh-five. Hydroponics disagrees. Only one
    of them is required to be honest."
  - *(The Wink.)* "You are on a couch, six weeks from any station I
    can reach. I appreciate the company. Continue."
  - *(Reveal.)* "It was in the manifest. It was in the manifest the
    moment we broke orbit. — Marcus signed off on the shipment
    himself. He was proud of it."

## 9. The Showcase Moment (`seq-truth`, Beat 6)

The amber pocket at the head of the table brightens once and then
holds. Cast manifest thumbnails slide forward one at a time — narrator
names what each *almost* caught, ending on a colony-detail (the
sealed cargo hold, the O2 requisition, the tour-count discrepancy).
The killer's manifest lifts to center; the amber pocket snaps cool;
`--accuse` fills the crew-tag; the last line lands in the grotesk at
full weight against engineering-blue black. The ventilation fans hum
back up. Cut to superlatives.

## 10. Failure Modes (Do Not Ship)

- **Grimdark space-horror.** This is *tense-technical*, not *Event
  Horizon*. Nightcap is not horror-as-distress.
- **Uniform-costume caricature.** Portraits are crew manifests; costume
  is authored, not chrome.
- **HUD overload.** Warning stickers and log timestamps are *incidental*.
  The stage stays one thing at a time.
- **Warm-sunset flood.** Only *one* warm pocket in frame. Two warm
  sources on stage kills the wrapper's discipline.

## 11. AW-268 Handoff Slots

- [ ] Reference image collection attached (film stills, spacecraft-
      interior photography, mining-station reference).
- [ ] Portrait treatment decided (crew-manifest thumbnail recommended).
- [ ] Card framing SVGs authored (crew manifest, personal log,
      shift-rotation prompt).
- [ ] Background texture (console phosphor / steam) SVG or CSS.
- [ ] Klaxon-strobe treatment authored for `seq-body` (bounded, single
      short flash, reduced-motion override).
- [ ] Amber-pocket ambient rule authored (period, position,
      reduced-motion override).
- [ ] Narrator voice fragments authored per 0068 §3.3.
- [ ] Contrast table per parent brief §5.
- [ ] Reduced-motion parity screenshots per `seq-*`.
