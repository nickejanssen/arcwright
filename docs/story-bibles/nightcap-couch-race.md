# Nightcap Couch Race Story Bible

> Current version: v0.1
> Last updated: 2026-07-15
> Status: Current — canonical Nightcap v1 launch target per ADR-0013 / D-071
> Canonical path: docs/story-bibles/nightcap-couch-race.md

**Working label only:** "Couch Race" is a planning label, not a committed product name. Naming is an open question in `docs/product/open-questions-log.csv`.

**Relationship to other bibles:** The killer-among-players experience previously described as Nightcap v1 is now the approved **Imposter Variant**, documented in `docs/story-bibles/nightcap-murder-mystery.md`. The interrogation capability defined here is shared platform infrastructure with `docs/story-bibles/daily-case.md`. World rules, content territory, and setting architecture are inherited from the Imposter Variant bible except where this bible overrides them.

---

## Section 1: What Nightcap Couch Race Is

Nightcap Couch Race is a social murder mystery race played in a living room: a TV carries the story, phones are private detective notebooks, and everyone on the couch is a rival investigator. The killer is never a player. The killer is one of the AI suspects on the screen, and the couch races to catch them.

The premise keeps Nightcap's DNA: a social gathering has been interrupted by a death. Everyone at that gathering had a reason to be there. One of them — an AI character — is responsible.

Each session is a complete, AI-generated case executed deterministically from a human-authored arc. No two cases are identical. A session runs 20 to 40 minutes, short enough that "one more case" is the natural end state of a game night.

**What stays constant across every session:**

- The setting is always a social gathering. The specific gathering varies.
- The story follows the six-beat Couch Race arc: The Pour, The Scene, The Grill, The Twist, Last Call, The Truth.
- The killer is always an AI suspect, resolved deterministically at session start. AI never decides or changes whodunit mid-session.
- Players are always investigators. No player is ever secretly a killer, victim, or conspirator.
- The genuine clue chain is always sufficient to solve the case (the balance principle).
- The narrator is always present: omniscient, aesthetic-linked, staged on the TV.
- The reveal always fires at the end, regardless of who solved it.

**What varies across every session:**

- The era, occasion type, and aesthetic of the gathering.
- The suspect cast: identities, personalities, relationships, secrets, and which of them is the killer.
- The murder: victim, method, motivation.
- The clue web, interrogation content, twist, and all narrative text and staging.
- Mini-game placement and content within their beat slots.

**Player promise:**

- You can be playing within a minute of sitting down. No roles to study, no acting required.
- You will never draw a role you don't want. Everyone plays the fun part: detective.
- The suspects remember what they told you — and what they told everyone else. Catching a lie feels earned.
- The race is always alive: wrong accusations sting but never eliminate you.
- Every case ends with the full truth, and another case is one tap away.

---

## Section 2: Strategic Role

Couch Race is the Nightcap v1 launch target (ADR-0013, D-071). It replaces the Imposter Variant as the first-launch experience because:

- **Faster validation loop.** A 20–40 minute session lets the founder run several cases per playtest evening instead of one.
- **Lower onboarding friction.** No role cards, no performance burden, no four-player floor. The floor drops to two players because suspects are AI.
- **Platform showcase.** Interrogating AI suspects whose answers are constrained by the knowledge graph makes Arcwright's headline primitive (D-034: cross-session and in-session narrative state) directly visible as gameplay. Contradiction-catching is provenance queries turned into points.
- **Shared capability.** The interrogation loop is the same capability Daily Case needs, so one build serves the v1 game and the second arc.
- **Differentiated lane.** Netflix's Knives Out party game occupies the killer-among-players lane with major IP; Jackbox and Death by AI ship authored or shallow-generative content. Nobody ships infinite, coherent, fair mysteries with suspects that hold knowledge state on a TV.

---

## Section 3: Setting and Suspect Cast Architecture

Setting architecture (era, occasion, aesthetic generation) is inherited from the Imposter Variant bible Section 2.

**The suspect cast** replaces the player character-slot architecture:

- Each case generates 4 to 6 AI suspects plus one victim (an AI character; the victim may appear in flashback staging but is not interrogatable in v1).
- Suspects are standard unified-model platform characters: identity, personality profile, goals, knowledge state, relationship graph. Exactly one holds the killer knowledge set.
- Every suspect has something to hide. Non-killer suspects carry secrets that produce evasive or misleading answers under interrogation — the red-herring engine. Lies must be falsifiable against the genuine evidence set.
- Suspect knowledge state is authored-generated at case resolution: who was where, who saw what, who is protecting whom, and what each suspect will lie about and why.
- Players hold light detective identities (name, flavor) for narrator address and scoreboard personality. These carry no hidden information and no role burden.

---

## Section 4: The Arc

Six execution beats, one compressed Story Circle. Beat count is arc-level (D-053); this arc is a new ArcDefinition, not an engine change.

**Beat 1: The Pour** | Structural function: establish the world and the death | Target: 3–5 minutes

Cold open on the TV: the gathering, the cast introduced with names and faces, and the death — staged as an animation-plus-audio sequence per D-070. Players receive detective identities on their phones. The beat ends with the narrator framing the race: first to the truth wins the night.

**Beat 2: The Scene** | Structural function: establish the investigative baseline | Target: 4–6 minutes

The crime scene opens. The first evidence wave lands: some group evidence on the TV, some private evidence per player phone. This beat is the primary slot for a competitive evidence mini-game (Crime Scene Smash slots here unchanged). Private evidence creates asymmetry: every player leaves the scene knowing something the couch does not.

**Beat 3: The Grill** | Structural function: the core loop — interrogation | Target: 8–12 minutes

Interrogation rounds (Section 6). Suspects take the stage on the TV one at a time or by player summons. The room hears every answer; the asker gets a private tell. The pacing engine watches engagement and tension, releasing evidence or narrator nudges when the case stalls.

**Beat 4: The Twist** | Structural function: recontextualization | Target: 3–5 minutes

A deterministic mid-case revelation lands: the alibi that collapses, the relationship no one declared, the second secret. The twist never changes whodunit; it reorders suspicion. A second evidence wave follows (Evidence Locker slots here). Early confident theories get punished; players who mined contradictions get paid.

**Beat 5: Last Call** | Structural function: convergence under pressure | Target: 4–6 minutes

A visible countdown starts. Final interrogation questions are scarce. Accusations lock in privately on phones. A first correct accusation immediately triggers the endgame for the whole table: everyone else gets one final chance to lock an answer before the reveal. No one sits out; no one is eliminated.

**Beat 6: The Truth** | Structural function: revelation and scoring | Target: 3–5 minutes

The reveal fires regardless of outcome (Section 8). Then scores, superlatives, and one prompt: another case?

Pacing targets follow the same tension-arc discipline as the Imposter Variant (rising through Beat 5, managed release in Beat 6), tuned for the compressed runtime.

---

## Section 5: The Narrator

The narrator carries over from the Imposter Variant bible Section 5 with its persona, brand voice, and behavior-trigger discipline intact. Couch Race adjustments:

- The narrator is also the **race master**: it frames rounds, announces evidence waves, marks the countdown, and stages the reveal. Scoreboard moments are narrator moments, in-fiction, never system-voiced.
- The narrator never confirms or denies a theory before The Truth, never names the killer early, and never reveals which suspect statements were lies.
- Player-addressable behavior (passive-player nudges) now targets players who have stopped asking questions or engaging with evidence.

---

## Section 6: The Interrogation System

The core mechanic. Interrogation is a platform capability (structured player questioning of AI characters with knowledge-gated answers) configured by this arc; Daily Case configures the same capability for solo asynchronous play.

**The round structure:**

1. A suspect takes the stage on the TV.
2. Each player privately selects a question on their phone from a generated intent menu: baseline intents (whereabouts, relationship to the victim, what they saw) plus unlocked intents derived from evidence that player holds. Question intents are deterministic menu selections in v1; free-text questioning is a deferred enhancement (open question).
3. Selected questions resolve in table order. The suspect answers aloud on the TV — voice and staging per D-070 — for the whole room.
4. The asker receives a private **tell** on their phone: a nervous detail, an inconsistency flag, a follow-up hook. Tells are part of the asymmetry economy.
5. Question tokens are scarce per beat. Spending them well is the strategy layer.

**Answer discipline (non-negotiable, engine-enforced):**

- Knowledge state queries run before every suspect answer (mandatory platform rule). A suspect can only reference what its character knows.
- Suspects lie only where the case resolution authorized a lie, and every authorized lie is falsifiable against the genuine evidence set.
- The engine records every answer as a claim with provenance: which suspect said what, to whom, in which round.

**Contradictions:**

When a suspect's answer conflicts with a prior claim or with evidence a player holds, that player can flag a contradiction from their phone. Contradiction detection is deterministic — claim ledger versus knowledge state and evidence, the same design spine as Daily Case's contradiction ledger. A confirmed catch scores points and stages a table moment on the TV: the suspect squirms. False flags cost a small penalty to keep spam out.

---

## Section 7: Clue and Contradiction Architecture

Clue architecture is inherited from the Imposter Variant bible Section 7 (delivery types: private, group, split, targeted; puzzle gating; distribution discipline) with these changes:

- **No killer interference.** There is no player-killer to plant false clues. Misdirection comes from suspect lies and authored red herrings resolved at case start. Every false signal is falsifiable.
- **Evidence unlocks interrogation intents.** A clue's value is not just information; it opens sharper questions. Split and private deliveries directly feed the race asymmetry.
- **Mini-games remain clue gates.** Crime Scene Smash (competitive, Beat 2) and Evidence Locker (solo, Beat 4) ride the existing puzzle-gated clue formats and their delayed-clue fallbacks unchanged.
- **The balance principle holds.** The genuine chain always suffices to solve the case with full engagement; redundancy is a design requirement; a stalled case degrades gracefully via pacing-engine evidence release, never dead-ends.

---

## Section 8: Scoring, Accusation, and the Reveal

**Scoring dimensions:**

- Evidence uncovered (individual finds, mini-game performance).
- Contradictions caught (confirmed catches; the marquee score).
- Accusation accuracy weighted by earliness (right and early beats right and late; wrong costs).

**Accusation rules:**

- Accusations are private phone submissions naming suspect, and optionally motive/method for bonus points.
- A wrong accusation applies a temporary lockout (cannot accuse again for a timed window) and a score penalty. No elimination, ever.
- The first correct accusation triggers Last Call table-wide: everyone else gets one final lock-in before the reveal.
- If the countdown expires with no correct accusation, the reveal still fires; the case wins.

**The Reveal (The Truth):**

The narrator delivers the full story in sequence: how and why the victim died, the killer's identity and how their lies held or broke, every genuine clue and what it pointed to, every lie and red herring and why it worked, each player's near-misses and best catches. Then the scoreboard: winner, superlatives (Best Interrogator, Lie Detector, Most Confidently Wrong), and the replay prompt.

The reveal is the trust contract: players must see the case was fair and solvable.

---

## Section 9: The Competition Dial

Per the configurable-composition principle, competition structure is arc configuration, not engine assumption:

- **Solo race (v1 ships this):** every player for themselves, with shared table moments (public answers, contradiction theater, group evidence).
- **Teams (deferred):** rival detective agencies; shared team evidence pools.
- **Co-op vs the clock (deferred):** the table against the countdown; contradiction catches extend time.

Deferred modes require approved specs before implementation.

---

## Section 10: World Rules and Content Territory

Inherited in full from the Imposter Variant bible Sections 10 and 11: same tone boundaries, same content territory, same safety posture (safety constraints enforced at the engine layer; arc configuration cannot bypass them). Death is staged with the same aesthetic discipline; the camera cuts away, the comedy is in the suspects, never in cruelty.

---

## Section 11: Relationship to the Imposter Variant

The Imposter Variant (killer-among-players) remains approved future scope, documented in `docs/story-bibles/nightcap-murder-mystery.md`. It shares this bible's setting architecture, narrator, clue formats, mini-games, and web experience layer. A group that loves Couch Race graduates to the Imposter Variant when they want to *be* the suspects. Sequencing for the variant is a post-proof roadmap decision.

---

## Section 12: Open Questions

Tracked in `docs/product/open-questions-log.csv`:

- Product name for Couch Race (working label only).
- Distribution channel strategy for launch (web link, Discord activity, TV app store later).
- Free-text interrogation timing (v1.x enhancement gated on intent-menu learnings).
- Victim interrogatability (séance/flashback mechanic) as a future twist mechanic.
