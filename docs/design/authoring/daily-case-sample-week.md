# Daily Case — Sample Week (Creative Proof)

> Current version: v0.1 DRAFT — founder-directed platform discovery (D-082)
> Last updated: 2026-07-19
> Status: Draft, awaiting founder review. Not build scope.
> Canonical path: docs/design/authoring/daily-case-sample-week.md
> Authority: `docs/story-bibles/daily-case.md`
> Purpose: one complete authored sample case demonstrating the second
> product's feel — solo, five minutes a day, one suspect who remembers.
> Proves the D-034 wedge creatively the way the exemplar proves the
> authoring surface.

## Differentiation Statement (the Murdle question, answered)

Daily deduction puzzles (Murdle et al.) are stateless logic grids:
today's puzzle forgets you at midnight. Daily Case is the opposite
primitive made playable: **a suspect with memory.** No grid, no
elimination matrix. The game is a week-long cross-examination where
the antagonist is one person's story, and the win condition is
catching where that story bends. The mechanic is provenance, not
logic — nothing on the market does it because nothing on the market
*keeps* knowledge state.

## The Sample Case — "The Locked Studio"

**Authored truth (resolved before day one, immutable):** Sculptor
Mira Voss was found dead in her locked studio Sunday night. The
suspect, **Julian Ashe** — her gallerist, oldest friend, and executor
— did not kill her. He believes he did. He rearranged the scene in a
panic to hide what he thinks is his fault, and he is lying to protect
that belief. The actual death was an accident Mira staged to look
deliberate — her last artwork, aimed at the art world that discarded
her. The player's job across the week is not "prove Julian guilty."
It is to interrogate a lying, grieving, innocent man until the truth
underneath his lies stops fitting a murder at all.

*(Design intent: the twist-genre inversion — the suspect's lies are
real, his guilt is real, his crime isn't — showcases that this engine
does character interiority, not gotcha grids. Also a fairness rail:
the case is solvable as "not murder" from accumulated contradictions
alone.)*

## The Handler Voice

Vesper is portable to Daily Case (the-host.md §9). Proposed register
here: **the case handler** — text-first, terse, letterhead-dry, warm
only in the last line of each day. The Boardroom-adjacent register at
telegram length. One founder decision: Vesper-as-handler, or a new
voice for the solo product line. Samples below assume Vesper.

**Day-open re-entry frame (shape, slots per platform discipline):**
> Case {{case_no}}, day {{day}}. Ashe is available. Yesterday he gave you {{claim_count}} claims; {{flag_count}} are flagged. He has had a night to think. So have you.

**Day-close (shape):**
> That's the day. He said one thing today that will matter more tomorrow. Sleep on which.

## The Week

Each day: re-entry frame → bounded questions (budget: 5) → suspect
answers from knowledge state + claim ledger → day-close hook. Below,
each day's authored function plus a sample exchange showing the
memory mechanic at work.

**Day 1 — The Statement.** Function: Julian's full account, laid
clean. Every lie he'll spend the week defending gets said today.
> **Player:** Where were you Sunday night?
> **Julian:** Home. I'd left the gallery at six — Mira wanted the studio to herself on Sundays, everyone knew that. I heard Monday morning, like everyone else.
> *(Ledger: claim J-3, "left at six, home all night." Flag: none — yet.)*

**Day 2 — The Timeline.** Function: fix his account against the
physical facts released today (the studio's door log, the rain).
> **Player:** The door log shows a keyholder entry at 9:40 Sunday night.
> **Julian:** Then it's wrong, or it was Mira re-keying it — she did that when she was in a mood. I told you. I was home by seven.
> *(Ledger: J-3 now contradicts E-2. Julian's denial is claim J-9. The player watches the ledger grow — the game's core image.)*

**Day 3 — The Relationship.** Function: open the grief. Julian talks
about Mira; his warmth is real and his tenses slip.
> **Julian:** She was — she *is* — the only artist I ever represented who didn't need me. You don't recover from being unnecessary to someone you love. You just bill them less.
> *(No new flags. Day 3 is authored as the trust day: the player
> should end it less sure he did it. The contradiction engine rests;
> the character engine carries.)*

**Day 4 — The Crack.** Function: confront J-3 vs E-2 directly.
Julian's texture is brittle (per the platform's per-suspect trait):
he holds, degrades on the second press, concedes on the third.
> **Julian:** *(third press)* Fine. I went back. 9:40, like your log says. She'd called me at nine — furious, incoherent, worse than I'd ever heard her. When I got there she wouldn't open the door. I still had my key. I didn't use it. I stood in the rain like a coward and went home. That's the truth. That's the *only* thing I've lied about.
> *(Ledger: J-3 superseded by J-15. "That's the only thing I've lied
> about" is claim J-16 — and tomorrow it breaks.)*

**Day 5 — The Scene.** Function: the staging evidence lands (the
moved pedestal, the wiped floor). J-16 collapses; Julian's real
secret — he entered after she was dead and rearranged everything —
comes out under the weight of his *own accumulated claims*.
> **Julian:** You don't understand what it looked like. What she'd *built*. I couldn't let them see her like — like an exhibit. So yes. I moved things. I made it look like a break-in. I did that. Whatever else you decide about me, that part I did.
> *(Day 5 is the product's proof moment: nothing todays says was
> extractable on day 1. The confession is priced in six days of his
> own words. Memory IS the gameplay.)*

**Day 6 — The Question Under The Question.** Function: with Julian's
lies spent, the remaining contradictions no longer point at him — the
9pm call, the staged studio, the door locked *from inside* after his
9:40 visit. The authored design guarantees the day-6 state: every
live contradiction now fits only one story, and it isn't his.
> **Julian:** Ask me anything. I've got nothing left to protect. — No. That's not true. One thing. Ask me why she called *me*, of all people, at nine o'clock. I've been avoiding that one myself.

**Day 7 — The Accusation.** The player files: murder (name Julian),
or the truth (no murder — name the staging, cite the claims). The
reveal accounts every flag: which contradictions were Julian's guilt,
which were Mira's design, and which the player caught versus walked
past. Handler close, either outcome, Vesper's costume fully off:
> The file is closed. He'll get your findings in the morning. For what it's worth — and in this office that phrase means a great deal — you asked the one on day {{day_ref}} that nobody asks. That's the whole job. Case {{next_case_no}} opens tomorrow.

## What This Proves (platform ledger)

- **Cross-session memory as core loop** — D-034's wedge, felt in
  play by day 2, decisive by day 5.
- **Same interrogation capability as the party product** — claims,
  flags, contradiction detection, per-suspect lie texture — zero new
  primitives, one new surface shape.
- **Authored spine, generated performance** — the week structure,
  truth, and day functions are authored; Julian's language is runtime;
  his facts never are.
- **Five-minute solo sessions** — the day shapes above each fit a
  question budget of five.

## Review Notes for the Founder

- The genre inversion (guilty-feeling innocent, victim as author of
  the scene) is the taste probe: if this is the right *kind* of story
  for the daily product, the platform's solo lane is character drama,
  not puzzle-adjacent. If you want it closer to classic whodunit,
  say so — the memory mechanic works either way.
- Vesper-as-handler vs. a new solo-product voice: open decision.
- Day 3 (the no-mechanics trust day) is a pacing bet — a day that's
  pure character. Confirm you want authored "rest days" in the
  week shape.
- Next steps if direction approved (renewable-model work): M5-C
  schema-validation pass against this sample, then the week shape as
  a real ArcDefinition.
