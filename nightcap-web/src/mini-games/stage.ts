// Server-side HTML helpers for the mini-game stage. Each Nightcap page
// (host, shared display, player) includes a stage section and the bundled
// browser entry script. Stage data attributes are populated by the page's
// existing connect/join JS once session context is known.

import type { Surface } from "../mini-game-kit/index.js";

const STAGE_BUNDLE_PATH = "/static/mini-games.js";

export function renderMiniGameStage(surface: Surface): string {
  // Initial state is "idle"; browser-entry takes over once data attributes
  // are populated by the surrounding page JS or page render context.
  return `<section
  class="card mini-game-stage"
  data-mini-game-stage
  data-surface="${surface}"
  data-mini-game-state="idle"
  aria-label="Mini-game stage"
>
  <h2>Mini-game</h2>
  <p class="muted mini-game-stage-empty" data-mini-game-empty>
    No mini-game in progress.
  </p>
</section>`;
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
.mini-game-stage[data-mini-game-state="idle"] [data-role],
.mini-game-stage[data-mini-game-state="idle"] .mg-choices,
.mini-game-stage[data-mini-game-state="idle"] .mg-options {
  display: none;
}
.mini-game-stage[data-mini-game-state^="active"] .mini-game-stage-empty {
  display: none;
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
.mini-game-stage[data-mini-game-state="boot-error"]::after,
.mini-game-stage[data-mini-game-state="unknown-game"]::after,
.mini-game-stage[data-mini-game-state="definition-error"]::after,
.mini-game-stage[data-mini-game-state="render-error"]::after {
  content: attr(data-mini-game-state);
  color: var(--danger, #fb7185);
  font-size: 0.85rem;
}
.mini-game-stage .mg-timer {
  font-variant-numeric: tabular-nums;
  font-size: 1.4rem;
  color: var(--accent, #7dd3fc);
}
@media (prefers-reduced-motion: reduce) {
  .mini-game-stage * {
    transition: none !important;
    animation: none !important;
  }
}
</style>`;
}
