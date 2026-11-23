---
id: productroadmap.roadmap.tasks.aw-361-keep-unruled-mini-game-presentation-off-the-tv
namespace: product-roadmap
title: "AW-361: Keep Mini-Game Presentation Without An Audience Rule Off The TV"
owner: Nico Janssen
status: draft
review_by: "2027-02-21"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# AW-361: Keep Mini-Game Presentation Without An Audience Rule Off The TV

**Milestone / Epic:** M7 / M7-B  
**Size:** S  
**Product:** Arcwright engine, with Nightcap mini-games as the first users  
**Owner:** One Claude Sonnet build session, after founder approval of its plan  
**GitHub issue:** [#484](https://github.com/nickejanssen/arcwright/issues/484)  
**Target date:** before AW-337 adds mechanics, and before the founder's test on 1 December 2026 (D-149)

## Plain-English Summary

The TV address needs no sign-in. When a mini-game type has no rule for what each audience may see, the engine sends the TV everything generated for that game's screens. A prompt meant for one phone could therefore appear on the TV. The safe default is that nothing is shared unless a rule allows it.

## Why This Matters

- Verified in code and recorded on #457: `build_run_view` (`engine/mini_games/audience_view.py:83-84`) copies the whole `presentation` when a mechanic has no `audience_rule`. Three of the four registered mechanics have none.
- Not tested: whether a real run's generated `presentation` holds phone-only text. The default should be safe either way.
- Privacy is enforced in the engine (AGENTS.md).

## Technical Scope

1. Make a mechanic with no audience rule send the shared display nothing from `presentation`.
2. Check what each shipped screen reads from `presentation` for `evidence-locker-breach`, `evidence-search-race` and `match-3-clue-race`. If a TV screen needs a public key, declare it in that mechanic's rule. Do not weaken the default.
3. Decide in the plan whether a signed-in player and the host keep today's view for a mechanic with no rule, and state why.
4. Prefer a rule that names what may be shown over one that names what must be hidden, if that fits the existing `AudienceRule`. Name the trade-off in the plan.

## Human Collaboration Contract

**Interaction profile:** Independent execution after plan approval. This changes a privacy boundary in the engine, so the founder approves the plan in his own words, in the build session or in his own issue comment.

## Acceptance Criteria

1. For a mechanic with no rule, the no-sign-in TV route returns an empty `presentation`.
2. A test proves a private key never reaches the shared display through the real API route.
3. Every shipped mini-game's TV screen still renders, or the plan names the exact gap.
4. `engine/` gains no reference to Nightcap, a game title or a murder mystery.
5. Each new test fails on `main` before the change and passes after it.

## Tests/Verification

- `pytest engine/tests/test_mini_game_audience_view.py api/tests/test_mini_game_views_api.py`, then `pytest engine/tests/`.
- `python -m ruff check engine api` and `python -m ruff format --check engine api`.
- `npm test --prefix dashboard` if a package or screen changes.
- All six pull request checks pass, and every review thread is answered and resolved.

## Dependencies

- AW-347 (pull request #461), merged.
- AW-337 should not add mechanics before this merges.

## Must Not Do

- Do not expose runtime state that is hidden today.
- Do not add a dependency, schema change or migration.
- Do not read or quote files in `nightcap/cases/`.

## Kickoff Prompt

> Implement AW-361 (#484). Read `AGENTS.md`, `HANDOVER.md`, this task and the orchestrator's comment on #457. Post the plan on the issue, name the hard rules it hits, and wait for the founder's own approval. Tests first. Do not merge.
