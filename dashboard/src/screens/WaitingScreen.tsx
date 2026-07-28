import type { CSSProperties } from "react";
import { FormEvent, useEffect, useRef, useState } from "react";
import { ArcwrightClient } from "@arcwright/sdk";
import type { MiniGameState, PlayerInput } from "@arcwright/sdk";
import { getValidPlayerToken, loadPlayerAuth } from "../api/auth";
import { fetchLobbyState } from "../api/lobby";
import type { LobbyState } from "../api/lobby";
import { fetchPlayerMiniGameState } from "../api/miniGame";
import TmstPlayerScreen from "./tmst/TmstPlayerScreen";

const TMST_GAME_ID = "tell-me-something-true";

function readParams(): {
  name: string;
  sessionId: string | null;
  hasPlayerAuth: boolean;
  characterId: string | null;
} {
  const p = new URLSearchParams(window.location.search);
  return {
    name: p.get("name") ?? "You",
    sessionId: p.get("session_id"),
    hasPlayerAuth: p.get("session_id")
      ? loadPlayerAuth(p.get("session_id")!) !== null
      : false,
    characterId: p.get("character_id"),
  };
}

export default function WaitingScreen() {
  const { name, sessionId, hasPlayerAuth, characterId } = readParams();

  const [miniGameState, setMiniGameState] = useState<MiniGameState | null>(
    null,
  );
  const [lobby, setLobby] = useState<LobbyState | null>(null);
  const [action, setAction] = useState("Continue investigating.");
  const [actionStatus, setActionStatus] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const clientRef = useRef<ArcwrightClient | null>(null);

  // The player token is kept in sessionStorage and is only used for
  // authenticated action submissions.
  const hasCredentials =
    sessionId !== null && hasPlayerAuth && characterId !== null;

  useEffect(() => {
    if (!hasCredentials) return;
    clientRef.current = new ArcwrightClient(
      sessionId!,
      () => getValidPlayerToken(sessionId!),
      characterId!,
      "",
    );
    return () => {
      clientRef.current?.disconnect();
      clientRef.current = null;
    };
  }, [characterId, hasCredentials, sessionId]);

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
        setLobby(await fetchLobbyState(sessionId!));
      } catch {
        // The action form remains usable if the public lobby poll is delayed.
      }
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

  const isTerminal = lobby?.is_terminal === true;

  if (isTmstActive) {
    return (
      <TmstPlayerScreen
        sessionId={sessionId!}
        playerToken={() => getValidPlayerToken(sessionId!)}
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
            {isTerminal
              ? "The case is complete."
              : hasCredentials
                ? "The host will start the case. Then submit an action to advance."
                : "Waiting for player authentication."}
          </p>
        </div>

        {isTerminal ? (
          <p style={styles.complete}>
            The case has reached The Truth. Player actions are complete.
          </p>
        ) : hasCredentials ? (
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
        ) : null}

        <p style={styles.hint}>
          {isTerminal
            ? "This rehearsal slice stops at the terminal beat; final reveal and scoreboard rendering are not enabled yet."
            : "Keep this screen open. The game will begin soon."}
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
  complete: {
    width: "100%",
    padding: "1rem",
    border: "1px solid var(--border)",
    borderRadius: "6px",
    color: "var(--accent)",
    lineHeight: 1.5,
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
