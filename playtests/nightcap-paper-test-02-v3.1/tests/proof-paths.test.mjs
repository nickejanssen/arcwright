import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import {
  acknowledgeLockResult,
  challengeClaim,
  completeOpening,
  createInitialState,
  enterLastCall,
  evaluateCaseFile,
  followThread,
  openLockWindow,
  resolveLock,
  shouldOpenLockWindow,
  visitInvestigation,
} from "../runtime.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const caseData = JSON.parse(
  fs.readFileSync(path.join(here, "..", "case.json"), "utf8"),
);

function runVisits(targets, lockOutcome = "abort") {
  const state = createInitialState(caseData, {
    nowMs: 0,
    runId: "legal-route",
  });
  assert.equal(completeOpening(state, 1), true);
  for (const [index, target] of targets.entries()) {
    const at = 100 + index * 100;
    assert.equal(visitInvestigation(state, caseData, target, at), true, target);
    if (shouldOpenLockWindow(state, caseData)) {
      assert.equal(openLockWindow(state, at + 1), true);
      assert.equal(resolveLock(state, caseData, lockOutcome, at + 2), true);
      assert.equal(acknowledgeLockResult(state), true);
    }
  }
  return state;
}

function solved(state, pieces) {
  assert.equal(enterLastCall(state, caseData, 1000), true);
  const verdict = evaluateCaseFile(state, caseData, "clara-hensley", pieces);
  assert.deepEqual(verdict, { correct: true, reason: "solved" });
  return verdict;
}

test("Beatrice confrontation yields a four-fact path through five visits", () => {
  const state = runVisits([
    "gideon-materials",
    "seance-room",
    "clara-hensley",
    "beatrice-ashcombe",
    "writing-room",
  ]);
  assert.equal(challengeClaim(state, caseData, "beatrice-ashcombe", 750), true);
  assert.equal(state.majorActions, 5);
  solved(state, [
    "e-beatrice-impact",
    "e-clara-transcribed-43",
    "e-cylinder-transcript",
    "e-service-route",
  ]);
});

test("Rusk chronology works without Beatrice confrontation testimony", () => {
  const state = runVisits([
    "gideon-materials",
    "seance-room",
    "edwin-rusk",
    "clara-hensley",
    "beatrice-ashcombe",
  ]);
  assert.equal(challengeClaim(state, caseData, "edwin-rusk", 710), true);
  assert.equal(followThread(state, caseData, "beatrice-ashcombe", 720), true);
  assert.equal(
    state.discoveries.some((item) => item.id === "e-beatrice-impact"),
    false,
  );
  solved(state, [
    "e-cylinder-transcript",
    "e-rusk-sighting",
    "e-private-detail-match",
    "e-clara-transcribed-43",
    "e-service-route",
  ]);
});

test("lock loss releases a sufficient recording after the next investigation", () => {
  const state = runVisits(
    [
      "gideon-materials",
      "seance-room",
      "clara-hensley",
      "beatrice-ashcombe",
      "writing-room",
    ],
    "rival-win",
  );
  assert.equal(challengeClaim(state, caseData, "beatrice-ashcombe", 750), true);
  assert.equal(
    state.discoveries.some((item) => item.id === "e-cylinder-43"),
    true,
  );
  solved(state, [
    "e-beatrice-impact",
    "e-clara-transcribed-43",
    "e-cylinder-43",
    "e-service-route",
  ]);
});

test("red herring first still reaches a supported case", () => {
  const state = runVisits([
    "lenora-quill",
    "gideon-materials",
    "seance-room",
    "clara-hensley",
    "beatrice-ashcombe",
  ]);
  assert.equal(challengeClaim(state, caseData, "beatrice-ashcombe", 750), true);
  solved(state, [
    "e-beatrice-impact",
    "e-clara-transcribed-43",
    "e-cylinder-transcript",
    "e-service-route",
  ]);
});

test("one Leverage cannot acquire both descriptive motive rewards", () => {
  const state = runVisits([
    "lenora-quill",
    "beatrice-ashcombe",
    "gideon-materials",
    "seance-room",
    "clara-hensley",
  ]);
  assert.equal(followThread(state, caseData, "lenora-quill", 700), true);
  assert.equal(followThread(state, caseData, "beatrice-ashcombe", 710), false);
  assert.equal(
    state.discoveries.some((item) => item.id === "e-quill-payment"),
    true,
  );
  assert.equal(
    state.discoveries.some((item) => item.id === "e-private-detail-match"),
    false,
  );
});

test("unowned fact and culprit guess cannot pass the scorer", () => {
  const state = runVisits([
    "gideon-materials",
    "seance-room",
    "clara-hensley",
    "beatrice-ashcombe",
    "writing-room",
  ]);
  assert.equal(enterLastCall(state, caseData, 1000), true);
  assert.deepEqual(evaluateCaseFile(state, caseData, "clara-hensley", []), {
    correct: false,
    reason: "choose-four-or-five",
  });
  assert.deepEqual(
    evaluateCaseFile(state, caseData, "clara-hensley", [
      "e-beatrice-impact",
      "e-clara-transcribed-43",
      "e-cylinder-transcript",
      "e-private-detail-match",
    ]),
    { correct: false, reason: "unowned-evidence" },
  );
});
