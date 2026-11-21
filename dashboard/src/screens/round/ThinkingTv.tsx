// Screen 6, the quiet TV in thinking time (D-134): the round title, a large
// clock and who is ready. Nothing else: no scene lines, no menu, no count of
// anyone's investigations, no sound, and nothing moves but the clock. The TV
// reads no route of its own here.

import type { SlotProps } from "../../shell/phaseScreens";
import { copy } from "../../shell/copy";
import { ReadyList, TvClock, TvTitle } from "./TvParts";

export default function ThinkingTv({ round }: SlotProps) {
  return (
    <div className="tv-thinking">
      <TvTitle title={round.beatName} />
      <p className="tv-prompt">{copy.round.investigateOnPhones}</p>
      <TvClock
        seconds={round.secondsLeft}
        running={round.status === "running"}
      />
      <ReadyList players={round.players} />
    </div>
  );
}
