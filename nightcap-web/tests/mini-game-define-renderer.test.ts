// Verifies defineRenderer with a sample renderer that exercises the same
// shape every real fixture renderer uses: mount() returns a lifecycle,
// update() rewrites the DOM, handleEvent() reacts to events, unmount()
// cleans up. happy-dom is used to give us a real DOM in node.

import assert from "node:assert/strict";
import test from "node:test";
import { Window as HappyWindow } from "happy-dom";

import {
  defineRenderer,
  el,
  setText,
  clearChildren,
  type MiniGameContext,
  type SurfaceLifecycle,
} from "../src/mini-game-kit/index.js";
import type { MiniGameDefinition } from "../src/mini-game-kit/index.js";
import type {
  ContentEvent,
  MiniGameState,
  MiniGameSubmissionResult,
} from "../src/types.js";

function makeDefinition(): MiniGameDefinition {
  return {
    schema_version: "1.0",
    game_id: "test-game",
    version: "0.1.0",
    mechanic_type: "timed-choice",
    participation_mode: "individual",
    content_mode: "authored",
    min_players: 1,
    max_players: 10,
    duration_seconds: 30,
    rules: {},
    authored_content: { prompt: "Pick one", choices: ["a", "b"] },
    generation_constraints: null,
    behavioral_outputs: [],
    clue_fallback: {
      delay_seconds: 15,
      clue_variant: "reduced",
      host_override: true,
    },
  };
}

function makeState(overrides: Partial<MiniGameState> = {}): MiniGameState {
  return {
    runId: "run-1",
    gameId: "test-game",
    status: "active",
    deadlineAt: null,
    mySubmissions: [],
    ...overrides,
  };
}

function makeContext(
  doc: Document,
  state: MiniGameState,
  overrides: Partial<MiniGameContext> = {},
): MiniGameContext {
  void doc;
  return {
    surface: "phone",
    sessionId: "session-1",
    participantId: "p-1",
    characterId: "c-1",
    state,
    definition: makeDefinition(),
    submit: async (): Promise<MiniGameSubmissionResult> => ({
      submissionId: "s-1",
      isAccepted: true,
    }),
    onEvent: () => () => {},
    reportPerf: () => {},
    ...overrides,
  };
}

test("defineRenderer: returns a renderer with the right gameId", () => {
  const renderer = defineRenderer({
    gameId: "test-game",
    phone: {
      mount(): SurfaceLifecycle {
        return {
          update: () => {},
          handleEvent: () => {},
          unmount: () => {},
        };
      },
    },
  });
  assert.equal(renderer.gameId, "test-game");
});

test("defineRenderer: missing surface mounts inert lifecycle", () => {
  const renderer = defineRenderer({ gameId: "test-game" });
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const root = doc.createElement("section");
  const lifecycle = renderer.mount(root, makeContext(doc, makeState()));
  // Should not throw on update/handleEvent/unmount.
  lifecycle.update(makeState({ status: "completed" }));
  lifecycle.handleEvent({} as ContentEvent);
  lifecycle.unmount();
});

test("defineRenderer: phone surface mounts and reacts to state changes", () => {
  const renderer = defineRenderer({
    gameId: "test-game",
    phone: {
      mount(root, ctx): SurfaceLifecycle {
        const doc = root.ownerDocument;
        const status = el(doc, "p", { "data-role": "status" }, [
          ctx.state.status,
        ]);
        const prompt = el(doc, "h2", { "data-role": "prompt" }, [
          (ctx.definition.authored_content as { prompt: string }).prompt,
        ]);
        root.appendChild(status);
        root.appendChild(prompt);
        return {
          update(state) {
            setText(status, state.status);
          },
          handleEvent() {},
          unmount() {
            clearChildren(root);
          },
        };
      },
    },
  });

  const window = new HappyWindow();
  const doc = window.document as unknown as Document;
  const root = doc.createElement("section");
  const lifecycle = renderer.mount(root, makeContext(doc, makeState()));

  assert.equal(
    root.querySelector('[data-role="status"]')?.textContent,
    "active",
  );
  assert.equal(
    root.querySelector('[data-role="prompt"]')?.textContent,
    "Pick one",
  );

  lifecycle.update(makeState({ status: "timed_out" }));
  assert.equal(
    root.querySelector('[data-role="status"]')?.textContent,
    "timed_out",
  );

  lifecycle.unmount();
  assert.equal(root.children.length, 0);
});

test("defineRenderer: surface is selected from context", () => {
  const renderer = defineRenderer({
    gameId: "test-game",
    phone: {
      mount(root): SurfaceLifecycle {
        root.setAttribute("data-mounted", "phone");
        return {
          update: () => {},
          handleEvent: () => {},
          unmount: () => {},
        };
      },
    },
    sharedDisplay: {
      mount(root): SurfaceLifecycle {
        root.setAttribute("data-mounted", "shared_display");
        return {
          update: () => {},
          handleEvent: () => {},
          unmount: () => {},
        };
      },
    },
  });
  const window = new HappyWindow();
  const doc = window.document as unknown as Document;

  const phoneRoot = doc.createElement("section");
  renderer.mount(
    phoneRoot,
    makeContext(doc, makeState(), { surface: "phone" }),
  );
  assert.equal(phoneRoot.getAttribute("data-mounted"), "phone");

  const sharedRoot = doc.createElement("section");
  renderer.mount(
    sharedRoot,
    makeContext(doc, makeState(), { surface: "shared_display" }),
  );
  assert.equal(sharedRoot.getAttribute("data-mounted"), "shared_display");
});
