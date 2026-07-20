# AW-284 Discovery and Checkpoint Record

**Date**: 2026-07-19

**Status**: Discovery, scoring brief, and scenario/tuning-table review all
approved; implementation plan next.

**Interaction profile**: Creative collaboration

## Discovery decisions

1. **Accusation window**: private accusations open from The Grill onward
   (not gated to Last Call) — required for the story bible's own claim that
   "the first correct accusation triggers Last Call table-wide" to be
   coherent, and to give the earliness-weighting dimension its full range.
2. **Wrong-accusation consequence**: real, beat-scoped consequences per the
   founder's explicit direction ("accusing should have real consequences if
   you get it wrong") — lockout and score penalty both escalate across
   Grill → Twist → Last Call, plus escalate again on repeat offenses by the
   same player within a session. See the scoring brief's Table 3.
3. **Accusation feature set — all five locked in**, arrived at via a
   structured ideation funnel (25 raw ideas → persona filter → 15 → 10 new
   ideas → 15 → a 9-criterion rubric → 8 → market research against Blood on
   the Clocktower, The Resistance/Avalon, Chameleon, Trivia Murder Party,
   and Fibbage → 5, stack-ranked). Momentum-weighted accusation bonus is the
   founder-selected primary mechanic:
   - **Momentum-weighted accusation bonus** (primary) — an accusation's
     payoff scales with confirmed contradiction-catches (AW-283
     `contradiction_confirmed` events only, never raw flags) banked since
     the player's last accusation attempt. Ties AW-283's headline mechanic
     directly into AW-284's scoring instead of running as two side-by-side
     systems.
   - **Chain-reaction Last Call** — each additional correct accusation
     after the first compresses the remaining countdown further.
   - **The Last Word** — one free suspect change allowed during Last Call,
     no extra penalty.
   - **Escalating lockout** — repeat wrong guesses cost progressively more
     (implements decision 2).
   - **Suspect Lock** — a private, zero-risk, zero-score "working theory"
     that the reveal narrates back to the player at the Truth beat.
4. **Beat-scoped accusation parameters**: confirmed — lockout length,
   penalty magnitude, and Last Word availability all vary by beat via arc
   configuration data (`nightcap/couch-race.arc.json`), not engine
   constants, per the platform's configurable-composition principle and the
   "do not hardcode beat IDs in engine code" rule (AW-256 lesson).
5. **Abuse-mitigation acceptance criteria** (adopted after a 50-item
   adversarial-scenario review spanning accusation/scoring abuse,
   contradiction-catch abuse, social griefing, technical/session abuse,
   content abuse, physical-world cheating, and Leverage-effect abuse):
   - Accusation tie-break is server-authoritative (receipt timestamp, never
     client-supplied), first-received-correct-accusation wins — this
     directly answers the question D-077 flagged AW-284 needed to resolve
     for itself on issue #238.
   - The momentum multiplier keys only off AW-283's `contradiction_confirmed`
     outcome events, never raw flag attempts, closing a bad-faith
     mass-flagging exploit.
   - Accusation submission is server-gated on current lockout state
     (rejected, not silently dropped, if attempted during an active
     lockout) — defense in depth beyond hiding the client-side button.
   - Harness tests must cover a fully-passive player (never submits
     anything) alongside the existing all-players-locked-early path.
   Broader session/API security items surfaced by the same review (replay
   attacks, token theft, rate limiting, seed leakage, injection) were
   explicitly scoped OUT of AW-284 as a platform-wide session-security
   concern, not a scoring-ticket concern. Content moderation was scoped out
   as already owned by `engine/safety/` (architecture principle 6).
   Physical-world cheating (photographing clues, outside coaching) has no
   technical mitigation in any party game and was not actioned.
6. **Scoring presentation — "Hidden Score, Loud Moments" plus a race-track
   visualization**: resolved via a second research-grounded design pass
   (Wordle, Kahoot, Among Us, core-loop/variable-reward literature) after
   the founder flagged that raw dimension names ("contradiction",
   "accusation accuracy weighted by earliness") read as jargon and
   "evidence found" alone read as boring. No live numbers or category names
   are ever shown to players. Every scoring event is an animated sting
   (icon + short phrase + sound); a shared-TV race-track visualization
   gives constant visible relative motion (blending all three dimensions,
   never leaking accusation proximity) so "Couch Race" stays visually a
   race throughout, not just a hidden-score reveal at the end. Full plain-
   language breakdown ("Evidence Found," "Lies You Caught," "The Verdict")
   only unpacks at the reveal. The underlying point math stays
   catches-dominant (decision 7's Table 1) — players just never see it as a
   formula.
7. **Scoring dimension weighting — catches dominant**, confirmed against
   the finalized presentation model and stress-tested in the scoring
   brief's three representative scenarios (below): even the single best-
   possible lucky-early-guess timing bonus, with zero contradiction catches,
   scores below a sustained catch-and-evidence performance. Reckless
   guessing (multiple wrong accusations before eventually landing the right
   one) scores well below either.
8. **Product-vision cross-check**: the founder asked whether the design
   was nailing "immersive story, every player racing to find the killer,
   mini-games throughout like Mario Party, a story that's unique and
   evolves with gameplay, always immersive and engaging." Assessed against
   what's actually shipped: immersive story, the race structure, and
   unique/evolving story are on track and reinforced by this task's own
   design choices (decision 6 in particular). Mini-game frequency is a real
   gap (only 2 of 6 beats have a mini-game slot in the shipped AW-281 arc;
   Grill, the longest beat, has none) but is out of AW-284's scope — see
   "Scope owner actions" below for the resulting follow-up tasks and
   decision record (D-079).
9. **State-machine finding**: the shipped `nightcap/couch-race.arc.json`
   beat graph (AW-281) is strictly linear (Pour → Scene → Grill → Twist →
   Last Call → Truth), with no shortcut edges. Realizing "first correct
   accusation triggers Last Call table-wide" as a genuine early trigger (not
   just flavor text) requires new arc-content edges (Grill→Last Call, and a
   first-correct-accusation-gated variant of Twist→Last Call) plus
   session-orchestration logic that sets the right condition flags and
   invokes the correct StateChart transition event. This is arc content and
   session logic, not an engine code change — full mechanism specified in
   the design doc below for the implementation plan to consume directly.

## Scoring brief (approved 2026-07-19)

Full tuning tables, three representative scoring scenarios (validating that
catches-dominant weighting holds even under the best-case lucky-guess
timing), and three required endgame walkthroughs (first-correct-then-
table-lock-in, countdown-expiry, all-players-locked-early) are recorded in
[docs/superpowers/specs/2026-07-19-aw284-race-scoring-design.md](../superpowers/specs/2026-07-19-aw284-race-scoring-design.md).
Founder approved as presented, no changes requested ("Let's go with this!").

## Deferred / spun-off decisions

- **D-079** (mini-game frequency): the founder chose to reopen D-064 rather
  than defer — Tell Me Something True is accelerated into Rehearsal 1
  (AW-288) and a new, not-yet-specified Trivia mini-game is added (AW-289).
  Neither is designed or built by AW-284; both gate AW-286 (Rehearsal 1)
  per D-079.
- **Tuning values** (Tables 1-4 in the design doc) are explicitly Rehearsal-
  1 starting points, not final — same deferred-tuning pattern as AW-287's
  bank-cap values and AW-283's Rattle-the-Witness boost amount.

## Checkpoints

| Checkpoint | Artifact | Approval evidence | Result |
|---|---|---|---|
| Accusation window | This record, decision 1 | Founder selected "From The Grill onward," 2026-07-19 | Approved |
| Wrong-accusation cost direction | This record, decision 2 | Founder: "accusing should have real consequences," 2026-07-19 | Approved |
| Accusation feature set | This record, decision 3; full ideation funnel in conversation history | Founder: "Im down to lock in all 5 with your favorite long term selection as the primary," 2026-07-19 | Approved |
| Beat-scoping and abuse mitigations | This record, decisions 4-5 | Founder answered both via interactive question, 2026-07-19 | Approved |
| Scoring presentation model | This record, decision 6 | Founder selected Option A (Hidden Score, Loud Moments) after a race-track refinement, 2026-07-19 | Approved |
| Product-vision cross-check | This record, decision 8 | Founder: "Flag it as a follow up and make sure it is included before the rehearsal," 2026-07-19 | Approved; spun off to D-079/AW-288/AW-289 |
| Scoring brief, tuning tables, scenarios, endgame walkthroughs | [design doc](../superpowers/specs/2026-07-19-aw284-race-scoring-design.md) | Founder: "Lets go with this!", 2026-07-19 | Approved |
| Implementation plan | *(pending)* | Not yet written | Pending |
| Thin slice | *(pending)* | Not yet implemented | Pending |

## Scope owner actions

- Planning for AW-284 (discovery through the implementation plan) is owned
  by this session; implementation is handed off to a separate execution
  session (Codex) once the plan is written.
- D-079, AW-288, and AW-289 were created during this session as a direct
  result of AW-284 discovery (decision 8) and are committed together with
  AW-284's planning artifacts per the founder's explicit instruction to
  fold them into the same commit.
- AW-284's implementation depends on AW-283's claims module
  (`engine/claims/`, `contradiction_confirmed`/`contradiction_rejected`
  events) which is discovery-complete and plan-ready but not yet executed —
  the implementation plan must sequence against AW-283's real shipped event
  shape once it lands, not just this plan's assumptions about it.
