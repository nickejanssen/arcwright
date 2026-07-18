# Moodboard  -  Y2K Launch

> Wrapper: **Corporate** · Mood: **Nostalgic-neon, giddy, precarious**
> Story-bible instances: December 1999 Y2K eve party, 2000s-era startup
> launch party, dot-com office holiday party, early-social-media era
> founder dinner.
> Launch skin: none in launch window.
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Candidate research for founder interview, not approved direction.

## 1. The Pitch

Someone's about to *ring the bell*. Someone's about to *drop the ball*.
The office is full of vodka Red Bulls and pool tables. Everyone has
options that just vested and half of them shouldn't have. Y2K Launch is
what Nightcap looks like when it wants to be *WeCrashed* by way of
*Halt and Catch Fire*  -  bright, giddy, badly-lit-in-a-charming way, and
utterly loaded with people who are about to find out the money isn't
what they thought. The couch loves this one because it's *nostalgic*
even if you weren't there. Reads *dot-com boom* immediately.

## 2. Reference Set

Steal the specific thing.

- ***WeCrashed* (2022)**  -  steal the *founder-charisma-in-a-loft*
  staging; the exact green of a WeWork glass wall.
- ***Halt and Catch Fire* (2014–2017)**  -  steal the *early-90s tech
  office*: mismatched furniture, ambient CRT glow, cigarette smoke.
- ***The Social Network* (2010)**  -  steal the *late-night computer
  glow*; a face lit by a monitor.
- ***Silicon Valley* (2014–2019, HBO)**  -  steal the *pool-table
  brogrammer house* as ensemble geometry.
- ***Hackers* (1995)**  -  steal the *maximalist neon* club scene, the
  disc-jewel-case color palette.
- ***Empire Records* (1995) / *Party Monster* (2003)**  -  steal the
  *late-90s / early-2000s club-adjacent party lighting*.
- ***The Wolf of Wall Street* (2013, launch scenes)**  -  steal the
  *rented-ballroom launch* energy.
- ***Mr. Robot* (2015–2019, party episodes)**  -  steal the *neon-and-
  glass* interior; Whiterose's compound lighting.

## 3. The Look

- **Center stage:** an early-dot-com office at midnight, a rented
  ballroom, a rooftop with the Manhattan skyline, a "Times Square 1999"
  set. Neon signage, CRT ambient, glow of the countdown clock.
- **Cast rail:** portrait chips as *badge lanyards* or *AIM screenname
  cards*  -  pixelated portrait treatment, screennames as flavor.
- **Phones:** cards look like early-2000s stationery (pastel invites),
  AIM chat windows, launch-day press releases. Private cards are
  handwritten notes on branded launch napkins. Action cards are ticker-
  tape rows.

## 4. Palette Anchors

| Role (0069 token) | Anchor | The vibe |
| --- | --- | --- |
| `--theme-glow` | Sodium orange `#F58A2E` | Times Square 1999 marquee glow. |
| `--narrator` | Champagne `#F3E3B2` | Warm, celebratory, slightly tacky. |
| `--private` | Neon aqua `#4CD6C7` | Late-90s screen-glow. iMac Bondi Blue slightly cooled. |
| `--accuse` | Firebrick launch red `#DA3B47` | Bright launch-button red. |
| `--ok` | Lime `#8FD46B` | Terminal-cursor green pushed toward friendly. |

Warmth cue: **neon-warm over crowd-dark**. Bright signage against
crowd shadow. The base is near-black; every source of light is a *sign*
or a *screen*.

## 5. Typography

- **Display face.** A confident modern grotesk with weight  -
  reference: *Space Grotesk* (OFL) or *IBM Plex Sans*. Beat titles can
  carry a subtle chromatic-aberration treatment on the reveal moment
  only.
- **UI face.** Inter (constant).
- **Voice rule.** Narrator never speaks Inter; UI never speaks the
  grotesk.

## 6. Material Vocabulary

- **Surfaces.** Chrome, glass, brushed aluminum, iridescent plastic,
  vinyl, neon tube, glossy black, glossy white, translucent lucite,
  branded napkin, CRT bezel.
- **Card framings.** Identity cards render as lanyard badges or AIM
  windows. Private-event cards are handwritten napkin notes. Action
  cards are ticker-tape row items.
- **Texture.** A faint CRT scanline overlay at the whisper line only;
  a faint chromatic-aberration edge on the reveal frame.
- **Cast rail.** Names in the grotesk, tight tracking; portrait slot
  slightly pixelated as a stylistic choice.

## 7. Motion Character

- **Snappy, on the beat.** Motion is *broadcast-graphics fast*. Beat-turn
  is a countdown-clock roll: dim, tick, resume.
- **`seq-body`** is a marquee sign snapping off. Hard cut, silence beat,
  single line, resume with the ambient neon dimmer than before.
- **Ambient is a slow *marquee chase*** on the whisper line  -  one
  pixel of light moving left to right, one frame per beat. Reduced
  motion holds it steady.

## 8. The Host  -  Vesper as the Launch MC

**See** [`the-host.md`](../the-host.md) for Vesper's bible.

- **Vesper's role tonight.** The MC of the launch party. Or the CFO
  who was warned. Names the round, the valuation, the champagne
  budget.
- **Register.** Bright, giddy, warm, ominous  -  the ballroom-toast-
  master voice with a hairline crack in it. Vesper's most *this is
  fine* register.
- **Cast-rail silhouette shape.** Pixelated lanyard badge or AIM
  screenname card  -  screennames as flavor beneath the character name.
- **Sample lines.**
  - *(Opening  -  full launch bright.)* "Ladies and gentlemen, we are
    forty-five minutes from midnight, Series C is *closed*, and the
    Y2K bug is somebody else's problem. Marcus is about to give the
    toast. Welcome  -  to the future!"
  - *(Beat turn, B2.)* "The countdown is at eleven-fifty-eight. Marcus
    was scheduled to give the toast. Marcus is now, unfortunately,
    part of the story."
  - *(Interrogation stinger.)* "Kent would like the couch to remember
    that she was at the bar at nine. The bar has security footage.
    The bar disagrees.  -  Sincerely."
  - *(The Wink.)* "You are watching from a couch. I want you to know
    the couch is *fully vested*, and I am delighted for you."
  - *(Reveal.)* "It was in the term sheet. It was in the term sheet
    from the beginning.  -  Marcus signed it. Of course he did."

## 9. The Showcase Moment (`seq-truth`, Beat 6)

Marquee lights swing across the stage in a slow chase. The cast rail
lanyards flip forward one by one as the narrator names what each
*almost* caught  -  ending on a Y2K-launch detail (the vested shares,
the pre-IPO cap table, the deleted press release). The killer's badge
comes up last, marquee bulbs behind it re-tinting to `--accuse`; the
countdown clock in the whisper line stops at midnight; the last line
lands in the grotesk at full weight against Times-Square black. A
single confetti frame. Cut to superlatives.

## 10. Failure Modes (Do Not Ship)

- **Vaporwave meme wash.** Neon is a *source*, not a wallpaper. If the
  frame reads *lofi-hip-hop-radio*, it has failed.
- **Retro-cringe font party.** One display face. One grotesk. Novelty
  faces stacked on top of each other kill the read.
- **Party-hat costume.** No 1999 stereotype accessories on portraits
  by default  -  party-hat detail belongs to authored moments, not chrome.
- **Actual social-media logos.** Brand-safe. Screennames yes; logos no.

## 11. AW-268 Handoff Slots

- [ ] Reference image collection attached (film stills, dot-com press
      photography, late-90s club and launch photography).
- [ ] Portrait treatment decided (pixelated badge recommended).
- [ ] Card framing SVGs authored (lanyard, AIM window, napkin note,
      ticker-tape row).
- [ ] Background texture (CRT scanline / marquee bulb) SVG or CSS.
- [ ] Marquee-chase ambient rule authored (period, direction,
      reduced-motion override).
- [ ] Chromatic-aberration reveal treatment authored (bounded to the
      reveal moment only).
- [ ] Narrator voice fragments authored per 0068 §3.3.
- [ ] Contrast table per parent brief §5 (extra care because glow is
      sodium  -  verify against warm narrator tint).
- [ ] Reduced-motion parity screenshots per `seq-*`.
