// Screen 4, the TV story (scene and bridge): the round title, the written lines
// one at a time, a clock, and who is ready. The lines are written by a person
// and shown as text. The TV holds no sign-in and reads only the room view the
// feed already holds.

import { useMemo } from "react";
import type { SlotProps } from "../../shell/phaseScreens";
import { copy } from "../../shell/copy";
import { readLines, useStagedLines } from "./staging";
import { ReadyList, TvClock, TvTitle } from "./TvParts";

export default function StoryTv({ round }: SlotProps) {
  const lines = useMemo(() => readLines(round.lines), [round.lines]);
  const phaseKey = `${round.phaseEntry ?? "none"}:${lines.map((l) => l.text).join("|")}`;
  const shown = useStagedLines(lines, phaseKey);

  return (
    <div className="tv-story">
      <div className="tv-story-top">
        <TvTitle title={round.beatName} />
        <TvClock
          seconds={round.secondsLeft}
          running={round.status === "running"}
        />
      </div>
      <div className="tv-lines" aria-live="polite">
        {shown.map((line, i) => (
          <p key={`${i}:${line.text}`} className="tv-line">
            {line.speaker && (
              <>
                <span className="tv-speaker">
                  {copy.round.speaker(line.speaker)}
                </span>{" "}
              </>
            )}
            {line.text}
          </p>
        ))}
      </div>
      <ReadyList players={round.players} />
    </div>
  );
}
