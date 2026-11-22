import { useEffect, useMemo, useState } from "react";
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

  useEffect(() => {
    let active = true;
    api
      .read()
      .then((value) => {
        if (active) setForm(value);
      })
      .catch(() => {
        if (active) setFailed(true);
      });
    return () => {
      active = false;
    };
  }, [api, round.phaseEntry]);

  async function save(answers: Record<string, string>, proof: string | null) {
    setBusy(true);
    setFailed(false);
    try {
      const theory = await api.save(answers, proof);
      setForm((current) => (current ? { ...current, theory } : current));
    } catch {
      setFailed(true);
    } finally {
      setBusy(false);
    }
  }
  async function lock() {
    setBusy(true);
    setFailed(false);
    try {
      const theory = await api.lock();
      setForm((current) => (current ? { ...current, theory } : current));
      setConfirm(false);
    } catch {
      setFailed(true);
    } finally {
      setBusy(false);
    }
  }

  const locked = form?.theory.state === "locked" || !form?.open;
  const complete = Boolean(
    form && form.slots.every((slot) => form.theory.answers[slot.slot_id]),
  );
  const content = form && (
    <section className="endgame-theory">
      <h1 className="sh-title">{copy.endgame.yourTheory}</h1>
      {form.theory.state === "locked" && <p>{copy.endgame.waiting}</p>}
      <div>
        {form.account.map((part, i) => {
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
                className="sh-button"
                disabled={busy}
                onClick={() => void lock()}
              >
                {copy.endgame.lock}
              </button>
              <button
                className="sh-button"
                disabled={busy}
                onClick={() => setConfirm(false)}
              >
                {copy.round.notNow}
              </button>
            </div>
          ) : (
            <button
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
        </>
      }
    />
  );
}
