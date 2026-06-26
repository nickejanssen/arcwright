// Privacy matrix: for every (audience, surface) combination, verify that
// withAudienceGuard delivers or drops the event correctly. This is the
// defense-in-depth boundary; the primary boundary is the scoped player
// token Arcwright issues per surface.

import assert from "node:assert/strict";
import test from "node:test";

import { withAudienceGuard } from "../src/mini-game-kit/index.js";
import type { ContentEvent } from "../src/types.js";
import type { Surface } from "../src/mini-game-kit/index.js";

function ev(
  audience: ContentEvent["target_audience"],
  targetPlayer: string | null = null,
): ContentEvent {
  return {
    event_id: `evt-${audience}-${targetPlayer ?? "none"}`,
    session_id: "session-1",
    timestamp: "2026-06-25T00:00:00Z",
    category: "private_delivery",
    event_type: "fixture",
    actor_id: null,
    target_audience: audience,
    target_player_id: targetPlayer,
    payload: { secret: "do-not-leak" },
    presentation_hints: {
      emotion: null,
      urgency: null,
      voice_hint: null,
      animation_hint: null,
      lighting_hint: null,
      pause_before_ms: 0,
    },
    sequence_number: 1,
  };
}

interface Case {
  audience: ContentEvent["target_audience"];
  targetPlayer: string | null;
  surface: Surface;
  participantId: string;
  shouldDeliver: boolean;
}

const cases: Case[] = [
  {
    audience: "all",
    targetPlayer: null,
    surface: "phone",
    participantId: "p-1",
    shouldDeliver: true,
  },
  {
    audience: "all",
    targetPlayer: null,
    surface: "shared_display",
    participantId: "p-1",
    shouldDeliver: true,
  },
  {
    audience: "all",
    targetPlayer: null,
    surface: "host",
    participantId: "p-1",
    shouldDeliver: true,
  },

  {
    audience: "specific_player",
    targetPlayer: "p-1",
    surface: "phone",
    participantId: "p-1",
    shouldDeliver: true,
  },
  {
    audience: "specific_player",
    targetPlayer: "p-2",
    surface: "phone",
    participantId: "p-1",
    shouldDeliver: false,
  },
  {
    audience: "specific_player",
    targetPlayer: "p-1",
    surface: "shared_display",
    participantId: "p-1",
    shouldDeliver: false,
  },
  {
    audience: "specific_player",
    targetPlayer: "p-1",
    surface: "host",
    participantId: "p-1",
    shouldDeliver: false,
  },

  {
    audience: "shared_display",
    targetPlayer: null,
    surface: "phone",
    participantId: "p-1",
    shouldDeliver: false,
  },
  {
    audience: "shared_display",
    targetPlayer: null,
    surface: "shared_display",
    participantId: "p-1",
    shouldDeliver: true,
  },
  {
    audience: "shared_display",
    targetPlayer: null,
    surface: "host",
    participantId: "p-1",
    shouldDeliver: false,
  },

  {
    audience: "host_only",
    targetPlayer: null,
    surface: "phone",
    participantId: "p-1",
    shouldDeliver: false,
  },
  {
    audience: "host_only",
    targetPlayer: null,
    surface: "shared_display",
    participantId: "p-1",
    shouldDeliver: false,
  },
  {
    audience: "host_only",
    targetPlayer: null,
    surface: "host",
    participantId: "p-1",
    shouldDeliver: true,
  },
];

for (const c of cases) {
  const label = `privacy: ${c.audience}${c.targetPlayer ? `(${c.targetPlayer})` : ""} → ${c.surface} (p=${c.participantId}) ${c.shouldDeliver ? "delivers" : "drops"}`;
  test(label, () => {
    let delivered = false;
    const guarded = withAudienceGuard(
      { surface: c.surface, participantId: c.participantId },
      () => {
        delivered = true;
      },
      { warn: () => {} },
    );
    guarded(ev(c.audience, c.targetPlayer));
    assert.equal(delivered, c.shouldDeliver);
  });
}
