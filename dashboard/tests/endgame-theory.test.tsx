import assert from "node:assert/strict";
import test from "node:test";
import { act, createElement } from "react";
import { endgameScreens } from "../src/screens/endgame/index.js";
import { mount, settle } from "./helpers/dom.js";
import { lobby, round, ME } from "./helpers/round-fixtures.js";

function formResponse(overrides: Record<string, unknown> = {}) {
  return {
    open: true,
    phase_entry: 7,
    deadline_at: null,
    seconds_left: 20,
    slots: [
      {
        slot_id: "s1",
        label: "First",
        kind: "cast",
        options: [{ value: "a", label: "Alpha", text: null }],
      },
      {
        slot_id: "s2",
        label: "Second",
        kind: "concept",
        options: [{ value: "b", label: "Beta", text: null }],
      },
    ],
    account: [],
    proof_options: [],
    theory: { state: "none", answers: {}, proof: null, revision: 0 },
    ...overrides,
  };
}

test("without an account the phone renders every slot in route order", async () => {
  const previous = globalThis.fetch;
  globalThis.fetch = async () => new Response(JSON.stringify(formResponse()));
  const Screen = endgameScreens.commit.phone!;
  const page = await mount(
    createElement(Screen, {
      sessionId: "game",
      lobby: lobby(),
      round: round({ phase: "commit" }),
      seat: { participantId: ME, displayName: "Jordan" },
      getToken: async () => "token",
    }),
  );
  try {
    const labels = Array.from(page.container.querySelectorAll("select")).map(
      (item) => item.getAttribute("aria-label"),
    );
    assert.deepEqual(labels, ["First", "Second", "Proof"]);
    assert.equal(page.button("Lock my theory").disabled, true);
  } finally {
    await page.unmount();
    globalThis.fetch = previous;
  }
});

test("a failed initial read can be retried and restored", async () => {
  const previous = globalThis.fetch;
  let count = 0;
  globalThis.fetch = async () =>
    ++count === 1
      ? new Response("", { status: 503 })
      : new Response(JSON.stringify(formResponse()));
  const Screen = endgameScreens.commit.phone!;
  const page = await mount(
    createElement(Screen, {
      sessionId: "game",
      lobby: lobby(),
      round: round({ phase: "commit" }),
      seat: { participantId: ME, displayName: "Jordan" },
      getToken: async () => "token",
    }),
  );
  try {
    assert.match(page.text(), /That did not work/);
    await page.click("Try again");
    assert.ok(page.container.querySelector('select[aria-label="First"]'));
    assert.doesNotMatch(page.text(), /That did not work/);
  } finally {
    await page.unmount();
    globalThis.fetch = previous;
  }
});

test("a closed no-theory form explains its state and cannot be edited", async () => {
  const previous = globalThis.fetch;
  globalThis.fetch = async () =>
    new Response(
      JSON.stringify(
        formResponse({
          open: false,
          theory: { state: "no_theory", answers: {}, proof: null, revision: 0 },
        }),
      ),
    );
  const Screen = endgameScreens.commit.phone!;
  const page = await mount(
    createElement(Screen, {
      sessionId: "game",
      lobby: lobby(),
      round: round({ phase: "commit" }),
      seat: { participantId: ME, displayName: "Jordan" },
      getToken: async () => "token",
    }),
  );
  try {
    assert.match(page.text(), /No theory was locked/);
    assert.ok(
      Array.from(page.container.querySelectorAll("select")).every(
        (item) => item.disabled,
      ),
    );
  } finally {
    await page.unmount();
    globalThis.fetch = previous;
  }
});

test("a delayed old read cannot replace the newer locked state", async () => {
  const previous = globalThis.fetch;
  let release!: (response: Response) => void;
  const pending = new Promise<Response>((resolve) => {
    release = resolve;
  });
  let reads = 0;
  globalThis.fetch = async () =>
    ++reads === 1
      ? pending
      : new Response(
          JSON.stringify(
            formResponse({
              theory: {
                state: "locked",
                answers: { s1: "a", s2: "b" },
                proof: null,
                revision: 2,
              },
            }),
          ),
        );
  const Screen = endgameScreens.commit.phone!;
  const token = async () => "token";
  const props = {
    sessionId: "game",
    lobby: lobby(),
    seat: { participantId: ME, displayName: "Jordan" },
    getToken: token,
  };
  const page = await mount(
    createElement(Screen, { ...props, round: round({ phase: "commit" }) }),
  );
  try {
    await page.rerender(
      createElement(Screen, {
        ...props,
        round: round({
          phase: "commit",
          players: [
            { participantId: ME, name: "Jordan", ready: false, locked: true },
          ],
        }),
      }),
    );
    assert.match(page.text(), /Locked\. Waiting/);
    await act(async () => {
      release(new Response(JSON.stringify(formResponse())));
    });
    await settle();
    assert.match(page.text(), /Locked\. Waiting/);
    assert.ok(
      Array.from(page.container.querySelectorAll("select")).every(
        (item) => item.disabled,
      ),
    );
  } finally {
    await page.unmount();
    globalThis.fetch = previous;
  }
});

test("theory account, options and proof follow the private route's order", async () => {
  const previous = globalThis.fetch;
  try {
    for (const labels of [
      ["Zebra", "Apple"],
      ["Apple", "Zebra"],
    ]) {
      globalThis.fetch = async (input, init) => {
        assert.match(String(input), /\/me\/theory$/);
        assert.equal(
          (init?.headers as Record<string, string>).Authorization,
          "Bearer private-token",
        );
        return new Response(
          JSON.stringify({
            open: true,
            phase_entry: 7,
            deadline_at: null,
            seconds_left: 102,
            slots: [
              {
                slot_id: "secret-slot",
                label: "Person",
                kind: "cast",
                options: labels.map((label) => ({
                  value: label,
                  label,
                  text: null,
                })),
              },
            ],
            account: [
              { text: "Placeholder account ", slot_id: null },
              { text: "", slot_id: "secret-slot" },
            ],
            proof_options: [
              {
                value: "secret-proof",
                label: "Placeholder proof",
                text: "Proof text",
              },
            ],
            theory: { state: "none", answers: {}, proof: null, revision: 0 },
          }),
        );
      };
      const Screen = endgameScreens.commit?.phone;
      assert.ok(Screen, "the commit phase has a phone screen");
      const page = await mount(
        createElement(Screen, {
          sessionId: "game-uuid-1111",
          lobby: lobby(),
          round: round({ phase: "commit" }),
          seat: { participantId: ME, displayName: "Jordan" },
          getToken: async () => "private-token",
        }),
      );
      try {
        assert.match(page.text(), /Placeholder account/);
        assert.match(page.text(), /Proof/);
        assert.ok(
          page.text().indexOf(labels[0]) < page.text().indexOf(labels[1]),
        );
        assert.match(page.text(), /Placeholder proof/);
        assert.doesNotMatch(page.text(), /secret-slot|secret-proof/);
      } finally {
        await page.unmount();
      }
    }
  } finally {
    globalThis.fetch = previous;
  }
});

test("saving, confirming and locking a theory use the player's private route", async () => {
  const previous = globalThis.fetch;
  let theory = {
    state: "none",
    answers: {} as Record<string, string>,
    proof: null as string | null,
    revision: 0,
  };
  const calls: string[] = [];
  globalThis.fetch = async (input, init) => {
    const path = String(input);
    const method = init?.method ?? "GET";
    calls.push(`${method} ${path}`);
    assert.equal(
      (init?.headers as Record<string, string>).Authorization,
      "Bearer private-token",
    );
    if (method === "PUT") {
      const body = JSON.parse(String(init?.body)) as {
        answers: Record<string, string>;
        proof: string | null;
      };
      theory = { ...body, state: "drafting", revision: theory.revision + 1 };
      return new Response(JSON.stringify(theory));
    }
    if (method === "POST") {
      theory = { ...theory, state: "locked" };
      return new Response(JSON.stringify(theory));
    }
    return new Response(
      JSON.stringify({
        open: true,
        phase_entry: 7,
        deadline_at: null,
        seconds_left: 102,
        slots: [
          {
            slot_id: "slot",
            label: "Person",
            kind: "cast",
            options: [{ value: "a", label: "Alex", text: null }],
          },
        ],
        account: [
          { text: "Placeholder ", slot_id: null },
          { text: "", slot_id: "slot" },
        ],
        proof_options: [{ value: "p", label: "Piece", text: "Placeholder" }],
        theory,
      }),
    );
  };
  const Screen = endgameScreens.commit.phone!;
  const page = await mount(
    createElement(Screen, {
      sessionId: "game",
      lobby: lobby(),
      round: round({ phase: "commit" }),
      seat: { participantId: ME, displayName: "Jordan" },
      getToken: async () => "private-token",
    }),
  );
  try {
    assert.equal(page.button("Lock my theory").disabled, true);
    const select = page.container.querySelector(
      'select[aria-label="Person"]',
    ) as HTMLSelectElement;
    await act(async () => {
      select.value = "a";
      select.dispatchEvent(new Event("change", { bubbles: true }));
    });
    await settle();
    assert.deepEqual(theory.answers, { slot: "a" });
    const proof = page.container.querySelector(
      'select[aria-label="Proof"]',
    ) as HTMLSelectElement;
    await act(async () => {
      proof.value = "p";
      proof.dispatchEvent(new Event("change", { bubbles: true }));
    });
    await settle();
    assert.equal(theory.proof, "p");
    await page.click("Lock my theory");
    assert.match(page.text(), /Lock it\?/);
    assert.ok(!calls.some((call) => call.startsWith("POST")));
    await act(async () => {
      proof.value = "";
      proof.dispatchEvent(new Event("change", { bubbles: true }));
    });
    await settle();
    assert.doesNotMatch(page.text(), /Lock it\?/);
    await page.click("Lock my theory");
    await page.click("Lock my theory");
    assert.match(page.text(), /Locked\. Waiting for the others/);
    assert.equal(
      (
        page.container.querySelector(
          'select[aria-label="Person"]',
        ) as HTMLSelectElement
      ).disabled,
      true,
    );
    assert.ok(calls.includes("POST /v1/sessions/game/me/theory/lock"));
  } finally {
    await page.unmount();
    globalThis.fetch = previous;
  }
});

test("a reconnect restores a locked theory without allowing edits", async () => {
  const previous = globalThis.fetch;
  globalThis.fetch = async () =>
    new Response(
      JSON.stringify({
        open: true,
        phase_entry: 7,
        deadline_at: null,
        seconds_left: 20,
        slots: [
          {
            slot_id: "slot",
            label: "Person",
            kind: "cast",
            options: [{ value: "a", label: "Alex", text: null }],
          },
        ],
        account: [
          { text: "Placeholder ", slot_id: null },
          { text: "", slot_id: "slot" },
        ],
        proof_options: [{ value: "p", label: "Piece", text: "Placeholder" }],
        theory: {
          state: "locked",
          answers: { slot: "a" },
          proof: "p",
          revision: 2,
        },
      }),
    );
  const Screen = endgameScreens.commit.phone!;
  const page = await mount(
    createElement(Screen, {
      sessionId: "game",
      lobby: lobby(),
      round: round({ phase: "commit" }),
      seat: { participantId: ME, displayName: "Jordan" },
      getToken: async () => "private-token",
    }),
  );
  try {
    assert.match(page.text(), /Locked\. Waiting for the others/);
    assert.equal(
      (
        page.container.querySelector(
          'select[aria-label="Person"]',
        ) as HTMLSelectElement
      ).value,
      "a",
    );
    assert.equal(
      (
        page.container.querySelector(
          'select[aria-label="Proof"]',
        ) as HTMLSelectElement
      ).value,
      "p",
    );
    assert.ok(
      Array.from(page.container.querySelectorAll("select")).every(
        (item) => item.disabled,
      ),
    );
    assert.equal(
      page.buttons().some((button) => button.textContent === "Lock my theory"),
      false,
    );
  } finally {
    await page.unmount();
    globalThis.fetch = previous;
  }
});
