export { defineRenderer } from "./define-renderer.js";
export { useCountdown, formatRemaining } from "./countdown.js";
export {
  createSubmissionGuard,
  type SubmissionGuard,
  type SubmissionGuardOptions,
} from "./submission.js";
export {
  isAuthorizedForSurface,
  withAudienceGuard,
  type AudienceGuardContext,
} from "./audience.js";
export { createPerfReporter, type PerfReporter } from "./perf.js";
export {
  createHostStatusCard,
  type HostStatusCardOptions,
} from "./host-status-card.js";
export {
  el,
  on,
  setText,
  setHidden,
  setDisabled,
  clearChildren,
  prefersReducedMotion,
  type AttrValue,
} from "./dom.js";
export type {
  Surface,
  ParticipationMode,
  ContentMode,
  MiniGameBehavioralOutput,
  MiniGameClueFallback,
  MiniGameDefinition,
  MiniGameContext,
  MiniGameRenderer,
  SurfaceHandler,
  SurfaceLifecycle,
  DefineRendererSpec,
} from "./types.js";
