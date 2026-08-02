import assert from "node:assert/strict";
import test from "node:test";

import { projectSharedDisplayEvent } from "../src/couch-race/display-projection.js";
import type { ContentEvent } from "../src/types.js";

export function contentEvent(overrides: Partial<ContentEvent>): ContentEvent {
  return {
    event_id: "event-1",
    session_id: "session-1",
    timestamp: "2026-08-01T12:00:00.000Z",
    category: "character_dialogue",
    event_type: "interaction_answer",
    actor_id: null,
    target_audience: "all",
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
    sequence_number: 1,
    ...overrides,
  } as ContentEvent;
}

test("shared display refuses to project any event not addressed to it", () => {
  // Deliberately uses a HANDLED event_type with a private audience. A test
  // using an unhandled type would pass vacuously and prove nothing.
  const event = contentEvent({
    event_type: "interaction_answer",
    target_audience: "specific_player",
    target_player_id: "player-a",
    payload: {
      target_id: "suspect-vesper",
      answer: { text: "Private aside meant only for player A." },
    },
  });

  assert.equal(projectSharedDisplayEvent(event), null);
});
