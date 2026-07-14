import assert from "node:assert/strict";
import test from "node:test";

import {
  isSharedDisplayVisibleEvent,
  SHARED_DISPLAY_VISIBLE_AUDIENCES,
} from "../src/filters.js";
import {
  getSharedDisplayEventBody,
  getSharedDisplayEventLabel,
  getSharedDisplayPresentationHintTokens,
  getPlayerEventBody,
  getPlayerEventLabel,
  renderHostPage,
  renderPlayerJoinPage,
  renderSharedDisplayPage,
} from "../src/ui.js";
import {
  HOST_SEED_PROMPTS,
  PLAYER_JOIN_PROMPTS,
} from "../src/personalization.js";

test("shared display body prefers narrator and group-visible text payloads", () => {
  assert.equal(
    getSharedDisplayEventBody({
      event_type: "narrator_bridge",
      payload: { text: "The room falls silent." },
    }),
    "The room falls silent.",
  );

  assert.equal(
    getSharedDisplayEventBody({
      event_type: "clue_acknowledged",
      payload: { message: "A clue has been passed to Rowan." },
    }),
    "A clue has been passed to Rowan.",
  );

  assert.equal(
    getSharedDisplayEventBody({
      event_type: "group_update",
      payload: { summary: "The group is circling the kitchen." },
    }),
    "The group is circling the kitchen.",
  );

  assert.equal(
    getSharedDisplayEventBody({
      event_type: "clue_acknowledged",
      payload: { clue_id: "clue-7", note: "private" },
    }),
    "A private event was shared.",
  );
});

test("player body preserves private payload text and raw structured payloads", () => {
  assert.equal(
    getPlayerEventBody({
      event_type: "clue_delivery",
      payload: { text: "Keep this clue private." },
    }),
    "Keep this clue private.",
  );

  assert.equal(
    getPlayerEventBody({
      event_type: "clue_delivery",
      payload: { clue_id: "clue-7", note: "private" },
    }),
    JSON.stringify({ clue_id: "clue-7", note: "private" }, null, 2),
  );

  assert.equal(
    getPlayerEventBody({
      event_type: "clue_delivery",
      payload: "Do not share this.",
    } as never),
    "Do not share this.",
  );
});

test("shared display presentation hints stay display-only", () => {
  assert.deepEqual(
    getSharedDisplayPresentationHintTokens({
      emotion: "tense",
      urgency: "high",
      voice_hint: "low and hushed",
      animation_hint: "slow fade",
      lighting_hint: "blue wash",
      pause_before_ms: 1500,
    }),
    [
      "emotion: tense",
      "urgency: high",
      "voice: low and hushed",
      "animation: slow fade",
      "lighting: blue wash",
      "pause: 1500ms",
    ],
  );

  assert.deepEqual(
    getSharedDisplayPresentationHintTokens({
      emotion: null,
      urgency: null,
      voice_hint: null,
      animation_hint: null,
      lighting_hint: null,
      pause_before_ms: 0,
    }),
    [],
  );
});

test("shared display page reuses the canonical audience list", () => {
  const html = renderSharedDisplayPage("session-123");

  assert.equal(
    SHARED_DISPLAY_VISIBLE_AUDIENCES.join(","),
    "all,shared_display",
  );
  assert.match(
    html,
    /const sharedDisplayVisibleAudiences = \["all","shared_display"\];/,
  );
  assert.match(html, /getSharedDisplayEventBody/);
  assert.match(html, /getSharedDisplayPresentationHintTokens/);
  assert.match(html, /getSharedDisplayEventLabel/);
  assert.ok(!html.includes("renderEventPayloadBody"));
});

test("shared display audience helper stays aligned with Arcwright routing", () => {
  assert.equal(isSharedDisplayVisibleEvent({ target_audience: "all" }), true);
  assert.equal(
    isSharedDisplayVisibleEvent({ target_audience: "shared_display" }),
    true,
  );
  assert.equal(
    isSharedDisplayVisibleEvent({ target_audience: "host_only" }),
    false,
  );
  assert.equal(
    isSharedDisplayVisibleEvent({ target_audience: "specific_player" }),
    false,
  );
});

test("shared display labels stay readable for narrator events", () => {
  assert.equal(
    getSharedDisplayEventLabel({
      category: "narrative",
      event_type: "narrator_bridge",
    }),
    "narrator bridge",
  );
});

test("player labels stay readable for private events", () => {
  assert.equal(
    getPlayerEventLabel({
      category: "private_delivery",
      event_type: "clue_delivery",
    }),
    "clue delivery",
  );
});

test("player join page exposes a join form and private player surface", () => {
  const html = renderPlayerJoinPage("session-123", "join-token-1");

  assert.match(html, /Join Nightcap/);
  assert.match(html, /Join code/);
  assert.match(html, /Quick personalization/);
  assert.match(html, /Answer the prompts, then tap Join\./);
  assert.match(html, /No character assigned yet/);
  assert.match(html, /player-input-form/);
  assert.match(html, /player-event-feed/);
  assert.match(html, /Private feed/);
  assert.match(html, /Private events stay on your device/);
  assert.match(html, /Retry feed/);
  assert.match(html, /Private character loaded\./);
  assert.match(html, /Your private feed and input stay on this device\./);
  assert.match(html, /auth\/exchange/);
  assert.match(html, /exchangeJoinTokenForBearerToken/);
  assert.ok(!html.includes("player_token: data.player.player_token"));
  assert.ok(!html.includes("JSON.stringify(character, null, 2)"));
  assert.ok(!html.includes("participant_id"));
  assert.ok(!html.includes("is_ai_controlled"));
  assert.ok(!html.includes("queueMicrotask(function()"));
  for (const prompt of PLAYER_JOIN_PROMPTS) {
    assert.ok(html.includes(prompt.label));
  }
});

test("player join page includes reconnect-safe session storage hooks", () => {
  const html = renderPlayerJoinPage("session-123", "");

  assert.match(html, /nightcap\.player\.active_session_id/);
  assert.match(html, /buildNightcapPlayerSessionStorageKey/);
  assert.match(html, /isNightcapPlayerSessionExpired/);
  assert.match(html, /Private feed connected\./);
  assert.match(html, /Your private session expired\. Rejoin to continue\./);
  assert.match(html, /resumeStoredSession/);
  assert.match(html, /expires_at/);
  assert.ok(!html.includes("renderEventPayloadBody"));
  assert.ok(!html.includes("getSharedDisplayEventLabel"));
});

test("player join page escapes dangerous tokens without inline script injection", () => {
  const html = renderPlayerJoinPage(
    "session-123",
    "join-token-1</script><img src=x onerror=alert(1)>",
  );

  assert.ok(
    html.includes(
      'value="join-token-1&lt;/script&gt;&lt;img src=x onerror=alert(1)&gt;"',
    ),
  );
  assert.ok(
    !html.includes("join-token-1</script><img src=x onerror=alert(1)>"),
  );
  assert.ok(!html.includes("initialSessionId"));
  assert.ok(!html.includes("initialJoinToken"));
});

test("host page renders the editable seed questions", () => {
  const html = renderHostPage("session-123");

  assert.match(html, /Group personalization/);
  for (const prompt of HOST_SEED_PROMPTS) {
    assert.ok(html.includes(prompt.label));
  }
});

test("host page phone sign-in rejects numbers outside the configured allowlist", () => {
  const htmlWithAllowlist = renderHostPage("session-123", {
    apiKey: "key",
    authDomain: "example.firebaseapp.com",
    projectId: "example",
    allowedTestPhoneNumbers: ["+16505551234"],
  });
  assert.match(
    htmlWithAllowlist,
    /const allowedTestPhoneNumbers = \["\+16505551234"\];/,
  );
  assert.match(
    htmlWithAllowlist,
    /allowedTestPhoneNumbers\.includes\(phoneNumber\)/,
  );

  const htmlWithoutAllowlist = renderHostPage("session-123");
  assert.match(htmlWithoutAllowlist, /const allowedTestPhoneNumbers = \[\];/);
});

test("host page persists and restores the exchanged host token across reload", () => {
  const html = renderHostPage("session-123");

  // Persisted on successful exchange, keyed to the session id + expiry —
  // not just an in-memory variable that a reload throws away.
  assert.match(html, /persistHostToken\(/);
  assert.match(html, /sessionStorage\.setItem\(hostTokenStorageKey/);
  // Restored inside onAuthStateChanged once Firebase confirms the signed-in
  // user, scoped to the session id already present in the URL/input.
  assert.match(html, /readPersistedHostToken\(existingSessionId\)/);
  // Cleared on sign-out so a stale token can't outlive the account session.
  assert.match(html, /clearPersistedHostToken\(\)/);
});
