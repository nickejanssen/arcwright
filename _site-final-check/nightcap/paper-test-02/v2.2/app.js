/* global window, document, sessionStorage, navigator, innerWidth, URLSearchParams */
import {createSession,recordAction,recordEvent,recordMajorInvestigation,completeSession,serializeTelemetry,buildFeedbackUrl,detectEnvironment,filterEligibleOptions} from './runtime.js';

const cfg=window.NIGHTCAP_PLAYTEST;
const app=document.querySelector('#app');
const notebook=document.querySelector('#notebook');
const notes=document.querySelector('#notes');
const KEY=`nightcap:${cfg.version}:session`;
let s=load();

document.querySelector('#version').textContent='v2.2';

function load(){
  try{
    const parsed=JSON.parse(sessionStorage.getItem(KEY));
    return parsed?.prototypeVersion===cfg.version?hydrate(parsed):createSession(cfg.version);
  }catch{return createSession(cfg.version)}
}
function hydrate(x){
  return Object.assign(createSession(cfg.version,x.startedAt),x,{
    events:x.events||[],majorInvestigations:x.majorInvestigations||[],majorCount:x.majorCount||0,earned:x.earned||[],
    caseDraft:x.caseDraft||{killer:'',mechanism:'',access:'',contradiction:''}
  });
}
function save(){sessionStorage.setItem(KEY,JSON.stringify(s));renderNotes()}
function restart(){sessionStorage.removeItem(KEY);s=createSession(cfg.version);save();welcome()}
function escapeHtml(v){return String(v).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
function panel(inner,{exit=true}={}){
  app.innerHTML=`<div class="panel">${inner}${exit?'<div class="exit"><button id="exit-early">End test early & give feedback</button></div>':''}</div>`;
  document.querySelector('#exit-early')?.addEventListener('click',()=>feedback('abandoned'));
}
function progress(label){return `<div class="phase"><span>${escapeHtml(label)}</span><small>${s.majorCount}/5 investigations</small></div>`}
function renderNotes(){
  if(!s.discoveries.length){notebook.classList.add('hidden');return}
  notebook.classList.remove('hidden');
  notes.innerHTML=s.discoveries.map(x=>`<div class="note">${escapeHtml(x)}</div>`).join('');
}
function go(step){s.currentStep=step;save();renderStep()}
function addEarned(id){if(id&&!s.earned.includes(id))s.earned.push(id)}
function allInvestigations(){return [...cfg.opening.observations,...cfg.followups]}
function findLead(id){return allInvestigations().find(x=>x.id===id)}
function hasEvent(prefix){return s.events.some(x=>x===prefix||x.startsWith(`${prefix}:`))}
function ensureEvent(name,detail=''){if(!hasEvent(name))recordEvent(s,name,detail)}
function evidenceList(entries){
  const available=filterEligibleOptions(entries,s.earned);
  return available.length?available:[{label:'I do not have enough owned proof for this yet'}];
}
function neutralize(leads){return [...leads].sort((a,b)=>a.label.localeCompare(b.label))}

function welcome(){
  notebook.classList.add('hidden');
  panel(`<span class="fixture-tag">${cfg.fixtureStatus}</span><h1>${cfg.title}</h1><p class="muted">${cfg.subtitle}</p><p class="notice">${cfg.notice}</p><p class="muted">The feedback service may retain normal technical metadata such as an IP address even though this test does not ask who you are.</p><div class="actions"><button class="primary" id="start">Enter the Halcyon</button></div>`,{exit:false});
  document.querySelector('#start').onclick=()=>{s=createSession(cfg.version);recordEvent(s,'test_started');go('opening')};
}

function opening(){
  panel(`${progress('WATCH')}<div class="eyebrow">${cfg.opening.eyebrow}</div>${cfg.opening.beats.map((p,i)=>i===4?`<div class="cinematic-impact">${escapeHtml(p)}</div>`:`<p>${escapeHtml(p)}</p>`).join('')}<div class="cast-grid">${cfg.opening.suspects.map(x=>`<div class="card"><strong>${escapeHtml(x.name)}</strong><small>${escapeHtml(x.role)}</small><p>${escapeHtml(x.detail)}</p></div>`).join('')}</div><p class="notice"><strong>Nobody has called it yet.</strong> You saw four things before Sebastian fell. Start with the one that bothered you.</p><div class="actions"><button class="primary" id="notice">Follow what you noticed</button></div>`);
  document.querySelector('#notice').onclick=()=>{ensureEvent('opening_completed');go('investigation_1')};
}

function chooseOpeningObservation(){
  const available=neutralize(cfg.opening.observations.filter(x=>!s.earned.includes(x.id)));
  panel(`${progress('HUNT')}<div class="eyebrow">FIRST INSTINCT</div><h2>What was weird?</h2><p class="muted">Choose the thing you actually want to check. The game will not tell you which one matters.</p><div class="choice-grid">${available.map(x=>`<button data-lead="${x.id}">${escapeHtml(x.label)}</button>`).join('')}</div>`);
  app.querySelectorAll('[data-lead]').forEach(b=>b.onclick=()=>resolveMajor(findLead(b.dataset.lead),'investigation_2'));
}

function investigationTwo(){
  const unlocked=new Set();
  cfg.opening.observations.filter(x=>s.earned.includes(x.id)).forEach(x=>(x.unlocks||[]).forEach(id=>unlocked.add(id)));
  const leads=neutralize(cfg.followups.filter(x=>unlocked.has(x.id)&&!s.earned.includes(x.id)));
  chooseLead('THE QUESTION IT CREATED','Your first look changed the shape of the room. What do you follow now?',leads,'rival');
}

function resolveMajor(item,nextStep){
  if(!item||s.earned.includes(item.id))return;
  s.majorCount+=1;
  addEarned(item.id);
  recordMajorInvestigation(s,item.id);
  recordAction(s,{label:item.label,branch:item.branch,discovery:item.discovery});
  recordEvent(s,`investigation_${s.majorCount}`,item.id);
  s.lastLeadId=item.id;
  s.nextStep=nextStep;
  s.currentStep='discovery';
  save();
  discoveryScreen();
}
function discoveryScreen(){
  const item=findLead(s.lastLeadId);
  if(!item){go(s.nextStep||'investigation_2');return}
  panel(`${progress('DISCOVERY')}<div class="eyebrow">YOU FOUND SOMETHING</div><h2>${escapeHtml(item.label)}</h2><p>${escapeHtml(item.text)}</p><div class="discovery"><strong>Your notes now include</strong><br>${escapeHtml(item.discovery)}</div><p class="muted">No conclusion has been added. What this means is yours to decide.</p><div class="actions"><button class="primary" id="continue">Follow the case</button></div>`);
  document.querySelector('#continue').onclick=()=>go(s.nextStep||'investigation_2');
}

function chooseLead(eyebrow,body,leads,nextStep){
  const unique=[];const seen=new Set();
  neutralize(leads).forEach(x=>{if(x&&!seen.has(x.id)&&!s.earned.includes(x.id)){seen.add(x.id);unique.push(x)}});
  panel(`${progress('HUNT')}<div class="eyebrow">${escapeHtml(eyebrow)}</div><h2>What do you do?</h2><p>${escapeHtml(body)}</p><div class="live-leads"><span>LIVE LEADS</span><small>Not ranked. Not all are equally useful.</small></div><div class="choice-grid">${unique.map(x=>`<button data-lead="${x.id}">${escapeHtml(x.label)}</button>`).join('')}</div>`);
  app.querySelectorAll('[data-lead]').forEach(b=>b.onclick=()=>resolveMajor(findLead(b.dataset.lead),nextStep));
}

function rivalInterruption(){
  if(!s.rivalLead)s.rivalLead=cfg.rival.priorities.find(id=>!s.earned.includes(id))||'waiter_timing';
  const first=s.majorInvestigations[0];
  const reaction=cfg.rival.reactions[first]||'Rhea studies the room, then takes a lead you left open.';
  if(!hasEvent('rival_pursued')){
    recordEvent(s,'rival_pursued',s.rivalLead);
    recordAction(s,{label:`Rhea pursued: ${findLead(s.rivalLead)?.label||s.rivalLead}`,branch:'rival pressure'});
    save();
  }
  panel(`${progress('PLAY')}<div class="rival"><div class="eyebrow">RHEA PIKE IS MOVING</div><h2>You are not investigating alone.</h2><p>${escapeHtml(cfg.rival.intro)}</p><p>${escapeHtml(reaction)}</p><p><strong>While you were working, Rhea pursued another live lead.</strong> You do not know what she found.</p></div><div class="actions"><button class="primary" id="next">Something interrupts both of you</button></div>`);
  document.querySelector('#next').onclick=()=>go('minigame_setup');
}

function minigameSetup(){
  panel(`${progress('PLAY')}<div class="eyebrow">${escapeHtml(cfg.minigame.title)}</div><h2>First access is up for grabs.</h2><p>${escapeHtml(cfg.minigame.setup)}</p><div class="object-tray">${cfg.minigame.memorize.map(x=>`<div>${escapeHtml(x)}</div>`).join('')}</div><p class="muted">Take a moment. When you are ready, the tray changes.</p><div class="actions"><button class="primary" id="ready">I’ve got it</button></div>`);
  document.querySelector('#ready').onclick=()=>go('minigame_question');
}
function minigameQuestion(){
  panel(`${progress('PLAY')}<div class="eyebrow">THE TRAY CHANGED</div><h2>${escapeHtml(cfg.minigame.prompt)}</h2><div class="choice-grid two">${cfg.minigame.changed.map(x=>`<button data-object="${escapeHtml(x)}">${escapeHtml(x)}</button>`).join('')}</div>`);
  app.querySelectorAll('[data-object]').forEach(b=>b.onclick=()=>resolveMinigame(b.dataset.object));
}
function resolveMinigame(choice){
  if(s.minigameOutcome){go('minigame_result');return}
  const won=choice===cfg.minigame.correct;
  s.minigameOutcome=won?'win':'loss';s.pulseResult=s.minigameOutcome;s.firstAccess=won?'player':'rhea';
  recordEvent(s,'minigame_result',s.minigameOutcome);
  recordAction(s,{label:`Effects Tray: ${s.minigameOutcome}`,branch:'competitive pulse'});
  if(won){addEarned('minigame_case');if(!s.discoveries.includes(cfg.minigame.winDiscovery))s.discoveries.push(cfg.minigame.winDiscovery)}
  go('minigame_result');
}
function minigameResult(){
  const won=s.minigameOutcome==='win';
  const body=won
    ? `<p><strong>You get the tray first.</strong></p><p>${escapeHtml(cfg.minigame.winDiscovery)}</p><div class="discovery"><strong>Owned proof</strong><br>${escapeHtml(cfg.minigame.winDiscovery)}</div>`
    : `<p><strong>Rhea gets first access.</strong></p><p>${escapeHtml(cfg.minigame.loseKnowledge)}</p><div class="knowledge"><strong>Knowledge, not owned proof</strong><br>You saw Rhea react to the medication case. Her evidence is still hers.</div>`;
  panel(`${progress('REACT')}<div class="eyebrow">CONSEQUENCE</div><h2>${won?'You beat Rhea to it.':'Rhea beats you to it.'}</h2>${body}<p class="muted">The opportunity moved. The murder did not become more or less solvable.</p><div class="actions"><button class="primary" id="leverage">Decide what to do with Rhea</button></div>`);
  document.querySelector('#leverage').onclick=()=>go('leverage');
}

function leverage(){
  panel(`${progress('REACT')}<div class="eyebrow">ONE PIECE OF LEVERAGE</div><h2>Information has a cost.</h2><p>You can spend your one competitive advantage to learn where Rhea went, or keep it and use that pressure for a sharper private follow-up.</p><div class="choice-grid"><button data-lev="spend">${escapeHtml(cfg.leverage.spend.label)}</button><button data-lev="save">${escapeHtml(cfg.leverage.save.label)}</button></div>`);
  app.querySelectorAll('[data-lev]').forEach(b=>b.onclick=()=>resolveLeverage(b.dataset.lev));
}
function resolveLeverage(kind){
  if(hasEvent('leverage')){go('leverage_result');return}
  s.leverageUsed=kind==='spend';
  if(s.leverageUsed){s.leverageResult=`spent:${s.rivalLead}`;recordEvent(s,'leverage','used')}
  else{s.leverageResult='saved';recordEvent(s,'leverage','saved')}
  recordAction(s,{label:`Leverage: ${kind}`,branch:'information warfare'});
  go('leverage_result');
}
function leverageResult(){
  const spent=s.leverageUsed;
  const lead=findLead(s.rivalLead);
  const text=spent?cfg.leverage.spend.result.replace('{lead}',lead?.label||'a live lead'):cfg.leverage.save.result;
  panel(`${progress('REACT')}<div class="eyebrow">INFORMATION WARFARE</div><h2>${spent?'You peek at Rhea’s direction.':'You keep the pressure.'}</h2><p>${escapeHtml(text)}</p><p class="muted">${spent?'Rhea’s evidence does not become yours just because you know where she looked.':'You traded competitive intelligence for a private investigative opportunity.'}</p><div class="actions"><button class="primary" id="hunt">Back to the murder</button></div>`);
  document.querySelector('#hunt').onclick=()=>go('investigation_3');
}

function leadPool(stage){
  const ids=stage===3
    ? (s.leverageUsed?['staff_inventory','key_log','waiter_timing','office_route','theo_followup','champagne']:['julian_private','staff_inventory','key_log','waiter_timing','theo_followup','champagne'])
    : stage===4
      ? ['medication_inventory','theo_followup','office_route','key_log','waiter_timing','celeste_glimpse','julian_statement','champagne','mara_records','letters','staff_inventory']
      : ['julian_statement','staff_inventory','waiter_timing','celeste_glimpse','key_log','champagne','theo_followup','office_route','mara_records','letters','medication_inventory'];
  return ids.map(findLead).filter(Boolean).filter(x=>!s.earned.includes(x.id)).slice(0,7);
}
function investigationThree(){chooseLead('BACK TO THE MURDER','Rhea changed the competitive state, not the facts. Which live thread do you pursue now?',leadPool(3),'story_reaction')}
function storyReaction(){
  const medication=cfg.reaction.triggerAny.some(id=>s.earned.includes(id))||s.earned.includes('minigame_case');
  ensureEvent('story_reaction',medication?'medication':'corridor');save();
  const title=medication?cfg.reaction.title:cfg.reaction.fallbackTitle;
  const text=medication?cfg.reaction.text:cfg.reaction.fallbackText;
  panel(`${progress('REACT → HUNT')}<div class="eyebrow">THE ROOM CHANGES</div><h2>${escapeHtml(title)}</h2><p>${escapeHtml(text)}</p><p class="notice">Something that was background a minute ago is now a live decision.</p><div class="actions"><button class="primary" id="act">Act on it</button></div>`);
  document.querySelector('#act').onclick=()=>go('investigation_4');
}
function investigationFour(){chooseLead('TEST THE STORY','A claim, route, object, or person no longer fits comfortably. What do you test?',leadPool(4),'investigation_5')}
function investigationFive(){chooseLead('LAST OPENING','You have time to chase one more thing before everyone has to put their case down.',leadPool(5),'last_call')}

function lastCall(){
  ensureEvent('last_call');save();
  panel(`${progress('LAST CALL')}<div class="eyebrow">LAST CALL</div><h2>Rhea closes her notebook.</h2><p>“I have a case,” she says, which is either useful information or a personality disorder.</p><p>The staff stop answering new questions. What you own is what you can use.</p><div class="owned-summary"><strong>Your owned notes</strong>${s.discoveries.map(x=>`<div>${escapeHtml(x)}</div>`).join('')}</div><div class="actions"><button class="primary" id="case">Build Case File</button></div>`);
  document.querySelector('#case').onclick=()=>go('case_file_1');
}

function caseShell(step,title,body,buttons){
  panel(`${progress('CASE FILE')}<div class="eyebrow">CASE FILE · ${step}/4</div><h2>${escapeHtml(title)}</h2><p class="muted">${escapeHtml(body)}</p><div class="choice-grid">${buttons}</div>`);
}
function caseFileKiller(){
  caseShell(1,'Who killed Sebastian?','Commit. No correctness feedback until after the research survey.',cfg.caseFile.suspects.map(x=>`<button data-case="${escapeHtml(x)}">${escapeHtml(x)}</button>`).join(''));
  app.querySelectorAll('[data-case]').forEach(b=>b.onclick=()=>{s.caseDraft.killer=b.dataset.case;save();go('case_file_2')});
}
function caseFileMechanism(){
  const options=evidenceList(cfg.caseFile.mechanism);
  caseShell(2,'What supports the critical act or mechanism?','Only evidence you legitimately acquired is available.',options.map(x=>`<button data-case="${escapeHtml(x.label)}">${escapeHtml(x.label)}</button>`).join(''));
  app.querySelectorAll('[data-case]').forEach(b=>b.onclick=()=>{s.caseDraft.mechanism=b.dataset.case;save();go('case_file_3')});
}
function caseFileAccess(){
  const options=evidenceList(cfg.caseFile.access);
  caseShell(3,'What establishes opportunity or access?','Choose the proof you would actually put in the file.',options.map(x=>`<button data-case="${escapeHtml(x.label)}">${escapeHtml(x.label)}</button>`).join(''));
  app.querySelectorAll('[data-case]').forEach(b=>b.onclick=()=>{s.caseDraft.access=b.dataset.case;save();go('case_file_4')});
}
function caseFileContradiction(){
  const options=evidenceList(cfg.caseFile.contradictions);
  caseShell(4,'Which statement or cover story fails?','This is your last commitment before research.',options.map(x=>`<button data-case="${escapeHtml(x.label)}">${escapeHtml(x.label)}</button>`).join(''));
  app.querySelectorAll('[data-case]').forEach(b=>b.onclick=()=>finishCase(b.dataset.case));
}
function finishCase(contradiction){
  s.caseDraft.contradiction=contradiction;
  s.caseCommitment=`killer=${s.caseDraft.killer} | mechanism=${s.caseDraft.mechanism} | access=${s.caseDraft.access} | failed_claim=${s.caseDraft.contradiction}`;
  s.finalNextInterest='Case File committed';
  recordAction(s,{label:`Case File: ${s.caseCommitment}`,branch:'case file'});
  recordEvent(s,'case_file_committed');
  save();
  feedback('completed');
}

function feedback(status){
  if(s.completionStatus==='in_progress'){
    completeSession(s,new Date().toISOString(),status);
    recordEvent(s,'survey_handoff',status);
  }
  s.currentStep='survey_handoff';
  save();
  surveyHandoff();
}
function surveyHandoff(){
  const env=detectEnvironment(navigator.userAgent,innerWidth);
  const data=serializeTelemetry(s,env);
  const url=buildFeedbackUrl(cfg.feedback.url,data,cfg.feedback.prefillMap);
  notebook.classList.add('hidden');
  panel(`<div class="completion"><div class="eyebrow">POST-PLAY RESEARCH</div><h2>${s.completionStatus==='completed'?'Case locked.':'Run ended.'}</h2><p>The gameplay portion is over. The next screen is the existing research survey.</p><p class="muted">We deliberately have not shown you the answer yet. Your first ratings should reflect the experience you just played, not whether your accusation was correct.</p><div class="actions"><a class="action primary center" href="${escapeHtml(url)}">Give feedback</a><button id="restart">Restart test</button></div></div>`,{exit:false});
  document.querySelector('#restart').onclick=restart;
}

function reveal(){
  notebook.classList.add('hidden');
  panel(`<span class="fixture-tag">${cfg.fixtureStatus}</span><div class="eyebrow">THE TRUTH</div><h1>${escapeHtml(cfg.truth.killer)}</h1><p>${escapeHtml(cfg.truth.summary)}</p><p class="muted">${escapeHtml(cfg.truth.note)}</p><div class="actions"><button class="primary" id="again">Play the test again</button></div>`,{exit:false});
  document.querySelector('#again').onclick=restart;
}

function renderStep(){
  ({
    welcome,opening,investigation_1:chooseOpeningObservation,discovery:discoveryScreen,investigation_2:investigationTwo,rival:rivalInterruption,
    minigame_setup:minigameSetup,minigame_question:minigameQuestion,minigame_result:minigameResult,leverage,leverage_result:leverageResult,
    investigation_3:investigationThree,story_reaction:storyReaction,investigation_4:investigationFour,investigation_5:investigationFive,
    last_call:lastCall,case_file_1:caseFileKiller,case_file_2:caseFileMechanism,case_file_3:caseFileAccess,case_file_4:caseFileContradiction,
    survey_handoff:surveyHandoff
  }[s.currentStep]||welcome)();
}

document.querySelector('#toggle-notes').onclick=()=>{const hidden=notes.classList.toggle('hidden');document.querySelector('#toggle-notes').textContent=hidden?'Show':'Hide'};
renderNotes();
if(new URLSearchParams(window.location.search).get('reveal')==='1')reveal();
else if(s.completionStatus!=='in_progress')surveyHandoff();
else renderStep();
