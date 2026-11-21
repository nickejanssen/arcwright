// Screen 11: this seat's signed-in package view. If a finding was still open
// when thinking time ended, it gets its one time-up moment before the game.

import { useCallback, useEffect, useState } from "react";

import { copy } from "../../shell/copy";
import type { SlotProps } from "../../shell/phaseScreens";
import RoundMiniGameStage from "./RoundMiniGameStage";
import type { StageServices } from "./RoundMiniGameStage";
import PhoneRoundFrame from "./PhoneRoundFrame";
import {
  FindingView,
  clearHeldFinding,
  peekHeldFinding,
} from "./InvestigatePhone";

export default function MiniGamePhone(
  props: SlotProps & { stageServices?: StageServices },
) {
  const { getToken, round, seat, sessionId } = props;
  const [finding, setFinding] = useState(() => peekHeldFinding(sessionId));
  const [token, setToken] = useState<string | null>(null);
  const [tokenFailed, setTokenFailed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [stageMessage, setStageMessage] = useState<
    "idle" | "unavailable" | "failed" | null
  >(null);
  const stageStateChanged = useCallback((state: string) => {
    setLoading(false);
    setStageMessage(
      state === "idle"
        ? "idle"
        : state === "unavailable"
          ? "unavailable"
          : !state.startsWith("active:")
            ? "failed"
            : null,
    );
  }, []);

  useEffect(() => setLoading(true), [round.phaseEntry]);

  useEffect(() => {
    if (!getToken) {
      setTokenFailed(true);
      setLoading(false);
      return;
    }
    let cancelled = false;
    let retry: ReturnType<typeof setTimeout> | undefined;
    const acquireToken = async () => {
      try {
        const value = await getToken();
        if (!cancelled) setToken(value);
        if (!cancelled) setTokenFailed(false);
      } catch {
        if (!cancelled) {
          setTokenFailed(true);
          setLoading(false);
          retry = setTimeout(() => void acquireToken(), 1000);
        }
      }
    };
    void acquireToken();
    return () => {
      cancelled = true;
      if (retry !== undefined) clearTimeout(retry);
    };
  }, [getToken, sessionId]);

  const now = finding ? (
    <FindingView
      finding={finding}
      closed
      action={{
        label: copy.round.ok,
        onClick: () => {
          clearHeldFinding();
          setFinding(null);
        },
      }}
    />
  ) : (
    <section className="rd-mini-game" aria-busy={loading}>
      {loading && (
        <p className="sh-line" role="status">
          {copy.round.gettingGameReady}
        </p>
      )}
      {tokenFailed && (
        <p className="sh-error" role="alert">
          {copy.round.failed}
        </p>
      )}
      {stageMessage === "idle" && (
        <p className="sh-line" role="status">
          {copy.round.noMiniGameInProgress}
        </p>
      )}
      {stageMessage === "failed" && (
        <p className="sh-error" role="alert">
          {copy.round.miniGameCouldNotShow}
        </p>
      )}
      {stageMessage === "unavailable" && (
        <p className="sh-error" role="alert">
          {copy.round.miniGameUnavailable}
        </p>
      )}
      {token && seat && (
        <RoundMiniGameStage
          key={round.phaseEntry ?? "mini-game"}
          surface="phone"
          sessionId={sessionId}
          participantId={seat.participantId}
          characterId={seat.characterId ?? ""}
          token={token}
          onStageState={stageStateChanged}
          services={props.stageServices}
        />
      )}
    </section>
  );

  return (
    <PhoneRoundFrame
      sessionId={sessionId}
      getToken={getToken}
      seat={seat}
      round={round}
      left={null}
      showClock={false}
      now={now}
    />
  );
}
