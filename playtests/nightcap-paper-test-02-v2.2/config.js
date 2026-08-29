/* global window */
window.NIGHTCAP_PLAYTEST = {
  version: 'nightcap-paper-test-02-v2.2',
  fixtureStatus: 'NON-CANON TEST FIXTURE',
  title: 'Nightcap',
  subtitle: 'Paper Test #2 v2.2 · The Last Toast',
  notice: 'This is an early Nightcap game prototype. Your gameplay choices and feedback will be recorded to help improve the game. We do not ask for your name or email.',
  feedback: {
    url: 'https://form.jotform.com/262397917027062',
    prefillMap: {
      prototype_version: 'q13_textbox11', run_id: 'q14_textbox12', started_at: 'q15_textbox13', completed_at: 'q16_textbox14',
      duration_seconds: 'q17_textbox15', action_sequence: 'q18_textbox16', investigation_branches: 'q19_textbox17',
      discoveries: 'q20_textbox18', pulse_result: 'q21_textbox19', case_commitment: 'q22_textbox20',
      final_next_interest: 'q23_textbox21', device_class: 'q24_textbox22', browser_class: 'q25_textbox23', completion_status: 'q26_textbox24',
      time_to_first_investigation_seconds: 'q28_time_to_first_investigation_seconds', major_investigations: 'q29_major_investigations',
      event_sequence: 'q30_event_sequence', abandonment_point: 'q31_abandonment_point'
    }
  },
  opening: {
    eyebrow: 'THE LAST TOAST',
    beats: [
      'The Halcyon Club has been closed for eleven years, which is apparently the exact amount of time required for rich people to miss a building they once complained about.',
      'Tonight owner Sebastian Vale is reopening it with four people who all have reasons to smile carefully.',
      'Mara Voss, his business partner, slips a folded document into her bag the instant Sebastian notices it. Theo Bell, Sebastian’s physician and oldest friend, watches Sebastian reach for a silver medication case and quietly says, “Not yet.”',
      'Celeste Vale, Sebastian’s estranged daughter, appears from the private corridor despite telling everyone she has only just arrived. Restoration director Julian Cross snaps at a waiter who nearly moves a plaster-dusted cart parked beside Sebastian’s office door.',
      'Then Sebastian raises a champagne coupe. “To the Halcyon. And to one partnership that will not survive dessert.” He drinks. Thirty seconds later, the glass hits the floor before he does.'
    ],
    suspects: [
      {name:'Mara Voss', role:'Business partner', detail:'Sebastian was preparing to force her out. She handled the champagne and hid a document.'},
      {name:'Dr. Theo Bell', role:'Physician and old friend', detail:'He knew Sebastian’s medication, changed the prescription recently, and looked worried before the toast.'},
      {name:'Celeste Vale', role:'Estranged daughter', detail:'She argued with Sebastian, knows his routines, and lied about when she arrived.'},
      {name:'Julian Cross', role:'Restoration director', detail:'Sebastian had been auditing his project. His cart blocked the office corridor shortly before the toast.'}
    ],
    observations: [
      {id:'mara_document', label:'Mara hiding the folded document', branch:'motive', discovery:'Mara hid acquisition papers from Sebastian', text:'Mara does not bother denying it. The document is a draft acquisition agreement with Sebastian’s signature line blank and several numbers overwritten by hand. “He was going to ruin me publicly at dessert,” she says. Then, almost as an afterthought: “But I poured from the same bottle as everyone else.”', unlocks:['champagne','mara_records']},
      {id:'theo_case', label:'Theo watching the silver medication case', branch:'mechanism', discovery:'Theo recently changed Sebastian’s prescription', text:'Theo admits he adjusted Sebastian’s evening prescription three days ago. The new tablets are scored with a single deep line. “He was meant to take one after dinner. Not before the toast.” He wants the silver case found before anyone starts calling champagne poison.', unlocks:['medication_inventory','theo_followup']},
      {id:'celeste_corridor', label:'Celeste emerging from the private corridor', branch:'movement', discovery:'Celeste used the private corridor before the toast', text:'Celeste’s “just arrived” story lasts twelve seconds. She came early to retrieve letters from her late mother that Sebastian kept in his office. She says the corridor was empty when she entered, but a restoration cart blocked part of her view when she left.', unlocks:['office_route','letters']},
      {id:'julian_cart', label:'Julian guarding the restoration cart', branch:'access', discovery:'Fresh plaster grit lies inside Sebastian’s office threshold', text:'The cart carries wall compound, brass fittings, and a ring of temporary access tags. Fresh white grit continues from one wheel to the carpet just inside Sebastian’s office. Julian says the cart never crossed the threshold.', unlocks:['office_route','key_log']}
    ]
  },
  followups: [
    {id:'champagne', label:'Inspect Sebastian’s glass and the shared bottle', branch:'mechanism', discovery:'Sebastian drank from the same bottle as three other guests', text:'The bottle was opened in front of the room. Mara poured five coupes from it. Three other people drank before Sebastian collapsed and none are ill. His glass smells only of champagne and expensive optimism.'},
    {id:'mara_records', label:'Press Mara on the altered acquisition papers', branch:'motive', discovery:'Mara forged valuation figures to hide a failing deal', text:'Mara admits she changed valuation figures before Sebastian could show them to the board. It gives her a powerful reason to fear dessert, but the timestamps show she was on a video call with counsel while Sebastian’s office corridor was blocked.'},
    {id:'medication_inventory', label:'Find Sebastian’s medication inventory', branch:'mechanism', discovery:'The prescribed evening tablet should carry one deep score line', text:'A concierge log records the medication delivered that afternoon: small white tablets, each with one deep score line. The silver case itself is not with the body.'},
    {id:'theo_followup', label:'Make Theo explain the prescription change', branch:'statements', discovery:'Theo expected Sebastian’s symptoms only if the wrong dose was taken', text:'Theo refuses to diagnose a corpse from across a ballroom, but he is precise about one thing: Sebastian’s collapse fits an excessive dose better than a sip of champagne. He looks furious at himself for saying it aloud.'},
    {id:'office_route', label:'Trace the private office route', branch:'access', discovery:'The private office can be reached unseen from the restoration corridor', text:'The corridor bends behind temporary acoustic panels before reaching Sebastian’s office. From the dining room, anyone beside the restoration cart would disappear from sight for roughly a minute.'},
    {id:'letters', label:'Verify Celeste’s story about the letters', branch:'motive', discovery:'Celeste retrieved letters proving Sebastian lied about her mother', text:'The letters are real, ugly, and irrelevant to pharmaceuticals. Celeste had every reason to rage at Sebastian. One envelope is time-stamped by the club scanner six minutes before Julian says he parked his cart in the corridor.'},
    {id:'key_log', label:'Check the temporary restoration access tags', branch:'access', discovery:'Julian signed out the only temporary office access tag', text:'The restoration log shows one temporary tag capable of opening Sebastian’s office. Julian signed it out at 6:10 PM and has not signed it back in. He says he never used it tonight.'},
    {id:'waiter_timing', label:'Ask the waiter when the cart moved', branch:'movement', discovery:'Julian was alone beside the office for about a minute', text:'The waiter remembers Julian refusing help with the cart, then vanishing behind it while the staff reset dessert service. “Maybe a minute. Long enough to make me wonder whether plaster has become private.”'},
    {id:'celeste_glimpse', label:'Ask Celeste what she saw leaving the corridor', branch:'movement', discovery:'Celeste saw a man in a dark restoration jacket leaving the office side', text:'Celeste would not swear to a face. She remembers a dark restoration jacket and someone turning away as she came through. Julian is wearing one. So are two staff members still downstairs.'},
    {id:'julian_statement', label:'Pin Julian down on his movements', branch:'statements', discovery:'Julian says he never entered Sebastian’s office tonight', text:'Julian is admirably specific: “I never entered Sebastian’s office tonight. Not once. I was in the ballroom or the service hall the entire time.” He offers the sentence like a receipt.'},
    {id:'julian_private', label:'Use saved pressure: privately press Julian about his access tag', branch:'statements', discovery:'Julian claims the office access tag never left his belt all night', text:'Away from Rhea, Julian lowers his voice. “The temporary office tag stayed clipped to my belt all night. I never handed it off, never used it, never lost it.” He has now made his access story more specific, not less.'},
    {id:'staff_inventory', label:'Ask staff what was removed from Sebastian’s effects', branch:'mechanism', discovery:'Staff found the silver medication case under Sebastian’s chair', text:'A server found the silver case beneath Sebastian’s chair after the collapse. One tablet inside has two shallow score marks instead of the single deep line recorded in the delivery log.'}
  ],
  rival: {
    name:'Rhea Pike',
    intro:'Rhea Pike is the other investigator. She has the unnerving confidence of someone who has never once mistaken volume for uncertainty.',
    priorities:['key_log','medication_inventory','office_route','waiter_timing','mara_records'],
    reactions:{
      julian_cart:'Rhea watches you inspect Julian’s cart, then immediately turns toward the office corridor. She noticed what interested you.',
      theo_case:'Rhea sees Theo bristle at your questions and starts asking staff where Sebastian kept personal effects.',
      celeste_corridor:'Rhea clocks Celeste’s lie and moves toward the access logs instead of following her.',
      mara_document:'Rhea lets you have Mara. “Financial fraud is either motive or cardio. I’ll check access.”'
    }
  },
  minigame: {
    title:'THE EFFECTS TRAY',
    setup:'A server finds Sebastian’s scattered personal effects just as staff begin clearing the room for police. You and Rhea reach the tray together. First clean observation gets first access.',
    memorize:['Silver medication case','Black fountain pen','Brass room tag','White pocket square'],
    changed:['Silver medication case','Black fountain pen','Halcyon matchbook','White pocket square'],
    correct:'Halcyon matchbook',
    prompt:'One item changed. Which one is new?',
    winDiscovery:'The silver case contains one tablet with two shallow score marks instead of one deep line.',
    loseKnowledge:'Rhea gets the tray first. Her expression changes at the silver case, and she pockets a note before stepping away. You know the discrepancy matters to her, but you do not own whatever proof she saw.'
  },
  leverage: {
    spend:{label:'Spend Leverage: learn what Rhea pursued', result:'Rhea chased {lead}. You learn her direction, not her evidence.'},
    save:{label:'Save Leverage: earn a private suspect follow-up', result:'You keep the pressure for yourself. Your next investigation can privately press Julian about the access tag.'}
  },
  reaction: {
    triggerAny:['staff_inventory','medication_inventory','theo_followup'],
    title:'Theo stops protecting his own reputation',
    text:'Theo finally admits why he was evasive. He changed Sebastian’s prescription after a private medical scare and feared the club would blame him for the death. Then he looks at the tablet description again. “That is not what I dispensed.” Across the room, Julian asks staff to seal the unfinished corridor before police arrive.',
    fallbackTitle:'The corridor suddenly matters to everyone',
    fallbackText:'A club manager announces that police want the unfinished corridor sealed for safety. Julian volunteers to handle it himself. Rhea looks at you, then at the office door. Whatever you were planning to check there now has a clock on it.'
  },
  caseFile: {
    suspects:['Mara Voss','Dr. Theo Bell','Celeste Vale','Julian Cross'],
    mechanism:[
      {label:'Different tablet scoring in the silver case', requiresAny:['minigame_case','staff_inventory']},
      {label:'Delivery log says every prescribed tablet had one deep score line', requiresAny:['medication_inventory']},
      {label:'Theo says the collapse fits an excessive dose better than champagne', requiresAny:['theo_followup']},
      {label:'Shared champagne bottle did not affect the other guests', requiresAny:['champagne']}
    ],
    access:[
      {label:'Julian held the only temporary office access tag', requiresAny:['key_log']},
      {label:'Private restoration corridor allows unseen office access', requiresAny:['office_route']},
      {label:'Waiter places Julian alone beside the office for about a minute', requiresAny:['waiter_timing']},
      {label:'Celeste saw a restoration-jacketed figure leaving the office side', requiresAny:['celeste_glimpse']},
      {label:'Fresh plaster grit crossed the office threshold from Julian’s cart', requiresAny:['julian_cart']}
    ],
    contradictions:[
      {label:'Julian: “I never entered Sebastian’s office tonight.”', requiresAny:['julian_statement']},
      {label:'Julian says the cart never crossed the threshold despite fresh grit inside', requiresAny:['julian_cart']},
      {label:'Julian says his access tag was never used despite signing out the only office tag', requiresAny:['key_log']},
      {label:'Julian says the office tag never left his belt all night', requiresAny:['julian_private']},
      {label:'Mara’s champagne implication fails because others drank from the same bottle', requiresAny:['champagne']}
    ]
  },
  truth: {
    killer:'Julian Cross',
    summary:'Julian used his restoration access to enter Sebastian’s office before the toast and substitute one evening medication dose. He expected Sebastian to take it around the toast and let the champagne absorb suspicion. The case against him is strongest when substitution proof, office opportunity, and his categorical “never entered” story are combined.',
    note:'This reveal belongs after baseline survey responses so correctness does not contaminate fun/detective ratings.'
  }
};
