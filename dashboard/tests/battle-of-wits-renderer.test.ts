import assert from "node:assert/strict";
import { resolve } from "node:path";
import test from "node:test";
import { Window as HappyWindow } from "happy-dom";
import { createServer, isFileLoadingAllowed, normalizePath } from "vite";

import renderer from "../../nightcap/mini_games/battle-of-wits/client/renderer.ts";
import definition from "../../nightcap/mini_games/battle-of-wits/definitions/0.1.0.json";
import type {
  MiniGameContext,
  MiniGameDefinition,
} from "../src/mini-game-kit/index.js";
import type {
  ContentEvent,
  MiniGameState,
} from "../src/mini-game-kit/wire-types.js";

const question = {
  phase: "question",
  index: 0,
  total: 3,
  kind: "choice",
  prompt: "How many?",
  options: ["One", "Two", "Three", "Four"].map((label) => ({
    id: label.toLowerCase(),
    label,
  })),
};
const sorting = {
  ...question,
  index: 1,
  kind: "sort",
  prompt: "Put these in order",
  options: ["A", "C", "B", "D"].map((label) => ({
    id: label.toLowerCase(),
    label,
  })),
};

test("Vite allows the renderer but protects the private question file in either config", async () => {
  const dashboard = resolve(process.env.DASHBOARD_DIR ?? "dashboard");
  const packagePath = resolve(
    dashboard,
    "../nightcap/mini_games/battle-of-wits",
  );
  for (const extension of ["ts", "js"]) {
    const server = await createServer({
      root: dashboard,
      configFile: resolve(dashboard, `vite.config.${extension}`),
      server: { middlewareMode: true, hmr: false, watch: null },
    });
    try {
      const allowed = (path: string) =>
        isFileLoadingAllowed(server, normalizePath(resolve(packagePath, path)));
      assert.equal(allowed("client/renderer.ts"), true);
      assert.equal(allowed("definitions/0.1.0.json"), true);
      assert.equal(allowed("server/questions-0.1.0.json"), false);
      assert.equal(
        allowed("../../../engine/tests/test_battle_of_wits.py"),
        false,
      );
      assert.equal(
        allowed(
          "../../../engine/tests/__pycache__/test_battle_of_wits.cpython-311.pyc",
        ),
        false,
      );
    } finally {
      await server.close();
    }
  }
});

function mount(
  surface: MiniGameContext["surface"],
  runtimeState: Record<string, unknown>,
  overrides: Partial<MiniGameState> = {},
  submit?: MiniGameContext["submit"],
) {
  const window = new HappyWindow();
  const root = window.document.createElement("section");
  const sent: unknown[] = [];
  const state: MiniGameState = {
    runId: "current-run",
    gameId: "battle-of-wits",
    status: "active",
    deadlineAt: new Date(Date.now() + 12000).toISOString(),
    runtimeState,
    mySubmissions: [],
    playerNames: {
      "char-1": "River",
      "seat-1": "River",
      "seat-2": "Kit",
      "seat-3": "Pat",
    },
    ...overrides,
  };
  const lifecycle = renderer.mount(root as unknown as HTMLElement, {
    surface,
    sessionId: "room",
    participantId: "seat-1",
    characterId: "char-1",
    state,
    definition: definition as MiniGameDefinition,
    async submit(payload, submissionId) {
      sent.push(payload);
      return (
        submit?.(payload, submissionId) ?? {
          submissionId: "saved",
          isAccepted: true,
        }
      );
    },
    onEvent: () => () => {},
    reportPerf: () => {},
  });
  return {
    root,
    lifecycle,
    sent,
    state,
    button(label: string) {
      const found = [...root.querySelectorAll("button")].find(
        (item) =>
          item.textContent === label ||
          item.getAttribute("aria-label") === label,
      );
      assert.ok(found, `missing button: ${label}`);
      return found;
    },
    async close() {
      lifecycle.unmount();
      await window.happyDOM.close();
    },
  };
}

function stageEvent(stage: object, runId: string): ContentEvent {
  return {
    event_id: "event",
    session_id: "room",
    sequence_number: 1,
    timestamp: new Date().toISOString(),
    actor_id: null,
    target_audience: "all",
    target_player_id: null,
    category: "state_transition",
    presentation_hints: {
      emotion: null,
      urgency: null,
      voice_hint: null,
      pause_before_ms: 0,
      lighting_hint: null,
    },
    event_type: "battle_of_wits_stage",
    payload: {
      run_id: runId,
      stage,
      deadline_at: new Date(Date.now() + 5000).toISOString(),
    },
  };
}

test("only the helped phone disables answers and a rejoin restores its lock", async () => {
  const phone = mount("phone", {
    stage: question,
    player: { "char-1": { locked: false, disabled: ["one", "two"] } },
  });
  try {
    assert.equal(phone.button("One").disabled, true);
    assert.equal(phone.button("Four").disabled, false);
    phone.button("Four").click();
    await new Promise<void>((resolve) => setImmediate(resolve));
    assert.deepEqual(phone.sent, [
      { action: "choice", question_index: 0, option_id: "four" },
    ]);
    assert.match(phone.root.textContent, /Answer locked/);
    phone.lifecycle.update({
      ...phone.state,
      runtimeState: { stage: question, player: { "char-1": { locked: true } } },
    });
    assert.match(phone.root.textContent, /Answer locked/);
  } finally {
    await phone.close();
  }
});

test("keyboard-accessible sorting preserves the pre-placed card and submits the displayed order", async () => {
  const phone = mount("phone", {
    stage: sorting,
    player: { "char-1": { locked: false, pinned: { id: "a", position: 0 } } },
  });
  try {
    assert.equal(phone.button("Move A down").disabled, true);
    phone.button("Move B up").click();
    phone.button("Lock order").click();
    await Promise.resolve();
    assert.deepEqual(phone.sent, [
      { action: "sort", question_index: 1, order: ["a", "b", "c", "d"] },
    ]);
  } finally {
    await phone.close();
  }
});

test("a lost reply retries the same answer and ID on an HTTP phone", async () => {
  const originalCrypto = Object.getOwnPropertyDescriptor(globalThis, "crypto");
  Object.defineProperty(globalThis, "crypto", {
    configurable: true,
    value: { getRandomValues: (bytes: Uint8Array) => bytes.fill(16) },
  });
  const ids: Array<string | undefined> = [];
  const phone = mount(
    "phone",
    {
      stage: question,
      player: { "char-1": { locked: false } },
    },
    {},
    async (_payload, id) => {
      ids.push(id);
      if (ids.length === 1) throw new TypeError("network response lost");
      return { submissionId: id ?? "missing", isAccepted: true };
    },
  );
  try {
    phone.button("Four").click();
    await new Promise<void>((resolve) => setImmediate(resolve));
    assert.equal(phone.root.querySelectorAll("button").length, 1);
    phone.button("Retry answer").click();
    await new Promise<void>((resolve) => setImmediate(resolve));
    assert.ok(ids[0]);
    assert.deepEqual(ids, [ids[0], ids[0]]);
    assert.deepEqual(
      phone.sent,
      Array(2).fill({
        action: "choice",
        question_index: 0,
        option_id: "four",
      }),
    );
    assert.match(phone.root.textContent, /Answer locked/);
  } finally {
    if (originalCrypto)
      Object.defineProperty(globalThis, "crypto", originalCrypto);
    await phone.close();
  }
});

test("TV ignores stale runs and shows correctness and ranking only at the current reveal", async () => {
  const display = mount("shared_display", { stage: question });
  const reveal = {
    ...question,
    phase: "reveal",
    answer: ["four"],
    correct: ["char-1"],
    scores: { "char-1": 4 },
    standing: [["char-1"]],
  };
  try {
    display.lifecycle.handleEvent(stageEvent(reveal, "past-run"));
    assert.doesNotMatch(display.root.textContent, /Correct answer/);
    assert.equal(display.root.querySelectorAll("button").length, 0);
    display.lifecycle.handleEvent(stageEvent(reveal, "current-run"));
    assert.match(display.root.textContent, /Correct answer.*Four/s);
    assert.match(display.root.textContent, /River/);
    display.lifecycle.handleEvent(stageEvent(question, "current-run"));
    assert.match(display.root.textContent, /Correct answer/);
  } finally {
    await display.close();
  }
});

test("result hold reads the saved standing from last to first and names shared winners", async () => {
  const display = mount(
    "shared_display",
    {},
    {
      status: "completed",
      deadlineAt: null,
      resultHold: {
        phaseEntry: 3,
        standing: [["seat-1", "seat-2"], ["seat-3"]],
      },
    },
  );
  try {
    const text = display.root.textContent;
    assert.match(text, /2\. Pat.*1\. River, Kit.*Winners: River, Kit/s);
    assert.match(text, /Back to the story/);
    assert.doesNotMatch(JSON.stringify(definition), /correct_order|answer_key/);
    const winnerIsHidden = () =>
      [...display.root.querySelectorAll("p")].find((line) =>
        line.textContent.startsWith("Winners:"),
      )?.hidden;
    assert.equal(winnerIsHidden(), true);
    display.lifecycle.update({
      ...display.state,
      playerNames: { "seat-1": "River", "seat-2": "Kit", "seat-3": "Pat II" },
    });
    assert.equal(winnerIsHidden(), true);
    assert.match(display.root.textContent, /2\. Pat II/);
  } finally {
    await display.close();
  }
});
