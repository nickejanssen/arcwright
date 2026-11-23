---
id: productroadmap.roadmap.tasks.aw-337-give-small-groups-a-mini-game-that-fits
namespace: product-roadmap
title: "AW-337: Design And Build The Mini-Game Mechanics For A Playthrough"
owner: Nico Janssen
status: active
review_by: "2027-02-16"
sensitivity: internal
source: authored
x-scope-evidence: D-112, D-126
tags: []
supersedes: []
---

# AW-337: Design And Build The Mini-Game Mechanics For A Playthrough

**Milestone / Epic:** M7 / M7-B  
**Size:** L  
**Product:** Nightcap  
**Owner:** Founder creative interview first, then one AI build session per mechanic  
**Target date:** 2026-12-03 for the core variant's mechanics

## Plain-English Summary

Decide which mini-game mechanics a Nightcap playthrough needs, then build or adapt each one for the player counts it declares, from 1 to 8, tuned for the common case of two to four (D-142). Mini-games are fun first: skinned to the story when that is natural, openly a game when not (D-143). No mechanic repeats in one playthrough. The set is chosen for the game, not from what happens to exist in the repository.

For the creative interview, start with the [ranked standalone minigame idea bank](../../gdd/nightcap/04-supporting-design/minigame-idea-bank.md). Each candidate includes a case-free fixture, local result, player-count adaptations and a first playtest question. Record selected mechanics on this task’s issue.

## Founder Interview (2026-11-19)

The founder's open answer is recorded word for word on issue #395. In short: two layers of mini-game. Side solo mini-games happen on one phone during investigation while the TV stays quiet and others glance over (lock picking a box only one player found). Group mini-games are events: the TV switches from story to mini-game, everyone sees how it is played and what is at stake, results land on the TV from last place to first with groans and cheers, then the TV says what happens next and returns to the story (a search-and-find scene with pinch and pan on the phone).

Inspirations: Jackbox's murder mystery trivia game (trivia with mini-games to save your life, and the final race before the darkness catches up; in his words "a bit too simple, watered down, and repetitive", with much more potential, "which is what inspired nightcap"), the *Sherlock* and *House* "battle of wits" (timed trivia, logic, math and puzzles), and Mario Party (varied, competitive, creative mini-games everyone looks forward to). His three ideas are in the idea bank under "Founder's ideas".

Decisions from the interview: D-142 (1 to 8 players, 2 to 4 common) and D-143 (fun first; skinned when natural; solo, pair or group). Open questions in `docs/product/open-questions-log.csv`: how a pair mini-game starts (AW-345), and whether a solo run counts against no-repeat.

## Direction For The Version 1a Mechanics (2026-11-22, approved by the founder)

Creative interview held 22 November 2026 for the two mechanics version 1a needs: Battle of Wits and Search and Find. **This is direction approval only. It is not plan approval and authorizes no code.** The build plan for each mechanic needs the founder's own approval. Adding either mechanic is blocked until AW-361 (#484) merges.

Approval, his selection in the interview dialog: "Approve, record it (Recommended)". Settled earlier and not reopened: D-136, D-137, D-142, D-143, D-147, D-148, D-151, D-152.

### Battle of Wits

Feel, in the founder's words: "It is the same feeling as the last game in Murder Mystery Trivia. Racing to be right, trying to rember answers, fightinh the clock and cheering when you get soemthing correct, feeling short on time, feeling like even if you get behind theres still a chance and theres no winner until the game ends! Laughing at some answers, being wowed by others, feeling like you learned something."

**Chosen by the founder:**

| Choice | Decision | His words |
| --- | --- | --- |
| Direction | Speed race with catch-up help: the player in last place gets two wrong answers struck out on their own phone for the next question | Selected "B: speed race + catch-up help (Recommended)" |
| Answer format | Four buttons, plus drag-and-drop sorting | "four buttons, drag and drop sorting," |
| Sorting score | Partial credit per item in the right place | "partial credit, but every questions has a timer, so i dont think we need more points for faster" |
| Speed bonus | None anywhere; the timer is the pressure | Selected "No speed bonus anywhere (Recommended)" |
| Reveal pacing | After every question the TV shows the right answer, who got it and a running ranking; at the end it ranks last to first, names the winner and returns to the story | Selected "After every question, then a final ranking (Recommended)" |
| Question tone (for AW-355) | Real trivia with a witty host; funny questions and answers are fine if they are good quality. No question bank written here | Selected "Real trivia with a witty host (Recommended)", then: "The questions and answers can be can be funny too, but they shoudl still be good quality questions." |

**Proposed defaults, shown to him and covered by his approval, not chosen one by one:**

- Last place also gets one item pre-placed on a sorting question. If everyone is tied for last, no one gets help.
- Ties share rank and use the existing tie-break (D-152).
- A player who does not answer scores zero on that question and the round continues. A dropped phone can rejoin.
- Case questions (round 2) use only facts players have already seen and give no solution away (D-126).
- The final race is the same mechanic with a bigger prize. Its standing counts only in the existing tie-break (D-152).
- Declares 1 to 8 players, tuned for 2 to 4 (D-142). Must be played on its own first (D-151, AW-348).

### Search and Find

Feel, in the founder's words: "On the TV is a fun and elaborate creative scene that delights the eye and makes everyone smile from it being fun and humorous and clever. It feels familiar to anyone who has played "Houseplants and Hot Sauce: A Seek-And-Find Book for Grown-Ups", "The Great Big Animal Search Book", "Pierre the Maze Detective: The Search for the Stolen Maze Stone" and "A Sherlock Holmes Seek & Find Mystery: The Crimes of London" are really good examples you should use. Everyone has the same scene that is on their tv on their phone and they are able to pinch and pan to look closer at the scene to find everything. Everyone is racing to find the most items. Everyone is shouting when they find something. Jumping when the tv says "10 seconds left!", and they are looking back and forth from tv to phone to race to find the most items before the time goes out."

**Chosen by the founder:**

| Choice | Decision | His words |
| --- | --- | --- |
| Find rule | The TV shows the items to find; the first player to tap one claims it with their name; most claims wins | Selected "A: first finder claims it (Recommended)" |
| Wrong tap | A short freeze on that phone; no points lost; the length is tuned in testing | Selected "Short freeze on that phone (Recommended)" |

**Proposed defaults, shown to him and covered by his approval:**

- One drawn scene, identical on the TV and every phone, with pinch and pan. The scene is art work and is not designed here. The four books he named are the reference for feel; they were not read.
- The round ends when the timer runs out or every item is claimed. The TV calls "10 seconds left!".
- Taps that arrive together go to whichever the server received first. Ties share rank.
- Declares 1 to 8 players, tuned for 2 to 4 (D-142). Items are for fun and release no case facts (D-126).
- It is the control game with the same rules in every version (D-152), provisional.

### Decisions to record (for the orchestrator; this branch does not edit the decisions log)

1. Battle of Wits direction: speed race with catch-up help; four buttons plus drag-and-drop sorting; partial credit on sorting; no speed bonus anywhere; reveal after every question; tone per AW-355. Relates to D-151, D-152.
2. Search and Find direction: first finder claims each item; most claims wins; wrong tap freezes that phone briefly. Relates to D-152.
3. Open for the plans, not decided: exact question counts and timer lengths per round, freeze length, item counts, and which scene to draw.

### Next steps

- Wait for AW-361 (#484) to merge; no mechanic is added before it.
- A build session writes one plan per mechanic; each needs the founder's approval.
- Battle of Wits must be played on its own first (AW-348) before version 1a repeats it (D-151).

## Why This Matters

- Rewritten on 2026-11-19 after the founder answered spec 0095 Q4 (D-136). His words: "I want the best number fo mini-games to fit a playthrough, not just trying to force in whats possible given our current mini-game inventory. I would rather create more mini-games to make it correct than adjusted for the test." And: "Wrappers can change the style/aesthetic of the game to match the story, but it doesnt change the mechanic, so playing the same game mechanic multiple times in one playthrough of the game seems like what we wouldnt want to do."
- Prior art he endorsed: It Takes Two's director used most mechanics for one scene only, because repetition is why story games go unfinished (reset audit, section 3).
- Verified on main `a528cad` from each package's definition file: Scene Sweep (evidence search race, engine rules working, no screen, declared 4 to 8 players); Tell Me Something True (social truth bluff, rules working, the only working screen, 4 to 8); Crime Scene Smash (match-3 clue race, rules a stub, prototype screen, 4 to 8); Evidence Locker #402 (lock-breach puzzle, rules a stub, prototype screen, exactly 1). The founder notes some may already play at two or even one; the declared counts are settings, not tested limits.
- The first version of this task (2026-11-16) asked for one mini-game reused with wrappers; that is withdrawn.

## Technical Scope

- Creative interview with the founder first: what each round's mini-game should make players feel and do, which mechanic families fit a murder mystery for two to four players, and which existing packages are worth adapting. Bring prior art (party and co-op games he named as inspirations) into each option.
- Propose a set of distinct mechanics for the core session 1 variant (D-137), and optional extras for the A/B variants, including at least one suited to a solo mini-game (AW-345).
- For each chosen mechanic: Python rules and a `standing` (AW-328), the package definition with real player counts, and a phone and TV renderer (one small renderer task each, spec 0095 "Out of Scope"). Story wrappers come from the case writer (AW-305).
- No mechanic releases case information (D-126).

## Human Collaboration Contract

**Interaction profile:** Creative collaboration (mechanics, feel, player counts), then independent execution per mechanic after plan approval. Begin with the founder's open-ended vision, offer two or three advised directions, lock one, then build in reviewable batches. The founder approves each plan in its build session himself or by his own comment on this issue.

## Acceptance Criteria

- [ ] The founder has chosen the mechanics for the core variant and the optional variants; the choice is recorded on this issue.
- [ ] Each chosen mechanic starts, runs, ranks its players and returns to the story at two, three and four players (and one, where it is a solo mechanic).
- [ ] No mechanic repeats within any one playthrough variant.
- [ ] No mini-game releases case information (D-126).

## Tests/Verification

- `python -m pytest tests engine/tests api/tests -q`
- `npm test --prefix dashboard` once the dashboard tests exist (AW-329)
- Seen in play: the founder TV run (core variant) and session 1 variants (AW-346).

## Recommended prototyping sequence

The creative interview starts now and does not wait for AW-348 (D-141, 2026-11-19). Once [AW-348](https://github.com/nickejanssen/arcwright/issues/443) exists, use it to exercise an existing game and then each new mechanic. For the first fresh mechanic, propose **The Emergency Seating Committee**: eight guest cards, two seat swaps and immediate consequences. Record time from a fresh brief to the first playable link. Try one rule change and time the next round. After standalone and destination parity, propose **Of Course I Work Here** for private prompts, simultaneous reveal and an uncoached four-player round. **An Entirely Normal Walk** is a later showcase candidate. These are recommendations for the creative interview. The founder selects the games.

Start with current `AGENTS.md` and `HANDOVER.md`, the idea bank and the minigame skill. Use one builder per branch (Codex or Claude) and a second reviewer for difficult rules or boundaries. Use GameGene for a concrete precedent question and Superpowers for design, debugging or verification when useful. Prefer the existing toolchain. Suggested tests are fixed-input Python rules checks and isolated browser players using Playwright or the existing equivalent. Test declared counts, including 1–8 where claimed; record which counts real people played. Observe whether people understand their first move and want another round. [AW-349](https://github.com/nickejanssen/arcwright/issues/444) owns the reusable porting guide.

## Dependencies

- AW-303, AW-328 (merged); AW-344 for several per round; AW-345 for solo; AW-329 to AW-332 for screens.
- Decisions: D-113, D-126, D-136, D-137. Spec: 0095 "Q4 Answered".

## Must Not Do

- Do not reuse one mechanic with different wrappers within a playthrough.
- Do not pick a mechanic only because it already exists; pick it because it fits, then reuse code where that helps.
- Do not open or read any real case file.

## Kickoff Prompt

> Read `AGENTS.md`, `HANDOVER.md`, this task, D-136 and D-137. Start with the founder's open-ended vision for the mini-games, one question at a time. Then propose two or three sets of distinct mechanics with prior art and a recommendation, and stop for his choice.
