---
id: engineeringpractice.specs.0094-endgame-for-the-thin-version
namespace: engineering-practice
title: "Spec 0094: Endgame For The Thin Version"
owner: Nico Janssen
status: active
review_by: "2027-02-16"
sensitivity: internal
source: authored
x-scope-evidence: D-112, D-118, D-123
tags: []
supersedes: []
---

# Spec 0094: Endgame For The Thin Version

**Status**: Approved by the founder on 2026-11-16 (D-125, issue #355). This permits AW-326 and AW-327 to write their plans once the tasks before them are merged. Each plan needs the founder's approval before code. It builds on spec 0093 (approved, D-124). See "Founder Approval" at the end.

**Author**: Claude Code (Spec Author role) | **Date**: 2026-11-16 | **Task**: AW-302, the endgame spec of three | **Checked against**: main at `bd7f32c`

**Canonical path**: `docs/specs/0094-endgame-for-the-thin-version.md`

---

# Plain-language goal

When this is built, the game finishes by itself. After the last round, Last Call starts a countdown. Each player privately picks who did it and arranges a short chain from what they found, then locks it. When everyone has locked or the time is up, the room sees who each player accused, then what really happened, then who solved it, then a short line about how each player played. Rules decide every result. No AI judges or writes anything.

It covers the engine and its routes only. How it looks is the screens spec.

---

# What you are approving

| Part | What it does | Build task |
| --- | --- | --- |
| G. Last Call and the private lock | A countdown. Each player builds a theory in private and locks it. A lock cannot be changed | AW-326 |
| H. The theory check | A rule decides whether each locked theory solved the case. Same theories, same result, every time | AW-326 |
| I. The winner and the tie-break | One solver wins. Several solvers are split by mini-game results, never by speed. No solver means nobody wins | AW-326 |
| J. The closing sequence | In order: who each player accused, the written truth, the result, and a short line about each player | AW-327 |

**Decisions that are approved if you approve this spec.** Each is the author's recommendation.

1. **A player who has not locked when time runs out.** Their latest saved draft is locked as it stands. If they saved nothing, they have no theory and cannot win. The GDD wants the pressure on deciding, not on tapping fast.
2. **The tie-break.** Among players who solved it: most mini-games won, then best overall placing across the mini-games. If they are still level, they share the win. Speed is never used (GDD).
3. **The Postmortem for session 1 is written by a person and chosen by rule.** The engine measures what each player really did (for example: never used the last investigation, looked into the same thing three times, won every mini-game). The game's content file holds written lines, each tied to one such measure. No AI writes it. A generated Postmortem needs a prompt, which is a hard rule, and is left for later.
4. **The truth is written by the case's author** and lives in the case file, which is the spoiler file. Nobody reads it to you.
5. **The old points code is left alone.** The inventory proposed lifting the countdown and the lock out of `engine/scoring`. Reading that code showed it is built around penalties for wrong accusations and a table named for suspects. It is simpler and cleaner to build Last Call on the clock from spec 0093 and leave the old code untouched and unused.
6. **Nothing shows whether you are right before everyone has locked.** Not to the player, not to the host, not in any route.

**Hard rules this spec touches (AGENTS.md).**

| Hard rule | Touched | Detail |
| --- | --- | --- |
| Changes across engine modules | **Yes** | `session`, `case`, `interactions`, `mini_games` (one field on a finished run), `telemetry`, plus thin API routes |
| Database tables or migrations | **No** | Drafts, locks and results are saved in the tables spec 0093 already uses |
| New dependencies | **No** | |
| Prompts or evaluation suites | **No** | No model call. Truth and Postmortem lines are written by people |
| Secrets or sign-in | **No** | |

---

# References

- Umbrella: [spec 0092](0092-nightcap-gdd-rebuild.md), work packages 10 and 11, open question Q3, and its acceptance criteria on the pure resolver, the three result branches and heard-versus-held.
- Builds on: [spec 0093](0093-engine-spine-for-the-thin-version.md): the case file (`solution`, `closing`), what each player holds (Part B), phases and the tick (Part C).
- GDD: [Last Call and Case File](../gdd/nightcap/01-authoritative-gdd/05-last-call-case-file.md), [Truth, Verdict, Postmortem](../gdd/nightcap/01-authoritative-gdd/08-truth-verdict-postmortem.md), [runtime boundary](../gdd/nightcap/01-authoritative-gdd/11-arcwright-runtime-boundary.md).
- Inventory: [work package 0](0092-wp0-thin-version-inventory.md), section 2 rows for Last Call, final theory, the check, and the closing sequence.
- Scope: [Nightcap status page](../product/nightcap-status.md). Decisions D-112, D-118, D-123.

**x-scope-evidence**: `D-112`, `D-118`, `D-123`. This spec adds no product scope beyond the thin version's must-have list.

---

# Overview

Add four phase kinds to the round engine of spec 0093 (`commit`, `reveal`, `result`, `recap`), a pure function that judges locked theories against the case file, a rule for the winner, and written closing content chosen by rule, so that a headless session runs from join to the last line at two and at four players with no model call.

---

# In Scope

## Part G. Last Call and the private lock

- A new phase kind, `commit`. On entry it starts the authored countdown and opens each player's private theory form.
- The form has the slots the case file's `solution` lists, in order. For a cast slot the player may pick any cast member the case marks as selectable. For a concept slot the player may pick any concept they hold, true or misleading. The engine never narrows the list toward the right answer and never orders it by importance.
- A player can save a draft as often as they like. Each save replaces the last. A draft survives a reconnect and an API restart.
- Locking makes the draft final. A lock is refused if any slot is empty. After a lock, any further save or lock from that player is refused.
- A concept the player does not hold is refused when the draft is saved. Something only heard is not held (spec 0093, Part B).
- The phase ends when every player has locked, or the countdown reaches zero, or the host moves on. At that moment any complete saved draft that is not locked is locked. A player with no complete draft is recorded as having no theory.
- Until the `reveal` phase, a player's draft and lock are sent to that player only. The host and the shared screen learn only who has locked.
- Pause and resume keep the time left, as for every phase.
- **Why no separate trigger rule:** the GDD wants Last Call to come at an authored moment and only once the case could fairly have been solved. In the thin version it comes after round three, and the loader's rule A3 already proves the case could be solved within the budget by then.

## Part H. The theory check

- One pure function takes the case file's `solution` and the locked theories, and returns, for each player and each slot, right or wrong.
- A slot is right when the player's answer is in that slot's accepted list. A theory solves the case when every slot is right.
- The function reads nothing else: no clock, no order of arrival, no text, no model. The same inputs always give the same result.
- It is run once, in the `result` phase. No route and no event exposes any part of its output before then.

## Part I. The winner and the tie-break

- Exactly one player solved it: that player wins.
- More than one solved it: compare, in order, the number of mini-game runs each won, then the sum of their placings across all runs (lower is better). Still level: they share the win.
- Nobody solved it: no player wins. The result says the case won.
- For this, every finished mini-game run records a **standing**: the players in order, with ties allowed. A mechanic that cannot rank its players records them all as tied. This is one added field in the run's saved outcome and a small change in each of the four mechanics.

## Part J. The closing sequence

Three more phase kinds, used in order on the final beats of the arc file. Each ends on its authored time, or when every player has marked ready, or when the host moves on.

| Phase | What the engine sends | To whom |
| --- | --- | --- |
| `reveal` | For each player, the answer in the slot the case marks as shown first (in Nightcap, who they accused). Nothing else from their theory | Everyone |
| `scene` (already in spec 0093) | The case file's written `closing` lines: what really happened | Everyone |
| `result` | Who won, or that nobody did; for each player, solved or not; and, if a tie-break decided it, which rule did | Everyone |
| `result`, private part | For each player, which of their own slots were right and wrong | That player only |
| `recap` | One written line for each player, chosen by rule from what that player did | Everyone |

- **How a recap line is chosen.** The engine works out a fixed set of measures for each player from the saved records: investigations used and left; how many different subjects they looked into; the subject they returned to most; reviews; how often they were last to mark ready; mini-games won; draft changes during Last Call; whether they locked before the time ran out; slots right. The game's content file lists written lines, each with a condition on one measure (for example "highest in the room" or "zero"). For each player the first line whose condition holds, and that no other player has been given, is used. A fallback line is required so nobody is left without one.
- A measure is only ever something the engine saw happen. No line may claim what a player thought (GDD: "If Nightcap could not observe it, Nightcap does not get to claim it happened").
- The result and every theory are saved, and readable from a route after the `result` phase, so a screen can rebuild itself and so the play record is complete.

## Routes

Thin handlers; all rules in the engine. Read my theory form (slots, my choices on offer, my draft, the time left); save my draft; lock; read the result (public part for anyone in the session, private part for the player it belongs to).

---

# Out of Scope

- Screens and any SDK or TypeScript change. Screens spec.
- An early or rule-triggered Last Call. In the thin version it follows round three.
- A generated Truth or Postmortem, and a cinematic confrontation. Both PARKED or later; a generated one needs prompt approval.
- Showing each player's whole theory to the room.
- Points, momentum, wrong-accusation costs, and everything in `engine/scoring`. Untouched and unused.
- The end-of-session survey. The existing replay-intent route stays as it is; the survey itself is in the screens spec and AW-308.
- Ending the session record automatically. The host ends it as today. The session-end record still carries an old game word, which stays with AW-274.
- Writing the first case's `solution`, `closing` and recap lines. Content, done in AW-305 and reviewed without spoilers.

---

# Human Collaboration Contract

**Interaction profiles:** Decision interview for approval. Independent execution for the two build tasks after each plan is approved. Creative collaboration for the recap lines.

**Classification rationale:** The lock, the check and the winner rule are rules with testable results. The recap lines are player-facing comedy in the game's voice, which depends on the founder's taste; they describe behaviour, not the solution, so the founder can review them without being spoiled.

**Required founder inputs:**
- Approval of this spec, including the six decisions listed under "What you are approving".
- Review of ten sample recap lines before the full set is written.

**Phase gates:**
1. Approve this spec. Permits AW-326 and AW-327 to write their plans, once spec 0093 is approved and AW-325 is merged.
2. Approve each task's plan. Each crosses engine modules.
3. Approve ten sample recap lines. Permits writing the full set.
4. The founder TV run plays the endgame once, start to finish.

**Review package:** this file. "What you are approving" is the part to read.

**Approval evidence:** the founder approved this spec on 2026-11-16: decision D-125, issue #355, and "Founder Approval" at the end of this file.

**Owner actions:** none beyond the steps below.

## Your steps

1. Read "Plain-language goal" and "What you are approving". About ten minutes.
2. Reply on issue #355 with "approve 0094", or say what to change. It can be approved after 0093; nothing in it is built before AW-325.
3. Later, when asked: read ten sample recap lines and say which sound like the game.

---

# Acceptance Criteria

Every test runs without a network, without a real database server, and with the model router replaced by one that fails the test if it is called.

**Part G**
- [ ] A draft can be saved, changed and read back; it reads the same after every service object is rebuilt over the same database.
- [ ] A lock with an empty slot is refused. A save or lock after a lock is refused and changes nothing.
- [ ] A draft naming a concept the player does not hold is refused, including a concept that player only heard from another character.
- [ ] The list offered for a concept slot equals the set the player holds, true and misleading alike, in an order that does not depend on which answers are accepted. Test compares the offer for two fixture cases that differ only in their accepted answers.
- [ ] The phase ends on each of its three rules. At the end a complete unlocked draft becomes locked; a player with none is recorded as having no theory.
- [ ] Before the `reveal` phase, no event to the shared screen, to the host or to another player contains any part of a draft or lock, and no route returns one to anyone but its owner. Test scans every event and calls every route as each role.

**Part H**
- [ ] The check is a pure function: called twice with the same inputs it returns equal results, and it is importable and callable with no database, clock or router. Property test over generated theories.
- [ ] Before the `result` phase, no route or event carries any right-or-wrong information. Test.

**Part I**
- [ ] One test per branch: one solver wins; two solvers split by mini-games won; two solvers level on wins split by placings; two solvers level on both share the win; no solver gives no winner.
- [ ] No input to the winner rule is a time or an order of arrival. Checked by the function's signature and in review.
- [ ] Every finished run of each of the four mechanics records a standing that names every eligible player once.

**Part J**
- [ ] The `reveal` event contains each player's shown-first answer and nothing else from any theory.
- [ ] The private part of the result reaches only its own player.
- [ ] Each recap line condition is tested against a fixture record; no two players get the same line; a player matching no condition gets the fallback.
- [ ] Every measure is computed from saved records only. Test rebuilds the measures after a restart and gets the same values.

**Whole game**
- [ ] **Named headless proof:** `engine/tests/test_endgame_headless.py::test_full_game_join_to_recap`, at 2 and at 4 participants, on the fixture arc and case. It asserts the full order of beats and phases from join to the last recap line, the result in each of the three branches, and that the model router was never called.
- [ ] The same run with nobody doing anything reaches the end on clocks alone, with no winner.
- [ ] `engine/` gains no word from the list in inventory section 7. The words "culprit", "accusation" and "suspect" do not appear in the new code; the case file supplies every label.
- [ ] `pytest engine/tests/`, the API tests, ruff and the type check pass. No file under `sdk/`, `dashboard/`, `nightcap-web/` or `engine/scoring/` is changed.

**Merged, deployed, verified in play.**

| State | What it means here |
| --- | --- |
| Merged | Both build tasks' pull requests are on main with the checks above green |
| Deployed | Not applicable before session 3. Runs on the founder's PC |
| Verified in play | The founder TV run reaches the last recap line once, recorded on the run's issue. Until then the endgame is proven in tests only |

---

# Test Plan

- **Unit tests:** the theory check; the winner rule, one per branch; each recap measure; line selection.
- **Property test:** the check gives the same result for the same inputs, over generated theories.
- **Integration tests:** the named headless proof at 2 and 4 participants in all three result branches; the idle run; restart in the middle of Last Call; the privacy scan before `reveal`.
- **API tests:** each route's happy path, wrong role, wrong session, and a second lock.
- **Manual testing:** the founder TV run.

---

# Build order

| Order | Task | Depends on |
| --- | --- | --- |
| 1 | AW-326: Last Call, the lock, the theory check, the winner rule (Parts G, H, I). The standing on each run is built first by AW-328, because the mini-game reward (spec 0093, Q1, D-126) needs it | AW-325, AW-303 and AW-328 merged |
| 2 | AW-327: the closing sequence and the recap lines (Part J), and the join-to-recap headless proof | AW-326; AW-304 for the measures |

---

# Risks and Unknowns

**Risks**
- **Per-slot answers may be too simple for some cases.** Each slot is judged alone. A case where answer A in slot 2 is only right together with answer B in slot 3 cannot be written in format version 1. The case-writing session is asked whether the first case needs that (the owner action in spec 0093). If it does, accepted combinations are added before AW-324 starts.
- **The form may be fiddly on a phone.** The GDD marks the interaction TESTING and parks a simpler fallback (culprit plus a few decisive facts). The engine side is the same for both; only the screens differ.
- **Recap lines can fall flat.** Rule-chosen written lines are safe and cheap but can feel canned. The ten-line sample is the check. If time runs short, the status page's first cut applies: one fixed closing text.
- **Depends on spec 0093's case format.** Spec 0093 is approved, but the case-writing session has not yet confirmed its draft fits the format. A change to the case file there changes this spec.
- **A refused transition is silent.** As in spec 0093, every test reads the state back.

**Unknowns**
- How long Last Call should be. Configuration; the first value comes from the founder TV run.
- How many slots the first case uses. Set by the case's author inside the spoiler file; the engine accepts any number from two up.
- Whether seeing only "solved or not" feels like enough of a result in the room. A playtest question.

---

# Open Questions

None that block approval. The recap lines' voice is settled by the ten-line sample (phase gate 3), not by this spec.

---

# Founder Approval (2026-11-16)

Recorded by the Scribe from the founder's message in session on 2026-11-16. Decision row: D-125. Also recorded on issue #355.

**Founder's words:** "Approved Spec 0094 (endgame)." In the same message: "Lets move quickly and be open to change if they ont turn out to be the best solution. We need to be quick, nimble, flexible, and open to trying different things safely. remember that."

**What this approves.** Phase gate 1 of this spec: Parts G to J, the six decisions listed under "What you are approving", and the direction of the changes across engine modules. It permits AW-326 and AW-327 to write their plans when the tasks before them are merged.

**What this does not approve.** Any build task's plan or code; each plan is shown to the founder first. The recap lines; ten samples are reviewed first (phase gate 3). Any table change, new dependency, prompt change or model call; this spec says none is needed, and a build session that finds otherwise stops and asks.

**Open to change (D-127).** The founder approved this as the current best plan, not as a fixed contract. A build session that finds a better way says so on its task's issue with a recommendation, and the change is recorded here before it is built.

**Changed with this approval.** The standing on each finished mini-game run (Part I) is built by AW-328 instead of AW-326. The mini-game reward (spec 0093, Q1, answered the same day as D-126) needs the standing first. What Part I says is unchanged; only the task that builds that one field moved.

---

# Change Approved 2026-11-19: The Theory Reads As An Account, With One Proof (D-138)

Recorded from the founder's answer in session on 19 November 2026 (spec 0095 Q5). The question's chosen option said: "Spec 0094's Verdict change is approved by this answer."

- **Part G.** The case file gives the solution slots an account text: a short sentence written by the case's author, with one blank per slot, in the slots' order. The form shows that text. The player also chooses one held concept as their **proof**; it is saved with the draft and locked with it. A lock still needs every slot filled; whether the proof is required to lock is settled in AW-326's plan.
- **Part H and Part I are unchanged.** The proof is not judged and does not change who solved it or who wins.
- **Part J, `result`.** The public part adds the winner's proof (or each co-winner's). Nobody else's proof is shown publicly. The private part is unchanged.
- No table change, no model call. Build tasks: AW-326 (account text, proof field), AW-327 (proof at the Verdict).

---

# Plan Answers Approved 2026-11-18: AW-326 (issue #388)

Recorded from the founder's approval of the AW-326 plan in session, with all four recommended answers.

1. **The proof is optional to lock.** A complete draft with no proof locks, and is auto-locked at time-up. Making it required later is a one-line change.
2. **The account text** is a case-file field `account`: one string with `{slot_id}` blanks, one per solution slot, in the slots' order. The loader refuses anything else. A case without it still loads. The form route returns it split into text pieces and blanks.
3. **A placing is the tier number** in a run's standing (best tier 1, ties share a number). A player missing from a run is placed after its last tier. Placings are summed across all finished runs that have a standing. A run is won by its top tier, and by nobody when that tier holds every player.
4. **AW-326 stops before the `result` phase.** It builds the check, the winner rule and `resolve_endgame` (`engine/session/endgame.py`), which reads saved rows, saves nothing and sends nothing, and refuses while a commit phase is open. No result event or route exists until AW-327, which also owns the join-to-recap headless proof.

Also settled: the check reads only each slot's accepted values and ignores an answer's `needs`. The shared screen and the host are told only who has locked and how many (`theory_lock_progress`); other players' phones are told nothing. The public round view's `ready_count` is the locked count during a commit phase.
