# Interrogation Experience — Founder Discovery Memo

> Current version: v0.2 — founder interview held 2026-07-21; partially
> resolved (see Resolution below)
> Last updated: 2026-07-21
> Status: Founder discovery interview complete (2026-07-21). Three items
> locked, two held for a design examination + paper test. This memo does
> NOT change AW-282's or AW-283's shipped behaviour. Resolution recorded
> here and in the decisions log (D-090, D-091); the examination lives in
> `couch-race-competition-model.md`; the validating test in
> `interrogation-paper-test.md`.

## Resolution (2026-07-21 founder interview)

**Locked:**
- **Presentation is a hard gate (D-090).** The interrogation mechanic
  lives or dies on the suspect's *catch/squirm* landing as a
  high-quality audiovisual performance (D-070). This is core scope, not
  polish — a non-negotiable acceptance criterion for AW-285 and the
  interrogation experience, tested in Rehearsal 1.
- **G2 (quote suspects): prove in the paper test, then build (D-091).**
  Highest-differentiation mechanic; validated on paper first, then a
  first-class build (AW-292).
- **G5 (room reasons to watch): adopt now** via staging (D-091);
  **G3 (asking as public performance): adopt** under the co-opetition
  model. Both AW-285 staging requirements.

**Held for examination + paper test:**
- **The competition model** — the founder surfaced that a shared TV +
  public answers + identical menus has no obvious PvP edge. Examined in
  `couch-race-competition-model.md` (recommendation: co-opetition);
  decided after the paper test.
- **G1 (strategy verbs vs data queries)** — held; both menus tested in
  the paper test under the chosen model.
- **G4 (productive conflict verbs)** — prototyped in the paper test,
  designed post-rehearsal (tied to the D-077 tie-break minigame).

**The viability verdict:** interrogating non-real suspects is a proven,
beloved genre (Her Story, LA Noire, Ace Attorney, Obra Dinn) — the loop
works IF the catch (not the ask) is the payoff AND the squirm clears the
audiovisual bar. Couch Race's differentiator over all of them: infinite
generated cases, social couch play, and knowledge-state-constrained
suspects (systemic, not scripted, contradictions).

---

### Original memo (2026-07-20) follows unchanged for provenance.
> Canonical path: docs/design/authoring/interrogation-experience-review.md
> Authority: `docs/story-bibles/nightcap-couch-race.md` §6;
> `engine/interactions/README.md` (shipped AW-282)

## The Founder's Question

Nightcap's original format had players interrogating *each other* —
social deduction, one player secretly the killer. ADR-0013/D-071 made
Couch Race the v1 target: the killer is always an AI suspect and
players are all investigators. The question raised: **does
interrogating AI suspects translate into world-class, addictive
gameplay — and what are we not considering?**

## What Is Already Built (verified, not assumed)

`engine/interactions/` shipped under AW-282 (PR #248) and is
platform-neutral:

- `InteractionDefinition` — an **authored** option catalog.
- `InteractionOption` — an authored player-facing choice, optionally
  gated by evidence held.
- Menus are deterministic and **never model-generated**.
- Resolution produces public answer groups plus private feedback to
  the asker.
- `InteractionTarget` accepts "character, object, location, **or other
  game entity**."

AW-283 (PR #256) composes answers and contradiction metadata within
knowledge-state and routing boundaries.

**Consequence: the concerns below are content and authoring problems,
not architecture problems.** The option catalog is authored data. This
is the cheapest possible place for a design change to land.

## The Risk, Named

**Interrogation degrades into a database query wearing a costume.**
Select menu item → receive answer → cross-check notes. That loop is
*work*, not play, and no amount of narrator voice rescues it.

## The Structural Insight

Across the medium's best mystery games — Ace Attorney, LA Noire,
Return of the Obra Dinn — **asking is not the pleasure; catching is.**
Asking is setup, catching is payoff. LA Noire's interrogation
selection was its most criticised element while its
doubt/lie confrontations were its most loved.

**Design imperative:** minimise the cost of asking; maximise the
frequency, legibility, and drama of catching.

## The Reframe

The AI suspect is **not the opponent**. The opponents are the other
players (the race); the shared enemy is the case. The AI suspect is
the **conversation piece** — the shared object the couch argues about
out loud. This relocation of the social layer is sound, and it sets
the real bar: **suspects must be worth talking about.** That is a
writing standard, not an engineering one.

## Five Gaps (the "what are we not thinking about" list)

**G1 — Intents are queries; they should be strategies.**
"Where were you at nine?" is a database field. "Rattle them" / "Play
nice and let them run their mouth" / "Press the timeline" / "Bring up
someone else and watch their face" is poker. Authored options should
be **verbs of approach**, not fields of data. The suspect's
lie-texture trait (D-081 decision 3: smooth / brittle / leaky) then
becomes a *strategic read* rather than flavour. **Cost: content only.**

**G2 — Quoting suspects to each other (candidate killer mechanic).**
*"Julian says you were in the study."* Mechanically: transfer a
recorded claim from suspect A into suspect B's interrogation, and let
B's knowledge state react. This is the strongest available
demonstration of the platform's headline primitive, it is the classic
detective-fiction move, and `InteractionTarget` already accepts
entities beyond characters — so a claim may be targetable without an
architectural change. **Needs: AW-283-adjacent scoping. Highest
value-per-effort item on this list.**

**G3 — Asking as public performance.**
The room watches whose question got asked and what it bought. Bad
questions are publicly bad; brilliant ones earn table credit. This
recovers social stakes *without* social deduction, and needs no new
mechanic — only staging (D-070 hints) that credits the asker on the
shared display.

**G4 — No productive disagreement mechanism.**
Players race in parallel; nothing lets the couch productively
conflict (redirect, challenge, second, or piggyback on another
player's line). Related to the deferred tie-break minigame (D-077,
issue #254). Worth considering alongside it.

**G5 — Suspects react to the asker, not the room.**
The bible gives the asker a private tell. Nothing yet gives the
*room* a reason to lean in during someone else's question. Staging
opportunity, not a new system.

## The Cheap De-Risk (recommended before Rehearsal 1)

This question is answerable **in about thirty minutes on paper**: one
person reads Vesper and the suspects from a printed script, two to
four people on a couch, no engine, no build. A targeted table test of
the interrogation loop only.

M0 (Wizard-of-Oz) was overridden as a *milestone* by founder decision
(May 2026); this is not a proposal to reinstate it. It is a proposal
to use the technique once, narrowly, on the single highest-risk
untested assumption in the product — because discovering "asking is
boring" during Rehearsal 1 costs a rehearsal, and discovering it on
paper costs an evening.

## Honest Framing Of The Format Change

The Imposter Variant (human killer) remains documented and approved.
Couch Race does not replace social-deduction pleasure; it occupies a
different lane with different, real advantages (no role burden, a
two-player floor, no eliminated players, infinite cases). **The danger
is expecting Couch Race to deliver the imposter format's joy.** It
must earn its own, and the catch-moment is where it earns it.

## Explicitly Not Decided Here

Nothing. No direction is locked, no scope is added, no shipped
behaviour changes. G1–G5 are candidates for a founder-led AW-282 /
AW-283 follow-up discovery cycle.
