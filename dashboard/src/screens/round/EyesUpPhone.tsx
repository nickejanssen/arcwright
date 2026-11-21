// Screen 5, the phone's Eyes up (scene and bridge): a prompt to look at the TV,
// the clock, "I'm ready", and "Who you are" (what this player holds from the
// start), collapsed so a player can read it at their own pace. A finding that
// was on screen when thinking time ended is shown here first, with the time's-up
// words, until the player taps OK.

import { useEffect, useState } from "react";
import type { Holding } from "../../api/player";
import { usePlayerApi } from "../../api/usePlayerApi";
import { copy } from "../../shell/copy";
import type { SlotProps } from "../../shell/phaseScreens";
import {
  FindingView,
  clearHeldFinding,
  heldFindingMsLeft,
  peekHeldFinding,
} from "./InvestigatePhone";
import PhoneRoundFrame, { ReadyControl } from "./PhoneRoundFrame";

// What the player holds from the start, as the engine reports it (it has no
// subject it was found from).
function WhoYouAre(props: {
  sessionId: string;
  getToken: SlotProps["getToken"];
}) {
  const api = usePlayerApi(props.sessionId, props.getToken);
  const [opening, setOpening] = useState<Holding[]>([]);

  useEffect(() => {
    let cancelled = false;
    api
      .holdings()
      .then((list) => {
        if (!cancelled) {
          setOpening(list.filter((h) => h.foundFrom === null));
        }
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [api]);

  if (opening.length === 0) return null;
  return (
    <details className="rd-who">
      <summary className="rd-summary">{copy.round.whoYouAre}</summary>
      {opening.map((h, i) => (
        <div key={i} className="rd-who-item">
          <h3 className="rd-subject">{h.label}</h3>
          <p className="rd-content">{h.text}</p>
        </div>
      ))}
    </details>
  );
}

export default function EyesUpPhone(props: SlotProps) {
  const { sessionId, round, seat, getToken } = props;
  const api = usePlayerApi(sessionId, getToken);
  const [dismissed, setDismissed] = useState(false);
  const [, renderAgain] = useState(0);

  // The held finding is read on every render, so it is gone once its hold is
  // over; a timer renders again at that moment in case nothing else does.
  const pending = dismissed ? null : peekHeldFinding(sessionId);
  const msLeft = pending ? heldFindingMsLeft(sessionId) : null;
  useEffect(() => {
    if (msLeft === null) return;
    const timer = setTimeout(() => renderAgain((n) => n + 1), msLeft + 50);
    return () => clearTimeout(timer);
  }, [msLeft === null]);

  // Whatever happens, a held finding is shown here once.
  useEffect(() => () => clearHeldFinding(), []);

  // Ready is always on screen: a finding beside it never blocks it.
  const now = pending ? (
    <>
      <FindingView
        finding={pending}
        closed
        action={{
          label: copy.round.ok,
          onClick: () => {
            clearHeldFinding();
            setDismissed(true);
          },
        }}
      />
      <ReadyControl api={api} round={round} seat={seat} />
    </>
  ) : (
    <>
      <p className="sh-title">{copy.round.eyesUp}</p>
      <ReadyControl api={api} round={round} seat={seat} />
      <WhoYouAre sessionId={sessionId} getToken={getToken} />
    </>
  );

  return (
    <PhoneRoundFrame
      sessionId={sessionId}
      getToken={getToken}
      seat={seat}
      round={round}
      left={null}
      now={now}
    />
  );
}
