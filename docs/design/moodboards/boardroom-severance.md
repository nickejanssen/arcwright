# Moodboard  -  Boardroom Severance

> Wrapper: **Corporate** · Mood: **Uncanny, minimal, quietly wrong**
> Story-bible instances: corporate off-site, C-suite retreat, board
> dinner in a private conference floor, late-night working session in
> a rented executive suite.
> Launch skin: none in launch window.
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Approved (AW-267 v1.0, see docs/product/aw267-discovery-and-checkpoints.md).

## 1. The Pitch

The fluorescent light hums. Every surface has been chosen by a
consultant. Everyone has a lanyard and a slightly forced smile. The
projector was left on. Boardroom Severance is what Nightcap looks like
when it wants to be *Severance* by way of *Industry*  -  coldly beautiful,
extremely uncanny, and *funny* in the exact register of someone
laughing too hard at their boss's joke. This board reads as *serious
prestige*: think of it as Nightcap's dry-comedy option, the one you
put on when your friends are tired of things being *warm*.

## 2. Reference Set

Steal the specific thing.

- ***Severance* (2022–)**  -  steal the *uncanny minimalism*: the hallway,
  the office plant, the exact green of Lumon carpet against beige. The
  serif waybar font.
- ***Industry* (2020–)**  -  steal the *late-night trading floor* glow;
  faces underlit by monitors.
- ***American Psycho* (2000, office scenes)**  -  steal the *executive
  set-piece*: identical suits, identical desks, one thing wrong.
- ***The Apartment* (1960)**  -  steal the *rows-of-desks* geometry.
- ***Michael Clayton* (2007)**  -  steal the *corporate blue-hour*
  interior light; conference rooms at 3am.
- ***Suits* (2011–2019)**  -  steal the *boardroom set* discipline as a
  reference for card layout.
- ***The Assistant* (2019)**  -  steal the *quiet-office menace*: nothing
  loud is happening; something bad is happening.
- ***Playtime* (Tati, 1967)**  -  steal the *deep-focus office comedy*:
  every extra is doing something specific.

## 3. The Look

- **Center stage:** a conference room, a floor of open cubicles, a
  glass-walled office at night. Fluorescent light. One plant. The
  projector at the head of the table showing the last slide.
- **Cast rail:** portrait chips as security-badge photographs on grey.
  Names in a corporate serif or waybar-style sans; tiny title beneath
  ("VP, Strategic Initiatives").
- **Phones:** cards are printed memos, embargoed pages, meeting-minute
  lines. Private cards are marked CONFIDENTIAL in a stamp treatment.
  Action cards are agenda items.

## 4. Palette Anchors

| Role (0069 token) | Anchor | The vibe |
| --- | --- | --- |
| `--theme-glow` | Fluorescent warm-white `#DFD9C4` | The overhead light nobody chose. |
| `--narrator` | Cool paper `#E6E4DE` | Copier-paper white. Reads *memo*. |
| `--private` | Ledger blue `#5A7291` | Corporate blue that has been used for a hundred years. |
| `--accuse` | Alarm red `#B93443` | The exit-sign red. Panic-button red. |
| `--ok` | Approval green `#5E9977` | The tick-box green in enterprise software. |

Warmth cue: **cool overhead, no window**. The base is still near-black;
the overhead light is a *source* but it is *ambient corporate light*,
which reads *institutional*, not warm.

## 5. Typography

- **Display face.** A modern grotesk or a *waybar-adjacent* editorial
  sans with weight. Reference: *Inter Display* variable, or an OFL
  grotesk like *Manrope*. Verify at 28px TV floor. Beat titles set in
  small-caps with tracking.
- **UI face.** Inter (constant). Slightly wider tracking here vs. other
  wrappers to emphasize the *system-formal* register.
- **Voice rule.** Narrator never speaks Inter; UI never speaks the
  editorial sans.

## 6. Material Vocabulary

- **Surfaces.** Vinyl wall base, industrial carpet, laminated wood,
  drop-ceiling tile, glass office wall, aluminum door frame, mesh
  chair, single ivy plant, whiteboard.
- **Card framings.** Identity cards render as security badges on grey
  card. Private-event cards are CONFIDENTIAL-stamped memos. Action
  cards are agenda-item rows.
- **Texture.** A faint copier-paper grain across the near-black base; a
  suggestion of a fluorescent tube reflection along the top edge of the
  stage.
- **Cast rail.** Names in the grotesk; portrait slot rounded-square,
  badge-style, with a tiny lanyard hairline.

## 7. Motion Character

- **Sharp, on the tick.** Elements land on a metronome; motion is *clocked*.
  Beat-turn dim happens with the confidence of an office lighting
  circuit switching off.
- **`seq-body`** is a fluorescent flicker. Two frames of stutter, hard
  cut to black, silence beat, single line, resume with the overhead back on.
- **Ambient is a fluorescent hum**: whisper-line has a nearly-imperceptible
  shimmer at very short period. Reduced motion holds it perfectly still.

## 8. The Host  -  Vesper as the Chief of Staff

**See** [`the-host.md`](../the-host.md) for Vesper's bible. This is
Vesper *reduced*  -  her most contained register. Because the baseline
is so flat, every shift lands like a crack in a glass.

- **Vesper's role tonight.** The Chief of Staff. Or HR. Speaks like
  someone who has drafted memos about worse. Not warm. Not cruel.
  *Efficient*. The Jackman-Logan end of her voice recipe.
- **Register.** Dry, procedural, faintly resigned. Every sentence is
  a talking point. Every third sentence isn't.
- **Cast-rail silhouette shape.** Security badge with a lanyard
  hairline, tiny title beneath the name.
- **Sample lines.**
  - *(Opening  -  flat, professional.)* "Welcome, everyone, to Q4
    close. The catering is here. The agenda is here. Marcus is
    somewhere on the fifth floor. Let us begin."
  - *(Beat turn, B2  -  the shift, whisper-quiet.)* "Marcus has not
    returned from the fifth-floor kitchen. We are treating this as a
    scheduling matter.  -  For now."
  - *(Interrogation stinger  -  procedural, cutting.)* "The couch would
    remind Ms. Kent that this conversation is not, strictly speaking,
    off the record. Nothing here is. That is HR's position."
  - *(The Wink.)* "The couch is reminded that participation in this
    session is voluntary and appreciated. Refreshments are your
    responsibility."
  - *(Reveal.)* "It was on the shared drive the whole time. It has
    always been on the shared drive.  -  Marcus, in fairness, had
    warned us."

## 9. The Showcase Moment (`seq-truth`, Beat 6)

The fluorescent goes down to one panel. The cast rail portraits step
forward one at a time  -  narrator names what each *almost* caught,
ending on a corporate detail (the sent-at timestamp, the printer
history, the calendar hold nobody remembers making). The killer's
badge lifts to center; a red exit-sign glow (`--accuse`) fills the
badge frame; the last line lands in the grotesk at full weight against
industrial-carpet black. The overhead light cuts. Cut to superlatives.

## 10. Failure Modes (Do Not Ship)

- **Actual horror.** Uncanny is the register, not psychological
  distress. No Kubrick Overlook shots; no *Backrooms* aesthetic.
- **Comic-Sans corporate parody.** The comedy is *deadpan minimalism*.
  Bad-clip-art anti-humor is not the register.
- **Startup-blue cheer.** The retired sky-blue accent stays retired.
  This wrapper is *institutional*, not *hip*.
- **Overexplaining.** Do not annotate the corporate details on-screen.
  The cast reads the joke; the frame does not point at it.

## 11. AW-268 Handoff Slots

- [ ] Reference image collection attached (film stills, office
      photography, corporate hospitality references).
- [ ] Portrait treatment decided (security badge recommended).
- [ ] Card framing SVGs authored (badge, CONFIDENTIAL memo, agenda).
- [ ] Background texture (copier grain / fluorescent reflection) SVG or CSS.
- [ ] Fluorescent-hum ambient rule authored (period, amplitude,
      reduced-motion override  -  must default to *off* for accessibility).
- [ ] Narrator voice fragments authored per 0068 §3.3.
- [ ] Contrast table per parent brief §5.
- [ ] Reduced-motion parity screenshots per `seq-*`.
