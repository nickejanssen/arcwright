import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { URL, fileURLToPath } from "node:url";
import {
  buildSurveyUrl,
  createInitialState,
  deriveTelemetry,
  recordEvent,
  setPrivateNotes,
} from "../runtime.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const caseData = JSON.parse(
  fs.readFileSync(path.join(here, "..", "case.json"), "utf8"),
);

test("1,000 miss transport round-trips canonical events without private notes", () => {
  const state = createInitialState(caseData, {
    nowMs: 1000,
    runId: "transport-stress",
  });
  setPrivateNotes(state, "PRIVATE NOTE MUST NOT TRAVEL");
  for (let index = 0; index < 1000; index += 1) {
    recordEvent(
      state,
      {
        event_type: "minigame_action",
        target: `pin-${(index % 4) + 1}`,
        choice: String(index % 100),
        outcome: "miss",
      },
      1000 + index,
    );
  }
  const url = buildSurveyUrl(state);
  const encodedBytes = Buffer.byteLength(url, "utf8");
  const decoded = new URL(url);
  assert.equal(decoded.searchParams.get("q14_textbox12"), "transport-stress");
  assert.equal(decoded.searchParams.get("q13_textbox11"), "3.1");
  assert.equal(
    decoded.searchParams.get("q30_event_sequence"),
    JSON.stringify(state.eventSequence),
  );
  assert.deepEqual(
    JSON.parse(decoded.searchParams.get("q30_event_sequence")),
    state.eventSequence,
  );
  assert.equal(
    deriveTelemetry(state).event_sequence,
    JSON.stringify(state.eventSequence),
  );
  assert.ok(encodedBytes > 1000);
  assert.equal(url.includes("PRIVATE NOTE MUST NOT TRAVEL"), false);
  process.stdout.write(`transport_stress_encoded_bytes=${encodedBytes}\n`);
});
