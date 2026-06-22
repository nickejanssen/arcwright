import test from "node:test";
import assert from "node:assert/strict";
import {
  NightcapConnector,
  type CreateSessionRequest,
  type SessionStateResponse,
} from "../src/connector.js";

function responseJson(body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: {
      "content-type": "application/json; charset=utf-8",
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
  assert.equal(calls[1]?.method, "GET");
  assert.equal(calls[1]?.path, "/v1/sessions/session-1");
  assert.equal(calls[1]?.headers.get("x-api-key"), "api-key-123");
  assert.equal(calls[2]?.method, "GET");
  assert.equal(calls[2]?.path, "/v1/sessions/session-1/events?since=0");
  assert.equal(calls[2]?.headers.get("authorization"), "Bearer player-token-1");
});
