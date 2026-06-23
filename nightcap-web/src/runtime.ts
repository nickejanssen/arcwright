import type {
  CreateSessionRequest,
  CreateSessionResponse,
  EndSessionRequest,
  JoinSessionResponse,
  PlayerSlotResponse,
  SessionStateResponse,
} from "./connector.js";

export interface NightcapBootstrapRequest extends CreateSessionRequest {
  personalization_intake?: Record<string, unknown>;
}

export interface NightcapRuntimeUrls {
  room_url: string;
  host_url: string;
  shared_display_url: string;
}

export interface NightcapBootstrapResponse {
  session: CreateSessionResponse;
  runtime: NightcapRuntimeUrls & { room_id: string };
  personalization_intake: Record<string, unknown>;
}

export interface NightcapLifecycleRequest {
  access_token?: string;
}

export interface NightcapLifecycleEndRequest
  extends NightcapLifecycleRequest, EndSessionRequest {}

export interface NightcapLifecycleResponse {
  session: SessionStateResponse;
}

export interface NightcapPlayerSlotResponse {
  session_id: string;
  player: PlayerSlotResponse;
  runtime: NightcapRuntimeUrls & { room_id: string; player_url: string };
}

export interface NightcapPlayerJoinRequest {
  session_id: string;
  join_token: string;
  personalization_intake?: Record<string, unknown>;
}

export interface NightcapPlayerJoinResponse {
  session_id: string;
  player: JoinSessionResponse;
  runtime: NightcapRuntimeUrls & { room_id: string; player_url: string };
  personalization_intake: Record<string, unknown>;
}

export interface NightcapPlayerSessionState {
  session_id: string;
  player_id: string;
  character_id: string;
  player_token: string;
  last_sequence_number: number;
}

export function normalizePersonalizationIntake(
  value: unknown,
): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return {};
  }

  return value as Record<string, unknown>;
}

export function buildNightcapRuntimeUrls(
  sessionId: string,
): NightcapRuntimeUrls {
  return {
    room_url: `/rooms/${sessionId}`,
    host_url: `/host?session_id=${encodeURIComponent(sessionId)}`,
    shared_display_url: `/shared-display?session_id=${encodeURIComponent(sessionId)}`,
  };
}

export function buildNightcapPlayerJoinUrl(
  sessionId: string,
  joinToken: string,
): string {
  const url = new URL("https://nightcap.local/join");
  url.searchParams.set("session_id", sessionId);
  url.searchParams.set("token", joinToken);
  return `${url.pathname}${url.search}`;
}

export function buildNightcapPlayerSessionStorageKey(
  sessionId: string,
): string {
  return `nightcap.player.session.${sessionId}`;
}

export function normalizeNightcapPlayerSessionState(
  value: unknown,
): NightcapPlayerSessionState | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }

  const candidate = value as Partial<NightcapPlayerSessionState>;
  if (
    typeof candidate.session_id !== "string" ||
    candidate.session_id.length === 0 ||
    typeof candidate.player_id !== "string" ||
    candidate.player_id.length === 0 ||
    typeof candidate.character_id !== "string" ||
    candidate.character_id.length === 0 ||
    typeof candidate.player_token !== "string" ||
    candidate.player_token.length === 0 ||
    typeof candidate.last_sequence_number !== "number" ||
    !Number.isFinite(candidate.last_sequence_number) ||
    candidate.last_sequence_number < 0
  ) {
    return null;
  }

  return {
    session_id: candidate.session_id,
    player_id: candidate.player_id,
    character_id: candidate.character_id,
    player_token: candidate.player_token,
    last_sequence_number: Math.floor(candidate.last_sequence_number),
  };
}
