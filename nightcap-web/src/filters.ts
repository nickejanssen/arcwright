import type { ContentEvent } from "./types.js";

export const SHARED_DISPLAY_VISIBLE_AUDIENCES = [
  "all",
  "shared_display",
] as const;

export const HOST_VISIBLE_AUDIENCES = ["all", "host_only"] as const;

export function isSharedDisplayVisibleEvent(
  event: Pick<ContentEvent, "target_audience">,
): boolean {
  return SHARED_DISPLAY_VISIBLE_AUDIENCES.includes(
    event.target_audience as (typeof SHARED_DISPLAY_VISIBLE_AUDIENCES)[number],
  );
}

export function isHostVisibleEvent(
  event: Pick<ContentEvent, "target_audience">,
): boolean {
  return HOST_VISIBLE_AUDIENCES.includes(
    event.target_audience as (typeof HOST_VISIBLE_AUDIENCES)[number],
  );
}
