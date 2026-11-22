import { useEffect, useState } from "react";
import { copy } from "../../shell/copy";
import type { SlotProps } from "../../shell/phaseScreens";
import { TvTitle } from "../round/TvParts";
import { prefersReducedMotion } from "../round/staging";

// Nightcap presentation setting. The seat order never uses correctness.
const HOLD_MS = 2000;

export default function AccusedTv({ round }: SlotProps) {
  const reveal = round.closing?.reveal;
  const rows = round.players.flatMap((player) => {
    const answer = reveal?.players.find(
      (item) => item.participant_id === player.participantId,
    );
    return answer?.answer
      ? [
          {
            id: player.participantId,
            name: player.name ?? copy.unnamedPlayer,
            answer: answer.answer.label,
          },
        ]
      : [];
  });
  const [step, setStep] = useState(() =>
    prefersReducedMotion() ? rows.length : 0,
  );
  const key = `${round.phaseEntry}:${rows.map((row) => `${row.name}:${row.answer}`).join("|")}`;
  useEffect(() => {
    if (prefersReducedMotion()) {
      setStep(rows.length);
      return undefined;
    }
    setStep(0);
    const timers = rows.map((_, index) =>
      setTimeout(() => setStep(index + 1), (index + 1) * HOLD_MS),
    );
    return () => timers.forEach(clearTimeout);
  }, [key]);
  const shown = step >= rows.length ? rows : rows.slice(step, step + 1);
  return (
    <div className="tv-thinking">
      <TvTitle title={copy.endgame.accused} />
      <div className="tv-lines" aria-live="polite">
        {shown.map((row) => (
          <p className="tv-line" key={row.id}>
            {copy.endgame.accuses(row.name, row.answer)}
          </p>
        ))}
      </div>
    </div>
  );
}
