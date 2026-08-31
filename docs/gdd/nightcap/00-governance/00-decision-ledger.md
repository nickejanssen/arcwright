# Nightcap — Decision Ledger

## Governance

Use these statuses exactly:

- **DECIDED** — explicitly approved by the creator and represents the current Nightcap design.
- **TESTING** — preferred direction / implementation awaiting evidence.
- **OPEN** — unresolved.
- **RECOMMENDATION** — proposed but not creator-approved.
- **PARKED** — deliberately deferred.

**DECIDED is not immutable.** Real gameplay, stronger evidence, or downstream cohesion problems may justify reopening or reversing an approved decision. Preserve decision history rather than pretending the earlier state never existed.

The assistant may recommend and challenge. It may not silently decide.

---

## DECIDED

### Core

- Cinematic competitive murder mystery centered on deduction, reasoning, puzzling, and investigation.
- Story immersion matters, but Nightcap must feel like a game rather than a choose-your-own-adventure experiment.
- Coherent story/truth spine with reactive presentation.
- Product promise: **A cinematic competitive murder mystery where everyone gets to be the detective.**
- Player fantasy: **Be the smartest, strangest detective in the room: observe, deduce, manipulate, compete, and prove your case.**
- Core loop: **WATCH → HUNT → THINK → PLAY → REACT**, leading to **LAST CALL → CASE FILE → THE TRUTH → THE VERDICT → THE POSTMORTEM**.

### Arcwright runtime boundary

- Nightcap is an authored **arc definition on the Arcwright narrative runtime**, not a standalone game whose narrative layer is bolted on afterward.
- Arcwright resolves authored state deterministically before generative expression. For Nightcap's fairness-critical mystery state, the model expresses resolved state; it does not choose or rewrite canonical truth.
- Arcwright provides a per-character knowledge graph queried before generation, a unified character model in which human-controlled and AI-driven roles use the same underlying character object, and surface-agnostic content events with audience targeting.
- Nightcap uses those primitives as gameplay: interrogation exposes character knowledge through authored interaction; public answers versus private tells use audience targeting; fresh presentation may be generative while case truth and resolution remain deterministic.
- Whether a suspect is AI-driven or human-controlled is a property of the character model rather than a separate Nightcap engine path.
- Arcwright owns resolved runtime state, character knowledge, event targeting, and presentation-independent content events. Nightcap's arc and GDD own the murder truth, fair evidence/proof architecture, gameplay meaning, competition rules, scoring, and player experience.
- Existing Nightcap system pages continue to own player-facing behavior. This runtime boundary should prevent duplicate case/story systems rather than create a second layer of gameplay rules.
- Nightcap cases have a **hidden authored graph/state topology**: players in the same Case Challenge begin from the same baseline/root state and may traverse different connected investigative routes toward the essential truths. This graph is not surfaced as a solution map to players.
- Arcwright should distinguish canonical case/solution relationships, investigation opportunity topology, and per-character knowledge state well enough to support deterministic endgame resolution and case analysis.
- Arcwright should track authored case complexity and actual player traversal as a platform/authoring/analytics capability. Candidate measures include path depth, branching, alternate routes, bottlenecks, dead ends, route overlap, and player movement; exact metrics/thresholds are **TESTING**.
- The requirement is explicit graph/state semantics, **not a neural-network decision layer**. Mystery truth, reachability, and fairness remain inspectable and deterministic.

### Investigation & deduction

- V1 investigation is bounded.
- Post-V1 direction remains hybrid targeted/free-form investigation.
- Pressure is primarily number of actions / opportunity pressure, not reading speed.
- Cinematic observation: bonus evidence first; required observational evidence later/configurable.
- Bounded branching; players pursue their own investigation.
- Shared baseline + private unlocks.
- Investigation should be **diegetic-first**: concrete people, places, objects, claims, behaviors, irregularities, records, and routes dominate the player-facing surface; underlying structure may remain where needed for clarity/accessibility.
- A meaningful investigation action may simply reveal fair, relevant information. It does not need to manufacture a world reaction.
- **The game presents observations; the player owns their implications.**
- Optimize for **freedom of reasoning, not unlimited freedom of input**.
- THINK is continuous, with occasional intentional opportunities to organize, compare, connect, challenge, or act on a theory rather than routine forced reasoning prompts.
- Player-generated hypotheses may feed bounded authored verification, comparison, confrontation, or challenge actions.

### Evidence / deduction fairness

- **Equal solvability, unequal information.**
- Fairness means every player has a legitimate opportunity to win from the case architecture; it does **not** mean equal outcomes, adaptive catch-up, or protecting a player from the consequences of weak investigation. Players may miss evidence, pursue bad theories, accuse the wrong culprit, and lose.
- **Redundant truth, nonredundant experience.**
- Private evidence can remain private through Last Call.
- Sharing is player-controlled.
- **Knowledge ≠ Proof:** players may communicate or learn claims from one another, but Arcwright still distinguishes heard/claimed information from legitimately acquired or verified case state when resolving the final reconstruction. The player should not have to perform proof bookkeeping manually.
- Nightcap tracks proof ownership/admissibility automatically. Players should not have to remember which discovered item is legally attachable at the end. The game may show what the player legitimately owns, but it may not tell them whether that proof actually supports their accusation.
- Big proof dimensions are known early.
- Hybrid deduction expression.
- No correctness confirmation before final commitment.
- Contextual uncertainty guidance.
- Fair-play mystery deception is allowed: red herrings, lies, mistakes, forgeries, staged scenes, planted objects, manipulated recordings, misleading context, omissions, and other literary/cinematic devices.
- **The fiction may lie. The game must play fair.** Deception must remain consistent with the authored truth and reasonably interrogable.

### Case Board / memory

- Case Board direction: player-built connections + structured comparison.
- Memory/history and Case Board have distinct jobs: memory retrieves what the player legitimately encountered; the Case Board supports how the player currently understands the case.
- Automatic organization may use objective factual metadata such as person, place, time, source, or artifact type.
- Meaningful deductive relationships normally remain player-owned.
- Case Board uses simple expressive tools for connecting, grouping, annotating, and optionally labeling player-created relationships.
- Case Board is an optional reasoning tool; players may use it heavily, lightly, or minimally.
- Current player-authored thinking stays clean; theory evolution may be retained invisibly for Postmortem/telemetry/research rather than cluttering the live board.
- Nightcap may retrieve/remember/review/organize/compare discovered information, but may not rank significance, choose the important comparison, identify an undiscovered contradiction, recommend the correct action, or infer the conclusion.
- Baseline memory support: persistent dialogue/claim transcript, clear speaker/suspect attribution, replay/review of earned case-critical information.

### Winning / Last Call / Case File — Structured Reconstruction

- Case lock only at Last Call.
- Hard countdown. The countdown pressures commitment and decision-making, **not interface speed**.
- V1 **Case File interaction uses Structured Reconstruction**: choose the culprit, then construct a short causal reconstruction from case concepts the player legitimately encountered/acquired. Player-facing naming remains an implementation/presentation detail.
- The authored case defines a small set of case-specific essential truths required for a solve. Do not force every case into a universal `killer / weapon / motive / room` template.
- The reconstruction is resolved **deterministically** against the authored solution/case graph. Generative models may express the result but may not judge whether an argument is persuasive or choose the winner.
- Multiple legitimate information routes may establish the same essential truth.
- Nightcap tracks what each player legitimately learned/owns so endgame admissibility is not bookkeeping, but it may not tell the player which facts are important or correct.
- V1 winner determination does **not** use numerical Case Strength or subjective argument scoring.
- If exactly one player solves the murder, that player wins.
- If multiple players solve it, they are tied on the murder; minigame performance is the current tie-break direction. Speed is not a standard endgame tie-breaker.
- If nobody solves the murder, **no player is crowned the murder winner**; the murderer/case beats the table. Postmortem recognition does not become an alternate victory.
- Last Call uses a **hybrid trigger**: authored dramatic timing constrained by a minimum fair-solvability state. That threshold asks whether the case offered a legitimate opportunity to solve it, not whether every player personally built a viable answer or received corrective opportunities.
- Final theories lock privately and simultaneously. After lock, each player's accused culprit is revealed theatrically before The Truth. Players do not give case presentations.
- Structured Reconstruction must feel like deduction and payoff, **not essay-writing, evidence paperwork, or giving a lecture**.
- Free text should be limited and generally optional; favor selecting/arranging/connecting meaningful learned concepts.
- **PARKED fallback:** Culprit + Decisive Facts if representative testing shows Structured Reconstruction is too fiddly or slow.
- **PARKED augmentation:** cinematic detective proclamation/confrontation after deterministic resolution if testing shows it improves payoff.
- **PARKED:** Ace-Attorney-like witness/interview contradiction mechanics unless feedback specifically indicates interviews need improvement.

### Minigames

- Competitive pulse, not strategic center.
- Story-wrapped/skinned without sacrificing mechanical fun.
- Broad eccentric-investigator/spy skill portfolio.
- Investigator archetype emerges from play rather than preselection.
- Graduated ranking.
- Adaptation target: pacing + skill diversity.
- Same competitive challenge for players in V1; no hidden outcome manipulation.
- Big reward swings.
- **Big swings, short half-life:** primarily finite tactical spikes, not persistent compounding engines. When a temporary advantage reveals legitimate information, the special access/priority/protection may expire but the player keeps what they learned; the short half-life applies to the mechanical privilege, not to memory.
- Minigame performance tracked for tie-breaking and Postmortem material.
- Major minigame beats must reconnect to murder-facing state; tiny/lightweight competitive moments may sometimes exist primarily for energy, humor, or personality.
- Minigames are **opportunity-first**: prefer access, priority, temporary advantage, resources, or information. Essential murder proof must still be earned through legitimate investigation.
- Trigger model is **story-triggered hybrid**: authored circumstances create competitive windows and player decisions influence what is contested or how the opportunity is used.

### Story Reactivity & re-entry

- REACT has a dedicated authoritative system owner but is **not a separate game mode/screen**.
- Reactions are **naturalistic but legible** rather than explicitly system-explained.
- Player actions may create real tactical consequences, including temporary or permanent loss of nonessential opportunities, while essential truths retain fair alternate routes.
- Reaction visibility is hybrid: shared events may contain unequal private meaning, information, or follow-up opportunities.
- REACT may expose state; it may not perform inference.
- Re-entry surfaces **state, not inference**: what changed, what was legitimately earned, and what opportunities exist without ranking what matters or recommending the correct next move.
- Major reactions should reconnect to something the player can investigate, reconsider, prove, conceal, expose, exploit, or act upon.

### Espionage / social play

- Social bluffing allowed.
- Heavy information warfare.
- Espionage-first Leverage fantasy.
- Alliances are social only.
- Evidence interaction primarily observe/copy, not destroy.
- Counterintel exists.
- Leverage is finite with a small capped bank and competing uses.
- Natural investigative advantage can come simply from discovering more, noticing more, or reaching useful information first; that advantage does not automatically need to become a spendable Leverage point.
- The earlier direction that Leverage is sourced primarily from minigames is reopened. Minigames may grant Leverage or other temporary advantages, but repeated minigame wins must not become the primary gateway to espionage or compound into control of the whole investigation. Exact Leverage sourcing remains **TESTING**.
- Keep Leverage bookkeeping small and legible; do not create a resource-management layer that players must constantly track.
- Leverage primarily creates **information + opportunity** rather than generic PvP damage.
- Strongest Leverage uses are contextual: the evolving case creates meaningful windows and the player chooses whether to spend the resource.
- Espionage uses uncertain attribution where possible. At two players, obvious actor attribution is accepted; uncertainty shifts toward what was learned/copied/protected/intended.
- Mostly additive sabotage.
- Nightcap does **not** automatically protect a player merely because multiple opponents choose to target them. Concentrated targeting, retaliation, bluffing, and temporary social coalitions are legitimate competitive behavior. Ordinary action costs, opportunity limits, fictional circumstances, and Counterintel apply equally to everyone. If representative testing finds a repeatable mechanic that materially prevents a targeted player from continuing to participate in the investigation, fix that mechanic as a playability failure rather than adding loser protection or pity immunity.

### World / tone / creative boundaries

- A Nightcap case is framed as a **social gathering**; era, occasion, location, and aesthetic may vary inside that legible social frame.
- **Vesper is Nightcap's Host.** `docs/design/the-host.md` remains the specialist voice/character authority where it does not conflict with this GDD.
- `docs/design/nightcap-art-direction.md` remains the specialist visual authority where it does not conflict with current GDD gameplay.
- Nightcap is witty, suspenseful, irreverent, darkly comedic, and cinematic while taking the death and mystery seriously. Humor targets behavior, social dysfunction, and specificity rather than making death itself trivial.
- Graphic violence/gore, sexual content, targeting real people, identity-based hate/slurs, harmful content involving minors, and player-directed psychological-horror/trauma content remain outside Nightcap's content territory.
- The former Story Bible rule that every specific story element must be generated is superseded by the current hybrid-content and deterministic-state-first direction.

### Content / AI

- Procedural scalability with authored quality.
- Hybrid library.
- Human/AI ownership expands only through evidence-gated autonomy.
- Hybrid generation pipeline.
- Soft continuity direction.
- Behavioral group personalization.
- Premium scenes must prioritize immersion, quality, story fit, and avoiding obvious AI slop.

### Truth / Verdict / Postmortem

- End sequence: **THE TRUTH → THE VERDICT → THE POSTMORTEM**.
- The Truth owns narrative catharsis and uses an **evidence-led cinematic reconstruction** of the canonical murder.
- The Truth may explain reality after final theories lock, but should not become a lecture about how players should have reasoned.
- The Verdict confirms the deterministic competitive result and should usually be concise because the solve condition itself should make the outcome obvious.
- When explanation is useful, The Verdict surfaces only the decisive factual difference; it does not defend a subjective score or compare whole essays.
- Generic "multiple awards" is superseded by **The Postmortem**.
- The Postmortem owns social catharsis and uses actual behavior for humorous, selective characterizations/callbacks/roasts.
- Postmortem humor uses **truthful exaggeration**: actual behavior determines the characterization; comedy heightens it without contradicting how the player played.
- Humor should be original Nightcap voice: crime-story confidence, absurd specificity, dysfunctional affection, sharp but playful character observation.
- Behavior is the target, not personal identity.

### Player count

- **Two-player support is mandatory in V1 and first-class.**
- Do not park it as a later Duel mode.
- Four players may remain the best-understood reference configuration unless evidence changes that.
- Two-player Nightcap preserves the same core fantasy with a **sharper, more intimate rivalry** rather than imitating four-player social texture.
- Player-count scaling preserves canonical culprit, canonical truth, authored core story, Case Challenge, proof requirements, and victory standard.
- Player count may selectively adapt information distribution, opportunity architecture, evidence-route density, contested windows, budgets, minigame configuration, Leverage opportunities, and optional social/story beats.
- **Spotlight is deliberately managed public story attention.** Especially at larger counts, Nightcap should actively distribute major visible story/reaction moments so players receive roughly comparable opportunities to matter in the shared room experience. Spotlight may not change truth, Case Challenge, evidence quality, or competitive outcomes to help someone win. Exact calibration remains TESTING.
- **Full core-loop parity** is required at two players; major Nightcap pillars may adapt but may not become vestigial.
- Two-player espionage accepts obvious attribution where unavoidable and preserves uncertainty around what was gained or intended.
- **The V1 upper bound is NOT decided.**

### Difficulty / accessibility / onboarding

- Layered architecture: Case Challenge + Investigation Pressure + Accessibility.
- One-tap normal setup direction with optional deeper customization; exact calibration remains TESTING.
- Case Challenge uses authored baselines; additional variants only when deliberately authored and validated.
- Case Challenge may vary reasoning-chain depth, clue/proof redundancy, ambiguity/contradiction subtlety, and red-herring/alternative-theory complexity.
- Investigation Pressure may vary action economy, opportunity pressure, and pacing; it is not reading-speed pressure.
- Learn by playing through progressive contextual teaching.
- Recommended first cases are full Nightcap cases, not tutorials.
- Case Challenge / Investigation Pressure lock at case start; individual non-reasoning accessibility can change during play.
- Accessibility is lean and mostly invisible: a design constraint, not a major gameplay subsystem.
- Accessibility removes barriers without lowering mystery challenge, proof requirements, competitive meaning, story/cinema quality, immersion, humor, or fun.
- Simplify/redesign a mechanic before making it easier for one competitor than another.
- All competitively meaningful case information requires an accessibility-equivalent presentation; flavor-only details may remain modality-specific.
- Preserve authored cinematics; adapt access around them rather than defaulting to a lesser summary version.
- Accessibility-compatible minigames by construction where practical; active player settings filter the room's minigame pool.
- Individual accessibility settings remain private.
- Persist earned information + use selective shared readiness gates.
- Last Call remains a hard shared countdown; group-level duration may be adjusted when needed.
- Optional group rescue: any player may propose, all active players must agree, and rescue adds authored evidence/opportunity rather than inference. Rescue adds no winner-specific bonus, penalty, or alternate winner calculation; because it changes the shared case state, it may naturally affect who ultimately wins. It is recorded for mastery/completion.
- Mixed-skill competition relies on broad skill expression + volatile tactical state, not loser bonuses or hidden rubber-banding.
- Two-player games retain the selected Case Challenge; player-count scaling adjusts opportunity architecture rather than automatically making the mystery easier.

---

## Superseded / Corrected States

- Any earlier framing that parks two-player play as a later Duel mode is superseded. Two-player support is mandatory and first-class in V1.
- The earlier generic `menu + rare special opportunities` Leverage-access framing is superseded by the current **contextual-opportunity** model; exact UI remains TESTING.
- Generic participation-style multiple awards are superseded by **The Postmortem**. When at least one player solves the murder, the competitive procedure produces one player winner after any required tie-break; if nobody solves it, the murderer/case wins instead.
- Speed is not a standard endgame tie-breaker, though speed may still be observed as Postmortem behavior.
- Prototype/test-fixture behavior never becomes a Nightcap law unless explicitly approved into the GDD.

---

## TESTING

- Exact Leverage costs/frequency.
- Repeated-targeting / Counterintel balance, especially whether any mechanic can be chained often enough to suppress another player's ability to investigate. Do not assume an anti-dogpile protection layer is required.
- **PARKED:** rare auctions; preserve the idea only as historical/design backlog until a concrete gameplay need justifies reopening it.
- Structured Reconstruction UX and accepted-solution authoring.
- Exact minigame frequency and reward calibration.
- Investigation action budgets.
- Spotlight distribution/calibration across player counts.
- Player-count scaling curves.
- Runtime.
- Alpha-player/quarterbacking countermeasures.
- Postmortem personality-generation implementation.
- Case Board UX.
- Continuity value/cost.
- Premium-scene generation architecture.
- Exact authored Case Challenge variant construction.
- Investigation Pressure calibration.
- Baseline memory-support friction vs. deduction impact.
- Whether provenance, re-entry cues, or search/filtering justify V1 scope.
- Room-compatible minigame-pool breadth and variety.
- Readiness-gate frequency and pacing cost.
- Group-rescue frequency, amount, presentation, and exploitability.
- Two-player same-challenge scaling.
- Equivalent-presentation QA for competitively meaningful information.
- Mixed-skill competitiveness without rubber-banding.
- Diegetic-first investigation action clarity: give players a clear view of what people, places, objects, or areas are currently available to explore, while preserving room to investigate within them rather than reducing play to a sequence of prescribed action buttons. The interface may clarify **what can be explored**, never **what is important** or **what it means**.
- Exact frequency of hypothesis-driven actions.
- Story-reactivity cadence and local-vs-shared presentation.
- Truth/Verdict/Postmortem endgame pacing.

## OPEN

- V1 upper player-count bound.
- 7–8-player viability.
- Detailed player-count-specific case scaling.
- Production/content budgets.
