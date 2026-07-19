# AW-283 Answer/Lie/Contradiction Sample Review

> Status: For founder review (AW-283 Human Collaboration Contract gate)
> Canonical path: docs/superpowers/specs/2026-07-19-aw283-answer-generation-design.md

## What this represents

Representative samples of the four content types AW-283 generates or
detects, grounded in AW-281's real, already-shipped schema
(`engine/case/models.py`: `EvidenceEntry`, `AuthorizedFalsehood`,
`ResolvedCase`) rather than invented from scratch. AW-283's actual job is
narrower than "write dialogue" — it renders pre-resolved facts and
pre-resolved lies in character voice, and checks flags against pre-resolved
contradiction links. AW-281 already proved every `AuthorizedFalsehood` is
falsifiable (`engine/case/invariants.py`); AW-283 does not re-derive that,
it consumes it.

## What it tests

- That naturalistic, wrapper-specific tone (the confirmed brief) actually
  reads as intended against real schema fields, not just in the abstract.
- **A genuine open fork the discovery record didn't fully pin down**: does a
  confirmed catch require the flagging player to have actually been
  delivered the contradicting evidence, or does any correct flag on an
  `AuthorizedFalsehood` count regardless of what the player has seen?

## What needs founder attention

One flagged **[REVIEW]** item below (the evidence-possession question) — the
rest follows directly from the confirmed brief and AW-281's existing schema.

---

## 1. Truthful answers (from `KnownFactContext`)

**Sample A — High Society wrapper, Séance 1928.** Suspect: Eleanor Voss
(the deceased's business partner). Question: "Where were you when the
lights went out?" Known fact: she was in the study reviewing contracts.

> "The study. I'd stepped away from the séance the moment Marguerite started
> her theatrics — someone has to keep the actual business of the evening
> running while everyone else is holding hands in the dark."

**Sample B — Corporate wrapper, Boardroom Severance.** Suspect: the Chief of
Staff. Question: "Did you speak with him before the meeting?"

> "Briefly. Two minutes, maybe less. He wanted to move the agenda item on
> the Kestrel account up. I told him it could wait."

**Sample C — Sci-Fi wrapper, Orbital Gala 2087.** Suspect: the station's
concierge AI liaison (human-played). Question: "What was his mood?"

> "Elevated. He'd had two of the synth-champagne flights and was telling
> everyone within range about the docking contract. Ship's crew found it
> tedious. I found it survivable."

Same underlying generation path for all three: known fact → naturalistic
rendering, tone shaped by wrapper register per the confirmed brief. No new
mechanism beyond what spec 0071 (live-loop AI dialogue) already does for
`KnownFactContext` — AW-283 doesn't invent a new fact-rendering pipeline for
truths, only for lies (below).

---

## 2. Authorized lies (from `AuthorizedFalsehood`)

**Sample D.** `AuthorizedFalsehood(falsehood_id="lie.location.marcus",
speaker_id="marcus", topic="location", claim_text="I was on the terrace the
whole time, getting air", contradicted_by=["evidence.coat_check_ticket"])`.

Rendered in character voice with the confirmed subtle tell (slightly less
specific than his other answers):

> "The terrace. Just — getting some air, mostly. I couldn't tell you exactly
> how long."

The tell: "mostly," "couldn't tell you exactly" — a small hedge, per the
confirmed brief's "subtle delivery tell... never a substitute for the
deterministic check." The ground truth (`contradicted_by`) stays in the
knowledge graph; nothing in this rendering exposes that it's a lie.

**Sample E.** `AuthorizedFalsehood(falsehood_id="lie.relationship.priya",
speaker_id="priya", topic="relationship", claim_text="We were never more
than colleagues", contradicted_by=["evidence.love_letter",
"evidence.hotel_receipt"])`.

> "Colleagues. That's — that's all it ever was, professionally."

The repetition ("that's — that's") is the tell; the content itself is a
clean, confident denial, matching "truths and lies share the same register."

---

## 3. Contradiction cases

**Sample F — confirmed catch.** A player flags Marcus's terrace claim
(Sample D). The engine checks: does `marcus`'s claim match an
`AuthorizedFalsehood`? Yes (`lie.location.marcus`). Per the Technical Scope
("engine checks claim-versus-claim and claim-versus-evidence"), the flag
resolves against `contradicted_by`. **[REVIEW — see below]**: does this
require the flagging player to hold `evidence.coat_check_ticket`, or does
matching the `AuthorizedFalsehood` alone confirm it?

**Sample G — false-positive guard.** A player flags Eleanor's study claim
(Sample A) — a `KnownFactContext`-sourced truthful statement, not an
`AuthorizedFalsehood`. The engine finds no matching falsehood record for
that claim; the flag rejects deterministically. No AI judgment call — the
absence of a record IS the answer, matching the Must Not Do ("do not use a
model call to judge whether a contradiction is real").

---

## 4. Fairness edge cases

**Sample H — technically-true-but-incomplete answer.** Suspect answers "I
was near the terrace" when the fuller truth is "I was on the terrace with
the victim." This is NOT an `AuthorizedFalsehood` (AW-281 didn't author a
lie here) — it's an under-specific truth. A player who flags it gets the
false-positive rejection (Sample G's mechanic), which may feel
counterintuitive ("that was obviously evasive!") even though it's correct
per the deterministic contract. This is a content-authoring concern for
AW-281's case generation (are under-specific-but-true answers common
enough to feel like a design gap?), not something AW-283 can fix by
changing the catch mechanic — flagging it here as a cross-task note, not an
AW-283 acceptance criterion.

**Sample I — evidence not yet delivered.** A player flags Priya's
relationship claim (Sample E) before either `evidence.love_letter` or
`evidence.hotel_receipt` has been delivered to anyone at the table (early
beat, evidence not yet released). If the catch mechanic is evidence-
possession-gated **[REVIEW below]**, this flag should reject — not because
the claim isn't a lie, but because the case for it hasn't been made
available yet. This is the concrete scenario the REVIEW question below
turns on.

---

## [REVIEW] Does a confirmed catch require the flagging player to hold the contradicting evidence?

Two options:

**Option A — match-only.** A flag confirms as soon as the claim matches an
`AuthorizedFalsehood`, regardless of what evidence the flagging player has
been delivered. Simpler to implement (one lookup). Risk: a player who
flags everything (or gets lucky) can catch a lie with zero evidence in
hand — this doesn't match the confirmed success bar ("a confirmed catch
should be traceable to a specific piece of evidence... so it reads as
earned rather than a lucky guess").

**Option B — possession-gated (recommended).** A flag confirms only if the
claim matches an `AuthorizedFalsehood` AND at least one of its
`contradicted_by` evidence entries has already been delivered to the
flagging player (checked via `ResolvedCase.visible_evidence_for` /
per-player delivery tracking, which AW-281/AW-282 already maintain — no new
state needed). This directly implements "catching a lie is a provenance
query" (spec 0072's headline framing) and the confirmed success bar. A flag
on a real lie before its evidence is out rejects the same way a flag on a
truth does (Sample I) — same failure mode, same player-facing message,
different underlying reason (internal only, never exposed pre-reveal per
Must Not Do).
