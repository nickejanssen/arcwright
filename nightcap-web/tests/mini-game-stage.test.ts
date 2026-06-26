// Confirms the three host pages embed the mini-game stage section and the
// browser-entry script tag. These assertions guard against the stage being
// dropped from a page during a future refactor.

import assert from "node:assert/strict";
import test from "node:test";

import {
  renderHostPage,
  renderPlayerJoinPage,
  renderSharedDisplayPage,
} from "../src/ui.js";
import {
  renderMiniGameScriptTag,
  renderMiniGameStage,
} from "../src/mini-games/stage.js";

test("host page embeds the host surface stage and the entry script", () => {
  const html = renderHostPage("session-x");
  assert.ok(
    html.includes("data-mini-game-stage"),
    "expected host page to contain data-mini-game-stage",
  );
  assert.ok(
    html.includes('data-surface="host"'),
    "expected host page to declare data-surface=host",
  );
  assert.ok(
    html.includes(renderMiniGameScriptTag()),
    "expected host page to include the mini-games script tag",
  );
});

test("shared display page embeds the shared display stage", () => {
  const html = renderSharedDisplayPage("session-x");
  assert.ok(html.includes("data-mini-game-stage"));
  assert.ok(html.includes('data-surface="shared_display"'));
  assert.ok(html.includes(renderMiniGameScriptTag()));
});

test("player join page embeds the phone surface stage", () => {
  const html = renderPlayerJoinPage("session-x", "token");
  assert.ok(html.includes("data-mini-game-stage"));
  assert.ok(html.includes('data-surface="phone"'));
  assert.ok(html.includes(renderMiniGameScriptTag()));
});

test("renderMiniGameStage emits idle state by default", () => {
  const stage = renderMiniGameStage("phone");
  assert.ok(stage.includes('data-mini-game-state="idle"'));
  assert.ok(stage.includes('data-surface="phone"'));
});
