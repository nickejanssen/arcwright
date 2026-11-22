// AW-359: four problems an independent review found in AW-332 part A, each shown
// here failing on the merged code and passing after the fix.

import assert from "node:assert/strict";
import test from "node:test";

import { StrictMode, createElement } from "react";
import EyesUpPhone from "../src/screens/round/EyesUpPhone.js";
import InvestigatePhone, {
  clearHeldFinding,
} from "../src/screens/round/InvestigatePhone.js";
import { mount, settle } from "./helpers/dom.js";
import {
  ITEMS,
  ME,
  fakeEngine,
  lobby,
  round,
  withFetch,
} from "./helpers/round-fixtures.js";
import type { FixtureItem } from "./helpers/round-fixtures.js";

const getToken = async () => "player-sign-in";

function slot(phase: string, sessionId = "game-uuid-1111") {
  return {
    sessionId,
    lobby: lobby(),
    round: round({ phase }),
    seat: { participantId: ME, displayName: "Jordan" },
    getToken,
  };
}

test("a held finding never hides Ready, and it goes when its hold is over", async () => {
  clearHeldFinding();
  const engine = fakeEngine();
  await withFetch(engine, async () => {
    const investigate = await mount(
      createElement(InvestigatePhone, slot("choices")),
    );
    await investigate.clickContaining("Search the desk");
    await investigate.click("Spend it");
    await investigate.unmount();

    const eyes = await mount(createElement(EyesUpPhone, slot("scene")));
    assert.ok(eyes.text().includes("A torn page is wedged behind the drawer."));
    assert.ok(
      eyes.buttons().some((b) => b.textContent?.trim() === "I'm ready"),
      "Ready is shown beside the held finding",
    );

    // Left alone past the hold: the next render no longer shows the finding.
    const realNow = Date.now;
    Date.now = () => realNow() + 31_000;
    try {
      await eyes.rerender(createElement(EyesUpPhone, slot("scene")));
    } finally {
      Date.now = realNow;
    }
    assert.ok(!eyes.text().includes("A torn page"));
    assert.ok(eyes.text().includes("Eyes on the TV."));
    await eyes.unmount();
  });
});

test("an older menu reply cannot replace a newer budget", async () => {
  clearHeldFinding();
  const engine = fakeEngine({ budget: 4 });
  await withFetch(engine, async () => {
    const page = await mount(createElement(InvestigatePhone, slot("choices")));
    let release: () => void = () => undefined;
    // The read made after the first choice is slow; it carries budget 3.
    engine.menuGates.push(
      new Promise<void>((resolve) => {
        release = resolve;
      }),
    );
    await page.clickContaining("Search the desk");
    await page.click("Spend it");
    await page.click("Back to the list");
    await page.clickContaining("Ask about the evening");
    await page.click("Spend it");
    assert.ok(page.text().includes("2 left"), "the newer budget is shown");

    release(); // the slow, older read lands last
    await settle();
    assert.ok(
      page.text().includes("2 left"),
      "the older reply did not put 3 back",
    );
    assert.ok(!page.text().includes("3 left"));
    await page.unmount();
  });
});

test("a choice refused after the screen is gone starts no request", async () => {
  clearHeldFinding();
  const engine = fakeEngine();
  await withFetch(engine, async () => {
    const page = await mount(createElement(InvestigatePhone, slot("choices")));
    await page.clickContaining("Search the desk");
    let release: () => void = () => undefined;
    engine.refuseNextChoice = true;
    engine.holdNextChoice = new Promise<void>((resolve) => {
      release = resolve;
    });
    await page.click("Spend it");
    await page.unmount(); // thinking time ends while the choice is in flight
    const reads = engine.calls.filter((c) =>
      c.path.endsWith("/me/menu"),
    ).length;
    release();
    await settle();
    assert.equal(
      engine.calls.filter((c) => c.path.endsWith("/me/menu")).length,
      reads,
      "no menu read after the screen is gone",
    );
  });
});

test("a menu in the order A, B, A is shown as A, B, A", async () => {
  clearHeldFinding();
  const [a1, , b, c] = ITEMS;
  const aAgain: FixtureItem = {
    ...ITEMS[1],
    opportunity_id: "opp_internal_9",
    label: "Ask about the garden",
    taken: false,
  };
  const items = [a1, b, aAgain, c];
  const engine = fakeEngine({ items });
  await withFetch(engine, async () => {
    const page = await mount(createElement(InvestigatePhone, slot("choices")));
    const text = page.text();
    const order = [
      "Ask about the evening",
      "Search the desk",
      "Ask about the garden",
      "Read the last page",
    ].map((label) => text.indexOf(label));
    assert.ok(
      order.every((n) => n >= 0),
      "every item is shown",
    );
    assert.deepEqual(
      [...order].sort((x, y) => x - y),
      order,
      "items appear in the engine's order",
    );
    assert.equal(
      text.split("The Butler").length - 1,
      2,
      "the Butler heads two separate groups",
    );
    await page.unmount();
  });
});

test("the held finding survives React StrictMode, which the dev server uses", async () => {
  clearHeldFinding();
  const engine = fakeEngine();
  await withFetch(engine, async () => {
    const investigate = await mount(
      createElement(InvestigatePhone, slot("choices")),
    );
    await investigate.clickContaining("Search the desk");
    await investigate.click("Spend it");
    await investigate.unmount();

    const eyes = await mount(
      createElement(
        StrictMode,
        null,
        createElement(EyesUpPhone, slot("scene")),
      ),
    );
    assert.ok(eyes.text().includes("A torn page is wedged behind the drawer."));
    await eyes.rerender(
      createElement(
        StrictMode,
        null,
        createElement(EyesUpPhone, slot("scene")),
      ),
    );
    assert.ok(
      eyes.text().includes("A torn page is wedged behind the drawer."),
      "still shown after a later render",
    );
    assert.ok(eyes.buttons().some((b) => b.textContent?.trim() === "OK"));
    await eyes.unmount();
  });
});
