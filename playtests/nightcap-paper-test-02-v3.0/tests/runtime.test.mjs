import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import {
  acknowledgeLockResult,
  buildSurveyUrl,
  chooseInvestigation,
  commitCaseFile,
  completeOpening,
  createInitialState,
  deriveTelemetry,
  enterLastCall,
  evaluateCaseFile,
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
  spendLeverage
} from "../runtime.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const caseData = JSON.parse(fs.readFileSync(path.join(here, "..", "case.json"), "utf8"));

function memoryStorage() {
  const data = new Map();
  return {
    getItem: (key) => data.has(key) ? data.get(key) : null,
    setItem: (key, value) => data.set(key, String(value))
  };
}

function discovery(id) {
  const all = [
    ...Object.values(caseData.investigation.routes).flatMap((route) => route.discoveries ?? []),
    ...Object.values(caseData.interviews).flatMap((interview) => [
      ...(interview.discoveries ?? []),
      ...(interview.conditional?.discoveries ?? []),
      ...(interview.follow_thread?.discovery ? [interview.follow_thread.discovery] : [])
    ]),
    caseData.competition.winner_private_observation
  ];
  return all.find((item) => item.id === id);
}

test("initial state is versioned, private, and starts with one test-granted Leverage", () => {
  const state = createInitialState(caseData, { nowMs: 1000, runId: "run-1" });
  assert.equal(state.fixtureVersion, "3.0");
  assert.equal(state.phase, "opening");
  assert.equal(state.runId, "run-1");
  assert.equal(state.leverage, 1);
  assert.deepEqual(state.discoveries, []);
  assert.deepEqual(state.investigatedTargets, []);
  assert.equal(state.lock.status, "unavailable");
});

test("event sequence is ordered and elapsed from one session clock", () => {
  const state = createInitialState(caseData, { nowMs: 1000, runId: "run-1" });
  completeOpening(state, 1500);
  chooseInvestigation(state, "writing-room", 2200);
  assert.deepEqual(state.eventSequence.map((event) => event.sequence), [1, 2]);
  assert.equal(state.eventSequence[1].elapsed_ms, 1200);
  assert.equal(state.eventSequence[1].event_type, "investigation_choice");
});

test("session state restores without duplicating major choices", () => {
  const storage = memoryStorage();
  const state = createInitialState(caseData, { nowMs: 1000, runId: "run-restore" });
  completeOpening(state, 1200);
  assert.equal(chooseInvestigation(state, "writing-room", 1500), true);
  persistState(state, storage);
  const restored = restoreState(caseData, storage);
  assert.equal(restored.runId, "run-restore");
  assert.equal(chooseInvestigation(restored, "writing-room", 1700), false);
  assert.equal(restored.majorActions, 1);
});

test("lock opens from case evidence or authored rival trigger", () => {
  const state = createInitialState(caseData, { nowMs: 0, runId: "run-lock" });
  completeOpening(state, 1);
  chooseInvestigation(state, "gideon-materials", 1000);
  recordDiscovery(state, discovery("e-cylinder-transcript"), {}, 1100);
  assert.equal(shouldOpenLockWindow(state, caseData), false);
  chooseInvestigation(state, "clara-hensley", 2000);
  assert.equal(shouldOpenLockWindow(state, caseData), true);
});

test("human lock win gives private first look then public release without duplicate evidence", () => {
  const state = createInitialState(caseData, { nowMs: 0, runId: "run-human-win" });
  completeOpening(state, 1);
  openLockWindow(state, 1000);
  for (let pin = 0; pin < 4; pin += 1) setLockProgress(state, pin, caseData.competition.pins[pin].target, "set", 1100 + pin * 100);
  assert.equal(resolveLock(state, caseData, "human-win", 1800), true);
  assert.equal(state.phase, "lock");
  assert.equal(state.privateDiscoveries.some((item) => item.id === "e-cylinder-43"), true);
  assert.equal(state.discoveries.some((item) => item.id === "e-cylinder-43"), false);
  assert.equal(resolveLock(state, caseData, "human-win", 1900), false);
  releaseCylinderPublicly(state, caseData, 3000);
  assert.equal(state.privateDiscoveries.some((item) => item.id === "e-cylinder-43"), false);
  assert.equal(state.discoveries.filter((item) => item.id === "e-cylinder-43").length, 1);
});

test("rival win offers meaningful Listen In spend or save", () => {
  const spendState = createInitialState(caseData, { nowMs: 0, runId: "run-rival-spend" });
  completeOpening(spendState, 1);
  openLockWindow(spendState, 1000);
  resolveLock(spendState, caseData, "rival-win", 5000);
  assert.equal(spendLeverage(spendState, caseData, "listen-in", 5100), true);
  assert.equal(spendState.leverage, 0);
  assert.equal(spendState.privateDiscoveries.some((item) => item.id === "e-cylinder-43"), true);

  const saveState = createInitialState(caseData, { nowMs: 0, runId: "run-rival-save" });
  completeOpening(saveState, 1);
  openLockWindow(saveState, 1000);
  resolveLock(saveState, caseData, "rival-win", 5000);
  saveLeverage(saveState, "listen-in", 5100);
  assert.equal(saveState.leverage, 1);
  assert.equal(saveState.privateDiscoveries.some((item) => item.id === "e-cylinder-43"), false);
});

test("break timeout and abort all preserve cylinder access through public fallback", () => {
  for (const outcome of ["break", "timeout", "abort"]) {
    const state = createInitialState(caseData, { nowMs: 0, runId: `run-${outcome}` });
    completeOpening(state, 1);
    openLockWindow(state, 1000);
    resolveLock(state, caseData, outcome, 3000);
    assert.equal(state.discoveries.some((item) => item.id === "e-cylinder-43"), true, outcome);
    assert.equal(state.lock.publicReleased, true, outcome);
  }
});

test("refresh after lock resolution cannot award a second result", () => {
  const storage = memoryStorage();
  const state = createInitialState(caseData, { nowMs: 0, runId: "run-refresh-lock" });
  completeOpening(state, 1);
  openLockWindow(state, 1000);
  resolveLock(state, caseData, "human-win", 2000);
  persistState(state, storage);
  const restored = restoreState(caseData, storage);
  assert.equal(resolveLock(restored, caseData, "rival-win", 3000), false);
  assert.equal(restored.eventSequence.filter((event) => event.event_type === "minigame_result").length, 1);
});

test("Follow the Thread has one real opportunity cost", () => {
  const state = createInitialState(caseData, { nowMs: 0, runId: "run-follow" });
  assert.equal(spendLeverage(state, caseData, "follow-the-thread", 1000), true);
  assert.equal(state.leverage, 0);
  assert.equal(spendLeverage(state, caseData, "follow-the-thread", 1200), false);
});

test("Case File requires Clara plus owned causal evidence covering all required truths", () => {
  const state = createInitialState(caseData, { nowMs: 0, runId: "run-case" });
  completeOpening(state, 1);
  state.phase = "investigation";
  state.majorActions = 5;
  for (const id of ["e-cylinder-transcript", "e-beatrice-impact", "e-clara-transcribed-43", "e-service-route"]) recordDiscovery(state, discovery(id), {}, 1000);
  enterLastCall(state, caseData, 2000);
  const good = evaluateCaseFile(state, caseData, "clara-hensley", ["e-cylinder-transcript", "e-beatrice-impact", "e-clara-transcribed-43", "e-service-route"]);
  assert.equal(good.correct, true);
  const culpritOnly = evaluateCaseFile(state, caseData, "clara-hensley", []);
  assert.equal(culpritOnly.correct, false);
  assert.equal(commitCaseFile(state, caseData, "clara-hensley", ["e-cylinder-transcript", "e-beatrice-impact", "e-clara-transcribed-43", "e-service-route"], 2200), true);
  assert.equal(state.caseFile.correct, true);
});

test("unowned evidence cannot be smuggled into the reconstruction", () => {
  const state = createInitialState(caseData, { nowMs: 0, runId: "run-unowned" });
  const verdict = evaluateCaseFile(state, caseData, "clara-hensley", ["e-cylinder-transcript", "e-beatrice-impact", "e-clara-transcribed-43", "e-service-route"]);
  assert.equal(verdict.reason, "unowned-evidence");
});

test("telemetry derives investigation, inference, lock, return, and same run id", () => {
  const state = createInitialState(caseData, { nowMs: 0, runId: "run-telemetry", deviceClass: "mobile", browserClass: "chrome" });
  completeOpening(state, 500);
  chooseInvestigation(state, "gideon-materials", 1500);
  recordDiscovery(state, discovery("e-cylinder-transcript"), {}, 1700);
  recordInferenceAction(state, "clara-hensley", "challenge-timeline", "opened", 2500);
  openLockWindow(state, 3000);
  resolveLock(state, caseData, "break", 7000);
  acknowledgeLockResult(state);
  chooseInvestigation(state, "lenora-quill", 9000);
  const telemetry = deriveTelemetry(state);
  assert.equal(telemetry.run_id, "run-telemetry");
  assert.equal(telemetry.device_class, "mobile");
  assert.equal(telemetry.browser_class, "chrome");
  assert.equal(telemetry.time_to_first_investigation_seconds, 2);
  assert.equal(telemetry.time_to_first_discovery_seconds, 2);
  assert.equal(telemetry.time_to_first_inference_seconds, 3);
  assert.equal(telemetry.pulse_result, "break");
  assert.equal(telemetry.lock_completion_seconds, 4);
  assert.equal(telemetry.post_lock_return_seconds, 2);
});

test("survey URL carries the same run id and handoff is single-fire", () => {
  const state = createInitialState(caseData, { nowMs: 0, runId: "run-survey" });
  markSurveyHandoff(state, 1000);
  assert.equal(markSurveyHandoff(state, 1100), false);
  const url = new URL(buildSurveyUrl(state));
  assert.equal(url.searchParams.get("q14_textbox12"), "run-survey");
});

test("reveal return is locally observable once but not represented as external proof", () => {
  const state = createInitialState(caseData, { nowMs: 0, runId: "run-reveal" });
  assert.equal(markRevealReturn(state, 1000), true);
  assert.equal(markRevealReturn(state, 2000), false);
  const event = state.eventSequence.find((item) => item.event_type === "reveal_return");
  assert.equal(event.outcome, "local-session-state-only");
});


test("partial Case File selections survive refresh", () => {
  const storage = memoryStorage();
  const state = createInitialState(caseData, { nowMs: 0, runId: "run-draft" });
  state.phase = "last-call";
  setCaseFileDraft(state, "clara-hensley", ["e-cylinder-transcript", "e-beatrice-impact"]);
  persistState(state, storage);
  const restored = restoreState(caseData, storage);
  assert.equal(restored.caseFile.draftCulprit, "clara-hensley");
  assert.deepEqual(restored.caseFile.draftPieces, ["e-cylinder-transcript", "e-beatrice-impact"]);
});

test("lock failure still permits a complete correct reconstruction", () => {
  const state = createInitialState(caseData, { nowMs: 0, runId: "run-lock-fallback-solve" });
  completeOpening(state, 1);
  openLockWindow(state, 1000);
  resolveLock(state, caseData, "break", 2000);
  acknowledgeLockResult(state);
  for (const id of ["e-beatrice-impact", "e-clara-transcribed-43", "e-service-route"]) recordDiscovery(state, discovery(id), {}, 3000);
  state.majorActions = 5;
  enterLastCall(state, caseData, 4000);
  const verdict = evaluateCaseFile(state, caseData, "clara-hensley", ["e-cylinder-43", "e-beatrice-impact", "e-clara-transcribed-43", "e-service-route"]);
  assert.equal(verdict.correct, true);
});
