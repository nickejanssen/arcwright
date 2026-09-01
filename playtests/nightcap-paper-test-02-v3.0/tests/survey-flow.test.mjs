import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import {
  buildSurveyUrl,
  createInitialState,
  markComplete,
  markSurveyHandoff
} from "../runtime.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const appSource = fs.readFileSync(path.join(here, "..", "app.js"), "utf8");
const caseData = JSON.parse(fs.readFileSync(path.join(here, "..", "case.json"), "utf8"));

test("survey screen does not expose a truth-preview bypass", () => {
  assert.equal(appSource.includes("Preview reveal locally"), false);
  assert.equal(appSource.includes('href="?reveal=1"'), false);
});

test("survey handoff records gameplay completion before leaving the fixture", () => {
  const completeIndex = appSource.indexOf("markComplete(state);");
  const handoffIndex = appSource.indexOf("markSurveyHandoff(state);");
  assert.ok(completeIndex >= 0);
  assert.ok(handoffIndex >= 0);
  assert.ok(completeIndex < handoffIndex);
});

test("completed gameplay telemetry can be prefilled into the existing form", () => {
  const state = createInitialState(caseData, { nowMs: 1000, runId: "run-survey-complete" });
  markComplete(state, 5000);
  markSurveyHandoff(state, 5100);
  const url = new URL(buildSurveyUrl(state));
  assert.equal(url.searchParams.get("q14_textbox12"), "run-survey-complete");
  assert.equal(url.searchParams.get("q16_textbox14"), new Date(5000).toISOString());
  assert.equal(url.searchParams.get("q26_textbox24"), "completed");
});
