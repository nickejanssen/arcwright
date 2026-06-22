import test from "node:test";
import assert from "node:assert/strict";

const DurableObjectStub = class {
  constructor(state: unknown, env: unknown) {
    void state;
    void env;
  }
};

// @ts-expect-error Node does not provide DurableObject at runtime.
globalThis.DurableObject = DurableObjectStub;

const { NightcapRoom } = await import("../src/room.js");

function createRoomState(roomId = "room-1") {
  const storage = new Map<string, unknown>();
  return {
    id: {
      toString: () => roomId,
    },
    storage: {
      async get<T>(key: string): Promise<T | undefined> {
        return storage.get(key) as T | undefined;
      },
      async put<T>(key: string, value: T): Promise<void> {
        storage.set(key, value);
      },
      async delete(key: string): Promise<void> {
        storage.delete(key);
      },
    },
  } as const;
}

async function readJson(response: Response): Promise<unknown> {
  return response.json();
}

test("NightcapRoom persists joins across room instances", async () => {
  const state = createRoomState();
  const env = { ARCWRIGHT_API_BASE_URL: "https://arcwright.test" };

  const room = new NightcapRoom(state as never, env);
  const joinResponse = await room.fetch(
    new Request("https://nightcap.test/rooms/session-1/join", {
      method: "POST",
      body: JSON.stringify({
        session_id: "session-1",
        client_id: "client-1",
        participant_id: "participant-1",
        role: "player",
      }),
    }),
  );

  assert.equal(joinResponse.status, 200);
  const joinBody = (await readJson(joinResponse)) as {
    snapshot: { member_count: number; session_id: string | null };
  };
  assert.equal(joinBody.snapshot.member_count, 1);
  assert.equal(joinBody.snapshot.session_id, "session-1");

  const restartedRoom = new NightcapRoom(state as never, env);
  const snapshotResponse = await restartedRoom.fetch(
    new Request("https://nightcap.test/rooms/session-1/snapshot", {
      method: "GET",
    }),
  );

  assert.equal(snapshotResponse.status, 200);
  const snapshotBody = (await readJson(snapshotResponse)) as {
    member_count: number;
    session_id: string | null;
    members: Array<{ client_id: string }>;
  };
  assert.equal(snapshotBody.member_count, 1);
  assert.equal(snapshotBody.session_id, "session-1");
  assert.equal(snapshotBody.members[0]?.client_id, "client-1");
});

test("NightcapRoom rejects malformed join payloads", async () => {
  const state = createRoomState("room-2");
  const env = { ARCWRIGHT_API_BASE_URL: "https://arcwright.test" };
  const room = new NightcapRoom(state as never, env);

  const response = await room.fetch(
    new Request("https://nightcap.test/rooms/session-2/join", {
      method: "POST",
      body: JSON.stringify({
        session_id: "",
        client_id: 123,
      }),
    }),
  );

  assert.equal(response.status, 400);
});
