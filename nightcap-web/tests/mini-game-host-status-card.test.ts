// Tests for the extracted host-status-card kit helper.

import assert from "node:assert/strict";
import test from "node:test";
import { Window as HappyWindow } from "happy-dom";

import {
  createHostStatusCard,
  type MiniGameDefinition,
} from "../src/mini-game-kit/index.js";
import type { ContentEvent, MiniGameState } from "../src/types.js";

function makeDefinition(): MiniGameDefinition {
  return {
    schema_version: "1.0",
    game_id: "test",
    version: "0.1.0",
    mechanic_type: "timed-choice",
    participation_mode: "individual",
    content_mode: "authored",
    min_players: 1,
    max_players: 10,
    duration_seconds: 30,
    rules: {},
    authored_content: null,
    generation_constraints: null,
    behavioral_outputs: [],
    clue_fallback: {
      delay_seconds: 18,
      clue_variant: "reduced",
      host_override: true,
    },
  };
}

function makeState(): MiniGameState {
  return {
    runId: "run-1",
    gameId: "test",
    status: "active",
    deadlineAt: null,
    mySubmissions: [],
  };
}

function makeEvent(eventType: string): ContentEvent {
  return {
    event_id: "evt",
    session_id: "session",
    timestamp: "2026-06-26T00:00:00Z",
    category: "acknowledgement",
    event_type: eventType,
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
  };
}

test("host status card renders badge, count, and fallback note", () => {
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const root = doc.createElement("section");
  const lifecycle = createHostStatusCard(root, {
    state: makeState(),
    definition: makeDefinition(),
    countLabel: (n) => `${n} answered`,
    countEventType: "mini_game_submission_accepted",
  });

  assert.equal(
    root.querySelector('[data-role="status"]')?.textContent,
    "active",
  );
  assert.equal(
    root.querySelector('[data-role="count"]')?.textContent,
    "0 answered",
  );
  assert.match(
    root.querySelector('[data-role="fallback"]')?.textContent ?? "",
    /Clue fallback: 18s, variant reduced/,
  );

  lifecycle.unmount();
});

test("host status card increments count on configured event type", () => {
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const root = doc.createElement("section");
  const lifecycle = createHostStatusCard(root, {
    state: makeState(),
    definition: makeDefinition(),
    countLabel: (n) => `${n} pieces shared`,
    countEventType: "mini_game_piece_shared",
  });

  lifecycle.handleEvent(makeEvent("mini_game_piece_shared"));
  lifecycle.handleEvent(makeEvent("mini_game_piece_shared"));
  lifecycle.handleEvent(makeEvent("unrelated_event"));

  assert.equal(
    root.querySelector('[data-role="count"]')?.textContent,
    "2 pieces shared",
  );

  lifecycle.unmount();
});

test("host status card update changes the badge", () => {
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const root = doc.createElement("section");
  const lifecycle = createHostStatusCard(root, {
    state: makeState(),
    definition: makeDefinition(),
    countLabel: (n) => `${n} answered`,
    countEventType: "mini_game_submission_accepted",
  });

  lifecycle.update({ ...makeState(), status: "timed_out" });
  assert.equal(
    root.querySelector('[data-role="status"]')?.textContent,
    "timed_out",
  );

  lifecycle.unmount();
});
