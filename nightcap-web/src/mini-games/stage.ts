// Server-side HTML helpers for the mini-game stage. Each Nightcap page
// (host, shared display, player) includes a stage section and the bundled
// browser entry script. Stage data attributes are populated by the page's
// existing connect/join JS once session context is known.

import type { Surface } from "../mini-game-kit/index.js";

// Bundle path. Served by the Cloudflare [assets] binding rooted at
// nightcap-web/dist/static — the URL maps 1:1 to a file inside that
// directory, so the bundle lives at /mini-games.js (no extra /static/
// prefix).
const STAGE_BUNDLE_PATH = "/mini-games.js";

// Stage states emitted via data-mini-game-state. Shared with client.ts and
// browser-entry.ts so the CSS, the boot loop, and the renderer error paths
// stay aligned.
export const StageStates = {
  Idle: "idle",
  InvalidConfig: "invalid-config",
  BootError: "boot-error",
  UnknownGame: "unknown-game",
  DefinitionError: "definition-error",
  RenderError: "render-error",
} as const;

export type StageState =
  | (typeof StageStates)[keyof typeof StageStates]
  | `active:${string}`;

export function buildActiveStageState(gameId: string): StageState {
  return `active:${gameId}`;
}

export function renderMiniGameStage(surface: Surface): string {
  // Initial state is idle; browser-entry takes over once data attributes
  // are populated. The "no mini-game in progress" placeholder, the section
  // label, and the error labels are all rendered via CSS ::after so they
  // survive a renderer's clearChildren on unmount and remain inert during
  // active mounts. aria-label provides the accessible region name; no
  // child header is needed (a renderer's first action is clearChildren on
  // this element, so any committed children would be discarded anyway).
  return `<section
  class="card mini-game-stage"
  data-mini-game-stage
  data-surface="${surface}"
  data-mini-game-state="${StageStates.Idle}"
  aria-label="Mini-game stage"
></section>`;
}

export function renderMiniGameScriptTag(): string {
  return `<script type="module" src="${STAGE_BUNDLE_PATH}"></script>`;
}

export function renderMiniGameStageStyles(): string {
  // Scoped CSS; appended to a page's existing inline style block or shipped
  // as a separate <style> tag. Tiny on purpose — most visual style lives in
  // the renderer kit and per-game CSS.
  return `<style>
.mini-game-stage {
  display: grid;
  gap: 14px;
}
.mini-game-stage[data-mini-game-state="${StageStates.Idle}"] .mg-choices,
.mini-game-stage[data-mini-game-state="${StageStates.Idle}"] .mg-options {
  display: none;
}
.mini-game-stage[data-mini-game-state="${StageStates.Idle}"]::after {
  content: "No mini-game in progress.";
  color: var(--ink-muted);
  font-size: 0.95rem;
}
.mini-game-stage .mg-choices,
.mini-game-stage .mg-options {
  display: grid;
  gap: 10px;
}
.mini-game-stage button {
  min-height: 44px;
  min-width: 44px;
}
.mini-game-stage[data-mini-game-state="${StageStates.BootError}"]::after,
.mini-game-stage[data-mini-game-state="${StageStates.UnknownGame}"]::after,
.mini-game-stage[data-mini-game-state="${StageStates.DefinitionError}"]::after,
.mini-game-stage[data-mini-game-state="${StageStates.RenderError}"]::after,
.mini-game-stage[data-mini-game-state="${StageStates.InvalidConfig}"]::after {
  content: attr(data-mini-game-state);
  color: var(--accuse);
  font-size: 0.85rem;
}
.mini-game-stage .mg-timer {
  font-variant-numeric: tabular-nums;
  font-size: 1.4rem;
  color: var(--theme-glow);
}
@media (prefers-reduced-motion: reduce) {
  .mini-game-stage * {
    transition: none !important;
    animation: none !important;
  }
}
</style>`;
}
