import type { CSSProperties } from "react";
import { FormEvent, useEffect, useRef, useState } from "react";
import { ArcwrightClient } from "@arcwright/sdk";
import type { MiniGameState, PlayerInput } from "@arcwright/sdk";
import { loadPlayerToken } from "../api/auth";
import { fetchPlayerMiniGameState } from "../api/miniGame";
import TmstPlayerScreen from "./tmst/TmstPlayerScreen";

const TMST_GAME_ID = "tell-me-something-true";

function readParams(): {
  name: string;
  sessionId: string | null;
  playerToken: string | null;
  characterId: string | null;
} {
  const p = new URLSearchParams(window.location.search);
  return {
    name: p.get("name") ?? "You",
    sessionId: p.get("session_id"),
    playerToken: p.get("session_id")
      ? loadPlayerToken(p.get("session_id")!)
      : null,
    characterId: p.get("character_id"),
  };
}

export default function WaitingScreen() {
  const { name, sessionId, playerToken, characterId } = readParams();

  const [miniGameState, setMiniGameState] = useState<MiniGameState | null>(
    null,
  );
  const [action, setAction] = useState("Continue investigating.");
  const [actionStatus, setActionStatus] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const clientRef = useRef<ArcwrightClient | null>(null);

  // The player token is kept in sessionStorage and is only used for
  // authenticated action submissions.
  const hasCredentials =
    sessionId !== null && playerToken !== null && characterId !== null;

  useEffect(() => {
    if (!hasCredentials) return;
    clientRef.current = new ArcwrightClient(
      sessionId!,
      playerToken!,
      characterId!,
      "",
    );
    return () => {
      clientRef.current?.disconnect();
      clientRef.current = null;
    };
  }, [characterId, hasCredentials, playerToken, sessionId]);

  async function submitAction(event: FormEvent) {
    event.preventDefault();
    const client = clientRef.current;
    if (!client) {
      setActionStatus("Player session is not authenticated yet.");
      return;
    }

    setSubmitting(true);
    setActionStatus(null);
    const input: PlayerInput = { kind: "action", content: action.trim() };
    try {
      await client.submitInput(characterId!, input);
      setActionStatus("Action submitted. The session advanced.");
    } catch (error) {
      setActionStatus(error instanceof Error ? error.message : String(error));
    } finally {
      setSubmitting(false);
    }
  }

  useEffect(() => {
    if (!hasCredentials) return;

    async function poll() {
      try {
        const mgState = await fetchPlayerMiniGameState(
          sessionId!,
          characterId!,
        );
        setMiniGameState(mgState);
      } catch {
        // Swallow; TmstPlayerScreen handles disconnected state internally
      }
    }

    poll();
    const interval = setInterval(poll, 2000);
    return () => clearInterval(interval);
  }, [hasCredentials, sessionId, characterId]);

  const isTmstActive =
    hasCredentials &&
    miniGameState !== null &&
    miniGameState.gameId === TMST_GAME_ID &&
    miniGameState.status === "active";

  if (isTmstActive) {
    return (
      <TmstPlayerScreen
        sessionId={sessionId!}
        playerToken={playerToken ?? ""}
        characterId={characterId!}
      />
    );
  }

  return (
    <div style={styles.root}>
      <div style={styles.card}>
        <h1 style={styles.title}>NIGHTCAP</h1>
        <p style={styles.subtitle}>A Murder Mystery</p>

        <div style={styles.messageBlock}>
          <p style={styles.greeting}>You&apos;re in, {name}.</p>
          <p style={styles.waiting}>
            {hasCredentials
              ? "The host will start the case. Then submit an action to advance."
              : "Waiting for player authentication."}
          </p>
        </div>

        {hasCredentials && (
          <form onSubmit={submitAction} style={styles.actionForm}>
            <label htmlFor="action" style={styles.label}>
              Action
            </label>
            <input
              id="action"
              value={action}
              onChange={(event) => setAction(event.target.value)}
              disabled={submitting}
              style={styles.input}
            />
            <button type="submit" disabled={submitting} style={styles.button}>
              {submitting ? "Sending..." : "Submit action"}
            </button>
            {actionStatus && <p style={styles.hint}>{actionStatus}</p>}
          </form>
        )}

        <p style={styles.hint}>
          Keep this screen open. The game will begin soon.
        </p>
      </div>
    </div>
  );
}

const styles: Record<string, CSSProperties> = {
  root: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "100vh",
    padding: "1.5rem",
    background: "var(--bg)",
  },
  card: {
    width: "100%",
    maxWidth: "420px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "0.5rem",
    textAlign: "center",
  },
  title: {
    fontSize: "2.5rem",
    letterSpacing: "0.3em",
    color: "var(--accent)",
  },
  subtitle: {
    fontSize: "0.85rem",
    letterSpacing: "0.2em",
    color: "var(--text-muted)",
    textTransform: "uppercase",
    marginBottom: "2.5rem",
  },
  messageBlock: {
    display: "flex",
    flexDirection: "column",
    gap: "1rem",
    marginBottom: "2rem",
  },
  greeting: {
    fontSize: "1.8rem",
    color: "var(--text)",
    lineHeight: 1.3,
  },
  waiting: {
    fontSize: "1.1rem",
    color: "var(--text-muted)",
    fontStyle: "italic",
  },
  hint: {
    fontSize: "0.8rem",
    color: "var(--text-muted)",
    letterSpacing: "0.05em",
  },
  actionForm: {
    width: "100%",
    display: "flex",
    flexDirection: "column",
    gap: "0.75rem",
  },
  label: {
    fontSize: "0.8rem",
    letterSpacing: "0.1em",
    color: "var(--text-muted)",
    textTransform: "uppercase",
  },
  input: {
    width: "100%",
    padding: "0.9rem 1rem",
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "6px",
    color: "var(--text)",
    fontSize: "1.1rem",
    outline: "none",
  },
  button: {
    padding: "1rem",
    background: "var(--accent)",
    color: "#0a0a0f",
    border: "none",
    borderRadius: "6px",
    fontSize: "1rem",
    fontWeight: "bold",
    letterSpacing: "0.05em",
  },
};
