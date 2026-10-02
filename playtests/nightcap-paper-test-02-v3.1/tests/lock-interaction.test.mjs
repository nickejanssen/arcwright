import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import {
  acknowledgeLockResult,
  attemptLockPin,
  completeOpening,
  createInitialState,
  deriveTelemetry,
  declineLockWindow,
  enterLastCall,
  openLockWindow,
  releaseCylinderPublicly,
  resolveLock,
  resolveRivalTheory,
  restoreState,
  saveLeverage,
  spendLeverage,
  triggerRivalActivity,
  visitInvestigation,
} from "../runtime.js";
import { classifyLeverage } from "../research.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const caseData = JSON.parse(
  fs.readFileSync(path.join(here, "..", "case.json"), "utf8"),
);
const makeState = (eligible = true) => {
  const state = createInitialState(caseData, { nowMs: 0, runId: "lock-test" });
  completeOpening(state, 1);
  if (eligible) {
    visitInvestigation(state, caseData, "seance-room", 100);
    visitInvestigation(state, caseData, "gideon-materials", 200);
  }
  return state;
};
const events = (state, type) =>
  state.eventSequence.filter((event) => event.event_type === type);

test("Start and Decline reject a lock window before the authored trigger", () => {
  const start = makeState(false);
  const decline = makeState(false);
  assert.equal(start.majorActions, 0);
  assert.equal(openLockWindow(start, caseData, 1000), false);
  assert.equal(declineLockWindow(decline, caseData, 1000), false);
  for (const state of [start, decline]) {
    assert.equal(state.lock.status, "unavailable");
    assert.equal(state.lock.startedAtMs, null);
    assert.equal(state.discoveries.length, 0);
    assert.equal(state.eventSequence.length, 1);
  }
});

test("ready state is untimed; decline grants public evidence without a minigame", () => {
  const state = makeState();
  assert.equal(state.lock.status, "unavailable");
  assert.equal(state.lock.startedAtMs, null);
  assert.equal(declineLockWindow(state, caseData, 90000), true);
  assert.equal(declineLockWindow(state, caseData, 91000), false);
  assert.equal(state.lock.outcome, "declined");
  assert.equal(state.lock.publicReleased, true);
  assert.equal(
    state.discoveries.filter((item) => item.id === "e-cylinder-43").length,
    1,
  );
  assert.equal(state.leverage, 1);
  assert.equal(events(state, "competitive_window_declined").length, 1);
  assert.equal(events(state, "minigame_started").length, 0);
  assert.equal(events(state, "minigame_result").length, 0);
  assert.equal(events(state, "first_look_closed").length, 0);
  assert.equal(deriveTelemetry(state).lock_completion_seconds, "");
  assert.equal(openLockWindow(state, caseData, 92000), false);
});

test("the exact rival deadline resolves before a queued pin and only once", () => {
  const state = makeState();
  openLockWindow(state, caseData, 1000);
  assert.equal(state.lock.startedAtMs, 1000);
  const first = attemptLockPin(state, caseData, 22, 20000);
  assert.deepEqual(first, {
    accepted: false,
    outcome: "rival-win",
    pinIndex: 0,
  });
  assert.equal(events(state, "minigame_action").length, 0);
  assert.equal(events(state, "minigame_result").length, 1);
  assert.equal(state.lock.winner, "rival");
  assert.equal(attemptLockPin(state, caseData, 22, 21000).accepted, false);
  assert.equal(resolveLock(state, caseData, "human-win", 21000), false);
  assert.equal(events(state, "minigame_result").length, 1);
});

test("last displayed value wins before the deadline; resume cannot grant a late human win", () => {
  const state = makeState();
  openLockWindow(state, caseData, 1000);
  assert.deepEqual(attemptLockPin(state, caseData, 22, 19999), {
    accepted: true,
    outcome: "set",
    pinIndex: 0,
  });
  assert.equal(state.lock.currentPin, 1);
  const storage = { getItem: () => JSON.stringify(state) };
  const resumed = restoreState(caseData, storage);
  assert.equal(
    attemptLockPin(resumed, caseData, 68, 20000).outcome,
    "rival-win",
  );
  assert.equal(resumed.lock.currentPin, 1);
});

test("a fourth pin queued at the exact deadline is a rival win", () => {
  const state = makeState();
  openLockWindow(state, caseData, 1000);
  for (let pin = 0; pin < 3; pin += 1)
    assert.equal(
      attemptLockPin(
        state,
        caseData,
        caseData.competition.pins[pin].target,
        2000 + pin,
      ).outcome,
      "set",
    );
  assert.equal(
    attemptLockPin(state, caseData, caseData.competition.pins[3].target, 20000)
      .outcome,
    "rival-win",
  );
  assert.equal(state.lock.currentPin, 3);
  assert.equal(events(state, "minigame_result").length, 1);
});

test("first look closes on next new investigation or Last Call, not free review", () => {
  const state = makeState();
  state.phase = "investigation";
  openLockWindow(state, caseData, 1000);
  resolveLock(state, caseData, "human-win", 2000);
  acknowledgeLockResult(state);
  assert.equal(state.lock.publicReleased, false);
  assert.equal(visitInvestigation(state, caseData, "writing-room", 3000), true);
  assert.equal(state.lock.publicReleased, true);
  assert.equal(events(state, "first_look_closed").length, 1);
  assert.equal(releaseCylinderPublicly(state, caseData, 4000), false);
  assert.equal(events(state, "first_look_closed").length, 1);
  const second = makeState();
  second.phase = "investigation";
  second.majorActions = 5;
  openLockWindow(second, caseData, 1000);
  resolveLock(second, caseData, "human-win", 2000);
  acknowledgeLockResult(second);
  assert.equal(enterLastCall(second, caseData, 3000), true);
  assert.equal(events(second, "first_look_closed").length, 1);
});

test("human win can explicitly save once and later spend; zero balance cannot save", () => {
  const state = makeState();
  openLockWindow(state, caseData, 1000);
  resolveLock(state, caseData, "human-win", 2000);
  assert.equal(saveLeverage(state, "first-look", 2100), true);
  assert.equal(saveLeverage(state, "first-look", 2200), false);
  assert.equal(
    events(state, "leverage_choice").filter((item) => item.choice === "save")
      .length,
    1,
  );
  assert.equal(spendLeverage(state, caseData, "follow-the-thread", 2300), true);
  assert.equal(state.leverage, 0);
  assert.equal(saveLeverage(state, "first-look", 2400), false);
  assert.deepEqual(classifyLeverage(state.eventSequence, 1), {
    spent: 1,
    explicitlySaved: 1,
    remaining: 0,
    unused: 0,
  });
  const zero = makeState();
  spendLeverage(zero, caseData, "follow-the-thread", 100);
  openLockWindow(zero, caseData, 1000);
  resolveLock(zero, caseData, "human-win", 2000);
  assert.equal(saveLeverage(zero, "first-look", 2100), false);
});

test("rival theory follows authored public evidence and ignores human-private lock facts", () => {
  const human = makeState();
  const rival = makeState();
  openLockWindow(human, caseData, 1000);
  openLockWindow(rival, caseData, 1000);
  resolveLock(human, caseData, "human-win", 2000);
  resolveLock(rival, caseData, "rival-win", 2000);
  assert.equal(
    resolveRivalTheory(human, caseData),
    resolveRivalTheory(rival, caseData),
  );
  assert.equal(human.rival.lockObservation, null);
  assert.ok(rival.rival.lockObservation);
  assert.equal(
    resolveRivalTheory(rival, caseData),
    caseData.rival.theory.accusation,
  );
  assert.equal(
    triggerRivalActivity(rival, caseData, "followed", "edwin-rusk", 3000),
    true,
  );
  assert.equal(
    rival.rival.knownFacts.includes("rusk-checked-service-corridor"),
    true,
  );
  assert.equal(
    triggerRivalActivity(rival, caseData, "followed", "edwin-rusk", 3001),
    false,
  );
});
