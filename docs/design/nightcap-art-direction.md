# Nightcap Art Direction Brief

> Current version: v0.2
> Last updated: 2026-07-17
> Status: Approved (founder, 2026-07-16; v0.2 expansion 2026-07-17); recorded as D-073 in `docs/product/decisions-log.csv`
> Canonical path: docs/design/nightcap-art-direction.md
> Task: AW-267 (#184)

## Purpose

This brief is the single source of truth for Nightcap's visual identity. It
sits above the execution-level detail in spec 0069 (tokens, motion
sequences, component inventory) and below the story bibles (which own
experience truth). It tells AW-268 — and every future theme skin, asset
production pass, and rendering PR — what Nightcap should look and feel
like, so no downstream work has to re-litigate direction mid-implementation.

Everything in this brief is direction. Nothing here is executable code,
gameplay scope, or a schema change. The engine remains surface-agnostic;
this document governs choices made in the game layer (`nightcap-web`) and
in per-theme asset production.

## References

- Story bibles:
  - `docs/story-bibles/nightcap-couch-race.md` (v1 launch target — canonical experience)
  - `docs/story-bibles/nightcap-murder-mystery.md` (Imposter Variant, world rules and setting library — §2, §5, §10, §11 inherited)
- Product decisions: D-066 (Tier 1/Tier 2 polish split), D-070 (story is animation + audio + text), D-071 (Couch Race is Nightcap v1 launch target)
- ADR-0013 (Couch Race launch target; cold open and suspect stage as D-070 showcase moments)
- Specs:
  - `docs/specs/0068-game-experience-quality-bar.md` §6 (aesthetic charter — principles this brief interprets)
  - `docs/specs/0069-nightcap-visual-design-system.md` v1.1 (execution — tokens, motion sequences, component inventory)
  - `docs/specs/0061-aw-258-tell-me-something-true.md` (social-opener design; wrapper reference)
- Moodboards: `docs/design/moodboards/high-society.md`, `docs/design/moodboards/corporate.md`, `docs/design/moodboards/sci-fi.md`

---

## 1. Visual Identity

**One sentence.** Nightcap should look like the murder mystery movie you
wanted to be inside — a room that has *just* gone wrong, staged with the
composition of prestige TV, dressed with the specificity of a production
designer, lit with the confidence of a show that knows its own genre.

Four governing ideas, in order of enforcement priority:

1. **Cinema first.** Every session is a short film your friends are inside.
   The reference altitude is *Glass Onion*, *Knives Out*, *The Menu*,
   *Death on the Nile*, *Succession*, *Severance*, *Blade Runner 2049*,
   *Crimson Peak* — shows and films where you can freeze any frame and it
   holds together. Nightcap must survive the same test. A stranger walking
   past the TV should stop because the *frame* is interesting, before they
   understand a word of the plot.
2. **The room is the stage.** The TV is a *stage*, not a HUD. The phone is
   a *private dossier*, not a controller. This split is a felt property
   before it is a technical one: at every moment, a stranger walking into
   the living room should be able to tell — without hearing a word — which
   surface is speaking to whom.
3. **Dark stage, warm light.** The base is near-black so that themed light
   (candlelight, ultraviolet, chrome) reads as *light*, so late-evening
   living-room TVs never flood the room, and so the narrator's voice can
   glow. Backgrounds recede. Words and moments carry the polish.
4. **Motion is meaning.** Animation happens when *the story* moves — beat
   turns, revelations, accusations, suspect cracks. Chrome never dances.
   The motion budget is scarce so that the budgeted moments land. Reduced
   motion collapses movement but preserves the *pauses* — the drama survives
   even when the movement goes.

**Appeal test.** Every wrapper and every moodboard must pass an
obvious-appeal check: someone flipping past this session on a stranger's
TV should *want* to sit down. If the mood does not have a hook a stranger
would recognize inside two seconds — a room, a light, a face, a texture
they know from something they've watched — the moodboard is not done.

**What Nightcap is not.**

- Not a game show. No point-total shouting, no lit-up buzzer aesthetic.
- Not a puzzle app. No dense chrome, no persistent progress rails.
- Not horror-as-distress. Suspense and mood are welcome — including
  spooky, gothic, and unsettled registers — but the tension is
  investigative and social, never psychological distress directed at the
  player.
- Not neutral SaaS. The current sky-blue dashboard palette is retired from
  player-facing surfaces.

## 2. Diegetic Wrapper System

Story bible §2 lists a wide range of era + occasion instances Nightcap
can generate a session inside. Producing a distinct art skin per instance
is not affordable. AW-268 groups instances into **three diegetic
wrappers** — thematic families that share aesthetic DNA. Inside each
wrapper, this brief ships **multiple moodboards** so that "a High
Society session" isn't a single look: 1928 Prohibition-deco, Victorian
gothic, Riviera 1962, and turn-of-the-century circus are all High
Society, and none should feel like the same night.

### 2.1 The three wrappers

| Wrapper | Spine | Launch skin (0069) | Range covered by the moodboards below |
| --- | --- | --- | --- |
| **High Society** | Period-realistic gatherings of wealth and social standing. Old-money textures. Ornament as vocabulary. | **Séance 1928** | Deco/prohibition, Victorian gothic, mid-century Riviera glam, turn-of-the-century circus. |
| **Corporate** | Contemporary status gatherings — professional, celebrity-adjacent, or nostalgic-tech. Engineered warmth over polished neutral. | *(No launch-window skin; direction-only until AW-268 activates it, per D-046.)* | Contemporary billionaire estate, uncanny corporate boardroom, reality-TV / influencer retreat, late-90s / early-2000s startup launch. |
| **Sci-Fi** | Speculative or future gatherings. Cool light on dark ground. The future as *atmosphere*, not gadget. | **Orbital Gala 2087** | Chrome-and-UV space opulence, neon-noir cyberpunk, off-world colony frontier, upload/simulation gathering. |

### 2.2 The moodboard index

Twelve moodboards, four per wrapper. Each covers a distinct *mood* within
its wrapper — moody, spooky, glossy, goofy, tense, nostalgic — so that
AW-268 can select or produce a skin whose reference set matches the case
the engine is about to run. Skin PRs may adopt one moodboard whole, or
blend two adjacent moodboards inside the same wrapper (never across
wrappers).

**High Society**

- [Séance 1928](moodboards/seance-1928.md) — deco + prohibition, moody-glamorous. *(Launch skin.)*
- [Manor Gothic](moodboards/manor-gothic.md) — Victorian and Edwardian, spooky-elegant.
- [Riviera 1962](moodboards/riviera-1962.md) — mid-century, sunlit-glossy.
- [Big Top 1899](moodboards/big-top-1899.md) — turn-of-the-century circus, macabre-carnival.

**Corporate**

- [The Estate](moodboards/the-estate.md) — contemporary billionaire, glossy-menacing.
- [Boardroom Severance](moodboards/boardroom-severance.md) — modern corporate, uncanny-minimal.
- [Influencer Retreat](moodboards/influencer-retreat.md) — reality-TV retreat, goofy-shiny.
- [Y2K Launch](moodboards/y2k-launch.md) — late-90s / early-2000s startup, nostalgic-neon.

**Sci-Fi**

- [Orbital Gala 2087](moodboards/orbital-gala-2087.md) — space-station opulence, chrome + UV. *(Launch skin.)*
- [Neon Noir](moodboards/neon-noir.md) — cyberpunk city, moody-crime.
- [Colony Post](moodboards/colony-post.md) — off-world frontier, tense-technical.
- [Sim Reunion](moodboards/sim-reunion.md) — upload / simulation, absurd-melancholic.

### 2.3 Rules for wrappers and moodboards

- **A wrapper is a *skin*, not a redesign.** It swaps semantic-token
  values (0069 §2), the display typeface (0069 §3), the card-framing
  texture, and the narrator persona register — nothing else. If a wrapper
  needs a layout change, that is a defect in the base identity, not the
  wrapper.
- **Every moodboard must satisfy the accessibility contract in §5
  unchanged.** Neither `--accuse` nor `--ok` may be color-only. No text
  below the surface minimums. Focus-visible states required.
- **Every moodboard must sustain a coherent Nightcap-voiced narrator
  (§4.4).** Different persona registers per moodboard are the point;
  breaking the Nightcap voice for the sake of a wrapper is not.
- **Moodboards do not add gameplay, mechanics, or scope.** They only
  change how the same six-beat arc *looks and sounds*.
- **Wild-card instances** (Wild West saloon, music-festival backstage,
  bachelorette weekend from story bible §2) are not covered by the
  launch set of moodboards. They are legitimate future additions to
  either an existing wrapper or a fourth wrapper; not launch scope.

Each moodboard in `docs/design/moodboards/` reads like a short producer's
pitch: a 30-second read-aloud pitch, a reference set that makes the look
obvious, palette anchors, material vocabulary, motion character, a
narrator voice sample, a description of the reveal moment for that
board, failure modes, and AW-268 handoff slots. AW-268 should be able to
brief a designer or an image model from any single moodboard without a
second conversation.

## 3. Motion Principles

Motion budget from 0068 §6 and enforced in 0069 §6. This brief owns the
intent behind those tokens.

- **The five named sequences are the whole animation vocabulary.**
  `seq-join`, `seq-beat-turn`, `seq-body`, `seq-spotlight`, `seq-truth` are
  the only places dramatic time is spent. Chrome (buttons, forms, list
  entries, tokens ticking down) never uses dramatic time.
- **The cold open (`seq-body`) and The Truth (`seq-truth`) are the polish
  showcases, with the suspect stage (`seq-spotlight`) close behind.** Per
  D-070 and ADR-0013 §6, treat these like the product's trailer: build
  them like the moment someone lifts a phone to film, not like the tech
  demo. If time is short, cut animation *elsewhere* to protect them.
- **Motion directs attention.** A revealed clue enters where the eye needs
  to look. A cracking suspect's chip elevates *toward* the accuser's cast
  position. Motion that only decorates is cut.
- **Stopping is a motion.** The 2-second silence beat inside `seq-body`
  (death is sudden — the stage snaps darker, the room stills, a single
  line lands, then the narrator resumes) is the most important stroke in
  the entire vocabulary. Do not lose it to smoothing.
- **Waiting states are staged, not spun.** A suspect answering under
  latency shows the suspect *hesitating* on the stage — a held breath, a
  glance away, a note re-checked. Never a loading spinner in the reveal
  moment.
- **`prefers-reduced-motion` collapses movement to crossfades but preserves
  timing structure.** The pauses still happen. The game is fully legible
  and winnable with motion off — this is a Tier 1 requirement, not a
  courtesy.

## 4. Typography

Direction (see 0069 §3 for tokens):

1. **The narrator has one voice, the UI has another.** The narrator never
   speaks in the UI face; the UI never speaks in the narrator's face. This
   single rule turns the narrator into a character rather than a system
   message and is the cheapest characterization tool in the whole design
   system.
2. **UI face is constant across wrappers.** Inter (already shipped).
   Chrome, forms, dense phone text. It disappears politely — that is its
   job.
3. **Display face swaps with the wrapper.** Warm serif for High Society
   (Fraunces as reference), wide grotesk or engineered mono-serif hybrid
   for Sci-Fi (Space Grotesk as reference), curated modern serif or
   editorial sans for Corporate (to be selected during AW-268 with the
   contrast/legibility tests below). One display face per skin. Never two.
4. **Fonts are self-hosted OFL only.** No CDN, no third-party runtime
   dependency. A living-room session cannot depend on font.googleapis.com.
5. **TV floor: 28px rendered at 1080p, verified at 720p.** Older
   living-room TVs are the real install base. If a screen needs a fourth
   hierarchy level, split it *in time*, not *in space* — the stage may
   present one thing at a time.
6. **Phone floor: 17px body; line length ≤ 34em.** The dossier is read
   at arm's length in a dim room. Err large.

## 5. Color

Direction (see 0069 §4 for tokens):

1. **Base stage inherits across wrappers.** `--stage-0`, `--stage-1`,
   `--stage-2`, `--ink-primary`, `--ink-muted`, `--line`. These do not vary
   by wrapper. They are the theater floor.
2. **A wrapper recolors five semantic roles.** `--theme-glow` (the
   wrapper's "light"), `--narrator` (the narrator's tint), `--private`
   (phone-only framing), `--accuse` (accusation / the killer at reveal),
   `--ok` (success, safe). Nothing else.
3. **Contrast is a design constraint, not a review afterthought.** All text
   ≥ WCAG AA against its surface; narrator lines on the TV target 7:1
   because they are the product. Every wrapper ships with a checked
   contrast table (0069 §4 pattern).
4. **`--accuse` versus `--ok` must remain distinguishable under
   deuteranopia.** Every accusation and safe-state affordance carries a
   non-color signal too: the token icon, a check or cross, motion
   direction, position. Color never carries meaning alone.
5. **Warmth cue distinguishes wrappers.** High Society is warm-source
   (candle, gilt, lamplight). Sci-Fi is cool-source (UV, chrome, plasma).
   Corporate is *staged-warm* (engineered warmth over polished neutral —
   the color of a hospitality-grade uplight). This is a felt property and
   an aesthetic tell.
6. **Retire the sky-blue dashboard accent from player surfaces.** It reads
   SaaS. The dashboard (developer surface) may keep it.

## 6. Narrator Visual Presence

The narrator is Nightcap's host intelligence and its single strongest
characterization tool. Direction:

1. **The narrator lives on the TV, not the phone.** Its lines take the
   stage — never a chat bubble, never a system toast. The phone may echo a
   private beat from the narrator (a whisper aside), but the narrator's
   home is the stage.
2. **The narrator is typographically distinct at all times.** Display
   face, `--narrator` tint, its own line rhythm (short lines, generous
   air, ≤ 2 sentences on screen at once per 0068 §3.3). A player who walks
   in during Beat 4 should know within two seconds *who is speaking*.
3. **The narrator's presence has three registers.** *Ambient* (whisper
   line at the top of the stage: "Evidence Locker opens in 2:00" — small,
   muted, never animated); *diegetic* (center-stage beat and revelation
   lines — the core register); *dramatic* (the reveal — display face at
   full weight, held on screen, no competing content). Register is chosen
   by the moment, not the player.
4. **The narrator is player-addressing but never player-mocking.** It
   addresses players only by character name. Dry wit allowed. Mockery of
   players never. The narrator takes the story seriously. It does not take
   itself too seriously.
5. **The narrator's tone shifts with the wrapper; its rules do not.** A
   High Society narrator is the martini-dry MC of a very expensive
   evening. A Corporate narrator is the mordant Ops lead who has watched
   this quarter go sideways before. A Sci-Fi narrator is the ship-log
   voice that has seen worse and is unimpressed. Each is Nightcap-voiced:
   witty without being smug, suspenseful without being portentous,
   irreverent without undercutting the stakes.
6. **The narrator never confirms or denies a theory before The Truth,
   never names the killer early, never reveals which suspect statements
   were lies.** These are inviolable across every wrapper.

## 7. Priority Order When Time Is Short

Beat labels here reflect the six-beat Couch Race arc per D-071 (the v1
launch target). Spec 0069 §5 uses the eight-beat Imposter Variant labels
for the same `seq-*` sequences; the sequences are the same, only the
beat numbers differ.

Per 0068 §6 and reaffirmed by D-070 / ADR-0013 §6, if a rehearsal or
milestone forces a choice between polish targets, execute in this order.
This is binding when time is short:

1. **The Truth (`seq-truth`, B6).** The single most polish-worthy screen
   in the product. If only one screen ships fully art-directed, this is it.
2. **The cold open (`seq-body`, B1).** The trailer moment. First
   impression of the entire product.
3. **The suspect stage (`seq-spotlight`, B3 / B5 Last Call).** The moment
   the platform's headline primitive (knowledge-gated dialogue) is
   visible as gameplay.
4. **The lobby (`seq-join`, pre-B1).** Joining should feel like being
   announced.
5. **Beat turns (`seq-beat-turn`, every beat).** The night's drumbeat.

Everything else (chrome, list entry motion, mini-game transitions,
scoreboard) sits below all five and cannot borrow their budget.

## 8. What Belongs to AW-268 (Execution)

This brief is direction. AW-268 executes it. The following belong to
AW-268 and are out of scope here:

- Illustration and portrait production per wrapper.
- Per-theme background textures, card framings, and ornament.
- The five stinger audio set (arrival, body, accusation, wrong-accusation,
  truth) per 0068 §6 and D-070 — sourced or produced per wrapper.
- Portrait / avatar treatment on the cast rail (0069 §Open Questions).
- Any illustration or animation asset file.

AW-268 must ship each wrapper as a **skin PR** that passes the 0069 §7 and
§Acceptance-Criteria checklist:

- 5 semantic color overrides
- 1 display face
- 1 background texture
- Card framing per card type (identity, private event, action)
- Narrator persona styling note
- Checked contrast table
- Reduced-motion parity screenshot for each `seq-*`

## 9. What Belongs to Neither This Brief Nor AW-268

- Engine, schema, API, or `presentation_hints` field changes.
- New gameplay, new beats, new mini-games, new scope of any kind.
- TTS or speech synthesis (out per D-066 and the scope boundary for the
  Rehearsal 1 window).
- Dashboard styling — developer surfaces keep the utilitarian look.
- Continuity or recap-artifact visuals — v1.1 per D-051.

## 10. Acceptance Criteria (This Brief)

1. This document exists at `docs/design/nightcap-art-direction.md` and
   covers visual identity, per-wrapper theme aesthetic, motion,
   typography, color, and narrator visual presence.
2. Twelve text-based moodboards exist in `docs/design/moodboards/`
   (four per wrapper — see §2.2 for the index) and each is sufficient
   for AW-268 to shop against without a second briefing.
3. The brief does not couple visual tokens to any single mini-game.
4. Founder sign-off is recorded in `docs/product/decisions-log.csv` as
   D-073.

## 11. Open Questions (Deferred)

- **Portrait/avatar treatment on the cast rail.** Initials chip versus
  themed silhouette set. Decided with the first skin PR in AW-268.
- **Whether the host needs a distinct "director view" style pass.**
  Revisit after Rehearsal 1 blocker log.
- **Enterprise wrapper skin.** No launch-window commitment. Direction is
  in place so AW-268 can activate the wrapper when the enterprise wedge
  (D-046) lights up.

## 12. Change Log

- **2026-07-17** — v0.2 (AW-267, PR #243 review). Founder feedback:
  moodboards need range, cinema, and obvious appeal. Added **Cinema
  first** governing principle (§1) and the appeal-test bar. Replaced the
  three wrapper-level moodboards with **twelve mood-specific moodboards**
  (four per wrapper, indexed in §2.2). Each new moodboard is written as a
  producer's pitch with named TV/film references, palette anchors,
  material vocabulary, narrator voice samples, and a per-moodboard
  description of the reveal moment.
- **2026-07-16** — v0.1 authored (AW-267). First draft covering all
  required sections; three wrapper-level moodboards written; D-073
  recorded in decisions-log.csv.
