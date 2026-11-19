---
id: nightcap.gdd.nightcap.04-supporting-design.minigame-idea-bank
namespace: nightcap
title: Standalone minigame idea bank
owner: Nico Janssen
status: active
review_by: "2027-02-27"
sensitivity: internal
source: authored
tags: [minigames, standalone, playtest]
supersedes: []
---

# Standalone minigame idea bank

Use this running list when brainstorming minigames, shortlisting mechanics or planning a standalone live playtest. Each ranked entry is a **RECOMMENDATION**. The fixture, scoring and player-count adaptations are starting points for experiments. The ranking reflects predicted replay appeal, social payoff, mystery fit and flexibility across group sizes. No player-count or fun claim here has been validated.

## What standalone means

A tester can open the minigame directly in a mobile or desktop browser, start a round and play to a result **with Nightcap shut down**. No Nightcap lobby, login, running service, case, arc, investigation, beat, save or reward is required. A multiplayer minigame can offer its own join link and use a game-independent rules service. Shared Arcwright code is fine. A phone, a desktop browser or a shared display is a surface choice; a TV is optional. The minigame supplies its own prompts, assets, example scenario, input, feedback, end condition and replay.

**Live acceptance check for a future implementation.** From its documented direct URL or local start command, play a fresh solo round on mobile and desktop. Have two real participants join the same standalone round from separate browsers, submit different choices, see the actual rules resolve them and start another round. Exercise the other advertised counts, including eight, and record which counts/devices were human-tested. A fixed-state renderer preview, paper rehearsal or headless rules test supplies different evidence; record each accurately. [AW-322 documents the standalone tooling and gaps](../../../roadmap/tasks/AW-322-prove-a-mini-game-can-be-built-and-played-on-its-own-and-list-the-gaps.md).

**Common fixture.** Each card below can be rehearsed with disposable prompts or props. For parallel challenges, give each participant the same initial scene, budget and conditions; solo uses the stated target, two compete head-to-head and 3–8 commit independently before the reveal. Preserve ties. For bluffing, route congestion and bidding, use the card’s own opponent model. In a digital build, record fixture version, player count, inputs and final result so a rules defect can be replayed. Keep private inputs private until the specified reveal.

**Optional Nightcap integration.** A story wrapper may supply a fictional trigger and consume the result. Standalone rules own their local objective and finish cleanly even when no wrapper listens. For thin-version rewards and shared standings consult [spec 0093](../../../specs/0093-engine-spine-for-the-thin-version.md) and the [competitive pulse GDD](../01-authoritative-gdd/04-minigame-competitive-pulse.md). No sample in this bank contains required case evidence. [AW-337](../../../roadmap/tasks/AW-337-give-small-groups-a-mini-game-that-fits.md) owns selection for a Nightcap playthrough.

## Ranked candidates

### 1. An Entirely Normal Walk

**Social camouflage.** Tail a bellhop across a six-stop lobby. Preview his next glance, then choose a shortcut, cover activity or safe detour. Replay the patrol and the detectives’ deeply suspicious shoe-tying.

**Standalone result and player counts.** Score checkpoints held, then closest undetected finish. Solo pursues a patrol target; rivals commit on identical routes and watch the closest shave.

**First playtest question.** Do two players watch each other’s replay? Start with two defensible risks at one corner.

### 2. The Portrait Has an Alibi

**Perspective construction.** Match a witness’s impossible photograph. Give everyone a doorway, a portrait, a waiter and a champagne tower. Make three snapped moves in a miniature room, then look through the keyhole.

**Standalone result and player counts.** Count matched silhouette landmarks from a fixed viewpoint. Solo attempts the target; rivals compare different arrangements that yield the same image.

**First playtest question.** Can two distinct arrangements pass? Does a player try another arrangement after the reveal?

### 3. Going Down?

**Push-your-luck routing.** Deliver a camera by dumbwaiter. Preview the floors, then stop, coast or ring. Ringing can draw a terrier away from a cake and summon a soup-laden waiter below. Bank a delivery or continue.

**Standalone result and player counts.** Rank successful deliveries by depth, then camera condition. Solo pursues a delivery target; rivals play the same schedule independently.

**First playtest question.** Can a player explain which earlier bell caused the mess?

### 4. Of Course I Work Here

**Hidden-role bluff.** Someone missed the staff briefing. Answer the guest, then see who was bluffing. Staff know the ice machine screams; the gatecrasher knows only that a guest heard a noise. Each locks in one reply. Reveal together, then staff privately pick the gatecrasher while the gatecrasher picks the secret from three explanations.

**Standalone result and player counts.** Solo interviews three authored staff with one follow-up and identifies the fake. At two, each writes one genuine and one bluff reply, then spots the rival’s fake. At 3–8 use one gatecrasher; start testing at four. Record correct staff picks and the gatecrasher’s evasion and secret guess separately. Rotate roles for rematches. Cross-role standings are open.

**First playtest question.** Can four newcomers play uncoached, including a player giving a straight answer? Skip formal challenges. Check whether both roles want a second turn and whether one reply gives everything away at three.

### 5. What the Butler Heard

**Foley composition.** Rebuild a three-beat sound cue with a tray of props. A teaspoon and teapot can pass for a lift bell. Place the sounds, play back the performance and compare it to the cue.

**Standalone result and player counts.** Score onset, duration and authored sound-family matches; give the same information in a visible beat strip. Solo matches a target; at larger counts replay the closest match and a strange near miss.

**First playtest question.** Do players try a second combination for the sound alone? Can a muted player reason from the strip?

### 6. The Emergency Seating Committee

**Constraint optimization.** A leaking chandelier forces guests to move. With two swaps, satisfy as many demands as possible: separate feuding twins, seat the widow facing the door, respect a dachshund’s diplomatic status. Animate the seating consequences.

**Standalone result and player counts.** One point per fulfilled demand; equal totals tie. Solo chases a perfect dinner; rivals compare which disaster they knowingly allowed.

**First playtest question.** Does the table talk about the guests it inconvenienced? Try eight place cards before commissioning art.

### 7. Last Porter Standing

**Load balancing.** Stack awkward luggage on a two-axle trolley. Bank the load or place one more piece. Send every trolley around three visible bends and watch which hatboxes survive.

**Standalone result and player counts.** Score delivered luggage value using the same tipping rules. Solo pursues a delivery quota; rivals submit separate loads for the common route.

**First playtest question.** Can a player predict why a particular bend will drop the cello?

### 8. The Séance Has Been Double-Booked

**Symbolic deduction.** Two spirits answer a lost-property inquiry through the same illustrated deck. One describes appearance; the other describes function. Ask two questions, untangle the answers and return each object.

**Standalone result and player counts.** Count correctly reunited spirit–object pairs. Solo solves the exchange; rivals select privately before the common reveal.

**First playtest question.** Can players explain two plausible readings of a card and why another clue breaks the tie?

### 9. Switchboard After Midnight

**Call routing.** Connect hotel calls from partial descriptions. Plug in, hear or read the opening exchange and spend a limited reroute if it sounds wrong. Make mistaken connections worth hearing.

**Standalone result and player counts.** Count requests connected correctly within the same call budget. Solo works a shift; rivals take independent switchboards. Feature one unusual connection.

**First playtest question.** Can testers recover from a funny mistake using the information they just heard or read?

### 10. The Decoy Must Go On

**Silhouette puppetry.** Cover a performer’s cue by staging three silhouettes behind a curtain. Rotate and reuse props: a feather duster plays a duchess’s plume, then her dog’s tail.

**Standalone result and player counts.** Count matched silhouette features across all poses. Solo sees its performance; rivals submit separate productions for a gallery.

**First playtest question.** Do people discover a second use for a prop without prompting?

### 11. Blackout at the Bellweather

**Power sequencing.** Restore power to a service wing. The mixer coasts after power is cut; the lift draws extra current on startup. Sequence appliances on the same small circuit and run the plan.

**Standalone result and player counts.** Count objectives powered within the load limit and move budget. Solo aims to restore the wing; rivals compare their programs on the same initial circuit.

**First playtest question.** Can a first-timer anticipate one overload and invent a workaround?

### 12. The Counterfeit Concierge

**Selective verification.** Three guests make requests. Spend at most two checks per guest on a seal, room call, signature or service detail. Admit or reject each request and reveal the forged credentials.

**Standalone result and player counts.** Count legitimate requests served and impostures caught. Solo plays an inspection desk; rivals choose checks separately on identical guest files.

**First playtest question.** Did a chosen question change a decision, or was the forgery obvious up front?

### 13. Room Service Roulette

**Simultaneous route prediction.** Choose a lift, stairs or corridor for a delivery. The lift has only two spaces. Ringing opens a corridor for everyone but costs the caller a move. Reveal together and resolve congestion.

**Standalone result and player counts.** Count completed deliveries over a fixed route sheet. Publish a rotating boarding order for oversubscribed lifts. Solo predicts visible staff traffic; groups predict other players.

**First playtest question.** Does a rival’s previous choice change your next one? Test congestion separately at two and eight.

### 14. The Clockmaker Pleads the Fifth

**Clockwork observation.** Run a model with four disagreeing clocks. Pause at an observable event such as a cuckoo emerging. Spend two inspections to identify which clock skips a beat and when.

**Standalone result and player counts.** Score the clock and event separately. Solo inspects the mechanism; rivals use the same clock schedules and lock predictions before playback.

**First playtest question.** Can someone solve it by watching the machine without doing timetable arithmetic?

### 15. Bid Me Goodnight

**Sealed bidding.** Spread six chips over three lost-property lots. Sets have public bonus values. Reveal bids, award each lot and total collections. Decide how many chips to save for a matching piece.

**Standalone result and player counts.** Rank collection value. For this fixture split value equally on exact high bids. Solo faces published reserve prices; two to eight rivals place sealed bids.

**First playtest question.** Does a player knowingly give up a valuable lot to complete a set? Check ties at eight.

### 16. Mind the Carriage Gap

**Reading movement cues.** Cross a swaying train by plotting step, brace and swing-door actions. Hanging lamps signal the upcoming bend. Commit before entering the tunnel and see the route play back.

**Standalone result and player counts.** Score checkpoints reached, then stable landings. Solo aims to reach the far carriage; rivals submit to the same train motion.

**First playtest question.** Can players read the cue in time using turn-based input?

### 17. The Witness Protection Sketch Artist

**Constrained likeness building.** Build a mascot portrait from a tray of faces and accessories. Halfway through, the witness clarifies that the moustache belongs to the bird. Revise only two pieces.

**Standalone result and player counts.** Count matching authored features. Solo compares against the description; rivals reveal portraits together. Any equally accurate depiction can tie.

**First playtest question.** Do players enjoy revealing imperfect portraits? Are corrections clear enough to act on?

### 18. The Floor Is Listening

**Acoustic path planning.** Cross a floor above a sleeping guest. Preview a board’s squeak, lay a movable rug and plot a route. Show and play the noise trail as the walker crosses.

**Standalone result and player counts.** Score distance under a visible noise budget. Solo targets the exit; rivals compare trails on identical floorboards.

**First playtest question.** Do testers place the rug differently after previewing a board?

### 19. Nothing to Declare

**Packing for retrieval.** Pack a suitcase with awkward objects while keeping likely inspection items reachable. Reveal a customs request and remove the item. Displaced objects cost moves.

**Standalone result and player counts.** Score requests fulfilled, then fewest removals. Solo uses a packing allowance; rivals face the same disclosed likelihoods and request sequence.

**First playtest question.** Can players explain why they buried the opera glasses under a swordfish?

### 20. Hold for Applause

**Cue timing.** Cross backstage during noisy beats of a performance. Preview sound and visual cues and trigger one sound effect. Poorly timed thunder can silence the audience during a proposal.

**Standalone result and player counts.** Count crossings covered by applause or the effect. Solo rehearses the route; rivals play through the same performance privately.

**First playtest question.** Does deciding when to spend the effect matter with the sound muted?

### 21. The Complaint Department

**Rule changes and recall.** Route complaints to urgent, routine or management trays under three visible policies. A new policy arrives halfway through. Recall one form before the trays close.

**Standalone result and player counts.** Count correctly routed forms against the published rules, including the recall. Solo runs a shift; rivals sort the same batch. Use a common generous reading window for the first test.

**First playtest question.** Does the recall produce a meaningful choice for a slower reader?

## Founder's ideas (2026-11-19)

The founder's own ideas from the AW-337 interview, recorded word for word on issue #395. Not yet ranked against the list above; AW-337 places them. Decisions D-142 (1 to 8 players, 2 to 4 common) and D-143 (fun first; skinned to the story when natural, openly a game when not; solo, pair or group) apply.

### F1. Battle of Wits

**Timed trivia, logic, math and puzzles.** Players race to answer questions and puzzles against the clock: trivia, logic, mental math, quick facts. The founder's source is the "battle of wits" in detective shows such as *Sherlock* and *House*, where the detective mumbles logic, does math in their head or spouts a random fact that later helps inspire a theory. It does not have to be tied to the story. Inspiration: Jackbox's murder mystery trivia game, with its mini-games to save your life and its final race to answer before the darkness catches up. The founder loves it but finds it "a bit too simple, watered down, and repetitive", with "so much more potential which is what inspired nightcap".

**Standalone result and player counts.** Rank by correct answers; solo against a target score; 2 to 8 race on the same questions. Open: who writes the questions. Written question banks need no approval; questions generated by a model would need a prompt, which is an AGENTS.md hard rule.

**First playtest question.** Does a mix of trivia, logic and math keep every player in it, or does one kind decide the winner?

### F2. Search and Find

**Hidden-object race.** Everyone gets the same busy, Where's-Waldo-style scene on their phone and pinches and pans to find hidden items before anyone else, glancing up at the TV between finds. A tap scores an item; players shout "found one!" When the timer ends or every item is found, the TV shows results from last place to first, then says what happens next and returns to the story. The existing Scene Sweep package (an evidence search race with no screen) is the nearest code.

**Standalone result and player counts.** Rank by items found, ties kept; solo against the clock; 2 to 8 on the same scene.

**First playtest question.** Is the scene big enough on a phone to search with pinch and pan, and does the TV pull eyes up between finds?

### F3. Lock Picking

**Solo, pair or group.** A player investigating finds a locked box with no key and may pick the lock. Only their phone shows the instructions and the lock; the others carry on investigating, may be picking locks of their own, or look over curiously. The player succeeds or fails. The same mechanic can be a solo game (one player found the box), a pair game (two found it at the same time) or a group game (everyone has access). It blends into a mystery easily, though that is not required (D-143).

**Standalone result and player counts.** Solo: open the lock before time runs out. Pair and group: first to open, or most locks opened. Open: how a pair game starts when two players find the same box (open-questions log, AW-345).

**First playtest question.** Does a player picking a lock alone feel focused and tense while the others notice and wonder?

## Where to start and how to maintain the list

Try *An Entirely Normal Walk* at two for the rival replay, *The Portrait Has an Alibi* alone for the viewpoint reveal, and *Of Course I Work Here* at four for uncoached bluffing. *The Emergency Seating Committee* is the cheapest paper trial: lay down guest cards, allow two swaps, then ask which guest each player knowingly inconvenienced. Paper is useful for selection; the eventual live test uses the minigame’s own entry point.

Add or revise a card here when an idea changes. Keep its title stable where practical, update ranks together, explain what a tester does and identify the observation that would move the idea up or down. Link dated playtest evidence when available. Record a founder selection on AW-337; a high rank alone does not select the mechanic for a build. Existing game packages are inventoried separately under [nightcap/mini_games](../../../../nightcap/mini_games/).
