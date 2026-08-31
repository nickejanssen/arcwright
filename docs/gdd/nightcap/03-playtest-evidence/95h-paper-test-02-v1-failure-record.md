# Nightcap — Paper Test #2 v1 Failure Record

**Status:** TEST FINDING / supporting evidence, not canon  
**Date:** 2026-08-26  
**Run:** Single real participant, chat-based exploratory execution  
**Fixture:** The Bellweather Toast  
**Treatment:** A — Basic History

## Finding

**Paper Test #2 v1 failed as a test instrument before it could validly test Memory Support.**

This is **not** evidence that Nightcap's core game is boring or that the approved memory-support direction is wrong. It is evidence that the v1 paper-test implementation represented Nightcap poorly and contaminated the behaviors it intended to measure.

## Verified Observations

- First meaningful choice was recorded at 117 seconds, but the absolute timing is contaminated by chat/app latency and typing.
- The prototype asked the participant to explain reasoning during play.
- The participant had little opportunity to investigate before being asked to reflect on the investigation.
- The prototype changed/removed action state in a way the participant found confusing after the interruption.
- The fixture did not originally specify exact lead-to-card sequencing; an explicit non-canon execution patch was required mid-run.
- Multiplayer/social behavior could not be observed in a single-participant chat execution.

## Player Reports

The participant described the experience as:

- "boring and confusing",
- like "writing essays for highschool",
- mixed with a "choose your own adventure text game",
- not detective-like,
- interface-heavy,
- too limited in actual exploration,
- overly signposted around Mara / the master key,
- confusing after the interruption.

The participant said they would not recommend pressing Start based on this prototype experience.

## Design Inferences

1. **The test interrupted play to ask about play.** Mid-play reflection prompts converted player behavior into research-task behavior.
2. **The test stripped out too much Nightcap.** `text → menu → text → essay` did not adequately represent cinematic investigation, discovery, deduction, or social competition.
3. **The fixture telegraphed its intended seam.** The setup made the master-key line disproportionately salient.
4. **There was insufficient exploration for a meaningful memory-support test.** Memory load was not allowed to develop naturally.
5. **The interruption measured interface discontinuity more than re-entry.**

## What This Run Does NOT Establish

This run does not establish that:

- Nightcap's core loop is boring,
- baseline memory support is useful or harmful,
- transcripts should be removed,
- the approved Difficulty + Accessibility laws are wrong,
- two-player Nightcap succeeds or fails,
- the intended cinematic/social experience succeeds or fails.

## Decision

**Paper Test #2 v1: FAILED AS TEST INSTRUMENT.**

**Time-to-Fun hypothesis:** NOT VALIDATED.  
**Memory Support hypothesis:** NOT TESTED.  
**Existing GDD decisions:** UNCHANGED.

## Approved Correction

Replace v1 with a **game-first observational microcase**:

- no mid-play essay/reflection questions,
- more actual investigation before any debrief,
- silent observation during play,
- short debrief only after the playable slice,
- first validate that the slice feels like a game,
- only then compare memory-support treatments.
