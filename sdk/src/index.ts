export { isTmstEvent } from "./types.js";

export type {
  AudienceTarget,
  EventCategory,
  PresentationHints,
  ContentEvent,
  GenericContentEvent,
  MiniGamePayload,
  MiniGameState,
  MiniGameSubmissionResult,
  PlayerInput,
  CharacterDetail,
  SurfaceType,
  TmstContentEvent,
  TmstInputActionPayload,
  TmstInputPhaseState,
  TmstPhaseStartedEvent,
  TmstPhaseStartedPayload,
  TmstPhaseState,
  TmstPresenceActionPayload,
  TmstPrivatePromptReadyEvent,
  TmstPrivatePromptReadyPayload,
  TmstRevealResolvedEvent,
  TmstRevealResolvedPayload,
  TmstScoreboardReadyEvent,
  TmstScoreboardReadyPayload,
  TmstSpotlightPhaseState,
  TmstSpotlightSkippedEvent,
  TmstSpotlightSkippedPayload,
  TmstSpotlightStartedEvent,
  TmstSpotlightStartedPayload,
  TmstSubmissionPayload,
  TmstVoteActionPayload,
  TmstVoteBreakdown,
  TypedContentEvent,
} from "./types.js";

import type {
  TypedContentEvent,
  MiniGamePayload,
  MiniGameState,
  MiniGameSubmissionResult,
  PlayerInput,
  CharacterDetail,
} from "./types.js";

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

  onEvent(callback: (event: TypedContentEvent) => void): () => void {
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

  async getMiniGameState(): Promise<MiniGameState | null> {
    const url = `${this._baseUrl}/v1/sessions/${this._sessionId}/mini-games/active`;
    let res: Response;
    try {
      res = await fetch(url, {
        headers: { Authorization: `Bearer ${this._playerToken}` },
      });
    } catch {
      return null;
    }
    if (res.status === 404) return null;
    if (!res.ok) {
      throw new Error(
        `getMiniGameState failed: ${res.status} ${res.statusText}`,
      );
    }
    const data = (await res.json()) as {
      run_id: string;
      game_id: string;
      mechanic_type: string | null;
      status: MiniGameState["status"];
      deadline_at: string | null;
      phase_state: MiniGameState["phaseState"];
      my_submissions: Array<{
        submission_id: string;
        is_accepted: boolean;
        rejection_reason?: string | null;
      }>;
    };
    return {
      runId: data.run_id,
      gameId: data.game_id,
      mechanicType: data.mechanic_type,
      status: data.status,
      deadlineAt: data.deadline_at,
      phaseState: data.phase_state,
      mySubmissions: data.my_submissions.map((s) => ({
        submissionId: s.submission_id,
        isAccepted: s.is_accepted,
        rejectionReason: s.rejection_reason ?? undefined,
      })),
    };
  }

  async submitMiniGameAction(
    runId: string,
    submissionId: string,
    payload: MiniGamePayload,
  ): Promise<MiniGameSubmissionResult> {
    const url = `${this._baseUrl}/v1/sessions/${this._sessionId}/mini-games/${runId}/submissions`;
    const res = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${this._playerToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ submission_id: submissionId, payload }),
    });
    if (!res.ok) {
      throw new Error(
        `submitMiniGameAction failed: ${res.status} ${res.statusText}`,
      );
    }
    const data = (await res.json()) as {
      submission_id: string;
      is_accepted: boolean;
      rejection_reason?: string | null;
    };
    return {
      submissionId: data.submission_id,
      isAccepted: data.is_accepted,
      rejectionReason: data.rejection_reason ?? undefined,
    };
  }

  disconnect(): void {
    this._connected = false;
    if (this._reader) {
      void this._reader.cancel();
      this._reader = null;
    }
  }

  private async _streamEvents(
    callback: (event: TypedContentEvent) => void,
    isReconnect: boolean,
  ): Promise<void> {
    const url = `${this._baseUrl}/v1/sessions/${this._sessionId}/events?since=${this._lastSequenceNumber}`;
    let res: Response;
    try {
      res = await fetch(url, {
        headers: { Authorization: `Bearer ${this._playerToken}` },
      });
    } catch {
      // Network failure before the stream even opened counts as an
      // unexpected end exactly like a mid-stream drop: retry once rather
      // than leaving the player's screen silently frozen.
      return this._reconnectOnce(callback, isReconnect);
    }

    if (!res.ok || !res.body) {
      return this._reconnectOnce(callback, isReconnect);
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
                const event = JSON.parse(json) as TypedContentEvent;
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

    return this._reconnectOnce(callback, isReconnect);
  }

  /** Single reconnect attempt on unexpected stream end, whether that end
   * came from a fetch failure, a non-OK response, or the stream closing
   * mid-session. */
  private async _reconnectOnce(
    callback: (event: TypedContentEvent) => void,
    isReconnect: boolean,
  ): Promise<void> {
    if (this._connected && !isReconnect) {
      await this._streamEvents(callback, true);
    }
  }
}
