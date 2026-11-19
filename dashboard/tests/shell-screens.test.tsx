// Screens 1, 2, 3 and 23 from fixture data: the key words show, no internal ID
// appears anywhere, and the TV shows nothing private.

import assert from "node:assert/strict";
import test from "node:test";

import { createElement } from "react";
import type { LobbyState } from "../src/api/lobby.js";
import type { RoundState } from "../src/api/round.js";
import { PhoneView } from "../src/screens/WaitingScreen.js";
import { TvView, formatClock } from "../src/screens/DisplayScreen.js";
import { DEFAULT_SETTINGS } from "../src/shell/settings.js";
import SettingsPanel from "../src/shell/SettingsPanel.js";
import { mount } from "./helpers/dom.js";

// Values that must never be drawn: internal IDs and tokens.
const SECRETS = [
  "beat_internal_1",
  "concept_internal_9",
  "game-uuid-1111",
  "participant-uuid-2222",
  "participant-uuid-3333",
  "character-uuid-4444",
  "custom-token-5555",
];

function lobby(over: Partial<LobbyState> = {}): LobbyState {
  return {
    session_id: "game-uuid-1111",
    join_code: "K7QP",
    status: "created",
    current_beat_id: "beat_internal_1",
    is_terminal: false,
    min_players: 2,
    player_count: 1,
    players: [
      { participant_id: "participant-uuid-2222", display_name: "Jordan" },
    ],
    ...over,
  };
}

function round(over: Partial<RoundState> = {}): RoundState {
  return {
    sessionStatus: "active",
    beatName: "The Study",
    phase: "scene",
    status: "running",
    secondsLeft: 102,
    readyCount: 1,
    playerCount: 3,
    lines: [{ concept_id: "concept_internal_9", text: "A line" }],
    ...over,
  };
}

const noop = async () => undefined;
const controls = {
  start: noop,
  pause: noop,
  resume: noop,
  moveOn: noop,
  end: noop,
  resolveMiniGame: noop,
  cancelMiniGame: noop,
};

function tv(l: LobbyState | null, r: RoundState | null, extra = {}) {
  return createElement(TvView, {
    sessionId: "game-uuid-1111",
    feed: { lobby: l, round: r, unreachable: false, gone: false, ...extra },
    joinBaseUrl: "https://app.test",
  });
}

function phone(l: LobbyState | null, r: RoundState | null, extra = {}) {
  return createElement(PhoneView, {
    sessionId: "game-uuid-1111",
    displayName: "Jordan",
    joinCode: "K7QP",
    joinUrl: "https://app.test/join?code=K7QP",
    feed: { lobby: l, round: r, unreachable: false, gone: false, ...extra },
    role: "player",
    controls,
    settings: DEFAULT_SETTINGS,
    onSettingsChange: () => undefined,
  });
}

function assertNoSecrets(text: string, html: string) {
  for (const secret of SECRETS) {
    assert.ok(!text.includes(secret), `text leaks ${secret}`);
    assert.ok(!html.includes(secret), `markup leaks ${secret}`);
  }
}

test("screen 1, the TV room: code, count, names, and no maximum player count", async () => {
  const few = await mount(tv(lobby(), null));
  assert.ok(few.text().includes("Join on your phone"));
  assert.ok(few.text().includes("K7QP"));
  assert.ok(few.text().includes("Needs 2 or more players to start."));
  assert.ok(few.text().includes("Jordan"));
  assert.ok(
    !/\b(2 to 4|4 players|up to)\b/.test(few.text()),
    "no maximum printed",
  );
  assertNoSecrets(few.text(), few.container.innerHTML);
  await few.unmount();

  const enough = await mount(
    tv(
      lobby({
        player_count: 3,
        players: [
          { participant_id: "participant-uuid-2222", display_name: "Jordan" },
          { participant_id: "participant-uuid-3333", display_name: null },
        ],
      }),
      null,
    ),
  );
  assert.ok(enough.text().includes("3 seated. The host can start the game."));
  assert.ok(
    enough.text().includes("Guest"),
    "an unnamed player is not shown as an ID",
  );
  assert.equal(enough.buttons().length, 0, "the TV has no controls");
  await enough.unmount();
});

test("the TV shows connecting, cannot-reach and game-gone states", async () => {
  const connecting = await mount(tv(null, null));
  assert.ok(connecting.text().includes("Connecting..."));
  await connecting.unmount();

  const down = await mount(tv(null, null, { unreachable: true }));
  assert.ok(down.text().includes("Cannot reach the game. Trying again."));
  await down.unmount();

  const gone = await mount(tv(null, null, { gone: true }));
  assert.ok(gone.text().includes("This game is no longer running."));
  await gone.unmount();
});

test("screen 23 on the TV: Paused and the time left, from the engine's seconds", async () => {
  const page = await mount(
    tv(
      lobby({ status: "paused" }),
      round({ status: "paused", secondsLeft: 102 }),
    ),
  );
  assert.ok(page.text().includes("Paused"));
  assert.ok(page.text().includes("1:42 left in this part"));
  assertNoSecrets(page.text(), page.container.innerHTML);
  await page.unmount();
  assert.equal(formatClock(5), "0:05");
  assert.equal(formatClock(-3), "0:00");
});

test("the TV in play shows no beat, phase or concept name", async () => {
  const page = await mount(tv(lobby({ status: "active" }), round()));
  assert.ok(page.text().includes("Play continues."));
  for (const word of ["scene", "The Study", "A line", "Current beat"]) {
    assert.ok(!page.text().includes(word), `shows ${word}`);
  }
  assertNoSecrets(page.text(), page.container.innerHTML);
  await page.unmount();
});

test("screen 3, the phone seated: greeting, waiting words, who is at the table, Menu", async () => {
  const page = await mount(phone(lobby(), null));
  assert.ok(page.text().includes("You are in, Jordan."));
  assert.ok(
    page.text().includes("Waiting for the host to start. Look at the TV."),
  );
  assert.ok(page.text().includes("At the table: Jordan"));
  assert.ok(page.button("Menu"));
  assertNoSecrets(page.text(), page.container.innerHTML);
  await page.unmount();
});

test("screen 23 on the phone: paused words, and Resume is in the menu", async () => {
  const page = await mount(
    phone(lobby({ status: "paused" }), round({ status: "paused" })),
  );
  assert.ok(
    page
      .text()
      .includes("Paused. Tap Menu, then Resume, when everyone is back."),
  );
  await page.click("Menu");
  assert.ok(page.button("Resume"));
  assertNoSecrets(page.text(), page.container.innerHTML);
  await page.unmount();
});

test("the phone in play and at the end, and when the game is gone", async () => {
  const play = await mount(phone(lobby({ status: "active" }), round()));
  assert.ok(play.text().includes("Eyes on the TV."));
  assertNoSecrets(play.text(), play.container.innerHTML);
  await play.unmount();

  const over = await mount(phone(lobby({ status: "completed" }), round()));
  assert.ok(over.text().includes("The game has ended."));
  await over.unmount();

  const gone = await mount(phone(null, null, { gone: true }));
  assert.ok(gone.text().includes("This game is no longer running."));
  assert.equal(
    gone.container.querySelector("a")?.getAttribute("href"),
    "/join",
    "a way back to the join page",
  );
  await gone.unmount();
});

test("Settings: text size, motion, room code and rejoin link; the link is the join address", async () => {
  const changes: Array<{ textSize: string; reduceMotion: string }> = [];
  const page = await mount(
    createElement(SettingsPanel, {
      settings: DEFAULT_SETTINGS,
      onChange: (next) => void changes.push(next),
      roomCode: "K7QP",
      joinUrl: "https://app.test/join?code=K7QP",
      onBack: () => undefined,
    }),
  );
  for (const words of [
    "Text size",
    "Normal",
    "Large",
    "Extra large",
    "Reduce motion",
    "Follow my phone",
    "Always",
    "Room code: K7QP",
    "https://app.test/join?code=K7QP",
  ]) {
    assert.ok(page.text().includes(words), `shows ${words}`);
  }
  assert.ok(page.button("Copy link"));
  assert.ok(!page.text().includes("Leave game"), "Leave game is not offered");
  assert.ok(!page.text().includes("token"));

  const large = Array.from(page.container.querySelectorAll("label")).find((l) =>
    l.textContent?.includes("Large"),
  )!;
  (large.querySelector("input") as HTMLInputElement).click();
  assert.deepEqual(changes[0], { textSize: "large", reduceMotion: "system" });
  await page.unmount();
});
