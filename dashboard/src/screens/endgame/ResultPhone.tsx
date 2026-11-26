// Screens 18 and 20. The table puts this on the recap phase only, so a phone
// shows nothing of its result until the engine has moved past the Verdict
// (founder decision on issue #436). Right and wrong come from the player's own
// result route; the words for their answers come from what this seat may
// already see. A value with no such words is left out, never shown raw.

import { useEffect, useMemo, useState } from "react";
import { theoryApi } from "../../api/endgame";
import type { PrivateResult } from "../../api/endgame";
import { createPlayerApi } from "../../api/player";
import { copy } from "../../shell/copy";
import type { SlotProps } from "../../shell/phaseScreens";
import PhoneRoundFrame from "../round/PhoneRoundFrame";

interface Own {
  result: PrivateResult;
  // The label of this player's answer, by slot.
  answers: Record<string, string>;
}

export default function ResultPhone({
  sessionId,
  getToken,
  seat,
  round,
}: SlotProps) {
  const token = useMemo(
    () => async () => {
      if (!getToken) throw new Error("No sign-in");
      return getToken();
    },
    [getToken],
  );
  const [own, setOwn] = useState<Own | null>(null);
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);
  // This player's answer in the slot shown to the room, which has its words.
  const shownFirst = round.closing?.reveal?.players.find(
    (item) => item.participant_id === seat?.participantId,
  )?.answer;

  useEffect(() => {
    let active = true;
    const api = theoryApi(sessionId, token);
    setFailed(false);
    Promise.all([
      api.result(),
      // The words are an extra: the marks show without them.
      api.read().catch(() => null),
      createPlayerApi(sessionId, token)
        .heldLabels()
        .catch(() => new Map<string, string>()),
    ])
      .then(([result, form, labels]) => {
        if (!active) return;
        if (shownFirst?.value) labels.set(shownFirst.value, shownFirst.label);
        const answers: Record<string, string> = {};
        for (const [slot, value] of Object.entries(
          form?.theory.answers ?? {},
        )) {
          const label = labels.get(value);
          if (label) answers[slot] = label;
        }
        setOwn({ result, answers });
      })
      .catch(() => {
        if (active) setFailed(true);
      });
    return () => {
      active = false;
    };
  }, [sessionId, token, attempt, shownFirst?.value]);

  const line = round.closing?.recap?.lines.find(
    (item) => item.participant_id === seat?.participantId,
  );

  return (
    <PhoneRoundFrame
      sessionId={sessionId}
      getToken={getToken}
      seat={seat}
      round={round}
      left={null}
      now={
        <>
          {line && (
            <section className="endgame-line">
              <h2 className="sh-heading">{copy.endgame.postmortem}</h2>
              <p className="sh-title">{line.text}</p>
            </section>
          )}
          {own && (
            <section>
              <h1 className="sh-title">{copy.endgame.yourTheory}</h1>
              {own.result.state === "no_theory" ? (
                <p className="sh-line">{copy.endgame.noTheory}</p>
              ) : (
                <ul className="endgame-slots">
                  {own.result.slots.map((slot) => (
                    <li className="endgame-slot" key={slot.slot_id}>
                      <span>{slot.label}</span>{" "}
                      {own.answers[slot.slot_id] && (
                        <>
                          <strong>{own.answers[slot.slot_id]}</strong>{" "}
                        </>
                      )}
                      <span className="endgame-mark">
                        {slot.right ? copy.endgame.right : copy.endgame.wrong}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          )}
          {failed && (
            <>
              <p className="sh-error" role="alert">
                {copy.round.failed}
              </p>
              <button
                type="button"
                className="sh-button"
                onClick={() => setAttempt((n) => n + 1)}
              >
                {copy.endgame.retry}
              </button>
            </>
          )}
        </>
      }
    />
  );
}
