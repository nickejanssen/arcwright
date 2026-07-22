# Writing For Living Stories — The Author's Craft Guide

> Current version: v0.1 DRAFT — founder-directed platform discovery (D-082)
> Last updated: 2026-07-19
> Status: Draft, awaiting founder review. Not build scope.
> Canonical path: docs/design/authoring/writing-for-living-stories.md
> Companion: `story-to-arc-exemplar.md` (shows WHAT an author produces;
> this guide teaches HOW to write each piece well)
> Audience: arc authors — internal first, third-party later. This is
> craft, not schema; the platform's technical authoring reference is
> separate and engineering-owned.

A story on this platform is performed by a machine that will never
improvise outside your rules — which means your rules are the writing.
This guide is the craft of writing things that stay excellent when a
runtime finishes them ten thousand different ways.

---

## 1. Write Shapes, Not Lines

The platform's first discipline: authored refrains, generated
specifics. You write a line's *shape* — rhythm, turn, emotional
mechanics — with slots for what varies. The craft test for any shape:

**A shape is good when it cannot be filled badly.**

Weak shape (the slot carries the drama):
> ~~"Suddenly, {{suspect}} did something shocking!"~~

The generator now owns "shocking." You've delegated the actual writing
to runtime — the one thing this platform exists to prevent.

Strong shape (the structure carries the drama; the slot is furniture):
> "{{suspect}} has refreshed their {{drink}} three times since the body was found. Grief takes many forms. So does arithmetic."

Fill it with any drink in any decade — the line lands identically,
because the *turn* ("so does arithmetic") is yours and untouchable.

**Craft rules for shapes:**

- Slots hold nouns, names, numbers, and times. Never verbs of
  consequence, never judgments, never emotion words.
- The last clause is always yours. Endings are where lines land;
  no slot goes after the turn.
- Write each shape's *worst plausible fill* before accepting it. If a
  ridiculous-but-valid fill breaks the line, the shape is leaking.

## 2. Write One Voice That Can Do Two Things

A performed narrator reads hundreds of lines a night. A voice with one
register becomes wallpaper by the third scene. The craft rule, proven
across every library this platform has: **every voice needs a default
and a counter-register, and every important line should be able to
move between them.**

Give the voice a *signature move* — a repeatable emotional mechanic
(a warm line that turns cold on the final clause; a formal line that
cracks once and reseals). Then budget it. A shift on every line is a
tic; a shift at each beat's hinge is a spine.

Practical discipline: for each line, declare what mood it can shift
*into* on delivery. If most of your library shifts nowhere, the voice
is flat. If everything shifts, nothing does.

## 3. Write People, Not Prompts

The platform's character sheet is identity, personality, goals,
knowledge, relationships. The craft failure to avoid: writing
*instructions to an AI* instead of *a person*.

Prompt-shaped (weak):
> ~~"Act evasive when asked about the vault. Be charming but suspicious."~~

Person-shaped (strong):
> "Proud, not stupid. Treats the system's decommissioning as a personal insult. Warms to anyone who respects the craft; cools fast on flattery."

The difference is testable: a person-shaped sheet can be *performed
wrongly* — you can read a generated line and say "she would never say
that." A prompt-shaped sheet can't be wrong, which means it can't be
right, which means you haven't written a character.

**The knowledge line is the character.** What this person knows, when
they learned it, and from whom is enforced by the platform before they
speak a word. So write knowledge the way you'd write backstory —
because on this platform, they are the same thing, and unlike
backstory, knowledge *cannot be contradicted at runtime*. It is the
one part of your character the performance can never betray.

## 4. Write Prohibitions Like Content

Rails — what generation may never do — read like boilerplate and play
like plot. "The complication may change the route, never the goal" is
not a safety note; it is the difference between a heist story and
chaos. Craft rules:

- **Rails protect meaning, not just safety.** "Marsh is never the
  villain" is a story decision wearing a rail's clothes. Your best
  rails will be the ones a lawyer wouldn't think of.
- **Every rail should be falsifiable in review.** "Keep it tasteful"
  is not a rail. "The comedy is in the specificity of the awfulness,
  never in the death itself" — that, a reviewer can check line by line.
- **Write the failure example next to the rule.** A named
  counterexample (~~struck through~~, visibly wrong) teaches faster
  than three paragraphs of principle. Every section of this guide
  does it. So should your arc bible.

## 5. Design the Variation, Don't Permit It

"This element is generative" is not a design. The craft is choosing
*axes* of variation and *anchors* of constancy, per element:

- An anchor is what makes session one and session one thousand
  recognizably the same story. (The six beats. The narrator. The
  fairness promise.)
- An axis is where sessions must never repeat. (The cast. The
  geography. What breaks.)

The test: describe your experience in one sentence that is true of
every possible session. Everything in that sentence is an anchor and
must be authored. Everything you had to leave out of the sentence is
an axis — and for each axis, you owe the generator a *menu or a rail*,
never a shrug.

## 6. Fairness Is A Writing Problem

Deterministic resolution makes fairness *possible*; only writing makes
it *felt*. The craft obligations:

- **Every false signal must be falsifiable** — by evidence that exists,
  in the session, before the accusation. Write the refutation when you
  write the lie. If you can't, the lie is not authorized.
- **The truth must be reachable by the dumbest sufficient path.** Not
  the *likely* path — the sufficient one. Chart it explicitly during
  authoring: which released facts, in which order, force the
  conclusion.
- **Account for the audience at the end.** Whatever your genre's
  ending is, it must pay the player's attention back: name what they
  caught, name what they nearly caught. An ending that only announces
  the outcome treats the performance as the product. The *player's
  week* is the product.

## 7. The Ordinary Line

One craft pattern worth stealing regardless of genre: end on the
smallest true thing. After the reveal, after the accounting, the last
authored line should name an ordinary object the whole story now
lives inside — under twelve words, no flourish, no emotion words.

> It was the second glass. Of course it was.
> The door was never locked. No one tried it.

If your ending needs a paragraph, the story hasn't finished — it's
still explaining. The ordinary line is how you know the structure did
its work: one small sentence, and the room fills in everything.

---

## The Author's Checklist

Before an arc goes to validation:

1. Every shape survives its worst plausible fill.
2. The voice has a default, a counter-register, and a budgeted
   signature move.
3. Every character sheet can be performed *wrongly*.
4. Every rail is falsifiable; every rule has a failure example.
5. One sentence true of every session; every axis has a menu or rail.
6. Every lie ships with its refutation; the sufficient path is
   charted.
7. The ending accounts for the audience.
8. The last line is ordinary.

## Review Notes for the Founder

- This guide generalizes craft rules proven in tonight's Nightcap
  libraries into platform-neutral form — it cites no game by name in
  its body on purpose (authors should receive it clean).
- If approved as a direction, its successors are engineering-owned:
  the technical authoring reference (schemas, validation) and
  eventually authoring tooling that *enforces* the checklist
  (e.g., worst-fill preview, shift-budget linting, sufficient-path
  charting). Those tool ideas are the "make it easy" pillar's
  product surface — worth their own discovery pass on a renewable
  model.
