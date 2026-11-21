// D-134, AW-332 criterion 2: the TV in thinking time shows only the round
// title, a clock and the ready list. Marker words sit in the fixture's lines,
// menu and holdings; none may reach the TV, and the TV must call no route.

import assert from "node:assert/strict";
import test from "node:test";

import { createElement } from "react";
import { TvView } from "../src/screens/DisplayScreen.js";
import ThinkingTv from "../src/screens/round/ThinkingTv.js";
import { mount } from "./helpers/dom.js";
import {
  ITEMS,
  OPENING,
  fakeEngine,
  lobby,
  round,
  withFetch,
} from "./helpers/round-fixtures.js";

test("the TV in thinking time shows the title, the clock and who is ready, and nothing else", async () => {
  const engine = fakeEngine();
  await withFetch(engine, async () => {
    const withMarkers = round({
      phase: "choices",
      lines: [
        {
          text: "MARKER-LINE the butler did it",
          speaker: "MARKER-SPEAKER",
          hints: {},
        },
      ],
    });
    const page = await mount(
      createElement(TvView, {
        sessionId: "game-uuid-1111",
        feed: {
          lobby: lobby(),
          round: withMarkers,
          unreachable: false,
          gone: false,
        },
        joinBaseUrl: "https://app.test",
      }),
    );
    const text = page.text();

    assert.ok(text.includes("A Quiet Evening"), "the round title");
    assert.ok(text.includes("1:42"), "the clock");
    assert.ok(text.includes("Ready:"), "the ready list");
    assert.ok(text.includes("Avery") && text.includes("Jordan"));

    // Nothing from a menu, holdings, lines, or anyone's spending.
    for (const item of ITEMS) {
      assert.ok(!text.includes(item.label), `menu item ${item.label}`);
      assert.ok(!text.includes(item.subject_label), item.subject_label);
      assert.ok(!text.includes(item.content), "finding text");
    }
    assert.ok(!text.includes(OPENING.text));
    assert.ok(
      !text.includes("MARKER-LINE"),
      "scene lines are not left on screen",
    );
    assert.ok(!text.includes("MARKER-SPEAKER"));
    assert.ok(!/\bleft\b/.test(text), "no investigations-left count");
    assert.ok(!/\b(spent|found|new|seen)\b/i.test(text));

    assert.equal(page.buttons().length, 0, "no controls");
    assert.equal(
      engine.calls.length,
      0,
      "the TV reads only the room view, which the feed holds",
    );
    await page.unmount();
  });
});

test("the thinking-time TV draws no new text and nothing moves but the clock", async () => {
  const page = await mount(
    createElement(ThinkingTv, {
      sessionId: "g",
      lobby: lobby(),
      round: round({ phase: "choices", secondsLeft: 30 }),
    }),
  );
  const before = page.container.innerHTML;
  assert.ok(!before.includes("animation"));
  assert.equal(
    page.container.querySelectorAll("img, video, audio, canvas, svg").length,
    0,
  );
  await page.unmount();
});
