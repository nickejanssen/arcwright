// Screen 21: thanks, and who has answered. The room view says only whether a
// player answered; the TV never has the answers.

import { copy } from "../../shell/copy";
import type { SlotProps } from "../../shell/phaseScreens";

export default function ThanksTv({ round }: SlotProps) {
  return (
    <div className="tv-center">
      <p className="tv-prompt">{copy.survey.thanks}</p>
      <ul className="tv-ready-list">
        {round.players.map((player) => (
          <li key={player.participantId} className="tv-ready-item">
            <span aria-hidden="true" className="tv-mark">
              {player.answeredSurvey ? "✓" : "○"}
            </span>{" "}
            <span>{player.name ?? copy.unnamedPlayer}</span>{" "}
            <span className="tv-ready-word">
              {player.answeredSurvey
                ? copy.survey.answered
                : copy.survey.notYet}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
