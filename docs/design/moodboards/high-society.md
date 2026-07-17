# Moodboard — High Society

> Wrapper covered: **High Society** — period-realistic gatherings of wealth
> and social standing. Story-bible instances: 1920s Prohibition dinner,
> 1950s Hollywood cocktail party, contemporary estate dinner, Victorian
> manor, Gilded Age formal gathering.
>
> Launch skin: **Séance 1928** (spec 0069 §7A).
> Parent brief: `docs/design/nightcap-art-direction.md`.
> Status: Draft — no image assets attached (per AW-267 scope: direction only).

## 1. Reference Set

*Reference set is atmosphere and voice guidance; not source material to
reproduce. Nightcap generates its own cases inside this territory.*

- **Ensemble mysteries with a stage sense.** *Glass Onion* (2022), *Knives
  Out* (2019), *Gosford Park* (2001) — how a room full of guilty people
  looks when the lights are warm. Composition of tables, rooms, staircases.
- **Deco theatricality.** Early *Poirot* series, *Death on the Nile*
  (2022), *Babylon Berlin* — deco as a lived vocabulary of ornament,
  costume, and hospitality.
- **Old-money social containment.** *The Age of Innocence* (1993), *The
  Great Gatsby* (2013) — the specific discomfort of being in a room where
  everyone is politely armed.
- **Party-game format reference.** Jackbox *Murder Trivia Party*
  (format only, not creative ceiling) — how to keep a living room's
  attention across a shared display without becoming a scoreboard.

## 2. Palette Anchors

*Anchor values; skin PRs author actual palettes and override the 0069
semantic tokens in the wrapper skin file.*

| Role (0069 semantic token) | Anchor | Note |
| --- | --- | --- |
| `--theme-glow` | Brass `#D4A853` | The wrapper's light source. Candlelight and gilt. Never fluorescent. |
| `--narrator` | Warm ivory-gold `#C9B98F` | The narrator's voice tint. Distinct from player/system text. |
| `--private` | Aged-paper cool `#8FB4C9` | The "for your eyes only" phone framing. |
| `--accuse` | Oxblood `#7A2230` | Danger, accusation, the killer at reveal. Deep red, never scarlet. |
| `--ok` | Muted botanical `#5FA97F` | Success, safe. Reads *considered*, not celebratory. |

Warmth cue: **warm-source**. Every wrapper decision in this family biases
toward candle, hearth, gilt lamp, incandescent bulb. Cool light (moonlight
through a window, silver on a decanter) is a highlight, never a base.

## 3. Typography Anchors

- **Display face (narrator, beat titles, reveal).** *Fraunces* (OFL,
  variable weight + optical size) as the reference. Skin PRs may substitute
  an OFL deco serif (e.g., an *Ostrich* / *Poiret* register) if it holds
  the contrast requirement at TV distance and stays legible at 28px.
- **UI face.** Inter (constant across all wrappers).
- **Voice rule.** The narrator never speaks in Inter; the UI never speaks
  in the display face. This makes the narrator feel like a character.

## 4. Material Vocabulary

- **Surfaces.** Aged paper, polished walnut, brass, cut crystal, cream
  linen, waxed velvet, tarnished silver. Ornament reads *lived-in*, never
  costume.
- **Card framing.** Identity cards render as folded place-cards or
  monogrammed correspondence. Private event cards render as telegrams or
  sealed notes. Action cards render as calling cards.
- **Texture.** A faint smoke gradient across the deep-black base; the
  suggestion of candlelight bleed at the top of the stage. Never a
  photographic texture; always suggestion.
- **Cast rail.** Names set in the display face, letterspaced, with room
  around them. When portrait assets exist (AW-268), portraits sit in oval
  cameo frames.

## 5. Motion Character

- **Settle, don't snap.** Everything arrives *placed* — a note laid on a
  table, a chip set on a card. Even the beat-turn dim is unhurried.
- **The exception is `seq-body` (Beat 1 in Couch Race — the cold-open
  death, per D-071 arc).** Death is sudden here as it is in every
  wrapper: stage snaps darker, silence beat, single line, resume.
- **The reveal (`seq-truth`) is candlelit lantern-slide.** Names and
  clues cross-fade like slides in a magic-lantern show. This is the
  wrapper's signature motion moment.

## 6. Narrator Voice Notes

- **Persona.** The martini-dry MC of a very expensive evening. Has seen
  every guest here get worse before. Composed enough to observe the
  cracks without commenting on them until asked.
- **Vocabulary register.** Period-flavored but never pastiche. "The
  library has gone quiet, which is usually a sign." Never "Odds bodkins."
- **Line rhythm.** Short. Punctuated. Air between clauses. The narrator
  is a stage voice, not a text-block.
- **Dry wit.** Yes. Mockery of players: never.

## 7. Failure Modes (Do Not Ship)

- Sepia everything. Sepia over the whole stage kills contrast and reads
  costume, not diegetic. Warm light is a source; the base stays near-black.
- Serif-everywhere UI. The UI face stays Inter; the display face stays
  reserved for the narrator, beat titles, and reveal.
- Historical caricature. The wrapper is period-*realistic*, not
  period-clichéd. Absurdity comes from character behavior, not accent.
- Chrome ornament (thick gold trim on every button). Ornament earns its
  place on cards and cast-rail names only.

## 8. AW-268 Handoff Slots

Filled by AW-268 during skin production. Left empty by AW-267.

- [ ] Reference image collection attached (film stills, art plates,
      hospitality photography).
- [ ] Portrait treatment decided per this wrapper.
- [ ] Card framing SVGs authored.
- [ ] Background texture SVG or CSS gradient authored.
- [ ] Narrator voice fragments authored per 0068 §3.3.
- [ ] Contrast table per §5 of the parent brief.
- [ ] Reduced-motion parity screenshots per `seq-*`.
