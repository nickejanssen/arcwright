import type {
  CreateSessionRequest,
  CreateSessionResponse,
  EndSessionRequest,
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
