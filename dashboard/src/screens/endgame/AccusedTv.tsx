import { useEffect, useState } from "react";
import { copy } from "../../shell/copy";
import type { SlotProps } from "../../shell/phaseScreens";
import { TvTitle } from "../round/TvParts";

// Nightcap presentation setting. The seat order never uses correctness.
const HOLD_MS = 2000;

export default function AccusedTv({ round }: SlotProps) {
  const reveal = round.closing?.reveal;
  const rows = round.players.flatMap((player) => {
    const answer = reveal?.players.find(
      (item) => item.participant_id === player.participantId,
    );
    return answer
      ? [
          {
            name: player.name ?? copy.unnamedPlayer,
            answer: answer.answer?.label ?? null,
          },
        ]
      : [];
  });
  const [step, setStep] = useState(0);
  const key = `${round.phaseEntry}:${rows.map((row) => `${row.name}:${row.answer}`).join("|")}`;
  useEffect(() => {
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
      <div className="tv-lines">
        {shown.map((row, index) => (
          <p className="tv-line" key={index}>
            {row.answer ? copy.endgame.accuses(row.name, row.answer) : row.name}
          </p>
        ))}
      </div>
    </div>
  );
}
