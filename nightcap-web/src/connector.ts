import type { ContentEvent } from "../../sdk/dist/index.js";

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

export interface NightcapConnectorOptions {
  baseUrl: string;
  apiKey: string;
  fetchImpl?: NightcapFetch;
}

export interface EventSubscriptionOptions {
  sessionId: string;
  accessToken: string;
  since?: number;
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
      headers: this.apiHeaders(),
      body: JSON.stringify(body),
    });
  }

  async getSession(sessionId: string): Promise<SessionStateResponse> {
    return this.jsonRequest<SessionStateResponse>(`/v1/sessions/${sessionId}`, {
      method: "GET",
      headers: this.apiHeaders(),
    });
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
    let reconnectAttempted = false;
    let lastSequenceNumber = options.since ?? 0;

    const stream = async (isReconnect: boolean): Promise<void> => {
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
        return;
      }

      if (!response.ok || !response.body || cancelled) {
        return;
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
            for (const line of block.split("\n")) {
              if (!line.startsWith("data:")) {
                continue;
              }

              const payload = line.slice(5).trim();
              if (!payload) {
                continue;
              }

              try {
                const event = JSON.parse(payload) as ContentEvent;
                lastSequenceNumber = event.sequence_number;
                onEvent(event);
              } catch {
                continue;
              }
            }
          }
        }
      } finally {
        reader = null;
      }

      if (!cancelled && !isReconnect && !reconnectAttempted) {
        reconnectAttempted = true;
        await stream(true);
      }
    };

    void stream(false);

    return () => {
      cancelled = true;
      void reader?.cancel();
    };
  }

  private apiHeaders(): HeadersInit {
    return {
      "X-Api-Key": this.apiKey,
      "Content-Type": "application/json",
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
}
