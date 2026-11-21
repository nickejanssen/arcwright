// Screen 10: a public shared view. The package owns its game UI and clock;
// the shell supplies only the round title and loading state.

import { useCallback, useEffect, useState } from "react";

import type { SlotProps } from "../../shell/phaseScreens";
import { copy } from "../../shell/copy";
import { TvTitle } from "./TvParts";
import RoundMiniGameStage from "./RoundMiniGameStage";
import type { StageServices } from "./RoundMiniGameStage";

export default function MiniGameTv(
  props: SlotProps & { stageServices?: StageServices },
) {
  const [loading, setLoading] = useState(true);
  const ready = useCallback(() => setLoading(false), []);
  useEffect(() => setLoading(true), [props.round.phaseEntry]);

  return (
    <main className="tv-mini-game">
      <TvTitle title={props.round.beatName} />
      {loading && (
        <p className="tv-mini-game-loading" role="status">
          {copy.round.gettingGameReady}
        </p>
      )}
      <RoundMiniGameStage
        key={props.round.phaseEntry ?? "mini-game"}
        surface="shared_display"
        sessionId={props.sessionId}
        participantId="display"
        characterId=""
        onInitialLoad={ready}
        services={props.stageServices}
      />
    </main>
  );
}
