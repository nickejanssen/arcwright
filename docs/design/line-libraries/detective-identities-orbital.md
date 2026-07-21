# Detective Identity Pool And Briefing Shapes — Orbital Gala 2087

> Current version: v0.1 DRAFT — not approved content
> Last updated: 2026-07-19
> Status: Draft, awaiting founder review (see 00-direction.md)
> Canonical path: docs/design/line-libraries/detective-identities-orbital.md
> Authority: AW-279 task contract; `docs/design/the-host.md` v1.2
> Companion: `detective-identities.md` (Séance 1928 pool + AW-279 rules)
> Completes AW-279 coverage for the launch wrapper pair.

AW-279 contract identical to the Séance pool: public name + flavor,
private habit that grants nothing, no hidden information, no burden.

## 1. Identity Pool (16)

Station-registry flavor: investigators are credentialed guests. Names
are surname-only and unisex, same as Séance.

| # | Name | Flavor (public) | Habit (private) |
| --- | --- | --- | --- |
| 1 | Inspector Vale | Cleared the Meridian Station affair from two decks away. | You distrust any room where the air smells like nothing. |
| 2 | Inspector Solano | Retained by three consortiums currently suing each other. | You count exits on arrival. Stations should have more of them. |
| 3 | Inspector Okafor | Reads a suit log the way others read a face. | You check your own suit log twice daily. It has never once been wrong. That's what worries you. |
| 4 | Inspector Marsh | Escorted off finer stations than this one. | You know exactly which champagne globe is the good vintage. You'd never file it. |
| 5 | Inspector Reyes | Licensed to practice in four jurisdictions, none of them up here. | You privately note when station AI pauses before answering. It paused twice tonight. |
| 6 | Inspector Adler | The insurers' first call when something happens above the atmosphere. | You price the salvage of every room you enter. The chandelier: suspicious. |
| 7 | Inspector Ihara | Once interrogated a maintenance drone. It deleted itself. | You don't believe in ghost signals. You believe in transmissions with motives. |
| 8 | Inspector Boone | Related to no one aboard, which the manifest finds statistically unlikely. | You've listed a different homeworld on every docking form this year. |
| 9 | Inspector Castellan | Never asks the first question. Files devastating follow-ups. | You keep one query in reserve at all times. Even in this briefing. |
| 10 | Inspector Petrova | Plays cards with the crew deck. Knows what the crew deck knows. | You always know where the nearest airlock and the second-nearest lie are. |
| 11 | Inspector Wren-9 | Small, quiet, present at every orbital scandal of the decade. Possibly the same Wren. | You collect overheard sentences. Recycled air carries them beautifully. |
| 12 | Inspector Sable | Wears the same coat in vacuum-rated and formal settings. Nobody's sure which this is. | You decided on docking who you'd suspect. You're already wrong. Continue. |
| 13 | Inspector Finch | Identifies toxins by the shape of the silence afterward. Works in vacuum too. | You scan every globe out of habit. Even your own. Especially your own. |
| 14 | Inspector Mercer | The one the killer, actuarially, should worry about. | You maintain eye contact one beat past comfortable. The station AI blinked first. |
| 15 | Inspector Gilt | Owed favors across three orbits. Collecting tonight. | You remember every toast given in your honor. Both, adjusted for time dilation. |
| 16 | Inspector Thorne | Left the service. The service still transmits. | You tap your collar at meaningful moments. It transmits nothing. Probably. |

## 2. Opening Briefing Shapes (4)

Slots: `{{detective_name}}`, `{{flavor}}`, `{{habit}}`, `{{occasion}}`,
`{{location}}`.

**br-1 — The Boarding Credential.** (Recommended default)
> ORBITAL TRANSIT AUTHORITY — CREDENTIAL CONFIRMED
> BEARER: {{detective_name}}
> ASSIGNMENT: {{occasion}}, {{location}}. Situation: developing.
> NOTES ON FILE: {{flavor}}
> *(appended, unofficial, lowercase)* {{habit}}

**br-2 — The Encrypted Dossier.**
> Decrypting… done. You are **{{detective_name}}** — yes, *that* {{detective_name}}. {{flavor}}
> This dossier will not self-destruct. Stations bill for that now.
> Between you and the encryption: {{habit}}

**br-3 — The Concierge Welcome.**
> {{location}} welcomes **{{detective_name}}**. Your reputation docked before you did: *{{flavor}}*
> Amenities: unlimited. Suspicions: encouraged. {{habit}}

**br-4 — The Manifest Anomaly.**
> The passenger manifest lists you twice: once as a guest, once as **{{detective_name}}** — {{flavor}}
> The station has elected not to correct the record. It suspects it will need you.
> *(margin note, origin unknown)* {{habit}}

## 3. D-070 Presentation Hints

| Shape | `presentation_hints` suggestion |
| --- | --- |
| br-1 | `style: credential`, `reveal: scan-line`, `sound-hint: chirp` |
| br-2 | `style: dossier`, `reveal: decrypt-fast` |
| br-3 | `style: concierge-card`, `reveal: single-fade` |
| br-4 | `style: manifest`, `reveal: line-by-line-fast` |

Reveal budget under 4 seconds, per AW-279.

## Review Notes for the Founder

- Address is "Inspector" here vs. Séance's "Detective" — matches the
  wrapper register, but Vesper's refrain slot is `{{detective}}` in
  both libraries. Decide: per-wrapper honorific (engine fills
  "Inspector Vale" as the whole slot value — no code change needed) or
  flatten to "Detective" everywhere.
- Wren-9 (11) and Sable (12) deliberately echo the Séance pool —
  a returning-cast joke for groups who play both wrappers. Cut if
  cross-wrapper continuity reads as canon you don't want.
- br-4 gives the *station* mild agency ("it suspects it will need
  you") — same diegesis family as open question 1; one answer governs.
