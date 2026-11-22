import { useEffect, useMemo, useRef, useState } from "react";
import { theoryApi } from "../../api/endgame";
import type { TheoryForm } from "../../api/endgame";
import { copy } from "../../shell/copy";
import type { SlotProps } from "../../shell/phaseScreens";
import PhoneRoundFrame from "../round/PhoneRoundFrame";

export default function TheoryPhone({
  sessionId,
  getToken,
  seat,
  round,
}: SlotProps) {
  const api = useMemo(
    () =>
      theoryApi(sessionId, async () => {
        if (!getToken) throw new Error("No sign-in");
        return getToken();
      }),
    [sessionId, getToken],
  );
  const [form, setForm] = useState<TheoryForm | null>(null);
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);
  const [confirm, setConfirm] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const requestVersion = useRef(0);
  const seatLocked = Boolean(
    round.players.find((player) => player.participantId === seat?.participantId)
      ?.locked,
  );

  useEffect(() => {
    let active = true;
    const version = ++requestVersion.current;
    api
      .read()
      .then((value) => {
        if (active && requestVersion.current === version) {
          setForm(value);
          setFailed(false);
        }
      })
      .catch(() => {
        if (active && requestVersion.current === version) setFailed(true);
      });
    return () => {
      active = false;
    };
  }, [api, round.phaseEntry, seatLocked, attempt]);

  async function save(answers: Record<string, string>, proof: string | null) {
    setBusy(true);
    setFailed(false);
    setConfirm(false);
    const version = ++requestVersion.current;
    try {
      const theory = await api.save(answers, proof);
      if (requestVersion.current === version)
        setForm((current) => (current ? { ...current, theory } : current));
    } catch {
      if (requestVersion.current === version) setFailed(true);
    } finally {
      setBusy(false);
    }
  }
  async function lock() {
    setBusy(true);
    setFailed(false);
    const version = ++requestVersion.current;
    try {
      const theory = await api.lock();
      if (requestVersion.current === version)
        setForm((current) => (current ? { ...current, theory } : current));
      if (requestVersion.current === version) setConfirm(false);
    } catch {
      if (requestVersion.current === version) setFailed(true);
    } finally {
      setBusy(false);
    }
  }

  const locked =
    seatLocked ||
    form?.theory.state === "locked" ||
    !form?.open ||
    round.status !== "running";
  const complete = Boolean(
    form && form.slots.every((slot) => form.theory.answers[slot.slot_id]),
  );
  const content = form && (
    <section className="endgame-theory">
      <h1 className="sh-title">{copy.endgame.yourTheory}</h1>
      {form.theory.state === "locked" && <p>{copy.endgame.waiting}</p>}
      {form.theory.state === "no_theory" && <p>{copy.endgame.noTheory}</p>}
      <div>
        {(form.account.length
          ? form.account
          : form.slots.map((slot) => ({ text: "", slot_id: slot.slot_id }))
        ).map((part, i) => {
          if (part.slot_id === null) return <span key={i}>{part.text}</span>;
          const slot = form.slots.find((item) => item.slot_id === part.slot_id);
          if (!slot) return null;
          return (
            <label key={i}>
              {slot.label}{" "}
              <select
                aria-label={slot.label}
                value={form.theory.answers[slot.slot_id] ?? ""}
                disabled={locked || busy}
                onChange={(event) =>
                  void save(
                    {
                      ...form.theory.answers,
                      [slot.slot_id]: event.target.value,
                    },
                    form.theory.proof,
                  )
                }
              >
                <option value="">{copy.endgame.choose}</option>
                {slot.options.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          );
        })}
      </div>
      <label>
        {copy.endgame.proof}{" "}
        <select
          aria-label={copy.endgame.proof}
          value={form.theory.proof ?? ""}
          disabled={locked || busy}
          onChange={(event) =>
            void save(form.theory.answers, event.target.value || null)
          }
        >
          <option value="">{copy.endgame.choose}</option>
          {form.proof_options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      {!locked && (
        <>
          <p>{copy.endgame.saved}</p>
          {confirm ? (
            <div role="dialog" aria-label={copy.endgame.confirmLock}>
              <p>{copy.endgame.confirmLock}</p>
              <button
                type="button"
                className="sh-button"
                disabled={busy}
                onClick={() => void lock()}
              >
                {copy.endgame.lock}
              </button>
              <button
                type="button"
                className="sh-button"
                disabled={busy}
                onClick={() => setConfirm(false)}
              >
                {copy.round.notNow}
              </button>
            </div>
          ) : (
            <button
              type="button"
              className="sh-button"
              disabled={!complete || busy}
              onClick={() => setConfirm(true)}
            >
              {copy.endgame.lock}
            </button>
          )}
        </>
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
      now={
        <>
          {content}
          {failed && <p role="alert">{copy.round.failed}</p>}
          {failed && (
            <button
              type="button"
              className="sh-button"
              onClick={() => setAttempt((n) => n + 1)}
            >
              {copy.endgame.retry}
            </button>
          )}
        </>
      }
    />
  );
}
