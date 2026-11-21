// Recovery cases for the investigate screen found in review of AW-332 part A:
// a finding survives a direct phase change, a 5xx keeps the same choice ID, and
// a failed first menu read loads by itself.

import assert from "node:assert/strict";
import test from "node:test";

import { createElement } from "react";
import EyesUpPhone from "../src/screens/round/EyesUpPhone.js";
import InvestigatePhone, {
  MENU_RETRY_MS,
  clearHeldFinding,
} from "../src/screens/round/InvestigatePhone.js";
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
  engine.dropMenus = 1;
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

test("the menu retry keeps going through several failures, stacks no timers, then recovers", async () => {
  const engine = fakeEngine();
  engine.dropMenus = 2;
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
    await new Promise((resolve) =>
      setTimeout(resolve, MENU_RETRY_MS * 2 + 400),
    );
    await settle();
    assert.ok(page.text().includes("Look into:"), "loaded after two failures");
    const reads = engine.calls.filter((c) => c.path.endsWith("/me/menu"));
    assert.equal(reads.length, 3, "one read at open, one per retry, no more");
    await page.unmount();
    const after = engine.calls.length;
    await new Promise((resolve) => setTimeout(resolve, MENU_RETRY_MS + 300));
    assert.equal(engine.calls.length, after, "no read after unmount");
  });
});

test("a reply that lands after the screen is gone holds nothing", async () => {
  clearHeldFinding();
  const engine = fakeEngine();
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
    let release: () => void = () => undefined;
    engine.holdNextChoice = new Promise<void>((resolve) => {
      release = resolve;
    });
    await page.click("Spend it");
    await page.unmount(); // thinking time ends before the reply arrives
    release();
    await settle();

    const later = await mount(
      createElement(EyesUpPhone, {
        sessionId: "game-uuid-1111",
        lobby: lobby(),
        round: round({ phase: "bridge" }),
        seat: { participantId: ME, displayName: "Jordan" },
        getToken,
      }),
    );
    assert.ok(later.text().includes("Eyes on the TV."));
    assert.ok(!later.text().includes("A torn page"));
    assert.ok(
      later.buttons().some((b) => b.textContent?.trim() === "I'm ready"),
    );
    await later.unmount();
  });
});

test("a held finding does not carry into another game in the same tab", async () => {
  clearHeldFinding();
  const engine = fakeEngine();
  await withFetch(engine, async () => {
    const page = await mount(
      createElement(InvestigatePhone, {
        sessionId: "game-A",
        lobby: lobby(),
        round: round({ phase: "choices" }),
        seat: { participantId: ME, displayName: "Jordan" },
        getToken,
      }),
    );
    await page.clickContaining("Search the desk");
    await page.click("Spend it");
    await page.unmount();

    const other = await mount(
      createElement(EyesUpPhone, {
        sessionId: "game-B",
        lobby: lobby(),
        round: round({ phase: "scene" }),
        seat: { participantId: ME, displayName: "Jordan" },
        getToken,
      }),
    );
    assert.ok(other.text().includes("Eyes on the TV."));
    assert.ok(!other.text().includes("A torn page"));
    await other.unmount();
  });
});
