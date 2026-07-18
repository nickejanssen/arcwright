# Moodboard  -  Séance 1928

> Wrapper: **High Society** · Mood: **Moody, glamorous, dangerous**
> Story-bible instances: 1920s Prohibition dinner party, speakeasy
> after-hours, private-club initiation, Gilded-Age holdout.
> Launch skin: **Séance 1928** (spec 0069 §7A).
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Candidate research for founder interview, not approved direction.

## 1. The Pitch

Late on a Saturday. The candles are lit. Somebody spent money on this
room. Somebody is about to lose everything in it. Séance 1928 is what
Nightcap looks like when it wants to be *Death on the Nile* by way of
*Babylon Berlin*  -  an evening you would have paid to attend, until you
realized whose funeral you were at. Gold on black. Smoke over silk.
Everyone knows everyone. Everyone is lying. And the couch decides who
walks out.

## 2. Reference Set

Steal the specific thing, not the whole vibe.

- ***Knives Out* (2019)**  -  steal the *composition of ensemble* against a
  single dark-wood interior; how a family fits in a frame.
- ***Death on the Nile* (2022)**  -  steal the *palette confidence*:
  saturated ivory and gold against deep water-blue; deco silhouettes.
- ***Babylon Berlin* (2017–)**  -  steal the *danger*: a party you would
  attend and later regret; the exact weight of cabaret light on a face.
- ***Boardwalk Empire* (2010–2014)**  -  steal the *interior wealth*: how
  Prohibition rooms carried money without looking like museums.
- ***Poirot* (ITV, 1989–2013)**  -  steal the *warmth of the interrogation*;
  Suchet's Poirot leaning in beside a decanter is Nightcap's shot.
- ***Peaky Blinders* (2013–2022)**  -  steal the *contrast staging*: bright
  face against near-black room, breath visible in the low light.
- ***The Great Gatsby* (2013)**  -  steal the *ornament as social
  vocabulary*: costumes, glassware, wallpaper as characters.
- ***Chicago* (2002)**  -  steal the *ensemble on stage*: this is a room
  where every suspect thinks they're the lead.

## 3. The Look

- **Center stage:** a single warmly-lit interior  -  a private parlor, a
  club backroom, the head of a dining table. Deep space around the frame;
  the room feels *contained*.
- **Cast rail:** portraits in oval brass frames or letterpressed name
  cards. Faces read *painted*, never photographic.
- **Phones:** every card is a folded place-card, a telegram, or an
  engraved invitation. Private-event cards carry a wax-seal treatment on
  the framing edge.

## 4. Palette Anchors

| Role (0069 token) | Anchor | The vibe |
| --- | --- | --- |
| `--theme-glow` | Brass `#D4A853` | Candlelight, gilt trim, the good lamp in the room. |
| `--narrator` | Warm ivory-gold `#C9B98F` | The narrator sounds *lit*, not backlit. |
| `--private` | Aged-paper cool `#8FB4C9` | A telegram in your palm. Private = correspondence. |
| `--accuse` | Oxblood `#7A2230` | Deep, considered red. The color of a decanter, of a stain, of the drape behind the confession. |
| `--ok` | Muted botanical `#5FA97F` | Malachite, absinthe, the reading lamp. Never neon. |

Warmth cue: **warm-source**. Every light in this world is a *flame* or a
*bulb pretending to be a flame*. Cool light exists only through leaded
glass and only for a second at a time.

## 5. Typography

- **Display face.** *Fraunces* (OFL, variable) as reference  -  a warm
  serif with optical size. Substitutes: an OFL deco face (Poiret-adjacent)
  used sparingly for beat titles only; body/narrator stays Fraunces.
- **UI face.** Inter (constant).
- **Voice rule.** The narrator never speaks Inter; the UI never speaks
  Fraunces.
- **Weight.** Beat titles land at high optical size, letterspaced,
  centered. Narrator lines held at mid weight with plenty of air above
  and below.

## 6. Material Vocabulary

- **Surfaces.** Aged paper, polished walnut, brass, cut crystal, cream
  linen, waxed velvet, tarnished silver, oxblood leather.
- **Card framings.** Identity cards render as folded place-cards or
  monogrammed correspondence. Private-event cards are sealed telegrams.
  Action cards are engraved calling cards.
- **Texture.** A faint smoke gradient across the near-black base; the
  suggestion of candlelight bleeding from off-frame at the top of the
  stage. Never a photographed texture  -  always a suggestion.
- **Cast rail.** Names in Fraunces, letterspaced. When portraits exist
  (AW-268), oval cameo frames on a dark ground.

## 7. Motion Character

- **Settle, don't snap.** Elements arrive *placed*  -  a note laid on a
  table, a chip set on a card. Even the beat-turn dim is unhurried.
- **The exception is `seq-body`.** Death is sudden here as everywhere:
  stage snaps darker, silence beat, single line, resume.
- **Candlelight breath.** Ambient chrome (whisper line, cast rail
  hairlines) shows the faintest luminance flicker at long period  -
  suggestion of a flame down the hall. This is the wrapper's ambient
  signature. Reduced motion holds the flame steady.

## 8. The Host  -  Vesper as Master of Ceremonies

**See** [`the-host.md`](../the-host.md) for the full character bible.
This board's job is to name Vesper's *role* in this wrapper and
demonstrate her *shifts*.

- **Vesper's role tonight.** The house's Master of Ceremonies. A
  decanter in one hand. A lit cigarette in the other. Has seen every
  guest here get worse before, and *still finds them interesting*.
- **Register.** Warm, deco-cadenced, dangerous under the charm.
- **Cast-rail silhouette shape.** Oval brass cameo on a dark ground.
  Every suspect is a candlelit painted portrait.
- **Sample lines (each demonstrates a shift).**
  - *(Opening  -  jubilant into grave.)* "Wonderful. Everyone made it.
    The Ashfords have brought the good decanter  -  the one they only
    open when they mean it. And of course, tonight, they meant it."
  - *(Interrogation stinger  -  delighted-about-awful.)* "Mr. Ashford
    is being asked, very politely, where he was at nine. He has been
    asked this *before*. Watch his hands."
  - *(The Wink  -  once per session.)* "You are, of course, on a couch.
    I have been informed this is where the best detective work happens
    now. Very well. Suspect?"
  - *(Reveal  -  grave, then delighted, then ordinary.)* "The house has
    known since the second glass was poured. It has been waiting for
    one of you to say so. And one of you nearly did.  -  It was the
    second glass. Of course it was."

## 9. The Showcase Moment (`seq-truth`, Beat 6)

Candlelit lantern-slide. The cast rail dims to silhouettes. One
character at a time steps forward into a warm-lit oval  -  narrator names
what each *almost* caught, held on the face just long enough to sting.
Then the killer's chip lifts to center stage, the oval frame
re-luminates in `--accuse`, and the last line lands in Fraunces at full
weight, held on screen while the room settles. The lantern goes dark.
Cut to superlatives.

## 10. Failure Modes (Do Not Ship)

- **Sepia over everything.** Sepia across the whole stage kills contrast
  and reads costume, not diegetic. Warm light is a *source*; the base
  stays near-black.
- **Historical caricature.** No "Odds bodkins," no comic monocle
  iconography. The era is period-realistic; the comedy is in specific
  awful behavior, not accent.
- **Chrome ornament everywhere.** Gilt earns its place on cast-rail
  names and identity-card seals only. Buttons stay quiet.
- **Serif-everywhere UI.** The UI face stays Inter. Fraunces is the
  narrator's voice, not the settings menu's.

## 11. AW-268 Handoff Slots

- [ ] Reference image collection attached (film stills, art plates,
      hospitality photography).
- [ ] Portrait treatment decided (oval cameo recommended).
- [ ] Card framing SVGs authored (place-card, telegram, calling card).
- [ ] Background texture (smoke gradient) SVG or CSS gradient authored.
- [ ] Candlelight ambient-flicker rule authored (period, amplitude,
      reduced-motion override).
- [ ] Narrator voice fragments authored per 0068 §3.3 (~8 lines per beat
      minimum for prompt priming).
- [ ] Contrast table per parent brief §5.
- [ ] Reduced-motion parity screenshots per `seq-*`.
