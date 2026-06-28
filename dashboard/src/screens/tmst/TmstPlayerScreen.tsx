import type { CSSProperties } from "react";
import { useEffect, useRef, useState } from "react";
import { ArcwrightClient, isTmstEvent } from "@arcwright/sdk";
import type {
  MiniGameState,
  TmstRevealResolvedEvent,
  TmstScoreboardReadyEvent,
  TmstSpotlightSkippedEvent,
  TmstInputPhaseState,
  TmstSpotlightPhaseState,
} from "@arcwright/sdk";

interface Props {
  sessionId: string;
  playerToken: string;
  characterId: string;
}

type PlayerPhase =
  | "loading"
  | "input"
  | "input-submitted"
  | "spotlight-watching" // spotlighted player: look at screen
  | "spotlight-voting" // other players: voting buttons
  | "spotlight-voted" // voted; waiting for reveal
  | "reveal-success"
  | "reveal-failure"
  | "reveal-abstained"
  | "scoreboard"
  | "timeout"
  | "skipped"
  | "disconnected";

interface PlayerState {
  miniGameState: MiniGameState | null;
  phase: PlayerPhase;
  revealEvent: TmstRevealResolvedEvent | null;
  scoreboardEvent: TmstScoreboardReadyEvent | null;
  // The vote the player submitted during the current spotlight, tracked
  // client-side only for reveal feedback. Server owns the authoritative outcome.
  myVote: "truth" | "lie" | null;
  disconnected: boolean;
}

function derivePhase(
  mgState: MiniGameState | null,
  revealEvent: TmstRevealResolvedEvent | null,
  scoreboardEvent: TmstScoreboardReadyEvent | null,
  skippedEvent: TmstSpotlightSkippedEvent | null,
  myVote: "truth" | "lie" | null,
  disconnected: boolean,
  prevPhase: PlayerPhase,
): PlayerPhase {
  if (disconnected) return "disconnected";
  if (!mgState || mgState.status === "pending") return "loading";
  if (mgState.status === "timed_out" || mgState.status === "cancelled")
    return "timeout";
  if (scoreboardEvent || mgState.status === "completed") return "scoreboard";

  if (revealEvent) {
    const { declared_truth } = revealEvent.payload;
    if (myVote === null) return "reveal-abstained";
    const guessedCorrectly =
      (myVote === "truth" && declared_truth) ||
      (myVote === "lie" && !declared_truth);
    return guessedCorrectly ? "reveal-success" : "reveal-failure";
  }

  if (skippedEvent) return "skipped";

  const ps = mgState.phaseState;
  if (ps?.phase === "input") {
    return ps.submitted ? "input-submitted" : "input";
  }

  if (ps?.phase === "spotlight") {
    if (ps.is_spotlighted_player) return "spotlight-watching";
    if (ps.has_voted) return "spotlight-voted";
    return ps.can_vote ? "spotlight-voting" : "spotlight-watching";
  }

  // Preserve reveal/scoreboard if we've already transitioned there
  if (
    prevPhase === "reveal-success" ||
    prevPhase === "reveal-failure" ||
    prevPhase === "reveal-abstained"
  ) {
    return prevPhase;
  }

  return "loading";
}

export default function TmstPlayerScreen({
  sessionId,
  playerToken,
  characterId,
}: Props) {
  const clientRef = useRef<ArcwrightClient | null>(null);
  const [state, setState] = useState<PlayerState>({
    miniGameState: null,
    phase: "loading",
    revealEvent: null,
    scoreboardEvent: null,
    myVote: null,
    disconnected: false,
  });
  // Tracks skipped event separately for transient display
  const [skippedEvent, setSkippedEvent] =
    useState<TmstSpotlightSkippedEvent | null>(null);

  // Text field for the statement blank (Phase 1)
  const [blankInput, setBlankInput] = useState("");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const client = new ArcwrightClient(sessionId, playerToken, characterId, "");
    clientRef.current = client;

    let latestMgState: MiniGameState | null = null;
    let latestReveal: TmstRevealResolvedEvent | null = null;
    let latestScoreboard: TmstScoreboardReadyEvent | null = null;
    let latestSkipped: TmstSpotlightSkippedEvent | null = null;
    let latestMyVote: "truth" | "lie" | null = null;

    function update(prevPhase: PlayerPhase): Partial<PlayerState> {
      const phase = derivePhase(
        latestMgState,
        latestReveal,
        latestScoreboard,
        latestSkipped,
        latestMyVote,
        false,
        prevPhase,
      );
      return {
        miniGameState: latestMgState,
        phase,
        revealEvent: latestReveal,
        scoreboardEvent: latestScoreboard,
        myVote: latestMyVote,
      };
    }

    // Poll for phase transitions
    async function poll() {
      try {
        const mgState = await client.getMiniGameState();
        latestMgState = mgState;
        setState((prev) => ({
          ...prev,
          ...update(prev.phase),
          disconnected: false,
        }));
      } catch {
        setState((prev) => ({ ...prev, disconnected: true }));
      }
    }

    poll();
    const interval = setInterval(poll, 2000);

    // Subscribe to real-time events for within-phase updates
    const unsubscribe = client.onEvent((event) => {
      if (!isTmstEvent(event)) return;

      if (event.event_type === "tmst_reveal_resolved") {
        latestReveal = event as TmstRevealResolvedEvent;
        // Clear prior skipped notice when reveal fires
        latestSkipped = null;
        setSkippedEvent(null);
        setState((prev) => ({ ...prev, ...update(prev.phase) }));
      } else if (event.event_type === "tmst_scoreboard_ready") {
        latestScoreboard = event as TmstScoreboardReadyEvent;
        setState((prev) => ({ ...prev, ...update(prev.phase) }));
      } else if (event.event_type === "tmst_spotlight_started") {
        // New spotlight: reset reveal/skipped state for this round
        latestReveal = null;
        latestSkipped = null;
        latestMyVote = null;
        setSkippedEvent(null);
        setState((prev) => ({
          ...prev,
          myVote: null,
          revealEvent: null,
          ...update(prev.phase),
        }));
      } else if (event.event_type === "tmst_spotlight_skipped") {
        const ev = event as TmstSpotlightSkippedEvent;
        latestSkipped = ev;
        setSkippedEvent(ev);
        setState((prev) => ({ ...prev, ...update(prev.phase) }));
        // Transient: auto-clear after 3 seconds
        setTimeout(() => {
          latestSkipped = null;
          setSkippedEvent(null);
          setState((prev) => ({ ...prev, ...update(prev.phase) }));
        }, 3000);
      }
    });

    return () => {
      clearInterval(interval);
      unsubscribe();
      client.disconnect();
      clientRef.current = null;
    };
  }, [sessionId, playerToken, characterId]);

  // Sync skippedEvent into phase derivation
  useEffect(() => {
    setState((prev) => {
      const phase = derivePhase(
        prev.miniGameState,
        prev.revealEvent,
        prev.scoreboardEvent,
        skippedEvent,
        prev.myVote,
        prev.disconnected,
        prev.phase,
      );
      return { ...prev, phase };
    });
  }, [skippedEvent]);

  async function submitInput(declaredTruth: boolean) {
    const client = clientRef.current;
    if (!client || !state.miniGameState) return;
    if (!blankInput.trim()) {
      setSubmitError("Enter something in the blank first.");
      return;
    }
    setSubmitting(true);
    setSubmitError(null);
    try {
      await client.submitMiniGameAction(
        state.miniGameState.runId,
        crypto.randomUUID(),
        {
          action: "input",
          statement_text: blankInput.trim(),
          declared_truth: declaredTruth,
        },
      );
    } catch (e) {
      setSubmitError(
        e instanceof Error ? e.message : "Submission failed. Try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function castVote(vote: "truth" | "lie") {
    const client = clientRef.current;
    if (!client || !state.miniGameState) return;
    const ps = state.miniGameState.phaseState as TmstSpotlightPhaseState | null;
    if (!ps || ps.phase !== "spotlight") return;
    setSubmitting(true);
    try {
      await client.submitMiniGameAction(
        state.miniGameState.runId,
        crypto.randomUUID(),
        { action: "vote", target_character_id: ps.target_character_id, vote },
      );
      setState((prev) => ({ ...prev, myVote: vote, phase: "spotlight-voted" }));
    } catch (e) {
      setSubmitError(
        e instanceof Error ? e.message : "Vote failed. Try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  const { phase, miniGameState, revealEvent, scoreboardEvent } = state;
  const inputPhaseState =
    miniGameState?.phaseState?.phase === "input"
      ? (miniGameState.phaseState as TmstInputPhaseState)
      : null;

  return (
    <div style={styles.root} role="main">
      <div style={styles.card}>
        <h1 style={styles.title}>NIGHTCAP</h1>
        <p style={styles.subtitle}>Tell Me Something True</p>

        {phase === "disconnected" && (
          <PlayerHold role="status">
            <p style={styles.holdText}>Reconnecting...</p>
          </PlayerHold>
        )}

        {phase === "loading" && (
          <PlayerHold>
            <p style={styles.hint}>One moment...</p>
          </PlayerHold>
        )}

        {phase === "timeout" && (
          <PlayerHold role="status">
            <p style={styles.holdText}>Time&apos;s up.</p>
            <p style={styles.hint}>Waiting for the next phase...</p>
          </PlayerHold>
        )}

        {phase === "skipped" && (
          <PlayerHold role="status">
            <p style={styles.holdText}>Disconnected player skipped.</p>
            <p style={styles.hint}>Moving to the next statement...</p>
          </PlayerHold>
        )}

        {(phase === "input" || phase === "input-submitted") &&
          inputPhaseState && (
            <InputPhasePlayer
              phaseState={inputPhaseState}
              blankInput={blankInput}
              onChange={setBlankInput}
              onSubmit={submitInput}
              submitting={submitting}
              error={submitError}
              submitted={phase === "input-submitted"}
            />
          )}

        {phase === "spotlight-watching" && (
          <PlayerHold>
            <p style={styles.holdText}>Look at the screen.</p>
          </PlayerHold>
        )}

        {(phase === "spotlight-voting" || phase === "spotlight-voted") && (
          <VotingPhasePlayer
            voted={phase === "spotlight-voted"}
            submitting={submitting}
            error={submitError}
            onVote={castVote}
          />
        )}

        {(phase === "reveal-success" ||
          phase === "reveal-failure" ||
          phase === "reveal-abstained") &&
          revealEvent && (
            <RevealPhasePlayer
              outcome={
                phase === "reveal-abstained"
                  ? "abstained"
                  : phase === "reveal-success"
                    ? "success"
                    : "failure"
              }
              declaredTruth={revealEvent.payload.declared_truth}
            />
          )}

        {phase === "scoreboard" && (
          <PlayerHold>
            <p style={styles.holdText}>Look at the screen.</p>
            {scoreboardEvent?.payload.all_truth_round && (
              <p style={styles.hint}>Everyone told the truth this round.</p>
            )}
            {scoreboardEvent?.payload.all_lie_round && (
              <p style={styles.hint}>Everyone lied this round.</p>
            )}
          </PlayerHold>
        )}
      </div>
    </div>
  );
}

function PlayerHold({
  children,
  role,
}: {
  children: React.ReactNode;
  role?: string;
}) {
  return (
    <div style={styles.holdBlock} role={role}>
      {children}
    </div>
  );
}

function InputPhasePlayer({
  phaseState,
  blankInput,
  onChange,
  onSubmit,
  submitting,
  error,
  submitted,
}: {
  phaseState: TmstInputPhaseState;
  blankInput: string;
  onChange: (v: string) => void;
  onSubmit: (truth: boolean) => void;
  submitting: boolean;
  error: string | null;
  submitted: boolean;
}) {
  if (submitted || phaseState.submitted) {
    return (
      <div style={styles.holdBlock} role="status">
        <p style={styles.holdText}>Submitted.</p>
        <p style={styles.hint}>
          Watch the screen — the game is about to begin.
        </p>
      </div>
    );
  }

  return (
    <div style={styles.inputBlock}>
      {/* TODO: the player's fact with the blank should come from
          TmstPrivatePromptReady event payload once the engine sends it.
          Currently showing a placeholder. */}
      <p style={styles.factLabel}>YOUR STATEMENT</p>
      <p style={styles.factText}>
        [Your character&apos;s fact with one word blanked out will appear here.]
      </p>

      <label htmlFor="blank-input" style={styles.fieldLabel}>
        Fill in the blank
      </label>
      <input
        id="blank-input"
        type="text"
        value={blankInput}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Your answer..."
        maxLength={120}
        disabled={submitting}
        style={styles.input}
        autoFocus
        autoComplete="off"
      />

      {error && (
        <p style={styles.error} role="alert">
          {error}
        </p>
      )}

      <div style={styles.buttonRow}>
        <button
          type="button"
          onClick={() => onSubmit(true)}
          disabled={submitting}
          style={{
            ...styles.button,
            background: "var(--accent)",
            color: "#0a0a0f",
          }}
          aria-label="Submit as truth"
        >
          {submitting ? "Submitting..." : "Submit Truth"}
        </button>
        <button
          type="button"
          onClick={() => onSubmit(false)}
          disabled={submitting}
          style={{
            ...styles.button,
            background: "var(--surface)",
            color: "var(--text)",
            border: "1px solid var(--border)",
          }}
          aria-label="Submit as lie"
        >
          {submitting ? "Submitting..." : "Submit Lie"}
        </button>
      </div>
    </div>
  );
}

function VotingPhasePlayer({
  voted,
  submitting,
  error,
  onVote,
}: {
  voted: boolean;
  submitting: boolean;
  error: string | null;
  onVote: (v: "truth" | "lie") => void;
}) {
  if (voted) {
    return (
      <div style={styles.holdBlock} role="status">
        <p style={styles.holdText}>Vote cast.</p>
        <p style={styles.hint}>Waiting for the reveal...</p>
      </div>
    );
  }

  return (
    <div style={styles.inputBlock}>
      <p style={styles.factLabel}>TRUTH OR LIE?</p>
      <p style={styles.factText}>Watch the screen and decide.</p>

      {error && (
        <p style={styles.error} role="alert">
          {error}
        </p>
      )}

      <div style={styles.buttonRow}>
        <button
          type="button"
          onClick={() => onVote("truth")}
          disabled={submitting || voted}
          style={{
            ...styles.button,
            background: "var(--accent)",
            color: "#0a0a0f",
          }}
          aria-label="Vote truth"
        >
          Truth
        </button>
        <button
          type="button"
          onClick={() => onVote("lie")}
          disabled={submitting || voted}
          style={{
            ...styles.button,
            background: "var(--surface)",
            color: "var(--text)",
            border: "1px solid var(--border)",
          }}
          aria-label="Vote lie"
        >
          Lie
        </button>
      </div>
    </div>
  );
}

function RevealPhasePlayer({
  outcome,
  declaredTruth,
}: {
  outcome: "success" | "failure" | "abstained";
  declaredTruth: boolean;
}) {
  const messages: Record<
    string,
    { headline: string; sub: string; color: string }
  > = {
    success: {
      headline: "Correct!",
      sub: `That was ${declaredTruth ? "the truth" : "a lie"} — and you knew it.`,
      color: "var(--accent)",
    },
    failure: {
      headline: "Wrong.",
      sub: `That was ${declaredTruth ? "the truth" : "a lie"} — you were fooled.`,
      color: "var(--red)",
    },
    abstained: {
      headline: "No vote.",
      sub: "You did not vote in time.",
      color: "var(--text-muted)",
    },
  };

  const msg = messages[outcome];
  return (
    <div style={styles.holdBlock} role="status">
      <p style={{ ...styles.holdText, color: msg.color }}>{msg.headline}</p>
      <p style={styles.hint}>{msg.sub}</p>
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
    marginBottom: "2rem",
  },
  holdBlock: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "0.75rem",
    marginTop: "1rem",
    width: "100%",
  },
  holdText: {
    fontSize: "1.8rem",
    color: "var(--text)",
    lineHeight: 1.3,
  },
  hint: {
    fontSize: "0.9rem",
    color: "var(--text-muted)",
    fontStyle: "italic",
  },
  inputBlock: {
    display: "flex",
    flexDirection: "column",
    gap: "0.75rem",
    width: "100%",
    marginTop: "0.5rem",
    textAlign: "left",
  },
  factLabel: {
    fontSize: "0.75rem",
    letterSpacing: "0.15em",
    color: "var(--text-muted)",
    textTransform: "uppercase",
  },
  factText: {
    fontSize: "1.05rem",
    color: "var(--text)",
    lineHeight: 1.5,
    padding: "0.9rem 1rem",
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "6px",
    marginBottom: "0.25rem",
  },
  fieldLabel: {
    fontSize: "0.75rem",
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
    fontSize: "0.85rem",
  },
  buttonRow: {
    display: "flex",
    flexDirection: "column",
    gap: "0.75rem",
    marginTop: "0.5rem",
  },
  button: {
    padding: "1rem",
    border: "none",
    borderRadius: "6px",
    fontSize: "1rem",
    fontWeight: "bold",
    letterSpacing: "0.05em",
    fontFamily: "inherit",
    cursor: "pointer",
  },
};
