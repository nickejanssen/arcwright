// Screen 9, the phone notebook: what this player found, grouped by the subject
// it came from, in the order the engine gave, with the round it was found in.
// It never ranks, labels or judges an item (GDD: the notebook may not rank
// significance). What the player held at the start is its own group.

import { useEffect, useMemo, useState } from "react";
import type { Holding } from "../../api/player";
import { usePlayerApi } from "../../api/usePlayerApi";
import { copy } from "../../shell/copy";

interface Group {
  // The subject's label, or null for "At the start".
  subject: string | null;
  items: Holding[];
}

// Groups appear in the order of their first item in the route's list, and the
// items keep the route's order.
function groupHoldings(held: Holding[]): Group[] {
  const groups: Group[] = [];
  for (const item of held) {
    const group = groups.find((g) => g.subject === item.foundFrom);
    if (group) group.items.push(item);
    else groups.push({ subject: item.foundFrom, items: [item] });
  }
  return groups;
}

interface Props {
  sessionId: string;
  getToken: (() => Promise<string>) | undefined;
}

export default function Notebook({ sessionId, getToken }: Props) {
  const api = usePlayerApi(sessionId, getToken);
  const [held, setHeld] = useState<Holding[] | null>(null);
  const [failed, setFailed] = useState(false);
  const [open, setOpen] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api
      .holdings()
      .then((list) => {
        if (!cancelled) setHeld(list);
      })
      .catch(() => {
        if (!cancelled) setFailed(true);
      });
    return () => {
      cancelled = true;
    };
  }, [api]);

  const groups = useMemo(() => (held ? groupHoldings(held) : []), [held]);
  // "Found" counts what the player looked into; what they held at the start
  // was not found.
  const found = held
    ? held.reduce((n, h) => (h.foundFrom === null ? n : n + 1), 0)
    : 0;

  if (failed) {
    return (
      <p className="sh-error" role="alert">
        {copy.round.failed}
      </p>
    );
  }
  if (held === null) return <p className="sh-line" aria-busy="true" />;

  return (
    <section className="rd-notebook">
      <header className="rd-notebook-head">
        <h2 className="sh-heading">{copy.notebook.title}</h2>{" "}
        {found > 0 && (
          <span className="rd-count">{copy.notebook.found(found)}</span>
        )}
      </header>

      {held.length === 0 && <p className="sh-line">{copy.notebook.empty}</p>}

      {groups.map((group) => (
        <div key={group.subject ?? "start"} className="rd-group">
          <h3 className="rd-subject">
            {group.subject ?? copy.notebook.atTheStart}
          </h3>
          <ul className="rd-notes">
            {group.items.map((item, i) => {
              const key = `${group.subject ?? "start"}:${i}`;
              const isOpen = open === key;
              return (
                <li key={key}>
                  <button
                    type="button"
                    className="rd-note"
                    aria-expanded={isOpen}
                    onClick={() => setOpen(isOpen ? null : key)}
                  >
                    <span className="rd-note-label">{item.label}</span>{" "}
                    {item.roundNumber !== null && (
                      <span className="rd-note-round">
                        {copy.notebook.round(item.roundNumber, item.roundTitle)}
                      </span>
                    )}
                  </button>
                  {isOpen && <p className="rd-note-text">{item.text}</p>}
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </section>
  );
}
