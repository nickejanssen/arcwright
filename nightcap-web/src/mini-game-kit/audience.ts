// Defense-in-depth audience filter. The primary privacy boundary is the
// scoped player token Arcwright issues per surface, which causes the SDK to
// receive only authorized events. This filter exists so a server-side
// misconfiguration cannot leak through unnoticed.

import type { ContentEvent } from "../types.js";
import type { Surface } from "./types.js";

export interface AudienceGuardContext {
  surface: Surface;
  participantId: string;
}

export function isAuthorizedForSurface(
  event: Pick<ContentEvent, "target_audience" | "target_player_id">,
  ctx: AudienceGuardContext,
): boolean {
  switch (event.target_audience) {
    case "all":
      return true;
    case "specific_player":
      return (
        ctx.surface === "phone" && event.target_player_id === ctx.participantId
      );
    case "shared_display":
      return ctx.surface === "shared_display";
    case "host_only":
      return ctx.surface === "host";
    default:
      return false;
  }
}

// Wraps an event handler with the audience filter. Events that do not match
// the surface are discarded silently. specific_player events that reach the
// wrong surface emit a console warning so server-side misconfiguration is
// noisy in observability without being user-visible.
export function withAudienceGuard(
  ctx: AudienceGuardContext,
  handler: (event: ContentEvent) => void,
  logger: Pick<Console, "warn"> = console,
): (event: ContentEvent) => void {
  return (event) => {
    if (isAuthorizedForSurface(event, ctx)) {
      handler(event);
      return;
    }
    if (
      event.target_audience === "specific_player" &&
      ctx.surface !== "phone"
    ) {
      logger.warn(
        `[mini-game-kit] specific_player event ${event.event_id} delivered to ${ctx.surface} surface; discarded.`,
      );
    }
  };
}
