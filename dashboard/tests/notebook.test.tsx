// Screen 9, the phone notebook: what this player found, grouped by the subject
// it came from in the engine's order, with the round it was found in, and no
// word that ranks or judges an item.

import assert from "node:assert/strict";
import test from "node:test";

import { createElement } from "react";
import Notebook from "../src/screens/notebook/Notebook.js";
import { mount } from "./helpers/dom.js";
import { OPENING, fakeEngine, withFetch } from "./helpers/round-fixtures.js";
import type { FixtureHolding } from "./helpers/round-fixtures.js";

function found(
  id: number,
  label: string,
  from: string,
  roundNumber: number,
  title: string,
): FixtureHolding {
  return {
    concept_id: `concept_internal_${id}`,
    label,
    text: `Text of ${label}.`,
    found_from: from,
    found_in_beat: "beat_internal_1",
    found_in_round_title: title,
    found_in_round_number: roundNumber,
  };
}

function screen() {
  return createElement(Notebook, {
    sessionId: "game-uuid-1111",
    getToken: async () => "player-sign-in",
  });
}

test("groups by subject in the engine's order, with At the start, the round title and number, and a count", async () => {
  const engine = fakeEngine({
    holdings: [
      found(1, "Torn page", "The Study", 2, "Second Course"),
      OPENING,
      found(2, "Spare keys", "The Butler", 1, "First Course"),
      found(3, "Wet footprints", "The Study", 1, "First Course"),
    ],
  });
  await withFetch(engine, async () => {
    const page = await mount(screen());
    const text = page.text();
    assert.ok(text.includes("Notebook"));
    assert.ok(
      text.includes("3 found"),
      "what was found; the opening is not a find",
    );

    // Groups follow the order of their first item in the route's list.
    const study = text.indexOf("The Study");
    const start = text.indexOf("At the start");
    const butler = text.indexOf("The Butler");
    assert.ok(study >= 0 && start >= 0 && butler >= 0);
    assert.ok(
      study < start && start < butler,
      "The Study, At the start, The Butler",
    );

    // Items in a group keep the route's order and carry their round.
    assert.ok(text.indexOf("Torn page") < text.indexOf("Wet footprints"));
    assert.ok(text.includes("Round 2: Second Course"));
    assert.ok(text.includes("Round 1: First Course"));
    assert.ok(text.includes("Your cover story"));
    await page.unmount();
  });
});

test("the same list in a different order is shown in that order", async () => {
  const items = [
    found(1, "Alpha", "Subject One", 1, "T1"),
    found(2, "Beta", "Subject Two", 1, "T1"),
  ];
  for (const holdings of [items, [...items].reverse()]) {
    const engine = fakeEngine({ holdings });
    await withFetch(engine, async () => {
      const page = await mount(screen());
      const text = page.text();
      assert.equal(
        text.indexOf(holdings[0].label) < text.indexOf(holdings[1].label),
        true,
      );
      await page.unmount();
    });
  }
});

test("tapping an item shows its full text and tapping again hides it", async () => {
  const engine = fakeEngine({
    holdings: [found(1, "Torn page", "The Study", 1, "First Course")],
  });
  await withFetch(engine, async () => {
    const page = await mount(screen());
    assert.ok(!page.text().includes("Text of Torn page."));
    await page.clickContaining("Torn page");
    assert.ok(page.text().includes("Text of Torn page."));
    await page.clickContaining("Torn page");
    assert.ok(!page.text().includes("Text of Torn page."));
    await page.unmount();
  });
});

test("an empty notebook says so in the approved words", async () => {
  const engine = fakeEngine({ holdings: [] });
  await withFetch(engine, async () => {
    const page = await mount(screen());
    assert.ok(page.text().includes("Nothing yet. Look into something."));
    assert.ok(!page.text().includes("found"), "no count when nothing is found");
    await page.unmount();
  });
});

test("the notebook never ranks or judges: no supports, contradicts, suspicious or importance words", async () => {
  const engine = fakeEngine({
    holdings: [OPENING, found(1, "Torn page", "The Study", 1, "First Course")],
  });
  await withFetch(engine, async () => {
    const page = await mount(screen());
    await page.clickContaining("Torn page");
    const text = page.text().toLowerCase();
    for (const word of [
      "support",
      "contradict",
      "suspicious",
      "important",
      "key clue",
      "★",
      " rank",
      "guilty",
      "innocent",
    ]) {
      assert.ok(!text.includes(word), word);
    }
    await page.unmount();
  });
});

test("a failed read shows the approved error line, not a blank page", async () => {
  const globals = globalThis as Record<string, unknown>;
  const real = globals.fetch;
  globals.fetch = (async () =>
    new Response("{}", { status: 500 })) as typeof fetch;
  try {
    const page = await mount(screen());
    assert.ok(page.text().includes("That did not work. Try again."));
    await page.unmount();
  } finally {
    globals.fetch = real;
  }
});
