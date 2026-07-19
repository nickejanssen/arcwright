# Moodboard  -  Riviera 1962

> Wrapper: **High Society** · Mood: **Sunlit, glossy, dangerous under the tan**
> Story-bible instances: 1950s Hollywood cocktail party, 1960s Riviera
> yacht weekend, cocktail hour on a private terrace, film festival
> after-party.
> Launch skin: none in launch window.
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Approved (AW-267 v1.0, see docs/product/aw267-discovery-and-checkpoints.md).

## 1. The Pitch

The sun goes down over the harbor. Somebody's on their fourth
Negroni. Everyone here is *photographed for a living*, or married to
someone who is. Riviera 1962 is what Nightcap looks like when it wants
to be *The Talented Mr. Ripley* by way of *Mad Men*  -  expensive,
laughing, and about to turn ugly the moment the ice runs out. The
couch feels *glamorous*. The couch also feels *outside*, which for a
Nightcap session is the trick  -  this one plays in daylight and still
lands the reveal.

## 2. Reference Set

Steal the specific thing.

- ***The Talented Mr. Ripley* (1999)**  -  steal the *sunlight on
  Italian tile*: the exact yellow of a terrace at 6pm; how a linen
  jacket carries a scene.
- ***Death on the Nile* (2022)**  -  steal the *saturated Deco-into-
  moderne palette* against water and cream.
- ***Mad Men* (2007–2015)**  -  steal the *drink in the frame*: how a
  glass in every hand tells a scene.
- ***Bond, Sean Connery era* (1962–1967)**  -  steal the *cool wardrobe
  as menace*: nobody looks nervous, everyone is dangerous.
- ***Call Me by Your Name* (2017)**  -  steal the *golden hour discipline*
  and the confidence to hold on faces.
- ***A Bigger Splash* (2015)**  -  steal the *pool-side ensemble under
  low sun*: bathing suits, secrets, tempers.
- ***Ferrari* (2023, the terrace scenes)**  -  steal the *European
  hospitality set-piece* look.
- ***The White Lotus* season 2 (2022)**  -  steal the *modern-Mediterranean*
  glamour with an edge; the villa as a character.

## 3. The Look

- **Center stage:** a sun-drenched terrace, an art-directed cocktail
  bar, a yacht deck at dusk. Sky in the frame. Water off-frame,
  reflecting up.
- **Cast rail:** portrait chips in mid-century-magazine style  -  a
  photo-half-tone dot pattern on cream stock, name letterspaced in
  editorial serif.
- **Phones:** cards are magazine spreads or postcard stock. Private
  cards read like a diary page. Action cards are hotel-room stationery.

## 4. Palette Anchors

| Role (0069 token) | Anchor | The vibe |
| --- | --- | --- |
| `--theme-glow` | Sun-gold `#E2B950` | The last hour of daylight over water. |
| `--narrator` | Cream `#F0E9D2` | Warm, editorial. Reads *magazine*, not *paper*. |
| `--private` | Riviera blue `#5F8FB8` | The pool at 6pm. Water framed by tile. |
| `--accuse` | Poppy red `#C63C3F` | Kodachrome red. Lipstick, geraniums, a stain on linen. |
| `--ok` | Aloe `#7EB498` | Botanical, sun-bleached. Reads *terrace plant*. |

Warmth cue: **warm-source, low sun**. This is the only wrapper in the
launch set where daylight is a source. Even so, the base stage stays
near-black  -  the frame is what a *golden-hour photograph* looks like
matted on black card.

## 5. Typography

- **Display face.** An editorial serif with mid-century warmth. Reference:
  a *Fraunces* optical-size cut, or an OFL *Cormorant*-adjacent register.
  Skin PRs verify at 28px TV floor.
- **UI face.** Inter (constant).
- **Voice rule.** Narrator never speaks Inter; UI never speaks the
  editorial serif.

## 6. Material Vocabulary

- **Surfaces.** Terracotta, whitewashed plaster, teak, chrome, glass,
  linen, tanned leather, sun-faded cotton, tile.
- **Card framings.** Identity cards render as magazine-spread pull
  quotes with a photo half-tone. Private-event cards are diary pages
  with a coffee ring. Action cards are hotel stationery.
- **Texture.** A faint print-emulsion grain across the near-black base;
  the suggestion of sun-hazed atmosphere at the top of the stage.
- **Cast rail.** Names in the editorial serif, letterspaced, on cream
  card. Portraits (when authored) sit in soft-cornered half-tone
  rectangles.

## 7. Motion Character

- **Slow, warm, confident.** Elements arrive like a page turn  -  a hand
  lifting a magazine, not an app rendering. Beat-turn dim is generous.
- **The exception is `seq-body`.** Death cuts the light instantly: the
  sun *sets* in half a second, the stage snaps to the near-black base,
  a single line, then resume.
- **A cicada or ice-in-glass hint** lives in the whisper line  -  a
  single-frame shimmer at long period. Reduced motion drops it.

## 8. The Host  -  Vesper as the Magazine Correspondent

**See** [`the-host.md`](../the-host.md) for Vesper's bible.

- **Vesper's role tonight.** The correspondent from a very expensive
  magazine. Not American, not quite anything. Has been to this hotel
  before. Names the drink, the tan, the tan line.
- **Register.** Confident, mid-Atlantic, luxurious, dry  -  the *most
  visibly enjoying herself* Vesper gets outside Big Top and Sim Reunion.
- **Cast-rail silhouette shape.** Magazine half-tone rectangle, soft-
  cornered, cream stock.
- **Sample lines.**
  - *(Opening  -  jubilant.)* "The Delacourts have brought the yacht
    around. The Ashfords have brought the champagne. The Contessa has
    brought her third husband. Everyone, in short, has brought
    someone.  -  Almost everyone."
  - *(Beat turn, B2  -  the shift.)* "The bar closes at nine. Nobody
    at this bar respects nine. And tonight, of course, there is a
    reason."
  - *(Interrogation stinger  -  delighted.)* "Mr. Delacourt would like
    to remind us all that he was on the tennis court at nine. The
    tennis court is *radiant*. The tennis court is also, unfortunately,
    disagreeing."
  - *(The Wink.)* "You, on the couch. Yes, you. I know you are pretending
    not to have a favourite suspect. I am not fooled. Nor is Mr. Delacourt."
  - *(Reveal.)* "It was in the water. It was in the water the whole
    time. So, in fairness, was the answer."

## 9. The Showcase Moment (`seq-truth`, Beat 6)

Sun-gold rims the frame at low altitude. One by one, cast portraits
slide into center on cream cards, held at magazine-spread scale  -  the
narrator names what each *almost* caught, ending on a specific
detail (the lipstick, the tan line, the drink they didn't finish).
The killer's card enters last, its half-tone re-tinting to
`--accuse` on the hard-cut line; the horizon behind darkens to
near-black; the last line lands in the editorial serif at full weight.
Cut to superlatives.

## 10. Failure Modes (Do Not Ship)

- **Instagram-summer preset.** Sun-gold is *directional light*, not a
  wash filter. The frame is not a lifestyle brand.
- **Vaporwave palm-tree kitsch.** This is 1962, not 1985. Palms are
  incidental, never neon.
- **Mad-Men sexism cosplay.** The wrapper is glamorous, not
  content-territory-crossing. World rules (story-bible §10) unchanged.
- **Bond parody.** No jetpacks, no puns, no monologues.

## 11. AW-268 Handoff Slots

- [ ] Reference image collection attached (film stills, editorial
      photography, mid-century hospitality).
- [ ] Portrait treatment decided (magazine half-tone recommended).
- [ ] Card framing SVGs authored (magazine spread, diary page, hotel
      stationery).
- [ ] Background texture (print grain / sun haze) SVG or CSS.
- [ ] Ambient shimmer rule authored (period, amplitude, reduced-motion
      override).
- [ ] Narrator voice fragments authored per 0068 §3.3.
- [ ] Contrast table per parent brief §5 (extra care because glow is
      warm on cream  -  verify 7:1 narrator on stage).
- [ ] Reduced-motion parity screenshots per `seq-*`.
