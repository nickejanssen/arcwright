# AW-276: Arc Voice Block Injection

**Milestone / Epic:** M5 / M5-I
**Size:** M
**Status:** Done (PR #231)

## Plain-English Summary

Inject the arc-declared voice directive into eligible generation prompts in a
stable, cacheable block without introducing game-specific engine vocabulary.

## Why This Matters

The six-beat Couch Race experience needs one consistent narrator and suspect
voice from the cold open through The Truth. Arc configuration already held the
voice, but live generation paths did not all consume it.

## Player Impact

Narrator and suspect language remains tonally coherent across the session.

## Business Value

Arc-declared voice is reusable across experiences and avoids repeated prompt
authoring at each generation call site.

## Technical Scope

- Render `tone_config.voice_directive` and scenario defaults as a `[VOICE]`
  block in the cacheable prompt region.
- Thread the block through direct dialogue, NPC exchange, live-loop dialogue,
  and narrator bridge paths.
- Source state is the resolved arc definition. The block does not choose state,
  audience, or case truth.
- Audience privacy and D-070 presentation hints remain responsibilities of the
  structured content event emitted by each caller.

## Human Collaboration Contract

**Interaction profile:** Independent execution.

**Rationale:** D-069 and approved implementation spec 0073 define the complete
contract, and PR #231 records passing implementation evidence. Reclassify
before any new subjective voice direction or prompt behavior is introduced.

**Founder input:** None unless a reclassification trigger occurs.

## Acceptance Criteria

- [x] The voice block renders from arc configuration and is absent when the arc
  omits usable voice content.
- [x] The block occupies the stable prompt region before per-turn content.
- [x] All eligible live generation paths receive the block.
- [x] Engine code contains no experience-specific voice content.

## Tests/Verification

- Evidence is recorded in `docs/specs/0073-aw-276-arc-voice-directive-injection.md`.
- PR #231 completed the named unit, integration, Ruff, engine, and API checks.

## Dependencies

- D-069
- `docs/specs/0073-aw-276-arc-voice-directive-injection.md`

## Must Not Do

- Do not put authored Nightcap lines in the engine.
- Do not bypass the routing, knowledge, or safety layers.
- Do not make the voice block responsible for canonical state.

## Architecture References

- `docs/architecture/03-arc-execution.md`
- `docs/architecture/06-model-routing.md`
- `docs/architecture/08-event-system.md`

## Playtest Relevance

Supplies the consistent voice layer consumed by the Couch Race narrative tasks.
