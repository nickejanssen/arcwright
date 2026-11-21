// Recovery cases for the investigate screen found in review of AW-332 part A:
// a finding survives a direct phase change, a 5xx keeps the same choice ID, and
// a failed first menu read loads by itself.

import assert from "node:assert/strict";
import test from "node:test";

import { createElement } from "react";
import InvestigatePhone, {
  MENU_RETRY_MS,
  clearHeldFinding,
} from "../src/screens/round/InvestigatePhone.js";
import { PhoneView } from "../src/screens/WaitingScreen.js";
import { DEFAULT_SETTINGS } from "../src/shell/settings.js";
import { mount } from "./helpers/dom.js";
import {
  ME,
  fakeEngine,
  lobby,
  round,
  withFetch,
} from "./helpers/round-fixtures.js";

const getToken = async () => "player-sign-in";
const noop = async () => undefined;

function phone(phase: "scene" | "choices") {
  return createElement(PhoneView, {
    sessionId: "game-uuid-1111",
    displayName: "Jordan",
    participantId: ME,
    getToken,
    joinCode: "K7QP",
    joinUrl: "https://app.test/join?code=K7QP",
    feed: {
      lobby: lobby(),
      round: round({ phase }),
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
}

test("a finding on screen survives a direct phase change on the same page", async () => {
  clearHeldFinding();
  const engine = fakeEngine();
  await withFetch(engine, async () => {
    const page = await mount(phone("choices"));
    await page.clickContaining("Search the desk");
    await page.click("Spend it");
    assert.ok(page.text().includes("A torn page is wedged behind the drawer."));

    // The phase ends with no unmount in between: one rerender swaps the screen.
    await page.rerender(phone("scene"));
    assert.ok(page.text().includes("A torn page is wedged behind the drawer."));
    assert.ok(page.text().includes("Time's up. It's in your notebook."));
    await page.click("OK");
    assert.ok(page.text().includes("Eyes on the TV."));
    await page.unmount();
  });
});

test("a 503 from a proxy keeps the choice ID, so the retry is one effect", async () => {
  const engine = fakeEngine({ budget: 4 });
  await withFetch(engine, async () => {
    const page = await mount(
      createElement(InvestigatePhone, {
        sessionId: "game-uuid-1111",
        lobby: lobby(),
        round: round({ phase: "choices" }),
        seat: { participantId: ME, displayName: "Jordan" },
        getToken,
      }),
    );
    await page.clickContaining("Search the desk");
    engine.unavailableNextChoice = true;
    await page.click("Spend it");
    assert.ok(page.text().includes("That did not work. Try again."));
    await page.click("Spend it");
    const sends = engine.calls.filter((c) => c.path.endsWith("/me/choices"));
    assert.equal(sends.length, 2);
    assert.equal(sends[0].body?.choice_id, sends[1].body?.choice_id);
    assert.equal(engine.effects.length, 1);
    await page.unmount();
  });
});

test("a failed first menu read loads by itself without a remount", async () => {
  const engine = fakeEngine();
  engine.dropNextMenu = true;
  await withFetch(engine, async () => {
    const page = await mount(
      createElement(InvestigatePhone, {
        sessionId: "game-uuid-1111",
        lobby: lobby(),
        round: round({ phase: "choices" }),
        seat: { participantId: ME, displayName: "Jordan" },
        getToken,
      }),
    );
    assert.ok(page.text().includes("That did not work. Try again."));
    await new Promise((resolve) => setTimeout(resolve, MENU_RETRY_MS + 300));
    await mount(createElement("div")); // lets pending updates flush
    assert.ok(page.text().includes("Look into:"));
    assert.ok(!page.text().includes("That did not work."));
    await page.unmount();
  });
});
