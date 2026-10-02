import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import {
  commitCaseFile,
  createInitialState,
  getVerdictView,
  markAbandoned,
  markComplete,
  markRevealReturn,
  persistState,
  recordDiscovery,
  restoreState,
  setCaseFileDraft,
} from "../runtime.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const caseData = JSON.parse(
  fs.readFileSync(path.join(here, "..", "case.json"), "utf8"),
);
const appSource = fs.readFileSync(path.join(here, "..", "app.js"), "utf8");
const evidence = [
  ...Object.values(caseData.investigation.routes).flatMap(
    (route) => route.discoveries ?? [],
  ),
  ...Object.values(caseData.interviews).flatMap((interview) => [
    ...(interview.discoveries ?? []),
    ...(interview.conditional?.discoveries ?? []),
  ]),
];
const pieces = [
  "e-cylinder-transcript",
  "e-beatrice-impact",
  "e-clara-transcribed-43",
  "e-service-route",
];

function caseState() {
  const state = createInitialState(caseData, {
    nowMs: 1000,
    runId: "recovery-run",
  });
  state.phase = "last-call";
  for (const id of pieces) {
    const fact = evidence.find((item) => item.id === id);
    assert.ok(fact, id);
    recordDiscovery(state, fact, {}, 1100);
  }
  return state;
}

function storage(raw) {
  return {
    getItem: () => raw,
    setItem: (_key, value) => {
      raw = value;
    },
  };
}

test("Case File keeps a draft and refuses counts outside four or five", () => {
  const state = caseState();
  for (const count of [0, 3, 6]) {
    const selected = [
      ...pieces.slice(0, count),
      ...(count === 6 ? ["x", "y"] : []),
    ];
    assert.equal(
      commitCaseFile(state, caseData, "clara-hensley", selected, 1200),
      false,
    );
    assert.equal(state.phase, "last-call");
  }
  assert.equal(
    setCaseFileDraft(state, "clara-hensley", pieces.slice(0, 3)),
    true,
  );
  assert.deepEqual(state.caseFile.draftPieces, pieces.slice(0, 3));
  assert.equal(
    commitCaseFile(
      state,
      caseData,
      "clara-hensley",
      [...pieces, pieces[0]],
      1200,
    ),
    false,
  );
  assert.equal(
    commitCaseFile(
      state,
      caseData,
      "clara-hensley",
      [...pieces.slice(0, 3), "unowned"],
      1200,
    ),
    false,
  );
  assert.equal(
    state.eventSequence.filter(
      (event) => event.event_type === "case_file_commitment",
    ).length,
    0,
  );
});

test("valid committed verdict explains its stored reason without mutation", () => {
  const state = caseState();
  assert.equal(getVerdictView(state, caseData).available, false);
  assert.equal(
    commitCaseFile(state, caseData, "clara-hensley", pieces, 1200),
    true,
  );
  const before = JSON.stringify(state);
  const view = getVerdictView(state, caseData);
  assert.deepEqual(
    { available: view.available, correct: view.correct, reason: view.reason },
    { available: true, correct: true, reason: "solved" },
  );
  assert.match(view.message, /Clara|timeline|recording/i);
  assert.equal(JSON.stringify(state), before);
  state.caseFile.reason = "missing-timing";
  assert.equal(getVerdictView(state, caseData).available, false);
});

test("five owned facts can commit and wrong culprit receives a factual reason", () => {
  const state = caseState();
  const fifth = evidence.find((item) => !pieces.includes(item.id));
  assert.ok(fifth);
  recordDiscovery(state, fifth, {}, 1150);
  assert.equal(
    commitCaseFile(
      state,
      caseData,
      "lenora-quill",
      [...pieces, fifth.id],
      1200,
    ),
    true,
  );
  const verdict = getVerdictView(state, caseData);
  assert.equal(verdict.correct, false);
  assert.equal(verdict.reason, "wrong-culprit");
  assert.match(verdict.message, /Clara/);
});

test("storage failures leave a usable in-memory state and restore no invented run", () => {
  const state = caseState();
  assert.equal(persistState(state, null), false);
  assert.equal(
    persistState(state, {
      setItem() {
        throw new Error("denied");
      },
    }),
    false,
  );
  assert.equal(
    persistState(state, {
      setItem() {},
      getItem() {
        throw new Error("denied");
      },
    }),
    false,
  );
  assert.equal(restoreState(caseData, null), null);
  assert.equal(
    restoreState(caseData, {
      getItem() {
        throw new Error("denied");
      },
    }),
    null,
  );
  for (const raw of [
    "{",
    "null",
    "{}",
    JSON.stringify({ ...state, fixtureVersion: "3.0" }),
  ])
    assert.equal(restoreState(caseData, storage(raw)), null);
  assert.equal(state.phase, "last-call");
});

test("malformed active lock cannot restore into the app renderer", () => {
  const state = createInitialState(caseData, {
    nowMs: 1000,
    runId: "bad-lock",
  });
  state.phase = "lock";
  state.lock.status = "active";
  state.lock.startedAtMs = 1200;
  for (const lock of [
    { ...state.lock, setPins: undefined },
    { ...state.lock, startedAtMs: null },
    { ...state.lock, currentPin: -1 },
  ]) {
    const malformed = { ...state, lock };
    assert.equal(
      restoreState(caseData, storage(JSON.stringify(malformed))),
      null,
    );
  }
  assert.equal(createInitialState(caseData).lock.status, "unavailable");
});

test("restore rejects missing or malformed commitments and preserves intact results", () => {
  const state = caseState();
  assert.equal(
    commitCaseFile(state, caseData, "clara-hensley", pieces, 1200),
    true,
  );
  const saved = storage();
  assert.equal(persistState(state, saved), true);
  const restored = restoreState(caseData, saved);
  assert.equal(getVerdictView(restored, caseData).correct, true);
  for (const changed of [
    { ...state, caseFile: { ...state.caseFile, lockedAt: null } },
    {
      ...state,
      caseFile: { ...state.caseFile, pieces: ["forged", ...pieces.slice(1)] },
    },
    { ...state, caseFile: { ...state.caseFile, correct: false } },
    {
      ...state,
      eventSequence: state.eventSequence.filter(
        (event) => event.event_type !== "case_file_commitment",
      ),
    },
    {
      ...state,
      eventSequence: state.eventSequence.filter(
        (event) => event.target !== pieces[0],
      ),
    },
    { ...state, eventSequence: [null, ...state.eventSequence] },
    { ...state, discoveries: [null, ...state.discoveries] },
  ])
    assert.equal(getVerdictView(changed, caseData).available, false);
  assert.equal(markRevealReturn(restored, 1300), true);
  assert.equal(markRevealReturn(restored, 1400), false);
  assert.equal(
    restored.eventSequence.filter(
      (event) => event.event_type === "reveal_return",
    ).length,
    1,
  );
});

test("unavailable verdict creates no completion, return or abandonment event", () => {
  const state = createInitialState(caseData, { nowMs: 1000, runId: "missing" });
  const before = JSON.stringify(state);
  assert.equal(getVerdictView(state, caseData).available, false);
  assert.equal(JSON.stringify(state), before);
  assert.equal(state.eventSequence.length, 0);
});

test("explicit abandonment is single fire and distinct from completion", () => {
  const state = caseState();
  assert.equal(markAbandoned(state, "last-call", 1200), true);
  assert.equal(markAbandoned(state, "last-call", 1300), false);
  assert.equal(
    state.eventSequence.filter((event) => event.event_type === "abandonment")
      .length,
    1,
  );
  assert.equal(markComplete(state, 1400), false);
});

test("Case File UI reports selection count and preserves notebook access", () => {
  assert.match(appSource, /id="selectionCount"[^>]*aria-live="polite"/);
  assert.match(appSource, /pieces\.length} of 4 or 5 facts/);
  assert.match(appSource, /id="reviewNotebook"/);
});

test("Case File UI asks for a culprit separately from missing facts", () => {
  assert.match(appSource, /if \(!culprit\) \{[\s\S]*?"Choose one culprit\."/);
  assert.match(
    appSource,
    /if \(pieces\.length < 4 \|\| pieces\.length > 5\) \{[\s\S]*?"Choose four or five facts\."/,
  );
});

test("reveal startup never creates a replacement run and load retry is bounded", () => {
  assert.match(appSource, /if \(isRevealMode\(\)\) \{/);
  assert.match(appSource, /getVerdictView\(state, caseData\)/);
  assert.match(appSource, /id="retryCaseLoad"/);
  assert.match(appSource, /loadAttempts < 3/);
});
