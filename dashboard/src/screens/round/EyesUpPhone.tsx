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

  // The finding and the moment its hold ends are taken once, when this screen
  // opens, so nothing that clears the shared hold afterwards (React StrictMode
  // in the dev server, or an unmount) can lose it. Every render checks the
  // moment again, so the finding goes when its hold is over; a timer renders
  // once more at that moment in case nothing else does.
  const [captured] = useState(() => {
    const finding = peekHeldFinding(sessionId);
    const msLeft = finding ? heldFindingMsLeft(sessionId) : null;
    return finding && msLeft !== null
      ? { finding, endsAt: Date.now() + msLeft }
      : null;
  });
  const pending =
    !dismissed && captured && Date.now() < captured.endsAt
      ? captured.finding
      : null;
  const endsAt = captured?.endsAt ?? null;
  useEffect(() => {
    if (endsAt === null) return;
    const wait = endsAt - Date.now();
    if (wait <= 0) return;
    const timer = setTimeout(() => renderAgain((n) => n + 1), wait + 50);
    return () => clearTimeout(timer);
  }, [endsAt]);

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
