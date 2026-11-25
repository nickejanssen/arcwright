import assert from "node:assert/strict";
import test from "node:test";

import { SEAT_MAX_AGE_MS, createSeatStore } from "../src/api/seatStore.js";
import { memoryStorage } from "./helpers/dom.js";

const auth = { idToken: "id-1", refreshToken: "refresh-1", expiresAt: 5_000 };
const seat = {
  gameId: "game-1",
  joinCode: "K7QP",
  participantId: "p-1",
  characterId: "c-1",
  displayName: "Jordan",
  auth,
};

function storeAt(clock: { now: number }, storage = memoryStorage()) {
  return {
    storage,
    store: createSeatStore(
      () => storage,
      () => clock.now,
    ),
  };
}

test("a saved seat is found by game, by code (any case) and as the most recent", () => {
  const clock = { now: 1_000 };
  const { store } = storeAt(clock);
  store.save(seat);
  store.save({ ...seat, gameId: "game-2", joinCode: "ZZZZ" });
  clock.now = 2_000;
  store.touch("game-1");

  assert.equal(store.get("game-1")?.displayName, "Jordan");
  assert.equal(store.findByCode("k7qp")?.gameId, "game-1");
  assert.equal(store.findByCode("NOPE"), null);
  assert.equal(store.mostRecent()?.gameId, "game-1");
});

test("a seat older than three days is deleted when it is met", () => {
  const clock = { now: 1_000 };
  const { store, storage } = storeAt(clock);
  store.save(seat);

  clock.now = 1_000 + SEAT_MAX_AGE_MS - 1;
  assert.ok(store.get("game-1"));

  clock.now = 1_000 + SEAT_MAX_AGE_MS + 1;
  assert.equal(store.get("game-1"), null);
  assert.equal(
    storage.length,
    0,
    "the stale entry is removed, not just hidden",
  );
});

test("a corrupt entry is deleted and ignored", () => {
  const clock = { now: 1_000 };
  const { store, storage } = storeAt(clock);
  storage.setItem("arcwright.seat.game-9", "{not json");
  storage.setItem("arcwright.seat.game-8", JSON.stringify({ gameId: "x" }));

  assert.equal(store.get("game-9"), null);
  assert.equal(store.mostRecent(), null);
  assert.equal(storage.length, 0);
});

test("refreshing a token keeps the seat's own time; clear removes it", () => {
  const clock = { now: 1_000 };
  const { store } = storeAt(clock);
  store.save(seat);
  clock.now = 9_000;
  store.updateAuth("game-1", { ...auth, idToken: "id-2" });

  const kept = store.get("game-1");
  assert.equal(kept?.auth.idToken, "id-2");
  assert.equal(kept?.savedAt, 1_000);

  store.clear("game-1");
  assert.equal(store.get("game-1"), null);
});

test("a storage that throws leaves the store empty instead of breaking", () => {
  const store = createSeatStore(() => {
    throw new Error("storage blocked");
  });
  store.save(seat);
  assert.equal(store.get("game-1"), null);
  assert.equal(store.mostRecent(), null);
});

test("only seat entries are read, and nothing else is stored with them", () => {
  const clock = { now: 1_000 };
  const { store, storage } = storeAt(clock);
  storage.setItem("arcwright.settings", "{}");
  store.save(seat);
  assert.deepEqual(
    Object.keys(JSON.parse(storage.getItem("arcwright.seat.game-1")!)).sort(),
    [
      "auth",
      "characterId",
      "displayName",
      "gameId",
      "joinCode",
      "participantId",
      "savedAt",
    ],
  );
  assert.equal(store.mostRecent()?.gameId, "game-1");
});
