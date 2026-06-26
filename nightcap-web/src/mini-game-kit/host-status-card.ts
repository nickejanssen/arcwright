// Reusable host-surface presentation. Three identical card structures across
// the fixture renderers (badge + count + clue-fallback note + status updates
// + count event handling) factor into one kit helper so future games inherit
// the same host UX with one line of code.

import { clearChildren, el, setText } from "./dom.js";
import type { MiniGameDefinition, SurfaceLifecycle } from "./types.js";
import type { ContentEvent, MiniGameState } from "../types.js";

export interface HostStatusCardOptions {
  state: MiniGameState;
  definition: MiniGameDefinition;
  /** Format the running count for display. e.g. `(n) => `${n} answered\``. */
  countLabel: (count: number) => string;
  /** Event type whose acceptance bumps the count. */
  countEventType: string;
}

export function createHostStatusCard(
  root: HTMLElement,
  opts: HostStatusCardOptions,
): SurfaceLifecycle {
  const doc = root.ownerDocument;
  clearChildren(root);

  const badge = el(
    doc,
    "span",
    { class: "mg-host-badge", "data-role": "status" },
    [opts.state.status],
  );

  const count = el(doc, "p", { class: "mg-host-count", "data-role": "count" }, [
    opts.countLabel(0),
  ]);

  const fallback = el(
    doc,
    "p",
    { class: "mg-host-fallback", "data-role": "fallback" },
    [
      `Clue fallback: ${opts.definition.clue_fallback.delay_seconds}s, variant ${opts.definition.clue_fallback.clue_variant}.`,
    ],
  );

  root.appendChild(badge);
  root.appendChild(count);
  root.appendChild(fallback);

  let n = 0;

  return {
    update(state) {
      setText(badge, state.status);
    },
    handleEvent(event: ContentEvent) {
      if (event.event_type === opts.countEventType) {
        n += 1;
        setText(count, opts.countLabel(n));
      }
    },
    unmount() {
      clearChildren(root);
    },
  };
}
