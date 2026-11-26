import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import test from "node:test";
import { Window } from "happy-dom";
import { mountRoom } from "../src/standalone-battle-of-wits";

test("two phone views join, show private state, and reconnect independently", async () => {
  const html = await readFile(
    resolve(process.env.DASHBOARD_DIR ?? "dashboard", "standalone/index.html"),
    "utf8",
  );
  const requests: string[] = [];
  const view = (token: string) => ({
    players: ["River", "Kit"],
    definition: { game_id: "battle-of-wits", version: "0.1.0" },
    game: {
      runId: "test-round",
      gameId: "battle-of-wits",
      status: "active",
      deadlineAt: new Date(Date.now() + 12000).toISOString(),
      mySubmissions: [],
      runtimeState: {
        stage: {
          phase: "question",
          index: 0,
          total: 3,
          kind: "choice",
          prompt: token === "River" ? "River's state" : "Kit's state",
          options: [{ id: "one", label: "One" }],
        },
        player: {},
      },
    },
  });
  function makePhone() {
    const window = new Window({ url: "http://192.0.2.15:8765" });
    window.document.write(html);
    const root = window.document.querySelector("main")!;
    const fetcher: typeof fetch = async (input, init) => {
      const path = String(input);
      const token = new Headers(init?.headers)
        .get("Authorization")
        ?.replace("Bearer ", "");
      if (path === "/api/join") {
        const { name } = JSON.parse(String(init?.body));
        return Response.json({
          token: name,
          character_id: name + "-character",
          participant_id: name + "-participant",
        });
      }
      assert.ok(token);
      requests.push(token);
      if (path === "/api/answer") {
        return Response.json({ submissionId: "saved", isAccepted: true });
      }
      return Response.json(view(token));
    };
    const mount = () => mountRoom(root as unknown as HTMLElement, fetcher);
    return { window, root, mount };
  }
  const phones = [makePhone(), makePhone()];
  const close = phones.map((phone) => phone.mount());
  try {
    for (const [i, name] of ["River", "Kit"].entries()) {
      const { root, window } = phones[i];
      root.querySelector("input")!.value = name;
      root.querySelector("form")!.dispatchEvent(new window.Event("submit"));
    }
    await new Promise((done) => setTimeout(done, 25));
    assert.match(phones[0].root.textContent, /River's state/);
    assert.doesNotMatch(phones[0].root.textContent, /Kit's state/);
    assert.match(phones[1].root.textContent, /Kit's state/);
    close[0]();
    close[0] = phones[0].mount();
    await new Promise((done) => setTimeout(done, 25));
    assert.match(phones[0].root.textContent, /River's state/);
    assert.deepEqual(requests, ["River", "Kit", "River"]);
  } finally {
    for (const stop of close) stop();
    for (const { window } of phones) await window.happyDOM.close();
  }
});
