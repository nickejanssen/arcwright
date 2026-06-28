import type { CSSProperties } from "react";
import { useEffect, useRef, useState } from "react";
import { isTmstEvent } from "@arcwright/sdk";
import type {
  MiniGameState,
  TmstRevealResolvedEvent,
  TmstScoreboardReadyEvent,
  TmstSpotlightStartedEvent,
  TypedContentEvent,
} from "@arcwright/sdk";
import { fetchLobbyState } from "../api/lobby";
import type { LobbyState } from "../api/lobby";
import { fetchDisplayMiniGameState } from "../api/miniGame";
import TmstDisplayScreen from "./tmst/TmstDisplayScreen";

const TMST_GAME_ID = "tell-me-something-true";

interface Props {
  sessionId: string;
}

interface TmstEventState {
  revealEvent: TmstRevealResolvedEvent | null;
  scoreboardEvent: TmstScoreboardReadyEvent | null;
  currentSpotlightEvent: TmstSpotlightStartedEvent | null;
  skippedCharacterId: string | null;
}

export default function DisplayScreen({ sessionId }: Props) {
  const [lobby, setLobby] = useState<LobbyState | null>(null);
  const [miniGameState, setMiniGameState] = useState<MiniGameState | null>(
    null,
  );
  const [tmstEvents, setTmstEvents] = useState<TmstEventState>({
    revealEvent: null,
    scoreboardEvent: null,
    currentSpotlightEvent: null,
    skippedCharacterId: null,
  });
  const [lobbyError, setLobbyError] = useState<string | null>(null);
  const [disconnected, setDisconnected] = useState(false);

  const skippedTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const sseActiveRef = useRef(true);
  const sseSeqRef = useRef(0);

  // Lobby + mini-game state polling
  useEffect(() => {
    async function poll() {
      // Lobby poll (for pre-game display)
      try {
        const state = await fetchLobbyState(sessionId);
        setLobby(state);
        setLobbyError(null);
      } catch (e) {
        setLobbyError(e instanceof Error ? e.message : "Connection error");
      }

      // Mini-game poll (unauthenticated — display surface)
      try {
        const mgState = await fetchDisplayMiniGameState(sessionId);
        setMiniGameState(mgState);
        setDisconnected(false);
      } catch {
        setDisconnected(true);
      }
    }

    poll();
    const interval = setInterval(poll, 2000);
    return () => clearInterval(interval);
  }, [sessionId]);

  // SSE event subscription for the display surface (no auth; best-effort).
  // Provides within-phase real-time updates for reveal/scoreboard/skipped events.
  useEffect(() => {
    sseActiveRef.current = true;

    function handleEvent(event: TypedContentEvent) {
      if (!isTmstEvent(event)) return;

      if (event.event_type === "tmst_spotlight_started") {
        const ev = event as TmstSpotlightStartedEvent;
        setTmstEvents((prev) => ({
          ...prev,
          currentSpotlightEvent: ev,
          revealEvent: null,
          skippedCharacterId: null,
        }));
      } else if (event.event_type === "tmst_reveal_resolved") {
        setTmstEvents((prev) => ({
          ...prev,
          revealEvent: event as TmstRevealResolvedEvent,
          skippedCharacterId: null,
        }));
      } else if (event.event_type === "tmst_scoreboard_ready") {
        setTmstEvents((prev) => ({
          ...prev,
          scoreboardEvent: event as TmstScoreboardReadyEvent,
        }));
      } else if (event.event_type === "tmst_spotlight_skipped") {
        const characterId = (event.payload as { target_character_id: string })
          .target_character_id;
        setTmstEvents((prev) => ({ ...prev, skippedCharacterId: characterId }));
        if (skippedTimerRef.current) clearTimeout(skippedTimerRef.current);
        skippedTimerRef.current = setTimeout(() => {
          setTmstEvents((prev) => ({ ...prev, skippedCharacterId: null }));
        }, 3000);
      }
    }

    async function streamDisplayEvents() {
      const url = `/v1/sessions/${sessionId}/events?since=${sseSeqRef.current}`;
      let res: Response;
      try {
        res = await fetch(url);
      } catch {
        return;
      }
      if (!res.ok || !res.body) return;

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";

      try {
        while (sseActiveRef.current) {
          const { done, value } = await reader.read();
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
                  sseSeqRef.current = event.sequence_number;
                  handleEvent(event);
                } catch {
                  // malformed SSE; skip
                }
              }
            }
          }
        }
      } finally {
        reader.cancel().catch(() => undefined);
      }

      // Retry after a short delay if still active
      if (sseActiveRef.current) {
        setTimeout(streamDisplayEvents, 3000);
      }
    }

    streamDisplayEvents();

    return () => {
      sseActiveRef.current = false;
      if (skippedTimerRef.current) clearTimeout(skippedTimerRef.current);
    };
  }, [sessionId]);

  const isTmstActive =
    miniGameState !== null &&
    miniGameState.gameId === TMST_GAME_ID &&
    miniGameState.status === "active";

  if (isTmstActive) {
    return (
      <TmstDisplayScreen
        miniGameState={miniGameState}
        revealEvent={tmstEvents.revealEvent}
        scoreboardEvent={tmstEvents.scoreboardEvent}
        currentSpotlightEvent={tmstEvents.currentSpotlightEvent}
        skippedCharacterId={tmstEvents.skippedCharacterId}
        disconnected={disconnected}
      />
    );
  }

  // ---- Lobby view (pre-game or non-TMST state) ----

  if (lobbyError) {
    return (
      <div style={styles.centered}>
        <p style={{ color: "var(--red)", fontSize: "1.2rem" }}>{lobbyError}</p>
        <p style={{ color: "var(--text-muted)", marginTop: "0.5rem" }}>
          Make sure the engine is running at localhost:8000
        </p>
      </div>
    );
  }

  if (!lobby) {
    return (
      <div style={styles.centered}>
        <p style={{ color: "var(--text-muted)", fontStyle: "italic" }}>
          Connecting...
        </p>
      </div>
    );
  }

  const joinUrl = lobby.join_code
    ? `${window.location.origin}/join?code=${lobby.join_code}`
    : null;

  return (
    <div style={styles.root}>
      <div style={styles.header}>
        <span style={styles.brand}>NIGHTCAP</span>
        <span style={styles.tagline}>A Murder Mystery</span>
      </div>

      <div style={styles.main}>
        <div style={styles.joinPanel}>
          <p style={styles.joinLabel}>JOIN THE GAME</p>

          {joinUrl && (
            <img
              src={`https://api.qrserver.com/v1/create-qr-code/?size=220x220&bgcolor=0a0a0f&color=c8a96e&data=${encodeURIComponent(joinUrl)}`}
              alt="QR code to join"
              style={styles.qr}
            />
          )}

          {lobby.join_code ? (
            <div style={styles.codeBlock}>
              <p style={styles.codeLabel}>or enter code</p>
              <p style={styles.code}>{lobby.join_code}</p>
            </div>
          ) : (
            <p style={{ color: "var(--text-muted)" }}>No join code yet</p>
          )}

          <p style={styles.urlHint}>{window.location.origin}/join</p>
        </div>

        <div style={styles.playerPanel}>
          <p style={styles.playerLabel}>
            {lobby.player_count === 0
              ? "Waiting for players to arrive..."
              : `${lobby.player_count} player${lobby.player_count !== 1 ? "s" : ""} in the room`}
          </p>

          <ul style={styles.playerList}>
            {lobby.players.map((p) => (
              <li key={p.participant_id} style={styles.playerItem}>
                <span style={styles.bullet}>&#x2022;</span>
                {p.display_name ?? "Anonymous"}
              </li>
            ))}
          </ul>

          {lobby.status === "created" && lobby.player_count >= 4 && (
            <p style={styles.readyHint}>
              Ready to start — 4+ players in the room
            </p>
          )}
        </div>
      </div>

      <div style={styles.footer}>
        <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>
          Powered by Arcwright
        </span>
      </div>
    </div>
  );
}

const styles: Record<string, CSSProperties> = {
  root: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    padding: "2rem 3rem",
    background: "var(--bg)",
  },
  centered: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "100vh",
  },
  header: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    marginBottom: "2rem",
  },
  brand: {
    fontSize: "clamp(2.5rem, 5vw, 4.5rem)",
    letterSpacing: "0.3em",
    color: "var(--accent)",
    fontFamily: "'Georgia', serif",
  },
  tagline: {
    fontSize: "1rem",
    letterSpacing: "0.25em",
    color: "var(--text-muted)",
    textTransform: "uppercase",
    marginTop: "0.25rem",
  },
  main: {
    display: "flex",
    flex: 1,
    gap: "4rem",
    alignItems: "flex-start",
    justifyContent: "center",
  },
  joinPanel: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "1rem",
    minWidth: "260px",
  },
  joinLabel: {
    fontSize: "0.85rem",
    letterSpacing: "0.2em",
    color: "var(--text-muted)",
    textTransform: "uppercase",
  },
  qr: {
    width: 220,
    height: 220,
    borderRadius: "8px",
    border: "2px solid var(--border)",
  },
  codeBlock: {
    textAlign: "center",
  },
  codeLabel: {
    fontSize: "0.75rem",
    color: "var(--text-muted)",
    letterSpacing: "0.1em",
    marginBottom: "0.25rem",
  },
  code: {
    fontSize: "var(--code-size)",
    letterSpacing: "0.2em",
    color: "var(--accent)",
    fontFamily: "'Georgia', serif",
    fontWeight: "bold",
  },
  urlHint: {
    fontSize: "0.85rem",
    color: "var(--text-muted)",
    letterSpacing: "0.05em",
  },
  playerPanel: {
    flex: 1,
    maxWidth: "420px",
    paddingTop: "0.5rem",
  },
  playerLabel: {
    fontSize: "1rem",
    color: "var(--text-muted)",
    letterSpacing: "0.1em",
    marginBottom: "1.5rem",
    textTransform: "uppercase",
  },
  playerList: {
    listStyle: "none",
    display: "flex",
    flexDirection: "column",
    gap: "0.75rem",
  },
  playerItem: {
    display: "flex",
    alignItems: "center",
    gap: "0.75rem",
    fontSize: "1.5rem",
    color: "var(--text)",
    borderBottom: "1px solid var(--border)",
    paddingBottom: "0.5rem",
  },
  bullet: {
    color: "var(--accent)",
    fontSize: "1.2rem",
  },
  readyHint: {
    marginTop: "2rem",
    color: "var(--accent)",
    fontSize: "0.9rem",
    letterSpacing: "0.1em",
  },
  footer: {
    display: "flex",
    justifyContent: "center",
    paddingTop: "1rem",
  },
};
