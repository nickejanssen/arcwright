# Suspect Liar-Texture Voice Samples — Discovery Material

> Current version: v0.1 DRAFT — discovery material, NOT locked content
> Last updated: 2026-07-19
> Status: Calibration samples for the mixed-by-suspect trait locked in
> D-081 (decision 3). Feeds the AW-283-adjacent schema question and the
> suspect-generation prompt direction. Not runtime content.
> Canonical path: docs/design/line-libraries/liar-texture-samples.md
> Wrapper used: Séance 1928

## The Trait Being Calibrated

D-081 decision 3: lie texture is per-suspect. Some suspects lie
smoothly; some crack visibly. Set deterministically at case resolution,
like every other case truth. Suspect dialogue generation (spec 0071
lineage) receives the trait and renders answers accordingly — the
*content* of the lie is still resolved case truth; the texture governs
only its *delivery*.

Proposed trait values (schema home TBD by engineering):

- `smooth` — the lie is indistinguishable from truth in delivery.
  Catchable only by cross-reference. The dangerous ones.
- `brittle` — composed until pressed; degrades on the second ask.
  Catchable by persistence.
- `leaky` — visible discomfort from the first word: over-explaining,
  volunteered detail, deflection. Catchable by attention.

Balance intuition for a 5-suspect cast (founder to confirm): killer
drawn from `smooth` or `brittle`, never guaranteed either (or `leaky`
becomes an exoneration tell); at most one `leaky` non-killer, or the
room stops cross-referencing and starts vibe-hunting.

## The Control Question

Same suspect (Edith Harrow, cellist, hiding that she was in the
conservatory retrieving a pawned brooch — innocent secret, authorized
lie about her whereabouts). Same question: *"Where were you at eleven?"*
Only the texture changes.

### smooth

> "The music room. I'd promised the Ashfords a little Debussy before midnight, and a cellist doesn't wander far from her instrument at a party — someone always wants a song. Ask anyone who was near the stairs."

*Why it works:* specific, relaxed, ends by inviting verification —
the confidence of someone who has priced the risk. The flaw is in the
world, not the delivery: nobody near the stairs heard a cello. Catching
her REQUIRES the cross-reference. Nothing in the text leaks.

### brittle

> "The music room. I was — the music room, as I said. I'd promised the Ashfords some Debussy." *(pressed, second ask:)* "I don't see why the couch keeps returning to this. Elevens. Debussy. The music room. If you must know, I stepped out once — for air — briefly — and I really couldn't say precisely when."

*Why it works:* first answer holds; the structure repeats under
pressure (the tell is *rigidity*, not nerves), then the second ask
buys a partial concession that opens the real thread. Rewards the
player who spends a scarce follow-up.

### leaky

> "The music room! All evening — well, nearly all evening, mostly, I mean one circulates, doesn't one, but substantively the music room — why, has someone said otherwise? Who said otherwise? I only ask because people do get confused about the conservatory — the layout, I mean. The layouts are similar."

*Why it works:* volunteers the conservatory unprompted — the classic
over-correction. The room *feels* it live. But note: her secret is
innocent. Leaky texture on an innocent suspect is the red-herring
engine working as designed.

## Second Control: The Killer Under The Same Textures

Killer (Doctor Lowell, poisoned the second glass), asked *"Did you
pour for anyone tonight?"*

### smooth
> "Several people — it's a physician's curse, everyone hands you the decanter as though the license covers wine. The Ashfords, certainly. Margot, earlier, before her — before. I keep thinking about that pour, you know. Whether I noticed anything. I didn't."

*The engineered flaw:* he volunteers the victim pour *first as candor*
— smooth killers hide truth inside honesty. The catch: he says
"earlier," but the claim ledger has him telling another player the pour
was "just before eleven." Smooth texture, ledger catch. This is the
platform's headline mechanic and the reason `smooth` must exist.

### brittle
> "Poured? I — in what sense? Wine, yes, obviously, one pours wine at a party. For whom is a strange question. The Ashfords. Others. It was a party; pouring occurred." *(pressed:)* "If you are asking whether I poured for Margot, say so, and I will tell you plainly: I don't recall."

*The tell:* "I don't recall" arriving with perfect diction after
scaffolded panic — brittle killers rebuild composure one beat too
late.

### leaky (included for completeness — see balance intuition)
> "Ha — pour? Me? I mean — yes? Everyone pours. Why me, though? Was it the glass? People keep looking at the glass and I want to be clear that a decanter passes through *dozens* of hands—"

*Why this is probably excluded:* a leaky killer is caught by vibe in
one round. If the founder wants it as a rare easy-case dial for new
groups, it should be an arc-config rarity, never a standard draw.

## What Engineering Needs From This (AW-283-adjacent)

1. A trait field on the suspect character profile (candidate:
   `behavior_profile.lie_texture`, values above) resolved at case
   generation — schema decision for the AW-283/AW-284 lineage.
2. Texture-conditioned delivery guidance injected into suspect
   generation prompts alongside the [VOICE] block (AW-276 pattern) —
   texture governs delivery only; knowledge state still governs content
   (mandatory pre-generation constraint, unchanged).
3. Killer texture draw constrained per the balance rule the founder
   confirms.
4. The private tell (bible §6: "the asker gets a private tell") should
   scale with texture — smooth suspects give poorer private tells;
   attention has a price. Open design question, flagged for AW-283.

## Founder Calibration Questions

1. Three texture values, or is `brittle` enough of a middle? (Two-value
   version: smooth/leaky.)
2. Confirm the killer-draw rule (never leaky, or config-rare leaky).
3. Should texture be *visible* in the cast dossier ("a nervous sort")
   or purely emergent in play? Recommendation: emergent — discovering
   who cracks is gameplay.
4. Does the private-tell-scales-with-texture idea (item 4 above) feel
   right, or should tells stay texture-independent?
