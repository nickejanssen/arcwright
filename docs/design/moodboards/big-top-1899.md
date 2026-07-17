# Moodboard  -  Big Top 1899

> Wrapper: **High Society** · Mood: **Macabre-carnival, ornate, off-kilter**
> Story-bible instances: turn-of-the-century circus / traveling show,
> vaudeville dressing room, magician's private table, freakshow gala.
> Launch skin: none in launch window.
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Candidate research for founder interview, not approved direction.

## 1. The Pitch

The show is over. The lights on the marquee are still on. Somebody was
found in the wardrobe wagon. Everyone here has a stage name and a
better reason not to have used it tonight. Big Top 1899 is what
Nightcap looks like when it wants to be *Nightmare Alley* by way of
*The Prestige*  -  ornate, half-lit, funny in a stage-magician way,
dangerous in a hey-*where's-the-strongman* way. The couch loves this
one because the cast reads *big*: knife-thrower, escape artist,
ringmaster, fortune-teller, contortionist. Everyone in the room is
already a *character*.

## 2. Reference Set

Steal the specific thing.

- ***Nightmare Alley* (2021)**  -  steal the *carnival-into-noir*
  palette: gaslamps, wet ground, damp velvet, cheap gold.
- ***The Prestige* (2006)**  -  steal the *stagecraft-as-menace*: a
  reveal that is itself a magic trick.
- ***Water for Elephants* (2011)**  -  steal the *circus-troupe
  domesticity*: this is a family that lives together.
- ***American Horror Story: Freak Show* (2014)**  -  steal the *ornate
  costuming discipline*, minus the exploitation register. Nightcap
  world rules apply (story-bible §11)  -  the cast has agency and
  dignity; the *setting* is dark, not the treatment of the people.
- ***Carnivàle* (2003–2005)**  -  steal the *dust-and-lantern* interior
  of a traveling show at night.
- ***The Greatest Showman* (2017)** *(aesthetic only)*  -  steal the
  *ringmaster silhouette* against a lit ring.
- ***Something Wicked This Way Comes* (1983)**  -  steal the *unease of
  a caravan* at the edge of town.
- ***Moulin Rouge!* (2001)**  -  steal the *ornate ensemble* staging;
  how a room this loud can go silent on cue.

## 3. The Look

- **Center stage:** the inside of a big top after hours, a wardrobe
  wagon, a magician's table, the ring under a spotlight. Rope shadow,
  sawdust, gilt.
- **Cast rail:** portrait chips as *playbills*  -  name in vaudeville
  poster caps, a stage title beneath ("The Whispering Blade," "Madame
  Corvax"), a laurel or ornament framing.
- **Phones:** cards are playbills, palm-reading cards, ticket stubs.
  Private cards are torn poster fragments. Action cards are a stage
  cue-sheet.

## 4. Palette Anchors

| Role (0069 token) | Anchor | The vibe |
| --- | --- | --- |
| `--theme-glow` | Marquee amber `#E29431` | Bulb-lit signage. Wet with condensation. |
| `--narrator` | Poster ivory `#EFE3C7` | Aged playbill paper. |
| `--private` | Dressing-room green `#5D8A83` | Backstage teal; palm-reader-tent green. |
| `--accuse` | Curtain red `#8E2830` | Velvet-drape red. Slightly dusty. |
| `--ok` | Gilt olive `#8A9F5C` | Ringmaster braid, tarnished laurel. |

Warmth cue: **warm-source, wet ground**. Bulb light off gilt off wet
sawdust. Cool light is a lantern in a tent flap, seen for a second at
a time.

## 5. Typography

- **Display face.** A slab or vaudeville-poster register  -  reference:
  *Rozha One* or an OFL slab with weight; may combine with a
  letterpressed small-caps treatment for beat titles ("THE GRILL")
  handled as an image-treatment style, not a second face.
- **UI face.** Inter (constant).
- **Voice rule.** Narrator never speaks Inter; UI never speaks the
  poster face.

## 6. Material Vocabulary

- **Surfaces.** Wet sawdust, canvas, velvet, gilt, rope, brass hardware,
  greasepaint, cracked mirror, playbill paper, laurel.
- **Card framings.** Identity cards render as playbills with laurel
  borders. Private-event cards are torn poster fragments. Action cards
  are cue-sheets.
- **Texture.** A faint bulb-condensation grain across the near-black
  base. A very subtle rope-shadow at the frame edges.
- **Cast rail.** Names in slab caps under stage-titles; portrait slot
  in a laurel oval.

## 7. Motion Character

- **Stagecraft.** Elements *reveal*  -  a curtain lift, a spotlight
  landing, a card turned over. Beat-turns feel like a spotlight
  finding the next act.
- **`seq-body`** is a sudden blackout. Not a fade  -  a hard cut to
  black, the silence beat held longer than feels comfortable, then a
  single line, then resume with the marquee glowing back on.
- **The bulb ambient**: whisper-line glow pulses at long, slow period,
  like a marquee bulb about to flicker. Reduced motion holds it steady.

## 8. The Host  -  Vesper as the Ringmaster

**See** [`the-host.md`](../the-host.md) for Vesper's bible. This is
Vesper's *most Ringmaster* register  -  the beat where the Jackman /
Caine end of her voice recipe is loudest.

- **Vesper's role tonight.** The Ringmaster. The show is over. She has
  chosen to stay in character. Vaudeville projection when the beat
  calls for it; ghost-quiet when it doesn't.
- **Register.** Elevated, theatrical, *performing*  -  but never the
  joke. The shift here is the biggest gap in the whole system:
  Vesper can go from *booming applause line* to *dead quiet* inside a
  single breath, and the beat lands harder for it.
- **Cast-rail silhouette shape.** Playbill oval with a laurel border,
  a small stage title below the name ("The Whispering Blade,"
  "Madame Corvax").
- **Sample lines.**
  - *(Opening  -  full Ringmaster.)* "Ladies! Gentlemen! Persons of every
    other persuasion the century has yet to name! Welcome, one and
    all  -  to the last show tonight. And this time, tonight, we mean
    it *last*."
  - *(Beat turn, B2  -  the drop.)* "The show has ended. The evening,
    apparently, has not. Marcus is in the wardrobe wagon. Marcus is
    not, tonight, going home."
  - *(Interrogation stinger  -  theatrical.)* "The Whispering Blade
    would like the couch to know he was on stage at nine. The couch
    is invited to doubt him. The audience always is. That is why we
    sell tickets."
  - *(The Wink.)* "You are watching from a room I have never seen. I
    have chosen to imagine it packed. Please, applaud when you feel
    moved. I will hear it. I always do."
  - *(Reveal  -  the whole range.)* "The trick, it turns out, was
    that there was no trick. Ladies and gentlemen  -  *she just walked
    in.*  -  Applause, if you would. Softly. For Marcus."

## 9. The Showcase Moment (`seq-truth`, Beat 6)

Marquee bulbs come up slowly. The cast rail illuminates one by one as
the ringmaster names each act  -  a curtain lifting on each playbill
card. When the killer's card is named, the marquee bulbs behind
change hue to `--accuse`; the ring goes silent; the last line lands
in slab caps at full weight against the wet-sawdust base. A single
bulb burns out. Cut to superlatives.

## 10. Failure Modes (Do Not Ship)

- **Creepy-clown horror.** The mood is *ornate and off-kilter*, not
  *IT (2017)*. Nightcap is not horror-as-distress.
- **Freakshow exploitation.** The cast has agency and dignity; the
  setting is theatrical, the *characters* are not props. Story-bible
  §11 world rules unchanged.
- **Steampunk goggles.** This is 1899 traveling circus, not
  brass-goggle novelty. Ornament is *stagecraft*, not *cog*.
- **Font chaos.** One display face plus a small-caps treatment.
  Novelty display faces stacked on top of each other kill the read.

## 11. AW-268 Handoff Slots

- [ ] Reference image collection attached (film stills, playbill
      archive photography, circus poster art).
- [ ] Portrait treatment decided (laurel-oval playbill recommended).
- [ ] Card framing SVGs authored (playbill, torn poster, cue-sheet).
- [ ] Background texture (wet sawdust / rope shadow) SVG or CSS.
- [ ] Marquee bulb ambient rule authored (period, amplitude,
      reduced-motion override).
- [ ] Stage curtain / spotlight sequence for `seq-truth`.
- [ ] Narrator voice fragments authored per 0068 §3.3 (~stage titles
      included in the prompt priming).
- [ ] Contrast table per parent brief §5.
- [ ] Reduced-motion parity screenshots per `seq-*`.
