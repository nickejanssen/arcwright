# Nightcap Couch Race — Design (Brainstorm Output)

**Status:** Approved direction (founder, July 15, 2026)
**Author:** Claude (brainstorming session with founder)
**Date:** 2026-07-15
**Canonical follow-ons:** ADR `docs/decisions/0013-nightcap-couch-race-v1-launch-target.md`, story bible `docs/story-bibles/nightcap-couch-race.md`, spec `docs/specs/0072-nightcap-couch-race-v1.md`, epic `docs/roadmap/epics/M5-I-nightcap-couch-race-arc-and-interrogation.md`

---

## Problem

The current Nightcap v1 model (killer-among-players, 30–75 minutes, four-player floor, role-performance burden) is expensive to playtest and has high onboarding friction. The founder directed a pivot: players sit on the couch, interact with the TV and each other, and race to solve a murder. ADR 0010 already documented this direction as two proposed post-playtest pivots ("Couch Game" pacing + "Competitive Investigator" structure); the founder has now pulled it forward, before Rehearsal 1, as the v1 launch target.

## Founder decisions recorded in this session

1. **Positioning:** Couch Race becomes the v1 MVP launch target. Rehearsal 1 retargets to it. Killer-among-players stays fully documented as the approved future "Imposter Variant."
2. **Competition structure:** platform supports a competition dial (solo race / teams / co-op vs clock) per the configurable-composition principle; v1 ships the solo race with shared table moments.
3. **Device model:** TV shared display + phones as private surfaces (Jackbox pattern), reusing the M4 privacy layer.
4. **Docs shape:** new canonical story bible for Couch Race; the existing `nightcap-murder-mystery.md` stays canonical for the Imposter Variant with a repositioning note.

## Approaches considered

1. **Reskin sprint** — NPC killer on the existing 8-beat arc plus race scoring; no interrogation. Fast but undifferentiated; no visible AI advantage.
2. **Interrogation-first couch race (selected)** — new compressed 6-beat arc; core loop is interrogating AI suspects rendered on the TV, answers constrained by the knowledge graph; race scoring with contradiction-catching. Pulls forward the interrogatable-AI-participant capability the old model deferred to v1.1; the same capability serves Daily Case.
3. **Full vision first** — free-text/voice questioning plus fully animated suspects with TTS from day one. Deferred: front-loads Tier 2 polish (D-066) before any human has played.

## Experience design (summary — the bible is canonical)

- 2–8 players, 20–40 minutes, TV + phones. Killer is one of the AI suspects on the TV, never a player.
- Six execution beats (compressed Story Circle): The Pour (cold open, murder staged audiovisually per D-070), The Scene (evidence wave; Crime Scene Smash slots in), The Grill (interrogation rounds), The Twist (recontextualizing revelation; Evidence Locker slots in), Last Call (countdown, accusations lock), The Truth (full reveal and scoring).
- Interrogation: per round each player privately selects a question intent on their phone; the suspect answers aloud on the TV for the whole room; the asker receives a private "tell." Question scarcity creates strategy; public answers create table talk.
- Scoring: evidence uncovered, contradictions caught (knowledge-graph provenance surfaced as a mechanic), accusation accuracy weighted by earliness. Wrong accusation = temporary lockout, never elimination. First correct accusation triggers Last Call for the table.

## Architecture mapping

- New ArcDefinition + case-generation templates; no engine schema changes expected for the beat structure (beat count is arc-level per D-053).
- Question intents are deterministic menu selections in v1; AI composes suspect dialogue from resolved knowledge state (mandatory pre-generation knowledge query). Free-text questioning later is a classification task in front of the same intents.
- Suspects are standard unified-model AI characters. Contradiction detection is deterministic (claim history vs. knowledge state), building on the Daily Case contradiction-ledger design.
- Reused as-is: M4 join flow, shared display rendering, phone privacy layer, mini-game layer, pacing engine, safety rails, SSE events, Cloudflare runtime. PR #225 (live-loop AI character dialogue, spec 0071) is the direct dependency for suspect answers.
- Cost: bounded question tokens bound generation calls (~30–50 short fast-tier generations per session + one cacheable case-generation pass + narrator lines). Shorter sessions reduce per-session cost against the M5 gross-margin gate.

## Business and market analysis

- Netflix launched TV party games with phones-as-controllers including Knives Out: Dead Man's Party — commercially validating both the living-room format and (for the future) the Imposter Variant, while occupying the killer-among-players lane with major IP.
- Death by AI (Little Umbrella) reached ~20M players in three months and profitability, proving AI-native party games scale; it is prompt-comedy, not coherent deduction.
- Jackbox's Trivia Murder Party proves a decade of demand for murder-comedy party framing; content is authored and finite.
- **Wedge:** infinite, coherent, fair murder mysteries with suspects that hold real knowledge state. Replayability is structural (engine-generated), not content-pack-based; the Arcwright engine is the moat (D-034).
- Pricing: host-pays-per-session north star retained; "case night" bundle (e.g., 3 cases) is the candidate purchasable unit. Numeric pricing still deferred until per-case cost is measured.
- Named risks: (1) generated-case fairness/solvability — mitigated by the balance principle and the AW-272 continuity/coherence eval suite as a launch gate; (2) distribution/discovery for web party games — open question; (3) Netflix IP muscle in the adjacent imposter lane — differentiation is racing against AI suspects; (4) suspect-answer latency on the TV — fast-tier routing + prompt caching are already architectural requirements.
- Verdict: credible commercial path; widened audience (floor drops from 4 players to 2 because suspects are AI); one capability build (interrogation) feeds two products (Couch Race, Daily Case); dramatically faster founder test loop (three cases per evening vs. one long session).

## Deliverables from this design

1. Story bible `docs/story-bibles/nightcap-couch-race.md` (new canonical v1 target).
2. `docs/story-bibles/nightcap-murder-mystery.md` repositioned as the Imposter Variant bible.
3. ADR 0013 (accepts and executes ADR 0010's pivots as the v1 target; ADR 0010 → Accepted).
4. Decisions log D-071; open-questions entries (product name, distribution channel, free-text interrogation timing).
5. PRD `03-scope.md` amendment and roadmap `00-overview.md` gate updates.
6. Epic M5-I with tasks AW-281–AW-286; spec 0072; GitHub issues.
7. Staged launch path: retargeted Rehearsal 1 (founder-run, local tunnel per D-065) → Rehearsal 2 (outside group) → M6 qualifying sessions → pricing decision.
