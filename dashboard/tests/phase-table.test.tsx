// The phase-to-screen table: one walk over every phase kind the engine has,
// checking the TV and the phone each get the screen the table names, and that
// a phase with an empty slot falls back to the plain screen.

import assert from "node:assert/strict";
import test from "node:test";

import { createElement } from "react";
import type { LobbyState } from "../src/api/lobby.js";
import type { RoundState } from "../src/api/round.js";
import { PhoneView } from "../src/screens/WaitingScreen.js";
import { TvView } from "../src/screens/DisplayScreen.js";
import { DEFAULT_SLOTS, resolveScreen } from "../src/shell/phaseScreens.js";
import type { SlotTable } from "../src/shell/phaseScreens.js";
import { DEFAULT_SETTINGS } from "../src/shell/settings.js";
import { mount } from "./helpers/dom.js";

// The phase names the engine's PhaseKind has (engine/arc/models.py).
const PHASES = ["scene", "choices", "mini_game", "bridge", "commit"] as const;

function lobby(status: string): LobbyState {
  return {
    session_id: "game-1",
    join_code: "K7QP",
    status,
    current_beat_id: "beat_1",
    is_terminal: false,
    min_players: 2,
    player_count: 3,
    players: [],
  };
}

function round(phase: string | null, status: RoundState["status"]): RoundState {
  return {
    sessionStatus: "active",
    beatName: null,
    phase,
    status,
    secondsLeft: 30,
    phaseEntry: 1,
    readyCount: 0,
    playerCount: 3,
    players: [],
    lines: [],
  };
}

const named = (label: string) => () => createElement("p", null, label);

const fullSlots: SlotTable = Object.fromEntries(
  PHASES.map((p) => [
    p,
    { tv: named(`TV-SLOT:${p}`), phone: named(`PHONE-SLOT:${p}`) },
  ]),
);

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

function tv(l: LobbyState, r: RoundState | null, slots?: SlotTable) {
  return createElement(TvView, {
    sessionId: "game-1",
    feed: { lobby: l, round: r, unreachable: false, gone: false },
    joinBaseUrl: "https://app.test",
    ...(slots ? { slots } : {}),
  });
}

function phone(l: LobbyState, r: RoundState | null, slots?: SlotTable) {
  return createElement(PhoneView, {
    sessionId: "game-1",
    displayName: "Jordan",
    joinCode: "K7QP",
    joinUrl: "https://app.test/join?code=K7QP",
    feed: { lobby: l, round: r, unreachable: false, gone: false },
    role: "player",
    controls,
    settings: DEFAULT_SETTINGS,
    onSettingsChange: () => undefined,
    ...(slots ? { slots } : {}),
  });
}

test("every phase kind names its slot on both surfaces", async () => {
  for (const phase of PHASES) {
    const l = lobby("active");
    const r = round(phase, "running");

    const tvResult = resolveScreen("tv", l, r, fullSlots);
    const phoneResult = resolveScreen("phone", l, r, fullSlots);
    assert.equal(tvResult.kind, "phase");
    assert.equal(phoneResult.kind, "phase");

    const tvPage = await mount(tv(l, r, fullSlots));
    assert.ok(tvPage.text().includes(`TV-SLOT:${phase}`), `TV shows ${phase}`);
    await tvPage.unmount();

    const phonePage = await mount(phone(l, r, fullSlots));
    assert.ok(
      phonePage.text().includes(`PHONE-SLOT:${phase}`),
      `phone shows ${phase}`,
    );
    await phonePage.unmount();
  }
});

test("a phase with an empty slot falls back to the plain screen, never a phase name", async () => {
  for (const phase of PHASES) {
    const l = lobby("active");
    const r = round(phase, "running");
    assert.equal(resolveScreen("tv", l, r, {}).kind, "fallback");

    const tvPage = await mount(tv(l, r, {}));
    assert.ok(tvPage.text().includes("Play continues."));
    assert.ok(!tvPage.text().includes(phase));
    await tvPage.unmount();

    const phonePage = await mount(phone(l, r, {}));
    assert.ok(phonePage.text().includes("Eyes on the TV."));
    assert.ok(!phonePage.text().includes(phase));
    await phonePage.unmount();
  }
});

test("a slot on one surface only leaves the other on the plain screen", async () => {
  const slots: SlotTable = { scene: { tv: named("TV-ONLY") } };
  const l = lobby("active");
  const r = round("scene", "running");
  assert.equal(resolveScreen("tv", l, r, slots).kind, "phase");
  assert.equal(resolveScreen("phone", l, r, slots).kind, "fallback");
});

test("room, paused and ended come from the engine's status, ahead of any phase", () => {
  const scene = round("scene", "running");
  assert.equal(
    resolveScreen("tv", lobby("created"), null, fullSlots).kind,
    "room",
  );
  assert.equal(
    resolveScreen("tv", lobby("paused"), scene, fullSlots).kind,
    "paused",
  );
  assert.equal(
    resolveScreen("tv", lobby("active"), round("scene", "paused"), fullSlots)
      .kind,
    "paused",
  );
  assert.equal(
    resolveScreen("phone", lobby("completed"), scene, fullSlots).kind,
    "ended",
  );
  assert.equal(
    resolveScreen("phone", lobby("active"), round(null, "ended"), fullSlots)
      .kind,
    "ended",
  );
});

test("the shipped slot maps cover every phase, Last Call to the recap", () => {
  for (const phase of PHASES) {
    const filled =
      phase === "scene" ||
      phase === "choices" ||
      phase === "mini_game" ||
      phase === "bridge" ||
      phase === "commit" ||
      phase === "reveal" ||
      phase === "result" ||
      phase === "recap";
    for (const surface of ["tv", "phone"] as const) {
      assert.equal(
        resolveScreen(
          surface,
          lobby("active"),
          round(phase, "running"),
          DEFAULT_SLOTS,
        ).kind,
        filled ? "phase" : "fallback",
        `${surface} ${phase}`,
      );
    }
  }
});
