import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import * as runtime from "../runtime.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const caseData = JSON.parse(
  fs.readFileSync(path.join(here, "..", "case.json"), "utf8"),
);

function fresh() {
  const state = runtime.createInitialState(caseData, {
    nowMs: 0,
    runId: "task-2",
  });
  runtime.completeOpening(state, 1);
  return state;
}

function visit(state, target, at) {
  assert.equal(typeof runtime.visitInvestigation, "function");
  assert.equal(runtime.visitInvestigation(state, caseData, target, at), true);
  if (runtime.shouldOpenLockWindow(state, caseData)) {
    assert.equal(runtime.openLockWindow(state, caseData, at + 1), true);
    assert.equal(runtime.resolveLock(state, caseData, "abort", at + 2), true);
    assert.equal(runtime.acknowledgeLockResult(state), true);
  }
}

test("fifth action opens Last Call, sixth is final, and seventh is rejected", () => {
  const state = fresh();
  for (const [index, target] of [
    "writing-room",
    "gideon-materials",
    "seance-room",
    "clara-hensley",
    "beatrice-ashcombe",
  ].entries()) {
    visit(state, target, 100 + index * 100);
  }
  assert.equal(state.majorActions, 5);
  assert.equal(runtime.canEnterLastCall(state, caseData), true);
  visit(state, "edwin-rusk", 700);
  assert.equal(state.majorActions, 6);
  const eventCount = state.eventSequence.length;
  assert.equal(
    runtime.visitInvestigation(state, caseData, "lenora-quill", 800),
    false,
  );
  assert.equal(state.majorActions, 6);
  assert.equal(state.eventSequence.length, eventCount);
  assert.equal(runtime.enterLastCall(state, caseData, 900), true);
  assert.equal(
    runtime.visitInvestigation(state, caseData, "lenora-quill", 1000),
    false,
  );
});

test("earned challenge stays free at cap and cannot grant twice", () => {
  const state = fresh();
  for (const [index, target] of [
    "gideon-materials",
    "writing-room",
    "seance-room",
    "clara-hensley",
    "beatrice-ashcombe",
    "edwin-rusk",
  ].entries())
    visit(state, target, 100 + index * 100);
  assert.equal(typeof runtime.challengeClaim, "function");
  const eventsBefore = state.eventSequence.length;
  assert.equal(
    runtime.challengeClaim(state, caseData, "edwin-rusk", 750),
    true,
  );
  assert.equal(state.majorActions, 6);
  assert.equal(
    state.discoveries.filter((item) => item.id === "e-rusk-sighting").length,
    1,
  );
  assert.equal(
    runtime.challengeClaim(state, caseData, "edwin-rusk", 760),
    false,
  );
  assert.equal(state.eventSequence.length, eventsBefore + 3);
  assert.equal(runtime.enterLastCall(state, caseData, 800), true);
  assert.equal(
    runtime.challengeClaim(state, caseData, "beatrice-ashcombe", 810),
    false,
  );
});

test("restored legacy facts block challenge replay without encounter history", () => {
  const state = fresh();
  visit(state, "gideon-materials", 100);
  visit(state, "edwin-rusk", 200);
  assert.equal(
    runtime.challengeClaim(state, caseData, "edwin-rusk", 300),
    true,
  );
  delete state.encounterHistory;
  const saved = JSON.stringify(state);
  const storage = { getItem: () => saved };
  const restored = runtime.restoreState(caseData, storage);
  const before = JSON.stringify(restored.eventSequence);
  assert.equal(
    runtime.canChallengeClaim(restored, caseData, "edwin-rusk"),
    false,
  );
  assert.equal(
    runtime.challengeClaim(restored, caseData, "edwin-rusk", 400),
    false,
  );
  assert.equal(JSON.stringify(restored.eventSequence), before);
  assert.equal(
    restored.discoveries.filter((item) => item.id === "e-rusk-sighting").length,
    1,
  );
});

test("single paid follow-up requires its context and remains available at cap", () => {
  const state = fresh();
  assert.equal(typeof runtime.followThread, "function");
  assert.equal(
    runtime.followThread(state, caseData, "beatrice-ashcombe", 50),
    false,
  );
  for (const [index, target] of [
    "gideon-materials",
    "writing-room",
    "seance-room",
    "clara-hensley",
    "beatrice-ashcombe",
    "edwin-rusk",
  ].entries())
    visit(state, target, 100 + index * 100);
  assert.equal(
    runtime.followThread(state, caseData, "beatrice-ashcombe", 750),
    true,
  );
  assert.equal(state.leverage, 0);
  assert.equal(state.followThreadUsed, true);
  assert.equal(state.majorActions, 6);
  assert.equal(runtime.followThread(state, caseData, "edwin-rusk", 760), false);
  assert.equal(
    runtime.followThread(state, caseData, "beatrice-ashcombe", 770),
    false,
  );
});

test("challenge rejects unowned prompt facts and unvisited suspects", () => {
  const state = fresh();
  assert.equal(typeof runtime.challengeClaim, "function");
  assert.equal(
    runtime.challengeClaim(state, caseData, "edwin-rusk", 50),
    false,
  );
  visit(state, "edwin-rusk", 100);
  assert.equal(
    runtime.challengeClaim(state, caseData, "edwin-rusk", 150),
    false,
  );
  visit(state, "gideon-materials", 200);
  assert.equal(
    runtime.challengeClaim(state, caseData, "edwin-rusk", 250),
    true,
  );
});

test("journal review is earned, idempotent and read only", () => {
  const state = fresh();
  assert.equal(typeof runtime.reviewEncounter, "function");
  assert.equal(runtime.reviewEncounter(state, "route:writing-room"), null);
  visit(state, "writing-room", 100);
  const before = JSON.stringify(state);
  const entry = runtime.reviewEncounter(state, "route:writing-room");
  assert.equal(entry.targetId, "writing-room");
  assert.match(entry.scene, /bookend/i);
  assert.deepEqual(entry.discoveryIds, ["e-bookend", "e-gideon-final-note"]);
  assert.equal(JSON.stringify(state), before);
  assert.equal(
    runtime.visitInvestigation(state, caseData, "writing-room", 200),
    false,
  );
  assert.equal(state.encounterHistory.length, 1);
});

test("private notes cap at 500 and never enter proof, events or survey URL", () => {
  const state = fresh();
  assert.equal(typeof runtime.setPrivateNotes, "function");
  const stored = runtime.setPrivateNotes(
    state,
    "e-cylinder-transcript " + "x".repeat(600),
  );
  assert.equal(Array.from(stored).length, 500);
  assert.equal(state.privateNotes, stored);
  assert.equal(
    runtime.ownedEvidenceIds(state).has("e-cylinder-transcript"),
    false,
  );
  assert.equal(
    runtime.evaluateCaseFile(state, caseData, "clara-hensley", [
      "e-cylinder-transcript",
      "a",
      "b",
      "c",
    ]).reason,
    "unowned-evidence",
  );
  assert.equal(
    JSON.stringify(state.eventSequence).includes("e-cylinder-transcript"),
    false,
  );
  assert.equal(
    JSON.stringify(runtime.deriveTelemetry(state)).includes(stored),
    false,
  );
  assert.equal(
    decodeURIComponent(runtime.buildSurveyUrl(state)).includes(stored),
    false,
  );
  delete state.encounterHistory;
  delete state.privateNotes;
  assert.equal(runtime.reviewEncounter(state, "route:writing-room"), null);
  assert.equal(runtime.setPrivateNotes(state, "short"), "short");
});
