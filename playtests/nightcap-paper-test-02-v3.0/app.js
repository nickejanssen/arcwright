import {
  acknowledgeLockResult,
  buildSurveyUrl,
  canEnterLastCall,
  chooseInvestigation,
  commitCaseFile,
  completeOpening,
  createInitialState,
  enterLastCall,
  isRevealMode,
  markComplete,
  markRevealReturn,
  markSurveyHandoff,
  openLockWindow,
  persistState,
  recordDiscovery,
  recordInferenceAction,
  releaseCylinderPublicly,
  resolveLock,
  restoreState,
  saveLeverage,
  setCaseFileDraft,
  setLockProgress,
  shouldOpenLockWindow,
  spendLeverage,
  triggerRivalActivity
} from "./runtime.js";

const app = document.querySelector("#app");
const notebook = document.querySelector("#notebook");
const notebookButton = document.querySelector("#notebookButton");
let caseData;
let state;
let lockFrame = null;
let lockInterval = null;
let currentMeterValue = 50;

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
}

function save() {
  persistState(state);
  renderNotebook();
}

function owned(id) {
  return [...state.discoveries, ...state.privateDiscoveries].some((item) => item.id === id);
}

function allEvidence() {
  const seen = new Set();
  return [...state.discoveries, ...state.privateDiscoveries].filter((item) => {
    if (seen.has(item.id)) return false;
    seen.add(item.id);
    return true;
  });
}

function renderNotebook() {
  const facts = allEvidence();
  notebook.innerHTML = `
    <div class="close-row"><h2>Detective notebook</h2><button class="ghost-button" id="closeNotebook" type="button">Close</button></div>
    <p class="small">This remembers what you actually encountered. It does not tell you what matters.</p>
    ${facts.length ? `<ul class="fact-list">${facts.map((item) => `<li class="fact"><strong>${esc(item.label)}</strong><div>${esc(item.fact)}</div><small>${esc(item.source)}${state.privateDiscoveries.some((privateItem) => privateItem.id === item.id) ? " · private for now" : ""}</small></li>`).join("")}</ul>` : `<p class="small">Nothing recorded yet.</p>`}
  `;
  notebook.querySelector("#closeNotebook")?.addEventListener("click", closeNotebook);
}

function openNotebook() {
  notebook.hidden = false;
  notebookButton.setAttribute("aria-expanded", "true");
  renderNotebook();
}
function closeNotebook() {
  notebook.hidden = true;
  notebookButton.setAttribute("aria-expanded", "false");
}
notebookButton.addEventListener("click", () => notebook.hidden ? openNotebook() : closeNotebook());

function meta() {
  return `<div class="meta-row"><span class="pill">Rival: <strong>${esc(caseData.rival.name)}</strong></span><span class="pill">Leverage: <strong>${state.leverage}</strong></span><span class="pill">Moves made: <strong>${state.majorActions}</strong></span></div>`;
}

function renderOpening() {
  app.innerHTML = `
    <section class="card">
      <p class="eyebrow">The Larkspur Hotel · Atlantic coast · 1926</p>
      <div class="story lede">
        <p>The séance is supposed to end with Gideon March embarrassing Lenora Quill before midnight. Gideon, a professional destroyer of fraudulent mediums and other profitable arrangements, has stationed himself somewhere outside the room. In the next room, a tray of untouched oysters is quietly losing its reason to exist.</p>
        <p>At 11:47, Quill raises a brass trumpet from the table. A man's voice comes through it.</p>
        <p><strong>“Mrs. Quill, do carry on. I can hear every word.”</strong></p>
        <p>Everybody recognizes Gideon.</p>
        <p>Quill does not look triumphant. She looks frightened. Clara Hensley, Gideon's secretary, is sitting three places from you. Edwin Rusk leaves the room almost immediately. Beatrice Ashcombe mutters that Gideon has always loved an entrance, particularly when he isn't making one.</p>
        <p>At midnight, Rusk knocks on Gideon's writing-room door.</p>
        <p>There is no answer.</p>
        <p>Gideon March is dead inside.</p>
      </div>
      <div class="notice"><strong>What happened in plain view:</strong> you heard Gideon's voice shortly before his body was found. Quill flinched. Rusk left. Clara was in the room. Beatrice had already threatened Gideon twice.</div>
      <div class="actions"><button class="primary" id="startInvestigation" type="button">Start investigating</button></div>
    </section>`;
  document.querySelector("#startInvestigation").addEventListener("click", () => {
    completeOpening(state);
    save();
    render();
  });
}

function rivalBeatAfterAction() {
  if (state.majorActions === 1) {
    const candidate = ["seance-room", "gideon-materials", "writing-room"].find((id) => !state.investigatedTargets.includes(id)) ?? "edwin-rusk";
    if (triggerRivalActivity(state, "pursued", candidate)) state.ui.notice = `${caseData.rival.name} heads for ${labelForTarget(candidate)} without waiting to see what you found.`;
  } else if (state.majorActions === 2 && state.lock.status === "unavailable") {
    if (triggerRivalActivity(state, "followed", "edwin-rusk")) state.ui.notice = `${caseData.rival.name} notices Rusk checking the service corridor and follows him.`;
  }
}

function labelForTarget(id) {
  const route = caseData.investigation.opening_opportunities.find((item) => item.id === id);
  const suspect = caseData.suspects.find((item) => item.id === id);
  return route?.label ?? suspect?.name ?? id;
}

function addDiscoveries(items, visibility = "public") {
  for (const item of items ?? []) recordDiscovery(state, item, { visibility });
}

function consumeFirstLookTurnIfNeeded() {
  if (state.lock.status === "resolved" && !state.lock.publicReleased) {
    state.lock.postResultActions = (state.lock.postResultActions ?? 0) + 1;
    if (state.lock.postResultActions >= 1) releaseCylinderPublicly(state, caseData);
  }
}

function visitRoute(routeId) {
  if (!chooseInvestigation(state, routeId)) return;
  const route = caseData.investigation.routes[routeId];
  addDiscoveries(route.discoveries);
  state.ui.lastTarget = routeId;
  state.ui.lastScene = route.scene;
  state.ui.peoplePickerOpen = false;
  rivalBeatAfterAction();
  consumeFirstLookTurnIfNeeded();
  save();
  render();
}

function visitInterview(suspectId, isRevisit = false) {
  const interview = caseData.interviews[suspectId];
  if (!isRevisit && !state.investigatedTargets.includes(suspectId)) {
    chooseInvestigation(state, suspectId);
    addDiscoveries(interview.discoveries);
    rivalBeatAfterAction();
    consumeFirstLookTurnIfNeeded();
  }
  state.ui.lastTarget = suspectId;
  state.ui.lastScene = `${interview.opening}\n\n${interview.claim}`;
  state.ui.peoplePickerOpen = false;
  save();
  render();
}

function conditionalAvailable(interview) {
  const conditional = interview.conditional;
  if (!conditional) return false;
  const already = (conditional.discoveries ?? []).every((item) => owned(item.id));
  if (already) return false;
  return (conditional.requires_any ?? []).some((id) => owned(id));
}

function challengeInterview(suspectId) {
  const interview = caseData.interviews[suspectId];
  if (!conditionalAvailable(interview)) return;
  recordInferenceAction(state, suspectId, "challenge-claim", "new-testimony");
  addDiscoveries(interview.conditional.discoveries);
  state.ui.lastScene = `${interview.conditional.scene}`;
  if (interview.conditional.unlocks?.includes("locked-box-trigger")) state.ui.notice = "Rusk has now admitted he locked Gideon's cylinder away.";
  save();
  render();
}

function followThread(suspectId) {
  const interview = caseData.interviews[suspectId];
  const follow = interview.follow_thread;
  if (!follow || owned(follow.discovery.id) || state.leverage < 1) return;
  if (!spendLeverage(state, caseData, "follow-the-thread")) return;
  recordInferenceAction(state, suspectId, "follow-the-thread", follow.discovery.id);
  recordDiscovery(state, follow.discovery);
  state.ui.lastScene = follow.scene;
  save();
  render();
}

function renderPeoplePicker() {
  const buttons = caseData.suspects.map((suspect) => {
    const investigated = state.investigatedTargets.includes(suspect.id);
    const interview = caseData.interviews[suspect.id];
    const revisit = investigated && (conditionalAvailable(interview) || (!owned(interview.follow_thread?.discovery?.id) && state.leverage > 0));
    const disabled = investigated && !revisit;
    return `<button class="choice" data-suspect="${esc(suspect.id)}" data-revisit="${revisit ? "1" : "0"}" ${disabled ? "disabled" : ""}><strong>${revisit ? "Revisit " : ""}${esc(suspect.name)}</strong><span>${esc(suspect.role)}</span></button>`;
  }).join("");
  return `<section class="card"><h2>Who do you want to question?</h2><div class="choice-grid">${buttons}</div><div class="actions"><button class="secondary" id="cancelPeople" type="button">Back</button></div></section>`;
}

function renderScene() {
  const target = state.ui.lastTarget;
  const interview = caseData.interviews[target];
  let extra = "";
  if (interview) {
    if (conditionalAvailable(interview)) extra += `<button class="secondary" id="challengeClaim" type="button">Challenge that claim</button>`;
    const follow = interview.follow_thread;
    if (follow && !owned(follow.discovery.id) && state.leverage > 0) extra += `<button class="secondary" id="followThread" type="button">Spend 1 Leverage: ${esc(follow.prompt)}</button>`;
  }
  return `<section class="card"><p class="eyebrow">${esc(labelForTarget(target))}</p><div class="story">${state.ui.lastScene.split("\n\n").map((p) => `<p>${esc(p)}</p>`).join("")}</div><div class="actions">${extra}<button class="primary" id="backToCase" type="button">Back to the case</button></div></section>`;
}

function lockCallout() {
  if (!shouldOpenLockWindow(state, caseData)) return "";
  return `<section class="card"><p class="eyebrow">Something just moved</p><h2>Rusk is heading for a locked hotel strongbox.</h2><p class="story">${caseData.rival.name} sees it too. Rusk has hidden something he found after the séance. If you want first look, get the box open before your rival does.</p><div class="actions"><button class="primary" id="openLock" type="button">Crack the box</button></div></section>`;
}

function renderInvestigationMenu() {
  const maxed = state.majorActions >= 6;
  const locationButtons = caseData.investigation.opening_opportunities.filter((item) => item.id !== "people").map((item) => {
    const done = state.investigatedTargets.includes(item.id);
    return `<button class="choice" data-route="${esc(item.id)}" ${done || maxed ? "disabled" : ""}><strong>${done ? "Visited: " : ""}${esc(item.label)}</strong><span>${done ? "You already searched this route." : esc(item.description)}</span></button>`;
  }).join("");
  const peopleAvailable = caseData.suspects.some((suspect) => {
    const interview = caseData.interviews[suspect.id];
    return !state.investigatedTargets.includes(suspect.id) || conditionalAvailable(interview) || (!owned(interview.follow_thread?.discovery?.id) && state.leverage > 0);
  });
  const lastCall = canEnterLastCall(state, caseData) ? `<section class="card"><p class="eyebrow">Last Call is open</p><h2>You have enough time for ${state.majorActions >= 6 ? "no more detours" : "one final move, if you want it"}.</h2><p class="story">When you are ready, lock your theory. Nobody gets to revise it after seeing what the other detective chose.</p><div class="actions"><button class="primary" id="enterLastCall" type="button">Lock my theory</button></div></section>` : "";
  return `
    ${meta()}
    ${state.ui.notice ? `<div class="notice rival"><strong>Rival activity:</strong> ${esc(state.ui.notice)}</div>` : ""}
    <section class="card"><h2>Your next move</h2><p class="small">Follow what interests you. The notebook keeps facts, not conclusions.</p><div class="choice-grid">${locationButtons}<button class="choice" id="peopleChoice" ${!peopleAvailable || maxed ? "disabled" : ""}><strong>Question Someone</strong><span>Clara, Quill, Rusk, or Beatrice.</span></button></div></section>
    ${lastCall}`;
}

function renderInvestigation() {
  if (state.ui.peoplePickerOpen) {
    app.innerHTML = meta() + renderPeoplePicker();
    document.querySelector("#cancelPeople").addEventListener("click", () => { state.ui.peoplePickerOpen = false; save(); render(); });
    document.querySelectorAll("[data-suspect]").forEach((button) => button.addEventListener("click", () => visitInterview(button.dataset.suspect, button.dataset.revisit === "1")));
    return;
  }
  if (state.ui.lastScene) {
    app.innerHTML = meta() + renderScene();
    document.querySelector("#challengeClaim")?.addEventListener("click", () => challengeInterview(state.ui.lastTarget));
    document.querySelector("#followThread")?.addEventListener("click", () => followThread(state.ui.lastTarget));
    document.querySelector("#backToCase").addEventListener("click", () => { state.ui.lastScene = null; state.ui.lastTarget = null; save(); render(); });
    return;
  }
  if (shouldOpenLockWindow(state, caseData)) {
    app.innerHTML = meta() + lockCallout();
    document.querySelector("#openLock").addEventListener("click", () => { openLockWindow(state); save(); render(); });
    return;
  }
  app.innerHTML = renderInvestigationMenu();
  document.querySelectorAll("[data-route]").forEach((button) => button.addEventListener("click", () => visitRoute(button.dataset.route)));
  document.querySelector("#peopleChoice")?.addEventListener("click", () => { state.ui.peoplePickerOpen = true; state.ui.notice = null; save(); render(); });
  document.querySelector("#enterLastCall")?.addEventListener("click", () => { enterLastCall(state, caseData); save(); render(); });
}

function stopLockTimers() {
  if (lockFrame) cancelAnimationFrame(lockFrame);
  if (lockInterval) clearInterval(lockInterval);
  lockFrame = null;
  lockInterval = null;
}

function meterPosition() {
  const elapsed = Date.now() - state.lock.startedAtMs;
  const cycle = (elapsed % 2400) / 2400;
  return cycle <= .5 ? cycle * 200 : (1 - cycle) * 200;
}

function finishLock(outcome) {
  stopLockTimers();
  if (resolveLock(state, caseData, outcome)) {
    if (outcome === "rival-win") state.ui.notice = `${caseData.rival.name} got the box open first.`;
    save();
    render();
  }
}

function renderLockResult() {
  const outcome = state.lock.outcome;
  let body;
  let actions;
  if (outcome === "human-win") {
    const cylinder = state.privateDiscoveries.find((item) => item.id === "e-cylinder-43");
    body = `<h2>You get the box open first.</h2><p class="story">Inside is Gideon March's missing cylinder 43.</p><div class="notice"><strong>Private first look:</strong> ${esc(cylinder?.fact ?? "You inspect cylinder 43 before anyone else.")}</div><p class="small">This is an information advantage, not a solution. The cylinder will enter normal investigation after your next move.</p>`;
    actions = `<button class="primary" id="returnFromLock" type="button">Use the head start</button>`;
  } else if (outcome === "rival-win") {
    body = `<h2>${esc(caseData.rival.name)} gets there first.</h2><p class="story">She opens the box and gets a private look at whatever Rusk hid inside. You know she found something tied to Gideon's recordings, but you do not own what she learned.</p>`;
    if (state.leverage > 0 && !owned("e-cylinder-43")) {
      actions = `<button class="secondary" id="listenIn" type="button">Spend 1 Leverage: Listen In</button><button class="primary" id="saveLeverage" type="button">Save it and keep investigating</button>`;
    } else {
      actions = `<button class="primary" id="returnFromLock" type="button">Keep investigating</button>`;
    }
  } else {
    body = `<h2>The lock wins the argument.</h2><p class="story">Rusk loses control of the situation. The strongbox is opened in front of everyone, and cylinder 43 becomes public evidence.</p><div class="notice"><strong>Cylinder 43:</strong> ${esc(caseData.competition.fallback_public_observation.fact)}</div>`;
    actions = `<button class="primary" id="returnFromLock" type="button">Back to the case</button>`;
  }
  app.innerHTML = meta() + `<section class="card">${body}<div class="actions">${actions}</div></section>`;
  document.querySelector("#listenIn")?.addEventListener("click", () => { spendLeverage(state, caseData, "listen-in"); save(); render(); });
  document.querySelector("#saveLeverage")?.addEventListener("click", () => { saveLeverage(state, "listen-in"); acknowledgeLockResult(state); state.ui.lastScene = null; save(); render(); });
  document.querySelector("#returnFromLock")?.addEventListener("click", () => { acknowledgeLockResult(state); state.ui.lastScene = null; save(); render(); });
}

function renderLock() {
  if (state.lock.status === "resolved") return renderLockResult();
  const pin = caseData.competition.pins[state.lock.currentPin];
  if (!pin) return finishLock("human-win");
  app.innerHTML = `
    ${meta()}
    <section class="card lock-stage"><p class="eyebrow">The Locked Box</p><h2>Set four pins before ${esc(caseData.rival.name)} cracks the lock.</h2><p class="small">The bright band is where this pin wants to settle. Tap <strong>Set pin</strong> when the marker crosses it. Release in the red ends and the pick snaps.</p>
      <div class="lock-box">
        <div class="pin-dots">${caseData.competition.pins.map((_, index) => `<span class="pin-dot ${state.lock.setPins.includes(index) ? "set" : ""}"></span>`).join("")}</div>
        <div class="lock-status"><span>Pin ${state.lock.currentPin + 1} of 4</span><span id="timeLeft">45s</span></div>
        <div class="meter" aria-label="Lock tension meter"><span class="target-zone" style="left:${pin.target - pin.tolerance}%;width:${pin.tolerance * 2}%"></span><span class="marker" id="marker"></span></div>
        <div class="lock-status"><span>${esc(caseData.rival.name)}</span><span id="rivalTime">moving</span></div><div class="progress"><span id="rivalProgress" style="width:0%"></span></div>
      </div>
      <div id="lockMessage" class="small" aria-live="polite">Feel for the first pin.</div>
      <div class="actions" style="justify-content:center"><button class="primary" id="setPin" type="button">Set pin</button><button class="danger-button" id="abortLock" type="button">Back off</button></div>
    </section>`;
  const marker = document.querySelector("#marker");
  const timeLeft = document.querySelector("#timeLeft");
  const rivalProgress = document.querySelector("#rivalProgress");
  const lockMessage = document.querySelector("#lockMessage");
  const tick = () => {
    if (state.lock.status !== "active") return;
    currentMeterValue = meterPosition();
    marker.style.left = `${currentMeterValue}%`;
    lockFrame = requestAnimationFrame(tick);
  };
  tick();
  const updateClock = () => {
    if (state.lock.status !== "active") return;
    const elapsed = (Date.now() - state.lock.startedAtMs) / 1000;
    const remaining = Math.max(0, caseData.competition.duration_seconds - elapsed);
    const rivalPct = Math.min(100, elapsed / caseData.competition.rival_finish_seconds * 100);
    timeLeft.textContent = `${Math.ceil(remaining)}s`;
    rivalProgress.style.width = `${rivalPct}%`;
    if (elapsed >= caseData.competition.rival_finish_seconds) return finishLock("rival-win");
    if (remaining <= 0) return finishLock("timeout");
  };
  updateClock();
  lockInterval = setInterval(updateClock, 120);
  document.querySelector("#setPin").addEventListener("click", () => {
    const value = currentMeterValue;
    if (value <= caseData.competition.red_zone_max || value >= caseData.competition.red_zone_min) {
      setLockProgress(state, state.lock.currentPin, value, "break");
      save();
      finishLock("break");
      return;
    }
    if (Math.abs(value - pin.target) <= pin.tolerance) {
      setLockProgress(state, state.lock.currentPin, value, "set");
      lockMessage.textContent = "Set.";
      save();
      stopLockTimers();
      if (state.lock.currentPin >= caseData.competition.pins.length) finishLock("human-win");
      else render();
    } else {
      setLockProgress(state, state.lock.currentPin, value, "miss");
      lockMessage.textContent = "Not quite. The pin drops back.";
      save();
    }
  });
  document.querySelector("#abortLock").addEventListener("click", () => finishLock("abort"));
}

function renderLastCall() {
  const evidence = allEvidence();
  app.innerHTML = `
    ${meta()}
    <section class="card"><p class="eyebrow">Last Call</p><h2>Lock your theory.</h2><p class="story">Choose the person you believe killed Gideon, then choose four or five facts that best reconstruct what happened. Your rival is locking a theory too. You will not see it first.</p>
      <label for="culpritSelect"><strong>Culprit</strong></label><select id="culpritSelect" class="suspect-select"><option value="">Choose one</option>${caseData.suspects.map((s) => `<option value="${esc(s.id)}" ${state.caseFile.draftCulprit === s.id ? "selected" : ""}>${esc(s.name)}</option>`).join("")}</select>
      <div class="evidence-grid">${evidence.map((item) => `<label class="evidence-option"><input type="checkbox" name="evidence" value="${esc(item.id)}" ${state.caseFile.draftPieces.includes(item.id) ? "checked" : ""}><span><strong>${esc(item.label)}</strong><br><span class="small">${esc(item.fact)}</span></span></label>`).join("")}</div>
      <div id="caseFileError" class="small" aria-live="polite"></div>
      <div class="actions"><button class="primary" id="commitTheory" type="button">Commit theory</button></div>
    </section>`;
  const persistDraft = () => {
    const culprit = document.querySelector("#culpritSelect").value;
    const pieces = [...document.querySelectorAll('input[name="evidence"]:checked')].map((input) => input.value);
    setCaseFileDraft(state, culprit, pieces);
    save();
  };
  document.querySelector("#culpritSelect").addEventListener("change", persistDraft);
  document.querySelectorAll('input[name="evidence"]').forEach((input) => input.addEventListener("change", persistDraft));
  document.querySelector("#commitTheory").addEventListener("click", () => {
    const culprit = document.querySelector("#culpritSelect").value;
    const pieces = [...document.querySelectorAll('input[name="evidence"]:checked')].map((input) => input.value);
    if (!culprit || pieces.length < 4 || pieces.length > 5) {
      document.querySelector("#caseFileError").textContent = "Choose one culprit and four or five facts.";
      return;
    }
    if (commitCaseFile(state, caseData, culprit, pieces)) {
      state.rival.accusation = state.lock.winner === "rival" ? "clara-hensley" : "lenora-quill";
      save();
      render();
    }
  });
}

function renderSurvey() {
  const playerAccused = caseData.suspects.find((s) => s.id === state.caseFile.culprit)?.name ?? "Unknown";
  const rivalAccused = caseData.suspects.find((s) => s.id === state.rival.accusation)?.name ?? "Unknown";
  app.innerHTML = `<section class="card"><p class="eyebrow">The accusations are locked</p><h2>You accused ${esc(playerAccused)}.</h2><p class="story">${esc(caseData.rival.name)} accused ${esc(rivalAccused)}.</p><p class="story">Before the truth is shown, answer the short post-play survey. Your run ID and playtest telemetry will be prefilled into the existing research form.</p><div class="actions"><button class="primary" id="openSurvey" type="button">Open post-play survey</button></div></section>`;
  document.querySelector("#openSurvey").addEventListener("click", () => {
    markComplete(state);
    markSurveyHandoff(state);
    save();
    window.location.assign(buildSurveyUrl(state));
  });
}

function renderReveal() {
  const solved = state?.caseFile?.correct === true;
  app.innerHTML = `<section class="card"><p class="eyebrow">The Truth</p><h2>Clara Hensley killed Gideon March.</h2><div class="reveal-list story"><div class="truth-step"><strong>Before the séance</strong><p>Gideon discovered that confidential research passing through Clara had reached Lenora Quill. He confronted Clara in the writing room. She killed him with the brass bookend.</p></div><div class="truth-step"><strong>The false voice</strong><p>Gideon had already recorded cylinder 43, including the sentence everyone later heard. Clara substituted it into Quill's concealed apparatus. Quill unknowingly played Gideon's recording at her normal cue while Clara sat visibly with the group.</p></div><div class="truth-step"><strong>The second cover-up</strong><p>Rusk found Gideon's cylinder in the apparatus and hid it in the strongbox to protect the hotel and Quill's fraudulent séances. His cover-up protected Clara without his knowing it.</p></div><div class="truth-step"><strong>Why the lies mattered</strong><p>Quill lied to protect her fraud. Rusk lied to protect the hotel. Beatrice lied to hide her threat and eavesdropping. Those three lies gave Clara cover she never had to invent.</p></div></div><hr><h3>The Verdict</h3><p>${solved ? "You reconstructed the murder correctly." : "Your locked reconstruction missed at least one essential part of the murder."}</p><p class="small">No model judged your argument. The fixture resolved your selected culprit and evidence against the authored solution graph.</p></section>`;
  if (state) {
    markComplete(state);
    save();
  }
}

function render() {
  stopLockTimers();
  renderNotebook();
  if (isRevealMode()) return renderReveal();
  if (state.phase === "opening") return renderOpening();
  if (state.phase === "investigation") return renderInvestigation();
  if (state.phase === "lock") return renderLock();
  if (state.phase === "last-call") return renderLastCall();
  if (state.phase === "survey") return renderSurvey();
  if (state.phase === "reveal") return renderReveal();
  state.phase = "investigation";
  save();
  renderInvestigation();
}

async function boot() {
  const response = await fetch("./case.json", { cache: "no-store" });
  if (!response.ok) throw new Error(`Could not load case data: ${response.status}`);
  caseData = await response.json();
  const deviceClass = window.matchMedia("(max-width: 640px)").matches ? "mobile" : "desktop";
  const ua = navigator.userAgent.toLowerCase();
  const browserClass = ua.includes("firefox") ? "firefox" : ua.includes("edg/") ? "edge" : ua.includes("chrome") || ua.includes("crios") ? "chrome" : ua.includes("safari") ? "safari" : "other";
  state = restoreState(caseData) ?? createInitialState(caseData, { deviceClass, browserClass });
  if (isRevealMode()) markRevealReturn(state);
  save();
  render();
}

boot().catch((error) => {
  console.error(error);
  app.innerHTML = `<section class="card"><h2>The case file failed to open.</h2><p>${esc(error.message)}</p></section>`;
});
