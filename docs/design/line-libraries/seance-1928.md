# Vesper Refrain Library — Séance 1928

> Current version: v0.1 DRAFT — not approved content
> Last updated: 2026-07-19
> Status: Draft, awaiting founder review (see 00-direction.md)
> Canonical path: docs/design/line-libraries/seance-1928.md
> Diegesis (D-084): **witness** — Vesper is present in-world as the
> house's Master of Ceremonies; first-person memory of the evening is
> in-character. Secondary memory-holder: the house.
> Authority: `docs/design/the-host.md` v1.2; `docs/design/moodboards/seance-1928.md`
> Wrapper: High Society — Séance 1928. Vesper as the house's Master of
> Ceremonies: decanter in one hand, lit cigarette in the other. Warm,
> deco-cadenced, dangerous under the charm.

## Format

Every entry:

- `mood` — jubilant | grave | wondering | ominous | wink | stinger-dry |
  stinger-ominous | stinger-delighted | wrong-accusation | reveal
- `beat` — pour | scene | grill | twist | last-call | truth | any
- `shift` — the mood this line can shift into on delivery, or `none`
- `slots` — the ONLY variables AI may fill. Everything else is fixed.

Slot vocabulary: `{{suspect}}` `{{victim}}` `{{detective}}`
`{{location}}` `{{time}}` `{{evidence}}` `{{drink}}` `{{occasion}}`
`{{callback}}` (a case-specific detail already established on stage).

Runtime rule (the-host.md §5): Vesper never speaks a line that is not
in this library. AI fills slots; AI does not compose.

---

## 1. Cold Open — Jubilant (8)

The welcome. Ends warm; every entry supports the drop.

**co-j-1** · pour · shift: grave · slots: {{occasion}}, {{location}}
> Good evening. The candles are lit, the silver is out, and {{location}} is wearing its best face — which, historically, is when things go wrong in the loveliest way.

**co-j-2** · pour · shift: grave · slots: {{occasion}}, {{drink}}
> Welcome to {{occasion}}. The {{drink}} is open — the good one, the one they only open when they mean it. And tonight, of course, they meant it.

**co-j-3** · pour · shift: grave · slots: {{location}}, {{occasion}}
> Somebody spent money on this room. Somebody rehearsed their entrance. Everybody, I promise you, checked the guest list twice.

**co-j-4** · pour · shift: grave · slots: {{occasion}}
> I do love {{occasion}}. Everyone arrives already knowing everyone — which saves such a great deal of time, later, when it matters who knew whom.

**co-j-5** · pour · shift: grave · slots: {{location}}, {{time}}
> By {{time}}, the party had found its rhythm: the laughter in the right rooms, the whispers in the wrong ones. A perfect evening. Nearly.

**co-j-6** · pour · shift: grave · slots: {{occasion}}, {{drink}}
> There is a rule in houses like this one: nothing truly interesting happens before the second {{drink}}. The house, tonight, kept to its rule.

**co-j-7** · pour · shift: grave · slots: {{location}}
> Every light in {{location}} tonight is a flame. Candles, lamplight, the ember of one unattended cigarette. Do keep track of the flames. I always do.

**co-j-8** · pour · shift: grave · slots: {{occasion}}, {{victim}}
> And there — {{victim}}, radiant, holding court by the fire. Remember them exactly like this. Please. It's important to me.

## 2. Cold Open — The Drop (6)

The shift-to-grave that lands the death. Fires on `seq-body`.

**co-d-1** · pour · shift: none (terminal grave) · slots: {{victim}}, {{location}}, {{time}}
> And then, at {{time}} — the music did not stop. Music never does. But {{victim}} was in {{location}}, and {{victim}} was not getting up.

**co-d-2** · pour · shift: none · slots: {{victim}}
> Here is the thing about a perfect evening: it only has to go wrong once. {{victim}} is dead. The party, I'm afraid, is now something else.

**co-d-3** · pour · shift: none · slots: {{victim}}, {{location}}
> {{victim}} came to {{location}} tonight with a coat, a grievance, and every intention of leaving. One out of three went home.

**co-d-4** · pour · shift: none · slots: {{victim}}, {{time}}
> At {{time}}, someone in this house made a decision. Quietly. Between one toast and the next. {{victim}} never heard it coming — and neither, I confess, did I.

**co-d-5** · pour · shift: none · slots: {{victim}}, {{evidence}}
> They found {{victim}} with {{evidence}} close at hand. The house went silent, room by room, the way a house does when it realizes what it's holding.

**co-d-6** · pour · shift: jubilant (the pick-up) · slots: {{victim}}
> {{victim}} is gone, and I take that seriously — I take very little else in this house seriously, but that, yes. So. Detectives. Shall we see who did it?

## 3. Beat Turns (18)

Six per mood. Carry the arc between beats; the race stays alive.

### Jubilant (6)

**bt-j-1** · scene · shift: ominous · slots: {{location}}
> The scene is open, detectives. {{location}} will receive you — touch nothing, suspect everything, and mind the rug. It has already had a difficult night.

**bt-j-2** · grill · shift: grave · slots: none
> And now the part I confess I dress for: the questions. One at a time, detectives. They've all rehearsed. Let's see who rehearsed *well*.

**bt-j-3** · grill · shift: none · slots: {{suspect}}
> {{suspect}} has agreed to take the stage — "agreed," in the sense that the alternative was worse. Ask nicely. Or don't. I'll enjoy either.

**bt-j-4** · twist · shift: grave · slots: none
> Oh, I *do* have something for you. I've been holding it all evening, the way one holds a telegram at a dinner party — until precisely the wrong moment. Which is now.

**bt-j-5** · last-call · shift: ominous · slots: none
> Last call, detectives. The candles are low, the decanter is empty, and someone in this house is very nearly out of evening. Final questions. Make them expensive.

**bt-j-6** · scene · shift: none · slots: {{evidence}}
> The house has offered up {{evidence}} — freely, which should worry you. Houses like this one give nothing away without a reason.

### Grave (6)

**bt-g-1** · grill · shift: jubilant · slots: {{victim}}
> Someone in this room watched {{victim}} die and then chose their next sentence carefully. They are still choosing sentences carefully. Listen for that.

**bt-g-2** · twist · shift: none · slots: {{callback}}
> Everything you believe about this case rests on {{callback}}. I want you to hold that thought very still — because in a moment it is going to move.

**bt-g-3** · last-call · shift: none · slots: none
> The truth does not care whether you find it, detectives. It will sit in this house for another hundred years, perfectly patient. You have rather less time.

**bt-g-4** · scene · shift: wondering · slots: {{victim}}, {{location}}
> {{victim}} spent their last hour in {{location}}. Walk it slowly. The dead leave the room; they never quite leave the furniture.

**bt-g-5** · grill · shift: jubilant · slots: {{suspect}}
> {{suspect}} has told you the truth tonight. Several times, in fact. The skill — and it is a skill — is in noticing which times.

**bt-g-6** · truth · shift: none · slots: none
> Put down your glasses. What happens next in this room is the reason we came.

### Wondering (6)

**bt-w-1** · scene · shift: ominous · slots: {{evidence}}
> {{evidence}}. Curious. It shouldn't be here — and things that shouldn't be here are my very favorite kind of thing.

**bt-w-2** · grill · shift: none · slots: {{suspect}}, {{time}}
> {{suspect}} keeps returning to {{time}}. Unprompted. Twice now. I don't know what it means yet — but a person who volunteers an alibi is a person who priced one.

**bt-w-3** · twist · shift: grave · slots: {{callback}}
> I keep turning {{callback}} over, the way one turns a place card at the wrong table. Whose seat was this, really?

**bt-w-4** · scene · shift: none · slots: {{location}}
> Why {{location}}? Of every room in this house, the worst one for a quiet crime. Unless, of course, quiet was never the point.

**bt-w-5** · last-call · shift: grave · slots: none
> Strange, isn't it — everyone's story fits everyone else's, like a set of borrowed cufflinks. Stories that fit that well were fitted.

**bt-w-6** · grill · shift: jubilant · slots: {{suspect}}, {{suspect_2}}
> {{suspect}} will not look at {{suspect_2}}. Has not, all evening. In a house this small, detectives, avoiding someone is a full-time occupation.

## 4. Suspect Stage Stingers (24)

Fires as a suspect takes the stage. Eight per register.

### Dry (8)

**st-d-1** · grill · shift: none · slots: {{suspect}}
> {{suspect}}. Everyone. Everyone — {{suspect}}. You've met. That, as it turns out, is rather the problem.

**st-d-2** · grill · shift: none · slots: {{suspect}}, {{time}}
> {{suspect}} is being asked, very politely, where they were at {{time}}. They have been asked this before. Watch the hands.

**st-d-3** · grill · shift: none · slots: {{suspect}}
> {{suspect}} would like you to know they have nothing to hide. In my experience, that sentence costs nothing and is priced accordingly.

**st-d-4** · grill · shift: none · slots: {{suspect}}, {{drink}}
> {{suspect}} has refreshed their {{drink}} three times since the body was found. Grief takes many forms. So does arithmetic.

**st-d-5** · grill · shift: none · slots: {{suspect}}
> The stage receives {{suspect}}, who has chosen — interestingly — to smile.

**st-d-6** · grill · shift: none · slots: {{suspect}}, {{victim}}
> {{suspect}} and {{victim}} were close. Everyone says so. Chiefly, it must be said, {{suspect}}.

**st-d-7** · grill · shift: none · slots: {{suspect}}
> A word on {{suspect}}: in eleven years, I have never once seen them arrive early, leave late, or answer the first question they were actually asked.

**st-d-8** · grill · shift: ominous · slots: {{suspect}}
> {{suspect}} takes the stage. Note, detectives, that of everyone in this house, they alone have not asked *who did it*.

### Ominous (8)

**st-o-1** · grill · shift: none · slots: {{suspect}}
> Before {{suspect}} answers anything — watch the pause. The pause is where this house keeps its secrets.

**st-o-2** · grill · shift: none · slots: {{suspect}}, {{location}}
> {{suspect}} knows {{location}} better than anyone here. Knows the doors. Knows which floorboard speaks. Knows, I'd wager, which one doesn't.

**st-o-3** · grill · shift: none · slots: {{suspect}}
> There are two versions of tonight, and {{suspect}} appears in both. Only one of them survives cross-examination.

**st-o-4** · grill · shift: none · slots: {{suspect}}, {{victim}}
> The last person to speak with {{victim}} is in this room. {{suspect}} would very much like that sentence to move along. It won't.

**st-o-5** · grill · shift: dry · slots: {{suspect}}, {{evidence}}
> Ask {{suspect}} about {{evidence}}. Ask twice. The first answer is for the room; the second, if you press, is for the record.

**st-o-6** · grill · shift: none · slots: {{suspect}}
> {{suspect}}'s story has one door in it that stays locked. Every story tonight has one. Theirs has a draft coming from under it.

**st-o-7** · grill · shift: none · slots: {{suspect}}, {{time}}
> Between {{time}} and the scream, there are eleven unaccounted minutes. {{suspect}} owns at least four of them.

**st-o-8** · grill · shift: none · slots: {{suspect}}
> The candles lean when {{suspect}} passes. Old houses notice things, detectives. I've learned to notice what they notice.

### Delighted-About-Awful (8)

**st-de-1** · grill · shift: grave · slots: {{suspect}}
> Oh, *wonderful* — {{suspect}}. I've been looking forward to this one all evening, and I am not remotely ashamed to say so.

**st-de-2** · grill · shift: none · slots: {{suspect}}, {{callback}}
> {{suspect}}, welcome. Before you sit: {{callback}} — was that before or after you told us the *other* version? Take your time. We have candles.

**st-de-3** · grill · shift: none · slots: {{suspect}}
> {{suspect}} swore they'd never set foot on this stage. And yet — here are the feet! I adore this house.

**st-de-4** · grill · shift: none · slots: {{suspect}}, {{drink}}
> {{suspect}} arrives with a fresh {{drink}} and a prepared expression. Detectives, as a personal favor: ruin the expression. Leave the {{drink}}.

**st-de-5** · grill · shift: grave · slots: {{suspect}}, {{victim}}
> {{suspect}} once told {{victim}} something unforgivable. I know because I was pouring. Ask me no more — ask *them*.

**st-de-6** · grill · shift: none · slots: {{suspect}}
> The thing I treasure about {{suspect}} — truly treasure — is that when they lie, they get *specific*. Listen for the detail nobody asked for.

**st-de-7** · grill · shift: none · slots: {{suspect}}
> {{suspect}}! Sit, sit. The chair is comfortable, the light is flattering, and absolutely nothing else about the next five minutes will be.

**st-de-8** · grill · shift: none · slots: {{suspect}}, {{evidence}}
> And now {{suspect}}, who has an explanation for {{evidence}}. A good one. Rehearsed in the mirror, I'd say, no fewer than — shall we count together?

## 5. Wrong Accusation (10)

Per D-081 (v1.1): by-name roasts permitted. Target the detective
identity, never the human. Registers labeled per the eight permitted.
The compassionate entries survive from the v1.0 rule; keep the mix.

**wa-1** · any · shift: jubilant · register: compassionate · slots: {{detective}}, {{suspect}}
> Detective {{detective}} accuses {{suspect}}. The house holds its breath — the house exhales. No. Not tonight, detective. But you saw *something* real. Hold on to it.

**wa-2** · any · shift: none · register: witty · slots: {{detective}}, {{suspect}}
> Detective {{detective}} names {{suspect}}. Bold. Confident. Wrong. Two of those three qualities will serve you well in this house.

**wa-3** · any · shift: none · register: dad-jokey · slots: {{detective}}, {{suspect}}
> {{suspect}}? No, detective {{detective}}. Innocent — of this, anyway. I'd say the case has a hole in it, but you've just made the hole yourself, so — carry on!

**wa-4** · any · shift: grave · register: solemn · slots: {{detective}}
> No, detective {{detective}}. And I want the room to note: that was a *serious* accusation, seriously made. It deserved to be right. It wasn't.

**wa-5** · any · shift: none · register: flirty · slots: {{detective}}, {{suspect}}
> Detective {{detective}}, that was very nearly dazzling. Wrong — {{suspect}} keeps their crimes strictly financial — but the way you said it? Do accuse someone else soon.

**wa-6** · any · shift: none · register: absurd · slots: {{detective}}, {{suspect}}
> {{suspect}}! Imagine. {{suspect}}, who once mourned a houseplant for a month. Detective {{detective}}, I've written your theory down and put it somewhere I keep the decorative fruit.

**wa-7** · any · shift: none · register: unhinged · slots: {{detective}}
> WRONG — sorry. Sorry. Composure. We are composed. Detective {{detective}}, the house thanks you for your donation to the evening's suspense fund.

**wa-8** · any · shift: jubilant · register: gravitas · slots: {{detective}}, {{suspect}}
> The accusation lands on {{suspect}} — and slides off. Some names hold a crime, detective {{detective}}; this one, tonight, does not. The killer heard you, though. The killer is smiling.

**wa-9** · any · shift: none · register: silly · slots: {{detective}}, {{suspect}}
> No! But points for theater, detective {{detective}} — you pointed and everything. {{suspect}} may now return to being merely suspicious, which they do beautifully.

**wa-10** · any · shift: grave · register: witty · slots: {{detective}}
> Wrong, detective {{detective}} — and expensively so. Every miss tells the killer exactly how safe they are. They are, at this moment, doing the math.

## 6. The Reveal (6)

Structure per the-host.md §6.3: grave reconstruction → delighted at
the killer's best move → ordinary last line. Entries here are the
grave-then-jubilant frames; the ordinary last line is authored per
case shape in the truth-sequence library (item 7, AW-278).

**rv-1** · truth · shift: jubilant · slots: {{victim}}, {{time}}
> Then let the house speak. At {{time}}, {{victim}} was alive. Everything after that was arranged — the light, the story, the seating. Detectives, you were *meant* to be looking elsewhere. Nearly all of you were.

**rv-2** · truth · shift: jubilant · slots: {{killer}}, {{victim}}
> It was {{killer}}. It was always {{killer}} — from the first pour, through every polite little lie, to the moment {{victim}} understood, one second too late, exactly whose house this really was.

**rv-3** · truth · shift: jubilant · slots: {{killer}}, {{evidence}}
> And here is what I admire — professionally, you understand: {{killer}}'s single mistake was {{evidence}}. One object. One oversight. Every perfect crime keeps one, like a signature.

**rv-4** · truth · shift: none · slots: {{detective}}, {{callback}}
> Detective {{detective}} — you nearly had it at {{callback}}. Nearly. The house watched you lean toward the truth and choose the more comfortable chair.

**rv-5** · truth · shift: jubilant · slots: {{killer}}
> {{killer}} planned everything except the part where you kept asking questions. Murderers rehearse endings, detectives. They never rehearse *you*.

**rv-6** · truth · shift: none · slots: {{victim}}
> Whatever else happens after the candles go out — {{victim}} was owed the truth in this room, tonight, said aloud. Consider the debt paid.

## 7. The Wink (6)

Once per session. Vesper notices the couch. Never tutorializes.

**wk-1** · grill · shift: none · slots: none
> You are, of course, on a couch. I'm told this is where the best detective work happens now. Very well. Suspect?

**wk-2** · scene · shift: none · slots: none
> Between us — and it is just us, the house doesn't count — you're doing rather better than the last group. I say that to everyone. Tonight I mean it.

**wk-3** · twist · shift: none · slots: none
> Comfortable? Good. I arranged the next part with you specifically in mind.

**wk-4** · grill · shift: none · slots: {{drink}}
> If anyone on that couch is holding a {{drink}} right now — a small toast. To you. The suspects can wait; good taste cannot.

**wk-5** · last-call · shift: grave · slots: none
> I see you leaning forward. I always know the exact moment a couch leans forward. It's my favorite moment — savor it, because the next one is heavier.

**wk-6** · pour · shift: none · slots: none
> One housekeeping note from your host: I have been doing this for a very long time, and you — arriving, sitting, suspecting — are still the part I look forward to.

---

## Coverage vs. the-host.md §5 Minimum

| Section | Minimum | Authored |
| --- | --- | --- |
| Cold open jubilant | 8 | 8 |
| Cold open drop | 6 | 6 |
| Beat turns | 18 | 18 |
| Stage stingers | 24 | 24 |
| Wrong accusation | 6 | 10 (D-081 roast registers) |
| Reveal | 6 | 6 |
| Wink | 6 | 6 |
| **Total** | **~74** | **78** |

## Review Notes for the Founder

- **wa-5 (flirty) and wa-7 (unhinged)** are the two lines most likely
  to cross your line — they're the calibration probes for D-081.
  If wa-7 is too much, the unhinged register caps at st-de-3's level.
- **st-de-5 and wk-2** give Vesper first-person memory of the house
  ("I was pouring"). This implies Vesper is diegetically *present*
  across sessions — consistent with "hosted a thousand of these
  evenings," but say the word and those become house-observed instead.
- New slot introduced: `{{suspect_2}}` (bt-w-6) and `{{killer}}`
  (reveal section — resolved case truth, only ever filled at Beat 6).
  Both need adding to the runtime slot whitelist when this converts to
  `nightcap/content/host_lines/`.
