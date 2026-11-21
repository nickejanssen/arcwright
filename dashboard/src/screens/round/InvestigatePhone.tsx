// Screens 7 and 8, the phone's investigate menu and a finding. The engine
// decides what is on the menu, what a choice costs and how many investigations
// are left; this screen prints the menu in the order the route gave, sends the
// choice the player taps, and shows the written content that comes back. The
// number left is always the route's number: it is read with the menu, replaced
// by the one in each choose reply, and read again after every change. The only
// comparison made on it is "is it 0", to choose between two sentences.

import { useEffect, useRef, useState } from "react";
import { createChoiceTracker } from "../../api/player";
import type { Menu, MenuItem } from "../../api/player";
import { ApiError } from "../../api/lobby";
import { usePlayerApi } from "../../api/usePlayerApi";
import { copy } from "../../shell/copy";
import type { SlotProps } from "../../shell/phaseScreens";
import PhoneRoundFrame, { ReadyControl } from "./PhoneRoundFrame";

interface Finding {
  subjectLabel: string;
  content: string;
}

type View =
  | { kind: "list" }
  | { kind: "confirm"; item: MenuItem }
  | { kind: "finding"; finding: Finding };

// A finding on screen when the phase ends stays on screen: the phone finishes
// its moment (spec 0095, "How the feelings answer shapes the layout"). The next
// screen of this phone picks it up and shows it with the time's-up words.
// The finding is marked as held the moment it is shown (at is null), because
// the next screen is built before this one's cleanup runs. The clock starts
// when this screen goes away.
const HOLD_MS = 30_000;
export const MENU_RETRY_MS = 2000;
let held: (Finding & { at: number | null }) | null = null;

export function peekHeldFinding(now: number = Date.now()): Finding | null {
  return held && (held.at === null || now - held.at <= HOLD_MS)
    ? { subjectLabel: held.subjectLabel, content: held.content }
    : null;
}

export function clearHeldFinding(): void {
  held = null;
}

export function FindingView(props: {
  finding: Finding;
  // True when the time is up: the closing words replace "Saved to your notebook."
  closed: boolean;
  action: { label: string; onClick: () => void } | null;
}) {
  return (
    <section className="rd-finding">
      <h2 className="sh-heading">{props.finding.subjectLabel}</h2>
      <p className="rd-content">{props.finding.content}</p>
      <p className="sh-line" role="status">
        {props.closed ? copy.round.timesUp : copy.round.saved}
      </p>
      {props.action && (
        <button
          type="button"
          className="sh-button"
          onClick={props.action.onClick}
        >
          {props.action.label}
        </button>
      )}
    </section>
  );
}

// The menu's items grouped under the subject each is about. Subjects appear in
// the order of their first item and items keep the route's order.
function groupBySubject(items: MenuItem[]): Array<{
  subjectId: string;
  label: string;
  kind: string;
  items: MenuItem[];
}> {
  const groups: Array<{
    subjectId: string;
    label: string;
    kind: string;
    items: MenuItem[];
  }> = [];
  for (const item of items) {
    const group = groups.find((g) => g.subjectId === item.subjectId);
    if (group) group.items.push(item);
    else {
      groups.push({
        subjectId: item.subjectId,
        label: item.subjectLabel,
        kind: item.subjectKind,
        items: [item],
      });
    }
  }
  return groups;
}

export default function InvestigatePhone(props: SlotProps) {
  const { sessionId, round, seat, getToken } = props;
  const api = usePlayerApi(sessionId, getToken);
  const tracker = useRef(createChoiceTracker()).current;

  const [menu, setMenu] = useState<Menu | null>(null);
  const [view, setView] = useState<View>({ kind: "list" });
  const [failed, setFailed] = useState(false);
  const [busy, setBusy] = useState(false);

  async function reread(clearFailure = false): Promise<void> {
    try {
      setMenu(await api.menu());
      if (clearFailure) setFailed(false);
    } catch {
      setFailed(true);
    }
  }

  // Read the menu when the screen opens and whenever the phase is entered again.
  useEffect(() => {
    void reread();
  }, [round.phaseEntry, api]);

  // If the first menu read fails, try again until it loads, so a short
  // disconnect does not leave the phone stuck in this phase.
  useEffect(() => {
    if (menu !== null || !failed) return;
    const timer = setTimeout(() => void reread(true), MENU_RETRY_MS);
    return () => clearTimeout(timer);
  }, [menu, failed]);

  // A finding still on screen when this screen goes away is held for the next:
  // it is marked held when shown, and its clock starts here.
  useEffect(
    () => () => {
      if (held && held.at === null) held = { ...held, at: Date.now() };
    },
    [],
  );

  async function send(item: MenuItem): Promise<void> {
    const attempt = tracker.attempt(item.opportunityId);
    setBusy(true);
    setFailed(false);
    try {
      const reply = await api.choose(attempt.choiceId, attempt.opportunityId);
      tracker.answered();
      setMenu((m) =>
        m ? { ...m, remainingBudget: reply.remainingBudget } : m,
      );
      const finding = {
        subjectLabel: item.subjectLabel,
        content: reply.content,
      };
      held = { ...finding, at: null };
      setView({ kind: "finding", finding });
      void reread();
    } catch (error) {
      if (error instanceof ApiError && error.status < 500) {
        // The engine answered and said no: that choice is over. (A 5xx from a
        // proxy may not have reached the engine, so it is retried with the
        // same ID, like a dropped send.) Read the menu again so the list shows
        // what the engine now says.
        tracker.answered();
        setView({ kind: "list" });
        void reread();
      }
      // Otherwise the send may not have arrived: the same choice stays ready to
      // be sent again with the same ID.
      setFailed(true);
    } finally {
      setBusy(false);
    }
  }

  function tap(item: MenuItem): void {
    setFailed(false);
    if (item.taken) void send(item);
    else setView({ kind: "confirm", item });
  }

  function backToList(): void {
    clearHeldFinding();
    setFailed(false);
    setView({ kind: "list" });
    void reread();
  }

  const closed = menu !== null && !menu.open;
  let now;
  if (menu === null) {
    now = failed ? (
      <p className="sh-error" role="alert">
        {copy.round.failed}
      </p>
    ) : null;
  } else if (view.kind === "finding") {
    now = (
      <FindingView
        finding={view.finding}
        closed={closed}
        action={
          closed ? null : { label: copy.round.backToList, onClick: backToList }
        }
      />
    );
  } else if (closed) {
    now = <p className="sh-title">{copy.round.timesUp}</p>;
  } else if (view.kind === "confirm") {
    now = (
      <section className="rd-confirm">
        <h2 className="sh-heading">{view.item.subjectLabel}</h2>
        <p className="rd-content">{view.item.label}</p>
        <p className="sh-confirm-text">
          {copy.round.spend(view.item.cost, menu.remainingBudget)}
        </p>
        <button
          type="button"
          className="sh-button"
          disabled={busy}
          onClick={() => void send(view.item)}
        >
          {copy.round.spendIt}
        </button>
        <button
          type="button"
          className="sh-button sh-button-quiet"
          disabled={busy}
          onClick={() => {
            setFailed(false);
            setView({ kind: "list" });
          }}
        >
          {copy.round.notNow}
        </button>
        {failed && (
          <p className="sh-error" role="alert">
            {copy.round.failed}
          </p>
        )}
      </section>
    );
  } else {
    now = (
      <>
        <p className="sh-line">{copy.round.lookInto}</p>
        {menu.remainingBudget === 0 && (
          <p className="sh-line">{copy.round.noneLeft}</p>
        )}
        {groupBySubject(menu.items).map((group) => (
          <div key={group.subjectId} className="rd-group">
            <h3 className="rd-subject">
              {copy.round.kinds[group.kind] && (
                <>
                  <span className="rd-kind">
                    {copy.round.kinds[group.kind]}
                  </span>{" "}
                </>
              )}
              <span>{group.label}</span>
            </h3>
            <ul className="rd-items">
              {group.items.map((item) => (
                <li key={item.opportunityId}>
                  <button
                    type="button"
                    className="rd-item"
                    disabled={busy}
                    onClick={() => tap(item)}
                  >
                    <span className="rd-item-label">{item.label}</span>{" "}
                    <span className="rd-item-meta">
                      <span className="rd-item-state">
                        {item.taken ? copy.round.isSeen : copy.round.isNew}
                      </span>
                      {!item.taken && (
                        <>
                          {" "}
                          <span className="rd-item-cost">{item.cost}</span>
                        </>
                      )}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
        {failed && (
          <p className="sh-error" role="alert">
            {copy.round.failed}
          </p>
        )}
        <ReadyControl api={api} round={round} seat={seat} />
      </>
    );
  }

  return (
    <PhoneRoundFrame
      sessionId={sessionId}
      getToken={getToken}
      seat={seat}
      round={round}
      left={menu ? menu.remainingBudget : null}
      now={now}
    />
  );
}
