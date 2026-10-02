/* global DOMPurify, document, cancelAnimationFrame, clearInterval, requestAnimationFrame, setInterval, window, fetch, navigator, console */
import {
  acknowledgeLockResult,
  buildSurveyUrl,
  canChallengeClaim,
  canEnterLastCall,
  canFollowThread,
  challengeClaim,
  commitCaseFile,
  completeOpening,
  createInitialState,
  declineLockWindow,
  enterLastCall,
  followThread as acquireFollowThread,
  getVerdictView,
  isRevealMode,
  markComplete,
  markRevealReturn,
  markSurveyHandoff,
  openLockWindow,
  attemptLockPin,
  persistState,
  reviewEncounter,
  resolveLock,
  resolveRivalTheory,
  restoreState,
  saveLeverage,
  setCaseFileDraft,
  setPrivateNotes,
  shouldOpenLockWindow,
  spendLeverage,
  triggerRivalActivity,
  visitInvestigation,
} from "./runtime.js";

function sanitizedHtmlTarget(element) {
  return {
    set innerHTML(value) {
      element.innerHTML = DOMPurify.sanitize(String(value), {
        USE_PROFILES: { html: true },
      });
    },
    get hidden() {
      return element.hidden;
    },
    set hidden(value) {
      element.hidden = value;
    },
    querySelector(selector) {
      return element.querySelector(selector);
    },
  };
}

const app = sanitizedHtmlTarget(document.querySelector("#app"));
const notebook = sanitizedHtmlTarget(document.querySelector("#notebook"));
const notebookButton = document.querySelector("#notebookButton");
let caseData;
let state;
let lockFrame = null;
let lockInterval = null;
let currentMeterValue = 50;
let storageAvailable = true;
let loadAttempts = 0;

function esc(value) {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (char) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        char
      ],
  );
}

function save() {
  storageAvailable = persistState(state);
  renderNotebook();
  return storageAvailable;
}

function owned(id) {
  return [...state.discoveries, ...state.privateDiscoveries].some(
    (item) => item.id === id,
  );
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
  const encounters = state.encounterHistory ?? [];
  const notes = state.privateNotes ?? "";
  notebook.innerHTML = `
    <div class="close-row"><h2>Detective notebook</h2><button class="ghost-button" id="closeNotebook" type="button">Close</button></div>
    <p class="small">This remembers what you actually encountered. It does not tell you what matters.</p>
    ${facts.length ? `<ul class="fact-list">${facts.map((item) => `<li class="fact"><strong>${esc(item.label)}</strong><div>${esc(item.fact)}</div><small>${esc(item.source)}${state.privateDiscoveries.some((privateItem) => privateItem.id === item.id) ? " · private for now" : ""}</small></li>`).join("")}</ul>` : `<p class="small">Nothing recorded yet.</p>`}
    <h3>Encounter journal</h3>
    ${encounters.length ? encounters.map((item) => `<section class="fact"><strong>${esc(labelForTarget(item.targetId))}</strong><small> · ${esc(item.kind)}</small><p>${esc(item.scene)}</p></section>`).join("") : `<p class="small">No encounters yet.</p>`}
    <label for="privateNotes"><strong>Private notes</strong></label>
    <textarea id="privateNotes" maxlength="500" rows="5" aria-describedby="notesLimit">${esc(notes)}</textarea>
    <p class="small" id="notesLimit">Your own notes stay on this device and do not count as evidence. <span id="notesCount">${Array.from(notes).length}</span>/500 characters.</p>
  `;
  notebook
    .querySelector("#closeNotebook")
    ?.addEventListener("click", closeNotebook);
  notebook
    .querySelector("#privateNotes")
    ?.addEventListener("input", (event) => {
      const stored = setPrivateNotes(state, event.target.value);
      event.target.value = stored;
      notebook.querySelector("#notesCount").textContent = String(
        Array.from(stored).length,
      );
      persistState(state);
    });
}

function openNotebook() {
  if (!state) return;
  notebook.hidden = false;
  notebookButton.setAttribute("aria-expanded", "true");
  renderNotebook();
}
function closeNotebook() {
  notebook.hidden = true;
  notebookButton.setAttribute("aria-expanded", "false");
}
notebookButton.addEventListener("click", () =>
  notebook.hidden ? openNotebook() : closeNotebook(),
);

function meta() {
  return `${storageAvailable ? "" : '<div class="notice" role="status">This is an in-memory session. This browser cannot save it, so refresh and survey return cannot restore your Case File.</div>'}<div class="meta-row"><span class="pill">Rival: <strong>${esc(caseData.rival.name)}</strong></span><span class="pill">Leverage: <strong>${state.leverage}</strong></span><span class="pill">Moves made: <strong>${state.majorActions}/${caseData.investigation.max_major_actions}</strong></span></div>`;
}

function renderOpening() {
  app.innerHTML = `
    <section class="card">
      <p class="eyebrow">The Larkspur Hotel · Atlantic coast · 1926</p>
      <div class="story lede">
        <p>Gideon March invited you to the Larkspur to watch him expose Lenora Quill's séance. He invited Nora Vance too. Two detectives, one demonstration. He seemed to relish an audience that might argue back.</p>
        <p>At 11:47, Quill raises a brass trumpet from the table. Gideon's voice comes through it.</p>
        <p><strong>“Mrs. Quill, do carry on. I can hear every word.”</strong></p>
        <p>Quill flinches. Clara Hensley, Gideon's secretary, is seated with the guests. Edwin Rusk leaves the room.</p>
        <p>At midnight, Rusk knocks on Gideon's writing-room door.</p>
        <p>There is no answer. When the door opens, Gideon lies dead beside his desk.</p>
        <p>Nora looks from the body to the corridor. Then she looks at you.</p>
      </div>
      <div class="notice"><strong>What you saw:</strong> Gideon's voice came through Quill's trumpet before the body was found. Quill flinched. Rusk left. Clara sat with the guests.</div>
      <div class="actions"><button class="primary" id="startInvestigation" type="button">Start investigating</button></div>
    </section>`;
  document
    .querySelector("#startInvestigation")
    .addEventListener("click", () => {
      completeOpening(state);
      save();
      render();
    });
}

function rivalBeatAfterAction() {
  if (state.majorActions === 1) {
    const candidate =
      ["seance-room", "gideon-materials", "writing-room"].find(
        (id) => !state.investigatedTargets.includes(id),
      ) ?? "edwin-rusk";
    if (triggerRivalActivity(state, caseData, "pursued", candidate))
      state.ui.notice = `${caseData.rival.name} heads for ${labelForTarget(candidate)} without waiting to see what you found.`;
  } else if (state.majorActions === 2 && state.lock.status === "unavailable") {
    if (triggerRivalActivity(state, caseData, "followed", "edwin-rusk"))
      state.ui.notice = `${caseData.rival.name} notices Rusk checking the service corridor and follows him.`;
  }
}

function labelForTarget(id) {
  const route = caseData.investigation.opening_opportunities.find(
    (item) => item.id === id,
  );
  const suspect = caseData.suspects.find((item) => item.id === id);
  return route?.label ?? suspect?.name ?? id;
}

function publicReleaseNotice() {
  return state.lock.firstLookClaimed
    ? "Rusk brings cylinder 43 into the open. Your earlier reading remains in your notebook."
    : "Rusk brings cylinder 43 into the open. The recording is now public evidence.";
}

function visitRoute(routeId) {
  const closesFirstLook =
    state.lock.status === "resolved" && !state.lock.publicReleased;
  if (!visitInvestigation(state, caseData, routeId)) return;
  state.ui.lastTarget = routeId;
  state.ui.lastEncounterId = `route:${routeId}`;
  state.ui.lastScene = reviewEncounter(state, state.ui.lastEncounterId).scene;
  state.ui.peoplePickerOpen = false;
  rivalBeatAfterAction();
  if (closesFirstLook) {
    state.ui.sceneNotice = publicReleaseNotice();
    state.ui.notice = null;
  }
  save();
  render();
}

function visitInterview(suspectId, isRevisit = false) {
  if (!isRevisit) {
    const closesFirstLook =
      state.lock.status === "resolved" && !state.lock.publicReleased;
    if (!visitInvestigation(state, caseData, suspectId)) return;
    rivalBeatAfterAction();
    if (closesFirstLook) {
      state.ui.sceneNotice = publicReleaseNotice();
      state.ui.notice = null;
    }
  } else if (!state.investigatedTargets.includes(suspectId)) {
    return;
  }
  state.ui.lastTarget = suspectId;
  state.ui.lastEncounterId = `interview:${suspectId}`;
  const interview = caseData.interviews[suspectId];
  state.ui.lastScene =
    reviewEncounter(state, state.ui.lastEncounterId)?.scene ??
    `${interview.opening}\n\n${interview.claim}`;
  state.ui.peoplePickerOpen = false;
  save();
  render();
}

function challengeInterview(suspectId) {
  if (!challengeClaim(state, caseData, suspectId)) return;
  state.ui.sceneNotice = null;
  state.ui.lastEncounterId = `challenge:${suspectId}`;
  state.ui.lastScene = reviewEncounter(state, state.ui.lastEncounterId).scene;
  if (
    caseData.interviews[suspectId].conditional.unlocks?.includes(
      "locked-box-trigger",
    )
  )
    state.ui.notice = "Rusk has now admitted he locked Gideon's cylinder away.";
  save();
  render();
}

function followThread(suspectId) {
  if (!acquireFollowThread(state, caseData, suspectId)) return;
  state.ui.sceneNotice = null;
  state.ui.lastEncounterId = `follow:${suspectId}`;
  state.ui.lastScene = reviewEncounter(state, state.ui.lastEncounterId).scene;
  save();
  render();
}

function renderPeoplePicker() {
  const maxed = state.majorActions >= caseData.investigation.max_major_actions;
  const buttons = caseData.suspects
    .map((suspect) => {
      const investigated = state.investigatedTargets.includes(suspect.id);
      return `<button class="choice" data-suspect="${esc(suspect.id)}" data-revisit="${investigated ? "1" : "0"}" ${maxed && !investigated ? "disabled" : ""}><strong>${investigated ? "Revisit " : "Question "}${esc(suspect.name)}</strong><span>${esc(suspect.public_hook)}</span><small>${investigated ? "Free review and earned questions" : "Costs 1 investigation"}</small></button>`;
    })
    .join("");
  return `<section class="card"><h2>Who do you want to question?</h2><div class="choice-grid">${buttons}</div><div class="actions"><button class="secondary" id="cancelPeople" type="button">Back</button></div></section>`;
}

function renderScene() {
  const target = state.ui.lastTarget;
  const interview = caseData.interviews[target];
  const encounter = reviewEncounter(state, state.ui.lastEncounterId);
  let extra = "";
  if (interview) {
    if (canChallengeClaim(state, caseData, target))
      extra += `<button class="secondary" id="challengeClaim" type="button">${esc(interview.conditional.prompt)} (free)</button>`;
    const follow = interview.follow_thread;
    if (canFollowThread(state, caseData, target))
      extra += `<button class="secondary" id="followThread" type="button">Spend 1 Leverage: ${esc(follow.prompt)}</button>`;
  }
  const learned = (encounter?.discoveryIds ?? [])
    .map((id) => allEvidence().find((item) => item.id === id))
    .filter(Boolean);
  const suspectHistory = interview
    ? (state.encounterHistory ?? []).filter((item) => item.targetId === target)
    : [];
  return `<section class="card">${state.ui.sceneNotice ? `<div class="notice"><strong>Case update:</strong> ${esc(state.ui.sceneNotice)}</div>` : ""}<p class="eyebrow">${esc(labelForTarget(target))}</p><div class="story">${state.ui.lastScene
    .split("\n\n")
    .map((p) => `<p>${esc(p)}</p>`)
    .join(
      "",
    )}</div>${learned.length ? `<div class="notice"><strong>Recorded from this encounter</strong><ul>${learned.map((item) => `<li>${esc(item.label)}: ${esc(item.fact)}</li>`).join("")}</ul></div>` : ""}${suspectHistory.length > 1 ? `<details><summary>Review earned history with ${esc(labelForTarget(target))}</summary>${suspectHistory.map((item) => `<p class="small">${esc(item.scene)}</p>`).join("")}</details>` : ""}<div class="actions">${extra}<button class="primary" id="backToCase" type="button">Back to the case</button></div></section>`;
}

function lockCallout() {
  if (!shouldOpenLockWindow(state, caseData)) return "";
  return `<section class="card"><p class="eyebrow">The Locked Box · ready</p><h2>Rusk is heading for the hotel strongbox.</h2><p class="story">${esc(caseData.rival.name)} sees it too. Rusk hid something he found after the séance. Start gives you 19 seconds to set four pins before Nora opens the box. Click or tap <strong>Set pin</strong> when the marker is inside each bright band. A red end breaks the pick. If you win, you see the contents first; if Nora wins, you may spend Leverage to Listen In. Backing off or declining makes the contents public without costing a move or Leverage.</p><p class="small">The clock starts only when you choose Start. Declining preserves the evidence, but gives neither detective a private first look.</p><div class="actions"><button class="primary" id="openLock" type="button">Start lock race</button><button class="secondary" id="declineLock" type="button">Decline and release the contents</button></div></section>`;
}

function renderInvestigationMenu() {
  const maxed = state.majorActions >= caseData.investigation.max_major_actions;
  const locationButtons = caseData.investigation.opening_opportunities
    .filter((item) => item.id !== "people")
    .map((item) => {
      const done = state.investigatedTargets.includes(item.id);
      return `<button class="choice" data-route="${esc(item.id)}" ${done || maxed ? "disabled" : ""}><strong>${done ? "Visited: " : ""}${esc(item.label)}</strong><span>${done ? "Review in your notebook." : esc(item.description)}</span><small>${done ? "Free review" : "Costs 1 investigation"}</small></button>`;
    })
    .join("");
  const peopleAvailable = caseData.suspects.some(
    (suspect) => state.investigatedTargets.includes(suspect.id) || !maxed,
  );
  const lastCall = canEnterLastCall(state, caseData)
    ? `<section class="card"><p class="eyebrow">Last Call is open</p><h2>You have enough time for ${maxed ? "no more detours" : "one final move, if you want it"}.</h2><p class="story">Earned questions and the one paid follow-up remain available until you enter Last Call. Nobody gets to revise a locked theory.</p><div class="actions"><button class="primary" id="enterLastCall" type="button">Lock my theory</button></div></section>`
    : "";
  return `
    ${meta()}
    ${state.ui.notice ? `<div class="notice rival"><strong>Case update:</strong> ${esc(state.ui.notice)}</div>` : ""}
    <section class="card"><h2>Your next move</h2><p class="small">New places and people cost one investigation. Last Call opens after five; the sixth is your final new investigation. Review and earned questions are free. The notebook keeps facts, not conclusions.</p><div class="choice-grid">${locationButtons}<button class="choice" id="peopleChoice" ${!peopleAvailable ? "disabled" : ""}><strong>Question Someone</strong><span>Clara, Quill, Rusk, or Beatrice.</span><small>New person: 1 investigation. Revisit: free.</small></button></div></section>
    ${lastCall}`;
}

function renderInvestigation() {
  if (state.ui.peoplePickerOpen) {
    app.innerHTML = meta() + renderPeoplePicker();
    document.querySelector("#cancelPeople").addEventListener("click", () => {
      state.ui.peoplePickerOpen = false;
      save();
      render();
    });
    document
      .querySelectorAll("[data-suspect]")
      .forEach((button) =>
        button.addEventListener("click", () =>
          visitInterview(
            button.dataset.suspect,
            button.dataset.revisit === "1",
          ),
        ),
      );
    return;
  }
  if (state.ui.lastScene) {
    app.innerHTML = meta() + renderScene();
    document
      .querySelector("#challengeClaim")
      ?.addEventListener("click", () =>
        challengeInterview(state.ui.lastTarget),
      );
    document
      .querySelector("#followThread")
      ?.addEventListener("click", () => followThread(state.ui.lastTarget));
    document.querySelector("#backToCase").addEventListener("click", () => {
      state.ui.lastScene = null;
      state.ui.lastTarget = null;
      state.ui.sceneNotice = null;
      save();
      render();
    });
    return;
  }
  if (shouldOpenLockWindow(state, caseData)) {
    app.innerHTML = meta() + lockCallout();
    document.querySelector("#openLock").addEventListener("click", () => {
      openLockWindow(state, caseData);
      save();
      render();
    });
    document.querySelector("#declineLock").addEventListener("click", () => {
      if (!declineLockWindow(state, caseData)) return;
      state.ui.notice =
        "Rusk opens the strongbox in front of both detectives. Cylinder 43 is public evidence in your notebook.";
      save();
      render();
    });
    return;
  }
  app.innerHTML = renderInvestigationMenu();
  document
    .querySelectorAll("[data-route]")
    .forEach((button) =>
      button.addEventListener("click", () => visitRoute(button.dataset.route)),
    );
  document.querySelector("#peopleChoice")?.addEventListener("click", () => {
    state.ui.peoplePickerOpen = true;
    state.ui.notice = null;
    save();
    render();
  });
  document.querySelector("#enterLastCall")?.addEventListener("click", () => {
    enterLastCallWithNotice();
  });
}

function enterLastCallWithNotice() {
  const releasesCylinder =
    state.lock.status === "resolved" && !state.lock.publicReleased;
  if (!enterLastCall(state, caseData)) return false;
  state.ui.lastCallReleaseNotice = releasesCylinder
    ? "Rusk opens the strongbox to everyone. Cylinder 43 is now public evidence."
    : null;
  render();
  state.ui.lastCallReleaseNotice = null;
  save();
  return true;
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
  return cycle <= 0.5 ? cycle * 200 : (1 - cycle) * 200;
}

function announceLockResult() {
  if (state.lock.outcome === "human-win")
    state.ui.notice =
      "You found cylinder 43 first. Its observation is private in your notebook until the next new investigation or Last Call.";
  else if (state.lock.outcome === "rival-win")
    state.ui.notice = `${caseData.rival.name} opens the box first and studies what Rusk hid.`;
  else if (state.lock.publicReleased)
    state.ui.notice =
      "Rusk opens the strongbox before both detectives. Cylinder 43 is now public evidence in your notebook.";
}

function finishLock(outcome) {
  stopLockTimers();
  if (resolveLock(state, caseData, outcome)) {
    announceLockResult();
    save();
    render();
  }
}

function renderLockResult() {
  const outcome = state.lock.outcome;
  let body;
  let actions;
  if (outcome === "human-win") {
    const cylinder = state.privateDiscoveries.find(
      (item) => item.id === "e-cylinder-43",
    );
    body = `<h2>You get the box open first.</h2><p class="story">Rusk steps back as you lift Gideon March's missing cylinder 43 from the box. Nora can see you found something, but cannot read it yet.</p><div class="notice"><strong>Private first look:</strong> ${esc(cylinder?.fact ?? "You inspect cylinder 43 before anyone else.")}</div><p class="small">This fact remains in your notebook. It becomes public after your next new major investigation or when you enter Last Call. Free review and earned questions do not close first look.</p>`;
    actions = `${state.leverage > 0 && !state.lock.leverageChoice ? '<button class="secondary" id="saveLeverage" type="button">Save Leverage for later</button>' : ""}<button class="primary" id="returnFromLock" type="button">Use the head start</button>`;
  } else if (outcome === "rival-win") {
    const heard = state.privateDiscoveries.find(
      (item) => item.id === "e-cylinder-43",
    );
    body = `<h2>${esc(caseData.rival.name)} gets there first.</h2><p class="story">She opens the box and studies the cylinder Rusk hid. ${heard ? "You spent Leverage to hear her observation." : "You know she found something tied to Gideon's recordings, but not what she learned."}</p>${heard ? `<div class="notice"><strong>Listen In acquired:</strong> ${esc(heard.fact)}</div><p class="small">This fact stays in your notebook. It becomes public after your next new major investigation or entering Last Call.</p>` : ""}`;
    if (
      state.leverage > 0 &&
      !owned("e-cylinder-43") &&
      !state.lock.leverageChoice
    ) {
      actions = `<button class="secondary" id="listenIn" type="button">Spend 1 Leverage: Listen In</button><button class="primary" id="saveLeverage" type="button">Save it and keep investigating</button>`;
    } else {
      actions = `<button class="primary" id="returnFromLock" type="button">Keep investigating</button>`;
    }
  } else {
    const cause =
      outcome === "abort"
        ? "You back away from the box. Rusk opens it in front of both detectives rather than leave it contested."
        : outcome === "break"
          ? "The pick snaps. Rusk opens the box in front of both detectives to settle what he hid."
          : "The lock takes too long. Rusk opens the box in front of both detectives.";
    body = `<h2>The box opens in public.</h2><p class="story">${cause}</p><div class="notice"><strong>Cylinder 43:</strong> ${esc(caseData.competition.fallback_public_observation.fact)}</div>`;
    actions = `<button class="primary" id="returnFromLock" type="button">Back to the case</button>`;
  }
  app.innerHTML =
    meta() +
    `<section class="card">${body}<div class="actions">${actions}</div></section>`;
  document.querySelector("#listenIn")?.addEventListener("click", () => {
    spendLeverage(state, caseData, "listen-in");
    save();
    render();
  });
  document.querySelector("#saveLeverage")?.addEventListener("click", () => {
    saveLeverage(state, outcome === "human-win" ? "first-look" : "listen-in");
    acknowledgeLockResult(state);
    state.ui.lastScene = null;
    save();
    render();
  });
  document.querySelector("#returnFromLock")?.addEventListener("click", () => {
    acknowledgeLockResult(state);
    state.ui.lastScene = null;
    save();
    render();
  });
}

function renderLock() {
  if (state.lock.status === "resolved") return renderLockResult();
  if (
    Date.now() - state.lock.startedAtMs >=
    caseData.competition.rival_finish_seconds * 1000
  )
    return finishLock("rival-win");
  const pin = caseData.competition.pins[state.lock.currentPin];
  if (!pin) return finishLock("human-win");
  app.innerHTML = `
    ${meta()}
    <section class="card lock-stage"><p class="eyebrow">The Locked Box</p><h2>Set four pins before ${esc(caseData.rival.name)} cracks the lock.</h2><p class="small">Click or tap <strong>Set pin</strong> while the marker is inside the bright band. A red end breaks the pick. Nora opens the box at 19 seconds.</p>
      <div class="lock-box">
        <div class="pin-dots">${caseData.competition.pins.map((_, index) => `<span class="pin-dot ${state.lock.setPins.includes(index) ? "set" : ""}"></span>`).join("")}</div>
        <div class="lock-status"><span>Pin ${state.lock.currentPin + 1} of 4</span><span id="timeLeft">19s until Nora opens it</span></div>
        <div class="meter" aria-label="Lock tension meter"><span class="target-zone" style="left:${pin.target - pin.tolerance}%;width:${pin.tolerance * 2}%"></span><span class="marker" id="marker"></span></div>
        <div class="lock-status"><span>${esc(caseData.rival.name)}</span><span id="rivalTime">moving</span></div><div class="progress"><span id="rivalProgress" style="width:0%"></span></div>
      </div>
      <div id="lockMessage" class="small" aria-live="polite">Pin ${state.lock.currentPin + 1} ready. Set pin when the marker reaches the bright band.</div>
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
    const remaining = Math.max(
      0,
      caseData.competition.duration_seconds - elapsed,
    );
    const rivalPct = Math.min(
      100,
      (elapsed / caseData.competition.rival_finish_seconds) * 100,
    );
    timeLeft.textContent = `${Math.ceil(Math.max(0, caseData.competition.rival_finish_seconds - elapsed))}s until Nora opens it`;
    rivalProgress.style.width = `${rivalPct}%`;
    if (elapsed >= caseData.competition.rival_finish_seconds)
      return finishLock("rival-win");
    if (remaining <= 0) return finishLock("timeout");
  };
  updateClock();
  lockInterval = setInterval(updateClock, 120);
  document.querySelector("#setPin").addEventListener("click", () => {
    const result = attemptLockPin(
      state,
      caseData,
      currentMeterValue,
      Date.now(),
    );
    if (!result.accepted && state.lock.status === "resolved") {
      announceLockResult();
      save();
      render();
      return;
    }
    if (!result.accepted) return;
    save();
    if (state.lock.status === "resolved") {
      announceLockResult();
      render();
    } else if (result.outcome === "set") {
      render();
      document.querySelector("#setPin")?.focus();
    } else {
      lockMessage.textContent = "Pin not set. Keep watching the marker.";
    }
  });
  document
    .querySelector("#abortLock")
    .addEventListener("click", () => finishLock("abort"));
}

function renderLastCall() {
  const evidence = allEvidence();
  const selectedCount = state.caseFile.draftPieces.length;
  app.innerHTML = `
    ${meta()}
    ${state.ui.lastCallReleaseNotice ? `<div class="notice" role="status">${esc(state.ui.lastCallReleaseNotice)}</div>` : ""}
    <section class="card"><p class="eyebrow">Last Call</p><h2>Lock your theory.</h2><p class="story">Choose the person you believe killed Gideon, then choose four or five facts that best reconstruct what happened. Your rival is locking a theory too. You will not see it first.</p><p class="small">This Case File is a short fact selection for this paper test. You can review your earned journal without spending a move.</p><button class="ghost-button" id="reviewNotebook" type="button">Review notebook and journal</button>
      <label for="culpritSelect"><strong>Culprit</strong></label><select id="culpritSelect" class="suspect-select"><option value="">Choose one</option>${caseData.suspects.map((s) => `<option value="${esc(s.id)}" ${state.caseFile.draftCulprit === s.id ? "selected" : ""}>${esc(s.name)}</option>`).join("")}</select>
      <p id="selectionCount" class="small" aria-live="polite">${selectedCount} of 4 or 5 facts selected.</p><div class="evidence-grid" role="group" aria-label="Earned facts" aria-describedby="selectionCount">${evidence.map((item) => `<label class="evidence-option"><input type="checkbox" name="evidence" value="${esc(item.id)}" ${state.caseFile.draftPieces.includes(item.id) ? "checked" : ""}><span><strong>${esc(item.label)}</strong><br><span class="small">${esc(item.fact)}</span></span></label>`).join("")}</div>
      <div id="caseFileError" class="small" aria-live="polite"></div>
      <div class="actions"><button class="primary" id="commitTheory" type="button">Commit theory</button></div>
    </section>`;
  const persistDraft = () => {
    const culprit = document.querySelector("#culpritSelect").value;
    const pieces = [
      ...document.querySelectorAll('input[name="evidence"]:checked'),
    ].map((input) => input.value);
    setCaseFileDraft(state, culprit, pieces);
    document.querySelector("#selectionCount").textContent =
      `${pieces.length} of 4 or 5 facts selected.`;
    save();
  };
  document
    .querySelector("#reviewNotebook")
    .addEventListener("click", () => openNotebook());
  document
    .querySelector("#culpritSelect")
    .addEventListener("change", persistDraft);
  document
    .querySelectorAll('input[name="evidence"]')
    .forEach((input) => input.addEventListener("change", persistDraft));
  document.querySelector("#commitTheory").addEventListener("click", () => {
    const culprit = document.querySelector("#culpritSelect").value;
    const pieces = [
      ...document.querySelectorAll('input[name="evidence"]:checked'),
    ].map((input) => input.value);
    if (!culprit) {
      document.querySelector("#caseFileError").textContent =
        "Choose one culprit.";
      return;
    }
    if (pieces.length < 4 || pieces.length > 5) {
      document.querySelector("#caseFileError").textContent =
        "Choose four or five facts.";
      return;
    }
    if (commitCaseFile(state, caseData, culprit, pieces)) {
      state.rival.accusation = resolveRivalTheory(state, caseData);
      save();
      render();
    } else {
      document.querySelector("#caseFileError").textContent =
        "Choose four or five different facts from your notebook.";
    }
  });
}

function renderSurvey() {
  const playerAccused =
    caseData.suspects.find((s) => s.id === state.caseFile.culprit)?.name ??
    "Unknown";
  const rivalAccused =
    caseData.suspects.find((s) => s.id === state.rival.accusation)?.name ??
    "Unknown";
  app.innerHTML = `<section class="card"><p class="eyebrow">The accusations are locked</p><h2>You accused ${esc(playerAccused)}.</h2><p class="story">${esc(caseData.rival.name)} accused ${esc(rivalAccused)}.</p><p class="story">Before the truth is shown, answer the short post-play survey. Your run ID and playtest telemetry will be prefilled into the existing research form.</p>${storageAvailable ? "" : '<div class="notice" role="status">This browser could not save your Case File. You can continue to the survey, but your individual verdict will be unavailable on return.</div>'}<div class="actions"><button class="primary" id="openSurvey" type="button">Open post-play survey</button></div></section>`;
  document.querySelector("#openSurvey").addEventListener("click", () => {
    markComplete(state);
    markSurveyHandoff(state);
    save();
    window.location.assign(buildSurveyUrl(state));
  });
}

function renderReveal() {
  const verdict = getVerdictView(state, caseData);
  app.innerHTML = `<section class="card"><p class="eyebrow">The Truth</p><h2>Clara Hensley killed Gideon March.</h2><div class="reveal-list story"><div class="truth-step"><strong>At 11:33</strong><p>Gideon had traced his leaked research to Quill. He confronted Clara in the writing room. She struck him with the brass bookend.</p></div><div class="truth-step"><strong>At 11:47</strong><p>Gideon was already dead. Clara had put his recorded cylinder into Quill's concealed apparatus. Quill played her usual cue, unaware that the voice was Gideon's. Clara sat with the guests while it sounded.</p></div><div class="truth-step"><strong>After the voice</strong><p>Rusk found cylinder 43 and hid it to protect the hotel and Quill's fraud. He did not know whose murder he was concealing.</p></div><div class="truth-step"><strong>The other lies</strong><p>Quill concealed the séance trick. Rusk concealed the cylinder. Beatrice concealed her threats and what she heard at Gideon's door. Their reasons were their own; Clara used the confusion.</p></div></div><hr><h3>The Verdict</h3><p>${esc(verdict.message)}</p></section>`;
}

function render() {
  stopLockTimers();
  if (isRevealMode()) return renderReveal();
  renderNotebook();
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

document.addEventListener("visibilitychange", () => {
  if (
    document.visibilityState === "visible" &&
    state?.lock.status === "active" &&
    Date.now() - state.lock.startedAtMs >=
      caseData.competition.rival_finish_seconds * 1000
  )
    finishLock("rival-win");
});

async function boot() {
  loadAttempts += 1;
  const response = await fetch("./case.json", { cache: "no-store" });
  if (!response.ok)
    throw new Error(`Could not load case data: ${response.status}`);
  caseData = await response.json();
  const deviceClass = window.matchMedia("(max-width: 640px)").matches
    ? "mobile"
    : "desktop";
  const ua = navigator.userAgent.toLowerCase();
  const browserClass = ua.includes("firefox")
    ? "firefox"
    : ua.includes("edg/")
      ? "edge"
      : ua.includes("chrome") || ua.includes("crios")
        ? "chrome"
        : ua.includes("safari")
          ? "safari"
          : "other";
  const restored = restoreState(caseData);
  if (isRevealMode()) {
    state = restored;
    if (getVerdictView(state, caseData).available) {
      markRevealReturn(state);
      save();
    } else {
      notebookButton.hidden = true;
    }
    render();
    return;
  }
  state =
    restored ?? createInitialState(caseData, { deviceClass, browserClass });
  save();
  render();
}

function showLoadFailure(error) {
  console.error(error);
  app.innerHTML = `<section class="card"><h2>The case could not be loaded.</h2><p>${loadAttempts < 3 ? "Try loading the case again." : "Reload this page to try again."}</p>${loadAttempts < 3 ? '<button class="primary" id="retryCaseLoad" type="button">Retry loading case</button>' : ""}</section>`;
  document.querySelector("#retryCaseLoad")?.addEventListener("click", () => {
    boot().catch(showLoadFailure);
  });
}

boot().catch(showLoadFailure);
