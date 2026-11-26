// Screen 17, the Verdict. Who solved it, who won and which rule decided it are
// all the engine's; this screen only stages them: everyone else one at a time in
// seat order, then the winner last and largest (spec 0095).

import type { ReactNode } from "react";
import type { RoundResult } from "../../api/round";
import { copy } from "../../shell/copy";
import type { SlotProps } from "../../shell/phaseScreens";
import { TvTitle } from "../round/TvParts";
import { useStagedLines } from "../round/staging";

export default function VerdictTv({ round }: SlotProps) {
  const result = round.closing?.result ?? null;
  const steps = result ? stepsOf(result, round.players) : [];
  const shown = useStagedLines(
    steps.map(() => ({ text: "", speaker: null, pauseBeforeMs: 0 })),
    `${round.phaseEntry}:${steps.length}`,
  ).length;
  return (
    <div className="tv-thinking">
      <TvTitle title={copy.endgame.verdict} />
      <div className="tv-verdict" aria-live="polite">
        {steps.slice(0, shown)}
      </div>
    </div>
  );
}

function stepsOf(
  result: RoundResult,
  players: SlotProps["round"]["players"],
): ReactNode[] {
  const seats = players.flatMap((player) => {
    const entry = result.players.find(
      (item) => item.participant_id === player.participantId,
    );
    if (!entry) return [];
    const winner = result.winners.find(
      (item) => item.participant_id === player.participantId,
    );
    return [
      {
        id: player.participantId,
        name: player.name ?? copy.unnamedPlayer,
        solved: entry.solved,
        winner,
      },
    ];
  });
  const others = seats
    .filter((seat) => !seat.winner)
    .map((seat) => (
      <p className="tv-line" key={seat.id}>
        {seat.solved
          ? copy.endgame.solved(seat.name)
          : copy.endgame.notSolved(seat.name)}
      </p>
    ));
  const winners = seats.filter((seat) => seat.winner);
  if (result.winners.length === 0) {
    return [
      ...others,
      <p className="tv-verdict-winner" key="nobody">
        {copy.endgame.nobody}
      </p>,
    ];
  }
  const reason =
    result.decided_by === "shared"
      ? copy.endgame.sharedWin
      : result.decided_by === "mini_game_wins" && winners[0]
        ? copy.endgame.wonMore(winners[0].name)
        : result.decided_by === "mini_game_placings" && winners[0]
          ? copy.endgame.placedHigher(winners[0].name)
          : null;
  // Winners land together, so a shared win never names one of them first.
  return [
    ...others,
    <div className="tv-verdict-winners" key="winners">
      {winners.map((seat) => (
        <div key={seat.id}>
          <p className="tv-verdict-winner">{copy.endgame.solved(seat.name)}</p>
          {seat.winner?.proof && (
            <p className="tv-line">
              {copy.endgame.theirProof(seat.winner.proof.label)}
            </p>
          )}
        </div>
      ))}
      {reason && <p className="tv-line">{reason}</p>}
    </div>,
  ];
}
