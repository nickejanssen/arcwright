import type { CSSProperties } from "react";
import { useEffect, useRef, useState } from "react";
import { ArcwrightClient } from "@arcwright/sdk";
import type { MiniGameState } from "@arcwright/sdk";
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
    playerToken: p.get("player_token"),
    characterId: p.get("character_id"),
  };
}

export default function WaitingScreen() {
  const { name, sessionId, playerToken, characterId } = readParams();

  const [miniGameState, setMiniGameState] = useState<MiniGameState | null>(
    null,
  );
  const clientRef = useRef<ArcwrightClient | null>(null);

  const hasCredentials =
    sessionId !== null && playerToken !== null && characterId !== null;

  // When the player has credentials, poll for an active mini-game so we
  // know when to hand off to the TMST player screen.
  useEffect(() => {
    if (!hasCredentials) return;

    const client = new ArcwrightClient(
      sessionId!,
      playerToken!,
      characterId!,
      "",
    );
    clientRef.current = client;

    async function poll() {
      try {
        const mgState = await client.getMiniGameState();
        setMiniGameState(mgState);
      } catch {
        // Swallow and retry on next tick; disconnected state handled inside TmstPlayerScreen
      }
    }

    poll();
    const interval = setInterval(poll, 2000);

    return () => {
      clearInterval(interval);
      client.disconnect();
      clientRef.current = null;
    };
  }, [hasCredentials, sessionId, playerToken, characterId]);

  const isTmstActive =
    hasCredentials &&
    miniGameState !== null &&
    miniGameState.gameId === TMST_GAME_ID &&
    miniGameState.status === "active";

  if (isTmstActive) {
    return (
      <TmstPlayerScreen
        sessionId={sessionId!}
        playerToken={playerToken!}
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
          <p style={styles.waiting}>Waiting for everyone else to join.</p>
        </div>

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
};
