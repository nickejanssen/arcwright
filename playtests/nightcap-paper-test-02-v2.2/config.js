/* global window */
window.NIGHTCAP_PLAYTEST = {
  version: 'nightcap-paper-test-02-v2.2',
  fixtureStatus: 'NON-CANON TEST FIXTURE',
  title: 'Nightcap',
  subtitle: 'Paper Test #2 v2.2',
  notice: 'This is an early Nightcap game prototype. Your gameplay choices and feedback will be recorded to help improve the game. We do not ask for your name or email.',
  feedback: {
    url: 'https://form.jotform.com/262397917027062',
    // Jotform URL-prefill keys are configured here, not in runtime logic.
    // Verify these Unique Names once in Jotform before the first research run.
    prefillMap: {
      prototype_version: 'prototypeVersion', run_id: 'runId', started_at: 'startedAt', completed_at: 'completedAt',
      duration_seconds: 'durationSeconds', action_sequence: 'actionSequence', investigation_branches: 'investigationBranches',
      discoveries: 'discoveries', pulse_result: 'pulseResult', case_commitment: 'caseCommitment',
      final_next_interest: 'finalNextInterest', device_class: 'deviceClass', browser_class: 'browserClass', completion_status: 'completionStatus'
    }
  },
  intro: {
    eyebrow: 'THE ROOM WITH NO DOOR',
    body: [
      'Rain needles the windows of Vesper House, a restored seaside hotel hosting an invitation-only preview dinner.',
      'At 10:18 PM, the lights flicker. A waiter opens the library and finds architect Adrian Wren dead beside an overturned chair. The windows are latched. The only visible door was watched from the dinner table.',
      'Near Adrian’s hand: a broken brass cufflink shaped like a fox. Nobody admits entering the room.'
    ],
    suspects: ['Celia March — business partner', 'Jonas Reed — restoration contractor', 'Mae Bell — estranged sister']
  },
  investigations: [
    { id:'bookcase', label:'Examine the bookcase', branch:'library', discovery:'Hidden bookcase catch', text:'Fresh scrape marks score the floor. Behind decorative books, you find a narrow brass catch. The “sealed” library may have another way in or out.' },
    { id:'cufflink', label:'Inspect the fox cufflink', branch:'library', discovery:'Blue paint on fox cufflink', text:'Dried deep-blue paint is caught in the hinge. Adrian’s clothing uses neither blue enamel nor blue thread.' },
    { id:'corridor', label:'Trace movement through the house', branch:'movement', discovery:'Hidden restoration corridor', text:'Temporary paneling conceals a restoration corridor connecting the library bookcase to the west service stairs.' },
    { id:'footprints', label:'Follow the wet footprints', branch:'movement', discovery:'Damaged-heel wet footprints', text:'Two partial wet prints mark the west service stairs. One heel has a distinctive missing corner.' },
    { id:'jonas', label:'Press Jonas Reed', branch:'guest statements', discovery:'Jonas claims west service door was locked', text:'“I went outside at ten-oh-five to take a call. I came back through the front entrance. The west service door was locked tonight.”' },
    { id:'celia', label:'Press Celia March', branch:'guest statements', discovery:'Celia links fox symbol to Jonas', text:'“Foxes were Jonas’s little branding gimmick. He put them on half the restoration materials.”' },
    { id:'mae', label:'Press Mae Bell', branch:'guest statements', discovery:'Mae admits argument with Adrian', text:'“I argued with Adrian before dinner. Then I spent ten minutes downstairs trying not to murder him. Irony noted.”' }
  ],
  reaction: {
    title:'A chance to make the information bite',
    body:'You can spend one moment testing something you discovered. This interaction is fixture-only; it is not a locked Nightcap mechanic.',
    options:[
      {label:'Show Jonas the blue-painted cufflink', requiresAny:['cufflink'], result:'Jonas glances at it too quickly, then says the fox symbol proves nothing. His response changes, but the game does not tell you what it means.'},
      {label:'Challenge the “sealed room” story in front of the guests', requiresAny:['bookcase','corridor'], result:'The room goes quiet. Celia immediately asks who knew about the corridor. Jonas says every contractor did.'},
      {label:'Ask Jonas about the damaged-heel footprint', requiresAny:['footprints'], result:'Jonas says damaged work boots are hardly unusual on a restoration site. The answer does not settle whether the print is his.'},
      {label:'Keep what you found private', result:'You keep your discoveries to yourself. The others continue arguing from what they already know.'}
    ]
  },
  pulse: {
    title:'HOTEL PANIC',
    body:'The fire alarm chirps once and dies. A burst pipe floods the west hallway. Staff rush to move guests while restoration materials are dragged out of the way.',
    prompt:'You get one quick grab before the hallway is cleared. What do you secure?',
    options:[
      {label:'Photograph the damaged-heel footprint', requiresAny:['footprints'], result:'You preserve a clear image of the footprint before water reaches it.'},
      {label:'Secure the blue-painted cufflink', requiresAny:['cufflink'], result:'You keep the cufflink from being misplaced during the scramble.'},
      {label:'Keep the hidden corridor accessible', requiresAny:['bookcase','corridor'], result:'You stop staff from sealing the concealed route behind the materials they are moving.'},
      {label:'Stay with the guests', result:'You skip the evidence scramble and keep your attention on the room. No new fact is awarded.'}
    ],
    disclaimer:'NON-CANON pulse: this exists only to exercise the party/minigame transition and consequence slot.'
  },
  commitments: {
    suspects:['Celia','Jonas','Mae','Not enough yet'],
    next:['Hidden route','Physical trace','Guest statements','Motive']
  }
};
