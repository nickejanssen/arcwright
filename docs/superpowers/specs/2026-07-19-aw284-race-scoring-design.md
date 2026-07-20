# AW-284 Race Scoring And Accusation State — Design

> Status: Founder-approved 2026-07-19 ("Lets go with this!")
> Canonical path: docs/superpowers/specs/2026-07-19-aw284-race-scoring-design.md

## What this represents

The full scoring and accusation-state model for Couch Race: how points are
computed (invisible to players), how accusations are submitted and gated,
how the five locked accusation features interact, how the state machine
realizes an early "first correct accusation" trigger against AW-281's
shipped arc, and the three required end paths. This is the artifact the
AW-284 implementation plan is written directly from — every number and
mechanism below is meant to be code-concrete, not aspirational.

Full discovery record and checkpoint evidence:
[docs/product/aw284-discovery-and-checkpoints.md](../../product/aw284-discovery-and-checkpoints.md).

## What it tests

- That "catches dominant" scoring weighting produces sensible outcomes
  under both a skill-heavy playstyle and the best-case pure-luck playstyle
  (Scenarios A/B below).
- That the beat-scoped wrong-accusation cost genuinely disincentivizes
  reckless guessing without ever eliminating a player (Scenario C).
- That all three required end paths are distinctly reachable and
  deterministic, including the edge case (all-players-locked-early) that
  is easy to conflate with plain countdown expiry but is a materially
  different state.

## What needs founder attention

Nothing outstanding — this doc reflects only decisions the founder already
approved (discovery record checkpoints table). It exists to make those
decisions code-concrete for the implementation plan, not to raise new
forks.

---

## 1. Scoring dimensions and base values

Three dimensions, matching the story bible (Section 8), computed
deterministically and never shown to players as raw numbers or category
names (Section 2 covers presentation).

**Table 1 — base point values** (Rehearsal-1 starting values; retune from
real telemetry, same pattern as AW-287's bank-cap values)

| Dimension | Value | Notes |
|---|---|---|
| Evidence found (individual) | 10 | steady, reliable, per `EvidenceEntry` delivered and acted on |
| Mini-game performance | 15–40 | linear scale from participation floor to best-result ceiling; converts each package's own internal result into race points |
| Contradiction catch (confirmed) | 50 | the marquee dimension — keyed **only** to AW-283's `contradiction_confirmed` outcome event, never a raw flag attempt |
| Correct accusation, at Grill start | 200 | earliness-curve peak |
| Correct accusation, mid-Twist | ~130 | curve midpoint; the curve is continuous, not a step function — implementation should interpolate by elapsed-session-time or beat-progress-fraction, not hardcode three discrete tiers |
| Correct accusation, in Last Call | 60 | curve floor |
| Motive/method bonus (each, on a correct accusation) | +25 | up to +50 total stacked |

## 2. Player-facing presentation — Hidden Score, Loud Moments + Race Track

No live numbers or dimension names (evidence/contradiction/accusation) are
ever shown to players. Every scoring event (Table 1-4 math, computed
server-side) renders as an animated sting — icon, a short phrase, sound —
never a bare digit or a category label. A shared-TV race-track
visualization gives constant, visible relative motion by blending all
three dimensions into one token position per player; this satisfies the
product's own "race" framing throughout the session, not only at a hidden-
score reveal. Track motion must never let a player's specific accusation
proximity leak (it blends evidence + catches + momentum together, and
accusation itself stays a private, binary, undisclosed submission until
Last Call). The full plain-language breakdown ("Evidence Found," "Lies You
Caught," "The Verdict") unpacks only at the Truth beat's reveal.

Engine-side, this means every scoring `ContentEvent` this task emits must
carry real `presentation_hints` (animation/voice/emotion hints per
`engine/events/models.py`) and must not place a raw numeric score or a
dimension name in any pre-reveal event's payload — mirrors the same
leak-guard pattern AW-283 uses for `is_authorized_lie`/`falsehood_id`
(`engine/claims/events.py`, per its own Must Not Do). The reveal-time
events (Truth beat only) are the one place raw per-dimension totals may
appear in a payload.

## 3. Momentum-weighted accusation bonus (primary mechanic)

**Table 2 — momentum multiplier**

| Confirmed catches banked since last accusation attempt | Bonus to accusation payoff |
|---|---|
| 0 | +0% |
| 1 | +10% |
| 2 | +20% |
| 3 | +30% |
| 4 | +40% |
| 5+ | +50% (capped) |

The streak counter increments once per `contradiction_confirmed` event
attributed to the accusing player, and resets to 0 the moment that player
submits *any* accusation (correct or wrong) — spending the streak, not
decaying it on a timer. This keeps the mechanic legible ("catches you
banked before you accused") without a confusing hidden decay clock. The
multiplier applies to the base accusation value (Table 1) before the
motive/method bonus is added.

## 4. Beat-scoped wrong-accusation cost

**Table 3**

| Beat | Lockout | Penalty | Repeat-offense escalation |
|---|---|---|---|
| Grill | 1 interrogation round | −20 | lockout ×1.5, penalty ×1.5 per repeat, same player |
| Twist | 1.5 rounds | −40 | same |
| Last Call | rest of Last Call, minus the player's one free Last Word | −60 | same, capped at remaining Last Call time |

These values live in arc configuration (`nightcap/couch-race.arc.json`),
keyed by `beat_id`, not engine constants — per the platform's configurable-
composition principle. Lockout state is enforced server-side: an accusation
submission attempted while a player's lockout is active is rejected by the
server, not merely hidden by the client UI (abuse mitigation, discovery
decision 5).

## 5. Chain-reaction Last Call

**Table 4**

| Additional correct accusation (after the 1st) | Countdown cut |
|---|---|
| 2nd correct | −20% of remaining time |
| 3rd correct | −20% of remaining (compounding on the already-reduced value) |
| 4th+ | −20% each, floor at 30 seconds minimum |

The floor exists so Chain Reaction can never collapse the countdown to zero
and skip the Last Call moment entirely for players still deciding.

## 6. The Last Word and Suspect Lock

- **The Last Word**: once per player, during Last Call only, a locked-in
  accusation may be changed once with no additional penalty beyond
  whatever the original submission already cost. Implemented as a
  per-player boolean flag (`last_word_used`) checked before allowing a
  second Last-Call submission to bypass the normal lockout-after-wrong-guess
  rule.
- **Suspect Lock**: a private, non-scoring "working theory" a player may
  set at any point from Grill onward, overwritable at will, carrying zero
  point value and zero lockout interaction. Recorded so the reveal (Truth
  beat) can narrate it back ("you suspected Marcus from the start") per the
  story bible's "the reveal is the trust contract" framing. Must not be
  readable by any other player before the reveal (private, per-player
  state).

## 7. Accusation tie-break

Server-authoritative receipt timestamp; the first **correct** accusation
received (by server clock, never client-supplied time) triggers the
table-wide Last Call transition. This closes the question D-077 flagged
AW-284 needed to resolve independently (issue #238) rather than assuming
AW-283's claim-flag tie-break answer carries over automatically — it does
carry over, by the same reasoning (first-received-wins, deterministic,
server-authoritative), confirmed as the right answer for accusations too
after this discovery pass.

## 8. State-machine mechanism for the early Last Call trigger

The shipped `nightcap/couch-race.arc.json` (AW-281) beat graph is linear:

```
pour -> scene -> grill -> twist -> last_call -> truth
```

with `grill.exit_conditions = ["interrogation_rounds_complete"]`,
`twist.exit_conditions = ["twist_delivered"]`, and
`last_call.exit_conditions = ["accusations_locked_or_countdown_expired"]`.
The StateChart guard for any generated transition event is
`ALL(source_beat.exit_conditions + target_beat.entry_conditions)`
(`engine/arc/arc_state.py`) — critically, **every outgoing edge from a
given source beat shares that same source beat's exit_conditions list**,
so two different edges out of `grill` cannot be gated on two unrelated
triggers by giving `grill` two different exit-condition lists.

The mechanism that works without any engine code change:

1. Rename `grill`'s exit condition to a single synthetic flag,
   e.g. `grill_exit_ready`, and `twist`'s to `twist_exit_ready`. The
   orchestrator (session service) sets these flags to `True` for **either**
   underlying cause: normal completion (`interrogation_rounds_complete` /
   `twist_delivered`) or a first-correct-accusation landing during that
   beat. The flag name stops meaning "rounds finished" specifically and
   starts meaning "this beat is over, for any reason" — the orchestrator,
   not the guard, is responsible for knowing which cause fired.
2. Add a new arc-graph edge `grill -> last_call` (alongside the existing
   `grill -> twist`), and keep `twist -> last_call` as the only edge out of
   `twist` (no branching needed there — an early accusation during Twist
   reuses the existing edge, it doesn't need a second one).
3. Leave `last_call.entry_conditions` and `twist.entry_conditions`
   **empty, exactly as shipped** — do NOT put a distinguishing flag there.
   `last_call.entry_conditions` is shared by *both* of last_call's incoming
   edges (the new `grill -> last_call` shortcut AND the existing
   `twist -> last_call` normal path); gating it on something like
   `accusation_triggered_early` would also block the normal
   Twist-completion path whenever nobody has accused early yet, which
   would make Endgame Path 2 (countdown expiry, nobody correct)
   unreachable. This was an error in an earlier draft of this section,
   caught during plan-grounding — corrected here.
4. Because `grill_exit_ready` alone is the only condition on both of
   grill's outgoing edges, `advance_grill_to_twist` and
   `advance_grill_to_last_call` end up with **identical guards** — both
   are satisfiable the instant `grill_exit_ready` is true, regardless of
   which underlying cause set it. This is safe only because the
   orchestrator, never the StateChart, decides which specific event to
   invoke: it tracks separately (in application code, not in arc data)
   whether the beat ended via normal completion or via a first-correct
   accusation, and calls the matching event. This matches the codebase's
   existing invariant that guards gate an invoked event, they don't
   auto-select among several satisfiable transitions — but it does mean
   the guard can no longer catch an orchestrator bug that calls the wrong
   event for the wrong reason. The implementation plan must include an
   explicit test asserting the orchestrator invokes
   `advance_grill_to_twist` on normal completion and
   `advance_grill_to_last_call` on an early correct accusation — not just
   that some transition fires and lands in a plausible-looking beat. Per
   the known StateChart silent-guard behavior, a call to an event whose
   guard isn't satisfied is silently ignored, not raised, so this test
   must also assert on `session_context`/current-beat state after the
   call, not just that the call didn't raise.

This is an arc-content change (`nightcap/couch-race.arc.json`) plus
session-orchestration logic, not an `engine/arc/` code change, and sits
squarely inside AW-284's own declared Technical Scope ("First-correct-
accusation transition: opens table-wide final lock-in, then forces beat
transition to The Truth"). It does touch AW-281's already-merged arc file,
which the implementation plan should call out explicitly rather than treat
as a silent side effect. Renaming the exit-condition flags is also a
grounding risk, not just an arc-data edit: the implementation plan's first
task must grep for any existing code, tests, or telemetry that reference
`interrogation_rounds_complete` or `twist_delivered` by their literal old
names (AW-282/AW-283 orchestration code is the most likely place) and
update every call site consistently, the same way the AW-283 plan's own
Task 1 was a mandatory grounding step before touching shared state.

## 9. Representative scoring scenarios

Sanity-checking that "catches dominant" (discovery decision 7) holds under
real point math, not just as a stated intention.

**Scenario A — The Careful Detective.** 4 evidence finds (4 × 10 = 40) + 3
confirmed catches (3 × 50 = 150, banking +30% momentum) + correct accusation
mid-Twist with the motive bonus: 130 base × 1.30 momentum = 169, + 25
motive = 194. **Total: 40 + 150 + 194 = 384.**

**Scenario B — The Lucky Early Guesser.** 1 evidence find (10) + 0
confirmed catches (0% momentum) + correct accusation at the very start of
Grill — the single best possible timing bonus in the entire game — with no
motive/method guess (200). **Total: 10 + 0 + 200 = 210.**

**Scenario C — The Reckless Accuser.** 2 evidence finds (20) + wrong
accusation in Grill, 1st offense, no catches banked yet (−20) + wrong
accusation in Twist, 2nd offense (−40 × 1.5 = −60) + 1 confirmed catch
banked afterward (50, momentum resets to 1 since the streak spent at each
wrong guess) + correct accusation in Last Call with that 1 fresh catch
(60 × 1.10 = 66). **Total: 20 − 20 − 60 + 50 + 66 = 56.**

Even Scenario B's maximum-possible lucky-timing bonus (210) scores well
below sustained catch-and-evidence play (A, 384) — the weighting holds
under the extreme case, not just on average. Scenario C shows reckless
guessing sharply tanks the final score (56 — barely a quarter of the lucky
guesser's total, despite still landing the correct answer eventually),
which is the direct implementation of the founder's "real consequences"
direction.

## 10. Endgame walkthroughs — all three required end paths

**Path 1 — First-correct, then table-wide lock-in, then Truth.** A player
submits a correct accusation mid-Grill. The orchestrator sets
`grill_exit_ready` and `accusation_triggered_early`, fires
`advance_grill_to_last_call` (Section 8), skipping the remainder of Grill
and all of Twist — the narrator bridges this gap rather than delivering
unplayed content. Last Call's countdown begins. Each further correct
accusation compresses the remaining time (Table 4). Each player may use
their one Last Word (Section 6) before the countdown or Chain Reaction
closes the window. Once `accusations_locked_or_countdown_expired` is
satisfied, `advance_last_call_to_truth` fires and the reveal narrates each
player's actual path (evidence found, catches landed, accusation timing).

**Path 2 — Countdown expiry, nobody correct.** No player ever submits a
correct accusation (wrong guesses may still happen and cost their
Table 3 penalties along the way). The session proceeds through the full
normal linear sequence — no early shortcut ever fires, so
`grill_exit_ready`/`twist_exit_ready` are only ever set by normal
completion. Last Call's countdown runs its full, normal-length course.
It expires with zero correct accusations recorded;
`accusations_locked_or_countdown_expired` is satisfied by the expiry
branch. Truth fires; the reveal announces the case wins — no elimination,
no additional penalty beyond whatever wrong guesses already cost.
Superlatives (including Most Confidently Wrong) still compute normally.

**Path 3 — All players locked out early.** During Last Call, several
players use their Last Word on a wrong final guess and end up
simultaneously locked out with no further live path to submit another
accusation (already spent their Last Word; no correct accusation recorded
by anyone). `accusations_locked_or_countdown_expired` must evaluate `True`
in this state regardless of remaining countdown time — the shipped arc's
single combined exit-condition name already anticipates exactly this OR.
Truth fires immediately rather than the table waiting out a dead timer.
This must be a distinct harness test case from Path 2, not folded into it,
since the triggering condition and the moment of firing are genuinely
different (mid-countdown vs. natural expiry).

A fourth, related but non-blocking case: a **fully passive player** (never
submits any accusation at all) must not prevent Paths 1, 2, or 3 from
resolving — they simply never contribute a lockout or a correct guess.
Abuse-mitigation acceptance criterion (discovery decision 5) requires this
as its own explicit harness test.

---

## Summary for the implementation plan

Everything in this document is founder-approved and code-concrete: the
presentation model (Section 2), 4 tuning tables (Sections 1, 3-5), the
tie-break rule (Section 7), the exact state-machine mechanism (Section 8),
3 representative scenarios, and 3+1 end-path walkthroughs. The
implementation plan should treat this document the way the AW-283
implementation plan treated its own sample-review doc — as settled input,
not a place to re-litigate open forks.
