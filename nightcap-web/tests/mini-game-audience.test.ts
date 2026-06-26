import assert from "node:assert/strict";
import test from "node:test";

import {
  isAuthorizedForSurface,
  withAudienceGuard,
} from "../src/mini-game-kit/index.js";
import type { ContentEvent } from "../src/types.js";

function ev(
  audience: ContentEvent["target_audience"],
  targetPlayer: string | null = null,
): ContentEvent {
  return {
    event_id: "evt-1",
    session_id: "session-1",
    timestamp: "2026-06-25T00:00:00Z",
    category: "private_delivery",
    event_type: "test_event",
    actor_id: null,
    target_audience: audience,
    target_player_id: targetPlayer,
    payload: {},
    presentation_hints: {
      emotion: null,
      urgency: null,
      voice_hint: null,
      animation_hint: null,
      lighting_hint: null,
      pause_before_ms: 0,
    },
    sequence_number: 1,
  };
}

test("audience: all is authorized for every surface", () => {
  for (const surface of ["phone", "shared_display", "host"] as const) {
    assert.equal(
      isAuthorizedForSurface(ev("all"), {
        surface,
        participantId: "p-1",
      }),
      true,
    );
  }
});

test("audience: specific_player is authorized for matching phone only", () => {
  const event = ev("specific_player", "p-1");
  assert.equal(
    isAuthorizedForSurface(event, { surface: "phone", participantId: "p-1" }),
    true,
  );
  assert.equal(
    isAuthorizedForSurface(event, { surface: "phone", participantId: "p-2" }),
    false,
  );
  assert.equal(
    isAuthorizedForSurface(event, {
      surface: "shared_display",
      participantId: "p-1",
    }),
    false,
  );
  assert.equal(
    isAuthorizedForSurface(event, { surface: "host", participantId: "p-1" }),
    false,
  );
});

test("audience: shared_display is authorized for shared display only", () => {
  const event = ev("shared_display");
  assert.equal(
    isAuthorizedForSurface(event, {
      surface: "shared_display",
      participantId: "p-1",
    }),
    true,
  );
  assert.equal(
    isAuthorizedForSurface(event, { surface: "phone", participantId: "p-1" }),
    false,
  );
  assert.equal(
    isAuthorizedForSurface(event, { surface: "host", participantId: "p-1" }),
    false,
  );
});

test("audience: host_only is authorized for host only", () => {
  const event = ev("host_only");
  assert.equal(
    isAuthorizedForSurface(event, { surface: "host", participantId: "p-1" }),
    true,
  );
  assert.equal(
    isAuthorizedForSurface(event, {
      surface: "shared_display",
      participantId: "p-1",
    }),
    false,
  );
  assert.equal(
    isAuthorizedForSurface(event, { surface: "phone", participantId: "p-1" }),
    false,
  );
});

test("withAudienceGuard forwards authorized events", () => {
  let received: ContentEvent | null = null;
  const guarded = withAudienceGuard(
    { surface: "phone", participantId: "p-1" },
    (e) => {
      received = e;
    },
  );
  const event = ev("specific_player", "p-1");
  guarded(event);
  assert.equal(received, event);
});

test("withAudienceGuard drops unauthorized events silently", () => {
  let count = 0;
  const guarded = withAudienceGuard(
    { surface: "phone", participantId: "p-1" },
    () => {
      count += 1;
    },
  );
  guarded(ev("specific_player", "p-other"));
  guarded(ev("host_only"));
  guarded(ev("shared_display"));
  assert.equal(count, 0);
});

test("withAudienceGuard warns when specific_player leaks to wrong surface", () => {
  const warnings: string[] = [];
  const guarded = withAudienceGuard(
    { surface: "shared_display", participantId: "p-1" },
    () => {},
    { warn: (msg: string) => warnings.push(msg) },
  );
  guarded(ev("specific_player", "p-1"));
  assert.equal(warnings.length, 1);
  assert.match(warnings[0]!, /specific_player event/);
});
