import assert from "node:assert/strict";
import test from "node:test";
import {
  classifyLeverage,
  firstTargetGate,
  postLockTimingGate,
} from "../research.js";

test("Leverage counts explicit actions without assigning intent to unused balance", () => {
  assert.deepEqual(classifyLeverage([], 1), {
    spent: 0,
    explicitlySaved: 0,
    remaining: 1,
    unused: 1,
  });
  assert.deepEqual(
    classifyLeverage([{ event_type: "leverage_choice", choice: "save" }], 1),
    { spent: 0, explicitlySaved: 1, remaining: 1, unused: 1 },
  );
  assert.deepEqual(
    classifyLeverage(
      [
        { event_type: "leverage_choice", choice: "save" },
        { event_type: "leverage_choice", choice: "spend" },
        { event_type: "inference_action", choice: "spend" },
      ],
      1,
    ),
    { spent: 1, explicitlySaved: 1, remaining: 0, unused: 0 },
  );
});

test("first-target bounds preserve missingness at the 75 percent gate", () => {
  assert.deepEqual(firstTargetGate([]), {
    status: "inconclusive",
    included: 0,
    measured: 0,
    missing: 0,
    maxObserved: 0,
    lowerConcentration: null,
    upperConcentration: null,
  });
  assert.equal(
    firstTargetGate(["a", "a", "a", "a", null, null, null, null]).status,
    "inconclusive",
  );
  assert.deepEqual(firstTargetGate(["a", "a", "a", "a", "a", "a", "b", "b"]), {
    status: "pass",
    included: 8,
    measured: 8,
    missing: 0,
    maxObserved: 6,
    lowerConcentration: 0.75,
    upperConcentration: 0.75,
  });
  assert.equal(
    firstTargetGate(["a", "a", "a", "a", "a", "a", "a", "b"]).status,
    "fail",
  );
  assert.equal(
    firstTargetGate([null, null, null, null, null, null]).status,
    "inconclusive",
  );
  assert.deepEqual(
    firstTargetGate(["a", "a", "b", "b", null, null, null, null])
      .lowerConcentration,
    0.25,
  );
});

test("post-lock timing requires six measured attempted locks and no missing intervals", () => {
  assert.deepEqual(postLockTimingGate([]), {
    status: "inconclusive",
    attempted: 0,
    measured: 0,
    missing: 0,
    median: null,
  });
  assert.deepEqual(postLockTimingGate([30, 40, 50, 70, 80, 90]), {
    status: "pass",
    attempted: 6,
    measured: 6,
    missing: 0,
    median: 60,
  });
  assert.equal(postLockTimingGate([30, 40, 50, 70, 80]).status, "inconclusive");
  assert.equal(
    postLockTimingGate([30, 40, 50, 70, 80, null]).status,
    "inconclusive",
  );
  assert.equal(postLockTimingGate([60, 61, 62, 63, 64, 65]).status, "fail");
  assert.deepEqual(postLockTimingGate([0, -1, Infinity, NaN, null, 5]), {
    status: "inconclusive",
    attempted: 6,
    measured: 2,
    missing: 4,
    median: 2.5,
  });
});
