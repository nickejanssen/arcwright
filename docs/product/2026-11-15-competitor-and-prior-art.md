---
id: productroadmap.product.2026-11-15-competitor-and-prior-art
namespace: product-roadmap
title: Competitor And Prior-Art Comparison, 2026-11-15
owner: Nico Janssen
status: active
review_by: "2027-02-15"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

> Current version: v1.0
> Last updated: 2026-11-15
> Status: Current (a dated record; prices and products change, so re-check before relying on a row)
> Canonical path: docs/product/2026-11-15-competitor-and-prior-art.md

# Competitor And Prior-Art Comparison, 2026-11-15

The output of task AW-316. It answers one question: which parts of what Arcwright does are already sold by someone else, and where is Arcwright actually different? It replaces the first-pass table in section 4 of the [reset audit](2026-11-15-reset-audit.md).

- **Method:** about twenty web searches and seven vendor pages read on 2026-11-15. No accounts were created, nothing was installed and no product was played.
- **Labels:** *vendor page* means read on the maker's own site on 2026-11-15. *Third party* means a review, a news article or a rival's comparison, which can be wrong or biased. *From memory* means not checked on the day.
- **Limit that matters:** nothing here was tested by playing. Every statement about how a product works is the maker's own claim.

## 1. The short answer

1. **The reset audit was wrong on one point.** It said nobody was found selling "a dungeon master for any game". Hidden Door now sells something close: a studio for modelling a world, a connection for AI assistants to build worlds, and an interface other products can call to run stories in those worlds.
2. **"Rules decide, the AI only voices" is no longer a difference by itself.** At least two products say the same thing in their own words.
3. **What nobody was found doing:** an AI-directed story for a group of people in one room, on a TV with phones, where the truth is fixed before play and can be checked for fairness. That is Nightcap. It is either a gap or a warning, and only a played session can say which.
4. **Recommendation:** no change of direction. Keep the games-first order, do not try to out-build Hidden Door on world modelling, and treat session 1 as the only proof that counts. One cheap founder step is added: play the two closest neighbours for twenty minutes each (task AW-323).

## 2. Who already does each part

| Part | Who does it | Price seen | Source | Position for Arcwright |
| --- | --- | --- | --- | --- |
| A story engine other people can build worlds on | **Hidden Door.** Atlas (a world-building studio), Creator MCP (build worlds from an AI assistant), Experience API (other products run stories in a world). Says every story turn is "checked against canon before anyone sees" it. Lists social games for many players online | None published. Free to play at launch in August 2025 | Vendor page; Variety, 2025-08 | **Closest neighbour.** Differ, do not copy. Their stories are generated inside world rules; Arcwright runs a person's written arc with a fixed truth. Revisit after session 1 |
| An AI game master for a group | **TableForge** (up to 6 players, tabletop rules resolved in code), **Friends and Fables** (new development paused until 2027, per a rival), **AI Dungeon** (shared free-form story, join by code) | TableForge: free, then $29.99 and $39.99 a month for the host | TableForge's own comparison, 2026-10-17, which is a rival's view of the others | Different product: online text campaigns of one rule set, each player on their own device. Not a room, not a TV, not any game |
| Talking characters | **Inworld** (now a runtime that chains speech and models, plus voices; its character studio is retired, per a third party), **Convai** (characters with a knowledge bank and a "narrative design" flow), **NVIDIA ACE** | Inworld voices: $25 per million characters on demand, $15 for the fast model. Convai: not re-checked today | Vendor pages for Inworld; third party for the rest | Crowded. Take voices only. Never let one of these decide what a character says |
| A writer-controlled branching story with a graph editor | **Charisma.ai** (stories are written straight into a story graph) | Credit bundles from $63, per a 2023 article | Vendor docs; third party for price | Mature. Import from a story tool (AW-306); do not rebuild one |
| Story-writing tools | Twine, articy:draft X, Arcweave, StoryFlow Editor, Ink, Yarn Spinner | See section 4 | Vendor pages for Arcweave and articy; third party for the rest | Adopt one (D-117, D-122) |
| Phones as controllers in a room | **Jackbox** (its own games only), **Playroom Kit** (a multiplayer service for web games) | Playroom: free for 10 daily users and non-commercial use; $10 a month for 10,000 monthly users | Vendor page | Already built in the repository. Do not adopt Playroom: it would hold the session state, and the engine must own it |
| AI murder mysteries | Perdify, Auferet, DetectivesGame and several hobby projects: question AI suspects by text or voice, then accuse | Not checked | App store and maker pages, read as search excerpts only | All found are solo or online chat. Many write a new murder each time, which is the opposite of a fixed, fair truth. Shows demand and shows the easy version is crowded |
| A pacing director | Left 4 Dead's AI Director; the drama manager in Facade; Versu | Not products for sale | From memory | Prior art for the idea, not a competitor. Nothing to adopt |

## 3. The four claimed differences

| Claim | Verdict | Why |
| --- | --- | --- |
| Rules decide the outcome; the AI only voices it | **Partly holds. Not unique.** | TableForge says its "rules engine owns the outcomes" (vendor page). Hidden Door says each turn is checked against canon and rules (vendor page). What was not found elsewhere: a mystery whose truth is fixed before play and checked for fairness by code. That narrower claim holds as a design and is untested with players |
| Characters speak only from what they know, with a record of who told whom | **Partly holds. Unproven.** | Rivals advertise character knowledge and memory. Nobody was found publishing a who-told-whom-and-when record that limits what a character may say. That is not proof they lack one. Inside the repository this exists and is tested; no player has seen it matter |
| It directs a group of real people in one room | **Holds today.** | Every AI game master found is an online campaign on separate devices. Every room-and-phones product found has no story engine. Nobody was found doing both |
| One shape of play record across every game | **Holds, and is worth nothing yet.** | Not found elsewhere, but it cannot be seen from outside. Hidden Door promises authors information on how fans play, which is the same idea as a business feature. It becomes a real difference only when a second game exists |

## 4. Story tools against D-122

D-122 requires a graph view the founder can edit. That requirement changes the shortlist for AW-306, and corrects one row of section 2.11.4 of the [technology stack](../architecture/02-technology-stack.md).

| Tool | Editable graph view | Price and licence | Gets data out | Passes D-122 |
| --- | --- | --- | --- | --- |
| Twine | Yes, a map of passages | Free, GPL-3.0 (third party; verified 2026-11-14) | Twee text and HTML (from memory); no built-in JSON (third party) | Yes |
| articy:draft X FREE | Yes, a flow chart | Free, commercial use allowed, 700 objects per project, all exports (vendor page) | JSON and XML | Yes |
| Arcweave | Yes, in the browser | **The free plan may not be used for commercial projects** (vendor page). 3 projects, 200 items each. Pro is $15 to $18 a member a month | JSON on every plan; API only from $25 to $30 a member | Yes for a trial; not on the free plan for a product |
| StoryFlow Editor | Yes, nodes | $30 once (the maker's own blog) | JSON, HTML | Yes; least proven |
| Ink | No. Text script only | Free, MIT | JSON through its compiler | **No, as the main tool** |
| Yarn Spinner | No. It draws a chart you cannot edit (third party) | Free, MIT core | Its own format | **No, as the main tool** |

**What this means for AW-306:** the two tools with the strongest story logic, Ink and Yarn Spinner, fail the founder's own requirement. The choice is now between Twine, articy:draft X FREE and Arcweave. The choice stays the founder's and is made inside AW-306, after trying them.

## 5. What was not done

- No product was played. Task AW-323 covers the two closest.
- Convai and NVIDIA ACE pricing was not re-checked today.
- Hidden Door's terms for outside creators, and its prices, are not published and were not found.
- The claims about what rivals lack are "not found", not "does not exist".
- The note in section 2.11.6 of the technology stack, that middleware alone has rarely reached very large outcomes, is still from memory and was not researched.

## 6. Sources

All read on 2026-11-15.

- Hidden Door: `https://www.hiddendoor.co/`; Variety, 2025-08, `https://variety.com/2025/gaming/news/hidden-door-ai-role-playing-fan-fiction-game-platform-1236488265/`; Forbes, 2025-08-14.
- TableForge: `https://tableforge.gg/blog/multiplayer-ai-dungeon-master-comparison` and `https://tableforge.gg/blog/friends-and-fables-vs-tableforge` (both dated 2026-10-17).
- Inworld: `https://inworld.ai/pricing`. Convai: `https://convai.com/`.
- Charisma.ai: `https://docs.charisma.ai/quick-start`.
- Playroom Kit: `https://joinplayroom.com/pricing`.
- Arcweave: `https://arcweave.com/pricing`. articy: `https://www.articy.com/en/articydraft/free/`.
- Story tool round-up from a rival maker: `https://storyflow-editor.com/blog/best-narrative-design-tools-for-game-developers-2025/`.
- AI murder mysteries: `https://auferet.com/ai-murder-mystery-game`; Perdify on the App Store; `https://intfiction.org/t/detectivesgame-a-new-ai-powered-murder-mystery-experience/78864`.
