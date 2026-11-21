// AW-332 criterion 3: the phone's investigations-left number equals the
// route's number at every step. A fake route does its own sums; the screen
// must print exactly what the route last said, and keep the order it gave.

import assert from "node:assert/strict";
import test from "node:test";

import { createElement } from "react";
import InvestigatePhone from "../src/screens/round/InvestigatePhone.js";
import { mount } from "./helpers/dom.js";
import type { Mounted } from "./helpers/dom.js";
import {
  ITEMS,
  ME,
  fakeEngine,
  lobby,
  round,
  withFetch,
} from "./helpers/round-fixtures.js";
import type { FakeEngine } from "./helpers/round-fixtures.js";

function screen() {
  return createElement(InvestigatePhone, {
    sessionId: "game-uuid-1111",
    lobby: lobby(),
    round: round({ phase: "choices" }),
    seat: { participantId: ME, displayName: "Jordan" },
    getToken: async () => "player-sign-in",
  });
}

// The number in the header, read from the page.
function shown(page: Mounted): number {
  const found = /(\d+) left/.exec(page.text());
  assert.ok(found, "the header shows an investigations-left number");
  return Number(found[1]);
}

function assertMatches(page: Mounted, engine: FakeEngine, step: string) {
  assert.equal(shown(page), engine.budget, `header number at: ${step}`);
}

test("the header number equals the route's number at every step", async () => {
  const engine = fakeEngine({ budget: 3 });
  await withFetch(engine, async () => {
    const page = await mount(screen());
    assertMatches(page, engine, "menu open");

    await page.clickContaining("Ask about the evening");
    assertMatches(page, engine, "confirm open");
    assert.ok(page.text().includes("Spend 1 of your 3?"));

    await page.click("Spend it");
    assert.equal(engine.budget, 2, "the route spent one");
    assertMatches(
      page,
      engine,
      "finding shown (after the reply and the reread)",
    );

    await page.click("Back to the list");
    assertMatches(page, engine, "back on the list");

    // Reading a seen item again: no confirm, nothing spent, number unchanged.
    await page.clickContaining("Ask about the keys");
    assert.ok(!page.text().includes("Spend "), "a seen item has no confirm");
    assertMatches(page, engine, "seen item reread");
    await page.click("Back to the list");

    // The route's number changes outside the screen (a reward in a mini-game).
    engine.budget = 7;
    await page.clickContaining("Search the desk");
    await page.click("Not now");
    await page.clickContaining("Search the desk");
    await page.click("Spend it");
    assert.equal(engine.budget, 6);
    assertMatches(page, engine, "after a number the screen did not compute");

    // Down to none.
    engine.budget = 1;
    await page.click("Back to the list");
    await page.clickContaining("Read the last page"); // cost 2, one left
    await page.click("Spend it");
    // The route refused (it cannot be afforded); the number is still its own.
    assert.ok(page.text().includes("That did not work. Try again."));
    assertMatches(page, engine, "refused choice");
    await page.unmount();
  });
});

test("with none left the screen says so, still opens a seen item, and the engine judges the rest", async () => {
  const engine = fakeEngine({ budget: 0 });
  await withFetch(engine, async () => {
    const page = await mount(screen());
    assert.equal(shown(page), 0);
    assert.ok(
      page.text().includes("No investigations left. You can still reread."),
    );

    await page.clickContaining("Ask about the keys");
    assert.ok(
      page.text().includes("He keeps the spare keys on a hook by the door."),
    );
    assertMatches(page, engine, "reread with none left");
    await page.click("Back to the list");

    // The screen does not decide a new item cannot be afforded: it asks, and
    // the engine says no.
    await page.clickContaining("Search the desk");
    assert.ok(page.text().includes("Spend 1 of your 0?"));
    await page.click("Spend it");
    assert.ok(page.text().includes("That did not work. Try again."));
    assert.equal(
      engine.effects.length,
      1,
      "only the seen reread had an effect",
    );
    await page.unmount();
  });
});

test("menu items appear in the order the route gave, grouped by subject, in two different orders", async () => {
  const orders = [ITEMS, [ITEMS[3], ITEMS[2], ITEMS[1], ITEMS[0]]];
  for (const items of orders) {
    const engine = fakeEngine({ items });
    await withFetch(engine, async () => {
      const page = await mount(screen());
      const text = page.text();
      const labels = items.map((i) => i.label);
      const positions = labels.map((l) => text.indexOf(l));
      assert.ok(
        positions.every((p) => p >= 0),
        "every item is shown",
      );

      // Subjects appear in the order of their first item; items keep their order.
      const subjectOrder: string[] = [];
      for (const item of items) {
        if (!subjectOrder.includes(item.subject_label))
          subjectOrder.push(item.subject_label);
      }
      const subjectPositions = subjectOrder.map((s) => text.indexOf(s));
      assert.deepEqual(
        subjectPositions,
        [...subjectPositions].sort((a, b) => a - b),
        "subjects keep the route's order",
      );
      const sameSubject = items.filter(
        (i) => i.subject_id === "subj_internal_A",
      );
      const aPositions = sameSubject.map((i) => text.indexOf(i.label));
      assert.deepEqual(
        aPositions,
        [...aPositions].sort((a, b) => a - b),
      );
      await page.unmount();
    });
  }
});
