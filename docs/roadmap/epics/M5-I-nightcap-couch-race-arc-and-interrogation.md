# M5-I: Nightcap Couch Race Arc And Interrogation Layer

**Milestone:** M5
**Status:** Planned

## Plain-English Summary

Build the Couch Race v1 experience per ADR-0013: a new six-beat competitive-investigator arc, the shared interrogation capability (menu-driven question intents, knowledge-gated AI suspect answers, claim ledger, deterministic contradiction detection), race scoring and accusation state, TV and phone rendering, and the retargeted Rehearsal 1 thin slice.

## Why This Matters

D-071 makes Couch Race the Nightcap v1 launch target. This epic is the path from the current pre-Rehearsal-1 platform state to a rehearsable Couch Race session. The interrogation capability it builds is shared platform infrastructure with Daily Case (M5-C lineage), so this epic also advances the D-034 wedge.

## Player Impact

Players get a 20–40 minute living-room mystery race with zero role burden: watch the TV, grill AI suspects, catch lies, accuse first. Floor drops to two players.

## Business Value

Faster founder test loop (multiple cases per evening), broader addressable audience, lower per-session cost against the M5 gross-margin gate, and a differentiated market lane (infinite coherent mysteries with knowledge-state-constrained suspects).

## Technical Scope

The technical scope is limited to the tasks listed below and the architecture references named in those task files.

## Tasks

- [AW-281: Couch Race Arc Definition And Case Generation](../tasks/AW-281-couch-race-arc-definition-and-case-generation.md)
- [AW-282: Interrogation Round Loop And Question Intents](../tasks/AW-282-interrogation-round-loop-and-question-intents.md)
- [AW-283: Suspect Answer Generation And Contradiction Detection](../tasks/AW-283-suspect-answer-generation-and-contradiction-detection.md)
- [AW-284: Race Scoring And Accusation State](../tasks/AW-284-race-scoring-and-accusation-state.md)
- [AW-285: Couch Race TV And Phone Rendering](../tasks/AW-285-couch-race-tv-and-phone-rendering.md)
- [AW-286: Couch Race Rehearsal Slice And Rehearsal 1 Retarget](../tasks/AW-286-couch-race-rehearsal-slice-and-rehearsal-1-retarget.md)
- [AW-288: Couch Race Mini-Game Beat Coverage And Tell Me Something True Acceleration](../tasks/AW-288-couch-race-mini-game-beat-coverage-and-tmst-acceleration.md)
- [AW-289: Couch Race Trivia Mini-Game](../tasks/AW-289-couch-race-trivia-mini-game.md)
- [AW-290: Narrator Slot Schema — Structured Location/Time And Wrapper Dressing Pack](../tasks/AW-290-narrator-slot-schema-and-wrapper-dressing.md)
- [AW-291: Narrator Refrain Resolver](../tasks/AW-291-narrator-refrain-resolver.md)
- [AW-292: Quote-Suspects Interrogation Mechanic](../tasks/AW-292-quote-suspects-interrogation-mechanic.md) — gated on paper-test validation (D-091)

## Supporting Rehearsal 1 Dependencies

AW-281 through AW-286 remain this epic's child tasks. The following D-069
narrative tasks are supporting dependencies retargeted to the six-beat Couch
Race experience by AW-286:

- [AW-276: Arc Voice Block Injection](../tasks/AW-276-arc-voice-block-injection.md)
- [AW-277: Couch Race Narrator Transition Lines](../tasks/AW-277-couch-race-narrator-transition-lines.md)
- [AW-278: Couch Race Truth Sequence And Reveal Accounting](../tasks/AW-278-couch-race-truth-sequence-and-reveal-accounting.md)
- [AW-279: Detective Identity And Opening Briefing](../tasks/AW-279-detective-identity-and-opening-briefing.md)
- [AW-280: Couch Race Clue Release Content](../tasks/AW-280-couch-race-clue-release-content.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- A headless harness run completes a full six-beat Couch Race session with 2 and with 8 synthetic players.
- Suspect answers never leak facts outside the suspect's knowledge state (existing mandatory pre-generation constraint).
- The founder can run a real-device Couch Race thin slice under D-065 local-tunnel deployment.

## Tests/Verification

- Verify every child task is complete and has evidence linked from its task issue.
- Verify the AW-272 continuity/coherence eval suite runs against a Couch Race synthetic batch and reports knowledge-leak rate and contradiction-detection correctness.
- Verify per-session cost telemetry captures interrogation generation spend.

## Dependencies

- ADR-0013 / D-071 (this epic's charter)
- PR #225 lineage: live-loop AI character dialogue (spec 0071), a direct dependency for suspect answers
- D-069 narrative tasks AW-276–AW-280, aligned to the six-beat arc
- Mini-game packages from D-062/D-064 (Crime Scene Smash, Evidence Locker)
  slot in unchanged; D-079 adds Tell Me Something True (AW-288) and a new
  Trivia package (AW-289) ahead of Rehearsal 1, amending D-064's original
  two-rehearsal split

## Must Not Do

- Do not let AI decide or mutate case truth; killer, motive, method, clue web, and authorized lies resolve deterministically at session start.
- Do not name the interrogation capability or its schemas after Nightcap; it is platform infrastructure shared with Daily Case (platform-clean naming per D-038/D-039).
- Do not build free-text question input in v1 (open question; menu intents only).
- Do not implement the teams or co-op competition modes (dial positions are deferred pending approved specs).
- Do not bypass Arcwright architecture principles in `AGENTS.md`.

## Architecture References

- `docs/story-bibles/nightcap-couch-race.md`
- `docs/decisions/0013-nightcap-couch-race-v1-launch-target.md`
- `docs/specs/0072-nightcap-couch-race-v1.md`
- `docs/architecture/03-arc-execution.md`, `docs/architecture/07-character-behavior.md`
- `docs/prd/03-scope.md` (amended MVP definition)
