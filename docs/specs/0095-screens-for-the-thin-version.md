---
id: engineeringpractice.specs.0095-screens-for-the-thin-version
namespace: engineering-practice
title: "Spec 0095: Screens For The Thin Version"
owner: Nico Janssen
status: active
review_by: "2027-02-16"
sensitivity: internal
source: authored
x-scope-evidence: D-112, D-118, D-123
tags: []
supersedes: []
---

# Spec 0095: Screens For The Thin Version

**Status**: Approved by the founder on 2026-11-19 (D-139, issue #355), with the answers to Q1 to Q5 (D-133 to D-138). This permits AW-329 to AW-334 to write their plans. Each plan needs the founder's approval before code. See "Founder Approval" at the end.

**Author**: Claude Code (Spec Author role) | **Date**: 2026-11-16 | **Task**: AW-302, the screens spec of three | **Checked against**: main at `83795a5`

**Canonical path**: `docs/specs/0095-screens-for-the-thin-version.md`

---

# Plain-language goal

When this is built, the whole thin game can be played on one TV and two to four phones, from typing the room code to answering the survey. The TV is the shared stage: the story, the clock, who is ready, and the big reveal at the end. Each phone is a private desk: what you can investigate, what you found, your mini-game controls and your final theory. Nothing private ever reaches the TV.

The screens show what the engine has already decided. They hold no game rules. Specs 0093 (rounds, investigations, mini-games) and 0094 (Last Call and the ending) build the rules; this spec builds what you see and tap.

**How the founder's feelings answer shapes it.** On 2026-11-16 you chose "I outsmarted you" as the feeling the screens protect first (D-128). So where the phone and the TV compete for attention, the phone wins during thinking time and the TV wins at the reveal. Section "How the feelings answer shapes the layout" says exactly where.

## What is fixed, what is open, how to review

| | |
| --- | --- |
| **Fixed by earlier decisions** | The thin version's contents (D-112, status page). Rounds, budget, mini-game start and return (spec 0093, D-124). Last Call, the theory check, the winner rule and the closing order (spec 0094, D-125). A mini-game win gives one extra investigation and no case information (D-126). Build what is unique, adopt the rest (ADR-0026, D-114). |
| **Proposed here, approved if you approve** | The eight decisions under "What you are approving", every screen in "Every screen, in play order", and the build order. |
| **Open** | Five questions at the end, each with a recommended default you can accept with one word. |
| **Not checked on a real TV** | Everything in this spec comes from reading code and documents. Nobody has watched either screen codebase run since August. "What the walkthrough must confirm" lists every claim that only AW-301 can prove. |

**How to review it.** Read this section, "What you are approving", and "How the feelings answer shapes the layout" (about fifteen minutes). Skim the wireframes in "Every screen, in play order"; they are plain-text sketches with placeholder content, not designs. Then answer the five questions. "Your steps" has the clicks.

**Spoiler safety.** No wireframe or example in this file uses content from the first case. Every case-specific word is a placeholder in square brackets, such as `[subject label]`.

---

# What you are approving

| Part | What it does | Build task |
| --- | --- | --- |
| K. One client | `dashboard/` becomes the one client for TV and phone. Three parts are copied in from `nightcap-web/` | AW-329, AW-330 |
| L. The screens | Every screen in play order, for the TV, each phone and the host | AW-330, AW-332, AW-333 |
| M. What the engine must add for the screens | A room view the TV can read without a player's sign-in, no new seats after the game starts, per-player survey answers | AW-331 |
| N. Reconnecting and host controls | A phone that closes its tab comes back to where it was. The host can start, pause, resume, move on and end | AW-330, AW-331 |
| O. The proof | A scripted run of a full game that checks every screen and every privacy rule without a TV | AW-334 |

**Decisions that are approved if you approve this spec.** Each is the author's recommendation and each is cheap to change later (D-127).

1. **One client: `dashboard/`.** It already uses React and the connection kit (`sdk/`), and it is what the rehearsal script starts (`scripts/rehearsal.py:459`, verified by reading). This follows the inventory (spec 0092 work package 0, section 8), which you reviewed without changes. React is already a dependency there, so the open question "may the surviving client add React" needs no new dependency. `nightcap-web/` is not deleted, moved or changed: it keeps its tests and stays the Cloudflare Worker that `deploy-web.yml` publishes. The thin version simply does not use its screens.
2. **Copy three parts across, do not move them.** The mini-game kit (`nightcap-web/src/mini-game-kit/`, 9 files), the package screen loader (`nightcap-web/src/mini-games/`, 5 files) and the privacy-test approach. Copying keeps `nightcap-web/` working and makes the change easy to undo. One correction to the inventory: the privacy tests test `nightcap-web`'s own page builder and its own API client (`nightcap-web/tests/privacy-matrix.test.ts:4`, verified), so they cannot be copied as they are. Their matrix (each role against each audience) is rewritten against the dashboard. The mini-game privacy test (`tests/mini-game-privacy-matrix.test.ts`) tests the kit alone and copies across.
3. **A phone remembers its sign-in after the tab closes.** Today the phone keeps its sign-in in storage that dies with the browser tab (`dashboard/src/api/auth.ts:78`, verified). It moves to the browser's long-lived storage, so reopening the join link returns the player to their own seat, notebook and draft.
4. **No new seat after the game starts.** Today joining with the code always adds a new player, even mid-game (`engine/session/service.py:574`, verified). A player who lost their tab and joined again would get an empty second seat. After start, the join screen says to use the phone you joined with. Recovering on a different phone is not in session 1; the host cheat sheet (AW-308) covers it.
5. **Every screen can rebuild itself from routes.** The live event stream makes screens fast, but it is held in memory and lost when the API restarts (spec 0093). Each screen reads its state from routes on load and after any reconnect.
6. **The TV never holds a player's sign-in.** It reads only routes and events meant for the shared screen. A phone reads its private mini-game view with its own sign-in. Today the phone reads it from an address that needs no sign-in at all, only the player's character ID (`dashboard/src/api/miniGame.ts:55`, verified); that address is closed to anyone without the matching sign-in.
7. **The survey is on the phones.** Three taps per player, matching the pass bar on the status page: fun (1 to 5), felt like a detective (1 to 5), play again (yes, maybe, no), plus an optional comment. Saved per player as events, with no table change. The only survey route today records one host-reported answer per session (`api/routers/sessions.py:221`, verified).
8. **No new look, motion or sound library for session 1.** Plain text, the colours and type already in the dashboard, and the browser's own transitions (technology stack 2.11.7, AW-309). Line-by-line staging of the story on the TV uses the presentation hints on each event (D-070). The visual design system (spec 0069) is applied only where it costs nothing extra; the rest waits for "motion on the TV", item 5 of the if-it-fits list.

**Hard rules this spec touches (AGENTS.md).**

| Hard rule | Touched | Detail |
| --- | --- | --- |
| New dependencies, or any `package.json` change | **Yes, `package.json` only** | No new package. `dashboard/package.json` gains a `test` script, and the Vite config gains one name alias so package screens find the kit. Tests use Node's own test runner and the server renderer already inside `react-dom`, the same approach `nightcap-web` uses today (`nightcap-web/package.json`, verified) |
| Changes across engine modules | **Yes, small** | `engine/session` (room view, seat rule, survey answers) and thin API routes. Reads, not new rules |
| Database tables or migrations | **No** | Survey answers are events. The room view reads what specs 0093 and 0094 save |
| Prompts or evaluation suites | **No** | No model call |
| Secrets or sign-in | **Yes** | Decision 3 changes where a phone keeps its sign-in. Decision 6 closes an address that hands out a player's private mini-game view without a sign-in. The Q1 answer (D-133) lets a player's sign-in pause and resume and moves the host role to a player's seat (Part M, M6) |

---

# References

- Umbrella: [spec 0092](0092-nightcap-gdd-rebuild.md), work package 14 (surfaces) and phase gate 4 ("approve low-cost samples (wireframes, sample copy) before each surface"). The wireframes here are that sample for the thin version.
- Inventory: [spec 0092 work package 0](0092-wp0-thin-version-inventory.md), sections 2, 5, 6 and 8. Founder review on issue #353, 2026-11-16.
- Builds on: [spec 0093](0093-engine-spine-for-the-thin-version.md) (phases `scene`, `choices`, `mini_game`, `bridge`; routes for the menu, a choice, ready, holdings, host move-on, and the current beat, phase and deadline) and [spec 0094](0094-endgame-for-the-thin-version.md) (phases `commit`, `reveal`, `result`, `recap`; routes for the theory form, draft, lock and result).
- GDD: [current design state](../gdd/nightcap/00-governance/02-current-design-state.md), [notebook and memory](../gdd/nightcap/01-authoritative-gdd/03-case-board-memory.md), [minigames](../gdd/nightcap/01-authoritative-gdd/04-minigame-competitive-pulse.md), [Last Call and Case File](../gdd/nightcap/01-authoritative-gdd/05-last-call-case-file.md), [Truth, Verdict, Postmortem](../gdd/nightcap/01-authoritative-gdd/08-truth-verdict-postmortem.md), [difficulty and accessibility](../gdd/nightcap/01-authoritative-gdd/10-difficulty-accessibility.md), [content boundaries](../gdd/nightcap/01-authoritative-gdd/12-experience-world-content-boundaries.md) (no internal names on screen).
- Stack: [technology stack 2.11.7](../architecture/02-technology-stack.md) (AW-309), [ADR-0026](../decisions/0026-build-what-is-unique-adopt-the-rest.md).
- Scope: [Nightcap status page](../product/nightcap-status.md). Decisions D-070, D-112, D-113, D-118, D-123, D-124, D-125, D-126, D-127. D-128.
- Related specs: 0069 (visual design system, approved July 2026), 0049 (mini-game API and SDK).

**x-scope-evidence**: `D-112`, `D-118`, `D-123`. This spec adds no product scope beyond the thin version's must-have list. The survey and the reconnect rule are on that list.

---

# Overview

Make `dashboard/` the one client, copy in the mini-game kit and loader, add a screen for each phase kind from specs 0093 and 0094 on the TV and the phone, add the few engine reads the screens need, and prove a full game's screens with a scripted run, so the founder TV run (by 2026-12-05) has screens to play on.

---

# What the code does today

Checked by reading code on 2026-11-16. Nothing was run. Line numbers will drift.

- **Four screens exist** in `dashboard/src/` (2,615 lines): the TV page (`/display/<session>`, `DisplayScreen.tsx`), the join page (`/join`), the phone's waiting page (`/waiting`, `WaitingScreen.tsx`), and hand-written screens for one mini-game, Tell Me Something True (`screens/tmst/`). Verified.
- **The host's controls are on the TV page.** The rehearsal script opens the TV page with the host's sign-in in the address (`scripts/rehearsal.py:343`). The only host control is "Start case" (`DisplayScreen.tsx:338`). Pause, resume and end exist as routes but have no button. Verified.
- **The phone polls every two seconds** for the lobby and the active mini-game, and does not listen to the event stream (`WaitingScreen.tsx:85`). Its only action is a free-text box that moves the old game on. Verified.
- **The TV listens to the event stream without a sign-in.** The API treats that as the shared screen and sends it no private events (`api/routers/events.py:65`). Verified by reading; not tested live.
- **The TV shows the beat's internal name**, not its story (`DisplayScreen.tsx:349`). Verified; already noted in spec 0093.
- **The TV's join QR code is drawn by an outside website** (`api.qrserver.com`, `DisplayScreen.tsx:298`). The join link goes to that site, and the QR fails without internet. Verified by reading.
- **Only one mini-game package has a real screen.** Tell Me Something True has a kit renderer (`nightcap/mini_games/tell-me-something-true/client/renderer.ts`). Crime Scene Smash and Evidence Locker #402 have visual prototypes that do not talk to the engine (their `client/README.md` says so). Scene Sweep has none. Verified.
- **No mini-game package is written for two or three players.** Three declare 4 to 8 players; Evidence Locker #402 declares exactly 1 (`definitions/0.1.0.json` of each, verified). Nothing in the engine enforces these numbers when a run is created (search of `engine/mini_games`, inferred). Session 1 has 2 to 4 players and the founder TV run has 2. See Q4.
- **API tests do not run in CI.** The required `verify` check runs `tests/` (`Makefile:12`); the CI job runs `engine/tests` (`.github/workflows/ci.yml:101`); `api/tests` is run by neither. Inferred from reading the workflows. This matters for the proof in Part O.

---

# Every screen, in play order

**How to read this section.** Each screen has a text sketch (a wireframe) for the TV and the phone, then what it shows, what a player can do, what feeds it, and what must never be on the TV. "Feeds" names the engine event or route. A route marked **(gap)** is one specs 0093 and 0094 do not provide; Part M adds it.

**Two surfaces and one role.**

- **TV**: the shared screen, 1920 by 1080, read from the sofa. Never signed in as a player.
- **Phone**: one per player, 375 by 812. Two tabs on every in-game screen: **Now** (what to do in this phase) and **Notebook** (what you found). A header shows your name, the round, the time left and, when it matters, your investigations left.
- **Host**: the first player to join, who can hand the role to another seated player (Q1, D-133). The host plays on their own phone like everyone else. Every phone has a **Start menu** (Pause, Resume, Settings); the host's Start menu also holds the host controls. It shows only room-safe facts: phase, time left, who is ready or locked. Never case content. This also keeps a host who is playing unspoiled and without an advantage. The TV has no controls.

**Phase kinds and their screens.** Every in-game screen is chosen by the phase kind the engine reports. The screens add no order of their own.

| Order in play | Phase kind (spec) | TV screen | Phone screen |
| --- | --- | --- | --- |
| Before start | none | 1. Room | 2. Join, 3. Seated |
| Opening and each round | `scene` (0093) | 4. Story | 5. Eyes up |
| Each round | `choices` (0093) | 6. Thinking time | 7. Investigate, 8. Finding, 9. Notebook |
| Each round | `mini_game` (0093) | 10. Mini-game, shared view | 11. Mini-game, phone view, then 12. Mini-game result |
| Each round | `bridge` (0093) | 4. Story | 5. Eyes up |
| Last Call | `commit` (0094) | 13. Last Call | 14. Your theory, 15. Locked |
| Accused reveal | `reveal` (0094) | 16. The accused | 5. Eyes up |
| The Truth | `scene` with the closing lines (0094) | 4. Story | 5. Eyes up |
| The Verdict | `result` (0094) | 17. Verdict | 18. Your result |
| The Postmortem | `recap` (0094) | 19. Postmortem | 20. Your line |
| After the last phase | none | 21. Thanks | 22. Survey |
| Any time | Paused | 23. Paused | 23. Paused |

## 1. TV: Room

```
+--------------------------------------------------------------+
|                          NIGHTCAP                            |
|                                                              |
|     Join on your phone              [QR]                     |
|     [join address]                                           |
|                                                              |
|                 ROOM CODE   K 7 Q P                          |
|                                                              |
|   Seated:  [Name A]   [Name B]   ( . )   ( . )               |
|   2 to 4 players                                             |
|                                                       [host] |
+--------------------------------------------------------------+
```

- **Shows:** the room code in large type, the join address, a QR code, who has sat down, the player range.
- **Can do:** nothing on the TV. The host starts the game from **Start game** in their phone's Start menu (enabled at two or more players).
- **Feeds:** `GET /v1/sessions/{id}/lobby` (exists); host **Start** is `POST /v1/sessions/{id}/start` (exists).
- **Never on the TV:** the host's sign-in or any player's sign-in. Today the host's sign-in is in the address bar fragment, which is not drawn on the page; the build keeps it that way.

## 2. Phone: Join

```
+---------------------------+
| NIGHTCAP                  |
|                           |
| Your name                 |
| [_____________________]   |
| Room code                 |
| [K7QP_________________]   |
|                           |
| [        Join          ]  |
+---------------------------+
```

- **Shows:** name and code fields; the code is filled in when the player came from the QR code.
- **Can do:** join. If this phone already has a seat in this game, it skips this screen and goes straight back into the game (decision 3). If the game has started and this phone has no seat, it says so plainly (decision 4).
- **Feeds:** `POST /v1/lobby-join` (exists; the rule against new seats after start is Part M).

## 3. Phone: Seated

```
+---------------------------+
| You're in, [Name A].      |
|                           |
| Waiting for the host to   |
| start. Look at the TV.    |
|                           |
| Seated: [A] [B]           |
+---------------------------+
```

- **Feeds:** the lobby route (exists).

## 4. TV: Story (scene, bridge and the Truth)

```
+--------------------------------------------------------------+
|  [Round title]                                    0:45       |
|                                                              |
|     [Host line, shown as text, one line at a time]           |
|                                                              |
|     [Next line appears after its authored hold]              |
|                                                              |
|  Ready:  [A] ok    [B] ...    [C] ok                         |
+--------------------------------------------------------------+
```

- **Shows:** the round's title, the written lines of the scene or bridge, one at a time, with the speaker's name when the line has one, and who has marked ready. The host's lines are written by a person and shown as text (status page must-have). In the Truth, the lines are the case file's `closing` lines.
- **Can do:** nothing; players mark ready on their phones.
- **Feeds:** the scene and bridge line events with their presentation hints (spec 0093, Part C); the closing lines (spec 0094, Part J). For a reload or an API restart: the room view (gap, Part M), which carries the current phase's lines and who is ready. The round title is the beat's `beat_name` from the arc file (verified that the field exists, `engine/arc/models.py`), which the case author writes as player-facing text. It is never the beat's ID.
- **Never on the TV:** anything from a player's menu, holdings or theory.

## 5. Phone: Eyes up

```
+---------------------------+
| Round 2         0:45      |
| -------------------------  |
|                           |
|   Eyes on the TV.         |
|                           |
| [      I'm ready       ]  |
|                           |
| [ Now ]   [ Notebook ]    |
+---------------------------+
```

- **Shows:** a prompt to look up, the time left. In the opening, it also shows "Who you are": the opening items every player holds (spec 0093, `opening`), so a player can read them at their own pace.
- **Can do:** mark ready (not in the reveal, verdict and Truth phases, which run on the authored clock or the host); open the notebook.
- **Feeds:** mark ready (spec 0093, Part D route); holdings (spec 0093, "read what I hold").

## 6. TV: Thinking time (choices)

```
+--------------------------------------------------------------+
|  [Round title]                                               |
|                                                              |
|                 Investigate on your phones.                  |
|                                                              |
|                           2:30                               |
|                                                              |
|  Ready:  [A] ok    [B] ...    [C] ...                        |
+--------------------------------------------------------------+
```

- **Shows:** the round title, a large clock, who is ready. Nothing moves except the clock (see "How the feelings answer shapes the layout"). Nothing else is shown here: Q2 answered, option 1 (D-134).
- **Feeds:** the room view (gap, Part M) and phase events (spec 0093).
- **Never on the TV:** what anyone chose, how many investigations anyone has spent or has left, what anyone found, or any menu item. Spec 0093 already sends the TV no content from a choice; this spec adds that the TV draws no count either. A rival activity feed is item 4 of the if-it-fits list and is not in this spec.

## 7. Phone: Investigate (choices)

```
+---------------------------+
| Round 2   2:30   4 left   |
| -------------------------  |
| Look into:                |
|                           |
| [Person] [subject label]  |
|   [choice label]   new  1 |
| [Place]  [subject label]  |
|   [choice label]   seen 0 |
| [Object] [subject label]  |
|   [choice label]   new  1 |
|                           |
| [      I'm ready       ]  |
| [ Now ]   [ Notebook ]    |
+---------------------------+
```

- **Shows:** every choice on this player's menu, grouped under the subject it is about, with its kind (person, place, object, record), whether it is new or already seen, and its cost. Investigations left in the header. The number comes from the engine; the phone never works it out.
- **Can do:** tap a choice, then confirm ("Spend 1 of your 4?"). A seen choice opens again at no cost and without a confirm ("review is free"). Mark ready. When none are left, the menu still opens seen choices and says "No investigations left. You can still reread."
- **Feeds:** read my menu, choose (spec 0093, Part D). Each choice carries an ID made on the phone before sending and reused on a retry, so a dropped connection never spends twice (spec 0093 already makes a repeated ID have one effect).
- **Never on the TV:** all of it.

## 8. Phone: Finding (after a choice)

```
+---------------------------+
| [Subject label]           |
| -------------------------  |
| [The written content the  |
|  player gets back, as the |
|  case author wrote it]    |
|                           |
| Saved to your notebook.   |
| [   Back to the list   ]  |
+---------------------------+
```

- **Shows:** the written content of that choice, exactly as written. No highlight, label or ranking that hints at importance (GDD notebook chapter: "It may not rank significance").
- **Feeds:** the choose route's answer, and the private event spec 0093 sends to that player only.

## 9. Phone: Notebook

```
+---------------------------+
| Notebook        3 found   |
| -------------------------  |
| [Person] [subject label]  |
|  - [item label]   Round 1 |
|  - [item label]   Round 2 |
| [Place] [subject label]   |
|  - [item label]   Round 2 |
| At the start              |
|  - [item label]           |
|                           |
| [ Now ]   [ Notebook ]    |
+---------------------------+
```

- **Shows:** what this player found themselves, grouped by the subject it came from, in the order found, with the round. Tapping an item shows its full text. This is the status page's "simple notebook: a list of what you personally found", arranged by objective facts only (who, where, what), which the GDD allows. No "supports", "contradicts" or "suspicious" labels.
- **Can do:** read. Private notes, living suspect cards and the Case Board are if-it-fits items 2 and 6 and are not in this spec.
- **Feeds:** read what I hold (spec 0093, Part D). That route must return, for each held item: its label, its text, the subject it came from (or "at the start"), and the round it was found in. If AW-325's route does not include the subject and round, AW-331 adds them.
- **Never on the TV:** all of it. Never on another player's phone: all of it.

## 10. TV: Mini-game, shared view

```
+--------------------------------------------------------------+
|  [Story wrapper title for this mini-game]          0:40      |
|                                                              |
|      [The package's shared-screen view: board, scores,       |
|       spotlight, whatever the package draws]                 |
|                                                              |
+--------------------------------------------------------------+
```

- **Shows:** the mini-game package's own shared-screen view, mounted by the loader (Part K). The dashboard's hand-written Tell Me Something True screens are replaced by that package's own renderer. At the end, the standing: who placed where.
- **Feeds:** `GET /v1/sessions/{id}/mini-games/active/display` without a character ID (exists); mini-game events (exist); the run's standing (spec 0094, Part I, built by AW-328).
- **Never on the TV:** any player's private mini-game input, and any case information (D-126: a mini-game gives none in session 1).

## 11. Phone: Mini-game, phone view

- **Shows:** the package's own phone view, mounted by the loader. The kit already handles the countdown, double-submit guarding and an audience check (`nightcap-web/src/mini-game-kit/`, verified by reading).
- **Feeds:** `GET /v1/sessions/{id}/mini-games/active` with the player's sign-in (exists, `api/routers/mini_games.py:399`), and the submissions route (exists). Not the display address with a character ID (decision 6).

## 12. Phone: Mini-game reward card

```
+---------------------------+
| You earned one more       |
| investigation.            |
|                           |
|            5 left         |
| [         OK           ]  |
+---------------------------+
```

- **Shows:** the saved mini-game reward once per grant, and the remaining investigation count returned by the menu route. The player acknowledges each grant with OK. A later grant gets its own card.
- **Feeds:** `GET /v1/sessions/{id}/me/menu`, including `rewards` matched by `grant_id` and `remaining_budget`. Read on each phase change and after a mini-game phase. A live message is not required. Acknowledged grant IDs are kept in this phone's browser storage as a convenience.
- **No placing line:** no route returns the player's placing to this screen. The card reports the saved reward from the menu, not a standing or a rank. This follows the approved AW-332 plan on issue #435.

## 13. TV: Last Call

```
+--------------------------------------------------------------+
|                        LAST CALL                             |
|                                                              |
|                          3:00                                |
|                                                              |
|        Build your theory on your phone. Then lock it.        |
|                                                              |
|   [A] locked      [B] ...       [C] locked                   |
+--------------------------------------------------------------+
```

- **Shows:** the countdown and who has locked. Nothing else.
- **Feeds:** the room view (gap, Part M) and lock events (spec 0094 tells the shared screen only who has locked).
- **Never on the TV:** any part of any draft or lock, how many slots anyone has filled, and anything about right or wrong.

## 14. Phone: Your theory

```
+---------------------------+
| Last Call        2:41     |
| -------------------------  |
| [Slot 1 label, e.g. who]  |
|   [ choose... ]           |
| [Slot 2 label]            |
|   [ choose... ]           |
| [Slot 3 label]            |
|   [ choose... ]           |
|                           |
| Saved as you go.          |
| [   Lock my theory     ]  |
+---------------------------+
```

- **Shows:** the case's slots in the case's order (spec 0094, Part G). Tapping a slot opens a list: for a person slot, the cast members the case marks as selectable; for any other slot, everything this player holds, true and misleading alike, in the order the engine gives. The phone never reorders, filters or marks the list.
- **Can do:** fill and change slots; each change saves the draft. **Lock** is enabled when every slot is filled and asks once more: "Lock it? You can't change it after this."
- **Feeds:** read my theory form, save my draft, lock (spec 0094, routes).
- **Never on the TV:** all of it.

## 15. Phone: Locked

- **Shows:** "Locked. Waiting for the others." and the player's own theory, read-only.
- **Feeds:** read my theory form (spec 0094).

## 16. TV: The accused

```
+--------------------------------------------------------------+
|                       THE ACCUSED                            |
|                                                              |
|     [Name A] accuses ...                                     |
|                                                              |
|                    [CAST MEMBER]                             |
|                                                              |
+--------------------------------------------------------------+
```

- **Shows:** for each player, only the answer in the slot the case shows first (in Nightcap, who they accused). One player at a time, then all side by side (Q3, D-135). The staging and the order are Nightcap's, set in Nightcap's files and performed by Nightcap's screens; the order never depends on who is right.
- **Feeds:** the `reveal` event (spec 0094, Part J); the room view for a reload (gap, Part M).
- **Never on the TV:** any other slot of any theory, and anything about right or wrong.

## 17. TV: Verdict

```
+--------------------------------------------------------------+
|                       THE VERDICT                            |
|                                                              |
|                 [Name C] solved it.                          |
|                                                              |
|     [A] did not solve it    [B] did not solve it             |
|                                                              |
|     (or: "Nobody solved it. The case wins.")                 |
|     (tie: "[A] and [C] solved it. [A] won more mini-games.") |
+--------------------------------------------------------------+
```

- **Shows:** who won, or that nobody did; for each player, solved or not; and when a tie-break decided it, which rule did (spec 0094, Part I). This is the moment the feelings answer protects most: names land one at a time, the winner last and largest.
- **Feeds:** the public part of the result (spec 0094, `result` phase and the read-result route).
- **Never on the TV:** which slots any player got right or wrong. The GDD's Verdict may name "the decisive factual difference"; spec 0094 does not provide one, so session 1 shows solved or not only.

## 18. Phone: Your result

```
+---------------------------+
| Your theory               |
| -------------------------  |
| [Slot 1]  [answer]  right |
| [Slot 2]  [answer]  wrong |
| [Slot 3]  [answer]  right |
+---------------------------+
```

- **Shows:** which of your own slots were right and wrong. It appears on the phone only after the TV has finished showing the Verdict, so heads stay up for the room's moment.
- **Feeds:** the private part of the result (spec 0094), for its owner only.

## 19. TV: Postmortem

- **Shows:** one written line per player, one player at a time, chosen by rule from what they did (spec 0094, Part J).
- **Feeds:** the `recap` events (spec 0094).

## 20. Phone: Your line

- **Shows:** your own Postmortem line, so you can screenshot it. The same line is already public on the TV.

## 21. TV: Thanks

- **Shows:** "Thanks for playing. Answer three quick questions on your phone." and who has answered.
- **Can do:** nothing on the TV. The host's phone Start menu offers **End game** (exists, `POST /v1/sessions/{id}/end`), with a confirm.
- **Feeds:** the room view, which carries who has answered (gap, Part M).

## 22. Phone: Survey

```
+---------------------------+
| How fun was it?           |
|  (1) (2) (3) (4) (5)      |
| Did you feel like a       |
| detective?                |
|  (1) (2) (3) (4) (5)      |
| Play again?               |
|  (Yes) (Maybe) (No)       |
| Anything else? (optional) |
| [_____________________]   |
| [        Send          ]  |
+---------------------------+
```

- **Feeds:** **(gap)** a new "save my survey answers" route (Part M). Answers are private to the player and the play record; they never appear on the TV.

## 23. Paused (both)

- **TV:** "Paused." with the time that was left. **Phone:** "Paused by the host." Nothing can be sent while paused.
- **Feeds:** pause and resume (exist); the room view carries the paused flag and the time left (spec 0093 saves both).

---

# How the feelings answer shapes the layout

You chose "I outsmarted you": players feel clever and competitive, and the best moment is one player's theory landing while the others groan that they missed it. The other feelings (laughing together, being inside the story, playing each other) stay wanted and rank below it. Here is where that choice decides something.

| Where | When the phone and the TV compete | What wins | Why |
| --- | --- | --- | --- |
| Thinking time (screens 6 and 7) | The TV could show activity, jokes or rival moves; the phone needs attention to read and choose | **The phone.** The TV goes quiet: title, clock, ready. No sound, no new text, no animation except the clock | Private thinking wins. Watching rivals is "playing each other", which ranks lower and is an if-it-fits item |
| Last Call (13 and 14) | Same | **The phone.** The TV shows only the countdown and who has locked | Private thinking wins. Pressure is on deciding, not on watching others (GDD) |
| A phase ends while a player is mid-choice | The engine moves on; the phone could jump away | **The phone finishes its moment.** A finding already shown stays on screen with "Time's up. It's in your notebook." The theory form locks by rule (spec 0094), and the phone says so | Nobody loses a thought to a screen change |
| The accused, the Truth and the Verdict (16, 4, 17) | The phone could show the private result at once | **The TV.** Phones show "Eyes up" until the TV's Verdict has landed, then the private result appears | The big public reveal wins. The groan needs everyone looking at the same screen at the same second |
| The Verdict's staging (17) | One fast summary, or a reveal with holds | **Holds.** Players' outcomes one at a time, the winner last and largest | That is the moment the feeling lives in |
| Story lines (4) | Quick summary, or staged line by line | **Staged, but short.** Lines appear one at a time with their authored holds; players may mark ready to move on | "Inside the story" is wanted but ranks lower, so story never blocks a ready room |
| Speed | A tempting tie-breaker or display | **Never shown.** No "first to lock", no timing on any screen | GDD: speed is not a tie-breaker, and pressure is not reading speed |

---

# In Scope

## Part K. One client

- `dashboard/` is the one client. The TV page, the join page, the phone page and the phone's Start menu (with the host's controls) live there.
- Copied from `nightcap-web/` into `dashboard/src/`: the mini-game kit (`mini-game-kit/`) and the package screen loader (`mini-games/`), adapted to the dashboard's types and the connection kit. Package screens import the kit by the name `@arcwright/mini-game-kit` (verified in the Tell Me Something True renderer), so the dashboard's Vite config maps that name to its copy. No package's screen code changes.
- The dashboard's hand-written Tell Me Something True screens (`dashboard/src/screens/tmst/`) stop being used once the package's own renderer runs through the loader. They are not deleted by this spec.
- Privacy tests in `dashboard/tests/`: the role-against-audience matrix rewritten for the dashboard, and the kit's mini-game privacy test copied across. They run with Node's own test runner.
- `nightcap-web/` stays exactly as it is. Its hosting role is re-homed in AW-269 before session 3 (inventory section 8).

## Part L. The screens

- Screens 1 to 23 above, chosen by the phase kind the engine reports.
- Every screen reads its state from routes when it opens and after any reconnect, then follows events (decision 5).
- No game rule in TypeScript: no budget arithmetic, no right-or-wrong, no deciding what is on a menu or a theory list, no ordering of a list the engine gave. The screens show what routes and events say (AGENTS.md: no arc logic in TypeScript).
- No internal name on any screen: no beat ID, phase kind, concept ID or subject ID. Every visible word comes from the case file, the arc file or the screens' own fixed copy (GDD content boundaries).
- Accessibility, lean: TV body text at least 40 pixels high at 1920 by 1080; phone tap targets at least 44 pixels; ready and locked shown by a word and a mark, never by colour alone; the browser's reduced-motion setting is respected.
- Screen copy (button labels, prompts) is written in the plans for AW-330, AW-332 and AW-333 and shown to the founder as one sample of about twenty lines before code (spec 0092, phase gate 4).

## Part M. What the engine must add for the screens

Specs 0093 and 0094 do not provide these. Each is a read or a small rule, with thin routes.

| Need | What it is | Why |
| --- | --- | --- |
| M1. Room view | One read that needs no player sign-in: beat title (`beat_name`), phase kind, deadline or time left, paused flag, the current scene or bridge lines with their presentation hints, who is ready, who has locked, who has answered the survey, whether the game is over, and after the `result` phase the public result. Nothing private | The TV and host must rebuild after a reload or an API restart, and the event stream is in memory only (spec 0093). Spec 0093 promises beat, phase and deadline from a route; the rest is new. If AW-325's route can carry these cheaply, AW-331 only adds what is missing |
| M2. No new seat after start | `lobby-join` is refused once the session has started, with a reason the join screen can show | Decision 4 |
| M3. Survey answers | Save one player's answers as an event on the play record; one answer per player, a repeat replaces it; private to that player | Decision 7. The only route today is host-reported replay intent |
| M4. Private mini-game view needs a sign-in | The display address returns a player's personalised view only to that player's sign-in; without one it returns the shared view | Decision 6 |
| M5. Notebook fields | Read what I hold returns each item's subject (or "at the start") and the round it was found | Screen 9. Only if AW-325's route lacks them |
| M6. Start menu sign-in (Q1, D-133) | Pause and resume accept a player's sign-in; the host role belongs to a player's seat (the first to join); a route lets the host hand it to another seated player; the host controls accept that seat's sign-in | Q1. Sign-in change, a hard rule: needs explicit approval in AW-331's plan |

All of M1 to M6 are game-agnostic. They use no murder-mystery word (inventory section 7).

## Part N. Reconnecting and host controls

**Reconnecting a phone mid-game.**

| What happened | What the player sees | How |
| --- | --- | --- |
| Screen locked, app switched, page reloaded | The same screen, refreshed | Sign-in kept on the phone (decision 3); state read from routes (decision 5) |
| Browser tab closed, then the join link or QR opened again | Straight back into their own seat, on the current phase, with their notebook, budget and any saved draft | Sign-in kept per session in long-lived storage; the join page checks for it first |
| Wi-Fi dropped mid-choice | The choice is sent again with the same ID when the connection returns; it is spent once | Spec 0093: a repeated choice ID has one effect |
| Dropped during the mini-game | The package's phone view comes back mid-run | The kit's reconnect, reading the active run with the player's sign-in |
| Dropped during Last Call | The draft is as last saved | Spec 0094: a draft survives a reconnect and a restart |
| The API restarted | Every screen notices the event count went backwards, resets and rereads its routes | Decision 5. Inferred from the in-memory event stream; checked in the proof |
| A different phone, or the browser's data was cleared | "This game has started. Use the phone you joined with." | Decision 4. Not recoverable in session 1; the host cheat sheet (AW-308) says what to do |
| A player never comes back | The game goes on by its clocks; at Last Call their saved draft is locked or they have no theory | Specs 0093 and 0094 |

**The Start menu and host controls (Q1, D-133).** Every phone has a Start menu, opened from a fixed button on every in-game screen. Every player's menu has Pause, Resume and Settings. The host's menu also has the host controls below. The host is the first player to join and can hand the role to another seated player.

| Control | Who | When | Route |
| --- | --- | --- | --- |
| Pause, Resume | Every player | Any in-game phase | Exist, host-only today; AW-331 lets a player's sign-in call them. Spec 0093 makes pause freeze the phase clock and the mini-game |
| Settings | Every player | Any time | None; contents proposed in AW-330's plan |
| Start game | Host | Room, two or more seated | Exists |
| Move on | Host | Any phase | Spec 0093, host move-on. In Last Call it confirms first: "This locks every saved theory now" |
| Mini-game: Resolve, Cancel | Host | During a mini-game | Exist (`api/routers/mini_games.py`) |
| End game | Host | Any time, with a confirm | Exists |
| Hand the host role on | Host | Any time | Gap; AW-331 |
| Show room code | Every player | Any time | The lobby route |

The host's Start menu shows the phase, the time left, and who is ready, locked or has answered. It never shows a menu item, a finding, a draft or a result that the host's own seat could not see as a player. A host who is also a player sees nothing more than the room.

## Part O. The proof

A full game's screens are proven without a TV in two halves.

1. **Python half: a scripted client.** It drives the API in-process, as the existing API tests do, through a full game on the fixture arc and case that AW-327's headless proof uses, at 2 and at 4 players, with a controlled clock. At every phase it reads what each screen reads: the room view and the shared mini-game view as the TV, the host Start menu's reads as the host, and every player route as each player. It records those answers and every event per audience into a file. The fixture case's private texts carry marker words, and the test fails if any marker reaches a TV or host read, or one player's marker reaches another player.
2. **TypeScript half: the screens replay that file.** Each recorded step is rendered through the dashboard's real screen components with the server renderer already inside `react-dom`, and the test checks the screen sequence, the privacy markers again on the rendered text, and that no internal ID appears.

The recorded file is committed. The Python half fails if a fresh run differs from it, so a change in the engine cannot silently leave the screens behind.

---

# Out of Scope

- Any rule. Rounds, budget, mini-game start and return: spec 0093. Last Call, the check, the winner, the closing: spec 0094.
- Everything on the if-it-fits list: host voice, living suspect cards, Leverage, rival activity feed, motion on the TV, Case Board, difficulty settings, the story-tool viewer, recorded voices. Private notes in the notebook are part of the GDD notebook but not of the status page's "simple notebook", so they wait too.
- New screens for mini-game packages. Which packages session 1 uses, and their player ranges, are Q4. Each new package renderer is its own small task once Q4 is answered.
- Recovering a seat on a different phone. Joining as a spectator.
- A new visual design, art, a motion library, a sound library, voice audio (decision 8).
- Deleting, moving or changing anything in `nightcap-web/`, `sdk/` or the old Couch Race screens.
- Cloud hosting and the Cloudflare Worker's role (AW-269).
- The written content: scene lines, findings, recap lines, the case. Content, done in AW-305 and reviewed without spoilers.

---

# Human Collaboration Contract

**Interaction profiles:** Decision interview for approval and the five questions. Creative collaboration for screen copy (one sample before code). Independent execution for the build tasks after each plan is approved. Facilitated live operation for the walkthrough (AW-301) and the founder TV run.

**Classification rationale:** Which client survives, the proof and the privacy rules are engineering with testable results. What the TV shows during thinking time, how the reveal is staged, where the host controls live and how many mini-games to build depend on the founder's taste and on how the room feels, so they are questions. Whether any of it works on a real TV can only be seen on one.

**Required founder inputs:**
- Approval of this spec, including the eight decisions under "What you are approving".
- Answers to Q1 to Q5. Each has a default; "agree" is a valid answer.
- One sample of screen copy, about twenty lines, before AW-330's code.
- The walkthrough (AW-301), ideally before AW-330's plan is approved.

**Phase gates:**
1. Approve this spec. Permits AW-329 to AW-334 to write their plans, in the build order below.
2. Approve each task's plan. AW-331 crosses engine modules; AW-329 changes `package.json`; AW-330 and AW-331 touch sign-in.
3. Approve the screen-copy sample.
4. The walkthrough (AW-301). If it contradicts a claim in "What the walkthrough must confirm", this spec is changed and shown to you before the affected task builds.
5. The founder TV run plays one full game on these screens.

**Review package:** this file. The parts to read are "Plain-language goal", "What you are approving", "How the feelings answer shapes the layout" and the open questions.

**Approval evidence:** approved by the founder on 2026-11-19: decision D-139, issue #355, and "Founder Approval" at the end of this file.

**Owner actions:** none beyond "Your steps".

## Your steps

1. Open the pull request for this spec on GitHub (the link is in the session's message to you). Click **Files changed**, then click the file name `docs/specs/0095-screens-for-the-thin-version.md`, then click the **...** menu on the file header and choose **View file** to read it formatted.
2. Read "Plain-language goal" and "What you are approving". About ten minutes.
3. Read "How the feelings answer shapes the layout". Check it says what you meant by "I outsmarted you". If not, say what is wrong in your own words.
4. Scroll through "Every screen, in play order". Look at the sketches, not the details. Say if a screen is missing or one should not be there.
5. Answer Q1 to Q5 at the end. Reply in the session, for example "Q1 agree, Q2 agree, Q3 option 2, Q4 agree, Q5 agree".
6. Reply on issue #355 with "approve 0095", or say what to change. You can approve before the walkthrough (AW-301); the walkthrough then checks the list under "What the walkthrough must confirm", and anything it disproves comes back to you before that part is built.

---

# Acceptance Criteria

Every Python test runs without a network, without a real database server, and with the model router replaced by one that fails the test if it is called. Every TypeScript test runs with Node's own test runner and no browser.

**Part K**
- [ ] The dashboard mounts a mini-game package's own renderer by its game ID through the copied loader. Test with the Tell Me Something True renderer on the TV and phone surfaces.
- [ ] Nothing under `dashboard/src/` imports `screens/tmst/` after AW-329. Checked by a test that searches the imports.
- [ ] No file under `nightcap-web/`, `sdk/` or `nightcap/mini_games/` is changed by any task of this spec, and `npm test --prefix nightcap-web` still passes.
- [ ] `dashboard/package.json` lists no new package; only a `test` script is added. Checked in review against the diff.

**Part L**
- [ ] Each of screens 1 to 23 has a component test that renders it with fixture data and checks its key text.
- [ ] For each phase kind in specs 0093 and 0094, the TV and the phone render the screen named in the table "Phase kinds and their screens". One test walks the table.
- [ ] No rendered screen contains any ID from the fixture case or arc. Test searches the rendered text.
- [ ] No TypeScript file computes a budget, a right-or-wrong, a menu or a theory list. Checked in review; the phone's investigations-left number equals the route's number in every step of the proof.
- [ ] The theory form lists concept options in the exact order the route returns. Test with two orders.
- [ ] The phone's private result appears only after the TV's Verdict step in the recorded run. Test on the proof's sequence.

**Part M**
- [ ] The room view, read with no sign-in, returns everything in M1 and, at every phase of a full fixture run, contains no private marker. Test.
- [ ] `lobby-join` after start is refused with a named reason; before start it works as today. Test.
- [ ] Survey answers save per player, a second send replaces the first, and they appear in no read the TV or another player can make. Test.
- [ ] The display mini-game address with a character ID and no sign-in returns the shared view, not that player's view. Test.
- [ ] Route handlers contain no rule; each calls one engine function. Checked in review.
- [ ] `engine/` gains no word from inventory section 7.

**Part N**
- [ ] A phone whose tab was closed and reopened on the join link resumes its own seat. Test of the join page with stored sign-in, using a fake storage.
- [ ] A choice sent twice with the same ID after a simulated reconnect is spent once. Test through the routes.
- [ ] After a simulated API restart (event numbers start again from zero), the screens reread their routes and show the current phase. Test in the TypeScript replay.
- [ ] Each host control calls its route; Move on in Last Call and End game ask to confirm first. Component tests.
- [ ] The host's Start menu renders no other player's menu, finding, draft or result, and no result before the TV does, at any step of the proof. Test.
- [ ] A player's Start menu offers Pause, Resume and Settings only; the host's adds the host controls; after the host hands the role on, the menus swap. Component tests.

**Part O and the whole client**
- [ ] **Named full-game proof, Python half:** `api/tests/test_screens_feed.py::test_full_game_screen_feeds`, at 2 and at 4 players, on AW-327's fixture arc and case. It records every read and event per role, fails on any privacy marker in the wrong place, fails if the committed recording differs, and asserts the model router was never called.
- [ ] **Named full-game proof, TypeScript half:** `dashboard/tests/full-game-screens.test.tsx`, test "full game screens at 2 and 4 players". It replays the recording through the real screen components and asserts, for the TV and each phone, the screen sequence from Room to Survey, the privacy markers, and no internal IDs.
- [ ] Both halves run in CI on every pull request. Today `api/tests` runs nowhere in CI, so AW-334 adds it to `.github/workflows/ci.yml` beside a `npm test --prefix dashboard` step. AW-336 (issue #394) was filed on 2026-11-16 to run `api/tests` in CI; if it merges first, AW-334 adds only the dashboard step.
- [ ] `npm run typecheck --prefix dashboard` and `npm run build --prefix dashboard` pass. `pytest engine/tests api/tests`, `python -m ruff check engine api` and the type check pass.
- [ ] `scripts/checks/provider_leak_check.py` passes.

**Merged, deployed, verified in play.** These are separate and are reported separately.

| State | What it means here |
| --- | --- |
| Merged | Each build task's pull request is on main with the checks above green, read check by check, since only `verify` is required (AW-298) |
| Deployed | Not applicable before session 3. The screens run on the founder's PC through `scripts/rehearsal.py` and the tunnel |
| Verified in play | The founder plays one full game on a real TV and two phones, from Room to Survey, and checks the TV with his own eyes for private information (AW-308). Until then the screens are proven in tests only |

---

# Test Plan

- **Unit and component tests (TypeScript):** each screen with fixture data; the loader; the sign-in storage; the phase-to-screen table; the Start menu for a player and for the host; the reconnect reset.
- **API tests (Python):** each Part M route's happy path, wrong role, wrong session, and repeat request.
- **Integration:** the two-half full-game proof at 2 and 4 players, including an idle run where nobody taps anything and every screen still reaches the Survey on clocks alone.
- **Privacy:** marker scans in both halves; the copied mini-game privacy test; the rewritten role matrix.
- **Manual:** the walkthrough (AW-301) before AW-330's plan, if possible; the founder TV run with two phones; the preflight look at the TV (AW-308).
- **Performance:** not measured. One session at a time in session 1. The phone keeps its two-second poll only as a fallback when the event stream is down.

---

# What the walkthrough must confirm

Every claim below was made from reading code or documents. Only AW-301 (the founder with a TV and two phones) can prove or disprove it. If the walkthrough disproves one, the named part of this spec changes first.

| # | Claim made here | Where it matters | If it is wrong |
| --- | --- | --- | --- |
| W1 | `make rehearsal` starts `dashboard/` and its TV page shows the room code and seated players | Decision 1 | Reconsider the client choice before AW-330 |
| W2 | The QR code on the TV draws and scans through the tunnel (it depends on an outside website) | Screen 1 | Show the code and address only, or adopt a QR package (new dependency) |
| W3 | Joining from a phone through the tunnel works, including the sign-in exchange | Screens 2 and 3 | Fix before anything else |
| W4 | The phone's sign-in survives a screen lock and an app switch on the founder's phones today | Decision 3 | Decision 3 becomes more urgent; no design change |
| W5 | Text the dashboard draws today is readable from the sofa on the founder's TV | Part L accessibility sizes | Raise the sizes |
| W6 | The phone layout works at phone size with the on-screen keyboard open (join page) | Screen 2 | Layout fix |
| W7 | The TV's event stream reconnects after a drop (it retries every three seconds) | Decision 5 | Lean on route rereads |
| W8 | The TV shows nothing private in the old game | Part M, the privacy baseline | Stop and raise it before any build |
| W9 | `nightcap-web/` either cannot be started by the rehearsal, or is not clearly better on screen than `dashboard/` | Decision 1 (made from code only) | Reopen the client choice |
| W10 | The Tell Me Something True screens (hand-written in the dashboard) and its package renderer look and behave alike enough that swapping one for the other loses nothing | Part K | Keep the hand-written screens for that one game |
| W11 | Two-second polling feels live enough on the phone as a fallback | Test plan | Shorten it |
| W12 | The host's "Start case" button appears on the TV page the rehearsal opens | Host controls | Fix the host sign-in path |

The walkthrough cannot confirm anything about the new screens, which do not exist yet. Those are proven by Part O and then by the founder TV run.

---

# Risks and Unknowns

**Risks**
- **The screens wait on the whole engine chain.** AW-332 needs AW-325, AW-303 and AW-328; AW-333 needs AW-326 and AW-327. The status page puts screens in the week to 2026-12-05 beside the endgame. If the engine runs late, the screens do too. Mitigation: AW-329 and the lobby part of AW-330 need no engine work and can start as soon as this spec is approved.
- **The mini-games do not fit two players.** Every package is written for 4 to 8 players or for 1, and the founder TV run has 2 (verified). This is a content and engine question for AW-303 and the case's mini-game wrappers, but the screens cannot show a mini-game that does not work at 2. Q4.
- **Only one package has a working screen,** and it is a draft package. A second or third mini-game means a new renderer each.
- **The theory form may be fiddly on a phone.** The GDD marks it TESTING and parks a simpler fallback. The founder TV run is the first real test.
- **Privacy is only as good as the audience on each event.** The screens trust the engine's audience field. The proof scans every event and every read; the founder's own look at the TV (AW-308) is the last check.
- **The outside QR website.** It receives the join link and fails without internet. Decision for session 1 is to keep it; replace before session 3.

**Unknowns**
- How the founder's TV and phones behave (W1 to W12).
- Whether a quiet TV during thinking time feels tense or dead in the room. Q2 is answered with the quiet TV (D-134); session 1 tests it.
- How long each staged reveal step should hold. Configuration, tuned at the founder TV run.

---

# Open Questions

Each has a recommended default you can accept with "agree". None blocks AW-329.

- **Q1. Where do the host's controls live?** **Answered 2026-11-18: on the phones, in a Start menu. See "Q1 Answered" at the end.** (1) On the TV page, folded into a corner, opened with the PC's mouse or keyboard. Recommended: it is where the host's sign-in already is, it needs no second link, and everything it shows is room-safe, so a host who is playing stays unspoiled. (2) On a separate host page opened on any phone with its own link; easier to reach from the sofa, but one more link to handle and one more device. (3) Both. Option 1 is cheap to change to 2 or 3 later. Blocks: AW-330's plan.
- **Q2. What does the TV show during thinking time?** **Answered 2026-11-18: option 1, quiet (D-134). See "Q2 Answered" at the end.** (1) Quiet: round title, clock, who is ready. Recommended, because private thinking wins (your feelings answer). (2) Quiet, plus the round's scene lines left on screen for anyone who wants to reread. (3) Quiet, plus a light line when someone investigates ("[Name] is looking into something"); this is the if-it-fits rival feed and needs engine work. Blocks: AW-332's plan.
- **Q3. How is "The accused" staged on the TV?** **Answered 2026-11-18: option 1, owned by Nightcap, order never by right or wrong (D-135). See "Q3 Answered" at the end.** (1) One player at a time with a short hold, then all side by side; the host can skip ahead. Recommended: it builds to the groan. (2) Everyone at once. (3) The host taps for each player. All three use the same engine event; this is a screen setting. Blocks: AW-333's plan.
- **Q4. How many different mini-games does session 1 need screens for?** **Answered 2026-11-19: not one reused game; distinct mechanics, several per round allowed, solo mini-games, session 1 variants (D-136, D-137). See "Q4 Answered" at the end.** Facts: only Tell Me Something True has a working package screen, and it is a draft written for 4 to 8 players; no package is written for 2 or 3 players (verified). (1) One mini-game that works at 2 to 4 players, reused in all three rounds with three different story wrappers; add a second only if it fits. Recommended: cheapest, and the status page's cut order already allows fewer mini-games. (2) Two different mini-games. (3) Three. Which mini-game and its story wrappers are chosen with the case's author. Blocks: the mini-game renderer tasks, not AW-329 to AW-334.
- **Q5. Two documents disagree on the final theory, and the screens follow the later one unless you say otherwise.** **Answered 2026-11-19: fill a short written account and pin one proof (D-138). See "Q5 Answered" at the end.** The status page says "arrange a short causal chain" (`docs/product/nightcap-status.md`, "What session 1 contains"). Spec 0094, approved later the same week, has the player fill the case's slots in the case's fixed order; the player does not choose the order (Part G). (1) Fill the case's slots in order, as spec 0094 builds. Recommended: no engine change, and the GDD's own example reads in a fixed order. The status page wording is then updated to match. (2) Let players put the pieces in their own order. That changes spec 0094's check and needs your approval there. Blocks: AW-333's plan.

---

# Proposed build order

Proposal only. These IDs are reserved for this spec; no task files, index entries or issues exist for them yet. At most two build sessions at once. "Owns" is the exact set of paths the task may change; no two tasks that can run at the same time share a path.

| Order | Task | Size | Depends on | Owns | Can run beside |
| --- | --- | --- | --- | --- | --- |
| 1 | **AW-329: Bring the mini-game kit, the package loader and the test setup into the dashboard.** Copy the kit and loader, map `@arcwright/mini-game-kit` in the Vite config, mount the Tell Me Something True package renderer through the loader, add the `test` script, copy the kit's privacy test | M | This spec approved | `dashboard/src/mini-game-kit/`, `dashboard/src/mini-games/`, `dashboard/tests/` (setup and the kit test only), `dashboard/package.json`, `dashboard/package-lock.json`, `dashboard/tsconfig.json`, `dashboard/tsconfig.node.json`, `dashboard/vite.config.ts` | Any engine task (AW-325, AW-303, AW-328, AW-326, AW-327) |
| 2 | **AW-330: Build the screen shell: pages, sign-in storage, room and join screens, the phone Start menu.** Pages for TV, join and phone; the phase-to-screen table with empty slots for round and endgame screens; reading routes on load and on reconnect; sign-in kept per session; screens 1, 2, 3 and 23; the phone Start menu with Settings, and the host's controls that exist today (Q1, D-133) | M | AW-329 merged. The phase-aware parts need AW-325 merged | `dashboard/src/App.tsx`, `dashboard/src/main.tsx`, `dashboard/src/index.css`, `dashboard/src/api/`, `dashboard/src/shell/` (new), `dashboard/src/screens/DisplayScreen.tsx`, `dashboard/src/screens/JoinScreen.tsx`, `dashboard/src/screens/WaitingScreen.tsx`, `dashboard/src/screens/round/index.tsx` and `dashboard/src/screens/endgame/index.tsx` (empty slots, handed over) | Any engine task |
| 3 | **AW-331: Add the room view, the seat rule, survey answers and the signed-in mini-game view (Part M).** | M | AW-327 merged, because the engine tasks before it change `engine/session/` and `api/main.py` | `engine/session/room_view.py` (new), `engine/session/survey.py` (new), `engine/session/service.py` (the join rule only), `api/routers/room.py` (new), `api/schemas/room.py` (new), `api/main.py` (one line), `api/routers/mini_games.py` (the display address only), `api/routers/lobby.py`, matching new tests in `engine/tests/` and `api/tests/` | AW-329, AW-330 |
| 4 | **AW-332: Build the round screens: story, thinking time, investigate, finding, notebook, mini-game and its result.** Screens 4 to 12 | L | AW-330, AW-331, AW-303 and AW-328 merged | `dashboard/src/screens/round/`, `dashboard/src/screens/notebook/` | AW-333 |
| 5 | **AW-333: Build the endgame screens: Last Call, your theory, the accused, the Verdict, the Postmortem, the survey.** Screens 13 to 22 | M | AW-330 and AW-331 merged; AW-326 and AW-327 merged | `dashboard/src/screens/endgame/`, `dashboard/src/screens/survey/` | AW-332 |
| 6 | **AW-334: Prove a full game's screens without a TV, and run the proof in CI.** Part O, the rewritten privacy matrix, and the CI steps | M | AW-332 and AW-333 merged | `api/tests/test_screens_feed.py`, `dashboard/tests/full-game/`, `dashboard/tests/fixtures/`, `dashboard/tests/privacy-matrix.test.tsx`, `.github/workflows/ci.yml` | Nothing |

Not numbered here: one small task per mini-game renderer that Q4's answer needs, each owning only `nightcap/mini_games/<package>/client/`, and any player-range change to a package's definition, which belongs with AW-303 or the case's mini-game wrappers.

---

# Changelog

- 2026-11-16: First draft (AW-302, the screens spec of three).
- 2026-11-16: Merged to main as a draft in pull request #393; still not approved. Cited D-128 now that pull request #392 has merged. Noted the two tasks filed from this draft's findings: AW-336 (API tests in CI, issue #394) and AW-337 (no mini-game fits two or three players, issue #395, linked to Q4).
- 2026-11-18: Q1 answered by the founder (host controls in a Start menu on the phones). The spec as a whole is still a draft and not approved.
- 2026-11-18: Q2 answered by the founder (a quiet TV during thinking time, D-134). Still a draft.
- 2026-11-18: Q3 answered by the founder (the accused shown one at a time, staged by Nightcap, D-135). Still a draft.
- 2026-11-19: Q4 answered by the founder (D-136, D-137). Still a draft.
- 2026-11-19: Q5 answered by the founder (D-138).
- 2026-11-19: Approved by the founder (D-139). Task files and issues for AW-329 to AW-334 created.

---

# Q1 Answered: Host Controls Live In A Start Menu On The Phones (2026-11-18)

Recorded from the founder's answers in session on 2026-11-18. Decision row: D-133. Also recorded on issue #355. This answers Q1 only. It does not approve this spec; "approve 0095" on issue #355 is still needed.

**Founder's words**, in order:
1. Choosing among the three options: "A separate host page on a phone. Easy to reach from the sofa. ... Just desinate a host that has the controls on their phone or add game pause on the phones similar to how video game controllers have a start menu."
2. Asked who may pause: "Everyone can pause (Recommended)".
3. Asked to confirm the summary: "Yes, but host can be reassigned by the first to join too. Also there should be a start menu and settings on the phones for everyone and the start menu actions depend on if youre host or regular player. The rest looks correct".

**What was decided**

- There is no host strip on the TV and no separate host link. The TV shows only the room.
- Every phone has a Start menu, opened from a fixed button on every in-game screen, like a game controller's Start button. It also holds Settings, for everyone.
- What the Start menu offers depends on the phone's role:

| Action | Every player | Host only |
| --- | --- | --- |
| Pause, Resume | Yes | Yes |
| Settings | Yes | Yes |
| Start game (in the room, two or more seated) | | Yes |
| Move on (confirms first in Last Call: "This locks every saved theory now") | | Yes |
| Mini-game Resolve, Cancel | | Yes |
| End game (with a confirm) | | Yes |
| Hand the host role to another seated player | | Yes |

- The host is the first player to join the room. The host can hand the role to another seated player. Read by the orchestrator as "the current host can reassign it"; if the founder meant something else, this line changes.
- The host's menu shows only what the whole room may see (phase, time left, who is ready, locked or has answered), so a host who is also playing stays unspoiled and has no advantage.

**What is not decided yet (proposals for the build plans, each shown to the founder)**

- **What Settings holds.** Proposal for AW-330's plan: text size, reduced motion, the room code and rejoin link, and "leave game". Nothing that changes the rules. The screen-copy sample (Part L) shows it.
- **Abuse of pause.** Any player can pause. Proposal: the TV shows who paused ("Paused by [Name]"), and anyone can resume. Changing this to host-only resume is a setting in the screens, cheap to change (D-127).
- **What happens to the host role if the host's phone drops.** Proposal: the role stays with that seat, and the seat's reconnect (decision 3) brings it back; the host cheat sheet (AW-308) covers a phone that never returns.

**What this changed above.** The "Host" bullet under "Two surfaces and one role", screens 1 and 21, Part K, Part N (now "The Start menu and host controls"), Part M (new row M6), the Part N and Part O acceptance criteria, the test plan and the AW-330 row of the build order were rewritten on 2026-11-18 to match this answer. Decision row: D-133.

- **Sign-in (a hard rule).** Today pause, resume, start, move-on and end accept only the host sign-in that is made when the session is created (`api/routers/sessions.py`, `require_host_jwt`). Letting every player pause, giving the host role to a player's seat, and handing it on need sign-in changes. They belong in AW-331 (Part M), whose plan needs the founder's explicit approval. AW-330 builds the menu.
- **Size.** Inferred: this adds the Start menu, Settings and the hand-over to AW-330 and AW-331, and removes the TV host strip. Net, about one more build day; not measured.

---

# Q2 Answered: A Quiet TV During Thinking Time (2026-11-18)

Recorded from the founder's answer in session on 2026-11-18. Decision row: D-134. Also recorded on issue #355. This answers Q2 only; it does not approve this spec.

**Question as put to the founder:** "the next question is spec 0095 Q2: what the TV shows while players investigate. I recommend keeping it quiet, showing only the round title, the clock and who is ready."

**Founder's words:** "I agree with your recommendation."

**What was decided.** Option 1. During a `choices` phase the TV shows only the round title, a large clock and who has marked ready. No scene lines left on screen, no rival activity line, no sound, no new text and no animation except the clock. This matches screen 6 and the "Thinking time" row of "How the feelings answer shapes the layout" (D-128: private thinking wins).

**What this does not decide.** Options 2 (scene lines left on screen) and 3 (a rival activity line) are not built for session 1. The rival feed stays item 4 of the if-it-fits list. Whether a quiet TV feels tense or dead is a session 1 question; changing it later is a screen setting, cheap to change (D-127).

**What this changes above.** Screen 6 and the Unknowns line now cite this answer. Q2 no longer blocks AW-332's plan.

---

# Q3 Answered: The Accused Shown One At A Time, Staged By Nightcap (2026-11-18)

Recorded from the founder's answers in session on 2026-11-18. Decision row: D-135. Also recorded on issue #355. This answers Q3 only; it does not approve this spec.

**Founder's words.** Asked how "The accused" is staged, he answered: "I want to make sure this is not part of the Arcwright engine and is part of the nightcap game. As long as that is certain, one at a time works because it can be used to make the order more suspenseful, misleading, or mysterious." Shown the summary below, with the order guard, he chose "Yes, with the guard (Recommended)".

**What was decided.**
- Option 1: each player's accused appears in turn with a short hold, then all side by side. The host can skip ahead from the Start menu on their phone (D-133).
- **It belongs to Nightcap, not the engine.** The Arcwright engine sends one generic `reveal` event holding each player's shown-first answer (spec 0094, Part J). It has no idea what an accusation is, and it does not stage, order or time anything for the room. The one-at-a-time staging, the hold between players and the order are set in Nightcap's own files (the Nightcap arc file's presentation hints for the `reveal` phase, D-070, or Nightcap's screen settings) and performed by Nightcap's screens. The engine passes presentation hints through without reading them.
- **The order is a storytelling tool,** for suspense or misdirection: an authored order, seat order, or a random order the case writer chooses.
- **Guard: the order never depends on who is right.** Ordering by right or wrong would give the Verdict away before it is shown. This is already required by spec 0094 Part H (no event carries right-or-wrong information before the `result` phase); this answer makes it explicit for the staging. The engine's `reveal` event lists players in a neutral order (AW-327).

**What this changes above.** Screen 16 cites this answer. Q3 no longer blocks AW-333's plan. AW-327's task file carries the neutral-order rule.

---

# Q4 Answered: Distinct Mechanics, Several Per Round, Solo Mini-Games, Session 1 Variants (2026-11-19)

Recorded from the founder's answers in session on 18 and 19 November 2026. Decision rows: D-136 (mini-game structure) and D-137 (session 1 variants). Also recorded on issue #355. This answers Q4 only; it does not approve this spec.

**Founder's words**, in order: "Wrappers can change the style/aesthetic of the game to match the story, but it doesnt change the mechanic, so playing the same game mechanic multiple times in one playthrough of the game seems like what we wouldnt want to do." "I want the best number fo mini-games to fit a playthrough, not just trying to force in whats possible given our current mini-game inventory. I would rather create more mini-games to make it correct than adjusted for the test." "Dont get to hung up on trying to measure the amount of time to play the game. We will find that out when we test and adjust from there based on player experience and feedback." "Im not married to 1 mini-game per round either. Some games could be played faster than others. There should be a cap per round, but it should be flexible and not exclusively 1. Some mini-games could also only be for one player if they stumble onto something other players havent." "Both in session 1, not required to be played, but I would like to A/B test that experience. We could have Sesseion 1a, 1b, 1c, and possibly 1d to test out varied experiences." Each summary was confirmed with "Yes, record it (Recommended)".

**What was decided**

- **None of the offered options.** Not one mini-game reused with wrappers: a wrapper changes the look, not the mechanic, and no mechanic repeats in one playthrough (the It Takes Two lesson, reset audit section 3).
- **Mechanics are designed for the game, not taken from inventory.** Each is built new or adapted for 2 to 4 players. How many a playthrough needs follows from design and testing, not from a time estimate (AW-337).
- **A round may hold more than one mini-game,** up to a cap set per round in Nightcap's arc file. This amends D-113's "one round ending in a story-wrapped mini-game" (AW-344).
- **Solo mini-games:** an investigation can lead one player into a private mini-game that only they found (AW-345).
- **Session 1 runs variants,** 1a to 1d, each a different arc-file setup, to A/B test these structures. The extras are optional; the core variant must be ready for the founder TV run by 5 December (D-137, AW-346).

**What this changes in this spec.** The Q4 recommendation (one game, three wrappers) is withdrawn. Screens 10 to 12 must handle several mini-games in a round and a solo mini-game that runs on one phone only; what the TV and the other phones show while a solo mini-game runs is open and is settled in AW-345's plan, within D-128 (private thinking wins) and D-134 (a quiet TV). Each new mechanic needs its own package renderer, one small task each, as "Out of Scope" already says.

---

# Q5 Answered: Fill The Story, Pin One Proof (2026-11-19)

Recorded from the founder's answers in session on 19 November 2026. Decision row: D-138. Also recorded on issue #355. This answers Q5; it does not approve this spec.

**Founder's words.** Asked about Q5, the founder first asked "What are the bust versions we thought through in the GDD?", then "Knowing what you know about how to creat amazing, fun, engaging, world class, and billion dollar games, is this the best way to do it? Do you have other suggestions?", then "What would be the best version for the dysfunctional detective agency idea I had?", then "I'm feeling better, but what does the gameplay look like? We can skip the skinning for right now and add it to part of the detective agency strategy." Shown a walkthrough, he answered the question "Lock this Last Call gameplay (fill the story from your own pieces, pin one proof, lock; the winner's proof shown on the TV at the Verdict; the proof does not change who wins)?" with "Lock it (Recommended)". The option he chose said: "Spec 0094's Verdict change is approved by this answer."

**What was decided.** The Last Call theory is Structured Reconstruction (the GDD's V1, spec 0092 Q3) presented as a short written account. (1) The case writer writes a short account of what happened with blanks; each blank is one of the case's solution slots (spec 0093 Part A), in the case's order. The player fills each blank by tapping pieces they hold themselves, true and misleading alike, in an order that never hints at the answer (spec 0094 Part G is otherwise unchanged). (2) The player also pins one held piece as their proof. The proof does not change who wins: the theory check and the winner rule (spec 0094 Parts H and I) are unchanged. (3) At the Verdict the TV shows the winner's proof with their name; nobody else's proof is shown publicly. Each phone shows its own blanks marked right or wrong only after the TV's Verdict (D-128). (4) The detective-agency wording (case report, Exhibit A, performance reviews, the side guess) is not part of this decision; it moves to the detective agency strategy, AW-319. Prior art considered (GameGene records): The Case of the Golden Idol judges a completed written account, not a name; Ace Attorney's single moment of presenting the decisive evidence; Return of the Obra Dinn and Golden Idol's partial-correctness feedback was rejected because the GDD forbids incremental correctness feedback.

**What this changes in this spec.**
- **Screen 14 (Your theory)** becomes the account with blanks: the case writer's sentence, each blank opening the list of the player's own pieces, plus one "Proof" field that opens their notebook. Lock asks once more, as before.
- **Screen 17 (Verdict)** adds the winner's proof after their name, for example "[Name] solved it. Their proof: [piece]."
- **Screen 18 (Your result)** shows the player's own account with each blank marked right or wrong, after the TV's Verdict.
- Q5's two original options are both replaced: the order is set by the case writer's account, and the player does not rearrange it.

---

# Founder Approval (2026-11-19)

Recorded from the founder's answer in session on 2026-11-19. Decision row: D-139. Also recorded on issue #355.

**Question:** "Approve spec 0095 (the screens for the thin version), with your five answers D-133 to D-138? This unblocks the screen task plans AW-329 to AW-334; each plan, and AW-331's sign-in change, still comes to you separately."

**Founder's words:** "Approve 0095 (Recommended)"

**What this approves.** Phase gate 1 of this spec: Parts K to O, the eight decisions under "What you are approving", and the answers in "Q1 Answered" to "Q5 Answered" (D-133 to D-138). Where an answered section and earlier text disagree, the answered section is the later record. It permits AW-329 to AW-334 to write their plans, in the build order above.

**What this does not approve.** Any plan or code; each plan is shown to the founder first. The hard rules each task touches (AW-329: `package.json`; AW-330 and AW-331: sign-in; AW-331: changes across engine modules) need his explicit approval of that plan. The screen-copy sample (about twenty lines) comes before AW-330's code. The walkthrough (AW-301) still checks W1 to W12; anything it disproves comes back to him before that part is built.
