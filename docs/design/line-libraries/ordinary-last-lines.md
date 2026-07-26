# The Ordinary Last Lines — Seed Library

> Current version: v0.1 DRAFT — not approved content
> Last updated: 2026-07-19
> Status: Draft, awaiting founder review (see 00-direction.md)
> Canonical path: docs/design/line-libraries/ordinary-last-lines.md
> Authority: `docs/design/the-host.md` §6.3 — "the last line. Small.
> Precise. Read a hundred times, still lands. This is the game's
> screenshot."
> Feeds: AW-278 (truth sequence); expands the 6-seed set in
> `truth-sequence-shapes.md`

## The Discipline

The ordinary last line is the held final frame of every session — the
line the couch photographs. Rules derived from the approved seeds:

1. **Under twelve words** wherever possible. Never over sixteen.
2. **Names an ordinary object or act** — a glass, a door, a toast, a
   count. Never the murder, never the emotion.
3. **The room already knows why it lands.** The line explains nothing;
   it *confirms* everything. If it needs context, it fails.
4. **Present- or past-plain tense. No flourish.** The drama is over;
   this is the receipt.
5. Slots are permitted but the *shape* carries the weight — a slot
   fills a noun, never the turn.

Selection is deterministic: each line is keyed to a case-archetype tag
resolved at case generation (the method/motive/flaw family), so the
line always lands on the detail the reveal just proved.

## The Library (24)

Keyed by archetype tag. Wrapper-neutral by design — the ordinary line
is the one moment Vesper drops the costume.

### Method archetypes

**oll-poison-vessel** *(poison in a shared drink)*
> It was the second glass. Of course it was.

**oll-poison-order** *(poison; timing of service)*
> {{victim}} was served first. Just that once.

**oll-timing-toast** *(crime staged during a group moment)*
> Everyone watched the toast. That was the point of the toast.

**oll-access-door** *(access; the unforced entry)*
> The door was never locked. No one tried it.

**oll-access-key** *(access; the copied or borrowed key)*
> Two keys. The house only ever issued one.

**oll-staging-scene** *(scene arranged post-mortem)*
> The room was tidy. Rooms are never tidy.

**oll-weapon-ordinary** *(weapon hidden in plain sight)*
> It went back on the shelf. It's still there.

**oll-timing-clock** *(alibi built on a moved clock or log)*
> The clock was right twice today. Eleven wasn't one of them.

### Motive archetypes

**oll-motive-money** *(inheritance, debt, insurance)*
> The will was dated Tuesday. The invitations went out Wednesday.

**oll-motive-secret** *(silencing what the victim knew)*
> {{victim}} knew. That's why the toast was early.

**oll-motive-love** *(jealousy, affair, refusal)*
> Two coats on one hook. All evening. Nobody's.

**oll-motive-grudge** *(the old wound)*
> Eleven years. They counted. That was the mistake — the counting.

**oll-motive-ambition** *(succession, position, the seat)*
> Someone took the good chair before the body was cold. Look who.

### Flaw archetypes (how the killer was caught)

**oll-flaw-word** *(the pronoun/tense slip in the ledger)*
> {{killer}} said "we" all evening. The dead don't get a "we."

**oll-flaw-count** *(the arithmetic that didn't reconcile)*
> Count the gloves again. Slowly, this time.

**oll-flaw-knowledge** *(knew a detail nobody was told)*
> Nobody mentioned the cellar. {{killer}} gave directions to it.

**oll-flaw-effort** *(the alibi maintained too well)*
> An honest evening has gaps. Theirs didn't. That was the tell.

**oll-flaw-return** *(returned to the scene)*
> The candle was relit. Corpses don't need light.

**oll-flaw-kindness** *(the incriminating considerate act)*
> Someone brought {{victim}}'s coat in from the rain. The rain started after.

**oll-flaw-silence** *(never asked the question everyone asks)*
> Everyone asked who. One person asked how much we knew.

### Unsolved-case closers (house win — voiced with relish)

**oll-unsolved-table**
> The truth was on the table twice. The table kept it.

**oll-unsolved-patience**
> The house can wait. The house is very good at waiting.

**oll-unsolved-next**
> Wrong name, right question. Bring the question back tomorrow.

**oll-unsolved-almost**
> {{detective}} was one door away. The door will remember.

## Review Notes for the Founder

- Archetype keying is the engineering contract: case generation
  already resolves method/motive/flaw families deterministically, so
  the reveal contract selects `oll-*` by tag. If current case schema
  lacks an archetype tag, that's a small AW-278 addition — flag it in
  that discovery pass.
- These are deliberately wrapper-neutral (rule: the costume drops for
  the last frame). If you'd rather the last line stay in-wrapper, each
  needs a per-wrapper render like the superlatives — say the word.
- Probes: **oll-flaw-kindness** (the rain) and **oll-unsolved-almost**
  (the door will remember) lean poetic — the edge of "ordinary." If
  either is too much, the ceiling is **oll-motive-love** (two coats).
