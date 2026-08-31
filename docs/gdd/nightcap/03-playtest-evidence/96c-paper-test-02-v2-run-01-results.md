# Nightcap — Paper Test #2 v2 Run 01 Results

**Status:** TEST FINDING / supporting evidence, not canon  
**Fixture:** The Room With No Door  
**Treatment:** game-first baseline / no memory-support comparison yet  
**Participants:** 1 real participant  
**Environment:** Chat exploratory gate  
**Gate decision:** **REVISE AND RERUN**

## Limits

This run does not validate multiplayer play, social competition, living-room timing, memory-support effectiveness, or final Nightcap UX. Absolute timing is contaminated by chat/UI latency.

## Observed telemetry

- First meaningful choice: 141s
- Actions: Service Corridor → Wet Footprints → Bookcase
- Interruption ended: 179s
- Final commitment: 196s
- Post-interruption commitment interval: 17s
- Prime suspect: Not enough yet
- Next desired thread: Guest statements
- Most useful discovery: Bookcase

## Player report

- Compared with v1: **Better**
- Felt like investigating: **A little**
- Wanted another action: **Maybe**
- Most interesting/fun: **More options to explore**
- Still boring/confusing/interface-like: **Bolded text seemed obvious**
- Wanted to do next: **Interview people**

## Test findings

### Supported

- Removing mid-play research questions materially improved the experience relative to v1.
- Player-directed exploration is more promising than forced reflection.
- The player formed a coherent investigative trajectory without being required to explain it.
- The player ended with an unresolved question and a desired next investigative verb (interview people).

### Not yet supported

- Baseline has not yet reached the detective-feel / time-to-fun gate.
- Player desire to continue is not yet strong enough.
- Memory Support A/B comparison should not begin yet.

## Prototype failure modes

1. **Over-signposting:** emphasized/bolded clue presentation made significance feel preselected by the interface.
2. **Under-exploration:** three actions were insufficient before forcing an interruption/commitment.
3. **Thin verb diversity:** the player wanted direct interviewing, suggesting the slice did not expose enough investigator verbs early enough.
4. **Interface residue:** discoveries still arrived as explicit information cards rather than sufficiently diegetic investigation outcomes.

## Recommendation

Revise the baseline before touching the GDD:

- reduce significance formatting; bold labels/titles, not clue conclusions,
- allow more investigation before the interruption,
- expose guest interviews as a first-class action from the beginning,
- increase verb diversity without adding rules,
- remove explanatory “What you know” summaries,
- make discoveries concrete observations and statements rather than interface-authored interpretations,
- keep lightweight commitment after enough exploration to support a real theory.

No Nightcap design decision changes from this run.
