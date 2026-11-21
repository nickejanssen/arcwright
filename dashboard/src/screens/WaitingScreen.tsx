// The phone page (spec 0095 screens 3 and 23). It reads the seat this phone
// holds, follows the engine through the feed, and draws the screen the phase
// table names inside the frame with the Menu button. It carries no ID in its
// address.

import { useCallback, useEffect, useMemo, useState } from "react";
import { getValidPlayerToken } from "../api/auth";
import { createControls } from "../api/controls";
import type { Controls } from "../api/controls";
import { fetchMyRole, handOverAvailable } from "../api/seam";
import type { SeatRole } from "../api/seam";
import { seatStore } from "../api/seatStore";
import type { StoredSeat } from "../api/seatStore";
import type { FeedState } from "../shell/feed";
import { copy } from "../shell/copy";
import PhoneFrame from "../shell/PhoneFrame";
import { resolveScreen } from "../shell/phaseScreens";
import type { SlotTable } from "../shell/phaseScreens";
import RewardCard from "./round/RewardCard";
import { applySettings, loadSettings, saveSettings } from "../shell/settings";
import type { Settings } from "../shell/settings";
import { useFeed } from "../shell/useFeed";

export default function WaitingScreen() {
  const [seat] = useState<StoredSeat | null>(() => seatStore.mostRecent());

  useEffect(() => {
    if (seat) seatStore.touch(seat.gameId);
    else window.location.replace("/join");
  }, [seat]);

  if (!seat) return null;
  return <Seated seat={seat} />;
}

function Seated({ seat }: { seat: StoredSeat }) {
  const feed = useFeed(seat.gameId);
  const [role, setRole] = useState<SeatRole>("player");
  const [settings, setSettings] = useState<Settings>(() => loadSettings());

  useEffect(() => {
    let cancelled = false;
    fetchMyRole(seat.gameId, () => getValidPlayerToken(seat.gameId))
      .then((value) => {
        if (!cancelled) setRole(value);
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [seat.gameId]);

  useEffect(() => {
    applySettings(document.documentElement, settings);
  }, [settings]);

  // The game is gone, so the seat is of no use.
  useEffect(() => {
    if (feed.gone) seatStore.clear(seat.gameId);
  }, [feed.gone, seat.gameId]);

  const getToken = useCallback(
    () => getValidPlayerToken(seat.gameId),
    [seat.gameId],
  );

  const controls = useMemo(
    () => createControls(seat.gameId, () => getValidPlayerToken(seat.gameId)),
    [seat.gameId],
  );

  function changeSettings(next: Settings) {
    setSettings(next);
    saveSettings(next);
  }

  const joinUrl = `${window.location.origin}/join?code=${encodeURIComponent(seat.joinCode)}`;

  return (
    <PhoneView
      sessionId={seat.gameId}
      displayName={seat.displayName}
      participantId={seat.participantId}
      characterId={seat.characterId}
      getToken={getToken}
      joinCode={seat.joinCode}
      joinUrl={joinUrl}
      feed={feed}
      role={role}
      controls={controls}
      settings={settings}
      onSettingsChange={changeSettings}
    />
  );
}

interface PhoneViewProps {
  sessionId: string;
  displayName: string;
  // This seat's own row in the room view, and its sign-in, for the screens
  // that read or send for this player.
  participantId?: string;
  characterId?: string;
  getToken?: () => Promise<string>;
  joinCode: string;
  joinUrl: string;
  feed: FeedState;
  role: SeatRole;
  controls: Controls;
  settings: Settings;
  onSettingsChange: (next: Settings) => void;
  slots?: SlotTable;
}

export function PhoneView(props: PhoneViewProps) {
  const { feed } = props;
  const { lobby, round } = feed;

  if (feed.gone) {
    return (
      <PhoneFrame
        menu={null}
        settings={props.settings}
        onSettingsChange={props.onSettingsChange}
        roomCode={null}
        joinUrl={null}
      >
        <p className="sh-line">{copy.seated.gameGone}</p>
        <a className="sh-button" href="/join">
          {copy.seated.joinAgain}
        </a>
      </PhoneFrame>
    );
  }

  let body;
  if (!lobby) {
    body = <p className="sh-line">{copy.tv.connecting}</p>;
  } else {
    const resolved = resolveScreen("phone", lobby, round, props.slots);
    if (resolved.kind === "room") {
      const names = lobby.players
        .map((p) => p.display_name ?? copy.unnamedPlayer)
        .join(", ");
      body = (
        <>
          <p className="sh-title">{copy.seated.youAreIn(props.displayName)}</p>
          <p className="sh-line">{copy.seated.waitingForHost}</p>
          {names && <p className="sh-line">{copy.seated.atTheTable(names)}</p>}
        </>
      );
    } else if (resolved.kind === "paused") {
      body = <p className="sh-title">{copy.paused.phone}</p>;
    } else if (resolved.kind === "ended") {
      body = <p className="sh-title">{copy.seated.gameOver}</p>;
    } else if (resolved.kind === "phase" && round) {
      const Slot = resolved.Slot;
      body = (
        <Slot
          sessionId={props.sessionId}
          lobby={lobby}
          round={round}
          seat={{
            participantId: props.participantId ?? "",
            characterId: props.characterId,
            displayName: props.displayName,
          }}
          getToken={props.getToken}
        />
      );
    } else {
      body = <p className="sh-title">{copy.seated.eyesOnTv}</p>;
    }
  }

  const activeBody =
    round?.status === "running" && round.phaseEntry !== null ? (
      <RewardCard
        sessionId={props.sessionId}
        getToken={props.getToken}
        round={round}
      >
        {body}
      </RewardCard>
    ) : (
      body
    );

  return (
    <PhoneFrame
      menu={
        lobby
          ? {
              role: props.role,
              sessionStatus: lobby.status,
              phase: round?.phase ?? null,
              playerCount: lobby.player_count,
              minPlayers: lobby.min_players,
              controls: props.controls,
              canHandOver: handOverAvailable(),
            }
          : null
      }
      settings={props.settings}
      onSettingsChange={props.onSettingsChange}
      roomCode={props.joinCode}
      joinUrl={props.joinUrl}
    >
      {activeBody}
    </PhoneFrame>
  );
}
