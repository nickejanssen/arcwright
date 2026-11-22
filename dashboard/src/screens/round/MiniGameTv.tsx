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
  const [idle, setIdle] = useState(false);
  const [unavailable, setUnavailable] = useState(false);
  const [failed, setFailed] = useState(false);
  const stageStateChanged = useCallback((state: string) => {
    setLoading(false);
    setIdle(state === "idle");
    setUnavailable(state === "unavailable");
    setFailed(
      state !== "idle" &&
        state !== "unavailable" &&
        !state.startsWith("active:"),
    );
  }, []);
  useEffect(() => {
    setLoading(true);
    setIdle(false);
    setUnavailable(false);
    setFailed(false);
  }, [props.round.phaseEntry]);

  return (
    <main className="tv-mini-game">
      <TvTitle title={props.round.beatName} />
      {loading && (
        <p className="tv-mini-game-loading" role="status">
          {copy.round.gettingGameReady}
        </p>
      )}
      {idle && (
        <p className="tv-mini-game-idle" role="status">
          {copy.round.noMiniGameInProgress}
        </p>
      )}
      {unavailable && (
        <p className="tv-mini-game-loading" role="alert">
          {copy.round.miniGameUnavailable}
        </p>
      )}
      {failed && (
        <p className="tv-mini-game-loading" role="alert">
          {copy.round.miniGameCouldNotShow}
        </p>
      )}
      <RoundMiniGameStage
        key={props.round.phaseEntry ?? "mini-game"}
        surface="shared_display"
        sessionId={props.sessionId}
        participantId="display"
        characterId=""
        onStageState={stageStateChanged}
        services={props.stageServices}
      />
    </main>
  );
}
