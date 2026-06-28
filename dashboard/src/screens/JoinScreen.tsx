import type { CSSProperties, FormEvent } from "react";
import { useState } from "react";
import { joinLobby } from "../api/lobby";

export default function JoinScreen() {
  const params = new URLSearchParams(window.location.search);
  const codeFromUrl = params.get("code") ?? "";

  const [name, setName] = useState("");
  const [code, setCode] = useState(codeFromUrl.toUpperCase());
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) {
      setError("Enter your name to join.");
      return;
    }
    if (!code.trim()) {
      setError("Enter the code shown on the screen.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await joinLobby(name.trim(), code.trim());
      const params = new URLSearchParams({
        name: result.display_name,
        session_id: result.session_id,
      });
      if (result.player_token) params.set("player_token", result.player_token);
      if (result.character_id) params.set("character_id", result.character_id);
      window.location.href = `/waiting?${params.toString()}`;
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Something went wrong. Try again.",
      );
      setLoading(false);
    }
  }

  return (
    <div style={styles.root}>
      <div style={styles.card}>
        <h1 style={styles.title}>NIGHTCAP</h1>
        <p style={styles.subtitle}>A Murder Mystery</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label} htmlFor="name">
            Your name
          </label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Jordan"
            maxLength={64}
            disabled={loading}
            style={styles.input}
            autoFocus
            autoComplete="given-name"
          />

          <label style={styles.label} htmlFor="code">
            Join code (from the screen)
          </label>
          <input
            id="code"
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            placeholder="e.g. ABC123"
            maxLength={8}
            disabled={loading}
            style={{
              ...styles.input,
              letterSpacing: "0.3em",
              textAlign: "center",
            }}
          />

          {error && <p style={styles.error}>{error}</p>}

          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? "Joining..." : "Join the game"}
          </button>
        </form>
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
    marginBottom: "2rem",
  },
  form: {
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
  error: {
    color: "var(--red)",
    fontSize: "0.9rem",
    textAlign: "center",
  },
  button: {
    marginTop: "0.5rem",
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
