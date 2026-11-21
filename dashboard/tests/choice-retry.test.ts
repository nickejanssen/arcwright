// A dropped choice is sent again with the same choice_id, so the engine
// records one effect (spec 0093 gives a repeated ID one effect). A tap on a
// seen item is a new free read and gets a new ID.

import assert from "node:assert/strict";
import test from "node:test";

import { createElement } from "react";
import { createChoiceTracker, createPlayerApi } from "../src/api/player.js";
import InvestigatePhone from "../src/screens/round/InvestigatePhone.js";
import { mount } from "./helpers/dom.js";
import {
  ME,
  fakeEngine,
  lobby,
  round,
  withFetch,
} from "./helpers/round-fixtures.js";

test("an unanswered choice is resent with the same ID and has one effect", async () => {
  const engine = fakeEngine({ budget: 4 });
  const api = createPlayerApi("g1", async () => "tok", engine.fetch);
  const tracker = createChoiceTracker();

  engine.dropAnswerOnce = true; // the engine processes it, the answer is lost
  const first = tracker.attempt("opp_internal_3");
  await assert.rejects(
    api.choose(first.choiceId, first.opportunityId),
    TypeError,
  );
  assert.equal(
    engine.effects.length,
    1,
    "the engine did process the first send",
  );

  const retry = tracker.attempt("opp_internal_3");
  assert.equal(retry.choiceId, first.choiceId, "same ID on the retry");
  const answer = await api.choose(retry.choiceId, retry.opportunityId);
  tracker.answered();
  assert.equal(answer.replayed, true);
  assert.equal(engine.effects.length, 1, "still one effect after the retry");
  assert.equal(engine.budget, 3, "spent once");
  assert.equal(answer.remainingBudget, 3);
});

test("a tap on a seen item after an answer uses a new ID", async () => {
  const engine = fakeEngine({ budget: 4 });
  const api = createPlayerApi("g1", async () => "tok", engine.fetch);
  const tracker = createChoiceTracker();

  const first = tracker.attempt("opp_internal_2"); // already seen
  await api.choose(first.choiceId, first.opportunityId);
  tracker.answered();

  const second = tracker.attempt("opp_internal_2");
  assert.notEqual(second.choiceId, first.choiceId, "a new free read, a new ID");
  await api.choose(second.choiceId, second.opportunityId);
  tracker.answered();
  assert.equal(engine.effects.length, 2);
  assert.equal(engine.budget, 4, "reading again cost nothing");
});

test("a different item after an unanswered one gets its own ID", () => {
  const tracker = createChoiceTracker();
  const a = tracker.attempt("opp_internal_1");
  const b = tracker.attempt("opp_internal_3");
  assert.notEqual(a.choiceId, b.choiceId);
});

test("on the screen, a dropped send keeps the confirm and the retry reuses the ID", async () => {
  const engine = fakeEngine({ budget: 4 });
  await withFetch(engine, async () => {
    const page = await mount(
      createElement(InvestigatePhone, {
        sessionId: "game-uuid-1111",
        lobby: lobby(),
        round: round({ phase: "choices" }),
        seat: { participantId: ME, displayName: "Jordan" },
        getToken: async () => "tok",
      }),
    );
    await page.clickContaining("Search the desk");
    engine.dropAnswerOnce = true;
    await page.click("Spend it");
    assert.ok(page.text().includes("That did not work. Try again."));
    assert.ok(
      page.buttons().some((b) => b.textContent?.trim() === "Spend it"),
      "the choice is kept so it can be sent again",
    );

    await page.click("Spend it");
    const sends = engine.calls.filter((c) => c.path.endsWith("/me/choices"));
    assert.equal(sends.length, 2);
    assert.equal(
      sends[0].body?.choice_id,
      sends[1].body?.choice_id,
      "same choice_id",
    );
    assert.equal(engine.effects.length, 1, "one effect");
    assert.equal(engine.budget, 3);
    assert.ok(page.text().includes("A torn page is wedged behind the drawer."));
    assert.ok(page.text().includes("3 left"));
    await page.unmount();
  });
});
