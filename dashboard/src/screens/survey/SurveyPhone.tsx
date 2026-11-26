// Screen 22, the survey: three taps and an optional comment, private to this
// seat. A saved copy is restored; sending again replaces it.

import { useEffect, useMemo, useRef, useState } from "react";
import { surveyApi } from "../../api/survey";
import type { SurveyAnswers } from "../../api/survey";
import { copy } from "../../shell/copy";
import type { SlotProps } from "../../shell/phaseScreens";

// The engine's limit on a comment.
const COMMENT_LIMIT = 1000;
const SCALE = [1, 2, 3, 4, 5].map((n) => ({ value: n, label: String(n) }));

const QUESTIONS = [
  { key: "fun", label: copy.survey.fun, options: SCALE },
  { key: "detective", label: copy.survey.detective, options: SCALE },
  {
    key: "play_again",
    label: copy.survey.again,
    options: [
      { value: "yes", label: copy.survey.yes },
      { value: "maybe", label: copy.survey.maybe },
      { value: "no", label: copy.survey.no },
    ],
  },
];

export default function SurveyPhone({ sessionId, getToken }: SlotProps) {
  const api = useMemo(
    () =>
      surveyApi(sessionId, async () => {
        if (!getToken) throw new Error("No sign-in");
        return getToken();
      }),
    [sessionId, getToken],
  );
  const [answers, setAnswers] = useState<SurveyAnswers>({});
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [failed, setFailed] = useState<"read" | "send" | null>(null);
  const [attempt, setAttempt] = useState(0);
  // Set once the player touches the form, so a slow read never undoes it.
  const touched = useRef(false);

  useEffect(() => {
    let active = true;
    api
      .read()
      .then((saved) => {
        if (!active) return;
        setFailed(null);
        if (!saved.answered || touched.current) return;
        setAnswers(saved.answers);
        setComment(saved.comment ?? "");
        setSent(true);
      })
      .catch(() => {
        if (active) setFailed("read");
      });
    return () => {
      active = false;
    };
  }, [api, attempt]);

  function change() {
    touched.current = true;
    setSent(false);
  }

  async function send() {
    touched.current = true;
    setBusy(true);
    setFailed(null);
    try {
      await api.save(answers, comment.trim() ? comment : null);
      setSent(true);
    } catch {
      setFailed("send");
    } finally {
      setBusy(false);
    }
  }

  const complete = QUESTIONS.every(
    (question) => answers[question.key] !== undefined,
  );

  return (
    <section className="survey">
      {QUESTIONS.map((question) => (
        <fieldset className="survey-question" key={question.key}>
          <legend>{question.label}</legend>
          <div className="survey-options">
            {question.options.map((option) => {
              const on = answers[question.key] === option.value;
              return (
                <button
                  type="button"
                  key={option.label}
                  className={`sh-button rd-tab${on ? " rd-tab-on" : ""}`}
                  aria-pressed={on}
                  disabled={busy}
                  onClick={() => {
                    change();
                    setAnswers((now) => ({
                      ...now,
                      [question.key]: option.value,
                    }));
                  }}
                >
                  {option.label}
                </button>
              );
            })}
          </div>
        </fieldset>
      ))}
      <label className="sh-label" htmlFor="survey-comment">
        {copy.survey.comment}
      </label>
      <textarea
        id="survey-comment"
        className="sh-input"
        rows={3}
        maxLength={COMMENT_LIMIT}
        value={comment}
        disabled={busy}
        onChange={(event) => {
          change();
          setComment(event.currentTarget.value);
        }}
      />
      <button
        type="button"
        className="sh-button"
        disabled={!complete || busy}
        onClick={() => void send()}
      >
        {copy.survey.send}
      </button>
      {sent && <p role="status">{copy.survey.sent}</p>}
      {failed && (
        <p className="sh-error" role="alert">
          {copy.round.failed}
        </p>
      )}
      {failed === "read" && (
        <button
          type="button"
          className="sh-button"
          onClick={() => setAttempt((n) => n + 1)}
        >
          {copy.endgame.retry}
        </button>
      )}
    </section>
  );
}
