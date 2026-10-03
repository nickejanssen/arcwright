import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import {
  acknowledgeLockResult,
  completeOpening,
  createInitialState,
  declineLockWindow,
  openLockWindow,
  recordDiscovery,
  releaseCylinderPublicly,
  resolveLock,
  visitInvestigation,
} from "../runtime.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const caseData = JSON.parse(
  fs.readFileSync(path.join(here, "..", "case.json"), "utf8"),
);
const cylinder = caseData.competition.fallback_public_observation;
const events = (state, type) =>
  state.eventSequence.filter((event) => event.event_type === type);

function lockReady() {
  const state = createInitialState(caseData, {
    nowMs: 0,
    runId: "qa-contract",
  });
  completeOpening(state, 1);
  assert.equal(visitInvestigation(state, caseData, "seance-room", 100), true);
  assert.equal(
    visitInvestigation(state, caseData, "gideon-materials", 200),
    true,
  );
  return state;
}

test("one private observation can become public once without a second award", () => {
  const state = lockReady();
  assert.equal(
    recordDiscovery(state, cylinder, { visibility: "private" }, 300),
    true,
  );
  assert.equal(
    recordDiscovery(state, cylinder, { visibility: "private" }, 301),
    false,
  );
  assert.equal(releaseCylinderPublicly(state, caseData, 302), true);
  assert.equal(releaseCylinderPublicly(state, caseData, 303), false);
  assert.equal(
    state.privateDiscoveries.some((item) => item.id === cylinder.id),
    false,
  );
  assert.equal(
    state.discoveries.filter((item) => item.id === cylinder.id).length,
    1,
  );
  assert.deepEqual(
    events(state, "discovery")
      .filter((event) => event.target === cylinder.id)
      .map((event) => event.outcome),
    ["private", "public"],
  );
  assert.equal(events(state, "first_look_closed").length, 1);
});

for (const outcome of ["break", "abort"]) {
  test(`${outcome} releases public evidence immediately without first-look expiry`, () => {
    const state = lockReady();
    assert.equal(openLockWindow(state, caseData, 1000), true);
    assert.equal(resolveLock(state, caseData, outcome, 2000), true);
    assert.equal(state.lock.publicReleased, true);
    assert.equal(
      state.discoveries.filter((item) => item.id === cylinder.id).length,
      1,
    );
    assert.equal(
      events(state, "discovery").filter(
        (event) => event.target === cylinder.id && event.outcome === "public",
      ).length,
      1,
    );
    assert.equal(events(state, "first_look_closed").length, 0);
    assert.equal(acknowledgeLockResult(state), true);
    assert.equal(
      visitInvestigation(state, caseData, "writing-room", 3000),
      true,
    );
    assert.equal(events(state, "first_look_closed").length, 0);
    assert.equal(
      events(state, "discovery").filter((event) => event.target === cylinder.id)
        .length,
      1,
    );
  });
}

test("decline releases public evidence immediately without a played lock or delayed expiry", () => {
  const state = lockReady();
  assert.equal(declineLockWindow(state, caseData, 1000), true);
  assert.equal(state.lock.publicReleased, true);
  assert.equal(
    state.discoveries.filter((item) => item.id === cylinder.id).length,
    1,
  );
  assert.equal(events(state, "minigame_started").length, 0);
  assert.equal(events(state, "minigame_result").length, 0);
  assert.equal(events(state, "first_look_closed").length, 0);
  assert.equal(visitInvestigation(state, caseData, "writing-room", 3000), true);
  assert.equal(events(state, "first_look_closed").length, 0);
  assert.equal(
    events(state, "discovery").filter((event) => event.target === cylinder.id)
      .length,
    1,
  );
});
