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
  const ready = useCallback(() => setLoading(false), []);

  useEffect(() => setLoading(true), [round.phaseEntry]);

  useEffect(() => {
    if (!getToken) {
      setTokenFailed(true);
      setLoading(false);
      return;
    }
    let cancelled = false;
    void getToken()
      .then((value) => {
        if (!cancelled) setToken(value);
      })
      .catch(() => {
        if (!cancelled) {
          setTokenFailed(true);
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
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
      {token && seat && (
        <RoundMiniGameStage
          key={round.phaseEntry ?? "mini-game"}
          surface="phone"
          sessionId={sessionId}
          participantId={seat.participantId}
          characterId={seat.characterId ?? ""}
          token={token}
          onInitialLoad={ready}
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
