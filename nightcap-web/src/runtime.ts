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
