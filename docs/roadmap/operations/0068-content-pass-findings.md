# Content Pass Findings — 0068 §3 Standards vs. Current Generation Pipelines

> Current version: v1.0
> Last updated: 2026-07-14
> Status: Findings recorded; proposed actions await founder approval (prompt
> changes are a Hard Rules item)
> Canonical path: docs/roadmap/operations/0068-content-pass-findings.md
> Reviewed against: docs/specs/0068-game-experience-quality-bar.md §1–§4

Scope reviewed: `nightcap/arc.json` (tone, intent, narrator, beats, rails),
`engine/characters/dialogue.py` + `context.py` (dialogue prompt assembly),
`engine/narrator/bridge.py`, `engine/characters/service.py`,
`engine/session/service.py`, roadmap index for coverage.

## What is in good shape

- **G1 — Authorial intent is wired end-to-end.** `authorial_intent` (theme,
  tone, per-beat tension targets) is well-authored in `arc.json` and injected
  into the cacheable stable region of dialogue prompts (AW-270 / spec 0064
  pattern). The emotional progression matches the 0068 §2 moment map.
- **G2 — Knowledge constraint blocks are strong.** Known/not-known fact
  blocks with provenance, leak detection (`find_unknown_fact_leak`), and
  pressure/crumble blocks are exactly the platform wedge working as designed.
- **G3 — Tone system is well-designed as data.** `tone_config` (brand
  envelope ranges, scenario defaults, voice directive) is a thoughtful,
  game-agnostic structure with sensible Nightcap values.

## Findings

**F1 — HIGH: The voice directive is dead configuration.**
`tone_config.voice_directive` ("Wit-first ensemble mystery… mildly
unhinged"), `brand_envelope`, and `scenario_defaults` are parsed into arc
models (covered by `engine/tests/test_arc_models.py`) but consumed by
**zero generation call sites** — not dialogue, not the narrator bridge, not
mini-game content resolution. The entire Nightcap voice never reaches a
prompt. 0068 §3.3 (narrator voice) and §1 P2/P3 cannot be met while this is
true.
*Proposed action:* inject a `[VOICE]` block (voice directive + scenario
tone defaults) into the stable cacheable region of every player-facing
generation prompt, same placement pattern as the authorial-intent block.
Engine-neutral: the block renders whatever the arc declares.

**F2 — HIGH: No beat-level narrator generation pipeline exists.**
The narrator exists in `arc.json` (persona, behavior triggers:
beat_transition, clue_release, tension_threshold, player_inaction) but the
only narrator generation in the engine is the resume bridge (AW-221).
AW-227 renders narrator events; nothing generates them at beat transitions.
The narrator is the product's voice (0068 §3.3) and beats B2/B8 bars depend
on it. No open roadmap task covers this.
*Proposed action:* verify behavior at the next synthetic dry run (what text
actually reaches the shared display at beat turns), then scope a
narrator-dialogue generation task into M5 if confirmed absent.

**F3 — MEDIUM: Character identity prompts are data-shaped, not
voice-shaped.** The dialogue identity block renders personality, goals,
secrets, and tells as raw JSON with no style guidance (no speak-as-a-person
directive, no wit register). Adequate for knowledge enforcement; weak for
the §3.1 read-aloud bar. Additionally, no cast/identity-card *generation*
module was found (`characters: []` with `character_generation: true`), and
no roadmap task covers it — the player-facing identity card content path is
unverified.
*Proposed action:* confirm at the synthetic dry run what identity content
players actually receive at session start; measure against the §3.1
five-part format and three tests; scope accordingly.

**F4 — MEDIUM: Clue content generation has no located prompt path.**
`generative_elements.clue_content: true`, and AW-251 gates clue *access*
via mini-games, but no clue-content prompt assembly was found. §3.2
(point/sayable/world standards) has no implementation surface to review
yet.
*Proposed action:* same verification path as F2/F3 at the dry run.

## Recommended sequence

1. Run the synthetic dry run (`make rehearsal` + AW-255 loop) and capture
   what text actually renders at: session start (identity), beat turns
   (narrator), clue release. This turns F2–F4 from "not found" into
   verified facts in one session. No approval needed.
2. Founder approves the F1 `[VOICE]` block change (Hard Rules: prompt
   change). Implement with unit tests asserting the block renders from arc
   config and sits in the stable prompt region.
3. Scope any confirmed F2–F4 gaps as numbered M5 tasks (next free AW
   numbers; no reuse) before Rehearsal 1 if narrator beat lines are absent,
   otherwise before Rehearsal 2.

## Non-actions

- No prompt edits were made in this pass (Hard Rules).
- `arc.json` was not modified; its content quality is not the bottleneck —
  the bottleneck is config-to-prompt plumbing (F1) and pipeline existence
  (F2–F4).
