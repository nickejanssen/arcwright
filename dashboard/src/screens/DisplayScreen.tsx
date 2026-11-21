// The shared TV page. It holds no sign-in (spec 0095 decision 6): it reads only
// public routes and shows what the engine says. It has no controls; the host
// acts from a phone.

import { useEffect } from "react";
import type { FeedState } from "../shell/feed";
import { formatClock } from "../shell/clock";
import { copy } from "../shell/copy";
import { resolveScreen } from "../shell/phaseScreens";
import type { SlotTable } from "../shell/phaseScreens";
import { useFeed } from "../shell/useFeed";

export { formatClock };

interface Props {
  sessionId: string;
}

function publicJoinBaseUrl(): string {
  const configured = new URLSearchParams(window.location.search).get(
    "join_base_url",
  );
  if (!configured) return window.location.origin;

  try {
    const parsed = new URL(configured);
    if (parsed.protocol === "http:" || parsed.protocol === "https:") {
      return parsed.origin;
    }
  } catch {
    // Fall back to the display origin if the rehearsal URL is malformed.
  }
  return window.location.origin;
}

export default function DisplayScreen({ sessionId }: Props) {
  // An old rehearsal link may still carry a host sign-in. The TV never holds
  // one, so it is removed from the address bar and ignored.
  useEffect(() => {
    if (window.location.hash.includes("host_token")) {
      window.history.replaceState(
        null,
        "",
        `${window.location.pathname}${window.location.search}`,
      );
    }
  }, []);

  const feed = useFeed(sessionId);
  return (
    <TvView
      sessionId={sessionId}
      feed={feed}
      joinBaseUrl={publicJoinBaseUrl()}
    />
  );
}

interface TvViewProps {
  sessionId: string;
  feed: FeedState;
  joinBaseUrl: string;
  slots?: SlotTable;
}

export function TvView({ sessionId, feed, joinBaseUrl, slots }: TvViewProps) {
  const { lobby, round } = feed;

  if (feed.gone) {
    return <TvMessage text={copy.tv.gameGone} />;
  }
  if (!lobby) {
    return (
      <TvMessage
        text={feed.unreachable ? copy.tv.cannotReach : copy.tv.connecting}
      />
    );
  }

  const resolved = resolveScreen("tv", lobby, round, slots);
  let body;
  if (resolved.kind === "room") {
    const joinUrl = lobby.join_code
      ? `${joinBaseUrl}/join?code=${encodeURIComponent(lobby.join_code)}`
      : null;
    const names = lobby.players.map(
      (p) => p.display_name ?? copy.unnamedPlayer,
    );
    body = (
      <div className="tv-room">
        <p className="tv-label">{copy.tv.joinOnPhone}</p>
        {joinUrl && (
          <img
            className="tv-qr"
            src={`https://api.qrserver.com/v1/create-qr-code/?size=300x300&bgcolor=0a0a0f&color=c8a96e&data=${encodeURIComponent(joinUrl)}`}
            alt={copy.tv.qrAlt}
          />
        )}
        {lobby.join_code && (
          <>
            <p className="tv-label">{copy.tv.roomCode}</p>
            <p className="tv-code">{lobby.join_code}</p>
          </>
        )}
        <p className="tv-text">
          {lobby.player_count >= lobby.min_players
            ? copy.tv.readyToStart(lobby.player_count)
            : copy.tv.needsPlayers(lobby.min_players)}
        </p>
        {names.length > 0 && (
          <>
            <p className="tv-label">{copy.tv.atTheTable}</p>
            <ul className="tv-names">
              {lobby.players.map((p, i) => (
                <li key={p.participant_id}>{names[i]}</li>
              ))}
            </ul>
          </>
        )}
      </div>
    );
  } else if (resolved.kind === "paused") {
    body = (
      <div className="tv-center">
        <p className="tv-title">{copy.tv.paused}</p>
        {round?.secondsLeft != null && (
          <p className="tv-text">
            {copy.tv.timeLeft(formatClock(round.secondsLeft))}
          </p>
        )}
      </div>
    );
  } else if (resolved.kind === "ended") {
    body = <TvMessage text={copy.tv.gameOver} />;
  } else if (resolved.kind === "phase" && round) {
    const Slot = resolved.Slot;
    body = <Slot sessionId={sessionId} lobby={lobby} round={round} />;
  } else {
    body = <TvMessage text={copy.tv.playContinues} />;
  }

  return (
    <div className="tv-root">
      <header className="tv-header">
        <span className="tv-brand">{copy.brand}</span>
      </header>
      <main className="tv-main">{body}</main>
      {feed.unreachable && (
        <p role="status" className="tv-notice">
          {copy.tv.cannotReach}
        </p>
      )}
    </div>
  );
}

function TvMessage({ text }: { text: string }) {
  return (
    <div className="tv-center">
      <p className="tv-text">{text}</p>
    </div>
  );
}
