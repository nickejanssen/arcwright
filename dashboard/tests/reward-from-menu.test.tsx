// AW-343/AW-332: a reward survives a missed live message because the phone
// reads it from the authenticated menu route after phase changes.

import assert from "node:assert/strict";
import test from "node:test";
import { createElement } from "react";

import { PhoneView } from "../src/screens/WaitingScreen.js";
import { DEFAULT_SETTINGS } from "../src/shell/settings.js";
import { mount, settle } from "./helpers/dom.js";
import {
  ME,
  fakeEngine,
  lobby,
  round,
  withFetch,
} from "./helpers/round-fixtures.js";

const noop = async () => undefined;
const screen = (phaseEntry: number) =>
  createElement(PhoneView, {
    sessionId: "game-uuid-1111",
    displayName: "Jordan",
    participantId: ME,
    characterId: "character-internal",
    getToken: async () => "player-sign-in",
    joinCode: "K7QP",
    joinUrl: "https://app.test/join?code=K7QP",
    feed: {
      lobby: lobby(),
      round: round({ phase: "bridge", phaseEntry }),
      unreachable: false,
      gone: false,
    },
    role: "player",
    controls: {
      start: noop,
      pause: noop,
      resume: noop,
      moveOn: noop,
      end: noop,
      resolveMiniGame: noop,
      cancelMiniGame: noop,
    },
    settings: DEFAULT_SETTINGS,
    onSettingsChange: () => undefined,
  });

test("rewards arrive from menu reads, acknowledge once, persist across remounts, and show a second grant", async () => {
  window.localStorage.clear();
  const engine = fakeEngine({ budget: 5 });
  engine.rewards = [
    {
      grant_id: "grant_internal_1",
      run_id: "run_internal_1",
      beat_id: "beat_internal_1",
      amount: 1,
      kind: "investigation",
    },
  ];

  await withFetch(engine, async () => {
    const first = await mount(screen(12));
    await settle();
    assert.ok(first.text().includes("You earned one more investigation."));
    assert.ok(first.text().includes("5 left"));
    assert.ok(engine.calls.some((call) => call.path.endsWith("/me/menu")));
    assert.ok(!engine.calls.some((call) => call.path.includes("events")));
    await first.click("OK");
    await first.unmount();

    const afterRemount = await mount(screen(12));
    await settle();
    assert.ok(
      !afterRemount.text().includes("You earned one more investigation."),
    );
    await afterRemount.unmount();

    engine.budget = 6;
    engine.rewards.push({
      grant_id: "grant_internal_2",
      run_id: "run_internal_2",
      beat_id: "beat_internal_2",
      amount: 1,
      kind: "investigation",
    });
    const secondGrant = await mount(screen(13));
    await settle();
    assert.ok(
      secondGrant.text().includes("You earned one more investigation."),
    );
    assert.ok(secondGrant.text().includes("6 left"));
    await secondGrant.unmount();
  });
});

test("a failed reward menu read retries during the same phase", async () => {
  window.localStorage.clear();
  const engine = fakeEngine({ budget: 5 });
  engine.dropMenus = 1;
  engine.rewards = [
    {
      grant_id: "grant_internal_1",
      run_id: "run_internal_1",
      beat_id: "beat_internal_1",
      amount: 1,
      kind: "investigation",
    },
  ];

  await withFetch(engine, async () => {
    const page = await mount(screen(12));
    await new Promise((done) => setTimeout(done, 1100));
    await settle();

    assert.ok(
      engine.calls.filter((call) => call.path.endsWith("/me/menu")).length >= 2,
    );
    assert.ok(page.text().includes("You earned one more investigation."));
    await page.unmount();
  });
});
