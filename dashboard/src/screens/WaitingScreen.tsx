import type { CSSProperties } from "react";

export default function WaitingScreen() {
  const params = new URLSearchParams(window.location.search);
  const name = params.get("name") ?? "You";

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
