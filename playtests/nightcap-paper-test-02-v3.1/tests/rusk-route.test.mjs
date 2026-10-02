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

test("Rusk chronology route can solve without Beatrice confrontation testimony", () => {
  const state = createInitialState(caseData, {
    nowMs: 0,
    runId: "run-rusk-route",
  });
  assert.equal(completeOpening(state, 1), true);
  for (const [index, target] of [
    "gideon-materials",
    "seance-room",
    "edwin-rusk",
    "clara-hensley",
    "beatrice-ashcombe",
  ].entries()) {
    const now = 100 + index * 100;
    assert.equal(visitInvestigation(state, caseData, target, now), true);
    if (shouldOpenLockWindow(state, caseData)) {
      assert.equal(openLockWindow(state, caseData, now + 1), true);
      assert.equal(resolveLock(state, caseData, "abort", now + 2), true);
      assert.equal(acknowledgeLockResult(state), true);
    }
  }
  assert.equal(challengeClaim(state, caseData, "edwin-rusk", 700), true);
  assert.equal(followThread(state, caseData, "beatrice-ashcombe", 710), true);
  const pieces = [
    "e-cylinder-transcript",
    "e-rusk-sighting",
    "e-private-detail-match",
    "e-clara-transcribed-43",
    "e-service-route",
  ];
  assert.equal(enterLastCall(state, caseData, 800), true);
  assert.deepEqual(evaluateCaseFile(state, caseData, "clara-hensley", pieces), {
    correct: true,
    reason: "solved",
  });
  assert.equal(
    state.discoveries.some((item) => item.id === "e-beatrice-impact"),
    false,
  );
});
