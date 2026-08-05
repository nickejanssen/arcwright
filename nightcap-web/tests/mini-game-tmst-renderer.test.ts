import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { mkdir } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import test from "node:test";
import { build as esbuild } from "esbuild";
import { Window as HappyWindow } from "happy-dom";

import type {
  ContentEvent,
  MiniGameState,
  MiniGameSubmissionResult,
} from "../src/types.js";
import type {
  MiniGameContext,
  MiniGameDefinition,
  MiniGameRenderer,
  Surface,
} from "../src/mini-game-kit/index.js";

let rendererPromise: Promise<MiniGameRenderer> | null = null;

const nightcapWebRoot = [
  resolve("."),
  resolve("nightcap-web"),
  resolve("..", "nightcap-web"),
].find((candidate) =>
  existsSync(resolve(candidate, "src", "mini-game-kit", "index.ts")),
);

if (!nightcapWebRoot) {
  throw new Error("Could not locate nightcap-web source root");
}

const NIGHTCAP_WEB_ROOT = nightcapWebRoot;
const REPO_ROOT = resolve(NIGHTCAP_WEB_ROOT, "..");

async function loadRenderer(): Promise<MiniGameRenderer> {
  if (rendererPromise) return rendererPromise;
  rendererPromise = (async () => {
    const outfile = resolve(
      NIGHTCAP_WEB_ROOT,
      "dist",
      "tests",
      "tmst-renderer-bundle.mjs",
    );
    await mkdir(resolve(NIGHTCAP_WEB_ROOT, "dist", "tests"), {
      recursive: true,
    });
    await esbuild({
      entryPoints: [
        resolve(
          REPO_ROOT,
          "nightcap",
          "mini_games",
          "tell-me-something-true",
          "client",
          "renderer.ts",
        ),
      ],
      outfile,
      bundle: true,
      format: "esm",
      target: ["es2022"],
      platform: "browser",
      alias: {
        "@arcwright/mini-game-kit": resolve(
          NIGHTCAP_WEB_ROOT,
          "src",
          "mini-game-kit",
          "index.ts",
        ),
      },
      logLevel: "silent",
    });
    const mod = (await import(pathToFileURL(outfile).href)) as {
      default: MiniGameRenderer;
    };
    return mod.default;
  })();
  return rendererPromise;
}

function makeDefinition(): MiniGameDefinition {
  return {
    schema_version: "1.0",
    game_id: "tell-me-something-true",
    version: "0.1.0",
    mechanic_type: "social-truth-bluff",
    participation_mode: "group",
    content_mode: "hybrid",
    min_players: 4,
    max_players: 8,
    duration_seconds: 240,
    rules: {},
    authored_content: {
      phone_prompt: "Complete the private statement.",
    },
    generation_constraints: null,
    behavioral_outputs: [],
    clue_fallback: {
      delay_seconds: 30,
      clue_variant: "reduced",
      host_override: true,
    },
  };
}

function makeState(overrides: Partial<MiniGameState> = {}): MiniGameState {
  return {
    runId: "run-1",
    gameId: "tell-me-something-true",
    definitionVersion: "0.1.0",
    status: "active",
    deadlineAt: null,
    runtimeState: {},
    presentation: {
      title: "Tell Me Something True",
      prompt: "I once hid the ledger under ____.",
    },
    mySubmissions: [],
    ...overrides,
  };
}

function makeContext(
  surface: Surface,
  state: MiniGameState,
  submissions: unknown[] = [],
): MiniGameContext {
  return {
    surface,
    sessionId: "session-1",
    participantId: "p-1",
    characterId: "c-1",
    state,
    definition: makeDefinition(),
    submit: async (payload): Promise<MiniGameSubmissionResult> => {
      submissions.push(payload);
      return { submissionId: `sub-${submissions.length}`, isAccepted: true };
    },
    onEvent: () => () => {},
    reportPerf: () => {},
  };
}

function event(
  eventType: string,
  payload: Record<string, unknown>,
): ContentEvent {
  return {
    event_id: `event-${eventType}`,
    session_id: "session-1",
    timestamp: "2026-08-03T00:00:00Z",
    category: "system",
    event_type: eventType,
    actor_id: null,
    target_audience: "all",
    target_player_id: null,
    payload,
    presentation_hints: {
      emotion: null,
      urgency: null,
      voice_hint: null,
      animation_hint: null,
      lighting_hint: null,
      pause_before_ms: 0,
    },
    sequence_number: 1,
  };
}

test("tmst renderer: phone shows private prompt and submits engine-owned payload", async () => {
  const renderer = await loadRenderer();
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const root = doc.createElement("section");
  const submissions: unknown[] = [];
  const lifecycle = renderer.mount(
    root,
    makeContext("phone", makeState(), submissions),
  );

  lifecycle.handleEvent(
    event("tmst_private_prompt_ready", {
      phase: "input",
    }),
  );

  assert.match(root.textContent ?? "", /I once hid the ledger/);
  assert.match(root.textContent ?? "", /NON_AUTHORITATIVE_PREVIEW/);
  const input = root.querySelector<HTMLTextAreaElement>(
    '[data-role="statement-input"]',
  );
  if (!input) throw new Error("expected statement input");
  input.value = "the old piano";
  const truthButton = root.querySelector<HTMLButtonElement>(
    '[data-role="truth-action"]',
  );
  truthButton?.click();
  await new Promise((resolveDone) => setTimeout(resolveDone, 0));
  assert.deepEqual(submissions, [
    {
      action: "input",
      statement_text: "the old piano",
      declared_truth: true,
    },
  ]);
});

test("tmst renderer: shared display never renders private prompt payload", async () => {
  const renderer = await loadRenderer();
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const root = doc.createElement("section");
  const lifecycle = renderer.mount(
    root,
    makeContext("shared_display", makeState()),
  );

  lifecycle.handleEvent(
    event("tmst_private_prompt_ready", {
      phase: "input",
      prompt: "This private text must not appear.",
    }),
  );

  assert.doesNotMatch(root.textContent ?? "", /private text/i);
  assert.match(root.textContent ?? "", /NON_AUTHORITATIVE_PREVIEW/);
});

test("tmst renderer: phone vote prompt hides other players' vote choices", async () => {
  const renderer = await loadRenderer();
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const root = doc.createElement("section");
  const submissions: unknown[] = [];
  const lifecycle = renderer.mount(
    root,
    makeContext("phone", makeState(), submissions),
  );

  lifecycle.handleEvent(
    event("tmst_spotlight_started", {
      target_character_id: "character-2",
      spotlight_label: "Vesper",
      other_player_vote: "p-2 voted Truth",
    }),
  );

  assert.match(root.textContent ?? "", /Vesper: truth or lie/);
  assert.doesNotMatch(root.textContent ?? "", /p-2 voted Truth/);
  root.querySelector<HTMLButtonElement>('[data-role="vote-lie"]')?.click();
  await new Promise((resolveDone) => setTimeout(resolveDone, 0));
  assert.deepEqual(submissions, [
    {
      action: "vote",
      target_character_id: "character-2",
      vote: "lie",
    },
  ]);
});

test("tmst renderer: reduced motion is visible as state, not color only", async () => {
  const renderer = await loadRenderer();
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  Object.defineProperty(window, "matchMedia", {
    value: () => ({ matches: true }),
  });
  const root = doc.createElement("section");
  renderer.mount(root, makeContext("shared_display", makeState()));

  assert.equal(root.getAttribute("data-reduced-motion"), "true");
  assert.equal(
    root.getAttribute("data-authority"),
    "NON_AUTHORITATIVE_PREVIEW",
  );
});

test("tmst renderer: timeout and completed updates show preview fallback state", async () => {
  const renderer = await loadRenderer();
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const root = doc.createElement("section");
  const lifecycle = renderer.mount(
    root,
    makeContext("shared_display", makeState()),
  );

  lifecycle.update(makeState({ status: "timed_out" }));
  assert.match(root.textContent ?? "", /Fallback active/);

  lifecycle.update(makeState({ status: "completed" }));
  assert.match(root.textContent ?? "", /Final scoring remains engine-owned/);
});
