# Truth Sequence Shapes — Discovery Packet (AW-278)

> Current version: v0.1 DRAFT — discovery material, NOT a locked direction
> Last updated: 2026-07-19
> Status: Awaiting founder direction selection (AW-278 creative-collaboration
> contract; stopped at reversible research per human-collaboration rules)
> Canonical path: docs/design/line-libraries/truth-sequence-shapes.md
> Feeds: AW-278 (truth sequence and reveal accounting)
> Wrapper used for samples: Séance 1928

## Fixed (Already Founder-Approved — Not Open For Redesign)

From the-host.md §6.3, the reveal's *voice* structure is locked:

1. **Grave** — Vesper reconstructs the evening, naming what each
   detective *almost* caught.
2. **Delighted** — she names the killer's best move, with warmth.
3. **Ordinary** — the last line. Small. Precise. The screenshot.

From AW-278: AI composes language only; guilt, evidence validity,
scoring, and outcomes are resolved before a single word is generated.
The reveal must make fairness *legible* and must not be scoreboard-only.

## Open: The Sequence Architecture

How the reconstruction unfolds between those three voice movements —
what order the truth comes out in, and where each player's night gets
accounted. Three candidate architectures.

---

## Architecture A — "Rewind" (chronological reconstruction)

The evening replays in order, this time with nothing hidden. Each
staged moment re-fires briefly on the TV (D-070 hints reference the
original sequences) with the lie stripped out. Player accounting is
woven inline: as each deception falls, Vesper names who flagged it —
or who walked past it.

**Sample passage (solved case):**
> Then let the house speak — from the beginning, and honestly this time. At {{time_1}}, the argument by the conservatory: real, and unrelated — Detective Wren said so from the start, and Detective Wren was right. At {{time_2}}, {{suspect_2}}'s locked-door story — a lie, but an innocent one, protecting an affair, not a killer. Detective Rook caught it and, correctly, moved on. And at {{time_3}} — the second glass. Detective Hale asked about the second glass twice. The room laughed. The room, detectives, owes Detective Hale an apology.

**Strengths:** strongest fairness proof (the whole case re-derives in
front of the room); accounting lands where it happened, so credit feels
earned, not tallied.
**Risks:** longest of the three; a 6-suspect case rewound can overrun
Beat 6's 3–5 minute budget; repetitive if the session already surfaced
most of the truth.

## Architecture B — "The Unmasking" (suspect-by-suspect clearing)

Vesper clears the cast one portrait at a time — each innocent suspect's
secret named, their lie explained, their frame re-lit in `--ok` — until
one portrait remains. Player accounting attaches per suspect: whoever
caught that suspect's lie is named as the portrait clears. The killer's
portrait re-rings in `--accuse` for the grave reconstruction.

**Sample passage (mixed-catch case):**
> {{suspect_3}} lied about the telegram — to hide a debt, not a death. Detective Quill caught the lie; the debt survives the evening. Cleared. {{suspect_2}} was in the cellar with someone she is not married to. Nobody caught it. It didn't matter — but it was there to catch, detectives, and the cellar keeps score. Cleared. Which leaves — as it has left, all evening, for those counting portraits — one frame still lit.

**Strengths:** matches the moodboards' showcase-moment staging almost
exactly (portraits stepping forward is already the approved `seq-truth`
visual); naturally paces to cast size; every red herring gets its
fairness receipt.
**Risks:** the killer is inferable by elimination moments before the
naming — the "one frame remains" beat must be treated as intentional
drama, not a leak; weakest chronology (why-it-happened can get thin).

## Architecture C — "The Confession" (killer-voiced reconstruction)

After Vesper's grave opening names the killer outright, the killer
suspect takes the stage one final time and walks the room through the
crime in their own voice — constrained, like all suspect speech, by
knowledge state and resolved truth. Vesper frames and closes; the
accounting arrives as Vesper's rebuttal ("you were seen — Detective
Ivory saw you") woven through the confession.

**Sample passage (solved case):**
> *(Vesper, grave:)* It was {{killer}}. It was always {{killer}}. And because this house believes in finishing its stories properly — {{killer}}, the stage is yours. One last time. *(The killer, lit in oxblood:)* The toast was the only moment the hallway would be empty. I'd rehearsed the walk — eleven steps, no floorboard. What I hadn't rehearsed — *(Vesper:)* — was Detective Ivory, watching the mirror instead of the toast. Detectives always watch the wrong thing. The good ones watch it on purpose.

**Strengths:** the most cinematic and the most differentiated (no
competitor's reveal hands the knife to the killer); showcases the
platform's own suspect-dialogue capability at the emotional peak.
**Risks:** heaviest engineering coupling (a constrained generation call
inside the reveal contract); tone control is hardest — a killer who
plays it for laughs collapses the "takes the death seriously" rule;
unsolved-case variant needs care (a confession nobody earned can feel
like the game solving itself).

---

## The Unsolved Case (all three architectures must handle it)

Required review case per AW-278. Sample close (any architecture):

> No one named {{killer}}. The house notes — without judgment, the house has seen centuries of this — that the truth was on the table four times tonight. {{evidence}} said it. The cellar count said it. Detective Sable *almost* said it, at last call, and chose the safer chair. The race goes to the house tonight, detectives. It usually does. It's the house's favorite ending — and the reason there is always another case.

Rule established by this sample (confirm): an unsolved case is scored
as a *house win*, voiced with relish, never as player failure — the
loss must taste like "one more case," not like a shrug.

## Ordinary Last Lines (seed set, all architectures)

The §6.3 screenshot line. Small, case-specific, authored-shape with
slots. Six seeds:

1. > It was the second glass. Of course it was.
2. > The door was never locked. No one tried it.
3. > {{killer}} said "we" all evening. The dead don't get a "we."
4. > The candles burned down at different speeds. That's all. That was everything.
5. > {{victim}} knew. That's why the toast was early.
6. > Count the gloves again. Slowly, this time.

## Recommendation (advisory only — founder picks)

**B as the spine, with A's inline crediting rule and C held as a
premium variant.** B matches the approved showcase staging, budgets
cleanly, and gives every lie a fairness receipt; A's
credit-where-it-happened principle grafts onto it directly. C is the
most special and the most expensive — recommend prototyping it *after*
Rehearsal 1 as the high-tension-tier reveal (routing already supports
premium gating), not as the launch default.

## Founder Interview Questions (for the AW-278 discovery pass)

1. Which architecture (or blend)? Does B-plus-A's-crediting hold?
2. Elimination drama in B: is "one frame remains" a feature to stage
   hard, or a leak to obscure (e.g., clear the killer's secret mid-pack
   as a misdirect)?
3. Is C's killer-voiced confession wanted at all — launch, post-launch
   premium, or never?
4. Unsolved-case tone: confirm "house win, voiced with relish."
5. Ordinary-last-line authorship: shapes-with-slots (current seeds) or
   fully authored per case archetype?
