// Mini-game kit public types.
// The kit is the contract every renderer composes. It lives in nightcap-web
// for AW-253 and is intended to hoist to @arcwright/mini-game-kit once a
// second game adopts it. Keep the surface small and the contract stable.

import type {
  ContentEvent,
  MiniGamePayload,
  MiniGameState,
  MiniGameSubmissionResult,
} from "../types.js";

export type Surface = "phone" | "shared_display" | "host";

export type ParticipationMode = "individual" | "collaborative" | "group";

export type ContentMode = "authored" | "generative" | "hybrid";

export interface MiniGameBehavioralOutput {
  key: string;
  description: string;
  value_type: "integer" | "number" | "string" | "boolean";
  scope: "participant" | "run";
  derived: boolean;
}

export interface MiniGameClueFallback {
  delay_seconds: number;
  clue_variant: string;
  host_override: boolean;
}

// Mirror of the Python MiniGameDefinition schema (see
// nightcap/mini_games/_fixtures/*/definitions/0.1.0.json). Renderers read
// authored_content and generation_constraints to drive their UI; the engine
// owns everything else.
export interface MiniGameDefinition {
  schema_version: string;
  game_id: string;
  version: string;
  mechanic_type: string;
  participation_mode: ParticipationMode;
  content_mode: ContentMode;
  min_players: number;
  max_players: number;
  duration_seconds: number;
  rules: Record<string, unknown>;
  authored_content: Record<string, unknown> | null;
  generation_constraints: Record<string, unknown> | null;
  behavioral_outputs: MiniGameBehavioralOutput[];
  clue_fallback: MiniGameClueFallback;
}

export interface MiniGameContext {
  surface: Surface;
  sessionId: string;
  participantId: string;
  characterId: string;
  state: MiniGameState;
  definition: MiniGameDefinition;
  submit(payload: MiniGamePayload): Promise<MiniGameSubmissionResult>;
  onEvent(handler: (event: ContentEvent) => void): () => void;
  reportPerf(name: string, value: number): void;
}

export interface SurfaceLifecycle {
  update(state: MiniGameState): void;
  handleEvent(event: ContentEvent): void;
  unmount(): void;
}

export interface SurfaceHandler {
  mount(root: HTMLElement, ctx: MiniGameContext): SurfaceLifecycle;
}

export interface MiniGameRenderer {
  readonly gameId: string;
  mount(root: HTMLElement, ctx: MiniGameContext): SurfaceLifecycle;
}

export interface DefineRendererSpec {
  gameId: string;
  phone?: SurfaceHandler;
  sharedDisplay?: SurfaceHandler;
  host?: SurfaceHandler;
}
