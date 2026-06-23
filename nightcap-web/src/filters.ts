import type { ContentEvent } from "./types.js";

export function isSharedDisplayVisibleEvent(
  event: Pick<ContentEvent, "target_audience">,
): boolean {
  return (
    event.target_audience === "all" ||
    event.target_audience === "shared_display"
  );
}

export function isHostVisibleEvent(
  event: Pick<ContentEvent, "target_audience">,
): boolean {
  return (
    event.target_audience === "all" || event.target_audience === "host_only"
  );
}
