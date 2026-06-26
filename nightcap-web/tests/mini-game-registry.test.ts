import assert from "node:assert/strict";
import test from "node:test";

function expectThrows(fn: () => unknown, messagePattern: RegExp): void {
  let threw = false;
  try {
    fn();
  } catch (err) {
    threw = true;
    const message = err instanceof Error ? err.message : String(err);
    assert.match(message, messagePattern);
  }
  assert.equal(threw, true, "expected function to throw");
}

import {
  RendererRegistry,
  defaultRegistry,
} from "../src/mini-games/registry.js";
import type {
  MiniGameRenderer,
  SurfaceLifecycle,
} from "../src/mini-game-kit/index.js";

function makeRenderer(gameId: string): MiniGameRenderer {
  return {
    gameId,
    mount(): SurfaceLifecycle {
      return {
        update: () => {},
        handleEvent: () => {},
        unmount: () => {},
      };
    },
  };
}

test("registry: register and get returns the renderer", () => {
  const registry = new RendererRegistry();
  const renderer = makeRenderer("fixture-individual");
  registry.register(renderer);
  assert.equal(registry.get("fixture-individual"), renderer);
});

test("registry: has reports presence", () => {
  const registry = new RendererRegistry();
  registry.register(makeRenderer("fixture-individual"));
  assert.equal(registry.has("fixture-individual"), true);
  assert.equal(registry.has("not-a-game"), false);
});

test("registry: get throws on unknown gameId with explanatory message", () => {
  const registry = new RendererRegistry();
  expectThrows(
    () => registry.get("missing"),
    /No renderer registered for game: missing/,
  );
});

test("registry: duplicate registration throws", () => {
  const registry = new RendererRegistry();
  registry.register(makeRenderer("fixture-individual"));
  expectThrows(
    () => registry.register(makeRenderer("fixture-individual")),
    /Renderer already registered for game: fixture-individual/,
  );
});

test("registry: list returns all registered gameIds", () => {
  const registry = new RendererRegistry();
  registry.register(makeRenderer("fixture-individual"));
  registry.register(makeRenderer("fixture-group"));
  assert.deepEqual(registry.list().sort(), [
    "fixture-group",
    "fixture-individual",
  ]);
});

test("registry: clear empties the registry", () => {
  const registry = new RendererRegistry();
  registry.register(makeRenderer("fixture-individual"));
  registry.clear();
  assert.equal(registry.has("fixture-individual"), false);
});

test("registry: defaultRegistry is a usable singleton", () => {
  defaultRegistry.clear();
  defaultRegistry.register(makeRenderer("sentinel"));
  assert.equal(defaultRegistry.has("sentinel"), true);
  defaultRegistry.clear();
});
