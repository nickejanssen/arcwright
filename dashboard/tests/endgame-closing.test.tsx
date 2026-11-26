// Screens 17 to 22 (AW-333 part B): the Verdict, each player's result, the
// Postmortem, the thanks screen and the survey. All names and answers here are
// invented placeholders.

import assert from "node:assert/strict";
import test from "node:test";
import { act, createElement } from "react";
import type { RoundState } from "../src/api/round.js";
import { fetchRound } from "../src/api/round.js";
import { TvView } from "../src/screens/DisplayScreen.js";
import { PhoneView } from "../src/screens/WaitingScreen.js";
import { DEFAULT_SLOTS, resolveScreen } from "../src/shell/phaseScreens.js";
import { mount, settle, typeInto } from "./helpers/dom.js";
import type { Mounted } from "./helpers/dom.js";
import { ME, lobby, round, withFetch } from "./helpers/round-fixtures.js";

const A = "participant-uuid-3333";
const B = "participant-uuid-4444";
const players = [
  { participantId: A, name: "Avery", ready: false, answeredSurvey: true },
  { participantId: B, name: "Blair", ready: false, answeredSurvey: false },
  { participantId: ME, name: "Jordan", ready: false, answeredSurvey: false },
];

type Result = NonNullable<NonNullable<RoundState["closing"]>["result"]>;

function result(over: Partial<Result> = {}): Result {
  return {
    decided_by: "only_solver",
    winners: [
      {
        participant_id: A,
        proof: { concept_id: "concept_internal_1", label: "The torn page" },
      },
    ],
    players: [
      { participant_id: A, solved: true },
      { participant_id: B, solved: false },
      { participant_id: ME, solved: false },
    ],
    ...over,
  };
}

function tv(state: RoundState) {
  return createElement(TvView, {
    sessionId: "game-uuid-1111",
    feed: { lobby: lobby(), round: state, unreachable: false, gone: false },
    joinBaseUrl: "https://app.test",
  });
}

function phone(state: RoundState, status = "active") {
  return createElement(PhoneView, {
    sessionId: "game-uuid-1111",
    displayName: "Jordan",
    participantId: ME,
    getToken: async () => "my-sign-in",
    joinCode: "K7QP",
    joinUrl: "https://app.test/join",
    feed: {
      lobby: lobby({ status }),
      round: state,
      unreachable: false,
      gone: false,
    },
    role: "player",
    controls: {} as never,
    settings: { textSize: "normal", reduceMotion: "system" },
    onSettingsChange: () => undefined,
  });
}

function serving(fetcher: typeof fetch, run: () => Promise<void>) {
  return withFetch({ fetch: fetcher } as never, run);
}

async function still(run: () => Promise<void>) {
  document.documentElement.setAttribute("data-reduce-motion", "always");
  try {
    await run();
  } finally {
    document.documentElement.removeAttribute("data-reduce-motion");
  }
}

async function wait(ms: number) {
  await act(async () => {
    await new Promise((resolve) => setTimeout(resolve, ms));
  });
}

function noInternals(page: Mounted) {
  const html = page.container.innerHTML;
  assert.doesNotMatch(
    html,
    /participant-uuid|concept_internal|slot_internal|cast_internal/,
  );
}

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status });

const myResult = {
  participant_id: ME,
  state: "locked",
  solved: false,
  slots: [
    { slot_id: "slot_internal_who", label: "Who", right: true },
    { slot_id: "slot_internal_how", label: "How", right: false },
    { slot_id: "slot_internal_why", label: "Why", right: false },
  ],
};

// The private routes screen 18 reads. After Last Call the theory route returns
// only the saved answers, with no labels (engine commit_phase.read_form).
function resultRoutes(
  calls: string[] = [],
  mine: unknown = myResult,
): typeof fetch {
  return (async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    calls.push(url);
    assert.equal(
      (init?.headers as Record<string, string>).Authorization,
      "Bearer my-sign-in",
    );
    if (url.endsWith("/me/result")) return json(mine);
    if (url.endsWith("/me/theory"))
      return json({
        open: false,
        slots: [],
        account: [],
        proof_options: [],
        theory: {
          state: "locked",
          answers: {
            slot_internal_who: "cast_internal_1",
            slot_internal_how: "concept_internal_2",
            slot_internal_why: "cast_internal_9",
          },
          proof: null,
          revision: 2,
        },
      });
    if (url.endsWith("/me/holdings"))
      return json({
        concepts: [
          {
            concept_id: "concept_internal_2",
            label: "The spare key",
            text: "",
          },
        ],
      });
    throw new Error(`unexpected ${url}`);
  }) as typeof fetch;
}

const closing = {
  reveal: {
    players: [
      {
        participant_id: ME,
        answer: { value: "cast_internal_1", label: "Marlow" },
      },
    ],
  },
  result: result(),
  recap: {
    lines: [
      { participant_id: A, text: "Placeholder line for A.", hints: {} },
      {
        participant_id: ME,
        text: "Placeholder line for me.",
        hints: { pause_before_ms: 0 },
      },
    ],
  },
};

test("the room read keeps the result, the recap and who answered the survey", async () => {
  const state = await fetchRound("game", async () =>
    json({
      session_status: "active",
      phase: "recap",
      over: true,
      closing,
      players: [
        { participant_id: A, display_name: "Avery", answered_survey: true },
        { participant_id: B, display_name: "Blair" },
      ],
    }),
  );
  assert.equal(state?.status, "ended");
  assert.deepEqual(state?.closing?.recap, closing.recap);
  assert.deepEqual(state?.closing?.result, closing.result);
  assert.deepEqual(
    state?.players.map((p) => p.answeredSurvey),
    [true, false],
  );
});

// --- screen 17 ---

test("Verdict: names land one at a time, the winner last with their proof", async () => {
  const page = await mount(
    tv(round({ phase: "result", players, closing: { result: result() } })),
  );
  try {
    assert.match(page.text(), /The Verdict/);
    assert.match(page.text(), /Blair did not solve it/);
    assert.doesNotMatch(page.text(), /Jordan|Avery|torn page/);
    await wait(2100);
    assert.match(page.text(), /Jordan did not solve it/);
    assert.doesNotMatch(page.text(), /Avery/);
    await wait(2100);
    assert.match(page.text(), /Avery solved it\./);
    assert.match(page.text(), /Their proof: The torn page/);
    const text = page.text();
    assert.ok(text.indexOf("Jordan") < text.indexOf("Avery"));
    assert.ok(page.container.querySelector(".tv-verdict-winner"));
    noInternals(page);
  } finally {
    await page.unmount();
  }
});

test("Verdict: nobody solved it, with no winner or proof invented", () =>
  still(async () => {
    const value = result({
      decided_by: "no_solver",
      winners: [],
      players: players.map((p) => ({
        participant_id: p.participantId,
        solved: false,
      })),
    });
    const page = await mount(
      tv(round({ phase: "result", players, closing: { result: value } })),
    );
    try {
      assert.match(page.text(), /Nobody solved it\. The case wins\./);
      assert.doesNotMatch(page.text(), /Their proof|won more/);
    } finally {
      await page.unmount();
    }
  }));

test("Verdict: each tie-break is named, and a shared win shows both winners", () =>
  still(async () => {
    const solved = [
      { participant_id: A, solved: true },
      { participant_id: B, solved: true },
      { participant_id: ME, solved: false },
    ];
    for (const [decided_by, reason] of [
      ["mini_game_wins", /Avery won more mini-games\./],
      ["mini_game_placings", /Avery placed higher in the mini-games\./],
    ] as const) {
      const page = await mount(
        tv(
          round({
            phase: "result",
            players,
            closing: {
              result: result({
                decided_by,
                players: solved,
                winners: [{ participant_id: A, proof: null }],
              }),
            },
          }),
        ),
      );
      assert.match(page.text(), reason);
      assert.match(page.text(), /Blair solved it\./);
      assert.doesNotMatch(page.text(), /Their proof/);
      await page.unmount();
    }
    const page = await mount(
      tv(
        round({
          phase: "result",
          players,
          closing: {
            result: result({
              decided_by: "shared",
              players: solved,
              winners: [
                { participant_id: A, proof: { label: "Proof one" } },
                { participant_id: B, proof: { label: "Proof two" } },
              ],
            }),
          },
        }),
      ),
    );
    try {
      assert.equal(
        page.container.querySelectorAll(".tv-verdict-winner").length,
        2,
      );
      assert.match(page.text(), /Their proof: Proof one/);
      assert.match(page.text(), /Their proof: Proof two/);
      assert.match(page.text(), /A tie\. They share the win\./);
    } finally {
      await page.unmount();
    }
  }));

test("Verdict: a result that has not arrived shows only the title, then stages", async () => {
  const page = await mount(
    tv(round({ phase: "result", players, closing: { result: null } })),
  );
  try {
    assert.match(page.text(), /The Verdict/);
    assert.doesNotMatch(page.text(), /solved/);
    await page.rerender(
      tv(round({ phase: "result", players, closing: { result: result() } })),
    );
    assert.match(page.text(), /Blair did not solve it/);
  } finally {
    await page.unmount();
  }
});

// --- screen 18 ---

test("the phone stays eyes-up during result and reads nothing private", async () => {
  const calls: string[] = [];
  await serving(resultRoutes(calls), async () => {
    const page = await mount(
      phone(round({ phase: "result", players, closing })),
    );
    try {
      assert.match(page.text(), /Eyes on the TV\./);
      assert.doesNotMatch(
        page.text(),
        /Your theory|Right|Wrong|solved|Placeholder line/,
      );
      assert.ok(!calls.some((url) => url.endsWith("/me/result")));
    } finally {
      await page.unmount();
    }
  });
});

test("once the engine is past the Verdict the phone shows its own result", async () => {
  const calls: string[] = [];
  await serving(resultRoutes(calls), async () => {
    const page = await mount(
      phone(round({ phase: "result", players, closing })),
    );
    try {
      await page.rerender(
        phone(round({ phase: "recap", phaseEntry: 8, players, closing })),
      );
      const rows = Array.from(
        page.container.querySelectorAll(".endgame-slot"),
      ).map((row) => row.textContent);
      // Engine slot order. An answer with no public or held label is left out
      // rather than shown as an internal value.
      assert.deepEqual(rows, [
        "Who Marlow Right",
        "How The spare key Wrong",
        "Why Wrong",
      ]);
      assert.ok(calls.some((url) => url.endsWith("/me/result")));
      noInternals(page);
    } finally {
      await page.unmount();
    }
  });
});

test("a phone with no locked theory says so and marks nothing", async () => {
  await serving(
    resultRoutes([], { ...myResult, state: "no_theory" }),
    async () => {
      const page = await mount(
        phone(round({ phase: "recap", players, closing })),
      );
      try {
        assert.match(page.text(), /No theory was locked\./);
        assert.equal(
          page.container.querySelectorAll(".endgame-slot").length,
          0,
        );
      } finally {
        await page.unmount();
      }
    },
  );
});

test("a failed result read can be retried; missing labels never block it", async () => {
  let resultReads = 0;
  const fake = (async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/me/result") && ++resultReads > 1) return json(myResult);
    return json({}, 503);
  }) as typeof fetch;
  await serving(fake, async () => {
    const page = await mount(
      phone(round({ phase: "recap", players, closing })),
    );
    try {
      assert.match(page.text(), /That did not work/);
      await page.click("Try again");
      assert.equal(page.container.querySelectorAll(".endgame-slot").length, 3);
      assert.doesNotMatch(page.text(), /That did not work/);
    } finally {
      await page.unmount();
    }
  });
});

// --- screens 19 and 20 ---

test("Postmortem TV shows the public lines one at a time, in the engine's order", async () => {
  const page = await mount(tv(round({ phase: "recap", players, closing })));
  try {
    assert.match(page.text(), /Postmortem/);
    assert.match(page.text(), /Avery:\s*Placeholder line for A\./);
    assert.doesNotMatch(page.text(), /line for me/);
    await wait(2100);
    assert.match(page.text(), /Jordan:\s*Placeholder line for me\./);
    const text = page.text();
    assert.ok(text.indexOf("line for A") < text.indexOf("line for me"));
    noInternals(page);
  } finally {
    await page.unmount();
  }
});

test("Postmortem TV with no lines shows only the title", async () => {
  const page = await mount(
    tv(round({ phase: "recap", players, closing: { recap: { lines: [] } } })),
  );
  try {
    assert.match(page.text(), /Postmortem/);
    assert.equal(page.container.querySelectorAll(".tv-line").length, 0);
  } finally {
    await page.unmount();
  }
});

test("the phone shows only its own recap line, and none when it has none", async () => {
  await serving(resultRoutes(), async () => {
    const page = await mount(
      phone(round({ phase: "recap", players, closing })),
    );
    try {
      assert.match(page.text(), /Placeholder line for me\./);
      assert.doesNotMatch(page.text(), /line for A/);
      await page.rerender(
        phone(
          round({
            phase: "recap",
            players,
            closing: { recap: { lines: [closing.recap.lines[0]] } },
          }),
        ),
      );
      assert.doesNotMatch(page.text(), /Placeholder line|Postmortem/);
    } finally {
      await page.unmount();
    }
  });
});

// --- after the recap ---

test("only a recap the engine has finished leads to thanks and the survey", () => {
  const kind = (status: string, state: Partial<RoundState>) => {
    const resolved = resolveScreen(
      "tv",
      lobby({ status }),
      round(state),
      DEFAULT_SLOTS,
    );
    return resolved.kind === "phase" ? resolved.phase : resolved.kind;
  };
  const done = { phase: "recap", status: "ended" as const };
  assert.equal(kind("active", { phase: "recap" }), "recap");
  assert.equal(kind("active", done), "after:recap");
  assert.equal(kind("completed", done), "after:recap");
  // The host ended the game while the recap was on screen.
  assert.equal(kind("completed", { phase: "recap" }), "after:recap");
  assert.equal(kind("paused", done), "paused");
  assert.equal(kind("abandoned", done), "ended");
  for (const phase of ["commit", "reveal", "result", "scene"]) {
    assert.equal(kind("completed", { phase, status: "ended" }), "ended");
    assert.equal(kind("active", { phase, status: "ended" }), "ended");
  }
});

test("Thanks TV shows who has answered and no answers or controls", async () => {
  const page = await mount(
    tv(
      round({
        phase: "recap",
        status: "ended",
        players,
        closing,
        lines: [{ text: "PRIVATE SURVEY MARKER" }],
      }),
    ),
  );
  try {
    assert.match(page.text(), /Thanks for playing\./);
    assert.match(page.text(), /Answer three quick questions on your phone\./);
    assert.match(page.text(), /Avery\s*Answered/);
    assert.match(page.text(), /Blair\s*Not yet/);
    assert.doesNotMatch(page.text(), /MARKER|Placeholder line/);
    assert.equal(page.buttons().length, 0);
    noInternals(page);
  } finally {
    await page.unmount();
  }
});

// --- screen 22 ---

const after = round({ phase: "recap", status: "ended", players });

function surveyEngine(saved: Map<string, unknown>, sends: unknown[] = []) {
  let failNext = false;
  const fetcher = (async (input: RequestInfo | URL, init?: RequestInit) => {
    assert.match(String(input), /\/me\/survey$/);
    const seat = (init?.headers as Record<string, string>).Authorization;
    if (init?.method === "PUT") {
      if (failNext) {
        failNext = false;
        return json({}, 503);
      }
      const body = JSON.parse(String(init.body));
      sends.push(body);
      saved.set(seat, body);
      return json({ answered: true, ...body });
    }
    const mine = saved.get(seat) as object | undefined;
    return json(
      mine
        ? { answered: true, ...mine }
        : { answered: false, answers: {}, comment: null },
    );
  }) as typeof fetch;
  return { fetcher, fail: () => (failNext = true) };
}

function pick(page: Mounted, question: string, answer: string) {
  const group = Array.from(page.container.querySelectorAll("fieldset")).find(
    (item) => item.querySelector("legend")?.textContent === question,
  );
  const button = Array.from(group?.querySelectorAll("button") ?? []).find(
    (item) => item.textContent === answer,
  );
  assert.ok(button, `${question}: ${answer}`);
  return act(async () => {
    button.dispatchEvent(
      new (window.MouseEvent as typeof MouseEvent)("click", { bubbles: true }),
    );
  });
}

async function fill(page: Mounted) {
  await pick(page, "How fun was it?", "4");
  await pick(page, "Did you feel like a detective?", "5");
  await pick(page, "Play again?", "Maybe");
  await settle();
}

test("survey: three answers and an optional comment, retried after a failure, then replaced", async () => {
  const sends: unknown[] = [];
  const engine = surveyEngine(new Map(), sends);
  await serving(engine.fetcher, async () => {
    const page = await mount(phone(after, "completed"));
    try {
      assert.equal(page.button("Send").disabled, true);
      await fill(page);
      assert.equal(page.button("Send").disabled, false);
      engine.fail();
      await page.click("Send");
      assert.match(page.text(), /That did not work/);
      assert.doesNotMatch(page.text(), /Sent\./);
      await page.click("Send");
      assert.match(page.text(), /Sent\./);
      await pick(page, "Play again?", "Yes");
      await settle();
      assert.doesNotMatch(page.text(), /Sent\./);
      await page.click("Send");
      assert.deepEqual(sends, [
        {
          answers: { fun: 4, detective: 5, play_again: "maybe" },
          comment: null,
        },
        {
          answers: { fun: 4, detective: 5, play_again: "yes" },
          comment: null,
        },
      ]);
    } finally {
      await page.unmount();
    }
  });
});

test("survey: a phone gets back its own answers and never another seat's", async () => {
  const saved = new Map<string, unknown>([
    [
      "Bearer my-sign-in",
      {
        answers: { fun: 2, detective: 3, play_again: "no" },
        comment: "My own words",
      },
    ],
    ["Bearer other-sign-in", { answers: { fun: 5 }, comment: "Not mine" }],
  ]);
  const sends: unknown[] = [];
  await serving(surveyEngine(saved, sends).fetcher, async () => {
    const page = await mount(phone(after));
    try {
      const pressed = Array.from(
        page.container.querySelectorAll('[aria-pressed="true"]'),
      ).map((item) => item.textContent);
      assert.deepEqual(pressed, ["2", "3", "No"]);
      const box = page.container.querySelector("textarea")!;
      assert.equal(box.value, "My own words");
      assert.doesNotMatch(page.container.innerHTML, /Not mine/);
      await typeInto(box as never, "Changed");
      await page.click("Send");
      assert.equal((sends[0] as { comment: string }).comment, "Changed");
    } finally {
      await page.unmount();
    }
  });
});

test("survey: a slow saved copy does not overwrite what the player just chose", async () => {
  let release!: (response: Response) => void;
  const pending = new Promise<Response>((resolve) => {
    release = resolve;
  });
  await serving((async () => pending) as typeof fetch, async () => {
    const page = await mount(phone(after));
    try {
      await pick(page, "How fun was it?", "5");
      await act(async () => {
        release(
          json({ answered: true, answers: { fun: 1 }, comment: "Older" }),
        );
      });
      await settle();
      const pressed = Array.from(
        page.container.querySelectorAll('[aria-pressed="true"]'),
      ).map((item) => item.textContent);
      assert.deepEqual(pressed, ["5"]);
    } finally {
      await page.unmount();
    }
  });
});

test("survey: unsent answers survive the screen dropping out for one read", async () => {
  await serving(surveyEngine(new Map()).fetcher, async () => {
    const view = (state: RoundState | null) =>
      createElement(PhoneView, {
        ...phone(after).props,
        sessionId: "game-with-a-draft",
        feed: {
          lobby: lobby({ status: "completed" }),
          round: state,
          unreachable: false,
          gone: false,
        },
      });
    const page = await mount(view(after));
    try {
      await fill(page);
      await typeInto(
        page.container.querySelector("textarea") as never,
        "Half written",
      );
      await page.rerender(view(null));
      assert.equal(page.container.querySelector("textarea"), null);
      await page.rerender(view(after));
      assert.equal(
        page.container.querySelector("textarea")!.value,
        "Half written",
      );
      assert.equal(page.button("Send").disabled, false);
    } finally {
      await page.unmount();
    }
  });
});
