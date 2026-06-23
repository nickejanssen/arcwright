import assert from "node:assert/strict";
import test from "node:test";

import {
  NightcapConnector,
  type CreateSessionRequest,
} from "../src/connector.js";

const DurableObjectStub = class {
  constructor(state: unknown, env: unknown) {
    void state;
    void env;
  }
};

// @ts-expect-error Node does not provide DurableObject at runtime.
globalThis.DurableObject = DurableObjectStub;

const workerModule = await import("../src/worker.js");
const {
  authorizeBootstrapSession,
  bootstrapSession,
  createHostSession,
  proxySessionLifecycle,
  renderHostPage,
  renderSharedDisplayPage,
} = workerModule;
const workerRuntime = workerModule.default;
import type { NightcapRoom, NightcapWorkerEnv } from "../src/worker.js";

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

test("host api bootstrap session requires the bootstrap token", async () => {
  const response = await workerRuntime.fetch(
    new Request("https://nightcap.test/host/api/bootstrap/session", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        arc_id: "nightcap-v1",
      }),
    }),
    env,
    {} as ExecutionContext,
  );

  assert.equal(response.status, 401);
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

test("createHostSession includes host and shared-display runtime URLs", async () => {
  const createSessionCalls: CreateSessionRequest[] = [];
  const connector = {
    async createSession(request: CreateSessionRequest) {
      createSessionCalls.push(request);
      return {
        session_id: "session-456",
        room_url: "https://arcwright.invalid/rooms/session-456",
        host_token: "host-token",
      };
    },
  } as unknown as NightcapConnector;

  const response = await createHostSession(connector, {
    arc_id: "nightcap-v1",
    personalization_intake: {
      host_seed_1: "A",
      player_prompt_1: "B",
    },
  });

  assert.equal(response.status, 200);
  assert.equal(createSessionCalls.length, 1);
  const body = (await response.json()) as {
    session: { session_id: string };
    runtime: {
      room_id: string;
      room_url: string;
      host_url: string;
      shared_display_url: string;
    };
    personalization_intake: Record<string, unknown>;
  };

  assert.equal(body.session.session_id, "session-456");
  assert.equal(body.runtime.room_id, "session-456");
  assert.equal(body.runtime.room_url, "/rooms/session-456");
  assert.equal(body.runtime.host_url, "/host?session_id=session-456");
  assert.equal(
    body.runtime.shared_display_url,
    "/shared-display?session_id=session-456",
  );
  assert.deepEqual(body.personalization_intake, {
    host_seed_1: "A",
    player_prompt_1: "B",
  });
});

test("proxySessionLifecycle forwards host bearer tokens to Arcwright lifecycle calls", async () => {
  const events: string[] = [];
  const connector = {
    async startSession(sessionId: string, accessToken: string) {
      events.push(`start:${sessionId}:${accessToken}`);
      return {
        session_id: sessionId,
        status: "active",
        current_beat_id: "arrival",
        player_count: 4,
      };
    },
    async pauseSession(sessionId: string, accessToken: string) {
      events.push(`pause:${sessionId}:${accessToken}`);
      return {
        session_id: sessionId,
        status: "paused",
        current_beat_id: "arrival",
        player_count: 4,
      };
    },
    async resumeSession(sessionId: string, accessToken: string) {
      events.push(`resume:${sessionId}:${accessToken}`);
      return {
        session_id: sessionId,
        status: "active",
        current_beat_id: "arrival",
        player_count: 4,
      };
    },
    async endSession(
      sessionId: string,
      accessToken: string,
      body: { completion_type?: string; killer_identified?: boolean } = {},
    ) {
      events.push(
        `end:${sessionId}:${accessToken}:${body.completion_type ?? ""}:${body.killer_identified ?? false}`,
      );
      return {
        session_id: sessionId,
        status: "completed",
        current_beat_id: "arrival",
        player_count: 4,
      };
    },
  } as unknown as NightcapConnector;

  const startResponse = await proxySessionLifecycle(
    connector,
    "session-789",
    "start",
    new Request("https://nightcap.test/host/api/sessions/session-789/start", {
      method: "POST",
      headers: { Authorization: "Bearer host-token" },
    }),
  );
  const pauseResponse = await proxySessionLifecycle(
    connector,
    "session-789",
    "pause",
    new Request("https://nightcap.test/host/api/sessions/session-789/pause", {
      method: "POST",
      headers: { Authorization: "Bearer host-token" },
    }),
  );
  const resumeResponse = await proxySessionLifecycle(
    connector,
    "session-789",
    "resume",
    new Request("https://nightcap.test/host/api/sessions/session-789/resume", {
      method: "POST",
      headers: { Authorization: "Bearer host-token" },
    }),
  );
  const endResponse = await proxySessionLifecycle(
    connector,
    "session-789",
    "end",
    new Request("https://nightcap.test/host/api/sessions/session-789/end", {
      method: "POST",
      headers: {
        Authorization: "Bearer host-token",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        completion_type: "interrupted",
        killer_identified: true,
      }),
    }),
  );

  assert.equal(startResponse.status, 200);
  assert.equal(pauseResponse.status, 200);
  assert.equal(resumeResponse.status, 200);
  assert.equal(endResponse.status, 200);
  assert.deepEqual(events, [
    "start:session-789:host-token",
    "pause:session-789:host-token",
    "resume:session-789:host-token",
    "end:session-789:host-token:interrupted:true",
  ]);
});

test("proxySessionLifecycle logs upstream failures and keeps the browser response generic", async () => {
  const connector = {
    async startSession() {
      throw new Error("boom");
    },
  } as unknown as NightcapConnector;

  const originalError = console.error;
  const logs: unknown[][] = [];
  console.error = (...args: unknown[]) => {
    logs.push(args);
  };

  try {
    const response = await proxySessionLifecycle(
      connector,
      "session-999",
      "start",
      new Request("https://nightcap.test/host/api/sessions/session-999/start", {
        method: "POST",
        headers: { Authorization: "Bearer host-token" },
      }),
    );

    assert.equal(response.status, 502);
    assert.equal(await response.text(), "Arcwright lifecycle request failed");
    assert.equal(logs.length, 1);
    assert.match(
      String(logs[0]?.[0] ?? ""),
      /Arcwright lifecycle request failed/,
    );
    assert.deepEqual(logs[0]?.[1], {
      action: "start",
      sessionId: "session-999",
      error: "boom",
    });
  } finally {
    console.error = originalError;
  }
});

test("rendered runtime shells include host and shared-display controls", () => {
  const hostHtml = renderHostPage("session-123");
  const sharedHtml = renderSharedDisplayPage("session-123");

  assert.match(hostHtml, /Create session/);
  assert.match(hostHtml, /Start/);
  assert.match(hostHtml, /Pause/);
  assert.match(hostHtml, /Resume/);
  assert.match(hostHtml, /End/);
  assert.match(sharedHtml, /Shared display/);
  assert.match(sharedHtml, /Only public or shared-display events/);
});
