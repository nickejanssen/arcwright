# The Twist Menu — Beat 4 Authored Families

> Current version: v0.1 DRAFT — not approved content
> Last updated: 2026-07-19
> Status: Draft, awaiting founder review (see 00-direction.md and the
> master plan)
> Canonical path: docs/design/line-libraries/twist-menu.md
> Authority: Couch Race story bible §4 Beat 4 ("a deterministic
> mid-case revelation... The twist never changes whodunit; it reorders
> suspicion"); exemplar pattern: authored menu, generated dressing
> (story-to-arc-exemplar.md Step 2).
> Feeds: AW-281 lineage (case generation) and AW-284's twist-beat gates.

## The Contract

The bible names the twist's law and three examples, and stops. This
menu completes the authored side: **twelve twist families.** Case
generation selects one per case (deterministically, at resolution,
compatible with the resolved truth) and dresses it with case
specifics. The family defines what *kind* of ground shifts; the
dressing defines whose.

Rules every family obeys (from the bible, restated as authoring law):

- Never changes whodunit. Reorders suspicion only.
- Must be *retro-readable*: on reveal, players should see the twist
  was consistent with the truth all along.
- Must punish confident early theories and pay contradiction-miners —
  the beat's authored function.
- Lands as one staged revelation (D-070 sequence), then the second
  evidence wave (Evidence Locker slot) plays in its new light.

## The Twelve Families

Each entry: what shifts · why it's fair · compatibility notes for the
resolver (which case shapes it may attach to).

**T1 — The Collapsed Alibi.** A verified alibi for one non-killer
suspect fails (the witness recants, the timestamp was wrong). *Shifts:*
an "eliminated" suspect re-enters the pool. *Fair because:* the alibi's
flaw is in evidence already released. *Compatibility:* requires a
non-killer suspect the room has confidently cleared — the resolver
should pick the most-cleared suspect at twist time? No — resolved at
session start; the arc *predicts* clearing by making the alibi
prominent in wave 1. *(Design note for engineering: T1 is authored as
"the prominent alibi," not "the popular theory" — determinism holds.)*

**T2 — The Undeclared Relationship.** Two suspects who presented as
strangers are revealed connected (married, siblings, business partners,
ex-lovers). *Shifts:* every corroboration between them becomes
worthless; the room re-audits pairs. *Fair because:* their earlier
statements cross-corroborated a little too neatly (bt-w-5's seam line
foreshadows this family). *Compatibility:* any case with ≥4 suspects.

**T3 — The Second Secret.** A suspect's lie is exposed — and what it
hid is a *different* crime (theft, affair, embezzlement), not the
murder. *Shifts:* the room's best "gotcha" resolves innocent; the
killer's lie is still out there. *Fair because:* it teaches the mixed-
by-suspect texture rule mid-game. *Compatibility:* universal; the
red-herring engine's flagship family.

**T4 — The Victim's Motive.** The victim was doing something that gave
*several* suspects reason (blackmail notes found; a will changed
yesterday; a planned exposure). *Shifts:* motive stops narrowing the
field and widens it. *Fair because:* victim-side evidence was present
but unweighted. *Compatibility:* strongest with money/secret motive
archetypes (pairs with oll-motive-money / oll-motive-secret).

**T5 — The Moved Body.** The location everyone has treated as the
crime scene wasn't. *Shifts:* every location-based alibi re-indexes to
the true scene. *Fair because:* scene evidence carried the
inconsistency from wave 1 (the staging archetype). *Compatibility:*
requires staging in the resolved truth; pairs with oll-staging-scene.

**T6 — The Wrong Time.** The death happened meaningfully earlier or
later than assumed (the scream was staged; the clock was moved).
*Shifts:* the alibi window slides; safe suspects become exposed and
vice versa. *Fair because:* the timing anomaly is checkable against
released timeline evidence. *Compatibility:* timing-archetype cases;
pairs with oll-timing-clock.

**T7 — The Witness Among Us.** One suspect *saw* something and has
been lying about it — not as the killer, but out of fear or loyalty.
The twist releases their partial account. *Shifts:* a new, credible,
incomplete narrative enters; the room must decide how much to trust
it. *Fair because:* their evasiveness was readable as leaky texture
all along. *Compatibility:* requires a leaky or brittle non-killer.

**T8 — The Inheritance Of Suspicion.** Evidence surfaces implicating a
suspect the *victim* suspected of something — the victim's own notes,
half-right. *Shifts:* players inherit the victim's theory, which is
compelling and (per the resolver) partially wrong. *Fair because:* the
victim's error is falsifiable with wave-2 evidence. *Compatibility:*
secret/exposure motives; gives the victim posthumous character.

**T9 — The Locked Door Opens.** Something sealed all game — a room, a
safe, a phone, a diary — opens, releasing a dense cluster of new
evidence at once. *Shifts:* less a redirection than an acceleration;
the room re-prioritizes under load. *Fair because:* pure addition, no
recontextualization debt. *Compatibility:* universal; the lowest-risk
family — resolver's fallback when the case shape fits nothing sharper.

**T10 — The Double Life.** One suspect's *identity* is not what was
presented (a hired impostor, a returned relative under another name,
a professional — investigator, journalist, thief — working the party).
*Shifts:* everything they said re-reads under new intent. *Fair
because:* identity tells were plantable in wave 1 (the wrong
monogram, the practiced answer). *Compatibility:* casts with a
stranger/newcomer role; NOT compatible with T2 in the same case
(two identity quakes flatten each other).

**T11 — The Failed First Attempt.** Evidence of an earlier, failed
attempt on the victim — days ago, differently. *Shifts:* alibis for
tonight stop being sufficient; the room needs suspects' *pattern*, not
their evening. *Fair because:* it rewards players who probed history
in interrogation. *Compatibility:* grudge/ambition motives; requires
interrogation content to have seeded past-tense questions.

**T12 — The Accomplice Fracture.** The killer had help — knowing or
unknowing — and the help is now visibly panicking (a suspect changes
their story unprompted). *Shifts:* two-person theories become viable;
the couch splits productively. *Fair because:* the accomplice's
original statement carried the strain. *Compatibility:* the rarest
family; requires the resolved truth to include an accomplice role,
which is an arc-config dial (default off for v1 — **flag: enabling
T12 is a case-generation scope decision, not a content decision**).

## Vesper's Twist Delivery

The twist lands through the existing beat-turn refrains (bt-j-4 /
bt-g-2 / bt-w-3 families in each wrapper library) — no new mood
needed. The menu adds one requirement: each family carries a
`{{callback}}` recommendation — which released fact the dressing
should bind to Vesper's line, so her "hold that thought — it's about
to move" always points at something the room actually holds.

## Review Notes for the Founder

- T1's design note is the menu's one *engineering-relevant* subtlety:
  families must be resolvable at session start (determinism), so
  "punishing the confident theory" is achieved by authored prominence,
  never by watching the room. Confirm you're comfortable with that
  reading of the bible's intent.
- T12 is authored but gated off pending an accomplice-dial decision.
- Recommended v1 active set if you want to trim: T1–T6 + T9 (seven
  families ≈ every case feels distinct across a month of nightly
  play; T7/T8/T10/T11 join as the case generator matures).
- Each family should eventually carry per-wrapper dressing guidance
  (what a Collapsed Alibi looks like on a space station vs. in a
  manor) — renewable-model work once the founder approves the menu.
