// Pieces the TV's round screens share: the round title, the clock and the
// ready list. They show what the room view says and nothing from a menu, a
// notebook or a theory.

import type { RoundPlayer } from "../../api/round";
import { formatClock, useCountdown } from "../../shell/clock";
import { copy } from "../../shell/copy";

export function TvTitle({ title }: { title: string | null }) {
  if (!title) return null;
  return <h1 className="tv-round-title">{title}</h1>;
}

export function TvClock({
  seconds,
  running,
}: {
  seconds: number | null;
  running: boolean;
}) {
  const shown = useCountdown(seconds, running);
  if (shown === null) return null;
  return <p className="tv-clock">{formatClock(shown)}</p>;
}

// Each player is shown by name, a mark and a word, so ready is never told by
// colour alone. The players come in the order the engine gave.
export function ReadyList({ players }: { players: RoundPlayer[] }) {
  if (players.length === 0) return null;
  return (
    <div className="tv-ready">
      <span className="tv-ready-label">{copy.round.ready}</span>{" "}
      <ul className="tv-ready-list">
        {players.map((p) => (
          <li key={p.participantId} className="tv-ready-item">
            <span aria-hidden="true" className="tv-mark">
              {p.ready ? "✓" : "○"}
            </span>{" "}
            <span className="tv-ready-name">
              {p.name ?? copy.unnamedPlayer}
            </span>{" "}
            <span className="tv-ready-word">
              {p.ready ? copy.round.readyWord : copy.round.notReadyWord}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
