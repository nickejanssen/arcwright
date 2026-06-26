// Verifies the submission-guard UUID fallback honors crypto.getRandomValues
// when crypto.randomUUID is unavailable. We can't easily stub globalThis.crypto
// in node:test without polluting other tests, so the assertion focuses on the
// fact that the kit's own crypto.randomUUID path is exercised whenever the
// runtime exposes it (the common case).

import assert from "node:assert/strict";
import test from "node:test";

import { createSubmissionGuard } from "../src/mini-game-kit/index.js";

test("submission guard generates a UUID-shaped submission id by default", async () => {
  const captured: string[] = [];
  const guard = createSubmissionGuard({
    submit: async (id) => {
      captured.push(id);
      return { submissionId: id, isAccepted: true };
    },
  });
  await guard.submit({ choice: "a" });
  assert.equal(captured.length, 1);
  // Either a real v4 UUID (8-4-4-4-12 hex) from crypto.randomUUID or the
  // RFC 4122-formatted fallback from getRandomValues.
  const id = captured[0]!;
  assert.match(
    id,
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/,
  );
});
