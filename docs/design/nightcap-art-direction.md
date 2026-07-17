# Nightcap Art Direction Brief

> Current version: v0.3
> Last updated: 2026-07-17
> Status: Candidate research, founder direction not yet selected
> Canonical path: docs/design/nightcap-art-direction.md
> Task: AW-267 (#184)

> This document is reversible research for the founder discovery interview. It
> cannot guide AW-268 or establish a final visual direction until the required
> collaboration phases produce explicit approval.

## Purpose

This brief is the single source of truth for Nightcap's visual identity. It
sits above the execution-level detail in spec 0069 (tokens, motion
sequences, component inventory) and below the story bibles (which own
experience truth). It tells AW-268  -  and every future theme skin, asset
production pass, and rendering PR  -  what Nightcap should look and feel
like, so no downstream work has to re-litigate direction mid-implementation.

Everything in this brief is direction. Nothing here is executable code,
gameplay scope, or a schema change. The engine remains surface-agnostic;
this document governs choices made in the game layer (`nightcap-web`) and
in per-theme asset production.

## References

- Story bibles:
  - `docs/story-bibles/nightcap-couch-race.md` (v1 launch target  -  canonical experience)
  - `docs/story-bibles/nightcap-murder-mystery.md` (Imposter Variant, world rules and setting library  -  §2, §5, §10, §11 inherited)
- Product decisions: D-066 (Tier 1/Tier 2 polish split), D-070 (story is animation + audio + text), D-071 (Couch Race is Nightcap v1 launch target)
- ADR-0013 (Couch Race launch target; cold open and suspect stage as D-070 showcase moments)
- Specs:
  - `docs/specs/0068-game-experience-quality-bar.md` §6 (aesthetic charter  -  principles this brief interprets)
  - `docs/specs/0069-nightcap-visual-design-system.md` v1.1 (execution  -  tokens, motion sequences, component inventory)
  - `docs/specs/0061-aw-258-tell-me-something-true.md` (social-opener design; wrapper reference)
- **The Host bible**: `docs/design/the-host.md` (Vesper  -  canonical narrator reference; every moodboard cross-references it)
- Moodboards: twelve mood-specific boards in `docs/design/moodboards/` (see §2.2)

---

## 1. Visual Identity

**One sentence.** Nightcap should look and sound like the murder mystery
you wanted to be inside  -  a room that has *just* gone wrong, staged with
the composition of prestige TV, dressed with the specificity of a
production designer, hosted by a character who is delighted you came and
also, mid-sentence, very sorry to tell you what happened.

Five governing ideas, in order of enforcement priority:

1. **Vesper is the signature.** Nightcap's Host  -  see
   [`the-host.md`](the-host.md) for her bible  -  is the single strongest
   characterization tool in the whole product. Every session is Vesper
   welcoming you, running the room, and delivering the reveal. She is a
   named character (not a system voice); she has *range* (the *shift*
   between jubilant and grave inside a single line is her signature);
   she performs each wrapper as a role a great actor takes. If a
   generated line does not sound like Vesper, review fails.
2. **Cinema first.** Every session is a short film your friends are
   inside. Reference altitude: *Glass Onion*, *Knives Out*, *The Menu*,
   *Death on the Nile*, *Succession*, *Severance*, *Blade Runner 2049*,
   *Crimson Peak*  -  shows and films where you can freeze any frame and
   it holds together. A stranger walking past the TV should stop
   because the *frame* is interesting, before they understand a word of
   the plot.
3. **The room is the stage.** The TV is a *stage*, not a HUD. The phone
   is a *private dossier*, not a controller. This split is a felt
   property before it is a technical one: at every moment, a stranger
   walking into the living room should be able to tell  -  without hearing
   a word  -  which surface is speaking to whom.
4. **Dark stage, warm light.** The base is near-black so that themed
   light (candlelight, ultraviolet, chrome) reads as *light*, so late-
   evening living-room TVs never flood the room, and so Vesper's line
   can glow. Backgrounds recede. Words and moments carry the polish.
5. **Motion is meaning.** Animation happens when *the story* moves  -
   beat turns, revelations, accusations, suspect cracks. Chrome never
   dances. The motion budget is scarce so that the budgeted moments
   land. Reduced motion collapses movement but preserves the *pauses*  -
   the drama survives even when the movement goes.

**Appeal test.** Every wrapper and every moodboard must pass an
obvious-appeal check: someone flipping past this session on a stranger's
TV should *want* to sit down. If the mood does not have a hook a stranger
would recognize inside two seconds  -  a room, a light, a face, a texture
they know from something they've watched  -  the moodboard is not done.

**What Nightcap is not.**

- Not a game show. No point-total shouting, no lit-up buzzer aesthetic.
- Not a puzzle app. No dense chrome, no persistent progress rails.
- Not horror-as-distress. Suspense and mood are welcome  -  including
  spooky, gothic, and unsettled registers  -  but the tension is
  investigative and social, never psychological distress directed at the
  player.
- Not neutral SaaS. The current sky-blue dashboard palette is retired from
  player-facing surfaces.

## 2. Diegetic Wrapper System

Story bible §2 lists a wide range of era + occasion instances Nightcap
can generate a session inside. Producing a distinct art skin per instance
is not affordable. AW-268 groups instances into **three diegetic
wrappers**  -  thematic families that share aesthetic DNA. Inside each
wrapper, this brief ships **multiple moodboards** so that "a High
Society session" isn't a single look: 1928 Prohibition-deco, Victorian
gothic, Riviera 1962, and turn-of-the-century circus are all High
Society, and none should feel like the same night.

### 2.1 The three wrappers

| Wrapper | Spine | Launch skin (0069) | Range covered by the moodboards below |
| --- | --- | --- | --- |
| **High Society** | Period-realistic gatherings of wealth and social standing. Old-money textures. Ornament as vocabulary. | **Séance 1928** | Deco/prohibition, Victorian gothic, mid-century Riviera glam, turn-of-the-century circus. |
| **Corporate** | Contemporary status gatherings  -  professional, celebrity-adjacent, or nostalgic-tech. Engineered warmth over polished neutral. | *(No launch-window skin; direction-only until AW-268 activates it, per D-046.)* | Contemporary billionaire estate, uncanny corporate boardroom, reality-TV / influencer retreat, late-90s / early-2000s startup launch. |
| **Sci-Fi** | Speculative or future gatherings. Cool light on dark ground. The future as *atmosphere*, not gadget. | **Orbital Gala 2087** | Chrome-and-UV space opulence, neon-noir cyberpunk, off-world colony frontier, upload/simulation gathering. |

### 2.2 The moodboard index

Twelve moodboards, four per wrapper. Each covers a distinct *mood* within
its wrapper  -  moody, spooky, glossy, goofy, tense, nostalgic  -  so that
AW-268 can select or produce a skin whose reference set matches the case
the engine is about to run. Skin PRs may adopt one moodboard whole, or
blend two adjacent moodboards inside the same wrapper (never across
wrappers).

**High Society**

- [Séance 1928](moodboards/seance-1928.md)  -  deco + prohibition, moody-glamorous. *(Launch skin.)*
- [Manor Gothic](moodboards/manor-gothic.md)  -  Victorian and Edwardian, spooky-elegant.
- [Riviera 1962](moodboards/riviera-1962.md)  -  mid-century, sunlit-glossy.
- [Big Top 1899](moodboards/big-top-1899.md)  -  turn-of-the-century circus, macabre-carnival.

**Corporate**

- [The Estate](moodboards/the-estate.md)  -  contemporary billionaire, glossy-menacing.
- [Boardroom Severance](moodboards/boardroom-severance.md)  -  modern corporate, uncanny-minimal.
- [Influencer Retreat](moodboards/influencer-retreat.md)  -  reality-TV retreat, goofy-shiny.
- [Y2K Launch](moodboards/y2k-launch.md)  -  late-90s / early-2000s startup, nostalgic-neon.

**Sci-Fi**

- [Orbital Gala 2087](moodboards/orbital-gala-2087.md)  -  space-station opulence, chrome + UV. *(Launch skin.)*
- [Neon Noir](moodboards/neon-noir.md)  -  cyberpunk city, moody-crime.
- [Colony Post](moodboards/colony-post.md)  -  off-world frontier, tense-technical.
- [Sim Reunion](moodboards/sim-reunion.md)  -  upload / simulation, absurd-melancholic.

### 2.3 Rules for wrappers and moodboards

- **A wrapper is a *skin*, not a redesign.** It swaps semantic-token
  values (0069 §2), the display typeface (0069 §3), the card-framing
  texture, and the narrator persona register  -  nothing else. If a wrapper
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
  (death is sudden  -  the stage snaps darker, the room stills, a single
  line lands, then the narrator resumes) is the most important stroke in
  the entire vocabulary. Do not lose it to smoothing.
- **Waiting states are staged, not spun.** A suspect answering under
  latency shows the suspect *hesitating* on the stage  -  a held breath, a
  glance away, a note re-checked. Never a loading spinner in the reveal
  moment.
- **`prefers-reduced-motion` collapses movement to crossfades but preserves
  timing structure.** The pauses still happen. The game is fully legible
  and winnable with motion off  -  this is a Tier 1 requirement, not a
  courtesy.

## 4. Typography

Direction (see 0069 §3 for tokens):

1. **The narrator has one voice, the UI has another.** The narrator never
   speaks in the UI face; the UI never speaks in the narrator's face. This
   single rule turns the narrator into a character rather than a system
   message and is the cheapest characterization tool in the whole design
   system.
2. **UI face is constant across wrappers.** Inter (already shipped).
   Chrome, forms, dense phone text. It disappears politely  -  that is its
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
   hierarchy level, split it *in time*, not *in space*  -  the stage may
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
   Corporate is *staged-warm* (engineered warmth over polished neutral  -
   the color of a hospitality-grade uplight). This is a felt property and
   an aesthetic tell.
6. **Retire the sky-blue dashboard accent from player surfaces.** It reads
   SaaS. The dashboard (developer surface) may keep it.

## 5.5. Cast Rail Art Rule

The cast rail  -  the persistent row of suspects along the bottom of
the TV stage  -  is the single most-visible art surface in the whole
product. It is on screen for the entire session. It is the second
polish target after the reveal (§7 above). Direction:

1. **Silhouettes are always the visible cast rail on the TV.** Each
   wrapper ships a signature silhouette treatment: an oval brass
   cameo for Séance 1928; a daguerreotype gilt-hairline for Manor
   Gothic; a magazine half-tone rectangle for Riviera 1962; a laurel
   playbill oval for Big Top 1899; a press-kit square for The Estate;
   a security badge for Boardroom Severance; a soft-cornered Polaroid
   for Influencer Retreat; a pixelated lanyard for Y2K Launch; a
   hex-badge for Orbital Gala 2087; a cyan-outlined ID scan for Neon
   Noir; a crew-manifest thumbnail for Colony Post; a sim-avatar
   soft-square for Sim Reunion. The *silhouette shape* is the
   wrapper's cast-rail fingerprint. Every moodboard names its shape.
2. **AI-generated portraits are allowed only as private "file photos"
   on the phone dossier.** When a player taps a suspect on their
   phone, the dossier may reveal an AI-generated portrait styled
   through the wrapper's filter (paper grain for Séance, security-cam
   posterization for Boardroom, scan-line for Orbital, etc.). This
   keeps the "novel every session" magic without ever putting
   AI-portrait uncanny into the shared couch frame.
3. **The AI-portrait render is bounded.** One per suspect. Cached for
   the session. Styled through a wrapper filter opaque enough that
   AI tells (eye asymmetry, jewelry hallucinations) are absorbed
   into the style. If the wrapper's aesthetic cannot tolerate
   AI-portrait tells at all (Manor Gothic, Colony Post  -  where realism
   is the point), the phone dossier falls back to the silhouette on a
   letter background. This decision belongs per-wrapper in AW-268.
4. **The silhouette treatment is the launch commitment.** Illustrated
   portrait sets per wrapper (option 3 in the founder review) remain
   a legitimate stretch goal for hero wrappers post-launch. They are
   not launch-window scope.
5. **Player-uploaded photos** as a wrapper-styled cast-rail treatment
   are logged as a future product decision (§11 Open Questions). Not
   AW-267 or AW-268 scope.

## 6. The Host  -  Vesper

Vesper is Nightcap's Host. She is the single strongest
characterization tool in the whole product. Her bible is
[`docs/design/the-host.md`](the-host.md); this section is the visual
and stage-direction summary. Every wrapper performs her; every
moodboard reads as "Vesper as [role]."

### 6.1 Who Vesper is

**One-sentence recap.** Vesper is what you get when Caine from *The
Amazing Digital Circus*, David Tennant's Doctor, and Hugh Jackman's
ringmaster-into-tragedian split the same body  -  a performer whose
signature move is the *shift*: jubilant to grave and back inside a
breath, without ever losing the room. See `the-host.md` §2 for the
reference triad and §4 for how she wears each wrapper.

### 6.2 Visual presence

1. **Vesper lives on the TV, not the phone.** Her lines take the
   stage  -  never a chat bubble, never a system toast. In v1 the
   phone does not carry her voice at all. (A phone-whisperer
   register is future scope, not launch.)
2. **Vesper is typographically distinct at all times.** Display face,
   `--narrator` tint, short lines with generous air, ≤ 2 sentences on
   screen at once per 0068 §3.3. A player who walks in during Beat 3
   should know within two seconds *who is speaking*  -  and it is her.
3. **Vesper has three stage registers.** *Ambient* (whisper line at
   the top of the stage  -  small, muted, never animated); *diegetic*
   (center-stage beat and interrogation lines  -  her core register);
   *dramatic* (the reveal  -  display face at full weight, held on
   screen, no competing content). Register is a beat decision, not a
   skin decision.
4. **Vesper wears the wrapper.** Séance MC · Manor housekeeper ·
   Riviera correspondent · Ringmaster · Estate curator · Chief of
   Staff · influencer-retreat producer · Y2K MC · ship's log ·
   noir concierge · station Chief · sim customer host. Same
   character; different costume. See `the-host.md` §4 for the table.

### 6.3 Anti-slop authoring model  -  the guardrail

Vesper's dialogue is **authored refrains + AI-filled specifics.**
This is the single strongest defense against "AI slop" tells in the
whole product.

- **The *shape* of what Vesper says is handwritten**, per beat / per
  mood / per wrapper. The line library establishes cadence, rhythm,
  and  -  critically  -  the *shift target* on each line (which mood the
  line can pivot into on its final clause).
- **AI fills only the *specifics***  -  suspect name, timestamp,
  location, evidence detail, case-specific callback. The AI does not
  compose sentences for Vesper from scratch in v1.
- **Live-loop AI dialogue (spec 0071)** generates **suspect answers**
  from knowledge state. **It does not generate Vesper's lines.** This
  is the crisp boundary that keeps human spirit in the show.
- Line-library sizing, storage path, and per-beat/mood matrix live
  in `the-host.md` §5. Content-pipeline execution belongs to AW-283
  and the D-069 narrative-tasks lineage (AW-276–280).

### 6.4 Signature beats

Vesper's canonical moments are the same shape in every session; the
moodboards fill the specifics. See `the-host.md` §6 for detail.

- **The Opening**  -  jubilant welcome; last clause supports a
  shift-to-grave when the body drops in `seq-body`.
- **The Wink**  -  once per session, Vesper acknowledges the couch. She
  does not explain the game. She notices you.
- **The Reveal**  -  grave reconstruction, delighted-about-awful
  callback to the killer's best move, then one small ordinary last
  line. That last frame is the screenshot.

### 6.5 The three shifts

Vesper's characterization is *not* a tone  -  it is a *shift between
tones*. Every session must contain at minimum:

1. A **jubilant → grave** shift (the drop).
2. A **grave → jubilant** shift (the recovery  -  Vesper chooses to
   keep hosting).
3. A **wink** (fourth-wall aware; sparing; never tutorializing).

If a session lacks the shifts, the moodboard authoring failed. The
shift is the *human-spirit tell* that distinguishes Vesper from
narration.

### 6.6 What Vesper never does

- **Never names the killer before The Truth.**
- **Never confirms or denies a player's theory.**
- **Never breaks character to explain a mechanic** (UI does that in
  Inter; Vesper's line is in-fiction).
- **Never mocks a player.** She may be delighted by their wrongness.
  She is never cruel to them.
- **Never speaks as text-to-speech in v1.** Audio is out of scope per
  D-066 and the AW-267 directive.
- **Never appears in the phone dossier in v1.** Her stage is the TV.

## 7. Priority Order When Time Is Short

Beat labels here reflect the six-beat Couch Race arc per D-071 (the v1
launch target). Spec 0069 §5 uses the eight-beat Imposter Variant labels
for the same `seq-*` sequences; the sequences are the same, only the
beat numbers differ.

Per 0068 §6 and reaffirmed by D-070 / ADR-0013 §6, if a rehearsal or
milestone forces a choice between polish targets, execute in this
order. This is founder-ranked (AW-267 PR #243 review, 2026-07-17) and
binding when time is short:

1. **The Reveal (`seq-truth`, B6).** The single most polish-worthy
   screen in the product  -  this is *the screenshot*. It is what people
   film and repost. If only one screen ships fully art-directed, this
   is it.
2. **The Cold Open (`seq-body`, B1).** The trailer moment. First
   impression of the entire product; the shot that makes the couch's
   friends want to be at the next session.
3. **The Cast Rail / Lobby (`seq-join`, pre-B1, and the persistent
   rail).** The ensemble marquee  -  the shot that sells the session
   *before* it starts and holds the room through every beat. Named
   silhouettes plus wrapper framing; this is where Nightcap earns its
   own look on a stranger's TV.
4. **The Interrogation Crack (`seq-spotlight`, B3 / B5).** The gameplay
   showcase  -  the moment the platform's headline primitive
   (knowledge-gated dialogue) becomes visible as *play*.
5. **Beat turns (`seq-beat-turn`, every beat).** The night's drumbeat.

Everything else (chrome, list-entry motion, mini-game transitions,
scoreboard) sits below all five and cannot borrow their budget.

## 8. What Belongs to AW-268 (Execution)

This brief is direction. AW-268 executes it. The following belong to
AW-268 and are out of scope here:

- Illustration and portrait production per wrapper.
- Per-theme background textures, card framings, and ornament.
- The five stinger audio set (arrival, body, accusation, wrong-accusation,
  truth) per 0068 §6 and D-070  -  sourced or produced per wrapper.
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

## 8.5. Launch Surface and Distribution Direction

Candidate research note (2026-07-17, not approved direction): Nightcap launches
on **its own web app,
Jackbox-style**  -  the TV renders a room code and QR; phones join by
scanning or typing the code; a single browser session on the TV drives
the stage. Native / hardware surfaces (Steam, smart-TV apps,
console party-game surfaces) are legitimate Horizon 2 growth channels
and must not be painted into a corner by an MVP decision.

Design implications for AW-268 and downstream:

- **TV target is a 65-inch shared display at 3m viewing distance,
  rendered from a browser.** Typography floors (§4) and contrast
  targets (§5) are tuned for this.
- **Join flow gate stays under 30 seconds cold** (Rehearsal 1
  requirement, D-065). The room-code + QR moment lives on the
  lobby/marquee (`seq-join`)  -  the third-highest polish target (§7).
- **Discord Activity, in-Discord voice-call embed, and other
  third-party surfaces** are *deferred* growth channels. Not launch;
  not a design constraint on this brief. If they come back later, the
  cast-rail silhouette + Vesper voice profile port directly.
- **Netflix Party Games and Steam / hardware couch surfaces** stay
  interesting but sit past the launch window. They inform *don't
  paint into a corner*: no browser-only assumption that would block a
  future native compile; no non-web-portable font, animation, or
  layout dependency.

## 9. What Belongs to Neither This Brief Nor AW-268

- Engine, schema, API, or `presentation_hints` field changes.
- New gameplay, new beats, new mini-games, new scope of any kind.
- TTS or speech synthesis (out per D-066 and the scope boundary for the
  Rehearsal 1 window).
- Dashboard styling  -  developer surfaces keep the utilitarian look.
- Continuity or recap-artifact visuals  -  v1.1 per D-051.
- Vesper voice acting / audio recording. Post-M6 per 0068 §6; the
  authored refrain library ships text-only in v1 but must be
  recordable later without contradicting itself.
- Native / hardware surface adaptation (Steam, smart-TV, console).
  Horizon 2 per §8.5.
- Discord Activity embedding. Deferred growth channel, not launch
  scope.

## 10. Acceptance Criteria (This Brief)

1. This document exists at `docs/design/nightcap-art-direction.md` and
   covers visual identity, per-wrapper theme aesthetic, motion,
   typography, color, cast-rail art rule, the Host (Vesper), the
   anti-slop authoring model, and the launch surface direction.
2. `docs/design/the-host.md` exists as Vesper's character bible.
3. Twelve text-based moodboards exist in `docs/design/moodboards/`
   (four per wrapper  -  see §2.2 for the index) and each names its
   cast-rail silhouette shape, its "Vesper as [role]" register, and
   sample Vesper lines demonstrating the three shifts (§6.5).
4. The brief does not couple visual tokens to any single mini-game.
5. The prior D-073 approval claim is superseded by the collaboration reset;
   final founder sign-off remains pending.

## 11. Open Questions (Deferred)

- **Vesper's canonical silhouette.** Every player should recognize her
  outline the first time they see her  -  final form (a woman in a coat
  holding a decanter, an abstract vessel-and-hand icon, or something
  else entirely) is decided with the first AW-268 skin PR.
- **Player-uploaded photos** as a cast-rail treatment (a warm,
  personal, immediately-shareable direction). Introduces consent and
  content-moderation surface; requires a face-safe pipeline. Logged
  as a future product decision, not launch scope.
- **Whether the host controls surface needs a distinct "director
  view" style pass.** Revisit after Rehearsal 1 blocker log.
- **Enterprise wrapper skin.** No launch-window commitment. Direction
  is in place so AW-268 can activate the wrapper when the enterprise
  wedge (D-046) lights up.
- **Vesper's actor / voice casting.** Post-M6, when audio ships. No
  launch-window commitment; recorded here so v1 line-library authoring
  keeps the future recording session in mind.
- **Discord Activity embedding.** Deferred growth channel, revisited
  post-launch.

## 12. Change Log

- **2026-07-17**  -  v0.3 (AW-267, PR #243 founder review round 3).
  Named the Host: **Vesper**, with reference triad Caine (Amazing
  Digital Circus) + Tennant's Doctor + Jackman's ringmaster-into-
  tragedian range; the *shift* is her characterization. Created
  [`docs/design/the-host.md`](the-host.md) as her canonical bible.
  Locked the anti-slop authoring model  -  **authored refrains + AI-filled
  specifics**  -  with a per-beat / per-mood line library, sized in
  `the-host.md` §5. Added §5.5 cast-rail art rule (signature
  silhouettes always on the TV; AI portraits allowed only on private
  phone-dossier tap, wrapper-filter styled). Rewrote §6 as *The Host*
  and made every wrapper "Vesper as [role]." Re-ranked §7 priority
  order per founder ranking: Reveal → Cold Open → Cast Rail → Interro-
  gation Crack → Beat Turns. Added §8.5 launch-surface direction
  (Jackbox-style own web app; native / hardware = Horizon 2; Discord
  Activity deferred). Updated ACs (§10) and open questions (§11).
- **2026-07-17**  -  v0.2 (AW-267, PR #243 review). Founder feedback:
  moodboards need range, cinema, and obvious appeal. Added **Cinema
  first** governing principle (§1) and the appeal-test bar. Replaced the
  three wrapper-level moodboards with **twelve mood-specific moodboards**
  (four per wrapper, indexed in §2.2). Each new moodboard is written as a
  producer's pitch with named TV/film references, palette anchors,
  material vocabulary, narrator voice samples, and a per-moodboard
  description of the reveal moment.
- **2026-07-16**  -  v0.1 authored (AW-267). First draft covering all
  required sections; three wrapper-level moodboards written; D-073
  recorded in decisions-log.csv.
