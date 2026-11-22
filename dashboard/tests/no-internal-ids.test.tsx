// Spec 0095 Part L: no rendered screen contains an internal ID. Every screen of
// pull request A is rendered with a fixture whose routes carry IDs (opportunity,
// subject, concept, participant); the text and the markup are searched.

import assert from "node:assert/strict";
import test from "node:test";

import { createElement } from "react";
import type { ReactElement } from "react";
import Notebook from "../src/screens/notebook/Notebook.js";
import EyesUpPhone from "../src/screens/round/EyesUpPhone.js";
import InvestigatePhone from "../src/screens/round/InvestigatePhone.js";
import MiniGamePhone from "../src/screens/round/MiniGamePhone.js";
import MiniGameTv from "../src/screens/round/MiniGameTv.js";
import RewardCard from "../src/screens/round/RewardCard.js";
import StoryTv from "../src/screens/round/StoryTv.js";
import ThinkingTv from "../src/screens/round/ThinkingTv.js";
import { mount, settle } from "./helpers/dom.js";
import {
  INTERNAL_IDS,
  ME,
  fakeEngine,
  lobby,
  round,
  withFetch,
} from "./helpers/round-fixtures.js";
import type { Mounted } from "./helpers/dom.js";
import { fixtureServices } from "./helpers/mini-game-fixture.js";

const base = {
  sessionId: "game-uuid-1111",
  lobby: lobby(),
  seat: { participantId: ME, displayName: "Jordan" },
  getToken: async () => "player-sign-in",
};

function assertClean(page: Mounted, where: string) {
  const text = page.text();
  const html = page.container.innerHTML;
  for (const id of INTERNAL_IDS) {
    assert.ok(!text.includes(id), `${where}: text shows ${id}`);
    assert.ok(!html.includes(id), `${where}: markup holds ${id}`);
  }
  for (const phase of ["scene", "choices", "mini_game", "bridge", "commit"]) {
    assert.ok(!text.includes(phase), `${where}: shows the phase name ${phase}`);
  }
}

async function look(element: ReactElement, where: string) {
  const page = await mount(element);
  assertClean(page, where);
  return page;
}

test("no internal ID on any round screen", async () => {
  document.documentElement.setAttribute("data-reduce-motion", "always");
  const engine = fakeEngine();
  await withFetch(engine, async () => {
    const lines = [
      { text: "A line.", speaker: "Host", hints: { pause_before_ms: 0 } },
    ];

    const story = await look(
      createElement(StoryTv, {
        sessionId: "g",
        lobby: lobby(),
        round: round({ lines }),
      }),
      "screen 4",
    );
    await story.unmount();

    const thinking = await look(
      createElement(ThinkingTv, {
        sessionId: "g",
        lobby: lobby(),
        round: round({ phase: "choices" }),
      }),
      "screen 6",
    );
    await thinking.unmount();

    const eyes = await look(
      createElement(EyesUpPhone, { ...base, round: round() }),
      "screen 5",
    );
    await eyes.click("Notebook");
    assertClean(eyes, "screen 5, notebook tab");
    await eyes.unmount();

    const invest = await look(
      createElement(InvestigatePhone, {
        ...base,
        round: round({ phase: "choices" }),
      }),
      "screen 7",
    );
    await invest.clickContaining("Ask about the evening");
    assertClean(invest, "screen 7, confirm");
    await invest.click("Spend it");
    assertClean(invest, "screen 8, finding");
    await invest.click("Notebook");
    assertClean(invest, "screen 9, notebook after a find");
    await invest.unmount();

    const notebook = await look(
      createElement(Notebook, { sessionId: "g", getToken: base.getToken }),
      "screen 9",
    );
    await notebook.unmount();

    const tvGame = await look(
      createElement(MiniGameTv, {
        sessionId: "game-uuid-1111",
        lobby: lobby(),
        round: round({ phase: "mini_game", phaseEntry: 12 }),
        stageServices: fixtureServices(),
      }),
      "screen 10",
    );
    await settle();
    assertClean(tvGame, "screen 10 after package mount");
    await tvGame.unmount();

    const phoneGame = await look(
      createElement(MiniGamePhone, {
        ...base,
        seat: {
          participantId: ME,
          characterId: "character-internal",
          displayName: "Jordan",
        },
        round: round({ phase: "mini_game", phaseEntry: 12 }),
        stageServices: fixtureServices(),
      }),
      "screen 11",
    );
    await settle();
    assertClean(phoneGame, "screen 11 after package mount");
    await phoneGame.unmount();

    engine.rewards = [
      {
        grant_id: "grant_internal_1",
        run_id: "run_internal_1",
        beat_id: "beat_internal_1",
        amount: 1,
        kind: "investigation",
      },
    ];
    const reward = await look(
      createElement(
        RewardCard,
        {
          sessionId: "game-uuid-1111",
          getToken: base.getToken,
          round: round({ phase: "bridge", phaseEntry: 14 }),
        },
        createElement("p", null, "Screen underneath"),
      ),
      "screen 12",
    );
    await settle();
    assertClean(reward, "screen 12 after menu read");
    await reward.unmount();
  });
  document.documentElement.setAttribute("data-reduce-motion", "system");
});
