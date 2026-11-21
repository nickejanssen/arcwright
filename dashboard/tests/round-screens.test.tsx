// Screens 4 to 9 (AW-332, pull request A) from fixture data: the key words
// show, each screen is chosen by the phase table, and the round route the feed
// reads is the room view. Screens 10 to 12 are the next pull request.

import assert from "node:assert/strict";
import test from "node:test";

import { createElement } from "react";
import { fetchRound } from "../src/api/round.js";
import { TvView } from "../src/screens/DisplayScreen.js";
import EyesUpPhone from "../src/screens/round/EyesUpPhone.js";
import InvestigatePhone from "../src/screens/round/InvestigatePhone.js";
import StoryTv from "../src/screens/round/StoryTv.js";
import ThinkingTv from "../src/screens/round/ThinkingTv.js";
import { scheduleLines } from "../src/screens/round/staging.js";
import { PhoneView } from "../src/screens/WaitingScreen.js";
import { DEFAULT_SLOTS, resolveScreen } from "../src/shell/phaseScreens.js";
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
const seat = { participantId: ME, displayName: "Jordan" };

function slotProps(over: Record<string, unknown> = {}) {
  return {
    sessionId: "game-uuid-1111",
    lobby: lobby(),
    round: round(),
    seat,
    getToken,
    ...over,
  };
}

function reduceMotion(on: boolean) {
  document.documentElement.setAttribute(
    "data-reduce-motion",
    on ? "always" : "system",
  );
}

test("the round read is the room view, with the phase entry and who is ready", async () => {
  const seen: string[] = [];
  const answer =
    (body: unknown, status = 200) =>
    async (input: RequestInfo | URL) => {
      seen.push(String(input));
      return new Response(JSON.stringify(body), { status });
    };

  const state = await fetchRound(
    "g1",
    answer({
      session_status: "active",
      round_title: "The Study",
      phase: "choices",
      phase_entry: 9,
      seconds_left: 61.5,
      paused: false,
      lines: [],
      players: [
        {
          participant_id: "p1",
          display_name: "Jordan",
          ready: true,
          locked: false,
        },
        {
          participant_id: "p2",
          display_name: null,
          ready: false,
          locked: false,
        },
      ],
      ready_count: 1,
      player_count: 2,
      over: false,
    }) as typeof fetch,
  );
  assert.deepEqual(seen, ["/v1/sessions/g1/room"]);
  assert.equal(state?.beatName, "The Study");
  assert.equal(state?.phase, "choices");
  assert.equal(state?.phaseEntry, 9);
  assert.equal(state?.status, "running");
  assert.equal(state?.secondsLeft, 61.5);
  assert.deepEqual(
    state?.players.map((p) => [p.participantId, p.name, p.ready]),
    [
      ["p1", "Jordan", true],
      ["p2", null, false],
    ],
  );

  const paused = await fetchRound(
    "g1",
    answer({
      session_status: "active",
      paused: true,
      players: [],
      over: false,
    }) as typeof fetch,
  );
  assert.equal(paused?.status, "paused");
  const over = await fetchRound(
    "g1",
    answer({
      session_status: "completed",
      paused: false,
      players: [],
      over: true,
    }) as typeof fetch,
  );
  assert.equal(over?.status, "ended");
  const none = await fetchRound("g1", answer({}, 404) as typeof fetch);
  assert.equal(none, null);
});

test("the phase table names the story, thinking time, eyes up and investigate screens", () => {
  const l = lobby();
  for (const phase of ["scene", "bridge", "choices"]) {
    const r = round({ phase });
    assert.equal(
      resolveScreen("tv", l, r, DEFAULT_SLOTS).kind,
      "phase",
      `tv ${phase}`,
    );
    assert.equal(
      resolveScreen("phone", l, r, DEFAULT_SLOTS).kind,
      "phase",
      `phone ${phase}`,
    );
  }
  const scene = round({ phase: "scene" });
  const choices = round({ phase: "choices" });
  const tvScene = resolveScreen("tv", l, scene, DEFAULT_SLOTS);
  const tvBridge = resolveScreen(
    "tv",
    l,
    round({ phase: "bridge" }),
    DEFAULT_SLOTS,
  );
  assert.ok(tvScene.kind === "phase" && tvBridge.kind === "phase");
  assert.equal(tvScene.kind === "phase" && tvScene.Slot, StoryTv);
  assert.equal(tvBridge.kind === "phase" && tvBridge.Slot, StoryTv);
  const phoneScene = resolveScreen("phone", l, scene, DEFAULT_SLOTS);
  const tvChoices = resolveScreen("tv", l, choices, DEFAULT_SLOTS);
  const phoneChoices = resolveScreen("phone", l, choices, DEFAULT_SLOTS);
  assert.equal(phoneScene.kind === "phase" && phoneScene.Slot, EyesUpPhone);
  assert.equal(tvChoices.kind === "phase" && tvChoices.Slot, ThinkingTv);
  assert.equal(
    phoneChoices.kind === "phase" && phoneChoices.Slot,
    InvestigatePhone,
  );

  // The mini-game screens are the next pull request, and Last Call is AW-333.
  for (const phase of ["mini_game", "commit"]) {
    const r = round({ phase });
    assert.equal(
      resolveScreen("tv", l, r, DEFAULT_SLOTS).kind,
      "fallback",
      phase,
    );
    assert.equal(
      resolveScreen("phone", l, r, DEFAULT_SLOTS).kind,
      "fallback",
      phase,
    );
  }
});

test("screen 4, the TV story: title, speaker and line, clock, and who is ready by word and mark", async () => {
  reduceMotion(true);
  const lines = [
    {
      text: "Welcome to the house.",
      speaker: "Host",
      hints: { pause_before_ms: 0 },
    },
    {
      text: "Nobody leaves tonight.",
      speaker: null,
      hints: { pause_before_ms: 3000 },
    },
  ];
  const page = await mount(
    createElement(StoryTv, {
      sessionId: "g",
      lobby: lobby(),
      round: round({ lines }),
    }),
  );
  const text = page.text();
  assert.ok(text.includes("A Quiet Evening"));
  assert.ok(text.includes("Host:"), "the speaker's name before a spoken line");
  assert.ok(text.includes("Welcome to the house."));
  assert.ok(
    text.includes("Nobody leaves tonight."),
    "reduced motion shows every line at once",
  );
  assert.ok(text.includes("1:42"), "the clock is the route's seconds");
  assert.ok(text.includes("Ready:"));
  assert.ok(
    /Avery\s*ready/.test(text.replace(/[^\w\s]/g, "")),
    "a ready player has the word ready",
  );
  assert.ok(
    text.includes("not yet"),
    "a player not ready has the words not yet",
  );
  assert.ok(text.includes("Guest"), "an unnamed player is not shown as an ID");
  assert.equal(page.buttons().length, 0, "the TV has no controls");
  await page.unmount();
  reduceMotion(false);
});

test("screen 4 shows the first line at once and holds the next until its authored pause (floor 2 s)", async () => {
  reduceMotion(false);
  const lines = [
    { text: "First line.", speaker: null, hints: { pause_before_ms: 0 } },
    { text: "Second line.", speaker: null, hints: { pause_before_ms: 500 } },
  ];
  const page = await mount(
    createElement(StoryTv, {
      sessionId: "g",
      lobby: lobby(),
      round: round({ lines }),
    }),
  );
  assert.ok(page.text().includes("First line."));
  assert.ok(!page.text().includes("Second line."), "the second line waits");
  await page.unmount();

  assert.deepEqual(
    scheduleLines(
      [
        { text: "a", speaker: null, pauseBeforeMs: 0 },
        { text: "b", speaker: null, pauseBeforeMs: 500 },
        { text: "c", speaker: null, pauseBeforeMs: 4000 },
      ],
      2000,
    ),
    [0, 2000, 6000],
    "authored pause, with a floor between lines",
  );
});

test("screen 5, phone eyes up: name, round, clock, ready button, and the opening held under Who you are", async () => {
  const engine = fakeEngine();
  await withFetch(engine, async () => {
    const page = await mount(createElement(EyesUpPhone, slotProps()));
    const text = page.text();
    assert.ok(text.includes("Jordan"));
    assert.ok(text.includes("A Quiet Evening"));
    assert.ok(text.includes("1:42"));
    assert.ok(text.includes("Eyes on the TV."));
    assert.ok(text.includes("Who you are"));
    assert.ok(
      text.includes("You are the host's old friend"),
      "the opening is on the page, collapsed",
    );
    assert.ok(
      page.container.querySelector("details:not([open])"),
      "collapsed to start",
    );
    assert.ok(
      text.includes("Now") && text.includes("Notebook"),
      "the two tabs",
    );

    await page.click("I'm ready");
    const ready = engine.calls.find((c) => c.path.endsWith("/me/ready"));
    assert.equal(
      ready?.body?.phase_entry,
      7,
      "ready names the phase entry the room view gave",
    );
    assert.equal(ready?.authorization, "Bearer player-sign-in");
    assert.ok(page.text().includes("Ready. Waiting for the others."));
    assert.ok(
      !page.buttons().some((b) => b.textContent?.trim() === "I'm ready"),
      "the button is replaced",
    );
    await page.unmount();
  });
});

test("screen 5: a player the room view shows as ready keeps that after a reload, and a moved-on phase is not marked", async () => {
  const engine = fakeEngine();
  await withFetch(engine, async () => {
    const already = round({
      players: [{ participantId: ME, name: "Jordan", ready: true }],
    });
    const page = await mount(
      createElement(EyesUpPhone, slotProps({ round: already })),
    );
    assert.ok(page.text().includes("Ready. Waiting for the others."));
    await page.unmount();

    engine.entryNow = 8; // the round moved on since this phone looked
    const stale = await mount(createElement(EyesUpPhone, slotProps()));
    await stale.click("I'm ready");
    assert.ok(
      !stale.text().includes("Ready. Waiting for the others."),
      "the engine changed nothing, so the phone does not claim ready",
    );
    await stale.unmount();
  });
});

test("screen 5: when the engine refuses ready the phone says so in the approved words", async () => {
  const failing = (async () =>
    new Response("{}", { status: 409 })) as typeof fetch;
  const globals = globalThis as Record<string, unknown>;
  const real = globals.fetch;
  globals.fetch = failing;
  try {
    const page = await mount(createElement(EyesUpPhone, slotProps()));
    await page.click("I'm ready");
    assert.ok(page.text().includes("That did not work. Try again."));
    await page.unmount();
  } finally {
    globals.fetch = real;
  }
});

test("screen 6, the TV thinking time: title, line, clock and ready list", async () => {
  const page = await mount(
    createElement(ThinkingTv, {
      sessionId: "g",
      lobby: lobby(),
      round: round({ phase: "choices" }),
    }),
  );
  const text = page.text();
  assert.ok(text.includes("A Quiet Evening"));
  assert.ok(text.includes("Investigate on your phones."));
  assert.ok(text.includes("1:42"));
  assert.ok(text.includes("Ready:"));
  assert.ok(text.includes("Avery") && text.includes("Jordan"));
  await page.unmount();
});

test("screens 7 and 8, the investigate menu and a finding", async () => {
  const engine = fakeEngine();
  await withFetch(engine, async () => {
    const page = await mount(
      createElement(
        InvestigatePhone,
        slotProps({ round: round({ phase: "choices" }) }),
      ),
    );
    const text = page.text();
    assert.ok(text.includes("Look into:"));
    assert.ok(text.includes("4 left"));
    for (const word of [
      "The Butler",
      "Ask about the evening",
      "The Study",
      "Search the desk",
      "The Ledger",
    ]) {
      assert.ok(text.includes(word), word);
    }
    assert.ok(
      text.includes("Person") &&
        text.includes("Place") &&
        text.includes("Record"),
    );
    assert.ok(text.includes("new") && text.includes("seen"));
    assert.ok(
      page.buttons().some((b) => b.textContent?.trim() === "I'm ready"),
    );

    // A new item confirms with the route's numbers, then shows the finding.
    await page.clickContaining("Search the desk");
    assert.ok(page.text().includes("Spend 1 of your 4?"));
    await page.click("Not now");
    assert.ok(
      page.text().includes("Look into:"),
      "Not now goes back to the list",
    );
    await page.clickContaining("Search the desk");
    await page.click("Spend it");
    assert.ok(page.text().includes("A torn page is wedged behind the drawer."));
    assert.ok(page.text().includes("Saved to your notebook."));
    assert.ok(
      page.text().includes("The Study"),
      "the subject label heads the finding",
    );
    await page.click("Back to the list");
    assert.ok(page.text().includes("Look into:"));
    await page.unmount();
  });
});

test("screen 7: a closed menu and a refused choice use the approved sentences", async () => {
  const engine = fakeEngine();
  engine.open = false;
  await withFetch(engine, async () => {
    const closed = await mount(
      createElement(
        InvestigatePhone,
        slotProps({ round: round({ phase: "choices" }) }),
      ),
    );
    assert.ok(closed.text().includes("Time's up. It's in your notebook."));
    assert.ok(!closed.text().includes("Look into:"));
    await closed.unmount();

    engine.open = true;
    engine.refuseNextChoice = true;
    const page = await mount(
      createElement(
        InvestigatePhone,
        slotProps({ round: round({ phase: "choices" }) }),
      ),
    );
    await page.clickContaining("Search the desk");
    await page.click("Spend it");
    assert.ok(page.text().includes("That did not work. Try again."));
    await page.unmount();
  });
});

test("the phone page hands the slot its seat and sign-in, and the TV page hands it none", async () => {
  const engine = fakeEngine();
  await withFetch(engine, async () => {
    const noop = async () => undefined;
    const phone = await mount(
      createElement(PhoneView, {
        sessionId: "game-uuid-1111",
        displayName: "Jordan",
        participantId: ME,
        getToken,
        joinCode: "K7QP",
        joinUrl: "https://app.test/join?code=K7QP",
        feed: {
          lobby: lobby(),
          round: round({ phase: "scene" }),
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
      }),
    );
    assert.ok(phone.text().includes("Eyes on the TV."));
    assert.ok(phone.text().includes("Jordan"));
    await phone.click("I'm ready");
    assert.equal(engine.readyEntries.length, 1);
    await phone.unmount();

    const calls = engine.calls.length;
    const tv = await mount(
      createElement(TvView, {
        sessionId: "game-uuid-1111",
        feed: {
          lobby: lobby(),
          round: round({ phase: "choices" }),
          unreachable: false,
          gone: false,
        },
        joinBaseUrl: "https://app.test",
      }),
    );
    assert.ok(tv.text().includes("Investigate on your phones."));
    assert.equal(engine.calls.length, calls, "the TV called no route");
    await tv.unmount();
  });
});

test("a finding on screen when thinking time ends stays, with the time's-up words, on the next eyes-up screen", async () => {
  const engine = fakeEngine();
  await withFetch(engine, async () => {
    const investigate = await mount(
      createElement(
        InvestigatePhone,
        slotProps({ round: round({ phase: "choices" }) }),
      ),
    );
    await investigate.clickContaining("Search the desk");
    await investigate.click("Spend it");
    assert.ok(
      investigate.text().includes("A torn page is wedged behind the drawer."),
    );
    // The phase ends: the phone's screen is replaced by the next phase's.
    await investigate.unmount();

    const eyes = await mount(createElement(EyesUpPhone, slotProps()));
    assert.ok(eyes.text().includes("A torn page is wedged behind the drawer."));
    assert.ok(eyes.text().includes("Time's up. It's in your notebook."));
    await eyes.click("OK");
    assert.ok(eyes.text().includes("Eyes on the TV."));
    assert.ok(!eyes.text().includes("A torn page"));
    await eyes.unmount();

    // It is shown once: a later eyes-up screen starts clean.
    const later = await mount(createElement(EyesUpPhone, slotProps()));
    assert.ok(!later.text().includes("A torn page"));
    await later.unmount();
  });
});
