---
id: product.2026-11-23-solo-journaling-direction
namespace: product-roadmap
title: "Solo Journaling Games On Arcwright: Direction Record"
owner: Nico Janssen
status: draft
review_by: "2027-02-23"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: [solo, journaling, single-player, direction, research]
supersedes: []
---

# Solo Journaling Games On Arcwright: Direction Record

**Status:** Draft direction. Not approved scope. Recorded so the idea is not lost.
**Date:** 2026-11-23
**Raised by:** the founder, who called it "extremely promising" and a possible single-player (1p) flagship for Arcwright.
**Tracked by:** AW-362 (research, engine gap analysis and a go or no-go recommendation).
**Canonical path:** `docs/product/2026-11-23-solo-journaling-direction.md`

## Scope status

Nothing here is build scope. Under AGENTS.md (Product Scope Approval Rules), approval needs a row in `docs/product/decisions-log.csv` and, because this touches architecture and schemas, an ADR or approved spec. The open question is logged in `docs/product/open-questions-log.csv`. Nightcap's December dates (D-149) come first.

## How this record was made, and what is not yet verified

The founder had about 9% weekly usage left, so this session used the fallback the founder asked for: record the direction and file a ticket, instead of a full research run. No web searches were made. The Arcwright SME agents and GameGene were not called. The game notes below come from the founder's list and the writer's general knowledge, and each carries a confidence label:

- **Known:** the writer is confident of the core play loop.
- **Partial:** the broad idea is known, details need checking.
- **Unverified:** only the founder's one-line description or the title is known. Do not build on it until AW-362 checks a primary source (the publisher's page, itch.io, the rulebook).

Designer names are left out on purpose, because getting them wrong is worse than leaving them blank. AW-362 adds them from primary sources.

## The idea in one paragraph

Solo journaling tabletop games give one player a simple, repeatable loop: roll dice or draw cards, look up a prompt, and write what happens in a journal. The hook is the story and the player's sense of authorship, not the mechanics. The mechanics are light and shared across many games (prompt tables, oracles, card decks, progress tracks, maps, memory limits). Arcwright already does the hard part these games leave to the player: a human-authored arc, deterministic state, a knowledge graph, characters that remember, and personalised narration. Built on Arcwright, a solo journaling game could keep the authored structure and the player's freedom, and add a world that responds, characters that recall what the player wrote, and pacing that bends to them. The founder sees three shapes: one standalone game with many stories that share a loop; something tied to Nightcap; or a family of separate games on the engine.

## Design stance: adapt, do not transplant

Founder direction, 2026-11-24: "we would adapt and not just take the concept and plop it into a game." Arcwright takes what players love about these games and adapts it, keeping what paper does best and adding what only the engine can do. The reference games show what works. None of them is a template to copy.

**Tactility is a main reason people love the genre.** The founder named it directly. It covers rolling real dice, drawing and shuffling cards, handwriting in a notebook, drawing a map, and the finished journal as a keepsake. A screen-only version loses much of this, and loses the slow, ritual pace that makes the writing feel personal. Any design must say how it keeps or replaces each of these.

Options to test (ideas, not decisions):

1. **Hybrid play (likely the strongest).** The player keeps real dice, cards and a paper journal. Arcwright is the companion: it keeps state, remembers characters and past entries, answers oracle questions, and voices characters. The player enters a roll or draw, or the phone reads it. This keeps the tactile part and adds what paper cannot.
2. **Physical kit plus app.** A printed or boxed deck, a journal and dice designed for the game, linked to the app. This is also a product to sell, and fits print-and-play for a cheap first test.
3. **Digital tactility.** For screen-only play: dice you shake, cards you flip, handwriting or drawing input, haptics, sound, and a journal that looks and exports like a real book.
4. **A real keepsake at the end.** A printable or printed journal and map built from the player's own entries.

Arcwright's additions, in every option: a world and characters that remember, prompts that bend to what the player wrote, authored arcs with real payoffs, and continuity across sessions.

## The reference games

Each game was named for a reason. The "Lesson for Arcwright" column says what each one teaches.

| Game | Confidence | What it is and how it is played | Why it is special | Lesson for Arcwright |
| --- | --- | --- | --- | --- |
| Thousand Year Old Vampire | Known | You play a vampire across centuries. Roll a d10 minus a d6 to move up or down a book of numbered prompts. You write Experiences into a small set of Memories; when the set is full you must forget or move one into a Diary, which can be lost. You track Skills, Resources, mortal Characters and Marks. | Forgetting is the mechanic. The story is about loss, and the player chooses what the vampire loses. | The knowledge graph needs a capacity and a forgetting rule for the player character, applied deterministically. A prompt walk (move through a numbered table by dice) is a reusable arc pattern. |
| Ironsworn: Starforged | Known | Sci-fi solo, co-op or guided play. Moves resolve with an action die (d6 plus a stat) against two d10 challenge dice: strong hit, weak hit or miss. Oracles (random tables) answer questions about the world. Vows are tracked on progress tracks; momentum is a resource. | A complete, free-to-start toolkit that turns the rules into the game master. Large community and a proven solo audience. | Arcwright's deterministic resolver can run moves, oracles and progress tracks directly. This is the clearest model for a reusable solo rules layer and for "the engine is the GM". |
| Colostle | Partial | You explore a world that is one vast castle, with oceans and lands inside its rooms. A deck of playing cards drives exploration, encounters and combat. You may gain a Rook, a companion. | Wonder and scale from a tiny ruleset and a standard deck. | Card-deck state (what is drawn, what remains) as session state. A companion is a character object like any other (Architecture principle 4). |
| Koriko: A Magical Year | Partial | You play a young witch spending a year in a seaside town, making deliveries and meeting the town. Cards set the prompts across the seasons. | Cozy, low-stakes, calendar-shaped. Shows the market for gentle solo play, not only grim play. | A calendar (seasons, months) as the arc's spine. Recurring townsfolk who remember the player give the engine's character memory its best showcase. |
| Apothecaria | Partial | You play a witch who heals patients: gather ingredients across a region, brew remedies, treat ailments. Cards and dice drive patients, foraging and events. | A satisfying craft loop (gather, combine, treat) inside a journaling frame. | Inventory and recipe resolution as deterministic rules, with AI only narrating. A good fit for mini-games (foraging, brewing) slotted into a journal arc. |
| DELVE | Partial | You lead a group digging into the earth. Draw cards, draw a map as you go, place rooms and resources, and face threats from below. | The map is the journal. Play produces a drawing you keep. | Spatial state (a map or grid) owned by the engine. The surface renders it; the engine stays surface-agnostic (principle 1). Shareable output is a growth lever. |
| Home: Mech and Kaiju Mapmaking RPG | Unverified | From the title: map-making while mechs defend a home from kaiju. | Unknown until checked. Likely combines map drawing with escalating threat. | If confirmed: map state plus a threat clock; second data point after DELVE for map-driven play. |
| Artefact | Partial | You play a magical object across centuries, passing between owners. Prompts tell of each owner, what the object sees and how it changes. | An unusual point of view and a story told across generations. | Long time spans with many owners as characters, and a knowledge state that belongs to an object. Tests that "character" is general enough. |
| The Librarian's Apprentice | Unverified | Founder's note: a solo journaling game in an infinite library. | Unknown until checked. The infinite-library frame suits endless, procedural rooms. | If confirmed: an arc frame that can host many authored "books" (stories) inside one shell. Strong fit for "one game, many stories". |
| Just Roll With It | Unverified | Founder's note: role-play your way to a more fulfilling life. | Uses game structure for real-life goals and reflection. | Different product: wellbeing and habits. Needs care with safety, privacy and claims (it must not present as therapy). Shows journaling can reach non-gamers. |
| Alone on a Journey | Unverified | Founder's note: a collection of solo adventuring games. | Unknown until checked. A collection format. | If confirmed: evidence for the "anthology on one loop" business shape. |
| Void 1680AM | Partial | A solo playlist-building game: you play a late-night radio host broadcasting into the dark, and prompts lead you to choose real songs. | The output is a real playlist. The game reaches into the player's own life and taste. | Player input can be a real-world choice, not only text. Exports (a playlist, a map, a journal) are what players share. Any music-service link is a new integration and a hard-rule decision. |
| Death of the Author | Unverified | From the title, likely a game about an author and their work. | Unknown until checked. | If confirmed: meta-narrative play, where the player writes a story inside the story. |
| All Night Breakfast at the Midnight Owl | Unverified | From the title, likely a cozy night-diner game with strange visitors. | Unknown until checked. | If confirmed: a "visitors arrive" loop, which maps to authored characters entering a fixed place, one per session. |
| Notorious | Unverified | Title only. | Unknown until checked. | To be filled by AW-362. |
| Eleventh Beast | Unverified | Title only. | Unknown until checked. | To be filled by AW-362. |
| Seven Murders Till Midnight | Unverified | Title only; the name suggests a solo murder mystery against a clock. | If confirmed, the closest link to Nightcap. | If confirmed: a solo mystery could reuse Nightcap's case content, clue rules and knowledge graph. Highest priority to check. |
| The Cold Dark | Unverified | Title only. | Unknown until checked. | To be filled by AW-362. |

### Patterns across the list

Across the games the writer knows, the same few mechanics repeat: a prompt table walked by dice or cards; oracles that answer yes or no and "what is here"; a deck whose state matters; progress tracks or clocks; a map that grows; a limited memory or inventory; a calendar or generations as the spine; and companions or recurring characters. Every one of these is deterministic state plus narration, which is exactly the split Arcwright enforces (principle 2). The variety comes from the frame and the authored prompts, not from new mechanics. That is the case for "one engine, many stories".

## Assessment

**Verdict: promising, worth a cheap test after the Nightcap December sessions. Confidence: moderate.** The fit with the architecture is strong. The market and the audience's view of AI are the open risks.

### Why it fits Arcwright

- The engine's split already matches the genre: rules and dice resolve state, AI only writes from resolved state. Solo journaling games are that split done by hand.
- Solo play removes Nightcap's hardest problems: no group to gather, no TV, no phone sync, no social pacing. It is a cheaper way to prove the engine's personalisation and character memory.
- The knowledge graph is the selling point. A journal companion that remembers what you wrote three sessions ago, and a world where characters know only what they learned, is what pen-and-paper cannot do.
- One rules layer can carry many authored stories. Each new story is mostly writing, not code, which suits a content-pack model.
- Short sessions (10 to 30 minutes) suit phones and daily habit, and connect to the Daily Case idea.

### Business view

- **Shapes, best first:** (1) one app or game with a shared loop and many stories sold as packs; (2) a solo Nightcap mode that reuses case content between parties; (3) separate titles on the engine. Shape 1 tests the most with the least build. Shape 3 proves the platform to third-party developers but costs the most.
- **Revenue models to test:** paid story packs; a subscription for new stories; a free starter story. No numbers are claimed here. AW-362 must check market size and prices from sources before any forecast.
- **Platform value:** a solo rules layer (moves, oracles, decks, tracks, maps, memory) is reusable by Monster RPG and by outside developers. It would be the second arc family after Nightcap and test that the engine is general.

### Risks and honest objections

1. **The audience may reject AI.** Many solo journaling players value writing it all themselves, and the indie tabletop community is often hostile to generative AI. If the AI writes for the player, the core joy may be lost. Mitigation to test: the player stays the author; the engine keeps state, remembers, asks better questions and voices characters only when asked. This is the biggest risk and should be the first thing tested with real players.
2. **Player text and canonical state.** In these games the player writes what happened. Architecture principle 2 says AI must not decide what happened. The engine needs a rule for turning a player's journal entry into state: the player confirms structured facts, or uses choices and tags, or AI suggests tags that the player approves. AI must never set state on its own. This needs an ADR.
3. **IP.** The listed games are inspiration for what players love, not material to copy. Arcwright's games and stories are original, built to the adapt-not-transplant stance above, unless a licence is signed.
4. **Losing the tactile feel.** A screen-only design may lose what players love most (see Design stance). Test hybrid play early.
5. **Focus.** Nightcap has fixed dates (D-149). This must not draw build sessions away before then.
6. **Competition.** AI story apps already exist. The difference must be authored arcs, real memory and player authorship, and AW-362 should check the field.
7. **Wellbeing titles** (Just Roll With It style) bring safety, privacy and claims risk; keep them out of the first test.

## What the engine would need

Status of each against today's engine is not verified in code; AW-362 checks it. Items marked hard-rule need explicit founder approval under AGENTS.md.

1. **Solo session runtime:** a session with one player, no shared display, that can pause for days and resume (persistence and resume exist for Nightcap, specs 0042 and 0043; check they cover long gaps).
2. **Long-lived campaigns:** state that carries across many sessions. Overlaps with Nightcap Continuity (ADR 0006, v1.1 scope); align, do not duplicate.
3. **Randomness as logged, seeded state:** dice and card decks resolved by the engine with a recorded seed, so every outcome is reproducible and deterministic.
4. **Reusable solo rules primitives:** prompt tables, oracles, decks, progress tracks and clocks, a map or grid, inventory and recipes, a calendar. Authored in arc files, resolved in Python, never in TypeScript.
5. **Knowledge graph extensions:** a capacity limit and forgetting rules (Thousand Year Old Vampire), knowledge owned by objects (Artefact), and recall across sessions. Schema change: hard-rule.
6. **Journal entries as input:** free-text entries stored as player-authored content, with a deterministic, player-confirmed path from entry to state. ADR needed.
7. **Journal surface events:** structured events a surface can render as a journal, map or deck. No rendering logic in `engine/`.
8. **Exports:** journal, map and other outputs the player keeps or shares. A music or other third-party link is a new integration: hard-rule.
9. **Routing and cost:** solo play generates per player, not per group, so the cost per player-hour may be higher. Use cheap models for tagging and safety, cache the arc and character layers (principle 6), and budget it in AW-362.
10. **Safety:** introspective and dark themes (loss, horror, personal goals) need engine-layer safety settings that the arc cannot switch off.
11. **Mini-games:** foraging, brewing, mapping or deduction mini-games slotted into a journal arc, reusing the mini-game registry and the porting work (AW-322, AW-348, AW-349).

## Questions for the founder (logged, not answered)

1. Which shape first: shared-loop anthology, solo Nightcap mode, or separate titles?
2. Who writes: the player only, the player with AI help on request, or AI drafts the player edits? (This decides most of the design and the audience risk.)
3. When may this start: after the 15 December Nightcap session, or in parallel as research only?
4. How should the tactile part work: hybrid play with real dice, cards and paper; a physical kit plus app; digital tactility only; or a mix?

## Next steps

AW-362 holds the full plan: verify each game from primary sources, run the Arcwright SME agents and GameGene for design precedent, check the engine against the list above, size the market from sources, and return a go or no-go with a cheap paper or Wizard-of-Oz test design. It is research only and changes no code.
