---
id: nightcap.gdd.nightcap.04-supporting-design.99-paper-test-02-v3.0-improvement-review
namespace: nightcap
title: Nightcap Paper Test 2 v3.0 Improvement Review
owner: Nico Janssen
status: active
review_by: "2027-04-01"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Nightcap Paper Test 2 v3.0 Improvement Review

**Design status:** RECOMMENDATION, awaiting selection of implementation scope.  
**Version:** 1.0  
**Reviewed:** 2026-10-01  
**Source snapshot:** `b3526d0cc250cd3c5ad0f3eadde05bcc6cf49368` on `claude/phase-1-v3-send-readiness`.  
**Canonical path for this review:** `docs/gdd/nightcap/04-supporting-design/99-paper-test-02-v3.0-improvement-review.md`.

The founder authorized writing this review. Its recommendations are not approved changes to the GDD, fixture, instrument, or analysis thresholds. This document is an additional review artifact beyond the original Phase 1 file map. The approved Phase 1 phone survey/reveal smoke gate remains open.

## 1. Spoiler-free conclusion

The fixture includes a real four-pin timing minigame, an authored mystery, several investigation routes, a finite Leverage choice, and deterministic Case File evaluation. It is useful for a bounded test of detective agency and cohesion. It does not yet establish the quality or fun of the complete Nightcap experience.

The earlier Task 1 record reports 14 passing situations and two accepted gaps. That establishes specific functional coverage. This review adds source-level GDD and editorial scrutiny; it does not replace human play or rerun that QA.

The most valuable improvements are:

1. Make every notebook fact something the player actually encountered in a scene.
2. Preserve earned dialogue and explain investigation costs and remaining opportunities.
3. Teach the lock before its clock starts and make its actual competitive deadline legible.
4. Make Leverage spending, saving, and resulting information clear to the player and research analysis.
5. Give characters distinct voices and let players do more of the connecting themselves.
6. Give an honest, useful verdict, including when a returning browser has lost its run state.

These changes concern the quality of the sampled game experience. They do not justify building multiplayer infrastructure, production cinematics, a general Case Board, or a larger minigame library into this fixture.

**Quality judgment:** the premise and interlocking secrets are promising; the prose has atmosphere and wit. Some scenes compress discovery into summaries, and several speakers share a similar polished, quippy cadence. Those are editorial judgments, not objective ratings. Beauty and fun require founder taste and player response. GDD conformity alone proves neither.

## 2. Scope, evidence, and classification

### Evidence boundary

- Fixture: `nightcap-paper-test-02-v3.0`, version `3.0`; Jotform instrument version `2.2`, form `262397917027062`.
- Sources: current branch code, authored case, canonical GDD, retained Host guidance, existing QA, v2.2 baseline, and approved v3.0 analysis plan.
- No fresh Jotform submissions were fetched for this review. The historical baseline contains three v2.2 responses; it is not evidence of v3.0 fun.
- No new browser playthrough, accessibility session, or automated gameplay test was run for this review. Findings marked confirmed refer to source behavior, not newly observed player outcomes.
- Catalog validation ran on 2026-10-01: `python scripts/playtest_tool.py --json validate` returned `ok: true`, with no errors. This validates metadata, not the live survey redirect or game quality.
- No tester identities, raw exports, or verbatim tester comments are included.

### How to distinguish game feedback from framework feedback

| Class | Decision rule | Typical response |
|---|---|---|
| Game | The issue would remain with an ideal interface and real players. | Change authored story, meaningful choices, rules, or pacing after design approval. |
| Fidelity | The fixture omits or distorts something needed to experience the intended game. | Add the smallest representation needed for a valid test. |
| Harness | Controls, state, handoff, or measurement misrepresent the player's actions. | Correct the defect or measurement limitation without adding game scope. |
| Deferred | Valuable production work outside this test's question. | Record for its owning GDD/system work; do not build it to polish this fixture. |

A single comment may have two causes. For example, "I forgot what she said" may reflect missing transcript access and unclear dialogue. Preserve the player's words privately, record the encounter and intended action, then distinguish observed friction from the proposed cause. Do not automatically dismiss negative feedback as a prototype limitation.

### Labels

- **Confirmed:** directly visible in the inspected source or existing record.
- **Editorial:** a reasoned creative assessment requiring human judgment.
- **Needs observation:** a plausible risk whose practical effect has not been demonstrated.
- **P1:** resolve or explicitly account for before interpreting the affected research result. This is not a claim that every item must be implemented before the current smoke run.
- **P2:** candidate for a narrowly scoped successor, selected for expected learning value.
- **Later:** production or subsequent research scope.

## 3. GDD representation

| GDD expectation | v3.0 representation | Limit on the conclusion |
|---|---|---|
| Bounded-open detective investigation | Multiple locations and interviews, conditional testimony, finite moves | Choice exists; experienced agency and fairness still need human evidence. |
| Observations before player interpretation | Authored scenes and factual notebook | Some facts appear only in the notebook; some prompts supply the comparison. See 07 and 11. |
| Baseline memory and provenance | Facts with source labels | Full earned transcript, living suspect history, and optional notes are absent. Final Case Board UX is explicitly excluded. |
| Story-connected competitive pulse | Locked Box timing race and temporary first look | Real minigame, but deterministic rival scaffolding cannot establish social competition or production picker support. |
| Bounded information advantage | One test-granted Leverage and two contextual effects | Useful decision sample; production earning, economy, and multiplayer balance remain untested. |
| Fair Last Call and authored evaluation | Five-action entry, six-action UI cap, culprit plus four/five facts | A selected-fact proxy does not establish production Structured Reconstruction quality or shared countdown pressure. |
| Truth, Verdict, Postmortem | Written truth and binary verdict | Cinematic payoff and final Postmortem are outside fixture scope. Survey occurs before truth. |
| Cinematic, social, characterful mystery | Text atmosphere, authored suspect dialogue, scripted rival | No claim of full Vesper performance, multiplayer chemistry, shared-screen staging, or final audiovisual quality. |
| Deterministic truth and human authorship | Authored case and deterministic local evaluator | Appropriate research scaffold; browser runtime is not evidence of production Arcwright implementation. |

Sources: GDD [investigation](../01-authoritative-gdd/02-investigation-deduction.md), [memory](../01-authoritative-gdd/03-case-board-memory.md), [competitive pulse](../01-authoritative-gdd/04-minigame-competitive-pulse.md), [Last Call](../01-authoritative-gdd/05-last-call-case-file.md), [reactivity](../01-authoritative-gdd/06-story-reactivity-reentry.md), [Leverage](../01-authoritative-gdd/07-espionage-leverage-update.md), [endgame](../01-authoritative-gdd/08-truth-verdict-postmortem.md), [accessibility](../01-authoritative-gdd/10-difficulty-accessibility.md), [runtime boundary](../01-authoritative-gdd/11-arcwright-runtime-boundary.md), and [experience boundaries](../01-authoritative-gdd/12-experience-world-content-boundaries.md). Explicit fixture exclusions are in the [fixture README](../../../../playtests/nightcap-paper-test-02-v3.0/README.md).

## 4. Comprehensive improvement list

**SPOILERS BELOW: identities, evidence, and the solution are discussed. Read after a first unspoiled play if you want to preserve that experience.**

Source shorthand throughout this section:

- **APP:** [app.js](../../../../playtests/nightcap-paper-test-02-v3.0/app.js).
- **RUN:** [runtime.js](../../../../playtests/nightcap-paper-test-02-v3.0/runtime.js).
- **CASE:** [case.json](../../../../playtests/nightcap-paper-test-02-v3.0/case.json).
- **ANALYSIS:** [approved analysis plan](../02-validation/99-paper-test-02-v3.0-analysis-plan.md).
- **QA:** [pre-send QA evidence](../03-playtest-evidence/99-paper-test-02-v3.0-pre-send-qa.md).

Function names and case identifiers anchor findings to the snapshot above. Acceptance criteria below describe proposed future work, not completed fixes.

### A. Research validity

#### 01. Distinguish explicit saving from an unused Leverage balance

**P1 | Harness | Confirmed.** ANALYSIS H4 requires a `leverage_choice`. APP `renderLockResult` provides explicit save only on the rival-win branch. A human can win, retain Leverage throughout, and emit no such event. QA Run A records that legitimate path. The metric therefore measures recorded interaction, not every decision to conserve the resource.

**Smallest improvement:** report spend, explicit save, and unused-at-completion separately using the existing event sequence. An unused balance alone cannot establish intentional saving. Obtain a brief human explanation if intent matters. Propose any change to the approved H4 gate separately; do not silently reinterpret it.

**Acceptance:** the three states are distinguishable in analysis; human-win/no-spend is not described as proven confusion or proven intentional saving; any revised gate has dated founder approval before research interpretation.

#### 02. Avoid treating an inference button press as proof of deduction

**P1 | Harness / Fidelity | Confirmed limitation.** APP `challengeInterview` and `followThread` emit `inference_action`; some CASE prompts explicitly tell the player what to compare. ANALYSIS H3 counts the event. It demonstrates taking the action, not independently recognizing its implication.

**Smallest improvement:** keep the approved count and label it accurately. Use existing qualitative feedback as corroboration, and propose a short neutral debrief such as "What made you change your theory?" for a future approved protocol. Do not coach during play.

**Acceptance:** reports distinguish action uptake from player-owned inference; no claim of successful independent deduction rests solely on the event. A new research prompt is approved before use.

#### 03. Prevent missing data and small samples from creating apparent success

**P1 | Harness | Confirmed analysis risk.** H1's maximum first-target share can look diverse when targets are missing: four identical targets among eight included players would appear as 50% despite no observed diversity. H4's median can likewise describe only a small measured subset. ANALYSIS says missingness cannot count toward meeting a threshold but needs an explicit computation for these cases.

**Smallest improvement:** report included, measurable, and missing counts for every metric; show observed-target concentration and the range consistent with missing targets. Define the missing-data decision rule before collection or interpretation. Keep v2.2's three-response baseline descriptive; absent old event names are not proof that players performed no equivalent action.

**Acceptance:** the example above cannot be called demonstrated agency; small measurable subsets cannot silently pass a cohort gate; any formal gate clarification is founder-approved and versioned.

#### 04. Name the interval actually measured after the lock

**P1 | Harness | Confirmed.** RUN `deriveTelemetry` measures from `minigame_result` to the next investigation or inference action. It includes result reading, notebook review, and decision time. It does not directly measure the moment the player returns to the investigation interface.

**Smallest improvement:** describe it as time to next investigative action, retain the approved threshold pending any amendment, and use observation to distinguish productive thinking from navigation friction. Report missing intervals explicitly.

**Acceptance:** analysis never attributes a long interval to confusion without supporting evidence; both endpoints and measurable sample size are stated.

#### 05. Separate gameplay completion, submission, and reveal reception

**P1 | Harness | Confirmed.** APP `renderSurvey` marks gameplay complete before navigating to Jotform. Reveal return is local; Q2-Q4 precede Truth/Verdict. A completed telemetry flag therefore proves neither form submission nor enjoyment of the ending.

**Smallest improvement:** finish the existing Task 5 phone smoke with its excluded run ID; report starts, eligible submissions, and observed reveal returns separately. Describe H5 ratings as pre-reveal. An optional post-reveal debrief requires a separately approved protocol, not a silent survey reorder.

**Acceptance:** no send-readiness claim precedes the smoke gate; no full-ending satisfaction claim rests on pre-reveal ratings; completion uses the approved private started-player denominator.

#### 06. Make feedback triage and approved status unambiguous

**P2 | Harness | Confirmed documentation issue.** ANALYSIS has an approved header but its closing paragraph still describes awaiting approval. Broad comments such as "boring" also need an encounter and likely cause to become useful work.

**Smallest improvement:** reconcile the stale approval prose while preserving approved numbers and date. For each feedback theme record encounter, observed problem, Game/Fidelity/Harness class, confidence, affected hypothesis, smallest fix, and what would disprove the diagnosis. Store identities and raw comments privately.

**Acceptance:** one consistent approval state; each prioritized theme has evidence and a testable diagnosis; no feedback becomes canon automatically.

### B. Investigation and memory

#### 07. Put acquired evidence into the scene that grants it

**P1 | Fidelity / Game | Confirmed.** APP `visitRoute` and `visitInterview` grant every listed discovery, while rendering only the scene or opening/claim. CASE gives Clara's cylinder-transcription acknowledgment, Beatrice's supplied letters, and Clara's initials on the transcript as notebook facts without establishing those details in their corresponding displayed first encounters.

**Smallest improvement:** add brief observable actions or attributable dialogue establishing each granted fact. If a fact belongs behind a later action, move its acquisition only after reviewing route solvability. Avoid adding explanatory deductions.

**Acceptance:** every granted discovery has an identifiable player-visible source encounter; the notebook introduces no new testimony or physical observation by itself; redundant proof routes remain available under the approved action budget.

#### 08. Preserve earned scenes and statements for rereading

**P1 | Fidelity | Confirmed.** APP `renderNotebook` lists evidence summaries; `lastScene` is replaced, visited locations are disabled, and interviews are revisitable only for remaining actions. Players cannot reliably revisit the exact words they earned. The GDD's baseline memory includes attributable dialogue and review of earned information.

**Smallest improvement:** retain read-only earned scene/claim history with speaker/location labels. Add basic suspect grouping only if needed for retrieval. Optional short private notes are a further GDD baseline candidate; a graph editor and automated links are unnecessary here.

**Acceptance:** previously seen case-critical wording is reachable during investigation and Case File without spending a move; rereading grants no evidence or inference event and reveals no unseen material.

#### 09. Explain the investigation budget and distinguish free review from new action

**P1 | Fidelity | Confirmed.** APP `meta` shows moves made, while the six-move ceiling becomes explicit at Last Call. `renderInvestigationMenu` disables the entire people entry at six, including access to previously earned follow-ups; some scene-local follow-ups remain available. Access can depend on which scene the player leaves open.

**Smallest improvement:** explain the finite opportunity budget before spending the first move, label costs consistently, and decide explicitly whether earned follow-ups remain available at the cap. Keep read-only review available regardless. Preserve the GDD distinction between a fair offered opportunity and a guaranteed solve.

**Acceptance:** players can predict which action consumes an opportunity; the cap follows one authored rule regardless of screen history; reviewing owned information remains free.

#### 10. Make the competitive interruption an understandable choice

**P2 | Fidelity / Game | Confirmed.** APP `renderInvestigation` replaces investigation with a single "Crack the box" button when triggered. Backing off is offered only after entering the timed challenge. This narrows the apparent freedom of an opportunity-first pulse.

**Smallest improvement:** propose a pre-start decline with a clear authored consequence, or explicitly explain the mandatory transition if the founder retains it for this experiment. Any new decline outcome must preserve proof availability and have defined telemetry semantics.

**Acceptance:** the player understands participation and consequences before the clock starts; every offered path returns to solvable investigation; no additional minigame or branching subsystem is required.

#### 11. Offer investigable actions without supplying their conclusions

**P2 | Game / Fidelity | Confirmed copy, editorial effect.** APP offers "Challenge that claim" when triggers exist; CASE follow-thread prompts sometimes identify the exact comparison. This may test following a suggestion more than forming a question.

**Smallest improvement:** review each prompt for the boundary between clear action and supplied interpretation. Use concrete people, objects, and statements the player knows. Preserve action-cost clarity and legitimate context; do not introduce a freeform argument evaluator or a new cross-examination game.

**Acceptance:** prompts say what an action does without asserting the contradiction or solution; a founder read-through finds no action depending on unknown knowledge; subsequent observation distinguishes deliberate investigation from button exhaustion.

#### 12. Give suspects a memorable public identity at selection

**P2 | Fidelity / Game | Confirmed.** CASE includes `public_hook` for each suspect, but APP `renderPeoplePicker` displays only name and role. The GDD calls for living suspect cards with a memorable human hook.

**Smallest improvement:** use a concise, spoiler-free public hook and accumulate only earned factual history. Combine with item 08 where practical.

**Acceptance:** each suspect is distinguishable before questioning; no secret, guilt label, suspicion ranking, or designer interpretation appears in their card.

### C. Minigame and competitive consequences

#### 13. Teach the lock before starting the race

**P1 | Fidelity / Harness | Confirmed.** APP starts `openLockWindow` before displaying the detailed instructions. The rival resolves at 19 seconds while the main clock displays a 45-second limit. Instructions say "Release" although the input is a "Set pin" click/tap.

**Smallest improvement:** provide a short ready screen explaining input, failure, stakes, and return, then start both competitors together. Make the rival deadline legible and use the actual input verb. A tutorial campaign is unnecessary.

**Acceptance:** reading instructions consumes no competitive time; a first-time player can identify the input and reward; visible clocks accurately describe when a rival win ends the race. The accepted unreachable-timeout gap need not become new gameplay.

#### 14. Preserve control focus and assess the moving target honestly

**P1 | Harness / Fidelity | Confirmed source risk; usability needs observation.** APP rerenders the lock after each successful pin, replacing the focused button. There is no explicit focus restoration. The CSS reduced-motion rule does not stop the JavaScript-driven marker. A visual moving target is not automatically accessible because buttons have focus outlines.

**Smallest improvement:** retain or restore the action control's focus and stable labels; inspect announcements and target cues with real keyboard and relevant assistive use. Define an equivalent accessible interaction separately if required; do not secretly give some players easier evidence requirements.

**Acceptance:** four pins can be attempted without losing keyboard control between successes; focus and result transitions are understandable; unsupported interaction needs are recorded rather than claimed solved by CSS.

#### 15. Tune challenge from first-use behavior, not assumed excitement

**P2 | Game | Needs observation.** CASE pin tolerances and a fixed rival clock set difficulty; APP uses a frame-cached marker position at click time. Touch delay, reading time, and timer throttling may affect perceived fairness. Their practical impact has not been measured here.

**Smallest improvement:** after item 13, observe first-use attempts on intended devices and inspect whether accepted inputs match visible timing. Decide whether a click should sample the current clock position or the last displayed frame, then validate that choice. Adjust only evidenced problems.

**Acceptance:** input timing matches the stated rule; tuning rationale names observed misses, comprehension, and win/loss experience. No hidden adaptive advantage or larger minigame pool is added to manufacture a pass rate.

#### 16. Show exactly what Leverage bought and when first look expires

**P1 | Fidelity | Confirmed.** After Listen In, RUN adds the private observation, but APP `renderLockResult` retains generic loss text instead of displaying the acquired fact. First-look copy says "next move" while expiration is consumed by new investigation visits, not every follow-up or reread.

**Smallest improvement:** show the acquired observation immediately, update the resource balance, and name the precise expiration trigger. Give a brief factual notice when the information becomes public. Keep learned information available after the privilege expires.

**Acceptance:** players can identify what they acquired and whether it remains private; each expiration happens once at its defined trigger; no ownership is removed and no conclusion is supplied.

#### 17. Decouple the rival's murder theory from who wins the lock

**P2 | Fidelity / Game | Confirmed.** APP `renderLastCall` assigns the rival the correct culprit if the rival won the lock and a different culprit otherwise. This is a direct win-to-accusation mapping without a represented deduction route. It risks implying that minigame success determines detective success.

**Smallest improvement:** use a small authored rival evidence route and consistent final theory, independent of simply winning the box, or disclose the abstraction when interpreting results. Keep the rival deterministic research scaffolding.

**Acceptance:** the rival's knowledge and accusation have an authored causal explanation; human lock success alone does not dictate rival correctness; reports still make no real-multiplayer balance claim.

#### 18. Make competitive consequences feel like events in the case

**P2 | Game / Fidelity | Editorial, grounded in APP result copy and rival notices.** Break/abort says the box is opened publicly without showing who acts or why. Rival activity is brief and mostly front-loaded, so a visible notice may feel like a status update rather than another detective pursuing a case.

**Smallest improvement:** add one short causal transition at each relevant result and a few authored, knowledge-consistent rival reactions. Explain the action, preserve ambiguity about deductions, and return promptly to player control.

**Acceptance:** players understand why the box's contents become available; reactions reflect actual state; no extra compulsory scene follows every mundane action and no autonomous rival system is built.

### D. Story and prose

#### 19. Establish the player's role, personal reason to act, and rival relationship

**P2 | Game | Editorial.** APP opening establishes a striking mystery; the rival is chiefly introduced through the interface and later activity. The player can be mechanically tasked without feeling situated in the gathering.

**Smallest improvement:** add a few concrete lines clarifying why this detective is present, what they can do, and why the other detective's progress matters. Use existing case circumstances rather than inventing a backstory system.

**Acceptance:** an unprompted reader can describe who they are, why they investigate, and why the rival matters; opening length remains appropriate for the short test and does not preview the solution.

#### 20. Differentiate voices beyond polished wit

**P2 | Game | Editorial.** CASE gives several suspects similarly elegant aphorisms or punchlines. Retain the wit but vary sentence shape, evasion, vocabulary, and emotional pressure. Clara can control detail, Rusk manage appearances, Quill perform authority, and Beatrice resist exposure without all sounding like the same writer.

**Smallest improvement:** review one representative exchange per character first, then apply the founder-approved voice direction. Use the [retained Host authority](../../../design/the-host.md) when writing Vesper; suspect dialogue should retain its own identities.

**Acceptance:** the founder can distinguish speakers in anonymized excerpts and explain the difference; every exchange advances character, observation, or tension; quips do not trivialize the death.

#### 21. Give decisive testimony dramatic resistance and observable limits

**P2 | Game | Editorial.** Beatrice's conditional scene delivers accusation, confrontation, impact, and sighting in one compact passage. It efficiently supplies proof, but may collapse a satisfying discovery into receiving a summary.

**Smallest improvement:** preserve the same truth and redundant routes while clarifying what she directly heard, what she saw, and why she withheld it. Let an earned question precipitate the disclosure. Do not add arbitrary clicks or hide necessary proof solely to make the case harder.

**Acceptance:** testimony remains attributable and distinguishable from inference; players can explain the connection in their own words; the Rusk alternative stays viable within the same evidence-slot budget.

#### 22. Strengthen the human stakes behind the motive and other lies

**P2 | Game | Editorial.** The authored scheme gives each suspect something to conceal. The emotional cost of exposure and the victim's effect on these people can be more tangible than an abstract reference to confidential research.

**Smallest improvement:** specify one concrete threatened consequence or relationship cost in existing scenes for the central motive and major innocent lies. Keep the approved murder truth. Avoid new suspects, side quests, or expository biographies.

**Acceptance:** a reader can explain why the killer acts and why each innocent suspect lies; motives feel distinct; ordinary dishonesty does not become automatic proof of murder.

#### 23. Audit causal and physical continuity through the delivered evidence

**P2 | Game | Needs targeted review.** CASE has an explicit timeline, recording substitution, apparatus access, and a later discovery of the body. This review does not establish a contradiction, but internal author notes alone cannot make the chain fair to the player.

**Smallest improvement:** map each essential causal link to an encountered observation, including timing, recording identity, access, substitution opportunity, motive, and the cover-up. Check travel and handling plausibility without adding unnecessary forensic detail.

**Acceptance:** the founder can explain the sequence without relying on an undisclosed decisive fact; apparent contradictions are either intentional witness claims or corrected; changes preserve the approved solution unless separately authorized.

#### 24. Use prose rhythm, silence, and detail to support tension

**P2 | Game | Editorial.** Short text cards are economical, but repeated summary-plus-witticism can flatten emotional progression. Beauty is contextual and cannot be certified through a readability score.

**Smallest improvement:** retain strong concrete images, cut decorative lines that compete with evidence, vary sentence length, and give the discovery of violence room to register. Read selected scenes aloud before rewriting the whole case. Avoid production voice, animation, or illustration work at this stage.

**Acceptance:** the founder approves an opening, a pressured interview, and the reveal as the prose standard; clue-bearing details remain clear; subsequent players describe tension or curiosity in specific moments rather than only praising general atmosphere.

### E. Commitment and ending

#### 25. Reduce Case File bookkeeping and label its representational limit

**P2 | Fidelity | Confirmed.** APP `renderLastCall` asks for culprit plus four/five unordered facts and reports invalid selection after attempting commitment. This samples evidence selection; it does not directly capture the causal reconstruction required by the production GDD. The fixture explicitly excludes final Structured Reconstruction UI.

**Smallest improvement:** show a selection count, preserve the draft, and keep evidence review easy. First assess whether a neutral explanation during an approved debrief resolves the research gap. Build a minimal causal-order prototype only if the next research question requires it.

**Acceptance:** the four/five constraint is clear before commitment; only owned evidence is selectable; no precommit correctness hints appear; reports do not equate selecting a set with demonstrating the full causal theory.

#### 26. Reconcile the authored proof descriptions and scorer

**P1 | Game / Harness | Confirmed representation difference; correctness impact needs validation.** CASE `essential_truths.routes` and `case_file.proof_groups` use different sufficient sets. For example, a transcript alone satisfies the scorer's false-voice group, while the descriptive route pairs transcript and service route. This may be intentional scoring compression; the difference alone does not prove an unfair verdict.

**Smallest improvement:** document the reason for each difference and check winning four/five-fact sets against the intended causal proof. Validate their actual acquisition through legal actions and alternatives, including loss/abort and the Rusk route. Directly injecting evidence into state is insufficient proof of reachability.

**Follow-up source audit, 2026-10-01:** both descriptive motive routes require `e-quill-payment` and `e-private-detail-match`. Those are separate Follow the Thread rewards, while one initial Leverage and the global single-use restriction prevent acquiring both legally. This establishes a conflict in the descriptive routes. It does not establish that the operational scorer has no reachable solution. Do not copy the descriptive routes into the scorer. Reconcile the authored proof explanation and demonstrate legal acquisition in the successor.

**Acceptance:** every accepted proof set has an authored justification; representative intended valid routes can obtain and submit a valid set within the budget; rejected counterexamples have a specific reason; any rule change is approved before editing.

#### 27. Give a factual verdict without teaching the answer before commitment

**P2 | Game / Fidelity | Confirmed.** RUN stores a verdict reason; APP `renderReveal` only says success or that at least one essential part was missed. The following technical sentence about model judgment and solution graphs interrupts the player-facing ending.

**Smallest improvement:** after revealing the truth, state the decisive supported or missing link in plain story language. Move implementation explanation to research documentation. Preserve the reveal's explanation of the innocent suspects' lies and avoid an exhaustive error report.

**Acceptance:** players understand why their locked theory succeeded or fell short; feedback agrees with authored evaluation; no solution hints appear before commitment and no final Postmortem system is required.

#### 28. Handle a reveal link with missing run state honestly

**P1 | Harness | Confirmed source path.** APP `boot` creates initial state when restoration fails, even in reveal mode; `renderReveal` treats anything other than `caseFile.correct === true` as failure and marks completion. A returning player with missing storage can receive a false negative verdict for an unrecorded run.

**Smallest improvement:** allow a truthful solution view while stating that the individual verdict is unavailable when no committed Case File exists. Avoid synthesizing research completion for a new empty run. This concerns state correctness, not securing a public static solution behind authentication.

**Acceptance:** a same-tab intact run preserves its verdict; missing-state return shows no fabricated failure or completed gameplay record; alternate-tab/storage-loss behavior is covered in approved QA.

### F. QA and economical delivery

#### 29. Make QA assertions match intentional state transitions

**P1 | Harness | Confirmed in QA.** The existing checker can label private-to-public evidence as a duplicate, and the plan expected a first-look-close event after a break despite immediate public release. Existing route tests also need to be read according to what they exercise, not treated as complete human-path proof.

**Smallest improvement:** correct the next QA protocol to account for discovery identity plus visibility transition and outcome-specific events. Add focused legal-path coverage for chosen changes. Keep accepted timeout and abandonment gaps explicit.

**Acceptance:** one legitimate private-to-public transition passes, a true repeated grant fails, and break/abort assert their public-release contract; test reports distinguish source invariants, runtime tests, and browser actions.

#### 30. Capture device context without mislabeling viewport width

**P2 | Harness | Confirmed semantics.** APP derives `device_class` from a 640 CSS-pixel breakpoint. A narrow desktop browser pane can therefore report mobile. QA Run A's actual width was not captured, so its device label is an anomaly to explain, not a proven detector defect.

**Smallest improvement:** document current semantics and collect actual device/browser context in the private research tracker. Change field semantics only with instrument/version review. Observe the existing phone smoke for scrolling, tap accuracy, readable clues, and survey return.

**Acceptance:** reports distinguish physical device from viewport class; no desktop result is presented as phone usability evidence; new metadata requirements are approved before instrument changes.

#### 31. Investigate handoff and storage robustness only where evidence warrants

**P2 | Harness | Needs observation.** RUN `buildSurveyUrl` serializes the event stream into a query string; repeated lock misses increase its size. APP storage and fetch failures have limited recovery. No URL truncation or storage-loss incident is established by this review.

**Smallest improvement:** use a bounded worst-reasonable run during approved QA to measure URL length and confirm Jotform read-back, plus inspect a storage-unavailable return. Fix demonstrated failure modes with clear recovery copy or bounded transport changes under an approved spec.

**Acceptance:** the sampled long run preserves the required fields through submission, or the limitation is documented with an actual failing case; no telemetry backend or new dependency is added merely to address a hypothetical risk.

#### 32. Preserve a stable experiment and cap fixture investment

**P1 | Harness / Deferred | Confirmed governance requirement.** The current fixture is an immutable published artifact and the analysis plan is approved. Changing content, timing, scoring, or measurement midway would mix materially different experiences.

**Smallest improvement:** select a bounded change package before implementation. If changes are approved, create an explicitly versioned successor through the existing publishing process and associate its protocol and evidence with that version. Update the Phase 1 scope record to account for this review artifact. Keep the original route available.

**Acceptance:** every response maps to the fixture and instrument it actually used; excluded QA/founder runs remain excluded; no unapproved threshold change, in-place release patch, or automatic expansion into production systems occurs.

## 5. Recommended order and stopping point

### Now: complete preparation and settle evidence limitations

The existing phone smoke remains useful and does not require implementing this backlog first. It checks the survey/return path, not prose quality. Resolve interpretation of items 01-05 before treating the resulting external cohort as a conclusive Gate 1 decision. Item 06's approval-state cleanup can be a small documentation follow-up.

Before external invites, present the founder with the confirmed experience issues in 07, 09, 13, 16, and 28 and the proof-alignment check in 26. Choose explicitly between sampling the current fixture with those limitations recorded and preparing a narrowly changed successor. This review does not grant send approval or automatically declare the existing QA invalid.

### First candidate implementation package

If a successor is selected, prioritize:

1. **Source integrity:** 07, 26, and focused checks from 29.
2. **Understandable play:** 09, 13, 14's focus correction, and 16.
3. **Honest outcomes:** 28 and the minimal verdict-copy work in 27.
4. **Memory fidelity:** the read-only earned-history portion of 08 if forgetting or forced memorization would otherwise confound this test.

This is a recommendation to scope, not an estimate or approval. Select only work needed to remove a named confound. Do not fold all P2 items into the package.

### Editorial pass after choosing direction

Use three short samples for 19-24: opening, one pressured interview, and reveal. Founder approval establishes a concrete voice and tension standard before a full rewrite. Preserve the existing case truth and compare each edit against evidence ownership and route viability. Do not tune story and lock difficulty simultaneously without recording which interpretation becomes harder to isolate.

### Explicitly defer

- Real multiplayer rivalry, simultaneous production pickers, and 7-8-player scaling validation.
- Production Leverage earning/economy, a larger minigame pool, and progression systems.
- A visual deduction graph, automatic clue links, full Case Board optimization, and Gate 2 memory research.
- Full Structured Reconstruction, live shared Last Call staging, final Postmortem, and production rankings.
- Full Vesper performance, generated dialogue, voice acting, cinematics, custom art pipelines, and animation systems.
- Backend abandonment capture, account/auth systems for a static reveal, and general analytics infrastructure.

These remain owned by their canonical systems and future plans. Their absence limits the representativeness of this fixture; it does not make them all prerequisites for a useful bounded test.

**Stop improving the fixture when:** the chosen cohort can understand actions, retrieve earned information, experience the intended decisions and consequences, and complete the research flow without the selected confounds. Remaining dissatisfaction that survives those conditions is evidence about the game to investigate, not a reason to keep polishing the framework indefinitely.

## 6. Validation and decision handoff

For any selected change, prepare an approved implementation plan with exact files and acceptance criteria from the relevant items above. Respect deterministic truth and ownership; research browser code does not authorize moving production arc logic out of Python. Keep Jotform read-only unless a separate instrument change is explicitly approved.

Validation should then cover:

1. Focused automated checks for changed state/evidence/proof behavior, including negative and alternate routes.
2. Browser interaction checks for changed controls, focus, refresh, and state restoration.
3. The approved real-phone survey/reveal smoke, with its labeled excluded run and screenshot evidence.
4. Founder creative review for voice, emotional credibility, and acceptable fidelity.
5. The approved external cohort for engagement and detective feeling; no technical result substitutes for this evidence.

A useful future feedback record is: `encounter -> observed problem -> likely cause -> class -> confidence -> smallest change -> affected hypothesis -> acceptance check`. Separate frequency from severity: a single blocked submission can matter more than several preferences about decorative prose.

### Review completion criteria

- [x] Compare the actual v3.0 source with the current GDD and explicit fixture exclusions.
- [x] Distinguish confirmed source findings, creative judgment, unverified risks, and prior QA evidence.
- [x] Provide 32 concrete improvements with priorities, smallest useful changes, and acceptance criteria.
- [x] Separate game quality, fidelity, harness reliability, and deferred production investment.
- [x] Preserve approved thresholds, published fixture, read-only survey boundary, and founder gates.
- [ ] Implement selected improvements. Outside this review's scope.
- [ ] Complete the founder phone smoke and establish external-player fun. Still pending.

## 7. Additional source records

- [Phase 1 execution plan](../../../superpowers/plans/2026-09-27-phase-1-v3-send-readiness.md) and [approved design](../../../superpowers/specs/2026-09-27-phase-1-v3-send-readiness-design.md).
- [GDD authority and routing](../README.md), [decision ledger](../00-governance/00-decision-ledger.md), and [current design state](../00-governance/02-current-design-state.md).
- [v2.2 baseline](../03-playtest-evidence/98-paper-test-02-v2.2-results.md) and [validation state](../02-validation/98-validation-state-and-remaining-plan.md).
- [Fixture tests](../../../../playtests/nightcap-paper-test-02-v3.0/tests/fixture.test.mjs), [Rusk route tests](../../../../playtests/nightcap-paper-test-02-v3.0/tests/rusk-route.test.mjs), and [styles](../../../../playtests/nightcap-paper-test-02-v3.0/styles.css).

This is a supporting review, not a replacement canonical GDD or a report of newly collected player evidence.

## 8. Remediation preparation

On 2026-10-01 the founder requested addressing all 32 improvements and validating them, using subagent-driven development. The concrete draft package is the [v3.1 contract](../../../specs/0091-nightcap-v3.1-improvements.md), [six-task plan](../../../superpowers/plans/2026-10-01-nightcap-v3.1-improvements.md), and [creative samples](99-paper-test-02-v3.1-creative-samples.md). Their specific research rules and creative direction await the required artifact approval.

The five existing v3.0 Node test files were rerun during preparation: 31 passed, zero failed. This is a baseline result, not validation of the proposed fixes. No fixture code has been changed and no new human play evidence has been collected.
