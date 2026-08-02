import { isSharedDisplayVisibleEvent } from "../filters.js";
import type { ContentEvent } from "../types.js";

export type SharedDisplayProjectionKind =
  | "suspect_answer"
  | "resource_effect"
  | "leverage_balance";

export interface SharedDisplayProjection {
  kind: SharedDisplayProjectionKind;
  body: string;
  suspectId: string | null;
  askerIds: string[];
  suspectState: string | null;
}

type ProjectableEvent = Pick<
  ContentEvent,
  "event_type" | "target_audience" | "payload"
>;

function asRecord(value: unknown): Record<string, unknown> | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  return value as Record<string, unknown>;
}

function asNonEmptyString(value: unknown): string | null {
  return typeof value === "string" && value.trim().length > 0 ? value : null;
}

function asStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((entry): entry is string => typeof entry === "string");
}

export function projectSharedDisplayEvent(
  event: ProjectableEvent,
): SharedDisplayProjection | null {
  // Audience is checked before event_type, never after. Several Couch Race
  // event types (notably resource_effect_outcome) are emitted with either an
  // `all` or a `specific_player` audience depending on the effect, so keying
  // a projection on event_type alone would leak private outcomes to the room.
  if (!isSharedDisplayVisibleEvent(event)) {
    return null;
  }

  const payload = asRecord(event.payload);
  if (!payload) {
    return null;
  }

  if (event.event_type === "interaction_answer") {
    const body = asNonEmptyString(asRecord(payload.answer)?.text);
    if (!body) {
      return null;
    }
    return {
      kind: "suspect_answer",
      body,
      suspectId: asNonEmptyString(payload.target_id),
      askerIds: asStringArray(payload.participant_ids),
      suspectState: null,
    };
  }

  if (event.event_type === "resource_effect_outcome") {
    const body = asNonEmptyString(asRecord(payload.outcome)?.text);
    if (!body) {
      return null;
    }
    return {
      kind: "resource_effect",
      body,
      suspectId: null,
      askerIds: [],
      suspectState: null,
    };
  }

  return null;
}
