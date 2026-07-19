# AW-287 Leverage Representative-Interaction Walkthrough

> Status: For founder review (AW-287 Human Collaboration Contract gate)
> Canonical path: docs/superpowers/specs/2026-07-18-aw287-leverage-walkthrough.md

## What this represents

A session-shaped sequence showing four of the six launch-set Leverage effects
firing in order, plus one danger-combination guardrail actually triggering.
It is a table read, not code — the goal is to catch a wrong sequencing or
visibility decision now, while it costs a paragraph edit, rather than after
the resolution engine is built.

## What it tests

- That the four D-075 decisions (public balances, post-resolution saboteur
  reveal with the Sting Operation exception, cross-beat persistence, per-
  effect visibility) actually produce a coherent moment-to-moment experience
  rather than just sounding right individually.
- That the danger-combination guardrails from the design doc (one offensive
  modifier per interaction; post-target protection window) have a concrete
  trigger condition, not just a stated rule.

## What needs founder attention

The two moments marked **[REVIEW]** below are judgment calls this walkthrough
makes that the design doc didn't fully pin down. Everything else follows
directly from decisions already locked (D-074, D-075, the design doc's
guardrails).

---

## Scenario: Beat 3 (The Dig), Boardroom Severance wrapper, 4 players

Table: **Priya** (12 Leverage banked, won the opening mini-game), **Marcus**
(4 Leverage), **Jordan** (2 Leverage), **Zoe** (7 Leverage, activated Sting
Operation last beat and it's still armed). All four totals are visible to
everyone on the shared display's Leverage readout (public balances, D-075).

**1. Priya spends Deep Read (Insight, 2 Leverage) on her own upcoming
question.**
The TV shows Priya's balance drop from 12 to 10 — a public state change,
since balances are public. What Deep Read actually surfaces (the sharpened
private observation) is delivered only to Priya's phone; the *content* of an
Insight-family advantage is inherently private to its user, same as it would
be with no Leverage system at all. Nothing here is new relative to AW-282/
AW-283's existing public/private answer split — Leverage just adds a spend
event on top.

**2. Marcus spends Rattle the Witness (Witness pressure sabotage, 2
Leverage) targeting Jordan's next question.**
Marcus's balance drops 4 → 2, publicly. Jordan's upcoming question resolves
against a more guarded suspect — the *answer itself* is public (it's a normal
interrogation answer, routed the same as any other), so the whole table
hears the suspect hedge. But per D-075, Marcus's identity as the saboteur is
withheld from Jordan (and the table) until Jordan's interaction finishes
resolving. **[REVIEW]:** this walkthrough assumes "resolves" means the
moment the answer content event is fully delivered, not the moment Jordan's
whole round-turn ends. If a beat has multiple questions queued, does
"resolves" mean per-question or per-round? Recommendation: per-question —
matches the design doc's targeting language ("a rival's next question," not
"a rival's whole turn") and keeps the delay short enough to still feel like
part of the same beat.

**3. Immediately after, Jordan (and only Jordan) learns: "Marcus rattled the
witness before your question."** Per D-075's actual reveal-timing decision,
this is delivered privately to the sabotaged target, not broadcast to the
table — an earlier draft of this walkthrough said "the table learns," which
overstated the decision; the implementation (and the discovery record) both
scope the reveal to the target only.
This becomes Jordan's post-target protection window: per the design doc's
danger-combination limit, Jordan cannot be the target of another
information-control or witness-pressure sabotage until either another player
is targeted, or the next interaction window opens. If Marcus (or anyone)
tried Listen In against Jordan right now, it would be rejected as
ineligible — this is the guardrail actually firing, not just documented.

**4. Zoe activates Sting Operation (Counterplay, 3 Leverage) in
anticipation, before anyone targets her.**
Zoe's balance drops 7 → 4, publicly. Nothing else visible happens yet — Sting
Operation is armed, not resolved.

**5. Priya spends Listen In (Information control sabotage, 2 Leverage)
targeting Zoe's next private observation — but Zoe has Sting Operation
armed.**
Priya's balance drops 10 → 8, publicly. Because Zoe's Sting Operation is
active, two things happen simultaneously per its documented behavior
("weakens the next sabotage and exposes its source"): Priya's Listen In
lands in a weakened form (Zoe's private observation is only partially
copied, not fully), **and** Priya's identity as the source is exposed to Zoe
**immediately** — this is the one case where D-075's "reveal after
resolution" default doesn't apply, because immediate exposure is what Sting
Operation's counterplay payoff *is*. The table does not automatically learn
Priya did this (Sting Operation's exposure is to its target, Zoe, not
table-wide) — **[REVIEW]:** should Sting Operation's exposure be private to
Zoe only, or also broadcast to the table as a bonus "gotcha" moment for
Zoe's smart play? Recommendation: private to Zoe only, matching how sabotage
identity reveals generally work (revealed to the *target*, not the table) —
keeping it table-wide would make Sting Operation strictly better than every
other counterplay option and encourage holding it defensively forever
instead of using Leverage proactively.

**6. Beat 3 ends. Beat 4 (The Thread) begins.**
Priya (8), Marcus (2), Jordan (2), Zoe (4) — all balances persist unchanged
into the new beat (cross-beat persistence, D-075). No reset event fires.

---

## Guardrails this walkthrough exercised

- One offensive modifier per interaction: not triggered here (no interaction
  received two offensive effects at once) — confirmed as a gap the
  implementation tests must cover separately, since this walkthrough only
  shows the *targeting-eligibility* guardrail (step 3), not the
  *stacking* guardrail.
- Post-target protection window: triggered and shown (step 3).
- Bank cap: not triggered (no balance approached the cap) — flagging that
  the cap's actual number is still undefined and belongs in the
  implementation plan (Task 15), not this walkthrough.
