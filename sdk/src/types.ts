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

export interface TmstPhaseStartedPayload {
  phase: "input";
  deadline: string;
  participant_count: number;
}

export interface TmstPrivatePromptReadyPayload {
  phase: "input";
}

export interface TmstSpotlightStartedPayload {
  phase: "spotlight";
  target_character_id: string;
  eligible_voter_ids: string[];
  deadline: string;
}

export interface TmstSpotlightSkippedPayload {
  target_character_id: string;
  reason: "disconnected";
}

export interface TmstVoteBreakdown {
  truth: number;
  lie: number;
  abstain: number;
}

export interface TmstRevealResolvedPayload {
  phase: "reveal";
  target_character_id: string;
  declared_truth: boolean;
  statement_text: string;
  vote_breakdown: TmstVoteBreakdown;
  abstaining_character_ids: string[];
}

export interface TmstScoreboardReadyPayload {
  phase: "scoreboard";
  scores: Record<string, number>;
  all_truth_round: boolean;
  all_lie_round: boolean;
  deflection_tendency: Record<string, Record<string, number>>;
}

export interface TmstPhaseStartedEvent extends Omit<
  ContentEvent,
  "event_type" | "payload"
> {
  event_type: "tmst_phase_started";
  payload: TmstPhaseStartedPayload;
}

export interface TmstPrivatePromptReadyEvent extends Omit<
  ContentEvent,
  "event_type" | "payload"
> {
  event_type: "tmst_private_prompt_ready";
  payload: TmstPrivatePromptReadyPayload;
}

export interface TmstSpotlightStartedEvent extends Omit<
  ContentEvent,
  "event_type" | "payload"
> {
  event_type: "tmst_spotlight_started";
  payload: TmstSpotlightStartedPayload;
}

export interface TmstSpotlightSkippedEvent extends Omit<
  ContentEvent,
  "event_type" | "payload"
> {
  event_type: "tmst_spotlight_skipped";
  payload: TmstSpotlightSkippedPayload;
}

export interface TmstRevealResolvedEvent extends Omit<
  ContentEvent,
  "event_type" | "payload"
> {
  event_type: "tmst_reveal_resolved";
  payload: TmstRevealResolvedPayload;
}

export interface TmstScoreboardReadyEvent extends Omit<
  ContentEvent,
  "event_type" | "payload"
> {
  event_type: "tmst_scoreboard_ready";
  payload: TmstScoreboardReadyPayload;
}

export type TmstContentEvent =
  | TmstPhaseStartedEvent
  | TmstPrivatePromptReadyEvent
  | TmstSpotlightStartedEvent
  | TmstSpotlightSkippedEvent
  | TmstRevealResolvedEvent
  | TmstScoreboardReadyEvent;

export interface GenericContentEvent {
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

export type TypedContentEvent = TmstContentEvent | GenericContentEvent;

export interface MiniGameSubmissionResult {
  submissionId: string;
  isAccepted: boolean;
  rejectionReason?: string;
}

export interface TmstInputPhaseState {
  phase: "input";
  deadline_at: string | null;
  prompt_ready: boolean;
  submitted: boolean;
}

export interface TmstSpotlightPhaseState {
  phase: "spotlight";
  deadline_at: string | null;
  target_character_id: string;
  connected_character_ids: string[];
  eligible_voter_ids: string[];
  is_spotlighted_player: boolean;
  can_vote: boolean;
  has_voted: boolean;
}

export type TmstPhaseState = TmstInputPhaseState | TmstSpotlightPhaseState;

export interface MiniGameState {
  runId: string;
  gameId: string;
  mechanicType: string | null;
  status:
    | "pending"
    | "active"
    | "paused"
    | "completed"
    | "timed_out"
    | "cancelled";
  deadlineAt: string | null;
  phaseState: TmstPhaseState | null;
  mySubmissions: MiniGameSubmissionResult[];
}

export interface TmstInputActionPayload {
  action: "input";
  statement_text: string;
  declared_truth: boolean;
}

export interface TmstVoteActionPayload {
  action: "vote";
  target_character_id: string;
  vote: "truth" | "lie";
}

export interface TmstPresenceActionPayload {
  action: "presence";
  connected: boolean;
}

export type TmstSubmissionPayload =
  | TmstInputActionPayload
  | TmstVoteActionPayload
  | TmstPresenceActionPayload;

export type MiniGamePayload = TmstSubmissionPayload | Record<string, unknown>;

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
