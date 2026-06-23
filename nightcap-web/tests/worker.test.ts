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
  createPlayerJoinLink,
  joinPlayerSession,
  proxySessionLifecycle,
  renderPlayerJoinPage,
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

test("join page route renders the player join shell", async () => {
  const response = await workerRuntime.fetch(
    new Request(
      "https://nightcap.test/join?session_id=session-123&token=join-token-1",
      {
        method: "GET",
      },
    ),
    env,
    {} as ExecutionContext,
  );

  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /Join Nightcap/);
  assert.match(html, /join-token-1/);
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

test("createPlayerJoinLink returns a runtime join URL for the player QR path", async () => {
  const createPlayerCalls: string[] = [];
  const connector = {
    async createPlayerSlot(sessionId: string) {
      createPlayerCalls.push(sessionId);
      return {
        participant_id: "participant-1",
        join_token: "join-token-1",
        join_url:
          "https://arcwright.invalid/v1/sessions/session-join/join?token=join-token-1",
      };
    },
  } as unknown as NightcapConnector;

  const fetchGlobal = globalThis as typeof globalThis & {
    fetch: typeof fetch;
  };
  const originalFetch = fetchGlobal.fetch;
  const fetchCalls: Array<{ url: string; authorization: string | null }> = [];
  fetchGlobal.fetch = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    const request =
      input instanceof Request
        ? input
        : new Request(input instanceof URL ? input : String(input), init);
    fetchCalls.push({
      url: request.url,
      authorization: request.headers.get("authorization"),
    });
    return new Response(JSON.stringify({ session_id: "session-join" }), {
      status: 200,
      headers: { "content-type": "application/json; charset=utf-8" },
    });
  };

  try {
    const response = await createPlayerJoinLink(
      connector,
      env,
      "session-join",
      new Request(
        "https://nightcap.test/host/api/sessions/session-join/players",
        {
          method: "POST",
          headers: { Authorization: "Bearer host-token" },
        },
      ),
    );

    assert.equal(response.status, 200);
    assert.equal(createPlayerCalls.length, 1);
    assert.equal(createPlayerCalls[0], "session-join");

    const body = (await response.json()) as {
      player: {
        participant_id: string;
        join_token: string;
      };
      runtime: {
        room_id: string;
        room_url: string;
        host_url: string;
        shared_display_url: string;
        player_url: string;
      };
    };

    assert.equal(body.player.participant_id, "participant-1");
    assert.equal(body.player.join_token, "join-token-1");
    assert.equal(body.runtime.room_id, "session-join");
    assert.equal(
      body.runtime.player_url,
      "/join?session_id=session-join&token=join-token-1",
    );
    assert.equal(fetchCalls.length, 1);
    assert.equal(
      fetchCalls[0]?.url,
      "https://arcwright.invalid/v1/sessions/session-join",
    );
    assert.equal(fetchCalls[0]?.authorization, "Bearer host-token");
  } finally {
    fetchGlobal.fetch = originalFetch;
  }
});

test("joinPlayerSession registers the player and returns the assigned character context", async () => {
  const roomJoins: unknown[] = [];
  const roomStub = {
    idFromName(name: string) {
      return name;
    },
    get() {
      return {
        async fetch(request: Request): Promise<Response> {
          roomJoins.push(await request.json());
          return new Response(JSON.stringify({ ok: true }), {
            headers: { "content-type": "application/json; charset=utf-8" },
          });
        },
      };
    },
  } as unknown as DurableObjectNamespace<NightcapRoom>;

  const joinCalls: Array<{
    sessionId: string;
    joinToken: string;
    personalizationIntake: Record<string, unknown>;
  }> = [];
  const joinConnector = {
    async joinSession(
      sessionId: string,
      joinToken: string,
      personalizationIntake: Record<string, unknown>,
    ) {
      joinCalls.push({ sessionId, joinToken, personalizationIntake });
      return {
        session_id: sessionId,
        player_id: "player-1",
        character_id: "character-42",
        player_token: "player-token-1",
      };
    },
  } as unknown as NightcapConnector;

  const response = await joinPlayerSession(
    joinConnector,
    {
      ...env,
      ROOMS: roomStub,
    },
    {
      session_id: "session-join",
      join_token: "join-token-1",
      personalization_intake: {
        notes: "opaque",
      },
    },
  );

  assert.equal(response.status, 200);
  assert.deepEqual(joinCalls, [
    {
      sessionId: "session-join",
      joinToken: "join-token-1",
      personalizationIntake: { notes: "opaque" },
    },
  ]);

  const body = (await response.json()) as {
    session_id: string;
    player: { player_id: string; character_id: string; player_token: string };
    runtime: { room_id: string; player_url: string };
    personalization_intake: Record<string, unknown>;
  };

  assert.equal(body.session_id, "session-join");
  assert.equal(body.player.player_id, "player-1");
  assert.equal(body.player.character_id, "character-42");
  assert.equal(body.player.player_token, "player-token-1");
  assert.equal(body.runtime.room_id, "session-join");
  assert.equal(
    body.runtime.player_url,
    "/join?session_id=session-join&token=join-token-1",
  );
  assert.deepEqual(body.personalization_intake, { notes: "opaque" });
  assert.deepEqual(joinCalls[0]?.personalizationIntake, { notes: "opaque" });
  assert.equal(roomJoins.length, 1);
  assert.deepEqual(roomJoins[0], {
    session_id: "session-join",
    client_id: "player-1",
    participant_id: "player-1",
    character_id: "character-42",
    role: "player",
  });
});

test("player api routes proxy scoped character fetch, input, and event replay", async () => {
  const fetchGlobal = globalThis as typeof globalThis & {
    fetch: typeof fetch;
  };
  const originalFetch = fetchGlobal.fetch;
  const fetchCalls: Array<{
    url: string;
    method: string;
    authorization: string | null;
    body: string | null;
  }> = [];

  fetchGlobal.fetch = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    const request =
      input instanceof Request
        ? input
        : new Request(input instanceof URL ? input : String(input), init);
    const url = new URL(request.url);
    const body = request.method === "GET" ? null : await request.text();
    fetchCalls.push({
      url: request.url,
      method: request.method,
      authorization: request.headers.get("authorization"),
      body,
    });

    if (
      request.method === "GET" &&
      url.pathname === "/v1/sessions/session-abc/characters/character-1"
    ) {
      return new Response(
        JSON.stringify({
          session_id: "session-abc",
          character_id: "character-1",
          participant_id: "player-1",
          surface_type: "phone",
          is_ai_controlled: false,
        }),
        {
          status: 200,
          headers: { "content-type": "application/json; charset=utf-8" },
        },
      );
    }

    if (
      request.method === "POST" &&
      url.pathname === "/v1/sessions/session-abc/characters/character-1/input"
    ) {
      assert.deepEqual(JSON.parse(body ?? "{}"), {
        kind: "action",
        content: "Look under the table.",
      });
      return new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "content-type": "application/json; charset=utf-8" },
      });
    }

    if (
      request.method === "GET" &&
      url.pathname === "/v1/sessions/session-abc/events"
    ) {
      assert.equal(url.searchParams.get("since"), "4");
      return new Response(
        `data: ${JSON.stringify({
          event_id: "event-7",
          session_id: "session-abc",
          timestamp: "2026-06-22T12:00:07.000Z",
          category: "private_delivery",
          event_type: "clue_delivery",
          actor_id: null,
          target_audience: "specific_player",
          target_player_id: "player-1",
          payload: { clue_id: "clue-7", text: "Your clue" },
          presentation_hints: {
            emotion: "tense",
            urgency: "high",
            voice_hint: null,
            animation_hint: null,
            lighting_hint: null,
            pause_before_ms: 0,
          },
          sequence_number: 7,
        })}\n\n`,
        {
          status: 200,
          headers: { "content-type": "text/event-stream" },
        },
      );
    }

    return new Response("not found", { status: 404 });
  };

  try {
    const characterResponse = await workerRuntime.fetch(
      new Request(
        "https://nightcap.test/player/api/sessions/session-abc/characters/character-1",
        {
          method: "GET",
          headers: {
            Authorization: "Bearer player-token-abc",
          },
        },
      ),
      env,
      {} as ExecutionContext,
    );

    assert.equal(characterResponse.status, 200);
    const characterBody = (await characterResponse.json()) as {
      character_id: string;
      surface_type: string;
    };
    assert.equal(characterBody.character_id, "character-1");
    assert.equal(characterBody.surface_type, "phone");

    const inputResponse = await workerRuntime.fetch(
      new Request(
        "https://nightcap.test/player/api/sessions/session-abc/characters/character-1/input",
        {
          method: "POST",
          headers: {
            Authorization: "Bearer player-token-abc",
            "content-type": "application/json",
          },
          body: JSON.stringify({
            kind: "action",
            content: "Look under the table.",
          }),
        },
      ),
      env,
      {} as ExecutionContext,
    );

    assert.equal(inputResponse.status, 200);

    const eventResponse = await workerRuntime.fetch(
      new Request(
        "https://nightcap.test/player/api/sessions/session-abc/events?since=4",
        {
          method: "GET",
          headers: {
            Authorization: "Bearer player-token-abc",
          },
        },
      ),
      env,
      {} as ExecutionContext,
    );

    assert.equal(eventResponse.status, 200);
    assert.equal(
      eventResponse.headers.get("content-type"),
      "text/event-stream",
    );
    const eventText = await eventResponse.text();
    assert.match(eventText, /Your clue/);

    assert.equal(fetchCalls[0]?.authorization, "Bearer player-token-abc");
    assert.equal(fetchCalls[1]?.authorization, "Bearer player-token-abc");
    assert.equal(fetchCalls[2]?.authorization, "Bearer player-token-abc");
  } finally {
    fetchGlobal.fetch = originalFetch;
  }
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
  const playerHtml = renderPlayerJoinPage("session-123", "join-token-1");

  assert.match(hostHtml, /Create session/);
  assert.match(hostHtml, /Start/);
  assert.match(hostHtml, /Pause/);
  assert.match(hostHtml, /Resume/);
  assert.match(hostHtml, /End/);
  assert.match(hostHtml, /Create player join link/);
  assert.match(sharedHtml, /Shared display/);
  assert.match(sharedHtml, /Only public or shared-display events/);
  assert.match(playerHtml, /Join Nightcap/);
  assert.match(playerHtml, /Join code/);
  assert.match(playerHtml, /Your surface/);
  assert.match(playerHtml, /Send input/);
  assert.match(playerHtml, /Private feed/);
});
