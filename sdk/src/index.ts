export type {
  AudienceTarget,
  EventCategory,
  PresentationHints,
  ContentEvent,
  PlayerInput,
  CharacterDetail,
} from "./types.js";

import type { ContentEvent, PlayerInput, CharacterDetail } from "./types.js";

export class ArcwrightClient {
  private readonly _sessionId: string;
  private readonly _playerToken: string;
  private readonly _characterId: string;
  private readonly _baseUrl: string;

  private _connected = false;
  private _lastSequenceNumber = 0;
  private _reader: ReadableStreamDefaultReader<Uint8Array> | null = null;

  constructor(
    sessionId: string,
    playerToken: string,
    characterId: string,
    baseUrl: string,
  ) {
    this._sessionId = sessionId;
    this._playerToken = playerToken;
    this._characterId = characterId;
    this._baseUrl = baseUrl.replace(/\/$/, "");
  }

  onEvent(callback: (event: ContentEvent) => void): () => void {
    this._connected = true;
    void this._streamEvents(callback, false);
    return () => this.disconnect();
  }

  async submitInput(characterId: string, input: PlayerInput): Promise<void> {
    const url = `${this._baseUrl}/v1/sessions/${this._sessionId}/characters/${characterId}/input`;
    const res = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this._playerToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(input),
    });
    if (!res.ok) {
      throw new Error(`submitInput failed: ${res.status} ${res.statusText}`);
    }
  }

  async getMyCharacter(): Promise<CharacterDetail> {
    const url = `${this._baseUrl}/v1/sessions/${this._sessionId}/characters/${this._characterId}`;
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${this._playerToken}` },
    });
    if (!res.ok) {
      throw new Error(`getMyCharacter failed: ${res.status} ${res.statusText}`);
    }
    return res.json() as Promise<CharacterDetail>;
  }

  disconnect(): void {
    this._connected = false;
    if (this._reader) {
      void this._reader.cancel();
      this._reader = null;
    }
  }

  private async _streamEvents(
    callback: (event: ContentEvent) => void,
    isReconnect: boolean,
  ): Promise<void> {
    const url = `${this._baseUrl}/v1/sessions/${this._sessionId}/events?since=${this._lastSequenceNumber}`;
    let res: Response;
    try {
      res = await fetch(url, {
        headers: { Authorization: `Bearer ${this._playerToken}` },
      });
    } catch {
      return;
    }

    if (!res.ok || !res.body) {
      return;
    }

    this._reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";

    try {
      while (this._connected) {
        const { done, value } = await this._reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        buf = buf.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
        const blocks = buf.split("\n\n");
        buf = blocks.pop() ?? "";
        for (const block of blocks) {
          for (const line of block.split("\n")) {
            if (line.startsWith("data:")) {
              const json = line.slice(5).trim();
              if (!json) continue;
              try {
                const event = JSON.parse(json) as ContentEvent;
                this._lastSequenceNumber = event.sequence_number;
                callback(event);
              } catch {
                // malformed SSE data line; skip
              }
            }
          }
        }
      }
    } finally {
      this._reader = null;
    }

    // Single reconnect attempt on unexpected stream end.
    if (this._connected && !isReconnect) {
      await this._streamEvents(callback, true);
    }
  }
}
