// Verifies the worker dispatches the mini-game bundle and definition paths
// to the ASSETS binding. Catches the regression where a misaligned URL
// prefix would silently 404 the bundle, leaving the stage permanently
// idle in production.

import assert from "node:assert/strict";
import test from "node:test";

import worker from "../src/worker.js";
import type { NightcapWorkerEnv } from "../src/worker.js";

function makeAssets() {
  const seen: string[] = [];
  const assets = {
    fetch: async (request: Request): Promise<Response> => {
      seen.push(new URL(request.url).pathname);
      return new Response("ok", { status: 200 });
    },
  };
  return { seen, assets };
}

function makeEnv(assets: Fetcher | undefined): NightcapWorkerEnv {
  // None of the /mini-games asset routes touch ROOMS or any other binding
  // so a fully stubbed environment is sufficient.
  return {
    ARCWRIGHT_API_BASE_URL: "https://arcwright.invalid",
    ARCWRIGHT_API_KEY: "test-key",
    FIREBASE_WEB_API_KEY: "test-firebase",
    BOOTSTRAP_TOKEN: "boot",
    ROOMS: {} as unknown as NightcapWorkerEnv["ROOMS"],
    ...(assets ? { ASSETS: assets } : {}),
  };
}

function makeCtx(): ExecutionContext {
  return { waitUntil: () => {} };
}

test("worker delegates /mini-games.js to the ASSETS binding", async () => {
  const { assets, seen } = makeAssets();
  const env = makeEnv(assets);
  const res = await worker.fetch(
    new Request("https://nightcap.test/mini-games.js"),
    env,
    makeCtx(),
  );
  assert.equal(res.status, 200);
  assert.deepEqual(seen, ["/mini-games.js"]);
});

test("worker delegates /mini-games/definitions/<id>/<version>.json to ASSETS", async () => {
  const { assets, seen } = makeAssets();
  const env = makeEnv(assets);
  const res = await worker.fetch(
    new Request(
      "https://nightcap.test/mini-games/definitions/fixture-individual/0.1.0.json",
    ),
    env,
    makeCtx(),
  );
  assert.equal(res.status, 200);
  assert.deepEqual(seen, [
    "/mini-games/definitions/fixture-individual/0.1.0.json",
  ]);
});

test("worker returns 404 for /mini-games.js when ASSETS is not bound", async () => {
  const env = makeEnv(undefined);
  const res = await worker.fetch(
    new Request("https://nightcap.test/mini-games.js"),
    env,
    makeCtx(),
  );
  assert.equal(res.status, 404);
});

test("worker does not delegate unrelated /mini-games sub-paths", async () => {
  const { assets, seen } = makeAssets();
  const env = makeEnv(assets);
  const res = await worker.fetch(
    new Request("https://nightcap.test/mini-games/other-endpoint"),
    env,
    makeCtx(),
  );
  // Falls through to the 404 catch-all; never reached ASSETS.
  assert.equal(res.status, 404);
  assert.deepEqual(seen, []);
});
