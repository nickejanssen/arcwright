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

Decide which mini-game mechanics a Nightcap playthrough needs, then build or adapt each one so it plays well with two to four players. No mechanic repeats in one playthrough. The set is chosen for the game, not from what happens to exist in the repository.

For the creative interview, start with the [ranked standalone minigame idea bank](../../gdd/nightcap/04-supporting-design/minigame-idea-bank.md). Each candidate includes a case-free fixture, local result, player-count adaptations and a first playtest question. Record selected mechanics on this task’s issue.

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

Use [AW-348](https://github.com/nickejanssen/arcwright/issues/443) to exercise an existing game first. For the first fresh mechanic, propose **The Emergency Seating Committee**: eight guest cards, two seat swaps and immediate consequences. Record time from a fresh brief to the first playable link. Try one rule change and time the next round. After standalone and destination parity, propose **Of Course I Work Here** for private prompts, simultaneous reveal and an uncoached four-player round. **An Entirely Normal Walk** is a later showcase candidate. These are recommendations for the creative interview. The founder selects the games.

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
