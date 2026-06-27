import type { CSSProperties } from "react";
import { useEffect, useRef, useState } from "react";
import { fetchLobbyState } from "../api/lobby";
import type { LobbyState } from "../api/lobby";

interface Props {
  sessionId: string;
}

export default function DisplayScreen({ sessionId }: Props) {
  const [lobby, setLobby] = useState<LobbyState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    async function poll() {
      try {
        const state = await fetchLobbyState(sessionId);
        setLobby(state);
        setError(null);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Connection error");
      }
    }

    poll();
    intervalRef.current = setInterval(poll, 2000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [sessionId]);

  if (error) {
    return (
      <div style={styles.centered}>
        <p style={{ color: "var(--red)", fontSize: "1.2rem" }}>{error}</p>
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
