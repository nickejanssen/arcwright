import type { ContentEvent } from "./types.js";

export type NightcapFetch = (
  input: RequestInfo | URL,
  init?: RequestInit,
) => Promise<Response>;

export interface CreateSessionRequest extends Record<string, unknown> {
  arc_id?: string;
}

export interface CreateSessionResponse {
  session_id: string;
  join_url: string;
  host_token: string;
  [key: string]: unknown;
}

export interface SessionStateResponse {
  session_id: string;
  status: string;
  current_beat_id?: string;
  player_count?: number;
  [key: string]: unknown;
}

export interface PlayerSlotResponse {
  participant_id: string;
  join_token: string;
  join_url: string;
  [key: string]: unknown;
}

export interface JoinSessionResponse {
  session_id: string;
  player_id: string;
  character_id: string;
  player_token: string;
  [key: string]: unknown;
}

export interface EndSessionRequest {
  completion_type?: "full_arc" | "interrupted" | "abandoned";
  killer_identified?: boolean;
}

export interface NightcapConnectorOptions {
  baseUrl: string;
  apiKey: string;
  fetchImpl?: NightcapFetch;
}

export interface EventSubscriptionOptions {
  sessionId: string;
  accessToken: string;
  since?: number;
  maxReconnectAttempts?: number;
  onError?: (error: EventSubscriptionError) => void;
  retryBaseDelayMs?: number;
}

export interface EventSubscriptionError {
  message: string;
  sessionId: string;
  attempt: number;
  sequenceNumber: number;
  retryDelayMs: number | null;
}

export interface ConnectedSession {
  session: SessionStateResponse;
  subscribe: (onEvent: (event: ContentEvent) => void) => () => void;
}

export class NightcapConnector {
  private readonly baseUrl: string;
  private readonly apiKey: string;
  private readonly fetchImpl: NightcapFetch;

  constructor(options: NightcapConnectorOptions) {
    this.baseUrl = options.baseUrl.replace(/\/$/, "");
    this.apiKey = options.apiKey;
    this.fetchImpl = options.fetchImpl ?? fetch;
  }

  async createSession(
    body: CreateSessionRequest,
  ): Promise<CreateSessionResponse> {
    return this.jsonRequest<CreateSessionResponse>("/v1/sessions", {
      method: "POST",
      headers: this.apiHeaders(true),
      body: JSON.stringify(body),
    });
  }

  async getSession(sessionId: string): Promise<SessionStateResponse> {
    return this.jsonRequest<SessionStateResponse>(`/v1/sessions/${sessionId}`, {
      method: "GET",
      headers: this.apiHeaders(false),
    });
  }

  async createPlayerSlot(sessionId: string): Promise<PlayerSlotResponse> {
    return this.jsonRequest<PlayerSlotResponse>(
      `/v1/sessions/${sessionId}/players`,
      {
        method: "POST",
        headers: this.apiHeaders(true),
      },
    );
  }

  async joinSession(
    sessionId: string,
    joinToken: string,
    personalizationIntake: Record<string, unknown> = {},
  ): Promise<JoinSessionResponse> {
    const url = new URL(`/v1/sessions/${sessionId}/join`, this.baseUrl);
    url.searchParams.set("token", joinToken);
    return this.jsonRequest<JoinSessionResponse>(url.pathname + url.search, {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify({
        personalization_intake: personalizationIntake,
      }),
    });
  }

  async startSession(
    sessionId: string,
    accessToken: string,
  ): Promise<SessionStateResponse> {
    return this.authorizedJsonRequest<SessionStateResponse>(
      `/v1/sessions/${sessionId}/start`,
      accessToken,
      { method: "POST" },
    );
  }

  async pauseSession(
    sessionId: string,
    accessToken: string,
  ): Promise<SessionStateResponse> {
    return this.authorizedJsonRequest<SessionStateResponse>(
      `/v1/sessions/${sessionId}/pause`,
      accessToken,
      { method: "POST" },
    );
  }

  async resumeSession(
    sessionId: string,
    accessToken: string,
  ): Promise<SessionStateResponse> {
    return this.authorizedJsonRequest<SessionStateResponse>(
      `/v1/sessions/${sessionId}/resume`,
      accessToken,
      { method: "POST" },
    );
  }

  async endSession(
    sessionId: string,
    accessToken: string,
    body: EndSessionRequest = {},
  ): Promise<SessionStateResponse> {
    return this.authorizedJsonRequest<SessionStateResponse>(
      `/v1/sessions/${sessionId}/end`,
      accessToken,
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    );
  }

  async attachToSession(
    sessionId: string,
    accessToken: string,
  ): Promise<ConnectedSession> {
    const session = await this.getSession(sessionId);
    return {
      session,
      subscribe: (onEvent) =>
        this.subscribeToEvents({ sessionId, accessToken }, onEvent),
    };
  }

  subscribeToEvents(
    options: EventSubscriptionOptions,
    onEvent: (event: ContentEvent) => void,
  ): () => void {
    let cancelled = false;
    let reader: ReadableStreamDefaultReader<Uint8Array> | null = null;
    let reconnectAttempts = 0;
    let lastSequenceNumber = options.since ?? 0;
    const maxReconnectAttempts = options.maxReconnectAttempts ?? 5;
    const retryBaseDelayMs = options.retryBaseDelayMs ?? 250;

    const sleep = async (ms: number): Promise<void> => {
      await new Promise<void>((resolve) => {
        setTimeout(resolve, ms);
      });
    };

    const retryDelayFor = (attempt: number): number | null =>
      attempt < maxReconnectAttempts ? retryBaseDelayMs * 2 ** attempt : null;

    const emitError = (message: string, retryDelayMs: number | null): void => {
      options.onError?.({
        message,
        sessionId: options.sessionId,
        attempt: reconnectAttempts,
        sequenceNumber: lastSequenceNumber,
        retryDelayMs,
      });
    };

    const scheduleRetry = async (message: string): Promise<boolean> => {
      const retryDelayMs = retryDelayFor(reconnectAttempts);
      emitError(message, retryDelayMs);
      if (cancelled || retryDelayMs === null) {
        return false;
      }

      reconnectAttempts += 1;
      await sleep(retryDelayMs);
      return !cancelled;
    };

    const parseBlock = (block: string): void => {
      let eventName: string | null = null;
      let eventId: string | null = null;
      const dataLines: string[] = [];

      for (const rawLine of block.split("\n")) {
        const line = rawLine.replace(/\r$/, "");
        if (!line || line.startsWith(":")) {
          continue;
        }

        if (line.startsWith("event:")) {
          eventName = line.slice(6).trim();
          continue;
        }

        if (line.startsWith("id:")) {
          eventId = line.slice(3).trim();
          continue;
        }

        if (line.startsWith("data:")) {
          dataLines.push(line.slice(5).replace(/^\s/, ""));
        }
      }

      if (dataLines.length === 0) {
        return;
      }

      try {
        const event = JSON.parse(dataLines.join("\n")) as ContentEvent;
        if (eventId) {
          const parsedEventId = Number.parseInt(eventId, 10);
          if (!Number.isNaN(parsedEventId)) {
            lastSequenceNumber = Math.max(lastSequenceNumber, parsedEventId);
          }
        }

        lastSequenceNumber = Math.max(
          lastSequenceNumber,
          event.sequence_number,
        );
        onEvent(event);
      } catch {
        emitError(
          `Received malformed SSE payload${eventName ? ` for ${eventName}` : ""}.`,
          null,
        );
      }
    };

    const stream = async (): Promise<void> => {
      while (!cancelled) {
        const url = new URL(
          `${this.baseUrl}/v1/sessions/${options.sessionId}/events`,
        );
        url.searchParams.set("since", String(lastSequenceNumber));

        let response: Response;
        try {
          response = await this.fetchImpl(url, {
            method: "GET",
            headers: {
              Authorization: `Bearer ${options.accessToken}`,
            },
          });
        } catch {
          if (!(await scheduleRetry("Failed to open event stream."))) {
            break;
          }
          continue;
        }

        if (!response.ok || !response.body || cancelled) {
          if (
            !(await scheduleRetry(
              `Event stream returned ${response.status} ${response.statusText}.`,
            ))
          ) {
            break;
          }
          continue;
        }

        reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        try {
          while (!cancelled) {
            const { done, value } = await reader.read();
            if (done) {
              break;
            }

            buffer += decoder.decode(value, { stream: true });
            buffer = buffer.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
            const blocks = buffer.split("\n\n");
            buffer = blocks.pop() ?? "";

            for (const block of blocks) {
              parseBlock(block);
            }
          }
        } finally {
          if (buffer.length > 0) {
            parseBlock(buffer);
          }
          reader = null;
        }

        if (
          cancelled ||
          !(await scheduleRetry("Event stream ended unexpectedly."))
        ) {
          break;
        }
      }
    };

    void stream();

    return () => {
      cancelled = true;
      void reader?.cancel();
    };
  }

  private apiHeaders(includeContentType: boolean): HeadersInit {
    return {
      "X-Api-Key": this.apiKey,
      ...(includeContentType ? { "Content-Type": "application/json" } : {}),
    };
  }

  private authorizedHeaders(
    accessToken: string,
    includeContentType: boolean,
  ): HeadersInit {
    return {
      Authorization: `Bearer ${accessToken}`,
      ...(includeContentType ? { "Content-Type": "application/json" } : {}),
    };
  }

  private async jsonRequest<T>(path: string, init: RequestInit): Promise<T> {
    const response = await this.fetchImpl(`${this.baseUrl}${path}`, init);
    if (!response.ok) {
      throw new Error(
        `${init.method ?? "GET"} ${path} failed with ${response.status}`,
      );
    }

    return response.json() as Promise<T>;
  }

  private async authorizedJsonRequest<T>(
    path: string,
    accessToken: string,
    init: RequestInit,
  ): Promise<T> {
    const response = await this.fetchImpl(`${this.baseUrl}${path}`, {
      ...init,
      headers: {
        ...this.authorizedHeaders(
          accessToken,
          init.body !== undefined || init.method === "POST",
        ),
        ...(init.headers ?? {}),
      },
    });

    if (!response.ok) {
      throw new Error(
        `${init.method ?? "GET"} ${path} failed with ${response.status}`,
      );
    }

    return response.json() as Promise<T>;
  }
}
