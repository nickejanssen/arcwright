import type { CSSProperties } from "react";
import { useEffect, useState } from "react";
import type {
  MiniGameState,
  TmstRevealResolvedEvent,
  TmstScoreboardReadyEvent,
  TmstSpotlightStartedEvent,
  TmstVoteBreakdown,
} from "@arcwright/sdk";
import { getDiegeticWrapper } from "./diegetic";

interface Props {
  miniGameState: MiniGameState;
  revealEvent: TmstRevealResolvedEvent | null;
  scoreboardEvent: TmstScoreboardReadyEvent | null;
  currentSpotlightEvent: TmstSpotlightStartedEvent | null;
  skippedCharacterId: string | null;
  disconnected: boolean;
}

type DisplayPhase =
  | "loading"
  | "input"
  | "spotlight"
  | "skipped"
  | "reveal"
  | "scoreboard"
  | "timeout"
  | "disconnected";

function resolvePhase(
  miniGameState: MiniGameState,
  revealEvent: TmstRevealResolvedEvent | null,
  scoreboardEvent: TmstScoreboardReadyEvent | null,
  currentSpotlightEvent: TmstSpotlightStartedEvent | null,
  skippedCharacterId: string | null,
  disconnected: boolean,
): DisplayPhase {
  if (disconnected && !miniGameState) return "disconnected";
  if (
    miniGameState.status === "timed_out" ||
    miniGameState.status === "cancelled"
  )
    return "timeout";
  if (scoreboardEvent || miniGameState.status === "completed")
    return "scoreboard";
  if (revealEvent) return "reveal";
  if (skippedCharacterId) return "skipped";
  if (miniGameState.phaseState?.phase === "spotlight") return "spotlight";
  if (miniGameState.phaseState?.phase === "input") return "input";
  if (miniGameState.status === "pending") return "loading";
  // Transitional: server advancing phase, waiting for next poll
  return "loading";

  // Suppress unused parameter warning for currentSpotlightEvent; it is
  // available to future callers for statement_text once the SDK exposes it.
  void currentSpotlightEvent;
}

// Countdown display only — server owns timing authority.
function useCountdown(deadlineAt: string | null): number {
  const [remaining, setRemaining] = useState(() => {
    if (!deadlineAt) return 0;
    return Math.max(
      0,
      Math.floor((new Date(deadlineAt).getTime() - Date.now()) / 1000),
    );
  });

  useEffect(() => {
    if (!deadlineAt) return;
    const tick = () => {
      setRemaining(
        Math.max(
          0,
          Math.floor((new Date(deadlineAt).getTime() - Date.now()) / 1000),
        ),
      );
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [deadlineAt]);

  return remaining;
}

function VoteBar({ breakdown }: { breakdown: TmstVoteBreakdown }) {
  const total = breakdown.truth + breakdown.lie + breakdown.abstain;
  if (total === 0) return null;
  return (
    <div style={styles.voteBar} role="group" aria-label="Vote breakdown">
      <div style={styles.voteRow}>
        <span style={{ ...styles.voteLabel, color: "var(--accent)" }}>
          TRUTH
        </span>
        <span style={styles.voteCount}>{breakdown.truth}</span>
      </div>
      <div style={styles.voteRow}>
        <span style={{ ...styles.voteLabel, color: "var(--red)" }}>LIE</span>
        <span style={styles.voteCount}>{breakdown.lie}</span>
      </div>
      {breakdown.abstain > 0 && (
        <div style={styles.voteRow}>
          <span style={{ ...styles.voteLabel, color: "var(--text-muted)" }}>
            ABSTAIN
          </span>
          <span style={styles.voteCount}>{breakdown.abstain}</span>
        </div>
      )}
    </div>
  );
}

export default function TmstDisplayScreen({
  miniGameState,
  revealEvent,
  scoreboardEvent,
  currentSpotlightEvent,
  skippedCharacterId,
  disconnected,
}: Props) {
  const phase = resolvePhase(
    miniGameState,
    revealEvent,
    scoreboardEvent,
    currentSpotlightEvent,
    skippedCharacterId,
    disconnected,
  );
  const wrapper = getDiegeticWrapper(miniGameState.gameId);

  const inputPhase =
    miniGameState.phaseState?.phase === "input"
      ? miniGameState.phaseState
      : null;
  const spotlightPhase =
    miniGameState.phaseState?.phase === "spotlight"
      ? miniGameState.phaseState
      : null;

  const countdown = useCountdown(
    phase === "input" ? (inputPhase?.deadline_at ?? null) : null,
  );

  if (phase === "disconnected") {
    return (
      <main style={styles.centered} aria-live="polite">
        <p style={{ color: "var(--text-muted)", fontStyle: "italic" }}>
          Reconnecting...
        </p>
      </main>
    );
  }

  if (phase === "loading") {
    return (
      <main style={styles.centered} aria-live="polite">
        <p style={{ color: "var(--text-muted)", fontStyle: "italic" }}>
          One moment...
        </p>
      </main>
    );
  }

  if (phase === "timeout") {
    return (
      <main style={styles.centered} aria-live="polite">
        <p style={styles.headlineSmall}>Time is up.</p>
        <p style={{ color: "var(--text-muted)", marginTop: "1rem" }}>
          Waiting for the host...
        </p>
      </main>
    );
  }

  return (
    <main style={styles.root}>
      <header style={styles.header}>
        <h1 style={styles.brand}>NIGHTCAP</h1>
        <p style={styles.wrapperTitle}>{wrapper.title}</p>
        {disconnected && (
          <p style={styles.reconnectBadge} role="status">
            Reconnecting...
          </p>
        )}
      </header>

      <section style={styles.content} aria-live="polite">
        {phase === "input" && (
          <InputPhaseDisplay
            wrapperIntro={wrapper.inputIntro}
            countdown={countdown}
          />
        )}
        {phase === "skipped" && (
          <SkippedDisplay characterId={skippedCharacterId ?? ""} />
        )}
        {phase === "spotlight" && spotlightPhase && (
          <SpotlightDisplay
            targetCharacterId={spotlightPhase.target_character_id}
            eligibleCount={spotlightPhase.eligible_voter_ids.length}
            wrapperIntro={wrapper.spotlightIntro}
          />
        )}
        {phase === "reveal" && revealEvent && (
          <RevealDisplay event={revealEvent} />
        )}
        {phase === "scoreboard" && (
          <ScoreboardDisplay event={scoreboardEvent} wrapper={wrapper} />
        )}
      </section>

      <footer style={styles.footer}>
        <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>
          Powered by Arcwright
        </span>
      </footer>
    </main>
  );
}

function InputPhaseDisplay({
  wrapperIntro,
  countdown,
}: {
  wrapperIntro: string;
  countdown: number;
}) {
  const isLow = countdown <= 10;
  return (
    <div style={styles.phaseBlock}>
      <p style={styles.narratorText}>{wrapperIntro}</p>
      <div
        style={{
          ...styles.countdown,
          color: isLow ? "var(--red)" : "var(--accent)",
        }}
        aria-label={`${countdown} seconds remaining`}
        aria-live="off"
      >
        {countdown}
      </div>
      <p style={styles.subLabel}>SECONDS REMAINING</p>
    </div>
  );
}

function SpotlightDisplay({
  targetCharacterId,
  eligibleCount,
  wrapperIntro,
}: {
  targetCharacterId: string;
  eligibleCount: number;
  wrapperIntro: string;
}) {
  return (
    <div style={styles.phaseBlock}>
      <p style={styles.narratorText}>{wrapperIntro}</p>
      <p style={styles.focusLabel}>NOW SPOTLIGHTING</p>
      {/* TODO: resolve targetCharacterId to display name once character
          name lookup is available on the display surface */}
      <p style={styles.headline}>{targetCharacterId}</p>
      {/* TODO: statement_text is not yet included in TmstSpotlightStartedEvent.
          Add statement_text to the event payload in a future AW-264 update. */}
      <p style={styles.statementPlaceholder}>[Statement revealing...]</p>
      <p style={styles.voteStatus}>
        {eligibleCount} player{eligibleCount !== 1 ? "s" : ""} voting
      </p>
      {/* TODO: live vote tally requires per-vote events not yet in SDK.
          Show truth/lie split here once tmst_vote_cast events are available. */}
    </div>
  );
}

function SkippedDisplay({ characterId }: { characterId: string }) {
  return (
    <div style={styles.phaseBlock} role="status">
      {/* TODO: resolve characterId to display name */}
      <p style={styles.headlineSmall}>
        {characterId} is disconnected — skipping to the next statement.
      </p>
    </div>
  );
}

function RevealDisplay({ event }: { event: TmstRevealResolvedEvent }) {
  const { declared_truth, statement_text, vote_breakdown } = event.payload;
  return (
    <div style={styles.phaseBlock}>
      <p style={styles.statementText}>&ldquo;{statement_text}&rdquo;</p>
      <p
        style={{
          ...styles.verdictLabel,
          color: declared_truth ? "var(--accent)" : "var(--red)",
        }}
        aria-label={declared_truth ? "That was the truth" : "That was a lie"}
      >
        {declared_truth ? "TRUTH" : "LIE"}
      </p>
      <VoteBar breakdown={vote_breakdown} />
      {/* TODO: narrator commentary — add narrator_commentary field to
          TmstRevealResolvedPayload in a future AW-264 update */}
    </div>
  );
}

function ScoreboardDisplay({
  event,
  wrapper,
}: {
  event: TmstScoreboardReadyEvent | null;
  wrapper: { allTruthMock: string; allLieMock: string };
}) {
  if (!event) {
    return (
      <div style={styles.phaseBlock} aria-live="polite">
        <p style={styles.headlineSmall}>Calculating results...</p>
      </div>
    );
  }

  const { scores, all_truth_round, all_lie_round } = event.payload;
  const sorted = Object.entries(scores).sort(([, a], [, b]) => b - a);

  return (
    <div style={styles.phaseBlock}>
      <h2 style={styles.focusLabel}>FINAL SCORES</h2>
      {all_truth_round && (
        <p style={styles.narratorText}>{wrapper.allTruthMock}</p>
      )}
      {all_lie_round && <p style={styles.narratorText}>{wrapper.allLieMock}</p>}
      <ol style={styles.leaderboard} aria-label="Final leaderboard">
        {sorted.map(([characterId, score], idx) => (
          <li key={characterId} style={styles.leaderboardRow}>
            <span style={styles.rank}>#{idx + 1}</span>
            {/* TODO: resolve characterId to display name */}
            <span style={styles.leaderboardName}>{characterId}</span>
            <span style={styles.leaderboardScore}>{score}</span>
          </li>
        ))}
      </ol>
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
    position: "relative",
  },
  brand: {
    fontSize: "clamp(2rem, 4vw, 3.5rem)",
    letterSpacing: "0.3em",
    color: "var(--accent)",
    fontFamily: "'Georgia', serif",
  },
  wrapperTitle: {
    fontSize: "1rem",
    letterSpacing: "0.25em",
    color: "var(--text-muted)",
    textTransform: "uppercase",
    marginTop: "0.25rem",
  },
  reconnectBadge: {
    position: "absolute",
    top: 0,
    right: 0,
    fontSize: "0.75rem",
    color: "var(--text-muted)",
    fontStyle: "italic",
  },
  content: {
    flex: 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  phaseBlock: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "1.5rem",
    maxWidth: "720px",
    textAlign: "center",
  },
  narratorText: {
    fontSize: "clamp(1rem, 2.5vw, 1.4rem)",
    color: "var(--text-muted)",
    fontStyle: "italic",
    lineHeight: 1.5,
    maxWidth: "600px",
  },
  countdown: {
    fontSize: "clamp(5rem, 15vw, 10rem)",
    fontFamily: "'Georgia', serif",
    lineHeight: 1,
    fontWeight: "bold",
  },
  subLabel: {
    fontSize: "0.85rem",
    letterSpacing: "0.3em",
    color: "var(--text-muted)",
    textTransform: "uppercase",
  },
  focusLabel: {
    fontSize: "0.85rem",
    letterSpacing: "0.3em",
    color: "var(--text-muted)",
    textTransform: "uppercase",
  },
  headline: {
    fontSize: "clamp(2rem, 5vw, 3.5rem)",
    color: "var(--accent)",
    fontFamily: "'Georgia', serif",
    letterSpacing: "0.1em",
  },
  headlineSmall: {
    fontSize: "clamp(1.2rem, 3vw, 2rem)",
    color: "var(--text)",
    fontFamily: "'Georgia', serif",
  },
  statementPlaceholder: {
    fontSize: "clamp(1rem, 2.5vw, 1.6rem)",
    color: "var(--text-muted)",
    fontStyle: "italic",
    padding: "1.5rem 2rem",
    border: "1px solid var(--border)",
    borderRadius: "8px",
    maxWidth: "600px",
  },
  statementText: {
    fontSize: "clamp(1.2rem, 3vw, 2rem)",
    color: "var(--text)",
    fontFamily: "'Georgia', serif",
    lineHeight: 1.4,
    padding: "1.5rem 2rem",
    border: "1px solid var(--border)",
    borderRadius: "8px",
    maxWidth: "640px",
  },
  verdictLabel: {
    fontSize: "clamp(3rem, 8vw, 6rem)",
    fontFamily: "'Georgia', serif",
    fontWeight: "bold",
    letterSpacing: "0.2em",
  },
  voteStatus: {
    fontSize: "0.9rem",
    color: "var(--text-muted)",
    letterSpacing: "0.1em",
    textTransform: "uppercase",
  },
  voteBar: {
    display: "flex",
    gap: "2rem",
    justifyContent: "center",
  },
  voteRow: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "0.25rem",
  },
  voteLabel: {
    fontSize: "0.75rem",
    letterSpacing: "0.2em",
    textTransform: "uppercase",
  },
  voteCount: {
    fontSize: "2.5rem",
    fontFamily: "'Georgia', serif",
    color: "var(--text)",
  },
  leaderboard: {
    listStyle: "none",
    display: "flex",
    flexDirection: "column",
    gap: "0.75rem",
    width: "100%",
    maxWidth: "480px",
  },
  leaderboardRow: {
    display: "flex",
    alignItems: "center",
    gap: "1rem",
    padding: "0.75rem 1.25rem",
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "6px",
    fontSize: "1.2rem",
  },
  rank: {
    color: "var(--text-muted)",
    fontSize: "0.85rem",
    minWidth: "2rem",
    letterSpacing: "0.05em",
  },
  leaderboardName: {
    flex: 1,
    color: "var(--text)",
  },
  leaderboardScore: {
    color: "var(--accent)",
    fontFamily: "'Georgia', serif",
    fontWeight: "bold",
    fontSize: "1.4rem",
  },
  footer: {
    display: "flex",
    justifyContent: "center",
    paddingTop: "1rem",
  },
};
