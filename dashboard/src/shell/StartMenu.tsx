import { useState } from "react";
import type { Controls } from "../api/controls";
import { ApiError } from "../api/lobby";
import type { SeatRole } from "../api/seam";
import ConfirmDialog from "./ConfirmDialog";
import { copy } from "./copy";

export interface StartMenuInfo {
  role: SeatRole;
  // The engine's session status ("created", "active", "paused", ...).
  sessionStatus: string;
  // The engine's phase name, or null before there is one.
  phase: string | null;
  playerCount: number;
  minPlayers: number;
  controls: Controls;
  // False until the engine has a hand-over route (AW-331).
  canHandOver: boolean;
  onHandOver?: () => Promise<void>;
}

interface StartMenuProps extends StartMenuInfo {
  onOpenSettings: () => void;
  onClose: () => void;
}

type Confirming = "moveOn" | "end" | null;

// The phase whose move-on locks every saved theory.
const LAST_CALL_PHASE = "commit";
const MINI_GAME_PHASE = "mini_game";

export default function StartMenu(props: StartMenuProps) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [confirming, setConfirming] = useState<Confirming>(null);

  const isHost = props.role === "host";
  const notStarted = props.sessionStatus === "created";
  const paused = props.sessionStatus === "paused";
  const ended =
    props.sessionStatus === "completed" || props.sessionStatus === "abandoned";
  const live = !notStarted && !ended;
  const enoughPlayers = props.playerCount >= props.minPlayers;

  async function run(action: () => Promise<void>) {
    setBusy(true);
    setMessage(null);
    setConfirming(null);
    try {
      await action();
      props.onClose();
    } catch (error) {
      const denied =
        error instanceof ApiError &&
        (error.status === 401 || error.status === 403);
      setMessage(denied ? copy.menu.notAllowed : copy.menu.failed);
      setBusy(false);
    }
  }

  if (confirming === "moveOn") {
    return (
      <ConfirmDialog
        text={copy.confirm.moveOn.text}
        yesLabel={copy.confirm.moveOn.yes}
        noLabel={copy.confirm.moveOn.no}
        onYes={() => void run(props.controls.moveOn)}
        onNo={() => setConfirming(null)}
      />
    );
  }
  if (confirming === "end") {
    return (
      <ConfirmDialog
        text={copy.confirm.endGame.text}
        yesLabel={copy.confirm.endGame.yes}
        noLabel={copy.confirm.endGame.no}
        onYes={() => void run(props.controls.end)}
        onNo={() => setConfirming(null)}
      />
    );
  }

  function item(label: string, onClick: () => void, disabled = false) {
    return (
      <button
        type="button"
        className="sh-button"
        disabled={busy || disabled}
        onClick={onClick}
      >
        {label}
      </button>
    );
  }

  return (
    <div role="dialog" aria-modal="true" aria-label={copy.menu.title}>
      <h2 className="sh-heading">{copy.menu.title}</h2>

      {live &&
        !paused &&
        item(copy.menu.pause, () => void run(props.controls.pause))}
      {live &&
        paused &&
        item(copy.menu.resume, () => void run(props.controls.resume))}

      {isHost && notStarted && (
        <>
          {item(
            copy.menu.startGame,
            () => void run(props.controls.start),
            !enoughPlayers,
          )}
          {!enoughPlayers && (
            <p className="sh-line">
              {copy.menu.needsPlayers(props.minPlayers)}
            </p>
          )}
        </>
      )}
      {isHost &&
        live &&
        item(copy.menu.moveOn, () =>
          props.phase === LAST_CALL_PHASE
            ? setConfirming("moveOn")
            : void run(props.controls.moveOn),
        )}
      {isHost &&
        live &&
        props.phase === MINI_GAME_PHASE &&
        item(
          copy.menu.finishMiniGame,
          () => void run(props.controls.resolveMiniGame),
        )}
      {isHost &&
        live &&
        props.phase === MINI_GAME_PHASE &&
        item(
          copy.menu.cancelMiniGame,
          () => void run(props.controls.cancelMiniGame),
        )}
      {isHost && live && item(copy.menu.endGame, () => setConfirming("end"))}
      {isHost &&
        live &&
        props.canHandOver &&
        props.onHandOver &&
        item(copy.menu.handOver, () => void run(props.onHandOver!))}

      {item(copy.menu.settings, props.onOpenSettings)}
      {message && (
        <p role="alert" className="sh-error">
          {message}
        </p>
      )}
      <button
        type="button"
        className="sh-button sh-button-quiet"
        onClick={props.onClose}
      >
        {copy.menu.close}
      </button>
    </div>
  );
}
