import test from "node:test";
import assert from "node:assert/strict";
import {
  NightcapConnector,
  type CreateSessionRequest,
  type SessionStateResponse,
} from "../src/connector.js";
import {
  isHostVisibleEvent,
  isSharedDisplayVisibleEvent,
} from "../src/filters.js";

function responseJson(body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: {
      "content-type": "application/json; charset=utf-8",
    },
  });
}

function responseText(status: number, body: string): Response {
  return new Response(body, {
    status,
    headers: {
      "content-type": "text/plain; charset=utf-8",
    },
  });
}

function responseSse(payloads: unknown[]): Response {
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      const encoder = new TextEncoder();
      for (const payload of payloads) {
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify(payload)}\n\n`),
        );
      }
      controller.close();
    },
  });

  return new Response(stream, {
    status: 200,
    headers: {
      "content-type": "text/event-stream",
    },
  });
}

function responseSseWithDelayedSecondEvent(payloads: unknown[]): Response {
  let timer: ReturnType<typeof setTimeout> | null = null;
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      const encoder = new TextEncoder();
      controller.enqueue(
        encoder.encode(`data: ${JSON.stringify(payloads[0])}\n\n`),
      );
      timer = setTimeout(() => {
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify(payloads[1])}\n\n`),
        );
        controller.close();
      }, 20);
    },
    cancel() {
      if (timer) {
        clearTimeout(timer);
        timer = null;
      }
    },
  });

  return new Response(stream, {
    status: 200,
    headers: {
      "content-type": "text/event-stream",
    },
  });
}

test("NightcapConnector calls session endpoints and streams scoped events", async () => {
  const calls: Array<{
    method: string;
    path: string;
    headers: Headers;
    body: string | null;
  }> = [];

  const createBody: CreateSessionRequest = {
    arc_id: "nightcap-v1",
    min_players: 4,
    max_players: 8,
  };

  const sessionState: SessionStateResponse = {
    session_id: "session-1",
    status: "active",
    current_beat_id: "arrival",
    player_count: 4,
  };

  const eventPayload = {
    event_id: "event-1",
    session_id: "session-1",
    timestamp: "2026-06-22T12:00:00.000Z",
    category: "private_delivery",
    event_type: "clue_delivery",
    actor_id: null,
    target_audience: "specific_player",
    target_player_id: "player-1",
    payload: { clue_id: "clue-1", text: "Private clue text" },
    presentation_hints: {
      emotion: "tense",
      urgency: "high",
      voice_hint: null,
      animation_hint: null,
      lighting_hint: null,
      pause_before_ms: 0,
    },
    sequence_number: 1,
  };

  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    const request =
      input instanceof Request
        ? input
        : new Request(input instanceof URL ? input : String(input), init);
    const url = new URL(request.url);
    const body = request.method === "GET" ? null : await request.text();

    calls.push({
      method: request.method,
      path: `${url.pathname}${url.search}`,
      headers: request.headers,
      body,
    });

    if (request.method === "POST" && url.pathname === "/v1/sessions") {
      return responseJson({
        session_id: "session-1",
        join_url: "https://arcwright.test/v1/sessions/session-1/join",
        host_token: "host-token",
      });
    }

    if (request.method === "GET" && url.pathname === "/v1/sessions/session-1") {
      return responseJson(sessionState);
    }

    if (
      request.method === "POST" &&
      url.pathname === "/v1/sessions/session-1/start"
    ) {
      return responseJson({ ...sessionState, status: "active" });
    }

    if (
      request.method === "POST" &&
      url.pathname === "/v1/sessions/session-1/pause"
    ) {
      return responseJson({ ...sessionState, status: "paused" });
    }

    if (
      request.method === "POST" &&
      url.pathname === "/v1/sessions/session-1/resume"
    ) {
      return responseJson({ ...sessionState, status: "active" });
    }

    if (
      request.method === "POST" &&
      url.pathname === "/v1/sessions/session-1/end"
    ) {
      return responseJson({ ...sessionState, status: "completed" });
    }

    if (
      request.method === "POST" &&
      url.pathname === "/v1/sessions/session-1/players"
    ) {
      return responseJson({
        participant_id: "participant-1",
        join_token: "join-token-1",
        join_url:
          "https://arcwright.test/v1/sessions/session-1/join?token=join-token-1",
      });
    }

    if (
      request.method === "POST" &&
      url.pathname === "/v1/sessions/session-1/join"
    ) {
      assert.equal(url.searchParams.get("token"), "join-token-1");
      assert.deepEqual(JSON.parse(body ?? "{}"), {
        personalization_intake: {
          host_familiarity: "mixed group",
        },
      });
      return responseJson({
        session_id: "session-1",
        player_id: "player-1",
        character_id: "character-1",
        player_token: "player-token-1",
      });
    }

    if (
      request.method === "GET" &&
      url.pathname === "/v1/sessions/session-1/events"
    ) {
      return responseSse([eventPayload]);
    }

    return new Response("not found", { status: 404 });
  };

  const connector = new NightcapConnector({
    baseUrl: "https://arcwright.test",
    apiKey: "api-key-123",
    fetchImpl,
  });

  const created = await connector.createSession(createBody);
  assert.equal(created.session_id, "session-1");
  assert.equal(
    created.join_url,
    "https://arcwright.test/v1/sessions/session-1/join",
  );
  assert.equal(created.host_token, "host-token");

  const loaded = await connector.getSession("session-1");
  assert.equal(loaded.current_beat_id, "arrival");
  assert.equal(loaded.player_count, 4);

  const started = await connector.startSession("session-1", "host-token");
  assert.equal(started.status, "active");

  const paused = await connector.pauseSession("session-1", "host-token");
  assert.equal(paused.status, "paused");

  const resumed = await connector.resumeSession("session-1", "host-token");
  assert.equal(resumed.status, "active");

  const ended = await connector.endSession("session-1", "host-token", {
    completion_type: "full_arc",
    killer_identified: true,
  });
  assert.equal(ended.status, "completed");

  const playerSlot = await connector.createPlayerSlot("session-1");
  assert.equal(playerSlot.participant_id, "participant-1");
  assert.equal(playerSlot.join_token, "join-token-1");
  assert.equal(
    playerSlot.join_url,
    "https://arcwright.test/v1/sessions/session-1/join?token=join-token-1",
  );

  const joined = await connector.joinSession("session-1", "join-token-1", {
    host_familiarity: "mixed group",
  });
  assert.equal(joined.session_id, "session-1");
  assert.equal(joined.player_id, "player-1");
  assert.equal(joined.character_id, "character-1");
  assert.equal(joined.player_token, "player-token-1");

  const received: Array<typeof eventPayload> = [];
  let unsubscribe = () => {};
  const done = new Promise<void>((resolve) => {
    unsubscribe = connector.subscribeToEvents(
      {
        sessionId: "session-1",
        accessToken: "player-token-1",
      },
      (event) => {
        received.push(event as typeof eventPayload);
        unsubscribe();
        resolve();
      },
    );
  });

  await done;

  assert.equal(received.length, 1);
  assert.equal(received[0]?.target_audience, "specific_player");
  assert.equal(received[0]?.payload.clue_id, "clue-1");

  assert.equal(calls[0]?.method, "POST");
  assert.equal(calls[0]?.path, "/v1/sessions");
  assert.equal(calls[0]?.headers.get("x-api-key"), "api-key-123");
  assert.equal(calls[0]?.headers.get("content-type"), "application/json");
  assert.equal(calls[1]?.method, "GET");
  assert.equal(calls[1]?.path, "/v1/sessions/session-1");
  assert.equal(calls[1]?.headers.get("x-api-key"), "api-key-123");
  assert.equal(calls[1]?.headers.get("content-type"), null);
  assert.equal(calls[2]?.path, "/v1/sessions/session-1/start");
  assert.equal(calls[2]?.headers.get("authorization"), "Bearer host-token");
  assert.equal(calls[3]?.path, "/v1/sessions/session-1/pause");
  assert.equal(calls[4]?.path, "/v1/sessions/session-1/resume");
  assert.equal(calls[5]?.path, "/v1/sessions/session-1/end");
  assert.equal(calls[5]?.headers.get("authorization"), "Bearer host-token");
  assert.equal(calls[6]?.method, "POST");
  assert.equal(calls[6]?.path, "/v1/sessions/session-1/players");
  assert.equal(calls[6]?.headers.get("x-api-key"), "api-key-123");
  assert.equal(calls[6]?.headers.get("content-type"), "application/json");
  assert.equal(calls[7]?.method, "POST");
  assert.equal(
    calls[7]?.path,
    "/v1/sessions/session-1/join?token=join-token-1",
  );
  assert.equal(calls[7]?.method, "POST");
  assert.equal(calls[7]?.headers.get("content-type"), "application/json");
  assert.ok(calls[7]?.body);
  assert.deepEqual(JSON.parse(calls[7]?.body ?? "{}"), {
    personalization_intake: {
      host_familiarity: "mixed group",
    },
  });
  assert.equal(calls[8]?.method, "GET");
  assert.equal(calls[8]?.path, "/v1/sessions/session-1/events?since=0");
  assert.equal(calls[8]?.headers.get("authorization"), "Bearer player-token-1");
  assert.equal(calls[8]?.headers.get("content-type"), null);
});

test("NightcapConnector retries failed event stream opens and reports errors", async () => {
  const calls: Array<{ method: string; path: string }> = [];
  const errors: Array<{ message: string; retryDelayMs: number | null }> = [];
  let eventRequestCount = 0;

  const eventPayload = {
    event_id: "event-2",
    session_id: "session-2",
    timestamp: "2026-06-22T12:00:01.000Z",
    category: "acknowledgement",
    event_type: "clue_acknowledged",
    actor_id: null,
    target_audience: "shared_display",
    target_player_id: null,
    payload: { clue_id: "clue-2" },
    presentation_hints: {
      emotion: "warm",
      urgency: "low",
      voice_hint: null,
      animation_hint: null,
      lighting_hint: null,
      pause_before_ms: 0,
    },
    sequence_number: 2,
  };

  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    const request =
      input instanceof Request
        ? input
        : new Request(input instanceof URL ? input : String(input), init);
    const url = new URL(request.url);
    calls.push({
      method: request.method,
      path: `${url.pathname}${url.search}`,
    });

    if (url.pathname === "/v1/sessions/session-2/events") {
      eventRequestCount += 1;
      if (eventRequestCount === 1) {
        return responseText(503, "temporary outage");
      }

      return responseSse([eventPayload]);
    }

    if (request.method === "GET" && url.pathname === "/v1/sessions/session-2") {
      return responseJson({
        session_id: "session-2",
        status: "active",
      });
    }

    return responseJson({
      session_id: "session-2",
      join_url: "https://arcwright.test/v1/sessions/session-2/join",
      host_token: "host-token",
    });
  };

  const connector = new NightcapConnector({
    baseUrl: "https://arcwright.test",
    apiKey: "api-key-123",
    fetchImpl,
  });

  const received: unknown[] = [];
  let unsubscribe = () => {};
  const done = new Promise<void>((resolve) => {
    unsubscribe = connector.subscribeToEvents(
      {
        sessionId: "session-2",
        accessToken: "player-token-2",
        maxReconnectAttempts: 2,
        retryBaseDelayMs: 0,
        onError: (error) => {
          errors.push({
            message: error.message,
            retryDelayMs: error.retryDelayMs,
          });
        },
      },
      (event) => {
        received.push(event);
        unsubscribe();
        resolve();
      },
    );
  });

  await done;

  assert.equal(eventRequestCount, 2);
  assert.equal(received.length, 1);
  assert.equal(errors.length >= 1, true);
  assert.match(errors[0]?.message ?? "", /503/);
  assert.equal(errors[0]?.retryDelayMs, 0);
});

test("NightcapConnector unsubscribe stops later SSE events", async () => {
  const connector = new NightcapConnector({
    baseUrl: "https://arcwright.test",
    apiKey: "api-key-123",
    fetchImpl: async (input, init) => {
      const request =
        input instanceof Request
          ? input
          : new Request(input instanceof URL ? input : String(input), init);
      const url = new URL(request.url);
      if (url.pathname === "/v1/sessions/session-3/events") {
        return responseSseWithDelayedSecondEvent([
          {
            event_id: "event-3",
            session_id: "session-3",
            timestamp: "2026-06-22T12:00:02.000Z",
            category: "system",
            event_type: "connect",
            actor_id: null,
            target_audience: "host_only",
            target_player_id: null,
            payload: {},
            presentation_hints: {
              emotion: null,
              urgency: null,
              voice_hint: null,
              animation_hint: null,
              lighting_hint: null,
              pause_before_ms: 0,
            },
            sequence_number: 3,
          },
          {
            event_id: "event-4",
            session_id: "session-3",
            timestamp: "2026-06-22T12:00:03.000Z",
            category: "system",
            event_type: "disconnect",
            actor_id: null,
            target_audience: "host_only",
            target_player_id: null,
            payload: {},
            presentation_hints: {
              emotion: null,
              urgency: null,
              voice_hint: null,
              animation_hint: null,
              lighting_hint: null,
              pause_before_ms: 0,
            },
            sequence_number: 4,
          },
        ]);
      }

      return responseJson({
        session_id: "session-3",
        status: "active",
      });
    },
  });

  const received: Array<{ event_id: string }> = [];
  let unsubscribe = () => {};
  const done = new Promise<void>((resolve) => {
    unsubscribe = connector.subscribeToEvents(
      {
        sessionId: "session-3",
        accessToken: "player-token-3",
        retryBaseDelayMs: 0,
      },
      (event) => {
        received.push({ event_id: event.event_id });
        unsubscribe();
        resolve();
      },
    );
  });

  await done;
  await new Promise((resolve) => setTimeout(resolve, 50));

  assert.equal(received.length, 1);
  assert.equal(received[0]?.event_id, "event-3");
});

test("shared display visibility helpers only allow public and shared events", () => {
  assert.equal(isSharedDisplayVisibleEvent({ target_audience: "all" }), true);
  assert.equal(
    isSharedDisplayVisibleEvent({ target_audience: "shared_display" }),
    true,
  );
  assert.equal(
    isSharedDisplayVisibleEvent({ target_audience: "host_only" }),
    false,
  );
  assert.equal(isHostVisibleEvent({ target_audience: "host_only" }), true);
  assert.equal(
    isHostVisibleEvent({ target_audience: "specific_player" }),
    false,
  );
});
