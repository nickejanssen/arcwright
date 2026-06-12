# Bundle C narrative
Generated: 2026-06-12

Manifest:
- docs/07-Story-Bible-Murder-Mystery-v1 361b7de354a8817a99ece1b701763f06.md
- docs/09-Story-Bible-Monster-RPG-v1 0 365b7de354a881e08dd5d43e2ab2edb5.md
- docs/Accusation and voting display design what does the 362b7de354a88173af1cf04bbdcfd7cd.md
- docs/Arc structure graph with branching, convergence, m 35ab7de354a881f0a898f1ae967223df.md
- docs/Conspirator guess mechanic what is the UX on the k 362b7de354a881698521cb619acdf9af.md
- docs/D-001 Monster RPG single-player at MVP Multiplayer 364b7de354a881a8bf9ad544fb392233.md
- docs/D-003 Monster RPG world runs in story-time, not re 364b7de354a88124bd3cff63795a9581.md
- docs/D-012 No omniscient narrator in Monster RPG Dialog 364b7de354a881c0aba0c9e6a019f722.md
- docs/D-013 Creatures and NPCs age over story-time; play 364b7de354a881dda1f7efe4dbd946a6.md
- docs/D-023 NPC memory narrative-meaningful events only, 364b7de354a881bc9423fea6bd911dfa.md
- docs/D-029 Monster RPG Story Bible structured as 12 cha 364b7de354a881a1bcfbdd86bcd4bedb.md
- docs/D-030 Monster RPG player-facing term is 'chapter,' 364b7de354a8811e878ec31ef0c50a17.md
- docs/D-035 Visual Storyworld staged roadmap 366b7de354a8812e8699ea2cae9a8d5f.md
- docs/D-045 narrative_momentum_score scope at MVP 366b7de354a8818ba75fd27cef776208.md
- docs/Fully generative story content is a Nightcap-speci 361b7de354a881acac91c863ab4876c6.md
- docs/Killer active capabilities are story-prompted opti 361b7de354a8814ba5b5f98f767eb312.md
- docs/Killer assignment behavioral signal specification  362b7de354a8811caa65f1fa3c85e5fb.md
- docs/Killer revelation is mid-session, variable between 361b7de354a881dd8f09f1fa4cfa57b1.md
- docs/Murder timing is variable across beats 1-3 Mini-ga 361b7de354a881fea286e3539f89f859.md
- docs/Nightcap aesthetic mode generative The visual and  360b7de354a88142af3cfa707c5861d6.md
- docs/Nightcap arc structure Dan Harmon Story Circle Arc 360b7de354a881a18d5dd1a4a63d7944.md
- docs/Nightcap character mode generated Characters are g 360b7de354a881118a47e9b3cb227460.md
- docs/Nightcap era and occasion list finalization which  362b7de354a881b3abdcf4f5e7af4484.md
- docs/Nightcap narrator host persona on shared display V 360b7de354a881d0b7a7cb4d59a0ce9f.md
- docs/Nightcap play mode at MVP imposter One player is a 360b7de354a881519ececc3e05ddd174.md
- docs/Nightcap rendering layer specification how does Ni 362b7de354a8813fba0cd8796c407915.md
- docs/Nightcap setting constraint social gathering The p 360b7de354a881348916cb26de1baeef.md
- docs/Nightcap uses 8 execution beats in 1 1 Story Circl 361b7de354a881609cecfae20230cc67.md
- docs/Q-115 Monster RPG Story Bible v1 0 finalization 365b7de354a881b68978e0544ef171d8.md
- docs/Q-115 What is the final v1 0 of the Monster RPG St 365b7de354a8815c9761c253345257b8.md
- docs/Should NPC actions in Nightcap be exclusively rout 363b7de354a881e79bb0cfa7a4b35356.md
- docs/Should NPC tool availability be gated by narrative 363b7de354a8817a8224cb985a470593.md
- docs/Story Circle is a functional platform-native 8-bea 361b7de354a88108aec9cf3340ff45aa.md
- docs/Victim is a dedicated 7th structural position Kill 361b7de354a881b58fd2d476f3e60b12.md
- docs/What are Arcwright's narrative quality metrics for 363b7de354a881cb9552f5f14d92ec69.md

---
## SOURCE FILE: docs/07-Story-Bible-Murder-Mystery-v1 361b7de354a8817a99ece1b701763f06.md

# 07-Story-Bible-Murder-Mystery-v1

**Status:** Draft v1 with Chat 9 schema and enterprise adaptation notes applied | **Date:** 2026-05-19 | **Chat:** Chat 7 + Chat 9 integration

**Design inspirations:** Murder Trivia Party (Jackbox) as format reference; ReBoot (animated series) game-descent mechanic as Arcwright platform philosophy.

---

## Chat 9 Integration Notes

Schema references in this Bible follow the platform-clean naming principle from D-038 and D-039: schema names describe structure, while game-specific semantics live in configuration. Relevant platform names include `bonded_entities`, `player_anchor_location`, `current_companion_entities`, `event_authorship`, `witness_entity_ids`, and `current_intent` where applicable. Nightcap may not exercise all fields.

Enterprise adaptations of Nightcap-style arcs are in scope per D-046. Future enterprise templates may derive from Nightcap structure with corporate-context content, while still running on the same Arcwright platform.

## Section 1: What Nightcap Is

Nightcap is a social murder mystery experience for 2 to 8 players, played in a physical space with a shared display and individual player devices. Each session is a complete, AI-generated story. No two sessions are identical.

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

Four-slot (2-4 players): the complete core experience. Nothing is missing or simplified. Six-slot (5-8 players): adds two expansion slots that deepen the clue web and increase social complexity. Empty slots are filled by AI-controlled NPC participants who hold information states, cover stories, and respond dynamically when players interact with them.

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

*Assignment:* The engine internally determines which player is the killer. Can happen anywhere from session start to immediately before the revelation beat. The engine observes player behavior passively across early beats and evaluates candidates based on narrative fit and social dynamics. Specific interaction triggers (including mini-game outputs) can accelerate or influence the decision.

*Revelation:* Fires privately on the killer's device at the assigned beat (range: beats 2-4). The revelation delivers: role disclosure, the killer's prompted action opportunities for this session, and the victim designation prompt.

No slot is reserved for the killer. No slot is immune from the assignment.

**Victim Slot (7th structural position)**

The victim is a dedicated structural position, separate from the six role types. The victim is never a playable investigative role.

*Eligibility:* With three or fewer human players, NPCs fill the victim slot. With four or more human players, a human player can be the victim. The engine determines eligibility by player count.

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

Before or alongside the social dynamics, players may engage in aesthetic-themed mini-games delivered to their phones, optionally mirrored on the shared display. These games are framed as part of the gathering itself. They generate behavioral and response data that feeds the killer assignment logic, though players have no visibility into this function. Whether game data drives the assignment or not varies per session. The murder may occur during this beat.

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

Era and occasion type. Generated characters in each slot. Which player draws the killer role. Which beat the revelation fires in. Which beat the murder occurs in. Killer action opportunity configuration. The murder: victim, method, motivation. All clues, dialogue, story content. Whether a Conspirator role is active. Mini-game content and outputs. Whether additional kills occur in six-slot sessions. Victim role drawn from the pool.

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

---
## SOURCE FILE: docs/09-Story-Bible-Monster-RPG-v1 0 365b7de354a881e08dd5d43e2ab2edb5.md

# 09-Story-Bible-Monster-RPG-v1.0

> **STATUS, v1.0.** Finalized after Chat 9 (Platform-as-Product Strategy).
> 

> 
> 

> The design decisions in this document are committed: Decisions Log D-001 through D-030 (Chat 8) plus D-031 through D-047 (Chat 9). Chat 9 resolved: platform-as-product story (Q-113), game-agnostic schema naming pass (Q-114), MVP scope discipline pass on four overthought items via the schema-clean implementation-staged pattern (Q-114; see D-042 through D-045), and v1.0 finalization itself (Q-115).
> 

> 
> 

> Linked open questions still pending (not blocking v1.0): Q-101 (working name), Q-102 (gym leader equivalent vocabulary), Q-103 (other Pokemon-genre vocabulary), Q-104 (career paths), Q-105 (creature species), Q-106 (world setting), Q-107 (multiplayer roadmap), Q-112 (visual signature).
> 

> 
> 

> Linked decisions: D-001 through D-030 (Chat 8) and D-031 through D-047 (Chat 9). See Decisions Log for full rationales.
> 

# Chapter 1: What the Game Is

*Cross-reference: Nightcap §1 is the equivalent identity chapter. Both define the game's identity. Every specific claim differs because the games differ. The platform handles both natively because identity is configuration, not architecture.*

## Identity

The Monster RPG is a single-player narrative RPG of autonomous choice, set in a persistent world that runs in story-time. The player lives a life one session at a time. The world generates new events, encounters, and locations in response to how the player plays. Creatures with their own agency choose to walk alongside the player, witnessing the choices the player makes and becoming uniquely shaped by what they witness.

There is no single fixed story to complete. The player builds a life by deciding what to pursue, who to learn from, what career paths to try, and how to treat the world and its creatures. The story is the life. Sessions end at narrative-meaningful moments and leave threads pulling forward.

## Terminology note: session vs chapter

'Session' is platform/technical terminology used throughout this Bible and the Tech Architecture. It refers to a single load-and-play period.

The player-facing term in the game UI, marketing, and player-facing communication is 'chapter.' 'Today's chapter,' 'last night's chapter,' 'the chapter where you met your mentor.' This matches the life-and-story framing.

This Bible uses 'session' for technical clarity. The game itself uses 'chapter.'

## What it is

- A single-player game. No online or multiplayer at MVP.
- A persistent-world campaign spanning many sessions.
- An emergent-narrative game with no designed endpoint and no single climactic moment.
- A creature-companion game where multiple creatures bond with the player over time, each becoming structurally unique through the relationship.
- A wholesome game with serious moral underpinnings: cruelty exists in the world as something the player encounters and opposes, not something the player does.
- A non-lethal-competition game where battles are competitive sport.

## What it is not

- A monster-collecting game with a fixed gym ladder, region progression, or championship arc.
- A creature-care simulator. Creatures are companions in a life, not the central activity.
- A Tamagotchi-style single-creature game.
- A game with a real-time clock or absence pressure. The world advances in story-time, not real-time.
- A game where the player can be cruel. Cruelty is a villain trait, not a player option.
- A game with battle death, lethal combat, or graphic violence.

## What a session feels like

A session is 'a meaningful piece of a life.' It can be the day the player meets a mentor in an unfamiliar career. It can be the long evening spent training with a creature who has been hesitant to trust. It can be the morning the world delivers an unexpected event: a new island appearing, an old friend reaching out, a creature released long ago seen again.

A session ends when something meaningful has happened *and* the world delivers a moment that lets the player feel done. The pacing engine watches for this combination. The player can extend if they want to keep going.

The session always leaves a thread. Something the player wants to know the next chapter of.

## What is constant across sessions

The player's identity, choices history, and accumulated story. The world's state: who is who, where is where, what has happened. The current story-time. All bonded creatures and their accumulated witnessing. All NPCs and their accumulated relationships, opinions, and aging. The player's career path or paths. The player's reputation effects, debts, promises, and ongoing arcs.

## What varies session to session

What the player chooses to do. What the world chooses to deliver. Which NPCs and creatures the session features. What thread closes and what new threads open. What the world surprises the player with.

## Why it works

The game uses the Arcwright platform's capabilities the way they were designed to be used. The knowledge graph remembers what each creature and NPC has witnessed. The behavior engine drives them to respond believably across long timescales. The persistent character state lets the same creature accumulate a unique history with the player. The procedural generation responds narratively, not just topographically. The pacing engine targets narrative momentum rather than tension toward a climax. No other engine on the market is built to do this.

# Chapter 2: The Life and Fate Model

*Cross-reference: Nightcap has no analogous chapter. This is new architectural and design territory for the platform. It introduces a structural concept future games may also use, but it originates here.*

## The duality

The game is built on a duality between two narrative forces.

**Agency** is what the player chooses. The decisions made, the reactions to events, the directions pursued, the relationships entered, the careers tried, the things ignored. Agency is the player's authorship of their character.

**Fate** is what the world delivers. The events that happen, the new places that appear, the people who walk into the player's life, the consequences that arrive. Fate is the world's authorship of the story.

Neither force operates alone. Agency without fate is solipsistic: choices in an empty room. Fate without agency is passivity: the player as audience. The game is the collision between the two.

The game's emotional power comes from this collision. The player feels alive because their choices matter (agency working) and they feel a sense of story because the world surprises them (fate working). When the engine fails at either, the game loses its core feeling.

## Agency has scope

The player authors their own choices and reactions. The player does not author the world. NPCs have their own agency. Creatures have their own autonomy. History does not rewind. Fate cannot be canceled. The collision of these two scopes of authorship is where the game lives. The world is not a puppet for the player; the player is not a passenger in someone else's story. Both are real authors in their own domains.

## How agency is registered

Every meaningful player decision becomes a recorded event in the knowledge graph. 'Meaningful' includes career-path decisions, creature-relationship decisions, moral decisions in response to witnessed cruelty, treatment of NPCs, kept and broken promises, direction decisions, and autonomous decisions the world did not prompt.

Each decision is tagged with provenance: what context preceded it, who was involved, what alternatives existed. NPCs and creatures who witness the decision update their internal state with it. Decisions accumulate. The accumulated record *is* the player's character.

## How fate operates

**Scheduled fate** is events the world has been planning to deliver, scheduled in story-time. Mentors arrive on their own timelines. Seasons turn. NPCs age and make their own moves. World events happen at planned story-times whether the player engages or not.

**Responsive fate** is events generated procedurally in response to the player's accumulated agency. The platform's procedural generation does narrative work, not just topographic work. The world generates new content (a new location, a new visitor, a new opportunity) in response to a player's accumulated direction; a creature the player released years ago resurfaces because the player's behavior pattern signals they would care; a mentor in a path the player has hesitated to commit to reaches out, escalating the see-all-then-commit pressure; the world surfaces consequences of player choices, sometimes long after the choice.

Responsive fate is the engine's expression of 'the story noticing you.' It is the mechanism behind the secondary signature outcome: the world surprises the player in a way that feels meant for them.

## Where agency and fate collide

Sessions are built at the collision. The pacing engine watches for meaningful events, which come from either side: a player decision (agency) or a fate event (scheduled or responsive). Meaningful events accumulate within a session. When enough have accumulated and the world delivers a closing surprise (fate's gift of an ending), the session naturally winds down.

The player ends a session having seen their agency matter *and* having received a piece of fate they did not author. Both forces have spoken. The next session begins with the threads both forces have left open.

## The Witness Bond as the felt collision

The Witness Bond is how the player *feels* the life-and-fate collision. Creatures witness the player's agency (they see what the player chooses). Creatures live through the player's fate (they experience what happens to the player). Over story-time, the bonded creature becomes a recording of the collision: their form, abilities, and personality reflect what the player did and what the world did.

This is why the same creature, bonded to two different players, becomes structurally different. Different lives produce different creatures. The creature is the life made flesh.

## Platform implications

*(Schema names below use the game-agnostic forms confirmed in D-039: bonded_entities (was bonded_creatures), event_authorship (was agency_vs_fate), witness_entity_ids (was witnessing_creature_ids), current_intent (was pact_term), player_anchor_location (was home_base_location), player_role_arc (was career_path), current_companion_entities (was active_party). The natural-English usage of these terms in narrative discussion, for example "career path" as a life concept, remains intentional and unchanged.)*

The platform must distinguish player-authored events (agency) from world-authored events (fate) in the knowledge graph, including responsive fate generated in response to player patterns. It must schedule fate in story-time, not real-time. It must run a procedural responsive generator that reads the player's accumulated agency and produces world events from it. It must run a pacing engine that watches for events from both sides and recognizes when a session has had enough of both to close. It must track Witness Bond state per creature, accumulating what the creature has witnessed of player agency and world fate.

# Chapter 3: World Architecture

*Cross-reference: Nightcap §2 (Setting Architecture) is the closest equivalent, but the games diverge sharply. Nightcap has selectable per-session settings. The Monster RPG has one persistent world per player save with responsive procedural expansion.*

## Scope

One world per player save file. The world is not selectable per session. It is the world this player is living in.

The world has authored foundations (geography, history, cultures, institutions, named places) and procedurally generated content that appears responsively. Authored foundations are the same for every player at the start. Procedural and accumulated content diverges across players over time.

The world can grow. New locations, new visitors, new opportunities appear over story-time, generated procedurally in response to the player's accumulated agency.

## Persistence

The world state persists across all sessions for a given save. Persisting elements include the current story-time; geography state (authored locations permanent, procedural locations persistent once generated, changes to locations persist); population state for every named NPC; creature state for every named creature, bonded or wild; player state; event history; scheduled future events; downstream consequences of past events.

## Story-time

Story-time is the world's clock. It advances based on what happens in the player's life, not on wall-clock elapsed time.

Each session's results carry a time-advanced delta. A session covering 'a day' advances by a day. A session covering 'a season's training arc' advances by months. The pacing engine, when it closes a session, also tags how much story-time the session represented.

All time-dependent processes run on story-time: NPC aging, creature aging, seasonal change, world-event scheduling, ongoing-arc progression, accumulated wear. The player never feels real-time pressure. Returning after a month away presents the world exactly as story-time has progressed, which is by the amount of story actually told.

## What is authored

The authored foundations exist before any player encounters the world. Named geographical regions and their named locations. Major historical events and cultural memory of them. Cultural and institutional structures (governance, education, professional bodies, social customs). Named foundational NPCs (long-lived figures, public roles, mentor candidates for each career path). Career path definitions. Creature species, their wild behaviors, their habitats, their natural ranges. The rules of physical and social reality (Chapter 10).

## What is procedural and responsive

The platform generates new content in response to player behavior.

**Triggers** are patterns in the player's accumulated agency: sustained interest in a particular career path, consistent treatment of creatures (positive or negative), prolonged underexplored regions, accumulated unkept promises, refusal to commit past the see-all threshold, distinctive patterns of any kind in the choice history.

**Outputs** are generated content that responds to the trigger: a new location appears with content matched to the player's interests; a visitor arrives in a familiar town with a relevant offer; a creature the player released years ago is sighted with new context; a consequence of a past promise surfaces; a mentor in the unchosen path escalates outreach.

Generated content respects the authored foundations. The world does not spawn cultural or geographic impossibilities. Once generated, responsive content persists.

## Home base

The player establishes a place they call home. Over story-time it accumulates a family of bonded creatures who live there or visit regularly, plus NPCs and family-of-choice members. The home base is a player-established location type in the platform schema. Home base anchors the player; the player can come home between journeys, find their creatures and family there, and return to wherever they were going.

## What changes the world

Player actions alter NPC opinions, creature relationships, world state, and accumulated record. Fate events (scheduled and responsive) alter the world state directly. NPCs and creatures live their own background lives, age, form their own relationships, make their own decisions. Time itself drives seasonal change, generational shifts, institutional evolution.

The world is alive in the literal sense that change happens without the player. The pace is story-time pace.

## What the world owes the player

The world has obligations the engine and content rails enforce. Coherence: state must be internally consistent, NPCs do not contradict their established memories, fate events do not violate the world's rules. Responsiveness: the world must notice the player. Responsive fate is a guaranteed engine feature, not optional decoration. Fairness: the world does not punish arbitrarily. Coverage: the authored foundations are rich enough that no two playthroughs feel the same.

## Platform implications

*(Schema names use the game-agnostic forms confirmed in D-039. See Chapter 2 note for full mapping.)*

New world_instance schema per save. world_state with story_time field and structured persistence of all categories above. Responsive procedural generator subsystem reading player-pattern triggers. Home base as a player-established location type. Bonded creatures exist in various locations in the world, not in player inventory. Authored-foundation content layer (content authoring work, not platform engineering).

# Chapter 4: Character Architecture

*Cross-reference: Nightcap §3 (Character Slot Architecture) generates a roster of typed role slots per session. The Monster RPG has one player character plus a persistent population of NPCs across all sessions.*

## Player character

The player creates one character when they start a new save. That character is theirs for the life of that save file. Multiple save slots allow different parallel playthroughs with different characters. Autosave runs during play. There is no character re-creation per session.

Character creation includes a name chosen by the player, a visual appearance (specifics are art direction; the principle is customization within a defined visual language), and a starting context (background or origin treated as a starting condition, not a destiny).

The player character does not start with a defined goal or career path. Goal and path emerge through play.

The player character does not age. Other characters do.

Default age presence: young adult or undefined. No fixed number. No visible aging markers. Player imagination fills in. The character is treated by NPCs as new to the wider world, capable of being an apprentice across paths, and emotionally available to form family-of-choice.

## Found family default

The player character starts without a known family. Found family develops through play and is a deliberate emotional and narrative axis. The player builds their family of choice from NPCs and creatures they connect with deeply. Mentors can become parental figures, fellow apprentices can become siblings, long-time partners can become spouses (where age-appropriate and supported by player choice). Found family is emergent, not pre-authored.

## What the player character accumulates

A choice history (every meaningful decision). NPC-by-NPC perception (how each NPC sees them). Career path or paths (current, past, declined, deferred). Bonded-creature roster across all bond depths. Possessions inventory. Promises ledger. Ongoing-arc ledger. Accumulated state IS the player character.

## NPC types

**Foundational NPCs** are authored from the start. Long-lived, often public-facing. Respected mentors in each career path, regional leaders, cultural figures, and (where the design supports it) NPCs who become family-of-choice.

**Procedurally introduced NPCs** are generated as responsive fate produces them. A visitor arriving in a town, a stranger met in a new location, an apprentice taken on. They become persistent once introduced.

**Wild NPCs** are encountered briefly without becoming named persistent figures. Most everyday interactions. Memory is shallow.

## NPC memory and state

Foundational and procedurally introduced NPCs carry detailed state.

**Episodic memory** of specific encounters with the player, **restricted to narrative-meaningful events** (the same threshold the pacing engine uses). NPCs remember what mattered, not every micro-interaction.

**Opinion state** about the player, formed from direct witnessing only. Multi-dimensional: warmth, trust, respect, owed-or-owing, professional regard, age-appropriate romantic relevance where applicable.

**Own arcs**: the NPC's ongoing story independent of the player. Aging, career changes, relationships, troubles. The NPC has their own life.

There is no separate reputation system. The network of NPC opinions IS reputation. There is no gossip propagation between NPCs as a platform mechanism. World-level consequences flow through the procedural responsive fate generator, which reads the player's accumulated agency and produces world events from it.

## Cross-session continuity

Memory and state carry across every session in the save. An NPC the player offended three sessions ago remembers, with appropriate decay or healing depending on what has happened since.

## Mentors

Mentors are a specific NPC role within the career path system. Foundational NPCs who exemplify a career path and can open that path for the player. State includes the career path they represent; their career history and current status; their availability (accepting apprentices, retired, deceased of old age); their relationship with the player; their teaching style.

Mentors age. A mentor encountered early may retire by the time the player commits to their path. Career paths must persist across mentor changes.

## Character POV moments

NPCs and creatures occasionally surface POV content beyond dialogue: letters, journal entries, interior monologues, dreams, flashbacks, perceptual moments. The platform's character POV event content type. Rare by design. Used when they add what dialogue cannot.

## Player character development through play

The character develops beyond the starting state. Career path shapes the character: how others perceive them, what doors open and close. Style choices accumulate. The character at year 20 of story-time is a different character than at the start, even though the underlying identity is the same.

# Chapter 5: Creature / Companion Architecture

*Cross-reference: Nightcap has no analogous chapter. Creatures are entirely new platform territory.*

## What a creature is

A creature is a conscious being who shares the world with the player. Creatures have their own agency, their own preferences, their own histories. They are not possessions, mounts, tools, weapons, or slaves. They are companions when they choose to be, neighbors when they choose not to be, and characters in their own right.

The world has many creature species, each with authored characteristics and substantial procedural variation within species.

## The Witness Bond

When a player and a creature form a bond, the relationship becomes a Witness Bond. The creature witnesses the player's life from that point forward. What the creature witnesses shapes the creature.

A Witness Bond produces accumulated memory (every meaningful event the creature was present for); development of personality, behavior, and form over story-time in response to witnessing; mutual understanding (communication, not command); reflection (the creature mirrors the player's life back, their form and abilities are a record of the relationship).

The Witness Bond is the central distinguishing feature of this game.

## Pact terms simplified to 'current wanting'

Each bonded creature has a current wanting. Examples: a creature who wants to compete in athletic sport; a creature who wants to learn; to teach; to travel; quiet companionship; to witness a particular thing the player is doing.

The wanting can shift over story-time. The platform tracks current wanting per creature, with a history of past wantings. Not a renegotiable contract object. Just a state that shapes behavior.

If the player consistently fails to honor the creature's wanting, the creature may leave. Engine-enforced.

## Levels and progression (separate from Witness Bond)

Creatures have traditional progression mechanics as a separate layer from the Witness Bond. Some form of levels or visible ranks (novice / trained / skilled / expert / master), or visible skill ratings per area. XP earned through training, competition, and witnessed experience. Visible to the player. Familiar feedback.

Levels say what the creature CAN DO. The Witness Bond says WHO the creature IS. Orthogonal layers. Two level-30 creatures of the same species are mechanically equivalent in capability but not the same beings.

Inheritance hooks dropped as a separate mechanism. Specific creatures with prior history are authored backstory, not a platform feature.

## Multiple creatures, varying bond depth

No fixed limit on bonded creatures over a save. Bond depth varies. Some bonds are deep and lifelong (Witness Bond producing the 'uniquely mine' feeling). Others are lighter and shorter (a creature bonded for a season, less developed, still meaningful). A player at year 20 of story-time might have bonded with 20+ creatures across that span, with three or four being deep lifelong relationships.

## Where creatures live

Bonded creatures live somewhere they are comfortable.

**Home base.** Most bonded creatures live at or visit the player's home base. Cozy anchor.

**Wild habitats.** Some bonded creatures prefer their wild habitat. The bond persists; the creature is not moved. The player visits.

**Other arrangements.** Some creatures live with NPCs the player has formed family-of-choice with. Some travel between places on their own schedule.

## Active party (travel companions)

When the player journeys, a subset of bonded creatures travels with them. **Active party size: 3 to 4 creatures maximum.** Each creature chooses whether to come on each trip. Different creatures prefer different journeys.

## Travel rest space

A practical shelter (satchel, woven carrier, design-original, not pokeball-shaped, not capsule-shaped) that traveling creatures use to rest *when they want*. They enter and exit on their own choice. Lodging, not storage. Trade dress is original.

## Creature autonomy

Creatures choose. Engine-enforced: bonding is consensual; competition is opt-in; training requires engagement; departure is allowed; refusal is real. The structural commitment that makes the creature feel like a being, not a function.

## Competitive sport

Battles are competitive sport. Athletic, skill-based, ruled, respectful. End at clear non-lethal thresholds: yielding, exhaustion thresholds (no injury), points, time, specific accomplishment.

Battles take place in cultural and institutional contexts: regional competitions, tournaments, friendly matches, training exercises, exhibitions. Not generic random encounters. The world has structure around when and why creatures compete.

Wild creatures may sometimes confront the player or a bonded creature in non-competitive contexts. These are not battles. They are encounters the player has to respond to.

## Dynamic difficulty calibration (standard scaling)

The game always feels challenging. Standard difficulty scaling applies, with inputs from creature levels, career path progression, accumulated experience, and accumulated NPC opinion effects in relevant networks. Not a new multi-axis subsystem.

Challenges and competitions presented by the world scale to be at or just above the player's current capability. Different challenge types rotate (battle, social, ethical, exploration, problem-solving, care-based). Stakes rise in narrative weight as the player progresses.

The player can lose. The player should sometimes lose. Loss is a meaningful event a session can close on, not a fail state.

## Mortality

Creatures age over story-time. Eventually, bonded creatures pass of natural causes. Treated with dignity. Memory persists in the player's accumulated record and in other characters and creatures.

The world handles this with grief content appropriate to the wholesome-serious tone. A creature's life ending is a fate event of high narrative weight.

# Chapter 6: Career Path System

*Cross-reference: Nightcap has typed role slots assigned per session. The Monster RPG has career paths discovered through play over the course of a save.*

## What a career path is

A career path is a way of living a life in this world. Profession, calling, institutional role, vocation. Examples: competitive athlete, competitive establishment owner, scientist, civic leader, healer, ranger, mediator, performer, teacher, artisan, journalist, ethicist, conservationist. The list is open.

A career path is not a class. The player is a person currently pursuing a path, not a class with abilities. The path shapes what the player does, what relationships open, what opportunities the world surfaces, how others perceive the player.

## Discovery through mentors

Career paths are not selectable from a menu. They are discovered.

Each career path has authored mentor NPCs available to apprentice the player. The player meets a mentor by encountering them in the world. The encounter is sometimes scheduled (mentors live in specific places at specific story-times) and sometimes responsive (the procedural fate generator delivers a mentor encounter when the player's pattern signals interest).

When a mentor encounter happens, the mentor demonstrates their path. The player can accept apprenticeship, decline explicitly, defer, or continue exploring.

The player can pursue multiple paths simultaneously but the design assumes most players will have one primary current path at any given time.

## See-all-and-commit pressure

After the player has encountered all available authored career paths, a soft pressure activates: NPCs ask, mentors check in, family of choice expresses concern, eventually a fate event surfaces asking what the player is doing with this life. Patient at first, escalating over story-time.

Not punitive. Not a time limit. The world acknowledging that infinite exploration is not a life. Delivered through the procedural fate generator as one pattern among many, not a separate tracking subsystem.

## Reversibility

Career paths are reversible. The player can leave one and take another in any direction at any point. Transition is not instantaneous: there is a story-time arc to it.

Past paths leave traces. A scientist who became an athlete still has scientific knowledge and relationships. The accumulated record is the player. Paths are layered, not erased.

## How paths shape the player

Skills accumulate. Professional networks form. NPCs in that path's space perceive the player differently. Opportunities surface that fit the path. Limitations exist (a path is also a choice not to be doing other things). The player's career path is one input to dynamic difficulty calibration.

## Paths and the Witness Bond

Bonded creatures witness the player's career. A creature bonded during a scientific phase witnesses science. The creature develops accordingly. If the player shifts paths, the creature's existing development persists, and the creature now begins witnessing a different life. A creature whose wanting aligned with the previous path may struggle with the shift.

## Thread genealogy and branching beats

Career threads form a directed acyclic graph. Most are root-level. Some are children of previous threads: a discovery during the scientist arc reveals a place that demands exploration; a friendship with a wild creature during the explorer arc opens the path to training; a long-running training partnership becomes the seed of a competitive establishment.

When a career arc closes, the engine can produce arc opportunity events as fate beats. These say narratively: 'the work you have done has led somewhere new.' The player can pursue the child arc, defer it, or pick something unrelated.

A **branching beat** is the specific moment of transition. Structurally: a closing beat for the current arc + a decision beat + an opening beat for the new arc + a genealogy event. Branching beats are rare, high-weight, and often natural session-closing moments.

Branching beats also fire without arc closure. The player can add a new path without leaving the current one.

## Career paths and family of choice

Mentor relationships and within-path relationships often produce family of choice in this game. A mentor can become parental. Fellow apprentices can become siblings. Long-time partners can become spouses (where age-appropriate). Not mechanically enforced; emergent from player choices.

# Chapter 7: Narrative Structure

*Cross-reference: Nightcap §4 defines an 8-beat Story Circle. The Monster RPG has emergent narrative with no designed endpoint. arc_structure: emergent.*

## The architecture of story here

Story emerges from the collision of player agency and world fate. The narrative engine does not author specific stories. It tracks events, classifies them, and generates content around them.

The fundamental unit is the **beat**: a narrative-meaningful event. The beat graph has no terminal state.

## Beat types

Six beat types plus the special branching beat.

**Decision beats.** Meaningful player decisions.

**Encounter beats.** Significant encounters with NPCs or creatures.

**Development beats.** State changes: bond depth threshold, relationship state crossing, career milestone, skill threshold, level threshold.

**Fate beats.** Scheduled or responsive fate events firing.

**World beats.** Background world events: a mentor retires, a season turns, an institution changes.

**Closing beats.** Beats the pacing engine recognizes as natural pause points.

**Branching beats.** Career transition moments. Combination of closing + decision + opening + genealogy event.

## How decisions cascade

A player decision records into the knowledge graph and triggers downstream effects: NPC opinion updates for witnessing NPCs; bonded creature witnessing; career path system updates if relevant; accumulated agency pattern updates the fate generator can read later; promise ledger updates for commitments.

## How fate events fire

Scheduled fate fires when story-time reaches the scheduled time. Responsive fate is generated by the procedural responsive fate generator.

**MVP scope (per D-043):** condition-driven templates only. The fate event schema and template engine ship at MVP. The full procedural multi-signal generator that reads accumulated agency patterns (sustained career interest, accumulated kindness, refused commitments, neglected regions) and parameterizes events from rich context ships at Monster RPG H2 when those long-form RPG signals are actually exercised. The schema-clean implementation-staged pattern applies: the schema is identical between MVP and H2, and only the implementation sophistication evolves.

## Open beat graph

The arc_structure for this game is 'emergent.' No terminal state. The pacing engine recognizes meaningful beats and identifies natural pause points for session breaks. A save's story runs as long as story-time allows.

## Threads

A thread is a narrative through-line running across multiple sessions. Career arcs, NPC relationships, creature life arcs, unresolved decisions, institutional questions. Threads open, progress, close. Multiple run in parallel.

Threads can have parents (genealogy from branching beats). A thread is recorded with parent_thread_id when it spawned from a closing arc.

# Chapter 8: Pacing and Momentum

*Cross-reference: Nightcap targets dramatic_tension_score. Monster RPG targets narrative_momentum_score. Different scoring function, same architecture.*

## Job of the pacing engine

Maintain engagement; recognize natural session-end points.

Engagement is built by ensuring meaningful events happen at a livable rate.

Session closure is built by recognizing meaningful events have accumulated AND the world has delivered a moment that lets the player feel done.

## The narrative_momentum_score

Built from beats, weighted by type. Relative ordering from lowest to highest contribution: development beats, decision beats, encounter beats, world beats, fate beats, closing beats. Exact weights are tuning parameters (Q-108).

## How a session paces

Begins with momentum from previous session's threads carrying over. Beats fire as the player plays; the engine updates momentum. When momentum is too low for too long, the engine surfaces opportunities. When momentum has accumulated enough AND a closing beat occurs, the engine offers a gentle pause.

## The closing beat

Produces the 'I can stop playing' feeling (signature outcome #2). Typically: a fate event resolving a thread; a world surprise meant for the player; a creature development moment with weight; a scene-completing decision.

Engine watches for one to occur naturally. If the player has been playing long enough without one, the engine can signal the fate generator to produce a candidate closing beat.

## Cross-session pacing

The engine tracks beat type distribution across recent sessions and biases future generation toward balance. Prevents long stretches of all-one-thing.

## Rhythm and rest

Beats don't pile uniformly. Quiet moments and dense moments. Rest is part of pacing.

## What the player perceives

The player does not see the score. They perceive that things keep happening at a rate that feels right; sessions end at the right moment; they want to come back.

# Chapter 9: Narrator and Voice

*Cross-reference: Nightcap §5 has an omniscient narrator. Monster RPG has none. NarratorConfig: none.*

## No omniscient narrator

This game has no narrator. No voice-of-god. The player experiences events directly through gameplay, observation, dialogue, and character POV moments.

## Why

Life-and-fate framing puts the player inside a life, not outside watching one. The Witness Bond is mediated by being with the creature, not by being told. Player-respecting: the player makes meaning from what happens.

Literary-fiction approach: multiple consciousness without an omniscient one.

## Dialogue carries the foreground

Characters and creatures (when appropriate) speak. Dialogue generation respects voice signatures per character and tone rails.

## Character POV moments

Non-dialogue content type. Letters, journal entries, interior monologues, dreams, flashbacks, perceptual moments. Rare by design. Generated when narrative state warrants exposure. Constrained by content rails.

## The world's voice

Without a narrator: environmental detail, authored history, the shape of events, recurring patterns.

## Tone control without a narrator

Content rails on all generated content. Voice signature consistency per character. Event tone tagging (the pacing engine knows the emotional register of each beat). Environmental tone.

# Chapter 10: World Rules

*Cross-reference: Nightcap §10 is the equivalent. Same purpose: invariants the engine enforces.*

## Authorship and agency

The player authors their own choices and reactions. The player does not author the world. The collision is what the game is.

Specific authorship boundaries: no retroactive change to made-and-witnessed decisions; no forcing NPC behavior; no forcing a Witness Bond; no bypassing the mentor-gated discovery system; no preventing scheduled fate events; no canceling fired fate events; no cruelty toward creatures; no direct assault on NPCs; no breaking world laws.

## Laws of the world

Time moves forward only. Death is permanent. No teleportation magic that breaks geography. No revival of dead characters. No precognition shared with the player. No information impossibilities (knowledge graph enforces). No identity-shifting (career paths shift; identity does not).

## Hard creature rules

Engine-enforced absolutes.

No creature death from battles. Ever. Competition ends at clear non-lethal thresholds.

Creature consent is real. Bonding, competing, training all require willingness. Refusal is engine-enforced.

The player cannot abuse a creature. Engine prevents these actions and prevents AI from generating dialogue or scenes suggesting the player has done them.

Villains can. Villainous NPCs treat creatures cruelly in ways depicted as wrong. Player encounters, responds, rescues. Never performs.

Creatures age and eventually pass naturally. Treated with dignity.

## Hard NPC rules

NPC agency is real. NPCs make their own choices.

NPCs age over story-time and eventually pass. Career paths must persist across mentor changes.

NPCs remember. Once witnessed, an event is remembered. Memory can fade or be reframed; not erased by player wish.

NPCs cannot be killed by the player. No kill-NPC affordance.

## Rules around fate

Scheduled fate fires when its story-time arrives. Responsive fate is constrained, not arbitrary. Fate events leave real consequences.

## Engine enforcement

Content rails, behavior engine, knowledge graph collectively enforce these rules. The pipeline rejects AI-generated content that would violate them.

## Soft conventions

Sessions tend to end at narrative-meaningful pauses. Consequences tend to surface within reasonable story-time. Mentors tend to remain available for a multi-season window before retiring. The world tends to introduce one or two new threads per session and close one or two.

# Chapter 11: Content Territory and IP Boundaries

*Cross-reference: Nightcap §11 is the equivalent.*

## Tone palette: wholesome serious

**Wholesome surface.** Bright, hopeful, kind. Competitions are joyful. Creatures are loved. Friendships are real. Default emotional valence is positive.

**Morally serious underneath.** Cruelty exists. Loss exists. Aging exists. Choices have weight. The seriousness makes the wholesomeness feel earned.

Reference points: Stardew Valley on surface, Studio Ghibli moral seriousness underneath, Pixar high-end (Coco for grief, Inside Out for self-knowledge, Wall-E for ecological seriousness). Not Pokemon's pop tone. Not Persona's adolescent darkness. Not SMT nihilism. Not grimdark.

## In bounds

Wholesome competition (athletic sport, friendly rivalry). Real emotional weight (meaningful friendships, age-appropriate romance, grief at natural death, joy at reunion). Moral conflict (encountering villainy, responding to it). Villain cruelty toward creatures (depicted as wrong, used as material). Non-lethal injury (exhaustion, hurt, trauma, healing). Natural death (treated with dignity). Difficult conversations (age-appropriate). Cultural and historical depth.

## Out of bounds

Battle death of creatures or characters. Player-perpetrated cruelty toward creatures. Graphic violence. Sexual content. Player-perpetrated harm toward NPCs. Profanity beyond mild. Substance abuse depicted as recreational. Real-world political controversy by direct allegory. Glorification of cruelty, exploitation, domination.

## IP boundaries

Genre is not protectable. Specifics are.

**Vocabulary is original.** Prohibited: Pokemon, Pokeball, Gym Leader, Pokedex, Elite Four, Trainer (in Pokemon-specific sense), Master Ball, Pokemon Center, PP, TM, HM. The world has its own words for these concepts.

**Mechanics avoid Pokemon signatures.** No badge-collection ladder as primary progression. No starter-trio elemental triangle. No three-stage forced evolution. No type-effectiveness matrix mirroring Pokemon's specific logic.

**Creature design is original.** No round-mascot capsule shapes mirroring Pokemon. No elemental affinities reading as Pokemon types. Visual signature developed independently.

**Trade dress is original.** No spherical or capsule-shaped creature-carriage devices. No badge-case visual signatures. No franchise-look UI signatures.

**Story signatures avoid Pokemon plots.** No 'evil organization plot' framing. No fixed regional progression. No rival character archetype.

Strongest legal protection equals strongest creative differentiation: Witness Bond, career path system, persistent story-time world, life-and-fate framing, creature autonomy principle.

## Content rails

Wholesome-serious tone enforced. AI never produces content depicting battle death, player cruelty, sexual content, or graphic violence. AI never produces content using prohibited vocabulary. AI flags procedurally generated content approaching IP risk lines for human review.

## What to register, what to protect

For IP Protection Tracker: document with dated invention notes the Witness Bond as a named mechanic; the career path mentor-gated discovery system; the narrative momentum pacing model; the life-and-fate duality as a design framework; the non-cruelty core principle as a brand position.

Game's eventual name, original creature names, original world-vocabulary terms, original visual signatures trademark candidates. Consult counsel for any formal step.

# Chapter 12: A Fully Realized Example Episode

*Cross-reference: Nightcap §9 is the equivalent. Example uses generic structural placeholders.*

*The example is designed to feel familiar to players of the genre while demonstrating every system specified in earlier chapters.*

## Pre-session state

Story-time roughly three years into this save. Current career path: science (three-year apprenticeship to [the previous Mentor]). For the last six months, increasingly drawn to the competitive sport.

Bonded creatures: [the Companion] (bonded two and a half years, deep Witness Bond); [the Newcomer] (bonded six months ago, lighter, with current wanting 'compete').

Open threads: research project; deepening doubt about scientific path; long-deferred trip to [the Competitive Venue Town] for the autumn exhibition.

Promise to [an old friend] to attend the autumn exhibition this year. NPC opinions: [the previous Mentor] holds player in growing professional regard but has noticed restlessness; [an old friend] hoping the player shows up.

World state: autumn in story-time. Exhibition begins in two days. New senior practitioner has arrived in [the Competitive Venue Town] this year.

## The session opens

Player loads save. At home in [the home town], the morning the trip begins. Route to [the Competitive Venue Town] is a half-day walk. [the Companion] alert. [the Newcomer] restless. Player sets out.

## On the road

A small wild creature crosses the path. [the Companion] freezes in a way the player has come to recognize: this species in this season deserves room. Player respects the signal. Wild creature passes. Micro-encounter that adds to accumulated patterns.

A traveler approaches with their own creature, recognizes the player as heading to the exhibition, offers a friendly bout. Player accepts. Non-lethal competitive sport, yielding rules. Traveler's creature is experienced. [the Newcomer] enters willingly (current wanting: compete). Bout produces a development beat: [the Newcomer] passes a skill threshold and gains a level. Player loses but learns. Both creatures and people unharmed and respectful when it ends.

The traveler mentions the new senior practitioner is 'the real reason to go this year.' Encounter beat with information.

## At the way-station

Player stops at a roadside way-station. Proprietor (recurring minor NPC who has known the player for years) asks 'competing this year?' Player answers. Proprietor's expression shifts in a way the player notices. Atmospheric moment, no beat per se, but the world is paying attention.

[the Companion] settled. [the Newcomer] recovering from the bout. The contrast in bond depth and current wanting is visible.

## Arrival

Player arrives mid-afternoon. Town busier than usual because of the exhibition. The competitive establishment is on the main square: open-air arena structure, training grounds, rest areas, supply and care facilities nearby.

Player walks to the registration desk and registers for a single exhibition bout the following day. Small administratively, but in context this is a decision beat: registering formalizes intent.

[an old friend] is in town and finds the player in the square. They embrace. The promise on the ledger clears. Encounter beat with relationship weight.

## The mentor encounter

That evening, an older figure approaches in the rest area beside the arena. This is [the Mentor of the Competitive Path].

The procedural responsive fate generator has been reading the player's accumulated patterns: extended interest in the competitive sport, the recent bout, the formal registration, [the Newcomer]'s visible growth, the unresolved restlessness in [the Companion]. The pattern triggered this responsive event: this mentor encounter, scheduled to occur tonight if the player registered.

The mentor introduces themselves, speaks about the path, asks the player about their work, their creatures, their life. Content generation produces the dialogue within the mentor's authored voice signature and the player's accumulated record.

The mentor offers an apprenticeship.

This is **the branching beat.** Structurally: a closing beat for the scientific arc (which has been approaching closure for six months); a decision beat of highest weight; an opening beat for the new arc; a genealogy event (the competitive arc is recorded as a child of the scientific arc with the research-toward-creatures pattern as the connective tissue).

Player options: accept; defer (continue science while training on the side); decline; ask for time. Player accepts.

## The quiet closing

After the conversation, the player walks back through the town with [the Companion] and [the Newcomer]. Light is fading. [the Companion] is calm in a different way than in recent months: the unresolved restlessness has shifted. The creature has witnessed something settled.

The player stops at the edge of the square and watches the arena being prepared for the next day's exhibition.

The pacing engine recognizes the moment. The day has produced a branching beat (highest weight), several supporting beats, and now a quiet emotional resolution in a moment of physical pause. The narrative_momentum_score peaks. The engine offers the gentle pause: 'this feels like a place to stop, if you want.'

The player accepts. The session ends with the player at the edge of the square, two creatures at their side, looking at the arena.

## What closed, what opened

**Closed:** the scientific career arc after three years of story-time. Thread genealogy records its closure.

**Opened:** the competitive-sport career arc as a child of the scientific arc. The new mentor relationship. The exhibition bout tomorrow.

**Progressed:** relationship with [an old friend] (promise cleared); [the Newcomer]'s level and skill (passed a threshold); [the Companion]'s relationship with this stage of the player's life. Recent-restlessness thread resolved by being witnessed alongside everything else.

**Unresolved and carried forward:** the exhibition bout tomorrow. The scientific work the player must wind down properly. [the previous Mentor] does not yet know. The proprietor at the way-station noticed something. Pending reactions are real.

## What a Pokemon fan recognizes

Walking a familiar route between towns. A wild creature crossing the path. A friendly bout with another traveler on the road. A supply stop where the proprietor knows you. Arrival at a town busy with an upcoming competition. Registering for an event. Meeting a senior practitioner. Two creatures at your side, each with their own personality and relationship. The kind of day a player of the genre has had hundreds of times.

## What is different underneath

The bout was governed by yielding rules and produced respect on both sides. No fainting. No creatures hurt. Player lost and the loss was a development beat, not a fail state.

The wild creature was respected and let pass. No capture mechanic offered.

[the Companion]'s behavior carried meaning derived directly from accumulated witnessing. Not a separate creature-as-social-radar mechanism; the Witness Bond produced the behavior naturally.

The mentor encounter was an apprenticeship offer, not a gym leader battle. Path is a career, not a ladder of badges.

Closing the scientific arc and opening the competitive arc was a thread genealogy event. The player's life will remember the connection.

The session ended on a quiet emotional moment the engine recognized. Not a level-up screen, not a checkpoint.

The world had been watching. Pending reactions are real.

## Signature outcomes delivered

**Narrative pull (primary):** the player wants to know what tomorrow brings, how [the previous Mentor] will react, how the new path will unfold.

**World surprise that lets the player feel done (secondary):** the mentor encounter arrived because the world had been paying attention. The player felt seen.

**Creature uniquely mine (tertiary):** [the Companion]'s response was specifically a response to *this* player's accumulated choices.

## Platform behavior exercised

Story-time advancement; persistent NPC state continuity; Witness Bond accumulation; career path branching event with thread genealogy; procedural responsive fate generating the mentor encounter from accumulated patterns; beat detection routing through all six beat types plus the branching beat; thread tracking with multiple progressing, one closing, several opening; pacing engine closing-beat recognition with gentle pause offer; content generation respecting voice signatures and tone rails; non-lethal competitive sport rules; no narrator, multiple perspectives implied through behavioral signaling and dialogue.

---

# End of v1.0

This Bible was drafted in Chat 8 (Monster RPG Story Bible) and finalized as v1.0 after Chat 9 (Platform-as-Product Strategy). Original design decisions committed in Decisions Log D-001 through D-030. Chat 9 resolved:

1. Game-agnostic naming pass on platform schemas (D-038, D-039; resolves Q-114 naming portion).
2. MVP scope discipline pass on the four overthought items via the schema-clean implementation-staged pattern (D-042 through D-045; resolves Q-114 scope portion).
3. Platform-as-product strategy: D-031 through D-047 (resolves Q-113).

**Schema renames applied to formal field references:** bonded_creatures became bonded_entities; home_base_location became player_anchor_location; career_path became player_role_arc; active_party became current_companion_entities; agency_vs_fate became event_authorship; witnessing_creature_ids became witness_entity_ids; pact_term became current_intent. Natural-English usage of these terms in narrative design discussion remains intentional and unchanged.

**Monster RPG's strategic role (per D-034):** Monster RPG is the H2 internal proof that the Arcwright platform handles solo-player RPG narrative state, building credibility for H3 expansion to mid-size narrative studios. It is not the H2 external segment target.

---
## SOURCE FILE: docs/Accusation and voting display design what does the 362b7de354a88173af1cf04bbdcfd7cd.md

# Accusation and voting display design: what does the Jackbox-style voting reveal screen look like per aesthetic theme, what is the animation and pacing model, and how is it specified as a ContentEvent type in the engine?

Category: Product
Date Opened: May 15, 2026
Priority: Medium
Status: Open

---
## SOURCE FILE: docs/Arc structure graph with branching, convergence, m 35ab7de354a881f0a898f1ae967223df.md

# Arc structure: graph with branching, convergence, multiple endings, loops

Date: May 7, 2026
Rationale: Arcs are not linear sequences. Beats are nodes; transitions are conditional edges. Graph supports: branching (multiple paths from a beat), convergence (multiple paths into a beat), loops (repeating beats like investigation rounds), multiple terminals (different endings), conditional transitions evaluated at runtime. World mutability supported through state JSONB on locations and objects. Arc mutation at runtime architecturally possible (data-driven YAML, not compiled), implementation deferred until use case requires it.
Section: Cross-cutting
Status: Committed

---
## SOURCE FILE: docs/Conspirator guess mechanic what is the UX on the k 362b7de354a881698521cb619acdf9af.md

# Conspirator guess mechanic: what is the UX on the killer device for the guess interaction, how is the leverage message generated at the prompt engineering level, and how does this event sequence integrate into the session flow?

Category: Product
Date Opened: May 15, 2026
Priority: Medium
Status: Open

---
## SOURCE FILE: docs/D-001 Monster RPG single-player at MVP Multiplayer 364b7de354a881a8bf9ad544fb392233.md

# D-001 Monster RPG single-player at MVP. Multiplayer deferred to a later phase.

Date: May 18, 2026
Rationale: Reduces MVP scope; matches founder intent for the core experience.
Section: Cross-cutting
Status: Committed
Tags: roadmap, verticals

---
## SOURCE FILE: docs/D-003 Monster RPG world runs in story-time, not re 364b7de354a88124bd3cff63795a9581.md

# D-003 Monster RPG world runs in story-time, not real-time or paused.

Date: May 18, 2026
Rationale: Removes absence pressure for working adults; aligns with life-and-fate framing.
Section: Cross-cutting
Status: Committed
Tags: verticals

---
## SOURCE FILE: docs/D-012 No omniscient narrator in Monster RPG Dialog 364b7de354a881c0aba0c9e6a019f722.md

# D-012 No omniscient narrator in Monster RPG. Dialogue plus character POV moments. NarratorConfig: none.

Date: May 18, 2026
Rationale: Player-respecting; matches literary-fiction approach.
Section: Cross-cutting
Status: Committed
Tags: verticals

---
## SOURCE FILE: docs/D-013 Creatures and NPCs age over story-time; play 364b7de354a881dda1f7efe4dbd946a6.md

# D-013 Creatures and NPCs age over story-time; player character does not age.

Date: May 18, 2026
Rationale: Preserves open-ended campaign; world mortality carries fate's emotional weight.
Section: Cross-cutting
Status: Committed
Tags: verticals

---
## SOURCE FILE: docs/D-023 NPC memory narrative-meaningful events only, 364b7de354a881bc9423fea6bd911dfa.md

# D-023 NPC memory: narrative-meaningful events only, not every micro-interaction.

Date: May 18, 2026
Rationale: Bounded knowledge graph load; PRD §5 cross-session memory commitment preserved at meaningful depth.
Section: Cross-cutting
Status: Committed
Tags: verticals

---
## SOURCE FILE: docs/D-029 Monster RPG Story Bible structured as 12 cha 364b7de354a881a1bcfbdd86bcd4bedb.md

# D-029 Monster RPG Story Bible structured as 12 chapters.

Date: May 18, 2026
Rationale: Identity, life-and-fate, world, characters, creatures, careers, narrative, pacing, narrator, rules, content territory, example.
Section: Cross-cutting
Status: Committed
Tags: workflow

---
## SOURCE FILE: docs/D-030 Monster RPG player-facing term is 'chapter,' 364b7de354a8811e878ec31ef0c50a17.md

# D-030 Monster RPG player-facing term is 'chapter,' 'session' is platform/technical terminology.

Date: May 18, 2026
Rationale: Player-facing language matches life-and-story framing.
Section: Cross-cutting
Status: Committed
Tags: verticals

---
## SOURCE FILE: docs/D-035 Visual Storyworld staged roadmap 366b7de354a8812e8699ea2cae9a8d5f.md

# D-035 Visual Storyworld staged roadmap

Date: May 19, 2026
Rationale: Visual creator tooling, internally referred to as Visual Storyworld, is pulled forward from H3 to a five-phase staged roadmap. Phase 1 (inspection surfaces: live knowledge graph visualization, read-only arc structure view, live event stream, character state inspection) ships with platform MVP in H1. Phase 2 (structured editing of existing primitives: arc composition, character authoring, content event templates) ships during H2 prep. Phase 3 (live preview and runtime debugging) ships with H2 launch. Phase 4 (full visual flow editor, Blueprints-shape) ships H2 mature to H3 early. Phase 5 (asset libraries, marketplace if pull exists, AI-assisted authoring) ships H3 plus. Positioning is narrative middleware with extraordinary creator tooling, not no-code platform. Phase ordering may be adjusted based on customer learning and bandwidth signals.
Section: Section 3: Three-Horizon Roadmap
Status: Committed

---
## SOURCE FILE: docs/D-045 narrative_momentum_score scope at MVP 366b7de354a8818ba75fd27cef776208.md

# D-045 narrative_momentum_score scope at MVP

Date: May 19, 2026
Rationale: The narrative_momentum_score function exists in the API at MVP with simplified implementation: event-count plus arc-position awareness, suggesting pause after N events or predefined arc breakpoints. Sophisticated multi-signal scoring with cross-session pacing memory and closing beat detection ships at Monster RPG H2.
Section: Cross-cutting
Status: Committed

---
## SOURCE FILE: docs/Fully generative story content is a Nightcap-speci 361b7de354a881acac91c863ab4876c6.md

# Fully generative story content is a Nightcap-specific design decision, not a platform requirement

Date: May 15, 2026
Rationale: The Arcwright platform supports authored, generative, and hybrid content strategies per arc. Nightcap chose fully generative story elements (characters, murder, clues, dialogue). Other arcs may have fixed authored characters, authored story content with generative edges, or any other combination. This distinction must be explicit in all platform documentation to avoid miscommunicating platform capabilities as Nightcap design choices.
Section: Cross-cutting
Status: Committed

---
## SOURCE FILE: docs/Killer active capabilities are story-prompted opti 361b7de354a8814ba5b5f98f767eb312.md

# Killer active capabilities are story-prompted optional actions, not tracked resource pools

Date: May 15, 2026
Rationale: No ability_charge concept. The engine identifies when a story moment makes an action narratively appropriate and presents it as an optional prompt on the killer device. Killer accepts or declines. Story continues either way. The killer's experience is being a character in a story, not managing a hand of cards. Ability_pool concept in arc definition now means the set of action types available in this session, not a resource counter.
Section: Cross-cutting
Status: Committed

---
## SOURCE FILE: docs/Killer assignment behavioral signal specification  362b7de354a8811caa65f1fa3c85e5fb.md

# Killer assignment behavioral signal specification: what specific signals does the engine track per player during beats 1-4 to inform assignment, what are the interaction triggers that can accelerate the decision, and how is this configuration expressed in the arc definition?

Category: Product
Date Opened: May 15, 2026
Priority: High
Status: Open

---
## SOURCE FILE: docs/Killer revelation is mid-session, variable between 361b7de354a881dd8f09f1fa4cfa57b1.md

# Killer revelation is mid-session, variable between beats 2-4. Killer assignment and killer revelation are two distinct events.

Date: May 15, 2026
Rationale: Killer does not know they are the killer at session start. Assignment fires internally at any point from session start to just before revelation. Engine observes player behavior passively and can be accelerated by specific interaction triggers. Revelation fires privately on killer device at assigned beat (range 2-4). This produces authentic early-game investigative behavior and a strategic pivot moment when revelation lands. Differentiates Nightcap from all major imposter-format games.
Section: Cross-cutting
Status: Committed

---
## SOURCE FILE: docs/Murder timing is variable across beats 1-3 Mini-ga 361b7de354a881fea286e3539f89f859.md

# Murder timing is variable across beats 1-3. Mini-games active in beats 1-3 feed killer assignment logic.

Date: May 15, 2026
Rationale: Murder can occur in any of the first three beats, not at a fixed narrative point. This mimics real social dynamics and creates meaningfully different session experiences. Mini-games (Jackbox-style social games) are framed as part of the gathering and run in beats 1-3. Their behavioral outputs are named inputs to the killer assignment logic. Players have no visibility into this function.
Section: Cross-cutting
Status: Committed

---
## SOURCE FILE: docs/Nightcap aesthetic mode generative The visual and  360b7de354a88142af3cfa707c5861d6.md

# Nightcap aesthetic mode: generative. The visual and tonal aesthetic of each session is generated fresh. The platform supports fixed, palette, and generative aesthetic modes; Nightcap uses generative.

Date: May 14, 2026
Rationale: Generative aesthetics contribute to session unrepeatability. Future arcs can use any mode.
Section: Cross-cutting
Status: Committed
Tags: roadmap

---
## SOURCE FILE: docs/Nightcap arc structure Dan Harmon Story Circle Arc 360b7de354a881a18d5dd1a4a63d7944.md

# Nightcap arc structure: Dan Harmon Story Circle. Arc structure is a configurable platform-level parameter; Nightcap uses Dan Harmon.

Date: May 14, 2026
Rationale: The Story Circle maps cleanly onto a murder mystery: normal world, disruption (murder), investigation, revelation, return transformed. Man in a Hole works for individual player emotional arcs within a session and can coexist at that level.
Section: Cross-cutting
Status: Committed
Tags: roadmap

---
## SOURCE FILE: docs/Nightcap character mode generated Characters are g 360b7de354a881118a47e9b3cb227460.md

# Nightcap character mode: generated. Characters are generated per session from typed character slots, not from authored fixed definitions. Character identities, names, and personalities are generated at session start, calibrated to the specific player group.

Date: May 14, 2026
Rationale: Every session should feel like a genuinely different story (Miracle Workers / Glass Onion model). Fixed authored characters produce a recognizable cast that repeats, reducing replayability. The arc schema supports authored, generated, and hybrid modes at the platform level; Nightcap uses generated.
Section: Cross-cutting
Status: Committed
Tags: roadmap

---
## SOURCE FILE: docs/Nightcap era and occasion list finalization which  362b7de354a881b3abdcf4f5e7af4484.md

# Nightcap era and occasion list finalization: which specific era/occasion combinations are in scope for v1 launch, what are the art production deliverables per theme, and who produces them?

Category: Content
Date Opened: May 15, 2026
Priority: High
Status: Open

---
## SOURCE FILE: docs/Nightcap narrator host persona on shared display V 360b7de354a881d0b7a7cb4d59a0ce9f.md

# Nightcap narrator: host persona on shared display. Voiced character on the TV. Aesthetic-linked persona, omniscient, player-addressable. Not a murder suspect. Behavior triggers: beat transitions, clue releases, tension threshold, player inaction. Mostly absent from phones.

Date: May 14, 2026
Rationale: The narrator is the architect of the evening: the host who built the stage and knows everything. The TV is the social anchor all players share when dispersed on phones. Persona adapts to aesthetic (dry Victorian butler vs theatrical Italian host) contributing to unrepeatability. Not a competing detective but an all-knowing master of ceremonies.
Section: Cross-cutting
Status: Committed
Tags: roadmap

---
## SOURCE FILE: docs/Nightcap play mode at MVP imposter One player is a 360b7de354a881519ececc3e05ddd174.md

# Nightcap play mode at MVP: imposter. One player is assigned the killer role at session start and plays to avoid detection. All other players are investigators. The killer receives a fundamentally different private phone experience from all other players.

Date: May 14, 2026
Rationale: Imposter mode creates the strongest social dynamics for a group party game: paranoia, misdirection, alliance-forming, and accusation. The killer's private experience maps directly to the personalization engine's strength. Replay value is high because the killer role is randomly assigned each session. Detective race mode deferred to v1.1.
Section: Cross-cutting
Status: Committed
Tags: roadmap

---
## SOURCE FILE: docs/Nightcap rendering layer specification how does Ni 362b7de354a8813fba0cd8796c407915.md

# Nightcap rendering layer specification: how does Nightcap's shared display and phone client map ContentEvent presentation_hints (animation_hint, lighting_hint, emotion) to specific pre-produced assets, animations, and UI states?

Category: Product
Date Opened: May 15, 2026
Priority: High
Status: Open

---
## SOURCE FILE: docs/Nightcap setting constraint social gathering The p 360b7de354a881348916cb26de1baeef.md

# Nightcap setting constraint: social gathering. The physical construct of every Nightcap session is some kind of social gathering. Time period, tone, and specific setting vary within this constraint.

Date: May 14, 2026
Rationale: Players should not need heavy imaginative lifting to inhabit the world. Social gathering is something all players have real-world experience with. Time period and accent can vary freely. Exotic settings with no player reference point break immersion rather than building it.
Section: Cross-cutting
Status: Committed
Tags: roadmap

---
## SOURCE FILE: docs/Nightcap uses 8 execution beats in 1 1 Story Circl 361b7de354a881609cecfae20230cc67.md

# Nightcap uses 8 execution beats in 1:1 Story Circle mapping: The Arrival, The Body, The Opening Move, The Dig, The Thread, The Reckoning, The Close, The Truth

Date: May 15, 2026
Rationale: 8 beats gives the engine direct knowledge of the current Story Circle phase at all times, enabling structural intent injection into generation, tone-aware pacing, and ensemble coordination. Named beats are Nightcap-canonical labels, separate from the Story Circle step names. BeatDefinition schema expanded with story_circle_step, structural_function, dramatic_purpose, emotional_target, information_goal, tension_target, character_emphasis.
Section: Cross-cutting
Status: Committed

---
## SOURCE FILE: docs/Q-115 Monster RPG Story Bible v1 0 finalization 365b7de354a881b68978e0544ef171d8.md

# Q-115 Monster RPG Story Bible v1.0 finalization.

Category: Workflow
Date Opened: May 18, 2026
Priority: High
Resolution Notes: v0.9 DRAFT is in Notion pending platform strategic review. After Q-113 and Q-114 settle, finalize as v1.0 with game-agnostic platform implications language.
Status: Open

---
## SOURCE FILE: docs/Q-115 What is the final v1 0 of the Monster RPG St 365b7de354a8815c9761c253345257b8.md

# Q-115 What is the final v1.0 of the Monster RPG Story Bible?

Category: Product
Date Opened: May 18, 2026
Priority: High
Resolution Notes: Depends on Q-113 and Q-114. v0.9 draft committed to Notion with all 12 chapters and 30 decisions integrated; final v1.0 incorporates platform-as-product naming and any MVP scope changes.
Status: Open

---
## SOURCE FILE: docs/Should NPC actions in Nightcap be exclusively rout 363b7de354a881e79bb0cfa7a4b35356.md

# Should NPC actions in Nightcap be exclusively routed through a finite, defined tool call vocabulary?

Category: Product
Date Opened: May 17, 2026
Priority: High
Status: Open

Emergence World's tool-as-interface pattern routes every agent action through explicit tool calls, making behavior observable, auditable, and replayable. Constraining NPC actions to a defined vocabulary (e.g., accuse, alibi, reveal, deflect, move) would also enable narrative-state-gating and clean separation between AI reasoning and game state. The alternative is free-form LLM output with post-processing, which is harder to audit and constrain. This needs an answer before engine architecture is finalized. Recommendation: adopt tool-as-interface; define an MVP action vocabulary of 8-15 tools for Nightcap before writing engine code.

---
## SOURCE FILE: docs/Should NPC tool availability be gated by narrative 363b7de354a8817a8224cb985a470593.md

# Should NPC tool availability be gated by narrative state rather than relying on prompt engineering alone?

Category: Product
Date Opened: May 17, 2026
Priority: High
Status: Open

Emergence World gates tool availability by agent location; agents cannot use tools they are not physically near. The Arcwright equivalent is narrative-state-gating: an NPC who has not been confronted cannot confess; a player who has not found a clue cannot pursue that lead. Enforcing story logic through tool availability rules is more reliable and auditable than prompt engineering alone. Deciding this early has significant engine architecture implications. Needs a mapping of which NPC actions are gated by which story states before any engine code is written.

---
## SOURCE FILE: docs/Story Circle is a functional platform-native 8-bea 361b7de354a88108aec9cf3340ff45aa.md

# Story Circle is a functional platform-native 8-beat template (not decorative metadata)

Date: May 15, 2026
Rationale: arc_structure field value changed from dan_harmon to story_circle. Story Circle is now a first-class platform object that scaffolds 8 pre-populated beat containers with story_circle_step, structural_function, and suggested dramatic_purpose. arc_structure is a functional engine input used for generation context, pacing calibration, and structural intent. Authors using Story Circle get pre-scaffolded beats; custom arc authors define their own. Resolved the open architecture question from Chat 7 pre-work.
Section: Cross-cutting
Status: Committed

---
## SOURCE FILE: docs/Victim is a dedicated 7th structural position Kill 361b7de354a881b58fd2d476f3e60b12.md

# Victim is a dedicated 7th structural position. Killer designates victim at revelation. Eligibility governed by player count (threshold: 4+ human players for player-eligible).

Date: May 15, 2026
Rationale: Victim slot is separate from the 6 player role types. In standard player counts (under threshold), victim is NPC. With 4+ human players, a human can be designated. The killer selects from available characters at the moment of revelation. Victim player receives their own private revelation with role assignment from the victim role pool: Witness, Specter, Informant, or Conspirator (conditional). All victim roles keep the player engaged through Beat 8. All learn killer identity at Beat 8 with everyone else.
Section: Cross-cutting
Status: Committed

---
## SOURCE FILE: docs/What are Arcwright's narrative quality metrics for 363b7de354a881cb9552f5f14d92ec69.md

# What are Arcwright's narrative quality metrics for evaluating Nightcap sessions?

Category: Product
Date Opened: May 17, 2026
Priority: Medium
Status: Open

Emergence World developed Agent World Indicators (AWI), a nine-metric scorecard for evaluating open-ended AI societies. Arcwright needs an analogous framework for narrative quality. Candidate dimensions: Was the mystery fair (were all necessary clues accessible)? Did NPC character consistency hold across the session? Did player choices meaningfully affect outcomes? Was the session pacing appropriate? These metrics are needed for iterative improvement of both the game and the underlying engine, and will become essential when positioning the platform for enterprise licensing. Should be defined before the first Nightcap playtest.

