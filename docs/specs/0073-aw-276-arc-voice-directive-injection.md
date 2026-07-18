# AW-276: Arc Voice Directive Injection ([VOICE] Block)

**Status**: Approved (implementation complete, PR #231)

**Author**: Engine session, 2026-07-16 | **Date**: 2026-07-16

---

# References

- Product decision: D-069 in `docs/product/decisions-log.csv` (authorizes
  the prompt work; this spec is the implementation contract D-069 refers
  to and does not replace)
- Design source: `docs/roadmap/operations/0068-content-pass-findings.md`,
  finding F1: `tone_config.voice_directive` was parsed and validated but
  consumed by zero generation call sites
- Quality bar: `docs/specs/0068-game-experience-quality-bar.md` §3.3
  (narrator voice)
- Related specs: `docs/specs/0064-aw-270-authorial-intent-block.md` (the
  `[AUTHORIAL INTENT]` block this spec's `[VOICE]` block is modeled after
  and sits alongside), `docs/specs/0071-live-loop-ai-character-dialogue.md`
  (spec 0071/PR #225 introduced a third generation call site this spec
  must also cover)
- GitHub issue: #226 (AW-276)
- PR: #231

---

# Overview

The arc's declared voice (`tone_config.voice_directive` and
`scenario_defaults`) must reach every live character-dialogue and
narrator-bridge generation prompt, in the cacheable stable region, the same
way `authorial_intent` already does. This spec is the durable record of
that contract: which call sites are in scope, where the block sits in the
prompt, and how "reaches every live call site" is verified: not just
asserted.

---

# In Scope

- `format_voice_block(tone_config)` in `engine/characters/dialogue.py`:
  renders `voice_directive` + `scenario_defaults` as a `[VOICE]` block;
  returns `None` when the arc declares no usable voice content.
- Injection into `build_dialogue_messages` / `generate_character_dialogue`
  (direct dialogue), `build_npc_npc_messages` / `generate_npc_npc_exchange`
  (NPC-NPC exchange), and `generate_narrator_bridge` (resume flow):
  stable region, after identity, before knowledge/authorial-intent blocks.
- Threading `tone_config` through every live dispatch path that reaches
  those functions:
  - `schedule_initiative_tasks` → `_run_initiative_action` →
    `generate_character_dialogue` (direct/player-group speech) and
    `generate_npc_npc_exchange` (NPC-NPC).
  - `CharacterService.generate_ai_responses` (spec 0071's live-loop path,
    `engine/characters/service.py`) → `generate_character_dialogue`.
- Engine-neutral implementation: no game-specific strings in engine code;
  the block renders whatever any arc's `tone_config` declares.

---

# Out of Scope

- A `generate()`-level chokepoint for `tone_config` (the pattern PR #232
  established for `content_rails` via `arc_id`). Each caller currently
  passes `tone_config` explicitly, mirroring how `authorial_intent` is
  passed today. Centralizing both is a candidate follow-up once a third
  arc-derived block needs the same treatment: not required for this spec.
- Any change to `authorial_intent` threading or the L1/L2/L3 safety
  pipeline.
- Voice content for clue generation or identity-card generation (AW-279,
  AW-280: those tasks consume this block once their own pipelines exist).

---

# Human Collaboration Contract

**Interaction profile:** Independent execution.

This spec, D-069, and the existing arc-authority boundary fully constrain voice
directive injection. After normal plan approval, the agent may execute and must
explain the directive path, precedence, and verification evidence clearly.

Stop and reclassify to Creative collaboration or Decision interview before
authoring new voice direction, changing prompt precedence, widening schema or
telemetry scope, or altering authority boundaries. Record plan approval, tests,
dates, and owner actions.

# Acceptance Criteria

- [x] `format_voice_block` renders from `nightcap/arc.json` tone_config and
  returns `None` for absent/empty tone_config (`engine/tests/test_voice_block.py`).
- [x] `[VOICE]` sits before knowledge/authorial-intent blocks in the
  dialogue system prompt (stable-region ordering test).
- [x] `generate_narrator_bridge` injects `[VOICE]` ahead of its task
  instruction when `arc_id` resolves a registered arc
  (`engine/tests/test_narrator_bridge.py::test_arc_id_injects_voice_block`).
- [x] `build_npc_npc_messages` includes `[VOICE]` when `tone_config` is
  passed, in the stable region before knowledge blocks
  (`engine/tests/test_initiative.py`).
- [x] `schedule_initiative_tasks` threads `tone_config` to both dispatch
  branches: NPC-NPC and direct/player-group: proven at the scheduler
  entry point, not just at the leaf function
  (`test_schedule_initiative_tasks_threads_tone_config_into_npc_exchange`,
  `test_schedule_initiative_tasks_threads_tone_config_into_player_group_dialogue`).
- [x] `CharacterService.generate_ai_responses` (spec 0071's live-loop path)
  passes `arc_definition.tone_config` and an end-to-end assertion proves a
  bus-triggered AI response's prompt contains `[VOICE]`
  (`test_dialogue_input_generates_one_knowledge_constrained_response`).
- [x] Full engine + api suite green; ruff check and format clean.

---

# Test Plan

Every acceptance criterion above is a named, passing test: not review by
inspection. The verification standard for "reaches a live call site" is:
patch at the `litellm.acompletion` or `engine.characters.*.generate`
boundary, capture the actual `messages` payload sent, and assert `[VOICE]`
and the arc's real voice directive text are present. Manual review alone
was insufficient for this feature: an earlier pass wired the block into
`build_dialogue_messages` and its tests but left three real dispatch paths
(initiative scheduler, NPC-NPC exchange, live-loop `CharacterService`)
unverified, which founder review (PR #231) and Codex review both caught.

---

# Risks and Unknowns

**Risks**:
- A future fourth generation call site could repeat this gap. Mitigated
  short-term by this spec's explicit call-site list; the Out of Scope note
  above names the chokepoint pattern as the durable fix if a fourth site
  appears.

**Unknowns**:
- None outstanding; all acceptance criteria are implemented and verified
  as of PR #231.

---

# Open Questions

- Should `tone_config` gain a `generate()`-level chokepoint like
  `content_rails` (PR #232) to make this class of gap structurally
  impossible rather than convention-enforced? Deferred: see Out of Scope.
