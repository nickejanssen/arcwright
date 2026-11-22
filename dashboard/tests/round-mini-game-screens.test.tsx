// AW-332 pull request B: the mini-game phase uses the package stage on both
// surfaces, and a finding left open by the choices phase is shown once here.

import assert from "node:assert/strict";
import test from "node:test";
import { act, StrictMode, createElement } from "react";

import MiniGamePhone from "../src/screens/round/MiniGamePhone.js";
import MiniGameTv from "../src/screens/round/MiniGameTv.js";
import InvestigatePhone, {
  clearHeldFinding,
} from "../src/screens/round/InvestigatePhone.js";
import { DEFAULT_SLOTS, resolveScreen } from "../src/shell/phaseScreens.js";
import { mount, settle } from "./helpers/dom.js";
import {
  ME,
  fakeEngine,
  lobby,
  round,
  withFetch,
} from "./helpers/round-fixtures.js";
import { fixtureServices } from "./helpers/mini-game-fixture.js";

const base = {
  sessionId: "game-uuid-1111",
  lobby: lobby(),
  seat: {
    participantId: ME,
    characterId: "character-internal",
    displayName: "Jordan",
  },
  getToken: async () => "player-sign-in",
};

async function leaveDeskFinding(remainingMs?: number) {
  const investigate = await mount(
    createElement(InvestigatePhone, {
      ...base,
      round: round({ phase: "choices" }),
    }),
  );
  await investigate.clickContaining("Search the desk");
  await investigate.click("Spend it");

  const realNow = Date.now;
  if (remainingMs !== undefined) {
    Date.now = () => realNow() - 30_000 + remainingMs;
  }
  try {
    await investigate.unmount();
  } finally {
    Date.now = realNow;
  }
}

test("the mini-game phase selects screen 10 on TV and screen 11 on phone", () => {
  const state = round({ phase: "mini_game", phaseEntry: 12 });
  const tv = resolveScreen("tv", lobby(), state, DEFAULT_SLOTS);
  const phone = resolveScreen("phone", lobby(), state, DEFAULT_SLOTS);
  assert.equal(tv.kind === "phase" && tv.Slot, MiniGameTv);
  assert.equal(phone.kind === "phase" && phone.Slot, MiniGamePhone);
});

test("screen 10 loads a fixture package on the public display address without sign-in or a shell clock", async () => {
  const seen: string[] = [];
  const services = fixtureServices(seen);
  const fetchActive = services.fetcher!;
  let release: () => void = () => {};
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  services.fetcher = (async (input: RequestInfo | URL, init?: RequestInit) => {
    if (String(input).includes("/mini-games/active")) await gate;
    return fetchActive(input, init);
  }) as typeof fetch;
  const page = await mount(
    createElement(MiniGameTv, {
      ...base,
      round: round({ phase: "mini_game", phaseEntry: 12 }),
      stageServices: services,
    }),
  );
  assert.ok(page.text().includes("Getting the game ready..."));
  release();
  await settle();

  assert.ok(page.text().includes("A Quiet Evening"));
  assert.ok(
    page.text().includes("Fixture shared view"),
    `${page.text()} ${page.container.innerHTML} ${seen.join(" | ")}`,
  );
  assert.ok(!page.text().includes("1:42"), "the shell adds no second clock");
  assert.ok(seen.some((url) => url.endsWith("/mini-games/active/display")));
  assert.ok(!seen.some((url) => url.endsWith("/mini-games/active")));
  await page.unmount();
});

test("screen 10 explains when no mini-game is running", async () => {
  const services = fixtureServices();
  const fetcher = services.fetcher!;
  services.fetcher = (async (input: RequestInfo | URL, init?: RequestInit) => {
    if (String(input).endsWith("/mini-games/active/display")) {
      return new Response("not found", { status: 404 });
    }
    return fetcher(input, init);
  }) as typeof fetch;
  const page = await mount(
    createElement(MiniGameTv, {
      ...base,
      round: round({ phase: "mini_game", phaseEntry: 12 }),
      stageServices: services,
    }),
  );

  assert.ok(page.text().includes("No mini-game in progress."));
  await page.unmount();
});

test("screen 10 distinguishes a network outage from a skipped mini-game", async () => {
  const services = fixtureServices();
  const fetcher = services.fetcher!;
  services.fetcher = (async (input: RequestInfo | URL, init?: RequestInit) => {
    if (String(input).endsWith("/mini-games/active/display")) {
      throw new TypeError("Failed to fetch");
    }
    return fetcher(input, init);
  }) as typeof fetch;
  const page = await mount(
    createElement(MiniGameTv, {
      ...base,
      round: round({ phase: "mini_game", phaseEntry: 12 }),
      stageServices: services,
    }),
  );

  assert.ok(page.text().includes("Could not reach the mini-game."));
  assert.ok(!page.text().includes("No mini-game in progress."));
  await page.unmount();
});

test("screen 10 shows a fallback when the package definition cannot load", async () => {
  const services = fixtureServices();
  services.loadDefinition = async () => {
    throw new Error("definition unavailable");
  };
  const page = await mount(
    createElement(MiniGameTv, {
      ...base,
      round: round({ phase: "mini_game", phaseEntry: 12 }),
      stageServices: services,
    }),
  );
  await settle();

  assert.ok(page.text().includes("The mini-game could not be shown."));
  await page.unmount();
});

test("screen 11 explains when no mini-game is running", async () => {
  const services = fixtureServices();
  const fetcher = services.fetcher!;
  services.fetcher = (async (input: RequestInfo | URL, init?: RequestInit) => {
    if (String(input).endsWith("/mini-games/active")) {
      return new Response("not found", { status: 404 });
    }
    return fetcher(input, init);
  }) as typeof fetch;
  const page = await mount(
    createElement(MiniGamePhone, {
      ...base,
      round: round({ phase: "mini_game", phaseEntry: 12 }),
      stageServices: services,
    }),
  );

  assert.ok(page.text().includes("No mini-game in progress."));
  await page.unmount();
});

test("screen 11 shows a fallback when the package definition cannot load", async () => {
  const services = fixtureServices();
  services.loadDefinition = async () => {
    throw new Error("definition unavailable");
  };
  const page = await mount(
    createElement(MiniGamePhone, {
      ...base,
      round: round({ phase: "mini_game", phaseEntry: 12 }),
      stageServices: services,
    }),
  );
  await settle();

  assert.ok(page.text().includes("The mini-game could not be shown."));
  await page.unmount();
});

test("screen 11 uses this seat's sign-in on the player route", async () => {
  const seen: string[] = [];
  const page = await mount(
    createElement(MiniGamePhone, {
      ...base,
      round: round({ phase: "mini_game", phaseEntry: 12 }),
      stageServices: fixtureServices(seen),
    }),
  );
  await settle();

  assert.ok(page.text().includes("Fixture phone view"));
  assert.ok(seen.some((url) => url.endsWith("/mini-games/active")));
  assert.ok(!seen.some((url) => url.endsWith("/mini-games/active/display")));
  await page.unmount();
});

test("screen 11 retries a failed token refresh and clears the error on recovery", async () => {
  const seen: string[] = [];
  let tokenCalls = 0;
  const page = await mount(
    createElement(MiniGamePhone, {
      ...base,
      getToken: async () => {
        tokenCalls += 1;
        if (tokenCalls === 1)
          throw new Error("temporary token refresh failure");
        return "player-sign-in";
      },
      round: round({ phase: "mini_game", phaseEntry: 12 }),
      stageServices: fixtureServices(seen),
    }),
  );
  assert.ok(page.text().includes("That did not work. Try again."));
  await new Promise((done) => setTimeout(done, 1100));
  await settle();

  assert.ok(tokenCalls >= 2);
  assert.ok(page.text().includes("Fixture phone view"));
  assert.ok(!page.text().includes("That did not work. Try again."));
  await page.unmount();
});

test("a later mini-game phase entry remounts the package stage", async () => {
  const seen: string[] = [];
  const services = fixtureServices(seen);
  const props = {
    ...base,
    round: round({ phase: "mini_game", phaseEntry: 12 }),
    stageServices: services,
  };
  const page = await mount(createElement(MiniGameTv, props));
  await settle();
  const before = seen.filter((url) =>
    url.endsWith("/mini-games/active/display"),
  ).length;
  assert.ok(before >= 1);

  await page.rerender(
    createElement(MiniGameTv, {
      ...props,
      round: round({ phase: "mini_game", phaseEntry: 13 }),
    }),
  );
  await settle();
  assert.ok(
    seen.filter((url) => url.endsWith("/mini-games/active/display")).length >
      before,
  );
  await page.unmount();
});

test("a finding left open at time-up is shown once on the mini-game phone", async () => {
  const engine = fakeEngine();
  await withFetch(engine, async () => {
    const investigate = await mount(
      createElement(InvestigatePhone, {
        ...base,
        round: round({ phase: "choices" }),
      }),
    );
    await investigate.clickContaining("Search the desk");
    await investigate.click("Spend it");
    assert.ok(
      investigate.text().includes("A torn page is wedged behind the drawer."),
    );
    await investigate.unmount();

    const first = await mount(
      createElement(MiniGamePhone, {
        ...base,
        round: round({ phase: "mini_game", phaseEntry: 12 }),
        stageServices: fixtureServices(),
      }),
    );
    assert.ok(
      first.text().includes("A torn page is wedged behind the drawer."),
    );
    assert.ok(first.text().includes("Time's up. It's in your notebook."));
    await first.click("OK");
    await first.unmount();

    const second = await mount(
      createElement(MiniGamePhone, {
        ...base,
        round: round({ phase: "mini_game", phaseEntry: 13 }),
        stageServices: fixtureServices(),
      }),
    );
    assert.ok(
      !second.text().includes("A torn page is wedged behind the drawer."),
    );
    await second.unmount();
  });
});

test("the mini-game stays playable beside a finding and OK dismisses it in StrictMode", async () => {
  clearHeldFinding();
  try {
    const engine = fakeEngine();
    await withFetch(engine, async () => {
      await leaveDeskFinding();
      const props = {
        ...base,
        round: round({ phase: "mini_game", phaseEntry: 12 }),
        stageServices: fixtureServices(),
      };
      const pageElement = () =>
        createElement(StrictMode, null, createElement(MiniGamePhone, props));
      const page = await mount(pageElement());
      try {
        assert.ok(
          page.text().includes("A torn page is wedged behind the drawer."),
        );
        assert.ok(
          page.text().includes("Fixture phone view"),
          "the mini-game remains mounted and playable beside the finding",
        );
        assert.ok(page.buttons().some((b) => b.textContent?.trim() === "OK"));

        await page.rerender(pageElement());
        await page.click("OK");
        assert.ok(
          !page.text().includes("A torn page is wedged behind the drawer."),
        );
        assert.ok(page.text().includes("Fixture phone view"));

        await page.rerender(pageElement());
        assert.ok(
          !page.text().includes("A torn page is wedged behind the drawer."),
        );
      } finally {
        await page.unmount();
      }
    });
  } finally {
    clearHeldFinding();
  }
});

test("the finding expires without a tap and stays gone on re-entry", async () => {
  clearHeldFinding();
  try {
    const engine = fakeEngine();
    await withFetch(engine, async () => {
      await leaveDeskFinding(2_000);
      const props = {
        ...base,
        round: round({ phase: "mini_game", phaseEntry: 12 }),
        stageServices: fixtureServices(),
      };
      let page: Awaited<ReturnType<typeof mount>> | undefined;
      try {
        page = await mount(createElement(MiniGamePhone, props));
        assert.ok(
          page.text().includes("A torn page is wedged behind the drawer."),
        );
        await act(async () => {
          await new Promise((done) => setTimeout(done, 2_250));
        });
        await settle();
        assert.ok(
          !page.text().includes("A torn page is wedged behind the drawer."),
        );
        assert.ok(page.text().includes("Fixture phone view"));
        await page.unmount();
        page = undefined;

        page = await mount(
          createElement(MiniGamePhone, {
            ...props,
            round: round({ phase: "mini_game", phaseEntry: 13 }),
          }),
        );
        assert.ok(
          !page.text().includes("A torn page is wedged behind the drawer."),
        );
      } finally {
        if (page) await page.unmount();
      }
    });
  } finally {
    clearHeldFinding();
  }
});
