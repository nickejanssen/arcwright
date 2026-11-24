---
id: productroadmap.roadmap.tasks.aw-362-research-solo-journaling-games-on-arcwright
namespace: product-roadmap
title: "AW-362: Research Solo Journaling Games On Arcwright And Recommend Go Or No-Go"
owner: Nico Janssen
status: draft
review_by: "2027-02-23"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: [solo, journaling, research]
supersedes: []
---

# AW-362: Research Solo Journaling Games On Arcwright And Recommend Go Or No-Go

**Milestone / Epic:** Post-M6 / none yet  
**Size:** M  
**Product:** Arcwright (Shared if a solo Nightcap mode is chosen)  
**GitHub issue:** [#493](https://github.com/nickejanssen/arcwright/issues/493)  
**Owner:** one research session, after the founder says when it may start  
**Target date:** after the Nightcap session on 15 December 2026 (D-149), unless the founder starts it sooner as research only

## Plain-English Summary

The founder thinks solo journaling tabletop games (one player, simple dice or card prompts, a written journal) could be Arcwright's single-player flagship: one game with many stories, a solo Nightcap mode, or a family of games on the engine. The direction is recorded in `docs/product/2026-11-23-solo-journaling-direction.md`. That record was written on low usage, without web research, the SME agents or GameGene. This task does the full research and returns a go or no-go recommendation with a cheap test design. It changes no code.

## Why This Matters

- Founder direction on 2026-11-23: "extremely promising", a possible 1p flagship, "Don't leave out details".
- The genre's split (rules resolve, the player or narrator writes) matches Architecture principle 2. Solo play avoids Nightcap's group, TV and sync problems, so it may be a cheaper proof of the engine's memory and personalisation.
- Main risks, unproven either way: the solo journaling audience may reject AI; player-written text must not become canonical state without a deterministic, player-confirmed path.
- Not approved scope (AGENTS.md Product Scope Approval Rules). Open question logged on 2026-11-23.

## Technical Scope

1. **Verify every reference game** from a primary source (publisher page, itch.io, rulebook): designer, how it is played, why it is special, a story summary, and the lesson for Arcwright. Update the table in the direction record and replace every Partial or Unverified label. Games: Home: Mech and Kaiju Mapmaking RPG; The Librarian's Apprentice; Just Roll With It; Alone on a Journey; Thousand Year Old Vampire; Void 1680AM; Colostle; Death of the Author; All Night Breakfast at the Midnight Owl; Ironsworn: Starforged; Koriko: A Magical Year; Apothecaria; DELVE; Artefact; Notorious; Eleventh Beast; Seven Murders Till Midnight; The Cold Dark. Check Seven Murders Till Midnight first (possible Nightcap link).
2. **Design precedent with GameGene:** look up claims, genes and joseki for prompt tables, oracles, memory loss, map drawing, card-driven exploration, cozy calendars and journaling. Cite pageUrls.
3. **Engine gap analysis with the SME agents** (arc-execution, knowledge-graph, session-runtime, character-behavior, model-routing, safety, developer-api; nightcap-sme for a solo Nightcap mode; daily-case-sme for overlap). Check each of the 11 engine needs in the direction record against the code, with file paths. Mark which are hard-rule changes.
4. **Player text to state:** propose options for turning a journal entry into state without AI deciding what happened. Draft an ADR outline only; do not decide.
5. **What players love, and tactility:** for each game, what players say they love (reviews, community posts), with the tactile parts called out (dice, cards, handwriting, maps, the finished journal). Say how each would be kept or adapted under the four tactile options in the direction record's Design stance. Founder direction (2026-11-24): adapt what players love, do not transplant the games.
6. **Market and audience:** market size, prices and the audience's view of AI, each with sources. No unsourced numbers.
7. **Cost:** estimate cost per player-hour for solo play under the routing table's tiers, with caching.
8. **Recommendation:** go or no-go, the first shape (anthology, solo Nightcap, separate titles), and a paper or Wizard-of-Oz test design with a success measure.

**Usage note:** this is a large job (about 20 to 40 web lookups, 8 SME calls, several GameGene queries). Cheapest full path: one session; batch the game lookups in parallel; one question per SME agent; GameGene by search terms, not full listings. Warn the founder of the size before starting.

## Human Collaboration Contract

**Interaction profile:** Decision interview plus independent research. The founder answers the four questions in the direction record (shape, who writes, when, tactile approach) one at a time with tappable options. The research itself is independent. No approval is inferred from this task existing.

## Acceptance Criteria

1. All 18 games have a verified row with a source link; no Partial or Unverified labels remain, or each remaining one says why it could not be checked.
2. Each of the 11 engine needs has a status (exists, partial, missing) with file paths and a hard-rule flag.
3. GameGene and SME findings are cited, and inferences are labelled separately from findings.
4. A go or no-go recommendation with confidence, first shape, test design and cost estimate.
5. The founder's answers are recorded in `docs/product/decisions-log.csv` only if the founder approves them in their own words.
6. No code, schema, prompt or dependency changes.

## Tests/Verification

Documentation only. Check that every claim in the direction record has a source or a confidence label, and that `python scripts/roadmap_status.py --task AW-362` resolves.
