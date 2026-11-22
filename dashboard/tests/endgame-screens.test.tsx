import assert from "node:assert/strict";
import test from "node:test";
import { act, createElement } from "react";
import { TvView } from "../src/screens/DisplayScreen.js";
import { fetchRound } from "../src/api/round.js";
import { mount } from "./helpers/dom.js";
import { lobby, round } from "./helpers/round-fixtures.js";

test("reduced motion shows public accusations together and omits seats with no answer", async () => {
  document.documentElement.setAttribute("data-reduce-motion", "always");
  const state = round({
    phase: "reveal",
    players: [
      { participantId: "a", name: "Alex", ready: false },
      { participantId: "b", name: "Blair", ready: false },
      { participantId: "c", name: "Casey", ready: false },
    ],
    closing: {
      reveal: {
        players: [
          { participant_id: "a", answer: { label: "Answer A" } },
          { participant_id: "b", answer: { label: "Answer B" } },
          { participant_id: "c", answer: null },
        ],
      },
    },
  });
  const page = await mount(
    createElement(TvView, {
      sessionId: "game",
      feed: { lobby: lobby(), round: state, unreachable: false, gone: false },
      joinBaseUrl: "https://app.test",
    }),
  );
  try {
    assert.match(page.text(), /Alex accuses Answer A/);
    assert.match(page.text(), /Blair accuses Answer B/);
    assert.doesNotMatch(page.text(), /Casey/);
    assert.ok(page.container.querySelector('[aria-live="polite"]'));
  } finally {
    await page.unmount();
    document.documentElement.removeAttribute("data-reduce-motion");
  }
});

test("Last Call TV shows the clock without private theory content", async () => {
  const page = await mount(
    createElement(TvView, {
      sessionId: "game-uuid-1111",
      feed: {
        lobby: lobby(),
        round: round({
          phase: "commit",
          lines: [{ text: "PRIVATE THEORY MARKER" }],
          players: [
            {
              participantId: "private-id-1",
              name: "Alex",
              ready: false,
              locked: true,
            },
            {
              participantId: "private-id-2",
              name: "Blair",
              ready: false,
              locked: false,
            },
          ],
        }),
        unreachable: false,
        gone: false,
      },
      joinBaseUrl: "https://app.test",
    }),
  );
  try {
    assert.match(page.text(), /Last Call/i);
    assert.match(page.text(), /1:42/);
    assert.match(page.text(), /Alex\s*Locked/);
    assert.match(page.text(), /Blair\s*Not locked/);
    assert.doesNotMatch(page.text(), /private-id/);
    assert.doesNotMatch(page.text(), /PRIVATE THEORY MARKER/);
  } finally {
    await page.unmount();
  }
});

test("the room read keeps each public locked status", async () => {
  const state = await fetchRound(
    "game",
    async () =>
      new Response(
        JSON.stringify({
          session_status: "active",
          phase: "commit",
          players: [
            {
              participant_id: "a",
              display_name: "Alex",
              ready: false,
              locked: true,
            },
            {
              participant_id: "b",
              display_name: "Blair",
              ready: false,
              locked: false,
            },
          ],
        }),
      ),
  );
  assert.deepEqual(
    state?.players.map((player) => player.locked),
    [true, false],
  );
});

test("the accused TV shows only the public reveal and keeps the room's seat order", async () => {
  const result = {
    reveal: {
      slot_label: "Person",
      players: [
        {
          participant_id: "b",
          answer: { value: "private-id", label: "Public answer B" },
        },
        {
          participant_id: "a",
          answer: { value: "private-id", label: "Public answer A" },
        },
      ],
    },
    result: null,
    recap: null,
  };
  const state = await fetchRound(
    "game",
    async () =>
      new Response(
        JSON.stringify({
          session_status: "active",
          phase: "reveal",
          phase_entry: 2,
          closing: result,
          players: [
            { participant_id: "a", display_name: "Alex", ready: false },
            { participant_id: "b", display_name: "Blair", ready: false },
          ],
        }),
      ),
  );
  assert.ok(state);
  const page = await mount(
    createElement(TvView, {
      sessionId: "game",
      feed: { lobby: lobby(), round: state, unreachable: false, gone: false },
      joinBaseUrl: "https://app.test",
    }),
  );
  try {
    assert.match(page.text(), /The accused/i);
    assert.match(page.text(), /Alex/);
    assert.match(page.text(), /Public answer A/);
    assert.doesNotMatch(page.text(), /Public answer B|private-id/);
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 2100));
    });
    assert.match(page.text(), /Public answer B/);
    assert.doesNotMatch(page.text(), /Public answer A/);
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 2100));
    });
    assert.match(page.text(), /Public answer A/);
    assert.match(page.text(), /Public answer B/);
  } finally {
    await page.unmount();
  }
});
