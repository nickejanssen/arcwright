// Screen 19, the Postmortem: the engine's public recap lines, one at a time, in
// the order it gave, each held for its written pause (never less than the
// story's floor).

import { useEffect, useRef } from "react";
import { copy } from "../../shell/copy";
import type { SlotProps } from "../../shell/phaseScreens";
import { TvTitle } from "../round/TvParts";
import { readLines, useStagedLines } from "../round/staging";

export default function PostmortemTv({ round }: SlotProps) {
  const lines = readLines(
    (round.closing?.recap?.lines ?? []).map((line) => {
      const player = round.players.find(
        (item) => item.participantId === line.participant_id,
      );
      return {
        text: line.text,
        speaker: player?.name ?? copy.unnamedPlayer,
        hints: line.hints,
      };
    }),
  );
  const shown = useStagedLines(
    lines,
    `${round.phaseEntry}:${lines.map((line) => line.text).join("|")}`,
  );
  const box = useRef<HTMLDivElement>(null);
  useEffect(() => {
    box.current?.lastElementChild?.scrollIntoView?.({ block: "nearest" });
  }, [shown.length]);
  return (
    <div className="tv-thinking">
      <TvTitle title={copy.endgame.postmortem} />
      <div className="tv-lines" aria-live="polite" ref={box}>
        {shown.map((line, i) => (
          <p className="tv-line" key={`${i}:${line.text}`}>
            <span className="tv-speaker">
              {copy.round.speaker(line.speaker ?? copy.unnamedPlayer)}
            </span>{" "}
            {line.text}
          </p>
        ))}
      </div>
    </div>
  );
}
