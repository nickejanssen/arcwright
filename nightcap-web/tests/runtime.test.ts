import assert from "node:assert/strict";
import test from "node:test";

import {
  isNightcapPlayerSessionExpired,
  normalizeNightcapPlayerSessionState,
} from "../src/runtime.js";

test("nightcap player session state requires an expiry timestamp", () => {
  assert.deepEqual(
    normalizeNightcapPlayerSessionState({
      session_id: "session-1",
      player_id: "player-1",
      character_id: "character-1",
      player_token: "player-token-1",
      expires_at: 1_725_000_000_000,
      last_sequence_number: 12.7,
    }),
    {
      session_id: "session-1",
      player_id: "player-1",
      character_id: "character-1",
      player_token: "player-token-1",
      expires_at: 1_725_000_000_000,
      last_sequence_number: 12,
    },
  );

  assert.equal(
    normalizeNightcapPlayerSessionState({
      session_id: "session-1",
      player_id: "player-1",
      character_id: "character-1",
      player_token: "player-token-1",
      last_sequence_number: 12,
    }),
    null,
  );
});

test("nightcap player session expiry is detected before reconnect", () => {
  assert.equal(
    isNightcapPlayerSessionExpired(
      {
        session_id: "session-1",
        player_id: "player-1",
        character_id: "character-1",
        player_token: "player-token-1",
        expires_at: 1_725_000_000_000,
        last_sequence_number: 12,
      },
      1_725_000_000_001,
    ),
    true,
  );

  assert.equal(
    isNightcapPlayerSessionExpired(
      {
        session_id: "session-1",
        player_id: "player-1",
        character_id: "character-1",
        player_token: "player-token-1",
        expires_at: 1_725_000_000_000,
        last_sequence_number: 12,
      },
      1_724_999_999_999,
    ),
    false,
  );
});
