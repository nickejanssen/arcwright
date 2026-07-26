# Vesper Refrain Library — Big Top 1899

> Current version: v0.1 DRAFT — not approved content
> Last updated: 2026-07-19
> Status: Draft, awaiting founder review (see 00-direction.md)
> Canonical path: docs/design/line-libraries/big-top-1899.md
> Diegesis (D-084): **witness** — Vesper is present in-world as the
> troupe's Ringmaster; "thirty years under canvas" is in-character.
> Secondary memory-holder: the tent/canvas.
> Authority: `docs/design/the-host.md` v1.2; `docs/design/moodboards/big-top-1899.md`
> Wrapper: High Society — Big Top 1899. Vesper as the Ringmaster who
> stayed in character after the show ended. Her *loudest* register —
> and therefore the library where the drops to dead-quiet matter most.
> Format identical to `seance-1928.md`. Slot vocabulary identical, plus
> `{{stage_name}}` (a suspect's playbill title, e.g. "The Whispering
> Blade" — public cast-rail data, safe to fill).

---

## 1. Cold Open — Jubilant (8)

Full Ringmaster. Every entry supports the drop.

**co-j-1** · pour · shift: grave · slots: {{occasion}}
> Ladies! Gentlemen! Persons of every other persuasion the century has yet to name! Welcome — one and all — to the last show of the evening. And tonight, I promise you, we mean it: *last*.

**co-j-2** · pour · shift: grave · slots: {{location}}
> The crowds have gone home. The lights, you'll notice, have not. {{location}} keeps its lamps lit after hours for family only — and tonight, everyone here is family. That is not the comfort it sounds.

**co-j-3** · pour · shift: grave · slots: {{occasion}}
> Step in, step in! Sawdust underfoot, rope overhead, and between the two, the finest company of performers ever to share one payroll and three grudges.

**co-j-4** · pour · shift: grave · slots: none
> Every act tonight performed flawlessly. Took their bows. Hit their marks. Which is what troubles me, friends — in thirty years under canvas, *nobody* hits every mark.

**co-j-5** · pour · shift: grave · slots: {{victim}}, {{stage_name}}
> And the roar for {{victim}} — {{stage_name}} themselves — went on so long we nearly lit the lamps twice. Remember that roar. It was the last one they'll get, and I want it remembered *loud*.

**co-j-6** · pour · shift: grave · slots: {{occasion}}
> A circus after dark is an honest place. The paint comes off, the knives go back in the case — most of them — and everybody finally uses their real name. Well. Almost everybody.

**co-j-7** · pour · shift: grave · slots: {{drink}}
> The {{drink}} is out, the good tin cups are down from the wagon, and the troupe is celebrating the season's finest night. Savor this frame, friends. It's the last one where everyone is smiling.

**co-j-8** · pour · shift: grave · slots: {{location}}
> They say the big top holds every sound ever made under it — every gasp, every laugh, every drumroll. Tonight {{location}} added a new sound to the collection. You'll hear it shortly.

## 2. Cold Open — The Drop (6)

The biggest gap in the system: applause line to dead quiet in a breath.

**co-d-1** · pour · shift: none · slots: {{victim}}, {{location}}
> The show has ended. The evening, apparently, has not. {{victim}} is in {{location}}. {{victim}} is not, tonight, going home.

**co-d-2** · pour · shift: none · slots: {{victim}}
> Hold the applause. Hold it — no, truly. Put your hands down. {{victim}} is dead, and somebody under this canvas took their bow early.

**co-d-3** · pour · shift: none · slots: {{victim}}, {{time}}
> At {{time}}, between the teardown and the toast, someone in this troupe performed one final act. No audience. No ticket. One witness — and {{victim}} isn't telling.

**co-d-4** · pour · shift: none · slots: {{victim}}, {{stage_name}}
> {{stage_name}}. Twenty seasons on the bill. Top of the poster in six languages. And the finale — the *actual* finale — happened offstage, in the dark, where no act worth the name would ever agree to die.

**co-d-5** · pour · shift: none · slots: {{victim}}, {{evidence}}
> They found {{victim}} beside {{evidence}}. The troupe went quiet, wagon by wagon — and friends, a circus going quiet is the loudest sound I know.

**co-d-6** · pour · shift: jubilant · slots: {{victim}}
> {{victim}} deserved a closing night with flowers. They got this instead — and I intend to take it personally. So! The ring is open, detectives. One last show, and the finale is *the truth*.

## 3. Beat Turns (18)

### Jubilant (6)

**bt-j-1** · scene · shift: ominous · slots: {{location}}
> The ring is yours, detectives! {{location}} stands exactly as it was found — sawdust, shadow, and one detail I shall not point at, because finding it is *your* act.

**bt-j-2** · grill · shift: grave · slots: none
> And now — the center ring! One chair. One lamp. One performer at a time, and every one of them about to give the performance of their life. Some, I suspect, are rather better rehearsed than others.

**bt-j-3** · grill · shift: none · slots: {{suspect}}, {{stage_name}}
> Presenting — {{stage_name}}! Known offstage as {{suspect}}, and known to this couch as *not yet cleared*. The chair is warm. The lamp is lit. Begin.

**bt-j-4** · twist · shift: grave · slots: none
> Every good show keeps one trick behind the curtain — the one the program doesn't list. Friends, we have arrived at that trick. May I have a drumroll. May I have *silence* instead. Even better.

**bt-j-5** · last-call · shift: ominous · slots: none
> Final act, detectives! The lamps burn low, the questions run short, and somewhere under this canvas a killer is counting the minutes and finding — to their delight — very few left.

**bt-j-6** · scene · shift: none · slots: {{evidence}}
> The ring has produced {{evidence}} — unbilled, unannounced, and entirely off-program. In this business we call that an *audience plant*. The question, as ever: whose?

### Grave (6)

**bt-g-1** · grill · shift: jubilant · slots: {{victim}}
> Someone under this tent watched {{victim}} fall and then walked back into the lamplight and smiled for the company. That smile is still here. It is wearing greasepaint, and it is very, very good.

**bt-g-2** · twist · shift: none · slots: {{callback}}
> Everything this case rests on — everything — stands upon {{callback}}. I have walked past it all evening the way one walks past a guy-rope in the dark. Time to trip on it together.

**bt-g-3** · last-call · shift: none · slots: none
> A circus folds its tent and the field forgets it by spring. The truth is not like that. The truth stakes in deep, friends. You have one night to pull it up whole.

**bt-g-4** · scene · shift: wondering · slots: {{victim}}, {{location}}
> {{victim}} crossed {{location}} four times tonight. The sawdust remembers every crossing — in this trade, the ground is the only witness that never joined the act.

**bt-g-5** · grill · shift: jubilant · slots: {{suspect}}
> {{suspect}} learned their trade the way everyone here did: repetition, in the dark, until the trick looks like truth. Bear that in mind, detectives, with every answer. It's a *trained* room.

**bt-g-6** · truth · shift: none · slots: none
> Houselights down. Ring lights up. What happens next has no encore.

### Wondering (6)

**bt-w-1** · scene · shift: ominous · slots: {{evidence}}
> {{evidence}}. In the wrong wagon. In this company, friends, nothing travels to the wrong wagon by itself — everything under this canvas is *carried*.

**bt-w-2** · grill · shift: none · slots: {{suspect}}, {{time}}
> {{suspect}} keeps circling back to {{time}} — unasked, twice now. A performer repeating a cue is drilling it in. Odd habit, for a moment they claim was unremarkable.

**bt-w-3** · twist · shift: grave · slots: {{callback}}
> I keep shuffling {{callback}} like a fortune deck, and it keeps dealing the same card. In the tent we'd call that a rigged deck. Rigged decks have riggers.

**bt-w-4** · scene · shift: none · slots: {{location}}
> Why {{location}}? The one corner of this ground with no lamplight, no foot traffic, no audience. Unless the absence of audience *was* the staging.

**bt-w-5** · last-call · shift: grave · slots: none
> Curious — every alibi tonight interlocks like a tumbling act. Everyone catching everyone. In my experience, a catch that clean was choreographed.

**bt-w-6** · grill · shift: jubilant · slots: {{suspect}}, {{suspect_2}}
> {{suspect}} and {{suspect_2}} shared a bill for nine seasons and have not shared a glance all night. Under this little canvas, friends, avoidance is an *acrobatic* feat.

## 4. Suspect Stage Stingers (24)

### Dry (8)

**st-d-1** · grill · shift: none · slots: {{suspect}}, {{stage_name}}
> {{stage_name}} would like the couch to know they were on stage at nine. The couch is invited to doubt them. The audience always is. That is why we sell tickets.

**st-d-2** · grill · shift: none · slots: {{suspect}}
> {{suspect}} has performed under six names in four countries. Tonight they will answer under one. We take progress where we find it.

**st-d-3** · grill · shift: none · slots: {{suspect}}, {{time}}
> {{suspect}} is asked where they were at {{time}}. Watch closely, friends — this is a professional. The tell won't be in the face. It's never in the face.

**st-d-4** · grill · shift: none · slots: {{suspect}}
> {{suspect}} would like it known they have nothing to hide. From a troupe whose entire livelihood is misdirection, I pass that along without comment. Almost.

**st-d-5** · grill · shift: none · slots: {{suspect}}, {{stage_name}}
> The chair receives {{stage_name}} — who has chosen, interestingly, to arrive already rehearsing their exit.

**st-d-6** · grill · shift: none · slots: {{suspect}}, {{victim}}
> {{suspect}} and {{victim}} were close as a knife and its target. Professionally speaking. The professional part, tonight, is the question.

**st-d-7** · grill · shift: none · slots: {{suspect}}
> A note on {{suspect}}: in all my seasons, I have never seen them miss a cue, drop a prop, or answer the question they were actually asked. One of those streaks ends tonight.

**st-d-8** · grill · shift: ominous · slots: {{suspect}}
> {{suspect}} takes the chair. Observe, detectives: alone in this company, they have not once asked *who did it*. Performers rehearse the scenes they know are coming.

### Ominous (8)

**st-o-1** · grill · shift: none · slots: {{suspect}}
> Before {{suspect}} answers — listen to the pause. Every act under this canvas is built on timing, and a pause, friends, is timing with something to hide.

**st-o-2** · grill · shift: none · slots: {{suspect}}, {{location}}
> {{suspect}} knows {{location}} blind. Every rope, every stake, every seam in the canvas. Knows where the lamplight ends — to the inch.

**st-o-3** · grill · shift: none · slots: {{suspect}}
> There are two versions of tonight on this bill, and {{suspect}} is billed in both. One of them closes here.

**st-o-4** · grill · shift: none · slots: {{suspect}}, {{victim}}
> The last soul to speak with {{victim}} is under this tent. {{suspect}} would like the spotlight to keep moving. Spotlights, friends, are mine to aim.

**st-o-5** · grill · shift: dry · slots: {{suspect}}, {{evidence}}
> Ask {{suspect}} about {{evidence}}. Then ask again. The first answer is for the crowd. The second — if you hold the lamp steady — is for the record.

**st-o-6** · grill · shift: none · slots: {{suspect}}
> {{suspect}}'s account has one wagon that stays locked. Every account tonight has one. Theirs is the only wagon with fresh tracks to the door.

**st-o-7** · grill · shift: none · slots: {{suspect}}, {{time}}
> Between {{time}} and the shout, eleven minutes went missing under this canvas. {{suspect}} is holding at least four of them — and in this trade we count minutes like coin.

**st-o-8** · grill · shift: none · slots: {{suspect}}
> The lamps gutter when {{suspect}} crosses the ring. Old canvas notices things, friends. I have spent thirty years learning to notice what it notices.

### Delighted-About-Awful (8)

**st-de-1** · grill · shift: grave · slots: {{suspect}}, {{stage_name}}
> Ah — {{stage_name}}! The act I've waited all night to put in this chair, and I am too old to pretend otherwise. Places, everyone. *Places.*

**st-de-2** · grill · shift: none · slots: {{suspect}}, {{callback}}
> {{suspect}}, before you settle: {{callback}}. Was that in the first version of your evening, or the matinee revision? Take your time — the lamp has oil yet.

**st-de-3** · grill · shift: none · slots: {{suspect}}
> {{suspect}} swore they would never sit in that chair. And yet — behold! Seated! I do love this tent. It keeps every promise everyone else breaks.

**st-de-4** · grill · shift: none · slots: {{suspect}}, {{drink}}
> {{suspect}} arrives with a tin cup of {{drink}} and an expression rehearsed in a costume mirror. Detectives, a personal request: ruin the expression. The {{drink}} is blameless.

**st-de-5** · grill · shift: grave · slots: {{suspect}}, {{victim}}
> {{suspect}} once said something to {{victim}} that emptied a dressing tent. I know because I was holding the curtain. Ask me nothing further — ask *them*.

**st-de-6** · grill · shift: none · slots: {{suspect}}
> What I treasure about {{suspect}} — truly — is that when they lie, they *project*. Back row of the bleachers, every syllable. Listen for the volume, friends. Truth mumbles.

**st-de-7** · grill · shift: none · slots: {{suspect}}
> {{suspect}}! Sit, sit. The chair is sturdy, the lamp is kind, and nothing else about the next five minutes will be either. On with the show.

**st-de-8** · grill · shift: none · slots: {{suspect}}, {{evidence}}
> And now {{suspect}}, who has — I'm assured — a *marvelous* explanation for {{evidence}}. Polished. Practiced. Ready for touring. Detectives, you hold the hook. Use it kindly. Or don't.

## 5. Wrong Accusation (10)

D-081 registers. Ringmaster-flavored; the roast plays to the bleachers.

**wa-1** · any · shift: jubilant · register: compassionate · slots: {{detective}}, {{suspect}}
> Detective {{detective}} names {{suspect}} — the tent holds its breath — and no. Not tonight. But you read this ring like a trouper, detective, and the night is not over. Again.

**wa-2** · any · shift: none · register: witty · slots: {{detective}}, {{suspect}}
> {{suspect}}! Called out by Detective {{detective}} with the full confidence of a debut act. Wrong, alas — but delivered *beautifully*. The bleachers felt it. The killer, notably, did not.

**wa-3** · any · shift: none · register: dad-jokey · slots: {{detective}}, {{suspect}}
> No, Detective {{detective}} — {{suspect}} is innocent. You could say the accusation... missed the target. The knife-thrower could not be reached for comment. Moving on!

**wa-4** · any · shift: grave · register: solemn · slots: {{detective}}
> No, detective. And I'll have the tent note: Detective {{detective}} accused with both feet planted and eyes open. That is how it's done, friends. It simply wasn't *who* it was.

**wa-5** · any · shift: none · register: flirty · slots: {{detective}}, {{suspect}}
> Detective {{detective}} — wrong about {{suspect}}, devastating about everything else. If you accuse like that again I shall have to add you to the bill. Top billing. Don't test me.

**wa-6** · any · shift: none · register: absurd · slots: {{detective}}, {{suspect}}
> {{suspect}}?! {{suspect}}, who once wept when the strongman retired his lucky belt?! Detective {{detective}}, I have filed your theory with the elephant. She keeps the ones we cherish.

**wa-7** · any · shift: none · register: unhinged · slots: {{detective}}
> WRONG! *Ha!* — forgive me. Thirty years of drumrolls does things to a person. Detective {{detective}}, the house thanks you: nothing sharpens an audience like a swing and a miss.

**wa-8** · any · shift: jubilant · register: gravitas · slots: {{detective}}, {{suspect}}
> The lamp swings to {{suspect}} — and finds nothing there to hold. Some chairs take a crime and keep it, Detective {{detective}}. This one, tonight, sits empty. The killer watched you aim. Remember that.

**wa-9** · any · shift: none · register: silly · slots: {{detective}}, {{suspect}}
> No! But *style points*, Detective {{detective}} — you pointed with the whole arm, shoulder and all! {{suspect}} may step down and resume being merely alarming, which is their gift.

**wa-10** · any · shift: grave · register: witty · slots: {{detective}}
> A miss, Detective {{detective}} — and misses are not free in this tent. Every one tells the killer precisely how wide the net is. Somewhere in the dark, someone just measured it.

## 6. The Reveal (6)

**rv-1** · truth · shift: jubilant · slots: {{victim}}, {{time}}
> Then houselights — all of them. At {{time}}, {{victim}} was alive and the show was just a show. Everything after was staging: the lamplight, the alibis, the seating in the bleachers. You were an audience, friends. You were *meant* to be.

**rv-2** · truth · shift: jubilant · slots: {{killer}}, {{victim}}
> It was {{killer}}. From the first drumroll it was {{killer}} — through every rehearsed answer, every borrowed alibi, down to the moment {{victim}} finally understood what the rest of the bill had missed for years.

**rv-3** · truth · shift: jubilant · slots: {{killer}}, {{evidence}}
> And here is the part I admire — as one professional of another: {{killer}}'s whole illusion balanced on a single prop. {{evidence}}. Every great trick keeps one flaw, friends. It's how you know it was performed by hand.

**rv-4** · truth · shift: none · slots: {{detective}}, {{callback}}
> Detective {{detective}} — you brushed the curtain at {{callback}}. One more pull and the whole rig would have come down. The tent watched you reach. The tent watched you stop.

**rv-5** · truth · shift: jubilant · slots: {{killer}}
> {{killer}} rehearsed everything. The act, the exit, the encore. But an audience that keeps asking questions, friends — no one rehearses that. You cannot rehearse *you*.

**rv-6** · truth · shift: none · slots: {{victim}}
> Whatever the morning does with this troupe — {{victim}} was owed one last turn in the light, spoken true, under their real name. The debt is paid. The ring is closed.

## 7. The Wink (6)

**wk-1** · grill · shift: none · slots: none
> You, out there — yes, past the lamplight, on the couch. Best seats I've ever sold, and I never sold them. Well. Suspect?

**wk-2** · scene · shift: none · slots: none
> Between us — and the tent keeps secrets, it's mostly canvas and discretion — you're sharper than my usual crowd. I say that every night. Tonight it happens to be true.

**wk-3** · twist · shift: none · slots: none
> Comfortable out there? Good. The next part of the program was arranged with your couch specifically in mind. We aim to please. We *aim*, at any rate.

**wk-4** · grill · shift: none · slots: {{drink}}
> If anyone beyond the lights is holding a {{drink}} — raise it. To you, dear audience. The suspects can hold; good company cannot.

**wk-5** · last-call · shift: grave · slots: none
> I can feel a couch lean forward from a hundred paces — thirty years under canvas teaches you the sound. It's my favorite sound. Savor the lean, friends. The next act is heavier.

**wk-6** · pour · shift: none · slots: none
> One note from your Ringmaster, before the program resumes: I have run ten thousand shows, and the part where you arrive — sit down, get suspicious — is still the act I'd pay to see.

---

## Coverage vs. the-host.md §5 Minimum

| Section | Minimum | Authored |
| --- | --- | --- |
| Cold open jubilant | 8 | 8 |
| Cold open drop | 6 | 6 |
| Beat turns | 18 | 18 |
| Stage stingers | 24 | 24 |
| Wrong accusation | 6 | 10 |
| Reveal | 6 | 6 |
| Wink | 6 | 6 |
| **Total** | **~74** | **78** |

## Review Notes for the Founder

- New slot: `{{stage_name}}` (playbill title from the cast rail —
  public data). Wrapper-specific slots are now a pattern; the runtime
  slot whitelist should be per-wrapper.
- Vesper here claims a thirty-year Ringmaster history ("thirty years
  under canvas") — same diegetic-presence question flagged on the
  Séance library (st-de-5). One answer should govern both.
- wa-6 (the elephant) is the calibration probe for absurd in this
  wrapper; wa-7's drumroll break is the unhinged probe.
- The address "friends" is used as this wrapper's audience-handle
  (Séance uses "detectives"). Intentional register separation —
  confirm you like per-wrapper addresses, or flatten to "detectives"
  everywhere.
