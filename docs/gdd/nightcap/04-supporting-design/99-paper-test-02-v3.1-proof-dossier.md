---
id: nightcap.gdd.nightcap.04-supporting-design.99-paper-test-02-v3.1-proof-dossier
namespace: nightcap
title: Nightcap Paper Test 2 v3.1 Proof Dossier
owner: Nico Janssen
status: active
review_by: "2027-04-01"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Paper Test 2 v3.1 Proof Dossier

**Status:** Task 2 analysis and Task 4 editorial audit, 2026-10-02. Founder causal sufficiency and full-case review pending.

`essential_truths.routes` describe causal explanations. `case_file.proof_groups` define what the current four/five fact scorer accepts. They differ. Automated reachability cannot establish that a selection fairly proves a murder.

## Discovery map before proof edits

| Encounter          | Granted facts                                                        | Cost                              |
| ------------------ | -------------------------------------------------------------------- | --------------------------------- |
| Writing Room       | `e-bookend`, `e-gideon-final-note`                                   | One major action                  |
| Gideon's Things    | `e-cylinder-index`, `e-cylinder-transcript`, `e-clara-access`        | One major action                  |
| Seance Room        | `e-service-route`, `e-quill-cue-sheet`                               | One major action                  |
| Clara              | `e-clara-lie`, `e-clara-transcribed-43`                              | One major action                  |
| Quill              | `e-quill-denial`                                                     | One major action                  |
| Rusk               | `e-rusk-denial`                                                      | One major action                  |
| Beatrice           | `e-beatrice-threat`, `e-beatrice-letters`                            | One major action                  |
| Quill challenge    | `e-quill-admission`                                                  | Free after an owned prompt fact   |
| Rusk challenge     | `e-rusk-found-cylinder`, `e-rusk-sighting`                           | Free after an owned prompt fact   |
| Beatrice challenge | `e-beatrice-impact`, `e-beatrice-sighting`, `e-clara-visible-seance` | Free after an owned prompt fact   |
| Clara follow-up    | `e-clara-evasion`                                                    | One Leverage                      |
| Quill follow-up    | `e-quill-payment`                                                    | One Leverage                      |
| Rusk follow-up     | `e-clara-quill-connection`                                           | One Leverage                      |
| Beatrice follow-up | `e-private-detail-match`                                             | One Leverage                      |
| Locked Box         | `e-cylinder-43`                                                      | Win, Listen In, or public release |

Both descriptive `t3-leak-motive` routes require `e-quill-payment` and `e-private-detail-match`. These are two separate paid follow-ups, so neither route can be acquired with the single initial Leverage. The scorer instead accepts `e-beatrice-impact` alone, `e-private-detail-match` alone, or `e-quill-payment` paired with either `e-gideon-final-note` or `e-clara-access`. These are compressed inferences: no one group directly establishes both Clara's leak and Gideon's discovery of it.

The false voice scorer accepts the transcript or cylinder alone, requiring the player to connect an earlier recording to the heard voice. Chronology accepts a witness account paired with recording evidence. Staging accepts chronology, Clara's access and the service route, or her lie with the Rusk follow-up, transcript and final note. The Rusk groups establish opportunity but contain no direct homicide observation. Founder review must decide whether their causal inference is sufficient or whether an authored correction is needed. Do not add Leverage, change the fixed timeline, or loosen proof groups simply to make a route pass.

## Scorer enumeration before acquisition constraints

Across 15 proof-relevant IDs, the current scorer accepts three four-fact sets and 38 five-fact sets. The four-fact sets are:

1. `e-beatrice-impact`, `e-clara-lie`, `e-clara-quill-connection`, `e-cylinder-transcript`.
2. `e-beatrice-impact`, `e-clara-transcribed-43`, `e-cylinder-43`, `e-service-route`.
3. `e-beatrice-impact`, `e-clara-transcribed-43`, `e-cylinder-transcript`, `e-service-route`.

This enumeration checks scorer logic only. Some five-fact sets contain two distinct Follow the Thread rewards and cannot be earned in one run. Legal transition tests and counterexamples belong below after implementation.

Of the 38 accepted five-fact sets, 32 contain one of the accepted four-fact sets. The six additional subset-minimal five-fact sets are:

| Facts                                                                                             | Acquisition status                                                                          |
| ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Beatrice sighting, Clara lie, Clara-Quill connection, cylinder transcript, private detail match   | Unreachable: Rusk and Beatrice follow-ups both cost Leverage                                |
| Beatrice sighting, Clara transcribed 43, cylinder 43, private detail match, service route         | Reachable with Beatrice's paid follow-up and public cylinder release                        |
| Beatrice sighting, Clara transcribed 43, cylinder transcript, private detail match, service route | Reachable with Beatrice's paid follow-up                                                    |
| Clara lie, Clara-Quill connection, cylinder transcript, private detail match, Rusk sighting       | Unreachable: Rusk and Beatrice follow-ups both cost Leverage                                |
| Clara transcribed 43, cylinder 43, private detail match, Rusk sighting, service route             | Reachable with Rusk's free challenge, Beatrice's paid follow-up and public cylinder release |
| Clara transcribed 43, cylinder transcript, private detail match, Rusk sighting, service route     | Reachable with Rusk's free challenge and Beatrice's paid follow-up                          |

The three accepted four-fact sets are legally reachable. The first uses Rusk's paid follow-up and Beatrice's free challenge. The other two use Beatrice's free challenge. All require five major actions before entering Last Call, even if the selected evidence was earned earlier. The cylinder version remains available after a lock loss through public release.

## Legal paths and counterexamples

`proof-paths.test.mjs` uses the same `visitInvestigation`, `challengeClaim`, `followThread`, lock, and Last Call transitions as the app. It establishes a Beatrice confrontation four-fact route, a five-fact Rusk chronology route without Beatrice confrontation testimony, a rival lock win followed by public cylinder release, and a Quill-first red herring route. No test assigns `majorActions` or injects a discovery to establish legal reachability. The scorer rejects culprit-only guessing and unowned facts. One Leverage cannot acquire both paid motive rewards.

These are **automated reachability** findings. They do not certify that the current compressed t3 and t4 groups make a fair, causally sufficient murder case. The founder must review whether the Rusk route's opportunity evidence is enough, and whether a payment or private detail match plus the other selected facts supports Gideon's discovery of the leak. If not, an authored correction to encounters and proof groups is needed in a separate approved artifact pass. Narrative sufficiency remains pending.

## Task 4 delivered-continuity audit

| Link                                | Earliest player-visible source                                                                                                                                                                    | Limit of what it establishes                                                                                                                                                     |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Recording identity                  | Gideon's Things shows the gap at 43, the transcript sentence, and Clara's initials. The Locked Box yields cylinder 43 privately or publicly.                                                      | The transcript and cylinder support a recorded voice. The player must connect the earlier recording to the later voice.                                                          |
| Physical voice route                | Séance Room shows the trumpet coupling and service wall; Quill's earned challenge admits the concealed tube and cabinet.                                                                          | The apparatus can carry a voice. Seeing the route does not identify who placed the cylinder.                                                                                     |
| Access and substitution opportunity | Gideon's Things shows Clara handled the transcript. Rusk's earned follow-up says she used the service corridor; Beatrice or Rusk can place her leaving the writing-room passage before the voice. | No witness sees Clara insert the cylinder. Staging remains an inference from access, timing and the false alibi.                                                                 |
| Time of death                       | Beatrice's earned challenge separates what she heard from the impact she did not see, then places Clara at the séance voice. Rusk's challenge provides a separate pre-voice sighting.             | Neither witness saw the fatal blow. Their accounts must be weighed against the recording evidence and Clara's claim.                                                             |
| Leak and exposure                   | Gideon's final note names Quill then Hensley. Quill's paid follow-up can show Clara's payments; Beatrice's paid follow-up can compare her letters with Gideon's private detail.                   | The descriptive motive routes require both paid rewards and remain unreachable with one Leverage. The scorer's compressed alternatives still require founder sufficiency review. |
| Concealment                         | Rusk's challenge says he put Gideon's cylinder in the strongbox after Quill's cue. The Locked Box reveals its contents.                                                                           | Rusk hid evidence of the fraud. His testimony gives him no knowledge of who killed Gideon.                                                                                       |

The editorial pass preserved all discovery IDs, the ten fixed timeline entries, the cast and the culprit. It adds no definitive case fact beyond the approved invitation framing. The opening, Beatrice's pressured account and the reveal received a deliberate line-by-line read for rhythm, hearing versus sight, and clue clarity. This is author judgment, not observed player response. The Beatrice encounter now explicitly states that Clara was seated when Gideon's voice sounded, matching the fact it grants. Public hooks use visible behavior or already public stakes, and challenge buttons ask about known speech or actions without naming a conclusion.
