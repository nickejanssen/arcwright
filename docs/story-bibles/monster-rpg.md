# Monster RPG Story Bible

> Current version: v1.0
> Last updated: 2026-06-13
> Status: Current
> Canonical path: docs/story-bibles/monster-rpg.md

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
