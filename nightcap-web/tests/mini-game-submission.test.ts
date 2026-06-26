import assert from "node:assert/strict";
import test from "node:test";

import { createSubmissionGuard } from "../src/mini-game-kit/index.js";
import type { MiniGameSubmissionResult } from "../src/types.js";

test("submission guard: forwards payload and submission id", async () => {
  const captured: { id: string; payload: unknown }[] = [];
  const guard = createSubmissionGuard({
    submit: async (id, payload) => {
      captured.push({ id, payload });
      return { submissionId: id, isAccepted: true };
    },
    generateSubmissionId: () => "fixed-id",
  });
  const result = await guard.submit({ choice: "circle" });
  assert.equal(captured.length, 1);
  assert.equal(captured[0]?.id, "fixed-id");
  assert.deepEqual(captured[0]?.payload, { choice: "circle" });
  assert.equal(result?.submissionId, "fixed-id");
  assert.equal(result?.isAccepted, true);
});

test("submission guard: dedups concurrent submissions (single-flight)", async () => {
  let calls = 0;
  let resolveInner: (r: MiniGameSubmissionResult) => void = () => {};
  const guard = createSubmissionGuard({
    submit: () =>
      new Promise<MiniGameSubmissionResult>((resolve) => {
        calls += 1;
        resolveInner = resolve;
      }),
    generateSubmissionId: () => `id-${calls}`,
  });
  const first = guard.submit({ choice: "a" });
  const second = guard.submit({ choice: "b" });
  resolveInner({ submissionId: "id-1", isAccepted: true });
  await first;
  await second;
  assert.equal(calls, 1);
});

test("submission guard: blocks further submissions once accepted", async () => {
  let calls = 0;
  const guard = createSubmissionGuard({
    submit: async (id) => {
      calls += 1;
      return { submissionId: id, isAccepted: true };
    },
    generateSubmissionId: () => "id",
  });
  await guard.submit({ choice: "a" });
  assert.equal(guard.hasSubmitted(), true);
  const second = await guard.submit({ choice: "b" });
  assert.equal(second, null);
  assert.equal(calls, 1);
});

test("submission guard: rejection unlocks for retry", async () => {
  let calls = 0;
  const guard = createSubmissionGuard({
    submit: async (id) => {
      calls += 1;
      return { submissionId: id, isAccepted: false, rejectionReason: "stale" };
    },
    generateSubmissionId: () => `id-${calls}`,
  });
  const first = await guard.submit({ choice: "a" });
  assert.equal(first?.isAccepted, false);
  assert.equal(guard.hasSubmitted(), false);
  await guard.submit({ choice: "b" });
  assert.equal(calls, 2);
});

test("submission guard: reset clears state", async () => {
  const guard = createSubmissionGuard({
    submit: async (id) => ({ submissionId: id, isAccepted: true }),
    generateSubmissionId: () => "id",
  });
  await guard.submit({ choice: "a" });
  assert.equal(guard.hasSubmitted(), true);
  guard.reset();
  assert.equal(guard.hasSubmitted(), false);
});
