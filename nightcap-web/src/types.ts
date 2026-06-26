// Mirrors sdk/src/types.ts — keep in sync until a shared import path is established.
export type AudienceTarget =
  | "all"
  | "host_only"
  | "specific_player"
  | "shared_display";

export type EventCategory =
  | "narrative"
  | "character_dialogue"
  | "private_delivery"
  | "acknowledgement"
  | "state_transition"
  | "input_request"
  | "system";

export interface PresentationHints {
  emotion: string | null;
  urgency: string | null;
  voice_hint: string | null;
  animation_hint: string | null;
  lighting_hint: string | null;
  pause_before_ms: number;
}

export interface ContentEvent {
  event_id: string;
  session_id: string;
  timestamp: string;
  category: EventCategory;
  event_type: string;
  actor_id: string | null;
  target_audience: AudienceTarget;
  target_player_id: string | null;
  payload: Record<string, unknown>;
  presentation_hints: PresentationHints;
  sequence_number: number;
}

export interface PlayerInput {
  kind: "action" | "dialogue";
  content: string;
}

export interface CharacterDetail {
  session_id: string;
  character_id: string;
  participant_id: string;
  surface_type: SurfaceType;
  is_ai_controlled: boolean;
}

export type SurfaceType = "phone" | "shared_display" | "host";

export type MiniGameStatus =
  | "pending"
  | "active"
  | "paused"
  | "completed"
  | "timed_out"
  | "cancelled";

export interface MiniGameSubmissionResult {
  submissionId: string;
  isAccepted: boolean;
  rejectionReason?: string;
}

export interface MiniGameState {
  runId: string;
  gameId: string;
  status: MiniGameStatus;
  deadlineAt: string | null;
  mySubmissions: MiniGameSubmissionResult[];
}

export type MiniGamePayload = Record<string, unknown>;
