// The frame every in-game phone screen of a round sits in (spec 0095, the
// phone sketches): a header with the player's name, the round, the clock and,
// on the investigate screen only, the investigations left; the screen for this
// phase ("Now"); and the "Notebook" tab. The number left is the route's number,
// handed in by the screen; the frame never works it out.

import { useState } from "react";
import type { ReactNode } from "react";
import type { PlayerApi } from "../../api/player";
import type { RoundState } from "../../api/round";
import { formatClock, useCountdown } from "../../shell/clock";
import { copy } from "../../shell/copy";
import type { SlotSeat } from "../../shell/phaseScreens";
import Notebook from "../notebook/Notebook";

interface FrameProps {
  sessionId: string;
  getToken: (() => Promise<string>) | undefined;
  seat: SlotSeat | undefined;
  round: RoundState;
  // The route's investigations-left number; null where it does not matter.
  left: number | null;
  showClock?: boolean;
  now: ReactNode;
}

type Tab = "now" | "notebook";

export default function PhoneRoundFrame(props: FrameProps) {
  const { round } = props;
  const [tab, setTab] = useState<Tab>("now");
  const clock = useCountdown(round.secondsLeft, round.status === "running");

  return (
    <div className="rd-frame">
      <header className="rd-header">
        {props.seat?.displayName && (
          <span className="rd-name">{props.seat.displayName}</span>
        )}{" "}
        {round.beatName && <span className="rd-title">{round.beatName}</span>}{" "}
        {props.showClock !== false && clock !== null && (
          <span className="rd-clock">{formatClock(clock)}</span>
        )}{" "}
        {props.left !== null && (
          <span className="rd-left">{copy.round.left(props.left)}</span>
        )}
      </header>

      <div className="rd-body">
        {tab === "now" ? (
          props.now
        ) : (
          <Notebook sessionId={props.sessionId} getToken={props.getToken} />
        )}
      </div>

      <nav className="rd-tabs" role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={tab === "now"}
          className={`sh-button rd-tab${tab === "now" ? " rd-tab-on" : ""}`}
          onClick={() => setTab("now")}
        >
          {copy.round.tabNow}
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "notebook"}
          className={`sh-button rd-tab${tab === "notebook" ? " rd-tab-on" : ""}`}
          onClick={() => setTab("notebook")}
        >
          {copy.round.tabNotebook}
        </button>
      </nav>
    </div>
  );
}

// Marks this player ready for the phase they saw. The room view says who is
// ready, so a reload keeps it; the phone also remembers a send the engine
// accepted, so the button is replaced at once. If the round has moved on, the
// engine saves nothing and says which entry it is on; the phone then claims
// nothing.
export function ReadyControl(props: {
  api: PlayerApi;
  round: RoundState;
  seat: SlotSeat | undefined;
}) {
  const { api, round, seat } = props;
  const [sentFor, setSentFor] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);

  const mine = round.players.find(
    (p) => p.participantId === seat?.participantId,
  );
  const entry = round.phaseEntry;
  const isReady = Boolean(mine?.ready) || (entry !== null && sentFor === entry);

  if (isReady) {
    return (
      <p className="sh-line rd-ready" role="status">
        {copy.round.readyWaiting}
      </p>
    );
  }
  if (entry === null) return null;

  async function mark(phaseEntry: number) {
    setBusy(true);
    setFailed(false);
    try {
      const state = await api.ready(phaseEntry);
      if (state.phaseEntry === phaseEntry) setSentFor(phaseEntry);
    } catch {
      setFailed(true);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <button
        type="button"
        className="sh-button"
        disabled={busy}
        onClick={() => void mark(entry)}
      >
        {copy.round.imReady}
      </button>
      {failed && (
        <p className="sh-error" role="alert">
          {copy.round.failed}
        </p>
      )}
    </>
  );
}
