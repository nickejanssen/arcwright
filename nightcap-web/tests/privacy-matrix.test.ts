import assert from "node:assert/strict";
import test from "node:test";

import { NightcapConnector } from "../src/connector.js";
import type { ContentEvent } from "../src/types.js";
import { getPlayerEventBody, getSharedDisplayEventBody } from "../src/ui.js";

type RoleName = "player-a" | "player-b" | "shared-display" | "host";

function responseSse(events: unknown[]): Response {
  const body = events
    .map((event) => `data: ${JSON.stringify(event)}\n\n`)
    .join("");

  return new Response(
    new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(new TextEncoder().encode(body));
      },
      cancel() {
        return;
      },
    }),
    {
      status: 200,
      headers: {
        "content-type": "text/event-stream",
      },
    },
  );
}

async function collectEvents(
  connector: NightcapConnector,
  sessionId: string,
  accessToken: string,
  expectedCount: number,
): Promise<Array<ContentEvent>> {
  const received: Array<ContentEvent> = [];
  let unsubscribe = () => {};

  await new Promise<void>((resolve) => {
    unsubscribe = connector.subscribeToEvents(
      {
        sessionId,
        accessToken,
        retryBaseDelayMs: 0,
      },
      (event) => {
        received.push(event);
        if (received.length >= expectedCount) {
          unsubscribe();
          resolve();
        }
      },
    );
  });

  return received;
}

test("Nightcap privacy matrix keeps each audience on the intended device role", async () => {
  const sessionId = "session-privacy-matrix";

  const allEvent = {
    event_id: "event-all",
    session_id: sessionId,
    timestamp: "2026-06-22T12:00:00.000Z",
    category: "acknowledgement",
    event_type: "room_update",
    actor_id: null,
    target_audience: "all",
    target_player_id: null,
    payload: { message: "The room collectively notices the back door open." },
    presentation_hints: {
      emotion: "tense",
      urgency: "medium",
      voice_hint: null,
      animation_hint: null,
      lighting_hint: null,
      pause_before_ms: 0,
    },
    sequence_number: 1,
  } as const;

  const playerAEvent = {
    event_id: "event-player-a",
    session_id: sessionId,
    timestamp: "2026-06-22T12:00:01.000Z",
    category: "private_delivery",
    event_type: "clue_delivery",
    actor_id: null,
    target_audience: "specific_player",
    target_player_id: "player-a",
    payload: { clue_id: "clue-a", text: "Player A private clue text" },
    presentation_hints: {
      emotion: "tense",
      urgency: "high",
      voice_hint: null,
      animation_hint: null,
      lighting_hint: null,
      pause_before_ms: 0,
    },
    sequence_number: 2,
  } as const;

  const playerBEvent = {
    event_id: "event-player-b",
    session_id: sessionId,
    timestamp: "2026-06-22T12:00:02.000Z",
    category: "private_delivery",
    event_type: "clue_delivery",
    actor_id: null,
    target_audience: "specific_player",
    target_player_id: "player-b",
    payload: { clue_id: "clue-b", text: "Player B private clue text" },
    presentation_hints: {
      emotion: "tense",
      urgency: "high",
      voice_hint: null,
      animation_hint: null,
      lighting_hint: null,
      pause_before_ms: 0,
    },
    sequence_number: 3,
  } as const;

  const hostOnlyEvent = {
    event_id: "event-host",
    session_id: sessionId,
    timestamp: "2026-06-22T12:00:03.000Z",
    category: "system",
    event_type: "host_note",
    actor_id: null,
    target_audience: "host_only",
    target_player_id: null,
    payload: { message: "Host-only clue summary." },
    presentation_hints: {
      emotion: null,
      urgency: null,
      voice_hint: null,
      animation_hint: null,
      lighting_hint: null,
      pause_before_ms: 0,
    },
    sequence_number: 4,
  } as const;

  const sharedDisplayEvent = {
    event_id: "event-display",
    session_id: sessionId,
    timestamp: "2026-06-22T12:00:04.000Z",
    category: "acknowledgement",
    event_type: "clue_acknowledged",
    actor_id: null,
    target_audience: "shared_display",
    target_player_id: null,
    payload: { message: "A clue has been passed to Rowan." },
    presentation_hints: {
      emotion: "warm",
      urgency: "low",
      voice_hint: null,
      animation_hint: null,
      lighting_hint: null,
      pause_before_ms: 0,
    },
    sequence_number: 5,
  } as const;

  const matrix: Array<{
    role: RoleName;
    accessToken: string;
    expectedAudiences: Array<string>;
    expectedCount: number;
  }> = [
    {
      role: "player-a",
      accessToken: "player-a-token",
      expectedAudiences: ["all", "specific_player"],
      expectedCount: 2,
    },
    {
      role: "player-b",
      accessToken: "player-b-token",
      expectedAudiences: ["all", "specific_player"],
      expectedCount: 2,
    },
    {
      role: "shared-display",
      accessToken: "display-token",
      expectedAudiences: ["all", "shared_display"],
      expectedCount: 2,
    },
    {
      role: "host",
      accessToken: "host-token",
      expectedAudiences: ["host_only"],
      expectedCount: 1,
    },
  ];

  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    const request =
      input instanceof Request
        ? input
        : new Request(input instanceof URL ? input : String(input), init);
    const url = new URL(request.url);

    if (
      request.method === "GET" &&
      url.pathname === `/v1/sessions/${sessionId}/events`
    ) {
      const authorization = request.headers.get("authorization");
      if (authorization === "Bearer player-a-token") {
        return responseSse([allEvent, playerAEvent]);
      }
      if (authorization === "Bearer player-b-token") {
        return responseSse([allEvent, playerBEvent]);
      }
      if (authorization === "Bearer display-token") {
        return responseSse([allEvent, sharedDisplayEvent]);
      }
      if (authorization === "Bearer host-token") {
        return responseSse([hostOnlyEvent]);
      }
    }

    return new Response("not found", { status: 404 });
  };

  const connector = new NightcapConnector({
    baseUrl: "https://arcwright.test",
    apiKey: "api-key-123",
    fetchImpl,
  });

  // Trust boundary: Arcwright owns audience filtering, and this matrix only
  // proves the browser surfaces do not widen or leak what scoped streams send.

  const receivedByRole = new Map(
    await Promise.all(
      matrix.map(
        async ({ role, accessToken, expectedCount }) =>
          [
            role,
            await collectEvents(
              connector,
              sessionId,
              accessToken,
              expectedCount,
            ),
          ] as const,
      ),
    ),
  );

  for (const scenario of matrix) {
    const events = receivedByRole.get(scenario.role) ?? [];
    assert.deepEqual(
      events.map((event) => event.target_audience),
      scenario.expectedAudiences,
    );
  }

  const playerAEvents = receivedByRole.get("player-a") ?? [];
  const playerBEvents = receivedByRole.get("player-b") ?? [];
  const sharedDisplayEvents = receivedByRole.get("shared-display") ?? [];
  const hostEvents = receivedByRole.get("host") ?? [];

  assert.ok(
    !JSON.stringify(playerAEvents).includes("Player B private clue text"),
  );
  assert.ok(
    !JSON.stringify(playerBEvents).includes("Player A private clue text"),
  );
  assert.ok(
    !JSON.stringify(sharedDisplayEvents).includes("Player A private clue text"),
  );
  assert.ok(
    !JSON.stringify(sharedDisplayEvents).includes("Player B private clue text"),
  );
  assert.ok(
    !JSON.stringify(sharedDisplayEvents).includes("Host-only clue summary."),
  );
  assert.ok(!JSON.stringify(hostEvents).includes("Player A private clue text"));
  assert.ok(!JSON.stringify(hostEvents).includes("Player B private clue text"));
  assert.ok(
    !JSON.stringify(hostEvents).includes("A clue has been passed to Rowan."),
  );

  assert.equal(getPlayerEventBody(playerAEvent), "Player A private clue text");
  assert.equal(getPlayerEventBody(playerBEvent), "Player B private clue text");
  assert.equal(
    getSharedDisplayEventBody(sharedDisplayEvent),
    "A clue has been passed to Rowan.",
  );
  assert.equal(
    getSharedDisplayEventBody(allEvent),
    "The room collectively notices the back door open.",
  );
});
