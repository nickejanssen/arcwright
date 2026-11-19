// Acceptance 1: sign-in kept across a closed tab. The join page resumes a
// stored seat without calling lobby-join, so no second seat is made.

import assert from "node:assert/strict";
import test from "node:test";

import { createElement } from "react";
import { ApiError, JoinError } from "../src/api/lobby.js";
import type { LobbyJoinResult, LobbyState } from "../src/api/lobby.js";
import { createSeatStore } from "../src/api/seatStore.js";
import { mount, memoryStorage, typeInto } from "./helpers/dom.js";
import JoinScreen from "../src/screens/JoinScreen.js";

const auth = { idToken: "id", refreshToken: "refresh", expiresAt: 9e12 };

function lobby(status: string): LobbyState {
  return {
    session_id: "game-1",
    join_code: "K7QP",
    status,
    current_beat_id: "beat_internal_1",
    is_terminal: false,
    min_players: 2,
    player_count: 1,
    players: [],
  };
}

function setup(fetchLobby: (id: string) => Promise<LobbyState>) {
  const storage = memoryStorage();
  const store = createSeatStore(() => storage);
  const calls = { join: 0, navigate: [] as string[] };
  const deps = {
    store,
    fetchLobby,
    join: async (): Promise<LobbyJoinResult> => {
      calls.join += 1;
      return {
        participant_id: "p-new",
        session_id: "game-1",
        display_name: "Jordan",
        character_id: "c-new",
        player_token: "custom-token",
      };
    },
    exchange: async () => auth,
    navigate: (path: string) => void calls.navigate.push(path),
  };
  return { store, storage, calls, deps };
}

function save(store: ReturnType<typeof createSeatStore>) {
  store.save({
    gameId: "game-1",
    joinCode: "K7QP",
    participantId: "p-1",
    characterId: "c-1",
    displayName: "Jordan",
    auth,
  });
}

test("a closed and reopened tab goes straight to the phone page without joining again", async () => {
  const { store, calls, deps } = setup(async () => lobby("active"));
  save(store);

  const page = await mount(createElement(JoinScreen, { code: "k7qp", deps }));

  assert.deepEqual(calls.navigate, ["/play"]);
  assert.equal(calls.join, 0, "lobby-join is never called for a held seat");
  assert.ok(!page.text().includes("Join"), "the form does not flash");
  await page.unmount();
});

test("a link with no code resumes the most recent seat", async () => {
  const { store, calls, deps } = setup(async () => lobby("created"));
  save(store);

  const page = await mount(createElement(JoinScreen, { deps }));
  assert.deepEqual(calls.navigate, ["/play"]);
  await page.unmount();
});

test("a different code shows the form and leaves the other seat alone", async () => {
  const { store, calls, deps } = setup(async () => lobby("active"));
  save(store);

  const page = await mount(createElement(JoinScreen, { code: "OTHR", deps }));
  assert.deepEqual(calls.navigate, []);
  assert.ok(page.button("Join"));
  assert.ok(store.get("game-1"), "the held seat is untouched");
  await page.unmount();
});

test("a game that no longer exists clears the seat and shows the form", async () => {
  const { store, deps, calls } = setup(async () => {
    throw new ApiError("gone", 404);
  });
  save(store);

  const page = await mount(createElement(JoinScreen, { code: "K7QP", deps }));
  assert.equal(store.get("game-1"), null);
  assert.deepEqual(calls.navigate, []);
  assert.ok(page.button("Join"));
  await page.unmount();
});

test("a finished game clears the seat and shows the form", async () => {
  const { store, deps } = setup(async () => lobby("completed"));
  save(store);

  const page = await mount(createElement(JoinScreen, { deps }));
  assert.equal(store.get("game-1"), null);
  assert.ok(page.button("Join"));
  await page.unmount();
});

test("an engine that cannot be reached keeps the seat and goes to the phone page", async () => {
  const { store, calls, deps } = setup(async () => {
    throw new Error("network down");
  });
  save(store);

  const page = await mount(createElement(JoinScreen, { deps }));
  assert.deepEqual(calls.navigate, ["/play"]);
  assert.ok(store.get("game-1"));
  await page.unmount();
});

test("joining stores the seat and opens the phone page with no ID in the address", async () => {
  const { store, calls, deps } = setup(async () => lobby("created"));
  const page = await mount(createElement(JoinScreen, { code: "k7qp", deps }));

  await typeInto(
    page.container.querySelector("#name") as HTMLInputElement,
    "Jordan",
  );
  await page.click("Join");

  assert.equal(calls.join, 1);
  assert.deepEqual(calls.navigate, ["/play"]);
  const kept = store.get("game-1");
  assert.equal(kept?.displayName, "Jordan");
  assert.equal(kept?.joinCode, "K7QP");
  await page.unmount();
});

test("a refused join says why, in plain words", async () => {
  for (const [failure, words] of [
    ["bad_code", "That code did not work. Check the TV."],
    ["started", "This game has started. Use the phone you joined with."],
  ] as const) {
    const { deps } = setup(async () => lobby("created"));
    deps.join = async () => {
      throw new JoinError(failure, 409);
    };
    const page = await mount(createElement(JoinScreen, { code: "K7QP", deps }));
    await typeInto(
      page.container.querySelector("#name") as HTMLInputElement,
      "Jordan",
    );
    await page.click("Join");
    assert.ok(page.text().includes(words), `shows: ${words}`);
    await page.unmount();
  }
});
