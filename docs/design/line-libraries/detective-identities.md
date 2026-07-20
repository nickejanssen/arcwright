# Detective Identity Pools And Opening Briefing Shapes — Séance 1928

> Current version: v0.1 DRAFT — not approved content
> Last updated: 2026-07-19
> Status: Draft, awaiting founder review (see 00-direction.md)
> Canonical path: docs/design/line-libraries/detective-identities.md
> Authority: AW-279 task contract; `docs/design/the-host.md` v1.1
> Feeds: AW-279 (detective identity and opening briefing)

## AW-279 Contract Restated (Binding On Every Entry)

- Identity = public name + public flavor only. **No hidden information,
  no assignments, no required performance, no case-truth advantage.**
- Delivered privately to the player's phone during The Pour, before
  Vesper frames the race; only name + flavor project to shared surfaces.
- Phone reveal is staged-but-fast per D-070 presentation hints.
- A player must be able to ignore their identity completely and lose
  nothing.

## 1. Identity Pool (16)

Each identity: `name` (public) · `flavor` (public, one line, scoreboard
and Vesper-address material) · `habit` (private, pure flavor, a wink to
the player — grants nothing, demands nothing).

Design rule: flavor lines describe a *reputation*, never an ability.
"Known for" not "can do." Habits are jokes the player owns privately.

| # | Name | Flavor (public) | Habit (private) |
| --- | --- | --- | --- |
| 1 | Detective Vane | Solved the Harrington affair without leaving the cloakroom. | You distrust anyone who compliments the wallpaper. |
| 2 | Detective Marlowe | Retained by three families who all suspect each other. | You count the candles in every room. There should be an even number. |
| 3 | Detective Quill | Writes everything down. Has never once needed to look. | Your notebook is empty. It has always been empty. It works. |
| 4 | Detective Ashcombe | Thrown out of better parties than this one. | You know exactly which drink is the good decanter. You'd never say. |
| 5 | Detective Ivory | Reads lips across a ballroom. Allegedly. | You nod slowly when suspects finish talking. It rattles them. |
| 6 | Detective Larkspur | The insurance companies' favorite guest. | You privately price everything in the room. The rug: suspicious. |
| 7 | Detective Croft | Once interrogated a séance. The table confessed. | You don't believe in ghosts. You believe in drafts with motives. |
| 8 | Detective Pemberly | Related to nobody here, which everyone finds suspicious. | You've claimed a different hometown at every party this year. |
| 9 | Detective Hale | Never asks the first question. Devastating with the second. | You keep one question in reserve at all times. Even now. |
| 10 | Detective Rook | Plays cards with the staff. Knows what the staff knows. | You always know where the nearest exit and second-nearest lie are. |
| 11 | Detective Wren | Small, quiet, present at every scandal of the decade. | You collect overheard sentences. Tonight already gave you three. |
| 12 | Detective Sable | Wears the same coat to funerals and galas. Nobody's sure which this is. | You decided on arrival who you'd suspect. You're already wrong. Keep going. |
| 13 | Detective Finch | Identifies poison by the shape of the silence afterward. | You sniff every glass out of habit. Even your own. Especially your own. |
| 14 | Detective Mercer | The one the killer, statistically, should worry about. | You maintain eye contact one beat too long. On purpose. Always. |
| 15 | Detective Gilt | Owed favors by half this guest list. Collecting tonight. | You remember every toast ever made in your honor. Both of them. |
| 16 | Detective Thorne | Left the force. The force still writes. | You tap the side of your nose at meaningful moments. It means nothing. |

## 2. Opening Briefing Shapes (4)

The private phone text that lands with the identity during The Pour.
Same anti-burden rule: brief, warm, zero instructions to perform.
Slots: `{{detective_name}}`, `{{flavor}}`, `{{habit}}`,
`{{occasion}}`, `{{location}}`.

**br-1 — The Telegram.** (Recommended default; strongest wrapper fit)
> TELEGRAM — URGENT
> TO: {{detective_name}}
> {{occasion}} AT {{location}} STOP SITUATION DEVELOPING STOP YOUR REPUTATION PRECEDES YOU — QUOTE — {{flavor}} — UNQUOTE STOP COME AS YOU ARE STOP TELL NO ONE STOP
> *(smaller, beneath the fold)* {{habit}}

**br-2 — The Place Card.**
> The house has seated you as **{{detective_name}}**.
> The other guests have heard the stories: *{{flavor}}*
> Between us: {{habit}}
> The rest of the evening is yours to solve.

**br-3 — The Engraved Invitation.**
> {{location}} requests the pleasure of **{{detective_name}}** — yes, *that* {{detective_name}}. {{flavor}}
> Dress: worn. Wits: sharp. {{habit}}

**br-4 — Vesper's Note.** (Handwritten treatment; Vesper's only phone
presence in v1 is this single written artifact — flag for founder: the
bible says Vesper never appears on the phone. This is authored as a
*note she wrote earlier*, physically in the world, not Vesper speaking
on the phone. If that distinction is too fine, cut br-4.)
> A note, tucked into your coat. The handwriting is beautiful and slightly dangerous:
> "{{detective_name}} — I asked for you specifically. {{flavor}} Prove me right. — V."
> *(and below, in the same hand)* {{habit}}

## 3. D-070 Presentation Hints (Per Briefing Shape)

Engine emits hints only; phones decide rendering (surface agnosticism).

| Shape | `presentation_hints` suggestion |
| --- | --- |
| br-1 | `style: telegram`, `reveal: line-by-line-fast`, `sound-hint: typewriter` |
| br-2 | `style: place-card`, `reveal: single-flip` |
| br-3 | `style: invitation`, `reveal: unfold` |
| br-4 | `style: handwritten`, `reveal: ink-in`, `sound-hint: pen` |

Total reveal budget: under 4 seconds to fully readable (AW-279
"staged but fast").

## 4. Vesper Address Formats (Shared Surfaces)

How Vesper uses the public fields on the TV. These are address
*patterns* for the refrain library's `{{detective}}` slot, not new
lines:

- Full formal: "Detective {{detective_name}}" — default.
- Flavor callback: Vesper may quote the flavor line verbatim as an
  aside ("...{{detective_name}} — who, I'm told, {{flavor_clause}}").
  Flavor is public, so this leaks nothing.
- Habits are NEVER spoken by Vesper. They are the player's private
  joke. (Enforcement: habit field simply isn't in the shared-surface
  projection — AW-279 acceptance criterion 3.)

## Review Notes for the Founder

- 16 identities supports 8 players across two sessions without repeats;
  the pool should eventually be per-wrapper (these are Séance-flavored).
  Confirm pool size target for launch.
- br-4 tests the "Vesper never appears on the phone" boundary — see
  inline flag. Cut or keep is a taste call.
- Identity 12 (Sable) and 13 (Finch) carry the darkest flavor; probes
  for how gothic the identity pool may lean.
- Names are surname-only and unisex by design: any player, any body,
  any age plays any card without friction.
