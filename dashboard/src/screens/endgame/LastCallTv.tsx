import type { SlotProps } from "../../shell/phaseScreens";
import { copy } from "../../shell/copy";
import { TvClock, TvTitle } from "../round/TvParts";

export default function LastCallTv({ round }: SlotProps) {
  return (
    <div className="tv-thinking">
      <TvTitle title={copy.endgame.lastCall} />
      <TvClock
        seconds={round.secondsLeft}
        running={round.status === "running"}
      />
      <p className="tv-prompt">{copy.endgame.lastCallPrompt}</p>
      <ul className="tv-ready-list">
        {round.players.map((player) => (
          <li key={player.participantId} className="tv-ready-item">
            <span aria-hidden="true">{player.locked ? "✓" : "○"}</span>{" "}
            <span>{player.name ?? copy.unnamedPlayer}</span>{" "}
            <span>
              {player.locked ? copy.endgame.locked : copy.endgame.notLocked}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
