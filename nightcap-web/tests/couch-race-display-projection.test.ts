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

test("shared display projects a suspect's public answer text", () => {
  const event = contentEvent({
    event_type: "interaction_answer",
    target_audience: "all",
    payload: {
      group_id: "window-1:suspect-vesper:intent-alibi",
      target_id: "suspect-vesper",
      option_id: "intent-alibi",
      selection_ids: ["sel-1"],
      answer: { text: "I was on the terrace the whole time." },
    },
  });

  const projection = projectSharedDisplayEvent(event);

  assert.equal(projection?.kind, "suspect_answer");
  assert.equal(projection?.body, "I was on the terrace the whole time.");
  assert.equal(projection?.suspectId, "suspect-vesper");
});

test("an interaction_answer with no answer text projects nothing", () => {
  const event = contentEvent({
    event_type: "interaction_answer",
    target_audience: "all",
    payload: { target_id: "suspect-vesper", answer: {} },
  });

  assert.equal(projectSharedDisplayEvent(event), null);
});

test("resource_effect_outcome projects only when publicly addressed", () => {
  // engine/resources/events.py emits this one event_type with a per-effect
  // audience: table-wide for effects like Make Them Wait, specific_player for
  // effects like Listen In. Both shapes are exercised here deliberately.
  const publicOutcome = contentEvent({
    category: "state_transition",
    event_type: "resource_effect_outcome",
    target_audience: "all",
    payload: {
      effect_key: "make-them-wait",
      outcome: { text: "Rowan's next question is delayed." },
    },
  });

  const privateOutcome = contentEvent({
    category: "private_delivery",
    event_type: "resource_effect_outcome",
    target_audience: "specific_player",
    target_player_id: "player-b",
    payload: {
      effect_key: "listen-in",
      outcome: { text: "You overhear Vesper's private tell." },
    },
  });

  const projected = projectSharedDisplayEvent(publicOutcome);
  assert.equal(projected?.kind, "resource_effect");
  assert.equal(projected?.body, "Rowan's next question is delayed.");

  assert.equal(projectSharedDisplayEvent(privateOutcome), null);
});

test("suspect answer projection carries asker identity for G3 crediting", () => {
  const event = contentEvent({
    event_type: "interaction_answer",
    target_audience: "all",
    payload: {
      target_id: "suspect-vesper",
      selection_ids: ["sel-1", "sel-2"],
      participant_ids: ["player-a", "player-b"],
      answer: { text: "I never touched the decanter." },
    },
  });

  const projection = projectSharedDisplayEvent(event);

  assert.deepEqual(projection?.askerIds, ["player-a", "player-b"]);
});

test("suspect answer projection defaults askerIds to an empty array", () => {
  const event = contentEvent({
    event_type: "interaction_answer",
    target_audience: "all",
    payload: {
      target_id: "suspect-vesper",
      answer: { text: "I never touched the decanter." },
    },
  });

  assert.deepEqual(projectSharedDisplayEvent(event)?.askerIds, []);
});

test("suspect answer projection filters non-string entries out of participant_ids", () => {
  const event = contentEvent({
    event_type: "interaction_answer",
    target_audience: "all",
    payload: {
      target_id: "suspect-vesper",
      participant_ids: ["player-a", 42, null, "player-b"],
      answer: { text: "I never touched the decanter." },
    },
  });

  assert.deepEqual(projectSharedDisplayEvent(event)?.askerIds, [
    "player-a",
    "player-b",
  ]);
});

// Regression guard, not a driver: the audience check in Task 1 already refuses
// these. It exists so a future projection added for one of these event types
// cannot quietly reach the shared display without this failing first.
test("no privately addressed Couch Race event type reaches the shared display", () => {
  const privateEventTypes = [
    "interaction_feedback",
    "resource_effect_source_revealed",
    "clue_delivery",
    "mini_game_clue_delivery",
    "tmst_private_prompt_ready",
  ];

  for (const eventType of privateEventTypes) {
    const event = contentEvent({
      category: "private_delivery",
      event_type: eventType,
      target_audience: "specific_player",
      target_player_id: "player-a",
      payload: {
        text: "PRIVATE-CANARY",
        answer: { text: "PRIVATE-CANARY" },
        outcome: { text: "PRIVATE-CANARY" },
      },
    });

    const projection = projectSharedDisplayEvent(event);
    assert.equal(
      projection,
      null,
      `${eventType} must not project to the shared display`,
    );
    assert.ok(
      !JSON.stringify(projection ?? {}).includes("PRIVATE-CANARY"),
      `${eventType} leaked private payload text to the shared display`,
    );
  }
});
