# 0069 — Nightcap Visual Design System (UI, Animation, Aesthetic)

> Current version: v1.0
> Last updated: 2026-07-12
> Status: Draft (founder review → Approved)
> Author: Design session 2026-07-12
> Canonical path: docs/specs/0069-nightcap-visual-design-system.md

## References

- `docs/specs/0068-game-experience-quality-bar.md` §6 (aesthetic charter —
  this spec is its execution-level detail)
- `docs/story-bibles/nightcap-murder-mystery.md` §2 (era + occasion define
  the aesthetic; assets pre-produced per theme for first production run)
- `nightcap-web/src/ui.ts` (current styling: inline CSS custom properties)
- `nightcap-web/src/mini-game-kit/` (countdown, host-status-card, dom helpers)
- Spec 0060 / AW-230 (real-device privacy matrix — re-verify after restyle)
- Roadmap M5-G (visual identity — this spec is M5-G's definition of done)

## Overview

Nightcap's current UI is a competent dark developer-dashboard: navy panels,
sky-blue accent, Inter everywhere, no motion language. Nothing about it says
*a glamorous gathering interrupted by a death*. This spec defines the visual
design system that closes that gap: a two-layer token architecture (base
stage + theme skins), typography and color systems for both surfaces, a
motion/animation system with choreography for the story's staged moments,
and a component inventory mapped to the existing code.

Everything here lives in `nightcap-web` (game layer). No engine changes; the
engine's `presentation_hints` on content events remain the only contract.
Surface agnosticism is untouched — this is Nightcap deciding how to render,
which is exactly the layer that owns that decision.

## In Scope

- Design language and art direction (base identity + theme-skin system).
- Design tokens: color, typography, spacing, radius, elevation, motion.
- Surface layout systems: shared display ("the stage") and phone ("the dossier").
- Motion system and choreography specs for the staged story moments.
- Component inventory and refactor path from `ui.ts` inline styles.
- Accessibility and TV-legibility requirements.
- Two launch theme skin definitions.

## Out of Scope

- Engine/schema/API changes; any new `presentation_hints` fields.
- Audio (post-M6 candidate per 0068 §6).
- Dashboard (`dashboard/`) and SDK styling — developer surfaces keep the
  utilitarian look for now.
- Illustration/asset production pipeline details (per-theme asset briefs are
  produced when a theme is built; this spec defines the slots they fill).
- New gameplay mechanics or scope of any kind.

---

## 1. Design Language: "The Velvet Stage"

**One sentence:** every surface is a theater — the shared display is the
stage, each phone is a private dossier passed to you in the dark — and the
theme (era + occasion) is the production design that dresses the same stage.

Three laws derived from it:

1. **Dark stage, warm light.** The base is always a deep, near-black stage
   so that themed light (candlelight, neon, chrome) reads as *light*, and
   so living-room TVs don't flood the room. Backgrounds recede; words and
   moments glow.
2. **The base is structure, the theme is soul.** Layout, spacing, type
   scale, motion timing, and component anatomy never change per theme.
   Palette, display typeface, texture, ornament, and narrator styling always
   do. This keeps theme production cheap (a skin, not a redesign) and the
   game legible across sessions.
3. **Motion is meaning.** Animation happens when the *story* moves (beat
   turns, revelations, accusations). Chrome never dances. If everything
   moves, nothing matters — the motion budget in 0068 §6 is enforced here
   with named, tokenized sequences.

## 2. Token Architecture

Extract all styling from `ui.ts` inline CSS into a token layer:

```
nightcap-web/src/design/
  tokens.base.css      — structure: spacing, radius, type scale, motion, z, elevation
  tokens.semantic.css  — roles: --surface-*, --ink-*, --narrator, --private, --accuse, --ok
  themes/
    midnight.css       — default/fallback skin (refined version of today's navy)
    seance-1928.css    — launch theme skin A
    orbital-2087.css   — launch theme skin B
```

Rules:

- Components reference **semantic tokens only** (`var(--ink-primary)`, never
  `#eef2ff`, never a base token directly). Enforced by review; a simple grep
  check (`#[0-9a-f]{3,8}` outside `design/`) keeps it honest.
- Theme skins may override semantic tokens and the two display typefaces —
  nothing else. A skin that needs a layout change is a defect in the base.
- Surfaces are modes, not apps: `body.surface-display` and
  `body.surface-phone` switch the type scale and spacing density; both load
  the same theme skin.
- Fonts are self-hosted woff2, open-licensed (OFL). No CDN fetches — a
  living-room session must not depend on a font CDN. Two families per theme
  maximum: one display face (theme voice), one text/UI face (constant).

## 3. Typography

**Constant UI/text face:** keep Inter (already shipped) for chrome, forms,
and dense phone text. It disappears politely — that is its job.

**Display face (theme voice):** used for the narrator, beat titles, case
name, and the reveal. Default skin: **Fraunces** (OFL; warm, slightly
theatrical serif, variable weight/optical size — one file, many voices).
Theme skins may substitute (e.g., a deco face for 1928, a grotesk for 2087).

**Shared display scale** (1080p at ~3m viewing distance; use `clamp()` with
viewport units, minimums in px):

| Role | Size (min) | Notes |
| --- | --- | --- |
| Narrator line | 44px, display face | ≤ 2 sentences on screen at once (0068 §3.3) |
| Beat title / case name | 64–96px, display face | One dramatic line, letterspaced |
| Event title (clue found, player joined) | 36px | |
| Supporting detail | 28px | The floor. Nothing smaller ever renders on the TV |
| Cast rail names | 28px | |

Exactly three hierarchy levels visible at any moment (0068 §6). If a screen
needs four, the screen is overloaded — split it in time, not in space.

**Phone scale:** body 17px minimum, identity-card name 28px, section labels
13px caps. Line length ≤ 34em. The dossier is read at arm's length in a dim
room; err large.

**Voice rules:** the narrator never speaks in the UI font; the UI never
speaks in the narrator's font. This single rule makes the narrator feel like
a character rather than a system message — it is the cheapest
characterization tool in the entire design system.

## 4. Color System

**Base stage (all themes inherit):**

| Token | Value | Role |
| --- | --- | --- |
| `--stage-0` | `#0A0A0F` | Display background (near-black, blue-warm neutral) |
| `--stage-1` | `#14141D` | Panels/cards on display |
| `--stage-2` | `#1D1D29` | Raised elements, phone cards |
| `--ink-primary` | `#F2EEE3` | Primary text — warm off-white (candlelit paper, not #fff) |
| `--ink-muted` | `#9A94A6` | Secondary text |
| `--line` | `rgba(242,238,227,0.14)` | Hairlines |

**Semantic roles (theme skins recolor these):**

| Token | Default (midnight) | Role |
| --- | --- | --- |
| `--theme-glow` | `#D4A853` (brass) | The theme's "light": accents, focus, active states |
| `--narrator` | `#C9B98F` | Narrator text tint — always distinct from player/system text |
| `--private` | `#8FB4C9` | "For your eyes only" framing on phones |
| `--accuse` | `#B33A4A` (oxblood) | Accusation, danger, the killer's color at reveal |
| `--ok` | `#5FA97F` | Success, correct, safe |

Requirements:

- Contrast: all text ≥ WCAG AA against its surface; narrator lines on the
  display target 7:1 (they are the product).
- `--accuse` vs `--ok` must remain distinguishable under deuteranopia —
  never encode accusation outcomes by hue alone (pair with iconography:
  the token symbol, a check/cross, motion direction).
- The current sky-blue `#7dd3fc` accent is retired from player surfaces; it
  reads SaaS, not séance. (The dashboard may keep it.)

## 5. Layout Systems

### 5.1 Shared display — "the stage"

A fixed three-zone stage, all beats, all themes:

- **Center stage (≈70% height):** one thing at a time — the narrator line,
  the beat title, the mini-game spectacle, the accusation spotlight, the
  reveal. Never two competing focal points.
- **Cast rail (bottom):** every character as a name chip (portrait slot when
  theme assets exist), persistent all night. This is the "who's in the
  room" anchor, and where accusation/reveal choreography points.
- **Whisper line (top, thin):** ambient status ("Evidence Locker opens in
  2:00", join code during lobby). Small, muted, never animated.

The lobby is the stage's overture: case name large, QR + join code center,
cast rail filling in as players join — joining *is* the show starting.

### 5.2 Phone — "the dossier"

A single-column card stack, newest on top, three card types with fixed
anatomy:

- **Identity card** (the §3.1/0068 five-part format): theme-framed (letter,
  telegram, badge), display face for the name, the secret visually set
  apart (e.g., redacted-bar treatment revealed on tap — a private moment
  with a tiny thrill).
- **Private event card:** always carries the `--private` framing edge + "only
  you can see this" microcopy. Private must *look* different from public at
  a glance (supports the AW-230 privacy model perceptually).
- **Action card** (inputs, votes, mini-game entry): one primary action per
  card, thumb-reach button placement, disabled states that explain
  themselves ("Waiting for the others…").

## 6. Motion System

**Tokens:**

| Token | Value | Use |
| --- | --- | --- |
| `--t-instant` | 80ms, linear | Press states, toggles |
| `--t-quick` | 180ms, ease-out | Card entry, hover, small reveals |
| `--t-scene` | 420ms, cubic-bezier(0.2, 0, 0.1, 1) | Panel/scene changes |
| `--t-dramatic` | 900ms, cubic-bezier(0.6, 0, 0.2, 1) | Story moments only |

**The five named sequences** (the only places `--t-dramatic` may appear —
this *is* the motion budget from 0068 §6, made enforceable):

1. **`seq-join`** (lobby): new player's name materializes on the cast rail
   with a single glow pulse (~1s total). Joining feels like being announced.
2. **`seq-beat-turn`** (every beat): stage dims 400ms → beat title in
   display face fades/settles center 900ms → holds 1.5s → content enters.
   The night's drumbeat; identical rhythm every time, themed dressing.
3. **`seq-body`** (B2): the hard tonal turn. Stage snaps darker (fast, not a
   slow fade — death is sudden), 2s silence beat with a single line, then
   the narrator resumes. The one place where *stopping* motion is the effect.
4. **`seq-spotlight`** (B6 accusations): stage dims, accused's cast-rail
   chip elevates to center stage, accusation text lands beside it,
   resolution plays before the stage relights. Target 8–12s of screen
   time — long enough to film, short enough to not stall the table.
5. **`seq-truth`** (B8): a multi-step choreography (the 90–150s story
   sequence from 0068 §2): night reconstruction lines → per-player
   "what you almost caught" beats stepping along the cast rail → killer's
   best-deception line → the reveal (killer chip turns `--accuse`, display
   face, full center stage). This sequence is the single most
   polish-worthy screen in the product.

**Rules:** chrome (buttons, forms, lists) uses `--t-instant`/`--t-quick`
only. `prefers-reduced-motion` collapses every sequence to crossfades with
the same *timing structure* (the pauses still happen — the drama survives,
the movement goes). Mini-game kit components (`countdown.ts`) adopt the
tokens; the final-5-seconds countdown dramatization (0068 §5) uses
`--t-quick` pulses, not dramatic time.

## 7. Launch Theme Skins

Two skins at launch (plus `midnight` fallback), chosen to prove the system
spans the era space; each needs only: 5 semantic color overrides, 1 display
face, 1 background texture, card framing, and a narrator persona styling
note.

**A. Séance 1928** — candlelit deco parlor. Glow `#D4A853` brass; accuse
oxblood `#7A2230`; ink on aged-paper cards; deco-flavored display face
(e.g., OFL deco serif or Fraunces high-contrast cut); texture: faint smoke
gradient; identity cards as folded place-cards.

**B. Orbital Gala 2087** — chrome and ultraviolet. Glow `#9D7BFF`; accuse
`#FF4D6D`; ink cool-white `#EAF0FF`; display face: a wide grotesk (e.g.,
Space Grotesk); texture: faint starfield/glass reflection; identity cards
as security badges.

The contrast and colorblind requirements in §4 apply to every skin; a skin
PR includes a checked contrast table.

## 8. Component Inventory & Refactor Path

Current: ~1,400 lines in `ui.ts` with inline styles; mini-game kit has its
own DOM helpers. Refactor path (no behavior changes, existing 98 tests must
stay green):

1. **Stage A — tokens + base restyle:** extract `design/` token files;
   restyle existing screens against semantic tokens; retire raw hex from
   components; apply type scales per surface mode. Deliverable: the same
   app, dressed for the theater in `midnight`.
2. **Stage B — the five sequences:** implement `seq-*` as reusable
   choreography utilities (data-driven step lists, honoring
   reduced-motion); wire B2/B6/B8 staged moments per 0068 §2 bars.
3. **Stage C — theme skins:** ship `seance-1928` and `orbital-2087`;
   host theme selection already exists product-side (story bible §2 —
   era/occasion selection); skins bind to it in the web layer.

Component list (post-refactor): StageFrame, CastRail, WhisperLine,
NarratorLine, BeatTitle, DossierCard (identity/private/action variants),
AccusationSpotlight, TruthSequence, MiniGameFrame, Countdown (kit),
HostStatusCard (kit), JoinLobby.

**Sequencing vs. proof:** Stage A can precede Rehearsal 2 (cheap, high
first-impression value for strangers). Stages B and C are M5-G/M6-window
work, sized by Rehearsal 1 evidence per 0068's risk note — if instant cards
already land, B scopes down.

## 9. Accessibility & Device Floor

- WCAG AA contrast everywhere; 7:1 target for narrator display text.
- No hue-only encoding for game-critical states (§4).
- TV floor: 28px minimum rendered text at 1080p; verify at 720p too (older
  living-room TVs are the real install base).
- Phone floor: iOS Safari + Android Chrome, 360px width, thumb-reach primary
  actions; no hover-dependent affordances (phones don't hover).
- `prefers-reduced-motion` honored by every sequence (§6).
- Re-run the AW-230 real-device privacy matrix after Stage A (restyle must
  not weaken the private-vs-public visual distinction — it must strengthen
  it via the `--private` framing).

## Acceptance Criteria

1. All styling flows from `design/` tokens; no raw color/font/duration
   literals in components (grep-verifiable).
2. Both surface modes render the correct type scales; nothing below 28px on
   the display surface, 13px on phone.
3. The five named sequences exist, are the only users of `--t-dramatic`,
   and honor `prefers-reduced-motion`.
4. `seq-truth` meets the 0068 §2 B8 bar (story sequence, every player
   named, 90–150s) in a founder walkthrough.
5. `midnight` + two launch skins pass the §4 contrast/colorblind table;
   switching skins touches zero component code.
6. 98/98 existing nightcap-web tests remain green; typecheck clean.
7. AW-230 privacy matrix re-verified post-restyle.
8. Rehearsal/M6 observers can answer "did eyes go up at the right moments?"
   (0068 P5) — logged in the fun-observation rubric.

## Test Plan

- Automated: existing test suite + typecheck per Stage; add unit tests for
  the sequence utility (step ordering, reduced-motion collapse).
- Manual: TV-distance review checklist (3m, 1080p and 720p); phone device
  pass on iOS Safari + Android Chrome at 360px; contrast table per skin;
  privacy matrix re-run.
- Evidence: before/after screenshots of each screen committed with the
  Stage A PR; sequence capture videos with Stage B.

## Risks / Unknowns

- Display typeface licensing: OFL-only removes risk; any non-OFL theme face
  requires founder sign-off before inclusion.
- Choreography vs. SSE timing: sequences must tolerate events arriving
  mid-animation (queue and settle; never drop a story event because the
  stage was busy). Stage B design must include an event queue rule.
- Theme asset scope creep: a skin is 5 colors, 1 face, 1 texture, card
  framing. Portrait art and per-theme illustration are *slots*, filled only
  when the pre-produced asset pipeline (story bible §2) produces them.
- Solo-founder bandwidth: Stage A is days, not weeks; if it threatens the
  Rehearsal 1 date, Rehearsal 1 wins — the current UI is rehearsal-adequate.

## Open Questions

- Portrait/avatar treatment for the cast rail at launch: initials chip vs.
  themed silhouette set (cheap, pre-produced) — decide with the first skin PR.
- Does the host need a distinct "director view" style pass, or does the
  display surface style cover host controls at MVP? (Current host controls
  are minimal; revisit after Rehearsal 1 blocker log.)
