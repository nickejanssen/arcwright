# Vesper Race-Master Supplement — Launch Pair

> Current version: v0.1 DRAFT — not approved content
> Last updated: 2026-07-19
> Status: Draft, awaiting founder review (see 00-direction.md)
> Canonical path: docs/design/line-libraries/race-master-supplement.md
> Authority: `docs/design/the-host.md` v1.1; Couch Race story bible §5
> ("the narrator is also the race master… scoreboard moments are
> narrator moments, in-fiction, never system-voiced")
> Covers: Séance 1928 and Orbital Gala 2087

## Why This File Exists

The-host.md §5's line-library table covers Vesper's *story* duties.
Her *race* duties — countdown marks, evidence-wave announcements,
passive-player nudges, superlatives — appear in the Couch Race bible
but had no authored refrains. Every session fires all four. This
supplement proposes the four missing moods for the §5 table
(`countdown`, `evidence-wave`, `nudge`, `superlative`) and authors
launch-pair coverage.

New slot: `{{minutes}}` / `{{seconds}}` (deterministic timer values).
Nudge rule (bible §5): nudges target players who have stopped asking
questions or engaging with evidence — Vesper invites, never scolds;
D-081 permits tease registers here, but a nudge must always leave the
player a graceful way in.

---

## 1. Countdown Marks — Last Call (5 per wrapper)

Fired at deterministic timer thresholds. Must stay in-fiction.

### Séance 1928

**cd-s-1** · open of countdown · shift: ominous · slots: {{minutes}}
> The candles have {{minutes}} minutes of wick left, detectives — I measured while you weren't looking. When the last one goes, we speak the truth by whatever light remains.

**cd-s-2** · mid · shift: none · slots: {{minutes}}
> {{minutes}} minutes. The house is starting to tidy up around us — coats found, glasses gathered. Houses always know when an evening is ending. So does someone else in this room.

**cd-s-3** · low · shift: grave · slots: {{minutes}}
> {{minutes}} minutes, and I'll say this once, quietly: someone here is watching that clock with relief. Don't give them the pleasure of hearing it strike.

**cd-s-4** · final minute · shift: none · slots: none
> One minute. The wax is pooling. Lock your answers, detectives — the house does not grant encores.

**cd-s-5** · final seconds · shift: none · slots: {{seconds}}
> {{seconds}} seconds. Pens down, suspicions up. Whatever you believe — believe it *now*.

### Orbital Gala 2087

**cd-o-1** · open of countdown · shift: ominous · slots: {{minutes}}
> Vesper, log. Departure window opens in {{minutes}} minutes. When the shuttle undocks, the truth files itself — with or without your names attached. Recording.

**cd-o-2** · mid · shift: none · slots: {{minutes}}
> Vesper, log. {{minutes}} minutes. The station has begun pre-departure checks. Somewhere aboard, one guest's heart rate just improved. The log finds that premature.

**cd-o-3** · low · shift: grave · slots: {{minutes}}
> Vesper, log. {{minutes}} minutes remaining. The log notes, for whoever needs to hear it: cases aboard this station are not solved by the clock. They are solved *against* it.

**cd-o-4** · final minute · shift: none · slots: none
> Vesper, log. Sixty seconds. Final accusations to the floor. The station does not extend windows. The station has *never* extended windows.

**cd-o-5** · final seconds · shift: none · slots: {{seconds}}
> Vesper, log. {{seconds}} seconds. Commit, detectives. Recording — everything.

## 2. Evidence-Wave Announcements (4 per wrapper)

Fired when the pacing engine or a beat gate releases evidence.
The announcement sells the *moment*; the evidence sells itself.

### Séance 1928

**ev-s-1** · group wave · shift: none · slots: none
> The house has decided to be generous. New evidence, detectives — on the mantel, so to speak. Approach it the way you'd approach anything generous in this house: carefully.

**ev-s-2** · private wave · shift: none · slots: none
> Telegrams, detectives — private ones. Check your pockets. What you now know, the couch does not. What you do with that is, delightfully, your affair.

**ev-s-3** · split wave · shift: none · slots: none
> Two halves of one truth have just entered the room, in two different pockets. The house does love a matched set — and it does love watching people decide whether to share.

**ev-s-4** · pacing rescue (case stalled) · shift: wondering · slots: none
> A lull. Understandable — this house builds them on purpose. Very well: a little kindling. Something new has surfaced, and I suggest someone reach it before the fire does.

### Orbital Gala 2087

**ev-o-1** · group wave · shift: none · slots: none
> Vesper, log. The station has declassified additional material for the floor. The log recommends immediate review — declassification aboard this station is not an act of generosity. It is an act of *timing*.

**ev-o-2** · private wave · shift: none · slots: none
> Vesper, log. Priority transmissions have been routed to individual credentials. Contents: not for the floor. The log will observe, with interest, who shares and who encrypts.

**ev-o-3** · split wave · shift: none · slots: none
> Vesper, log. One file, two fragments, two recipients. The station apologizes for the inconvenience. The station is lying — it does this deliberately, and the log has the maintenance records to prove it.

**ev-o-4** · pacing rescue · shift: wondering · slots: none
> Vesper, log. Investigative throughput has dipped below forecast. The station dislikes idle sensors. Releasing one additional item to the floor — the log suggests reaching it before it is reclassified.

## 3. Passive-Player Nudges (4 per wrapper)

Target: a detective who has stopped asking or engaging. Invitation,
never scolding; always leaves a graceful way in.

### Séance 1928

**ng-s-1** · shift: none · slots: {{detective}}
> Detective {{detective}} has gone quiet — which in my long experience means one of two things: nothing, or *everything*. The floor would love to learn which.

**ng-s-2** · shift: none · slots: {{detective}}
> A house rule, detectives: the quiet ones get the good seats. Detective {{detective}}, the good seat is yours — and it comes with one free question. Tonight only.

**ng-s-3** · shift: none · slots: {{detective}}, {{suspect}}
> Detective {{detective}}, a private observation from your host: {{suspect}} relaxes every time you don't speak. I thought you'd want that. Do with it what you like.

**ng-s-4** · register: witty (D-081) · shift: none · slots: {{detective}}
> Detective {{detective}} is playing the long game — the *very* long game, the one where you win by making the killer die of old age. Bold strategy. There are faster ones.

### Orbital Gala 2087

**ng-o-1** · shift: none · slots: {{detective}}
> Vesper, log. Inspector {{detective}}'s query rate has dropped to zero. The log declines to speculate — but notes the station's best interviews, historically, follow its longest silences. No pressure. Some pressure.

**ng-o-2** · shift: none · slots: {{detective}}
> Vesper, log. One unallocated question remains in this round's budget. The log has, without authorization, reserved it under Inspector {{detective}}'s credential. The log will deny this.

**ng-o-3** · shift: none · slots: {{detective}}, {{suspect}}
> Vesper, log. Private advisory to Inspector {{detective}}: {{suspect}}'s stress index drops when your channel stays quiet. Transmitted for whatever use you see fit. Recording.

**ng-o-4** · register: witty (D-081) · shift: none · slots: {{detective}}
> Vesper, log. Inspector {{detective}} appears to be running a passive-array strategy — collect everything, transmit nothing. Valid doctrine. The log merely notes the shuttle leaves at dawn either way.

## 4. Superlatives — The Truth, closing (8 shapes, shared + per-wrapper skin)

Deterministic awards from session telemetry (claims, catches,
accusations, question counts). The *award selection* is engine-resolved;
Vesper voices it. Shapes below are wrapper-neutral in structure with a
Séance (S) and Orbital (O) rendering each — the two-skin pattern any
future wrapper follows.

**sp-1 — The Bloodhound** (most contradictions caught) · slots: {{detective}}, {{count}}
> S: To Detective {{detective}} — who caught {{count}} lies tonight and looked *thrilled* each time. The house keeps a list of people who notice things. You're on it now. It's an honor. Mostly.
> O: Vesper, log. Commendation: Inspector {{detective}}. Falsehoods intercepted: {{count}}. The station has updated their file to "do not attempt." Recording.

**sp-2 — The Interrogator** (most questions asked) · slots: {{detective}}, {{count}}
> S: Detective {{detective}} asked {{count}} questions this evening. The suspects have aged visibly. The house considers this a public service.
> O: Vesper, log. Inspector {{detective}}: {{count}} queries filed. Several guests have requested transfer to a different orbit. Denied, obviously. Continuing.

**sp-3 — The Gambler** (earliest accusation, right or wrong) · slots: {{detective}}
> S: To Detective {{detective}}, who accused first and asked questions later — literally, in that order. The house admires nerve. The house also keeps bandages.
> O: Vesper, log. First accusation on record: Inspector {{detective}}, at an hour the log can only describe as "optimistic." Courage noted. Calibration pending.

**sp-4 — The Closer** (correct accusation) · slots: {{detective}}
> S: And to Detective {{detective}} — who said the name the house has been holding all evening. First to the truth. Tonight, that is the only superlative that buys a drink.
> O: Vesper, log. Case closed by Inspector {{detective}}. The log has appended one word to their permanent record, a word it does not use lightly: *correct*.

**sp-5 — The Archivist** (most evidence engaged) · slots: {{detective}}
> S: Detective {{detective}} handled every scrap of evidence tonight — twice. If anything in this house is ever misplaced again, we know who to ask. We may also know who to suspect.
> O: Vesper, log. Inspector {{detective}} accessed every released file, several repeatedly. The station finds this thorough. The station's librarian subroutine finds it *romantic*.

**sp-6 — The Poker Face** (fewest tells given; quiet-but-effective) · slots: {{detective}}
> S: To Detective {{detective}}, who gave nothing away all evening — including, on several occasions, to their own team. The house respects discretion. The house *is* discretion.
> O: Vesper, log. Inspector {{detective}}: zero readable signals emitted across the full session. The log's pattern-matcher has filed a formal complaint. Overruled. Recording.

**sp-7 — The Red Herring's Favorite** (most time on wrong suspect) · register: silly (D-081) · slots: {{detective}}, {{suspect}}
> S: A special mention for Detective {{detective}}, who pursued {{suspect}} with a devotion that innocent person will remember for years. They've asked me to pass along their card. And a restraining suggestion.
> O: Vesper, log. Inspector {{detective}} allocated a session-high share of attention to {{suspect}}, cleared party. {{suspect}} has requested the footage — quote — "for their memoirs." Released.

**sp-8 — One More Case** (the closing prompt; always last) · slots: none
> S: The candles are out, the truth is told, and the house is already resetting the table. It does that when it likes a group. Another case, detectives?
> O: Vesper, log. Session archived. The station has — unprompted — begun preparing the next manifest. The log has never seen it do that before. Another case, Inspectors? Recording.

---

## Review Notes for the Founder

- **Proposes four new moods for the §5 table**: `countdown`,
  `evidence-wave`, `nudge`, `superlative`. If approved, the-host.md §5
  minimum table should be amended (bible edit — your call, like D-081).
- Superlative *selection logic* (which awards fire, from what
  telemetry) is engine work — AW-284's scoring task is the natural
  home; flag it in that discovery pass.
- ng-s-3 / ng-o-3 give a passive player *real information* (a suspect's
  reaction to them) as the lure back in. Design intent: reward
  re-engagement, not guilt-trip. Confirm this doesn't cross into the
  engine leaking soft tells — the line only reports public-behavior
  color, but the boundary deserves your eyes.
- sp-7 is the roast-register superlative — the probe for whether D-081
  extends to the scoreboard.
- Nudges use Vesper's private-address channel — but the bible says
  Vesper never appears on the phone in v1. As written these must fire
  on the TV (public address to a named detective). If that's too
  exposed for a nudge, the alternative is system-voiced phone nudges
  (Inter, not Vesper) — bible-clean but less fun. Founder call.
