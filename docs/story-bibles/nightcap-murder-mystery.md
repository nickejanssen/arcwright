# Nightcap Murder Mystery Story Bible (Imposter Variant)

> Current version: v1.2
> Last updated: 2026-07-15
> Status: Current — approved future variant, not the v1 launch target
> Canonical path: docs/story-bibles/nightcap-murder-mystery.md

**Repositioning note (2026-07-15):** Per ADR-0013 and D-071, the Nightcap v1 launch target is now the Couch Race experience defined in `docs/story-bibles/nightcap-couch-race.md` (all players are investigators racing to solve a murder committed by an AI suspect). The killer-among-players experience described in this bible is renamed the **Imposter Variant** and remains approved future scope on the same platform infrastructure — setting architecture, narrator, clue formats, mini-games, and web experience layer are shared. Sections 2 (setting), 5 (narrator), 7 (clue architecture), 10 (world rules), and 11 (content territory) are inherited by the Couch Race bible by reference. Sequencing for this variant is a post-proof roadmap decision.

**Status:** Current v1.1 with Chat 9 schema, enterprise adaptation notes, and approved Nightcap Continuity v1.1 fast-follow scope applied | **Date:** 2026-06-13 | **Chat:** Chat 7 + Chat 9 integration + product review

**Design inspirations:** Murder Trivia Party (Jackbox) as format reference; ReBoot (animated series) game-descent mechanic as Arcwright platform philosophy.

---

## Chat 9 Integration Notes

Schema references in this Bible follow the platform-clean naming principle from D-038 and D-039: schema names describe structure, while game-specific semantics live in configuration. Relevant platform names include `bonded_entities`, `player_anchor_location`, `current_companion_entities`, `event_authorship`, `witness_entity_ids`, and `current_intent` where applicable. Nightcap may not exercise all fields.

Enterprise adaptations of Nightcap-style arcs are in scope per D-046. Future enterprise templates may derive from Nightcap structure with corporate-context content, while still running on the same Arcwright platform.

## Approved v1.1 Fast Follow: Nightcap Continuity

**Decision:** Nightcap Continuity is approved v1.1 fast-follow scope, not v1 MVP scope. The durable decision evidence is D-051 in `docs/product/decisions-log.csv` and ADR `docs/decisions/0006-nightcap-continuity-v11.md`. v1 proves the single-session party game. v1.1 adds cross-session group memory and a post-session recap artifact so Nightcap demonstrates the D-034 wedge: cross-session narrative state management with the knowledge graph as the headline primitive.

**Scope boundary:** This section is a v1.1 roadmap bookmark for future planning. It must not be treated as permission to add continuity schemas, APIs, consent flows, recap generation, storage, or UI to v1 implementation work without a dedicated v1.1 spec and normal approval.

**Problem statement:** A single Nightcap session can feel personalized, but it does not yet prove that Arcwright can remember a group over time. Continuity turns completed sessions into durable narrative state. It gives returning groups the feeling that the system remembers their table without requiring the v1 launch to carry consent, retention, and memory-product complexity.

**v1.1 scope:**

- Generate a post-session recap artifact after The Truth.
- Persist a group-level continuity record that can be used when the same host or group starts a later session.
- Store only narrative-relevant group memory, not raw chat or unnecessary personal detail.
- Give the host a clear way to reuse, ignore, or delete prior group memory for a future session.
- Use continuity as optional personalization input. The current session arc must still execute deterministically from the authored arc and current session state.

**Post-session recap artifact:**

- Session title or generated case name.
- Era and occasion theme.
- Final cast list, including killer, victim, major suspects, and optional Conspirator if active.
- Outcome: correct accusation, wrong accusation, killer survival, or exhausted accusations.
- Evidence chain summary: genuine clues, false clues, and what each pointed to.
- Memorable table moments suitable for players to reread after the game.
- Replay seed notes: hooks that could be referenced in a later Nightcap session without requiring continuity to alter canonical v1 arc structure.

**Group memory record:**

- Host or group identifier.
- Session IDs included in continuity.
- High-level play style signals, such as cautious investigators, aggressive accusers, social bluffing, puzzle focus, or roleplay-heavy table.
- Recurring group preferences, such as favored tone, pacing tolerance, clue density, and preferred themes.
- Prior session callbacks approved for reuse.
- Redacted or excluded items that must not be reused.

**Non-goals for v1.1:**

- No cross-session plot dependency. A new Nightcap case must remain playable by people who missed prior sessions.
- No raw transcript replay by default.
- No hidden permanent player profiling.
- No continuity requirement for first-time groups.
- No change to the v1 eight-beat Story Circle skeleton.

**Likely architecture touchpoints:**

- Knowledge graph: define which facts graduate from session-local knowledge into group memory.
- Session persistence: add post-completion summary generation and durable recap storage.
- Telemetry: track recap generation, continuity opt-in, reuse, deletion, and replay intent.
- Safety and privacy: classify recap contents before storage and define deletion behavior.
- API and SDK: expose recap retrieval and continuity selection at session creation.
- Nightcap experience layer: show recap after The Truth and let the host choose continuity behavior for a future session.

**Likely v1.1 task breakdown:**

1. Define `SessionRecap` and `GroupContinuityRecord` schemas.
2. Add recap generation after session completion.
3. Add consent and retention rules for continuity storage.
4. Add host controls for viewing, reusing, excluding, and deleting continuity.
5. Add continuity intake to session creation without making continuity required.
6. Add telemetry for recap and continuity usage.
7. Add tests for recap safety, deletion, reuse, and deterministic arc behavior.

**Acceptance criteria for v1.1 planning:**

- A completed session produces a recap artifact tied to the session.
- A host can start a new session with or without prior continuity.
- Continuity inputs can personalize generated content but cannot change canonical session state outside deterministic engine rules.
- Players are not surprised by durable storage of personal or group-specific details.
- Recap and continuity storage can be deleted or excluded.
- The implementation reinforces D-034 by making cross-session state visible and useful.

## Section 1: What Nightcap Is

Nightcap is a social murder mystery experience played in a physical space with a shared display and individual player devices. v1 requires a floor of four human players and scales up with additional human players. Two- and three-player sessions depend on interrogatable AI participants that can fill empty player slots, hold private knowledge state, and be the killer; that capability is deferred to v1.1. The narrator, NPC victim role, and non-participating background narration remain in v1. Each session is a complete, AI-generated story. No two sessions are identical.

The premise is always the same: a social gathering has been interrupted by a death. Everyone in the room had a reason to be there. One of them is responsible.

Players do not know who the killer is at the start of a session. The killer does not know they are the killer. At some point during the investigation, one player receives a private revelation on their device. From that moment, the session runs at two levels simultaneously: investigators working toward the truth, and a killer working to survive, misdirect, and win.

The session ends when the group makes a successful majority accusation, when the killer outlasts every accusation attempt, or when the pool of accusations is exhausted. The full story is revealed at the end regardless of outcome.

**What stays constant across every session:**

- The setting is always a social gathering. The specific gathering varies.
- The story always follows the eight-beat Story Circle structure: The Arrival, The Body, The Opening Move, The Dig, The Thread, The Reckoning, The Close, The Truth.
- The killer revelation always fires privately on the killer's device during beats 2 through 4.
- Each player holds exactly one accusation token for the full session.
- The target session duration is 30 to 75 minutes, governed by player pace and the pacing engine.
- The narrator is always present: omniscient, aesthetic-linked, player-addressable on the shared display.

**What varies across every session:**

- The era, occasion type, and aesthetic of the gathering.
- The specific characters generated into each role slot.
- Which player draws the killer role and which beat their revelation fires in.
- Which beat the murder occurs in (range: beats 1-3).
- The killer's prompted action opportunities for that session.
- The murder: victim, method, motivation.
- All clues, dialogue, plot structure, and story content.

**What Nightcap promises every player:**

- A story worth paying attention to.
- A role worth inhabiting.
- A reveal worth earning.
- An experience worth repeating.

---

## Section 2: Setting Architecture

Every Nightcap session takes place at a social gathering. This is not a crime scene investigation. It is not a procedural. It is a social event that has been interrupted by death, and the people who were already in the room must now reckon with what happened among themselves.

**The Social Gathering Constraint**

The setting is always a gathering: a deliberate assembly of people around a shared social occasion. The victim was part of that gathering. So was the killer. Everyone in the room had a reason to be there before anything went wrong.

A valid Nightcap setting is one where:

- The group assembled for a social reason.
- Every character slot has a plausible and specific reason to be present.
- The gathering creates social pressure for the group to stay and resolve what happened. This is social containment, not physical. Social obligation, shared investment, and the specific discomfort of being in the room where something terrible happened among people who know each other.
- The setting can plausibly accommodate a death that was not immediately obvious, explained away, or witnessed by everyone at once.

**What Is Fixed**

The social gathering constraint. The victim is always dead when the investigation begins (within beats 1-3). The narrator, two-surface model, beat structure, and accusation mechanics.

**What Is Variable**

Era and occasion type, selected by the host or randomized via Pick for Me. Together they define the aesthetic theme. Asset generation strategy: pre-produced per theme for the first production iteration. Runtime generation will be A/B tested against pre-produced in a future experiment to evaluate quality and experience difference.

**Asset Generation by Element**

| Element | Strategy (v1) |
| --- | --- |
| Background art, music, animations, UI chrome | Pre-produced per era/occasion theme |
| Character portraits | Generated at session start (before players join) |
| Setting name, gathering-specific flavor | Generative at session start |
| Character identities, backgrounds, motivations | Generative at runtime |
| Narrator dialogue | Generative at runtime, parameterized by tone config |

**Era and Occasion Options (current list)**

1920s Prohibition era, dinner party at a private estate. 1950s Hollywood, cocktail party at a studio executive's home. Contemporary, dinner party at a wealthy host's home. Victorian era, formal dinner at a manor house. Gilded Age, formal gathering at a mansion. Wild West, social event at a saloon or ranch. Circus or traveling show, gathering among performers and staff. Tech billionaire's dinner party (contemporary). Influencer retreat or brand activation event. Reality TV show set, between tapings. Y2K eve party, December 1999. Startup launch party, late 2000s. Bachelorette weekend at a rented estate. Music festival backstage. Additional options to be added as the slate develops.

Each entry is an art production engagement. Absurdist options have different asset requirements than period-realistic ones. Production scope for each must be named when art production is planned.

**v1 Launch Slate**

Nightcap v1 launches with two or three era/occasion themes selected from the existing list above. The remaining themes are post-proof content production, not v1 launch requirements.

**Physical Space**

Nightcap is designed for a room. Players may be seated at a table, on a couch, or moving freely through the space. No fixed arrangement is required. The phone is always with them. The shared display is not a continuous focal point.

The shared display earns every moment it asks for attention. It surfaces when the narrator has something to say, when a beat transition fires, when a group clue is released, when accusation mechanics require the full table, or when a voting/accusation result fires.

**Accusation and Voting Display**

When an accusation is made or a vote fires, the shared display transitions to a dedicated results moment: a group-facing, brand-toned visual reveal consistent with Nightcap's irreverent and slightly chaotic brand voice. This is a pre-produced UI element per aesthetic theme. It is one of the shared display's highest-value moments and is treated as a designed interaction.

**The Containment Principle**

Players stay not because they cannot leave but because they do not want to. Social obligation keeps them in the room at the start. Curiosity and competition keep them engaged through the middle. The approaching reveal keeps them present at the end.

---

## Section 3: Character Slot Architecture

Nightcap does not have fixed characters. It has fixed roles. Each session generates a complete cast from scratch, but every character occupies a typed slot that defines their structural function: what information they hold, what social position they occupy, and what they contribute to the mystery's tension.

The role is permanent. The character is not.

**The Two Configurations**

Four-slot (4 human players): the complete v1 core experience. Nothing is missing or simplified. Six-slot (5+ human players): adds two expansion slots that deepen the clue web and increase social complexity. Empty participant slots are not filled by interrogatable AI participants in v1. AI-controlled participant slots that hold information states, cover stories, respond dynamically, and can be the killer are deferred to v1.1.

**The Six Role Types**

These are the founding set. Role types are first-class platform objects in an extensible library. New role types can be added without changing the arc schema.

- **The Intimate** (core): Closest to the victim. Holds the deepest personal knowledge. Highest emotional stakes. Hardest to accuse.
- **The Deflector** (core): Visibly hiding something unrelated to the murder. The misdirection engine. Investigators spend significant attention here before determining relevance.
- **The Observer** (core): Positioned at the social edges. Sees what others are too involved to notice. Holds structural clues. The wildcard.
- **The Obvious Suspect** (core): Surface-level motive everyone recognizes. Creates the false trail the killer benefits from. If actually the killer, the reveal is earned.
- **The Loose Cannon** (6-slot expansion): Unpredictable, high-energy. Creates social chaos that simultaneously conceals and reveals.
- **The Catalyst** (6-slot expansion): Their presence or past action set something in motion before the session began. They may not know this.

**Killer Assignment**

Killer assignment is a two-event system:

*Assignment:* In v1, the engine internally determines which player is the killer through constrained-random assignment behind the existing assignment interface. No slot is reserved for the killer and no slot is immune from assignment. Mini-game behavioral inputs are captured in schema in v1 but are not wired into killer assignment until v1.1.

*Revelation:* Fires privately on the killer's device at the assigned beat (range: beats 2-4). The revelation delivers: role disclosure, the killer's prompted action opportunities for this session, and the victim designation prompt.

No slot is reserved for the killer. No slot is immune from the assignment.

**Victim Slot (7th structural position)**

The victim is a dedicated structural position, separate from the six role types. The victim is never a playable investigative role.

*Eligibility:* In v1, the NPC victim role is retained and the victim remains a dedicated structural position separate from playable investigative roles. Human victim eligibility begins at the four-human-player floor. Two- and three-player support depends on v1.1 interrogatable AI participants and is not part of v1.

*Designation:* The killer designates the victim at the moment of revelation, selecting from available characters. The engine may constrain choices to narratively valid options.

*Victim role pool:* Every victim draws a role from the pool below. The role is variable per session. The Conspirator role is conditional (fires only if the story benefits from it).

| Victim Role | Description |
| --- | --- |
| The Witness | Releases one cryptic clue per beat through the narrator, drawn from what their character observed before dying |
| The Specter | Observes all private information that surfaces after their death; cannot communicate directly |
| The Informant | Secretly paired with one investigator; can send limited private messages through their device |
| The Conspirator | Carries a story-generated obligation to protect something in the gathering. Default state: accidental complicity driven by targeted engine-delivered cues. Can transition to direct complicity if the player guesses the killer correctly on their device; if correct, a runtime-generated message gives their character a specific story reason to protect that person. Conditional: only fires if story benefits from it. |

All victim roles keep the player engaged for the full session. All victim roles learn the killer's identity at Beat 8 with everyone else.

**How Generated Characters Differ: Killer vs. Investigator**

Every character has the same visible profile: name, background, relationship to victim, personality, surface motivation. The killer's profile includes an additional private layer delivered at revelation: a constructed alibi, a specific version of events, and behavioral posture calibrated to deflect without overexplaining.

**Additional Kills in Larger Sessions**

In six-slot sessions, the killer may have the opportunity to kill one additional player. Not guaranteed. Availability is proportionate to remaining investigators and remaining beats. The engine enforces a floor: no additional kill fires if it would leave the pool unable to form a majority accusation. Additional kill opportunities can expand dynamically under specific story conditions (killer survived an accusation, investigation accelerating rapidly). The story governs the mechanic.

---

## Section 4: The Arc

The arc is the complete Story Circle, instantiated as eight execution beats. Each beat corresponds to one Story Circle step. The beats are the engine's technical containers. The Story Circle is the narrative experience those beats produce.

Every Nightcap session tells a different story in the same shape.

**Beat 1: The Arrival** | Story Circle Step 1: You | Structural function: establish comfort and order

The gathering is in full swing. Characters are in their element. No one knows anything is wrong yet. Players receive their character cards privately. The room has the energy of any social gathering before it goes wrong.

Beat 1 is one possible position for mini-games, but mini-game placement is flexible across the arc: games may appear at any beat, run as session-spanning layers, or serve as the primary structure through which the mystery unfolds. When mini-games appear in this beat, players engage in aesthetic-themed activities delivered to their phones, optionally mirrored on the shared display. These games are framed as part of the gathering itself. In v1, mini-games are timed, puzzle-gated interactions that gate clue access, drive competition, and create investigative leads across beats. They capture behavioral-read output in schema but do not feed killer assignment until v1.1. The murder may occur during this beat.

The pacing engine is observing but not intervening.

**Beat 2: The Body** | Story Circle Step 2: Need | Structural function: surface the disruption, establish stakes

Something is wrong. The murder is discovered or revealed, or in some sessions, occurs during this beat. The need is established. Players understand they are investigators, or believe they are. The killer revelation window opens.

The murder event occurs somewhere within beats 1 through 3. In sessions where it occurs in Beat 2, the discovery and the event are simultaneous or nearly so. In sessions where it occurred in Beat 1, Beat 2 is the moment the room realizes what happened.

**Beat 3: The Opening Move** | Story Circle Step 3: Go | Structural function: enter the unfamiliar

Investigation formally begins. Private clues surface on individual devices. Group clues surface on the shared display. Characters begin interacting through the lens of the investigation. In sessions where the murder occurs in Beat 3, something happens to someone during the earliest moments of investigation, recontextualizing everything that came before.

The killer revelation window remains open. The pacing engine monitors clue engagement and inter-player interaction.

**Beat 4: The Dig** | Story Circle Step 4: Search | Structural function: adapt and investigate

The investigation is active. Players are cross-referencing clues, forming theories, probing characters. The longest beat. Red herrings and misdirection are most active here.

The killer revelation window closes at the end of this beat. The revealed killer begins their strategic pivot: they know the investigation state, what clues are in play, and who suspects whom. The pivot is not dread. It is advantage recognized.

Pacing engine tension target: 0.6 by beat's close.

**Beat 5: The Thread** | Story Circle Step 5: Find | Structural function: first convergence

A significant discovery lands. A connection that recontextualizes what the group already knew. Not the final answer, but the shape of the answer becoming visible. First informal accusation energy. The killer actively manages the strategic implications of what is being discovered.

Pacing engine tension target: 0.7.

**Beat 6: The Reckoning** | Story Circle Step 6: Take | Structural function: confrontation and cost

Accusation tokens activate. Evidence is presented and argued. Wrong accusation events fire here: the accuser's token is burned, their standing drops, the wrongly accused is cleared, the killer gets a narrative reprieve. The killer's prompted action opportunities are most critical in this beat. Additional kill events may fire in six-slot sessions.

Pacing engine tension target: 0.85.

**Beat 7: The Close** | Story Circle Step 7: Return | Structural function: convergence and commitment

Remaining tokens are committed. The group must converge on a final answer. The killer win condition by attrition becomes visible if the investigator token pool is running low.

Pacing engine tension target: 0.95.

**Beat 8: The Truth** | Story Circle Step 8: Change | Structural function: revelation and change

The accusation fires. The truth surfaces regardless of outcome. The narrator delivers the full story. The experience ends with one prompt: play again?

Pacing engine manages a downward tension trajectory: from peak to approximately 0.2 as the truth lands. The only beat where the engine actively manages tension release rather than accumulation.

---

## Section 5: The Narrator

The narrator is Nightcap's host intelligence. It is not a character in the story. It is the intelligence that holds the story together: the voice that establishes the world, manages the experience, and keeps the session moving without players ever feeling managed.

The narrator is omniscient. It knows the full session state at all times. It uses this knowledge to create conditions in which players play the story themselves, not to play the story for them.

**Persona and Voice**

The narrator's persona shifts with the session aesthetic. Era and occasion type change vocabulary, register, and tone. What does not shift is the brand voice underneath: witty without being smug, suspenseful without being portentous, irreverent without undercutting genuine stakes. The narrator takes the story seriously. It does not take itself seriously.

**Behavior Triggers**

- *Beat transition:* Marks every beat transition on the shared display. Language shifts to match the incoming beat's dramatic purpose.
- *Clue release:* Frames every clue delivery. Private clues go directly to the device. Group clues are announced with enough context to feel like discoveries.
- *Tension threshold:* When the pacing engine reports stalling or low tension, the narrator intervenes in-story: new information, a character observation, a narrative nudge. The pacing engine is invisible.
- *Player inaction:* Addresses passive players directly, in-story, on their device or through a shared display moment involving their character.
- *Accusation and vote events:* Shared display transitions to a dedicated brand-toned results moment.
- *Mini-game transitions:* Narrator frames mini-games as part of the gathering itself, in a lighter social register that signals something to attentive players.
- *Killer revelation:* Entirely private. No shared display acknowledgment. The narrator's public behavior does not change.
- *Victim revelation:* Narrator acknowledges death in-story, consistent with aesthetic. Victim player's new role is never visible to others.

**What the Narrator Never Does**

Names the killer before Beat 8. Confirms or denies an accusation before the reveal. Breaks the fiction to give instructions. Speaks in system terms. Acknowledges the beat structure, pacing engine, or underlying mechanics.

---

## Section 6: Imposter Mode Dynamics

Every Nightcap session runs on two tracks simultaneously. Investigators are trying to find the truth. The killer is trying to survive long enough that the truth cannot be found.

**The Investigator Experience**

Investigators begin in good faith. They have a character, private clues, and a gathering full of people who may or may not be telling the truth. What makes the experience work is not the puzzle. It is the social pressure. Every person at the table is a potential liar. Every piece of information has a source whose motives are unknown. The Deflector is hiding something real. The Obvious Suspect looks guilty for a reason. And somewhere in the group, there may be a dead player whose loyalty is now unknown.

Investigators do not know which victim role has been drawn in their session. They do not know if the victim player is a neutral ghost or an active Conspirator. That uncertainty is a feature.

**The Killer Experience**

The killer begins the session not knowing what they are. They investigate alongside everyone else in good faith, because at that point, it is good faith.

At some point between beats 2 and 4, their device delivers a private revelation. The message recontextualizes everything. The killer wakes up ahead: they know what the investigators know, what clues have surfaced, who suspects whom. The revelation is not dread. It is advantage recognized. The strategic pivot from investigator to concealer is the moment the game changes gear. The killer who is having fun is the one who immediately starts thinking about how to use what they know.

**Killer Action Opportunities**

The killer does not track a resource pool or manage an inventory of abilities. The engine identifies when a story moment makes an action narratively appropriate and presents it as an optional prompt on the killer's device. The killer accepts or declines. The story continues either way.

The arc definition contains a set of action types available to the killer in this session. The specific configuration varies per session, contributing to replayability. Players never know which configuration the killer holds.

**Victim Designation**

Included in the revelation is the option to designate the victim. The killer selects from available characters within the engine's narrative constraints. The designation is private. The murder event is announced by the narrator in-story. The victim player receives their own private revelation: their victim role assignment.

**Win Conditions**

- Investigators win: majority accusation correctly identifies the killer before the token pool is exhausted.
- Killer wins: accusation token pool is exhausted without a correct majority, OR (in six-slot sessions) enough investigators are eliminated that majority accusation is mathematically impossible.
- The reveal fires regardless of outcome.

**The Accusation System**

Each player holds one accusation token for the full session. Tokens cannot be recovered. When a majority of players have directed their token at the same person, the reveal fires.

Wrong accusation consequences: the accuser's token is burned, their standing drops, the wrongly accused is cleared for the remainder, the killer gets a narrative reprieve, and the investigation continues with a depleted pool.

**The Standing System**

Standing is the room's credibility toward a player's character. Wrong accusations cost standing. Low standing shifts the narrator's treatment of that player: their testimony is framed with skepticism, their character treated as less reliable. Communicated through narrative behavior, not a visible score.

**The Balance Principle**

The session must remain genuinely winnable for both sides at all times. The genuine clue chain is always sufficient to solve the case with full investigator engagement. Killer action opportunities are throttled against the session's current balance state. False clues are always falsifiable given the complete set of genuine evidence. Neither side coasts.

---

## Section 7: Clue Architecture

A clue is a discrete piece of information with a defined delivery target, a delivery trigger, and a truth value. It is either genuine (part of the real evidence chain) or false (planted by the killer). Players cannot determine which from the clue alone.

**Delivery Types**

- *Private:* One player's device. Invisible to everyone else. The receiving player decides what to do with it.
- *Group:* Shared display. Visible to the full table simultaneously.
- *Split:* Part on the shared display, part delivered privately to one player. One person in the room holds more than the room knows.
- *Targeted multi-player:* Delivered to a defined subset of players, not the full group.

Any delivery type can be puzzle-gated. The puzzle determines access, not content or recipient.

Mini-games in v1 ride on these existing puzzle-gated clue formats as a cross-beat interaction layer. They are not opening-only content; they can appear wherever a beat calls for timed competitive clue-cracking or collaborative clue access.

**Puzzle Formats**

- *Individual puzzle:* One player solves it alone on their phone.
- *Collaborative puzzle:* Pieces distributed across multiple phones. Players coordinate to assemble. Highest-value interference target.
- *Group puzzle:* Displayed on the shared screen. Full table can see and contribute.

Puzzle type varies by clue and beat. Puzzles can be interfered with by the killer and (in applicable sessions) the Conspirator.

**Killer and Conspirator Interference**

Neither the killer nor the Conspirator tracks resources. The engine surfaces interference options as story-prompted optional actions.

- *False answer submission:* In a collaborative puzzle, submit a false answer corrupting one piece. The assembled clue is distorted or misleading.
- *Private clue redirect:* Intercept a private clue before it reaches its intended recipient. The intended player receives nothing or a placeholder.
- *False clue plant:* Introduce a false clue through a legitimate delivery channel, indistinguishable from genuine at delivery.

**Truth Value and the Reveal**

Every clue has a truth value not visible during the session. At Beat 8, the narrator accounts for all clues: genuine and false, what was real, what was planted, and why the false clues worked. The reveal is the full picture, not just the killer's identity.

**Clue Distribution Across the Arc**

- *Early beats (1-3):* Character-establishing clues. Predominantly private and direct. Establish the investigative baseline.
- *Mid-arc beats (4-5):* Evidential clues. More likely puzzle-gated and targeted. False clues most effective here.
- *Late beats (6-7):* Synthesis clues. Tend toward group or split delivery. Create shared reckoning before commitment.

**The Balance Principle**

The clue web is always sufficient for investigators to solve the case with full engagement. Redundancy is a design requirement. Interference opportunity throttling ensures the investigation remains recoverable. False clues are always falsifiable given the complete genuine evidence set.

---

## Section 8: The Reveal

The reveal is Beat 8: The Truth. It fires regardless of outcome.

**What the Reveal Contains**

The narrator delivers the full story in sequence: the victim's death (how and why, in session-specific terms), the killer's identity and occupied role, the alibi they maintained and how it held or broke, every genuine clue and what it pointed to, every false clue and how it was constructed, the Conspirator's role if active, victim roles held by dead players, the accusation history and its consequences.

Nothing in the session's information architecture is left unaccounted for.

**What Makes a Reveal Land**

A reveal lands when players feel the answer was always there and they had a real chance to find it. Retroactive coherence: looking back at the session and seeing how the clues connected, how the killer's behavior fits the story they were telling, why the false trails were effective.

A reveal fails when the outcome feels arbitrary, the evidence chain was too thin, the killer's win felt like luck rather than strategy, or investigators who engaged fully had no real path to the answer.

**Outcome Variants**

- Correct majority accusation: investigators found the killer. Narrator confirms and delivers the full story.
- Wrong accusation exhausting the token pool: narrator reveals the killer, explains how they managed the investigation.
- Killer win by attrition (larger sessions): narrator delivers the reveal including the arc of additional kills.

All outcomes end with one prompt: play again?

**Narrator Voice at Beat 8**

The narrator shifts tone. Still sharp, still Nightcap-voiced. The reveal lands with genuine weight. The humor, where it appears, comes from the specificity of the situation: the exact cover story, the particular way a false clue was constructed, the specific misdirection that worked. The narrator has known everything since before the session began. Beat 8 is the moment it closes the distance entirely.

---

## Section 9: One Fully Realized Example Session

*Reference implementation only. All details are illustrative of generative engine output. Nothing here is authored or locked.*

**Setting:** A private estate outside Chicago, 1923. A small gathering of associates, old friends, and inconvenient acquaintances for a dinner that was already tense before someone turned up dead. Six-slot session.

**The Cast (illustrative generated output)**

- *Slot 1, The Intimate:* The victim's business partner and closest confidante for fifteen years. Knows the finances, the secrets, the name of the person the victim trusted most. Arrived planning to resolve a disagreement that had been building for months.
- *Slot 2, The Deflector:* A man with a federal connection nobody is supposed to know about. His presence at a bootlegger's dinner party is itself the thing he is hiding.
- *Slot 3, The Observer:* A jazz musician who has played the estate's private parties for two years. Invisible to the social hierarchy. Has heard things from the corners of rooms.
- *Slot 4, The Obvious Suspect:* The victim's estranged nephew, present because he was in the will and everyone knows it. Visible motive. The most conspicuous alibi in the room.
- *Slot 5, The Loose Cannon:* A showgirl from the city who arrived with the Obvious Suspect. Has been drinking since before dinner. Says things she should not say at a volume she should not.
- *Slot 6, The Catalyst:* A lawyer who drafted the victim's most recent will amendment, signed three weeks ago. Came at the victim's personal request. Is the reason the stakes changed.
- *The Victim (NPC, 7th slot):* The estate's owner. Found in his study between courses. Method not immediately obvious. Room locked from the inside.

**The Murder (illustrative engine output)**

The victim was poisoned: a substance introduced to his private decanter before dinner, designed to take effect slowly and mimic a cardiac episode. Method surfaces through investigation, not announcement. The locked room is misdirection: the window latch was broken before tonight.

**One Illustrative Clue Per Slot**

- *The Intimate (private, Beat 3):* A handwritten note in the victim's correspondence, two weeks old, referencing a meeting that was never supposed to happen and a name she recognizes.
- *The Deflector (split, Beat 4):* His initials on a ledger page surfaced on the shared display. What column they appear in is delivered privately to one other player.
- *The Observer (private, Beat 3):* Overheard a specific conversation through the study door three nights ago. Its content recontextualizes the victim's behavior at dinner.
- *The Obvious Suspect (group, Beat 2):* The will amendment is read aloud by the lawyer. The nephew's share increased significantly. Everyone hears it simultaneously.
- *The Loose Cannon (collaborative puzzle, Beat 4):* She has half a torn photograph. Another player has the other half. Neither knows. Assembled on the shared display, it places two people at a location neither has mentioned.
- *The Catalyst (private, Beat 5):* He received a message at the estate this evening before dinner, not yet mentioned. The victim sent it four hours before dying.

**The Eight Beats: Skeleton**

1. *The Arrival:* Players receive character cards. Mini-game (Prohibition-era bluffing game) surfaces on shared display. Engine observes. Killer not yet assigned.
2. *The Body:* Between courses, the host is found. Lawyer reads the will amendment at the Obvious Suspect's insistence. Group clue lands. Killer revelation window opens.
3. *The Opening Move:* Investigation begins. Observer and Intimate receive first private clues. Loose Cannon says something she should not. Killer revelation fires for one player.
4. *The Dig:* Ledger page surfaces on shared display. Collaborative photograph puzzle becomes available. Killer revelation window closes. Killer now manages the investigation state.
5. *The Thread:* Photograph pieces assembled. Catalyst's private message surfaces to one player. The shape of the answer becomes visible.
6. *The Reckoning:* Accusation tokens activate. Obvious Suspect accused by two players, reaches majority. Wrong answer: cleared. Accusers lose standing. Killer receives interference prompt.
7. *The Close:* Remaining tokens converge. Correct accusation assembles.
8. *The Truth:* The Intimate was the killer. Financial exposure in the victim's concealed liability would have destroyed her if the amended will was executed. The Catalyst's message told her what the victim had done. She arrived to resolve it. She resolved it differently.

---

## Section 10: World Rules

**What Is Always True**

- The setting is always a social gathering.
- The story always follows the eight-beat Story Circle structure.
- There is always exactly one initial killer per session.
- The killer never knows they are the killer at session start.
- The revelation always fires privately between beats 2 and 4.
- The killer always designates the victim at the moment of revelation.
- Each player holds exactly one accusation token for the full session.
- The murder always occurs within beats 1 through 3.
- The full story always surfaces at Beat 8 regardless of outcome.
- The narrator is always present, omniscient, and never names the killer before Beat 8.
- The clue web is always sufficient for investigators to solve the case with full engagement.
- The shared display is never a continuous focal point.

**What Varies Per Session**

Era and occasion type. Generated characters in each slot. Which player draws the killer role. Which beat the revelation fires in. Which beat the murder occurs in. Killer action opportunity configuration. The murder: victim, method, motivation. All clues, dialogue, story content. Whether a Conspirator role is active. Mini-game content, outputs, and arc position. Whether additional kills occur in six-slot sessions. Victim role drawn from the pool.

**What the Engine Enforces**

Beat sequence and transition conditions. Killer revelation timing window. Accusation mechanics (token state, standing scores, majority threshold, wrong accusation consequences, killer win condition by attrition). The balance principle. Killer assignment logic. Victim eligibility by player count. Additional kill proportionality. Two-surface delivery (private information never appears on the shared display). Role type library validation.

**What Is Generated, Not Authored (Nightcap-Specific)**

Every specific story element in Nightcap is generated, not written in advance. The arc definition provides rules, constraints, and structural scaffolding. The engine and its generative layer produce the content within those constraints for each session.

This is a design decision specific to Nightcap. The Arcwright platform supports authored, generative, and hybrid content strategies across arcs. What Nightcap chose for itself is not what the platform requires of every experience built on it.

---

## Section 11: Content Territory

**What Nightcap Is**

Nightcap is a murder mystery. Death is the premise. Within that frame, Nightcap's tone is irreverent, witty, suspenseful, darkly comedic, and mildly unhinged. It does not take itself too seriously. It takes the story seriously.

Reference set: Guy Ritchie's Sherlock Holmes, Wes Anderson's ensemble films, Glass Onion, Jackbox Murder Trivia Party (format reference, not creative ceiling), The Amazing Digital Circus, Rick and Morty, The League.

**What Is In Bounds**

Murder as premise and investigation subject. Violence that is implied, discovered, or reconstructed through evidence. Morally complex motivations: greed, jealousy, self-protection, betrayal, ambition, desperation. Dark comedy. Absurdist character behavior. Social satire. Eccentric personalities. Embarrassing or professionally damaging secrets. Messy, dishonest, or mutually destructive relationships. Period-appropriate social context informing character generation without being the story's subject.

**What Is Out of Bounds**

Graphic violence. The method of death is discoverable through investigation, never depicted. Gore, physical suffering, or detailed descriptions of how the killing was executed are not generated.

Sexual content of any kind.

Content targeting real people, living or dead.

Content designed to trigger anxiety, distress, or trauma responses. Tension is investigative and social, not psychological horror directed at players.

Hate speech, slurs, or content that demeans people based on identity.

Content involving minors in any harmful context.

**How Dark It Goes and Where It Stops**

Nightcap goes dark in the way a sharp ensemble film goes dark: the situation is genuinely bad, someone is dead, the people in the room are worse than they appear. The comedy comes from the specificity of the awfulness.

Floor: the experience never produces content a reasonable person would find distressing rather than entertaining. Ceiling: enough real edge that stakes feel genuine. The space between is Nightcap's operating range.

The death is taken seriously by the characters and the story. The characters are not taken too seriously by the narrator. Players are never made to feel threatened or unsafe. They are made to feel clever, suspicious, entertained, and invested.

**How the Brand Voice Governs Generation**

Every generative output passes through the tone configuration in the arc definition. The brand envelope defines the range. Scenario dials position each session within that range. The voice directive carries the reference set synthesis as a generative instruction. The content territory is the outer wall. The tone configuration is the interior design. Both govern every session.
