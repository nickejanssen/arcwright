import assert from "node:assert/strict";
import test from "node:test";

import {
  NightcapConnector,
  type CreateSessionRequest,
} from "../src/connector.js";
import {
  authorizeBootstrapSession,
  bootstrapSession,
  type NightcapRoom,
  type NightcapWorkerEnv,
} from "../src/worker.js";

const roomNamespace = {
  idFromName(name: string) {
    return name;
  },
  get() {
    throw new Error("Unexpected Durable Object access in worker tests");
  },
} as DurableObjectNamespace<NightcapRoom>;

const env: NightcapWorkerEnv = {
  ARCWRIGHT_API_BASE_URL: "https://arcwright.invalid",
  ARCWRIGHT_API_KEY: "test-api-key",
  BOOTSTRAP_TOKEN: "bootstrap-secret",
  ROOMS: roomNamespace,
};

test("authorizeBootstrapSession requires the configured bootstrap token", () => {
  const missing = authorizeBootstrapSession(
    new Request("https://example.com/bootstrap/session", { method: "POST" }),
    env,
  );
  assert.equal(missing?.status, 401);

  const wrong = authorizeBootstrapSession(
    new Request("https://example.com/bootstrap/session", {
      method: "POST",
      headers: { "x-arcwright-bootstrap-token": "wrong" },
    }),
    env,
  );
  assert.equal(wrong?.status, 401);

  const allowed = authorizeBootstrapSession(
    new Request("https://example.com/bootstrap/session", {
      method: "POST",
      headers: { "x-arcwright-bootstrap-token": env.BOOTSTRAP_TOKEN },
    }),
    env,
  );
  assert.equal(allowed, null);
});

test("bootstrapSession forwards the Arcwright session id into room runtime state", async () => {
  const createSessionCalls: CreateSessionRequest[] = [];
  const connector = {
    async createSession(request: CreateSessionRequest) {
      createSessionCalls.push(request);
      return {
        session_id: "session-123",
        room_url: "https://arcwright.invalid/rooms/session-123",
      };
    },
  } as unknown as NightcapConnector;

  const response = await bootstrapSession(connector, {
    gameId: "nightcap",
    hostId: "host-1",
    playerNames: ["Avery", "Jordan"],
  });

  assert.equal(response.status, 200);
  assert.equal(createSessionCalls.length, 1);
  assert.deepEqual(createSessionCalls[0], {
    gameId: "nightcap",
    hostId: "host-1",
    playerNames: ["Avery", "Jordan"],
  });

  const body = (await response.json()) as {
    session: {
      session_id: string;
      room_url: string;
    };
    runtime: { room_id: string; room_url: string };
  };

  assert.equal(body.session.session_id, "session-123");
  assert.equal(
    body.session.room_url,
    "https://arcwright.invalid/rooms/session-123",
  );
  assert.deepEqual(body.runtime, {
    room_id: "session-123",
    room_url: "/rooms/session-123",
  });
});
