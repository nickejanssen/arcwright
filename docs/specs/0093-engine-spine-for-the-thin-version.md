---
id: engineeringpractice.specs.0093-engine-spine-for-the-thin-version
namespace: engineering-practice
title: "Spec 0093: Engine Spine For The Thin Version"
owner: Nico Janssen
status: active
review_by: "2027-02-16"
sensitivity: internal
source: authored
x-scope-evidence: D-112, D-113, D-118, D-123
tags: []
supersedes: []
---

# Spec 0093: Engine Spine For The Thin Version

**Status**: Approved by the founder on 2026-11-16 (D-124, issue #355). This permits its four build tasks to write their plans. Each plan needs the founder's approval before code. See "Founder Approval" at the end.

**Author**: Claude Code (Spec Author role) | **Date**: 2026-11-16 | **Task**: AW-302, the engine-spine spec of three | **Checked against**: main at `bd7f32c`

**Canonical path**: `docs/specs/0093-engine-spine-for-the-thin-version.md`

---

# Plain-language goal

When this is built, a game runs by itself from "everyone has joined" to "Last Call begins". Each round shows its written scene, lets every player spend investigations from a saved budget, starts the round's mini-game, ends that mini-game on a clock even if nobody plays, and moves on. No person pushes it along and no AI decides anything. It also fixes the file format the first case is written in, and a rule-based check that the case is fair.

It does not include the screens (a later spec) or Last Call onward (spec 0094). After this spec is built you can watch a full game run in a test and on the old plain screens, but it will not look like the game yet.

---

# What you are approving

| Part | What it does | Why it is needed | Build task |
| --- | --- | --- | --- |
| A. Case file format, loader, fairness check | One file format for a written case. The engine refuses a case that is unfair | The first case needs a target to be written to (AW-305, AW-306) | AW-324 |
| B. What each player holds | A saved record, per player, of what they found themselves, kept apart from what they only heard | The final theory may only count what you found yourself | AW-324 |
| C. Rounds that move by rule | A beat becomes ordered steps: scene, choices, mini-game, bridge. Each step ends by a rule or a clock | Today a beat ends when everyone has typed once | AW-325 |
| D. Investigations and the budget | A menu of what can be looked into, six per player per game, saved, with repeat looks free | Today the limit is per beat, in memory, with no route | AW-325 |
| E. Mini-game start, clock and return | The round starts its mini-game, the clock ends it, the round moves on | Today nothing starts one (inventory section 6) | AW-303 |
| F. Play records | The six generic facts are saved for every session, and four plain questions can be answered from them | D-115 | AW-304 |

**Decisions that are approved if you approve this spec.** Each is the author's recommendation. Say so if you want any of them changed.

1. **The clock.** A small loop inside the API checks every active session once a second and ends anything whose time is up. All deadlines are saved in the database, so a restart loses nothing. The alternative, checking only when a screen asks, needs every screen to keep asking and can leave a room waiting.
2. **The old game stays as it is.** The Couch Race arc file and its code stay registered and untouched until session 1 has been played, so the August path still runs. New behaviour applies only to an arc file that asks for it.
3. **The host's lines.** For the first case they are written into each beat of the arc file and shown as text. The larger line-library reader (AW-291) waits until after session 1.
4. **Written content first.** What a player gets back from an investigation is written by a person. Typed questions answered by an AI character keep working where they work today, but they no longer move the game on and the first case does not depend on them (spec 0092, Q8).
5. **A host "move on" button.** The host can end the current step by hand. It is the safety valve for a live room.

**Hard rules this spec touches (AGENTS.md).**

| Hard rule | Touched | Detail |
| --- | --- | --- |
| Changes across engine modules | **Yes** | `arc`, `case`, `session`, `interactions`, `mini_games`, `knowledge`, `characters`, `events`, `telemetry`, plus thin API routes. Approving this spec approves the direction; each build task still shows its plan first |
| Database tables or migrations | **No** | Everything is saved in tables that already exist (section "Where things are saved"). If a build session finds it needs a table change, it stops and asks |
| New dependencies | **No** | |
| Prompts or evaluation suites | **No** | No model call is added |
| Secrets or sign-in | **No** | New routes use the player and host tokens that exist |

---

# References

- Umbrella: [spec 0092](0092-nightcap-gdd-rebuild.md), work packages 1, 2, 3, 4, 7 (trigger and return only) and 15 (headless run). Open questions Q3, Q5, Q8, Q9, Q10.
- Inventory: [spec 0092 work package 0](0092-wp0-thin-version-inventory.md), sections 1, 2, 4, 5, 6 and 10. Founder review recorded on issue #353 on 2026-11-16.
- Scope: [Nightcap status page](../product/nightcap-status.md), "What session 1 contains". Decisions D-112 (thin version), D-113 (a beat is one round ending in a mini-game), D-115 (play records), D-118 (three combined specs), D-123 (approval of spec 0092 for the thin version).
- GDD: [investigation](../gdd/nightcap/01-authoritative-gdd/02-investigation-deduction.md), [minigames](../gdd/nightcap/01-authoritative-gdd/04-minigame-competitive-pulse.md), [runtime boundary](../gdd/nightcap/01-authoritative-gdd/11-arcwright-runtime-boundary.md).
- Architecture: [arc execution](../architecture/03-arc-execution.md); `AGENTS.md` principles 1, 2, 4, 5 and 8.
- Related specs: 0074 (structured interaction loop, the old questioning code), 0077 to 0079 (mini-game runtime), 0070 (game-agnostic vocabulary, AW-274).

**x-scope-evidence**: `D-112`, `D-113`, `D-118`, `D-123`. This spec adds no product scope beyond the thin version on the status page. The one item that would add scope is Q1 below, and it is not approved by this spec.

---

# Overview

Connect engine parts that already exist into a round that runs by rule, add a written-case format with a fairness check, and save each player's findings, choices and budget, so that a headless session reaches the last beat at two and at four players with no model call.

---

# What the code does today

Checked by reading code on 2026-11-16. Line numbers will drift.

- A live session moves to the next beat when every player has typed once (`engine/characters/service.py:164`, `engine/session/service.py:332`). Every condition the arc author wrote is treated as met (`engine/session/service.py:790`).
- **New finding, not in the inventory:** nothing sends a beat's written scene to the screens. The arc file holds `authored_content` for each beat, but no engine or API code reads it, and the shared screen shows the beat's internal name (`dashboard/src/screens/DisplayScreen.tsx:349`). The inventory's row for the opening said this worked; it does not. Part C builds it.
- Nothing outside tests creates, starts or times out a mini-game run, and a finished run does not tell the session (`engine/mini_games/runtime.py:316`, `:363`, `:514`, `:675`). A run does not record which beat it belongs to. Pausing a session does not pause its run.
- The `decisions` table exists and nothing writes to it (`engine/db/orm.py:341`). It fits "what a participant chose from what was offered".
- What a player holds can already be saved as a fact in the knowledge graph, with who it came from (`engine/knowledge/graph.py:36`, `engine/claims/evidence.py:15`).
- The stream of events to screens is held in memory only (`engine/events/bus.py`). A phone that reconnects after an API restart cannot replay it, so everything a screen needs must also be readable from a route.
- What players type is held in memory and lost on restart (`engine/characters/service.py:79`).

---

# In Scope

## Part A. Case file format, loader and fairness check

One JSON file per written case, in the game's own folder. The arc file names it. The engine code lives beside the existing case code in `engine/case/` and does not change the existing generated-case resolver (spec 0092, Q10).

**Fields.** Names are generic on purpose: the engine must not learn murder-mystery words.

| Field | Meaning |
| --- | --- |
| `case_id`, `format_version`, `title` | Identity. `format_version` is `1` |
| `supported_participant_counts` | The player counts the case is written for, for example 2, 3 and 4 |
| `cast` | The characters in the story. Each has an ID, a display name, the list of concepts that character knows, and whether a player may name them in the final theory. Each becomes a character in the engine's one character model |
| `subjects` | The things a player can look into: a person, a place, an object or a record. Each has an ID, a kind and a label |
| `concepts` | The units of information a player can hold. Each has an ID, a short label, the written text the player sees, and whether it is true or misleading |
| `opening` | The concepts every player holds at the start |
| `opportunities` | The investigation choices. Each names its subject, a label, the written content shown to the player, the beats it is available in, the concepts a player must already hold to see it, its cost (1, or 0 for a follow-up), and the concepts it gives |
| `essential_truths` | What must be established to solve the case. Each lists two or more routes; a route is a set of concepts that together establish the truth |
| `deceptions` | Each misleading concept, with the true concepts that expose it |
| `solution` | The ordered slots of the final theory. Each slot has an ID, a label, a kind (a cast member, or a concept), and the list of answers that are accepted for it. Several accepted answers in one slot are equal ways of being right. One slot is marked as the one shown to the room first. How a submitted theory is judged belongs to the endgame spec (0094) |
| `closing` | The written lines that explain what really happened, shown only after every theory is locked. Used by the endgame spec |

**The loader refuses a case, with a named reason, when:**

- A1. Any ID is duplicated, or any ID that is referred to does not exist.
- A2. Any essential truth has fewer than two routes, or one single opportunity is needed by every route to it.
- A3. For any supported player count, a single player starting from the opening cannot, within the budget, both reach at least one route to every essential truth and hold an accepted answer for every slot of the solution, obeying each opportunity's beats and prerequisites. This is computed by search, not by a model.
- A4. Any misleading concept has nothing that exposes it, or what exposes it cannot be obtained.
- A5. Any opportunity can never become available, or any round offers a fresh player fewer than two choices.
- A6. Any accepted answer in `solution` uses a concept that cannot be obtained, or any slot has fewer than two obtainable wrong answers. A slot with only right answers on offer would solve the case for the player.

**Two reports.** The check prints a full report for the case's author, and a summary for the founder that holds only each rule's name, pass or fail, and counts. The summary never prints a label, a text or an ID from the case file (spec 0092, Q7 spoiler rule).

**In format version 1:** every opportunity is open to every player (none is first come, first served), and no opportunity is hidden from a player by seat. Unequal information comes only from what each player chose to look into.

## Part B. What each player holds

- When the engine gives a player a concept (from the opening, from an investigation, or from a mini-game result), it saves a fact of one fixed type in the knowledge graph for that player's character, with no source character. That is "found it myself".
- What a player only heard, from another player or from a character speaking, stays in the existing who-said-what record and in knowledge with a source character. It is never counted as held.
- One function answers "which concepts does this participant hold". Parts A and D and the endgame spec all use that one function.
- At session start the loader also saves each cast character's `knows` list into the knowledge graph, so any generated line stays limited by what that character knows (principle 5).

## Part C. Rounds that move by rule

- A beat in an arc file may list ordered **phases** from a fixed set: `scene`, `choices`, `mini_game`, `bridge`. An arc file lists phases on every beat or on none. A beat without phases behaves exactly as today, so both registered arc files load and run unchanged.
- The engine moves from phase to phase, and from the last phase to the next beat, by these rules only:

| Phase | On entry | Ends when |
| --- | --- | --- |
| `scene` | Sends the beat's written scene lines as events, with presentation hints (D-070) | Every player has marked ready, or the authored time is up, or the host moves on |
| `choices` | Opens the investigation menu for each player (Part D) | Every player has marked ready, or the authored time is up, or the host moves on |
| `mini_game` | Creates and starts the run bound to the beat (Part E) | The run reaches an end state |
| `bridge` | Sends the beat's written bridge lines | The authored time is up, or every player has marked ready, or the host moves on |

- One engine function, the **tick**, takes a session and the current time, and applies everything that is due: phase deadlines and the mini-game deadline. Calling it twice at the same moment makes each change once.
- A loop in the API process calls the tick for each active session once a second. Tests do not use the loop; they call the tick with a controlled clock.
- Pausing a session freezes the phase clock and pauses the active run. Resuming restores both with the time that was left.
- When a beat has more than one exit, the first is taken, as today. Choosing between exits by rule is not needed for a straight three-round game and is out of scope.
- The current beat, phase and deadline are readable from a route, so a screen can rebuild itself after a reconnect.
- Typed input from a player no longer moves a phased arc forward.

## Part D. Investigations and the budget

- The arc file sets the budget per participant for the whole game. Default 6 (spec 0092, Q5). The value is configuration.
- During a `choices` phase a player can read their menu: every opportunity available in this beat whose prerequisites they hold, marked as new or already taken, with their remaining budget.
- Choosing a new opportunity costs its cost. The engine checks, in this order: the phase is open; the opportunity is on this player's menu; the budget covers it. Then it saves the choice with what was on offer, gives the concepts (Part B), and sends the written content to that player only.
- Choosing something already taken costs nothing and shows the same content again. "Review is free."
- A choice carries an ID from the phone. Sending the same ID twice has one effect. Two choices sent at the same moment by one player cannot both pass the budget check.
- Unspent budget carries to later rounds. When the budget is zero the player can still review and mark ready.
- The shared screen and other players receive no content from a choice. The host receives only that a choice was made.
- **Routes** (thin handlers; all logic in the engine): read my menu; choose an opportunity; mark ready; read what I hold; host move-on.
- The new code does not use the old questioning windows in `engine/interactions/` (spec 0074), which stay untouched for the old arc.

## Part E. Mini-game start, clock and return

- Entering a `mini_game` phase resolves the beat's binding, creates the run and starts it. The run saves which beat and binding it belongs to inside its stored definition, so no table changes.
- The tick calls the existing timeout check. With no submissions at all, the run ends when its deadline passes.
- When a run reaches any end state (completed, timed out, resolved or cancelled by the host), the session is told, the phase ends and the round continues.
- A beat with no binding skips the phase. A binding that cannot be resolved ends the phase at once with a recorded error, and the host is told; the game does not hang.
- Existing behaviour for duplicate and late submissions, scoring and what a package releases is not changed.

## Part F. Play records

Every session, for any game, saves these six facts. No table is renamed.

| Fact | Where it is saved |
| --- | --- |
| Story units entered and left, with times | `arc_beat_states`, plus a saved event for each phase change |
| Who learned what, and from whom | `knowledge_states` |
| What each participant chose from what was offered | `decisions` (new rows from Part D), `mini_game_submissions` |
| What each character said | `claims`, generation logs, `dialogue` events, and typed input saved as `player_input` events (AW-304; before AW-304 typed input was kept only in memory) |
| Tension against the author's target | The existing intent-fidelity events |
| Cost | The existing generation logs and cost summary |

- A small set of query functions answers, from the record alone: where did players stall (time per phase and who had not marked ready); what content did nobody see (opportunities never chosen); which characters drew attention (choices per subject); was the mini-game result used.
- Event and record names added by this spec use no murder-mystery word. Existing game words in table names (`accusations`, `suspect_locks`, `contradiction_flags`) are not touched; the thin version does not write to those tables. They stay listed for AW-274.

## Where things are saved

| Thing | Saved in | New table |
| --- | --- | --- |
| What a player holds | `facts` and `knowledge_states` | No |
| Each choice, the menu it was made from, and readiness | `decisions` | No |
| Budget left | Worked out from the saved choices | No |
| Phase, its deadline, and the time left while paused | `events` | No |
| Which beat a mini-game run belongs to | The run's stored definition | No |
| Typed input | `events`, type `player_input` (AW-304) | No |

---

# Out of Scope

- Screens, the notebook's look, and any SDK or TypeScript change. Screens spec, not yet written.
- Last Call, the final theory, its checker, the reveal, Truth, Verdict and Postmortem. Spec 0094. This spec only stores and checks the `solution` and `closing` blocks.
- What winning a mini-game gives the winner. See Q1.
- Choosing between a beat's exits by rule, loops, and an early Last Call.
- The line-library reader (AW-291), slot filling and host voice.
- Rival activity feed, Leverage, Case Board, difficulty settings, exclusive opportunities.
- Renaming game words that already exist in `engine/` or the database, and changing the engine's default arc (`engine/arc/registry.py:101`). Both stay with AW-274, because changing them risks the August path.
- The real Nightcap arc file and the first case's content. They are written in AW-305 against Part A. Tests here use a small made-up case and arc in the test fixtures.
- Deleting, moving or unregistering anything from the old game.
- Cloud hosting. More than one API process is not supported by the once-a-second loop and is noted for AW-269.

---

# Human Collaboration Contract

**Interaction profiles:** Decision interview for approval and Q1. Independent execution for the build tasks after each plan is approved. Facilitated live operation for the one TV check.

**Classification rationale:** The parts are engine plumbing with testable results, which does not need the founder's taste. What a mini-game win gives (Q1) is a gameplay choice and does. Whether a round feels right can only be judged on a TV.

**Required founder inputs:**
- Approval of this spec, including the five decisions listed under "What you are approving".
- An answer to Q1. It does not block approval or the first two build tasks.
- A message to the case-writing session (Owner actions).

**Phase gates:**
1. Approve this spec. Permits AW-324, AW-325, AW-303 and AW-304 to write their plans.
2. Approve each task's plan. Permits that task's code. Each crosses engine modules.
3. See one round on a real TV and two phones. Recorded on issue #356.

**Review package:** this file. "What you are approving" is the part to read. "Your steps" at the end says what to do.

**Approval evidence:** the founder's inventory review, issue #353 (2026-11-16), permitted writing this spec. The founder approved the spec on 2026-11-16: decision D-124, issue #355, and "Founder Approval" at the end of this file.

**Owner actions:**
- Send the case-writing session this message: "Read `docs/specs/0093-engine-spine-for-the-thin-version.md`, Part A. Say whether the case as drafted fits the format, and list anything it cannot express. In particular, say yes or no: is any answer in the final theory only right in combination with another answer? Do not put any solution detail in your reply."

## Your steps

1. Read "Plain-language goal" and the table under "What you are approving". About ten minutes.
2. Read the five decisions under that table. Each has the author's recommendation built in.
3. Answer Q1 when asked. "Agree" is a valid answer.
4. Reply on issue #355 with "approve 0093", or say what to change.
5. Send the message under "Owner actions" to the case-writing session.

---

# Acceptance Criteria

Every test below runs without a network, without a real database server, and with the model router replaced by one that fails the test if it is called.

**Part A**
- [ ] A1 to A6: one test per rule loads a fixture case broken in exactly that way and asserts the loader refuses it with that rule's name. `engine/tests/test_authored_case.py`.
- [ ] The valid fixture case loads at 2, 3 and 4 players.
- [ ] The summary report for the valid fixture, and for each broken one, contains none of the fixture's labels, texts or IDs. Test asserts this by searching the output.
- [ ] Loading the same file twice gives equal objects; no randomness.

**Part B**
- [ ] After a choice, the concepts it gives are returned by the "what does this participant hold" function for that participant and for nobody else.
- [ ] A concept a participant only heard from another character is not returned by that function. Test.
- [ ] After session start, each cast character's `knows` list is in the knowledge graph.

**Part C**
- [ ] Both registered arc files load unchanged, and `pytest engine/tests/` passes with no existing test edited to make it pass.
- [ ] An arc file with phases on some beats and not others is refused.
- [ ] Each phase ends on each of its listed rules. One test per rule, with a controlled clock.
- [ ] Calling the tick twice with the same time makes each change once.
- [ ] Pause then resume keeps the time left in the phase and in the active run, to the second.
- [ ] After entering a `scene` phase, the written lines are published once, with the audience the arc file names.
- [ ] After every transition the test reads the state back and asserts the expected beat and phase, because a refused transition does not raise.
- [ ] Typed input on a phased arc does not change the beat or phase.

**Part D**
- [ ] A participant with budget 6 can make six paid choices; the seventh is refused and nothing is saved for it.
- [ ] Choosing something already taken costs nothing.
- [ ] The same choice ID sent twice has one effect and returns the same answer.
- [ ] A choice is refused outside a `choices` phase, for an opportunity not on that participant's menu, and for a participant not in the session.
- [ ] Menu, budget and holdings read the same after every service object is rebuilt over the same database (the restart case).
- [ ] No event with a shared-screen audience, and no event addressed to another player, contains the content of a choice. Test scans every event of a full run.
- [ ] Route handlers contain no rule: each calls one engine function. Checked in review.

**Part E**
- [ ] Entering a `mini_game` phase creates and starts exactly one run, and the run records its beat and binding.
- [ ] With zero submissions the run ends when its deadline passes, and the phase ends.
- [ ] Each end state (completed, timed out, host resolve, host cancel) ends the phase.
- [ ] A beat with no binding skips the phase; a binding that cannot be resolved ends the phase with a recorded error.
- [ ] The existing mini-game tests pass unchanged.

**Part F**
- [ ] After one headless session, one query per fact returns rows.
- [ ] Each of the four questions is answered by a function that reads only saved records, not content files. Test.
- [ ] A test fails if the count of the words listed in inventory section 7 rises in `engine/` outside tests.

**Whole spine**
- [ ] **Named headless proof:** `engine/tests/test_spine_headless.py::test_full_run_reaches_final_beat`, at 2 and at 4 participants, on the fixture arc (opening, three rounds, a final beat) and fixture case. It asserts the full order of beats and phases, the budgets, one mini-game run per round, and that the model router was never called.
- [ ] The same run with nobody doing anything at all also reaches the final beat on clocks alone.
- [ ] `scripts/checks/provider_leak_check.py` and `scripts/checks/knowledge_query_guard.py` pass. `python -m ruff check engine api` and the type check pass.
- [ ] No file under `sdk/`, `dashboard/` or `nightcap-web/` is changed.

**Merged, deployed, verified in play.** These are separate and are reported separately.

| State | What it means here |
| --- | --- |
| Merged | Each build task's pull request is on main with the checks above green |
| Deployed | Not applicable before session 3. The build runs on the founder's PC through `scripts/rehearsal.py` |
| Verified in play | One round seen on a real TV and two phones, recorded on issue #356. Until then the spine is proven in tests only |

---

# Test Plan

- **Unit tests:** the loader and each fairness rule; the holdings function; menu building; the budget; each phase rule; the tick.
- **Integration tests:** the named headless proof at 2 and 4 participants; the idle run; pause and resume; the restart case; the privacy scan over every event; the mini-game run tied to its round.
- **API tests:** each new route's happy path, wrong role, wrong session and repeat request.
- **Manual testing:** one round on a TV and two phones with the old plain screens, during AW-303. It will look rough; the point is that it moves by itself.
- **Performance:** the tick over twenty active sessions takes under 200 milliseconds in a test. Session 1 has one session.

---

# Build order

At most two build sessions at once. The second and third change the same files, so they run one after the other.

| Order | Task | Depends on | Can run beside |
| --- | --- | --- | --- |
| 1 | AW-324: case format, loader, fairness check, holdings (Parts A and B) | This spec approved | Nothing yet |
| 2 | AW-325: phases, tick, scene and bridge delivery, budget, routes (Parts C and D) | AW-324 | AW-305 (the case, written to Part A) |
| 3 | AW-303: mini-game start, clock and return (Part E) | AW-325 | AW-304 |
| 4 | AW-304: play records and the query functions (Part F) | AW-325 | AW-303 |

---

# Risks and Unknowns

**Risks**
- **The case does not fit the format.** The case-writing session has a draft this author has not seen, by the spoiler rule. If it needs something Part A cannot express, the format changes before AW-324 starts. The owner action above tests this early.
- **Size against the date.** Four build tasks across most engine modules, due by 2026-11-28 on the status page. If it runs late, the cut order on the status page applies: three mini-games become two, then three beats become two.
- **A refused transition is silent.** The state chart ignores a transition whose guard fails. Every test reads the state back.
- **The test database is not the real one.** Tests run on an in-memory database; the real one is Postgres. Anything that depends on row locking (the budget check, the tick) is also run once against Postgres before the TV check.
- **The once-a-second loop in more than one process.** Safe because every change is checked against saved state first, but untested beyond one process.
- **The fairness check is necessary, not sufficient.** It proves a case can be solved by rule. It does not prove the case is fun or clear. Only play does.
- **Game words.** "Case" and "solution" are used as generic terms, as spec 0092 does. If AW-274 later chooses other words, this code is renamed with the rest.

**Unknowns**
- Whether the old plain screens show the new events well enough for the TV check, or whether the check has to wait for the screens spec.
- Whether one written scene per round reads well at the lengths the case author writes. A playtest question.
- The right length of each phase. All are configuration; first values come from the case author and are tuned after the founder TV run.

---

# Open Questions

- **Q1. What does winning a mini-game give in session 1?** **Answered 2026-11-16: option 1 (D-126). See "Q1 Answered" at the end.** Today a finished mini-game releases the same clue to every player, and the winner gets nothing extra. The GDD says rewards should be opportunities, and that winning must not replace detective work. Options: (1) the top-ranked player or players get one extra investigation, and nobody gets case information from the mini-game (author's recommendation: it is the GDD's own example, it uses the budget built here, and it is a small engine hook); (2) keep today's behaviour for session 1; (3) decide it with the first case's mini-game wrappers. Blocks: none of the four build tasks. It is settled before the screens spec.

Nothing else is open. Questions the build sessions find are raised on their task's issue, not decided silently.

---

# Founder Approval (2026-11-16)

Recorded by the Scribe from the founder's message in session on 2026-11-16. Decision row: D-124. Also recorded on issue #355.

**Founder's words:** "Approve 0093"

**What this approves.** Phase gate 1 of this spec: Parts A to F, the five decisions listed under "What you are approving", and the direction of the changes across engine modules. It permits AW-324, AW-325, AW-303 and AW-304 to write their plans, in the build order above.

**What this does not approve.** Any build task's plan or code; each plan is shown to the founder first (phase gate 2). Spec 0094. An answer to Q1, which stays open. Any table change, new dependency, prompt change or model call; this spec says none is needed, and a build session that finds otherwise stops and asks.

**Still open at approval.** The case-writing session has not confirmed that its draft fits Part A. If it does not fit, the format is changed and the change is shown to the founder before AW-324 builds on it.

---

# Q1 Answered: What A Mini-Game Win Gives (2026-11-16)

Recorded by the Scribe from the founder's message in session on 2026-11-16. Decision row: D-126. Also recorded on issue #355.

**Founder's words:** "Go with your mini-game recommendation."

**What was decided.** Option 1. The top-ranked player or players of a mini-game get one extra investigation. Nobody gets case information from the mini-game.

**How it is built.** This part is the author's proposal. The founder's answer chose the option; the design below is approved through the build task's plan, like any other.

- The reward is a setting on the beat's mini-game binding in the arc file: what is given, how much, and to whom. First values for the session 1 arc: one investigation, to the top-ranked.
- An arc that sets no reward behaves exactly as today. The old arcs do not change.
- "Top-ranked" is read from the standing that spec 0094, Part I, puts on every finished run. Everyone tied at the top gets the reward.
- The extra investigation is added to that participant's budget (Part D) and saved, so a restart keeps it. It is given once, even if the end of the run is processed twice.
- The session 1 arc's mini-games release no case information. How that is switched off is settled in the build task's plan.
- Changing the reward later (two investigations, a different prize, none) is an edit to the arc file, not to code. This keeps the choice cheap to change after a playtest (D-127).

**Task.** AW-328, after AW-303 and AW-325. It also records the standing, which AW-326 then reads.

**What this changes above.** "Out of Scope" lists the reward as Q1; it is now in scope through AW-328. The line that says Q1 "is not approved by this spec" is answered by D-126. Part E's "what a package releases is not changed" still holds for the code: releases are switched off in the session 1 arc file, not removed.
