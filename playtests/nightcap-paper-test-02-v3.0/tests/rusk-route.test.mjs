import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import {
  completeOpening,
  createInitialState,
  enterLastCall,
  evaluateCaseFile,
  recordDiscovery
} from "../runtime.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const caseData = JSON.parse(fs.readFileSync(path.join(here, "..", "case.json"), "utf8"));

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

test("Rusk chronology route can solve without Beatrice testimony", () => {
  const state = createInitialState(caseData, { nowMs: 0, runId: "run-rusk-route" });
  completeOpening(state, 1);
  state.phase = "investigation";
  state.majorActions = 5;

  const pieces = [
    "e-cylinder-transcript",
    "e-rusk-sighting",
    "e-private-detail-match",
    "e-clara-transcribed-43",
    "e-service-route"
  ];
  for (const id of pieces) {
    const found = discovery(id);
    assert.ok(found, `missing fixture discovery ${id}`);
    recordDiscovery(state, found, {}, 1000);
  }

  assert.equal(enterLastCall(state, caseData, 2000), true);
  const verdict = evaluateCaseFile(state, caseData, "clara-hensley", pieces);
  assert.equal(verdict.correct, true);
  assert.equal(pieces.some((id) => id.startsWith("e-beatrice-")), false);
});
