// Stage states and styles for the mini-game stage. Copied from
// nightcap-web/src/mini-games/stage.ts (AW-329) without its server-page
// helpers; the dashboard draws the stage element in MiniGameStage.tsx.

// Stage states emitted via data-mini-game-state. Shared with client.ts so the
// CSS, the boot loop, and the renderer error paths stay aligned.
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
