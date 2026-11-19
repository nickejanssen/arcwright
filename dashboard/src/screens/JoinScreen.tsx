// The join page (spec 0095 screen 2). Opening a join link first looks for a
// seat this phone already holds, so a closed tab or a second tap on the link
// never makes a second player.

import type { FormEvent } from "react";
import { useEffect, useRef, useState } from "react";
import { exchangePlayerToken } from "../api/auth";
import type { FirebaseAuthSession } from "../api/auth";
import { ApiError, JoinError, fetchLobbyState, joinLobby } from "../api/lobby";
import type { LobbyJoinResult, LobbyState } from "../api/lobby";
import { seatStore } from "../api/seatStore";
import type { SeatStore, StoredSeat } from "../api/seatStore";
import { copy } from "../shell/copy";

export interface JoinDeps {
  store: SeatStore;
  fetchLobby: (sessionId: string) => Promise<LobbyState>;
  join: (name: string, code: string) => Promise<LobbyJoinResult>;
  exchange: (customToken: string) => Promise<FirebaseAuthSession>;
  navigate: (path: string) => void;
}

const DEFAULT_DEPS: JoinDeps = {
  store: seatStore,
  fetchLobby: (id) => fetchLobbyState(id),
  join: (name, code) => joinLobby(name, code),
  exchange: exchangePlayerToken,
  navigate: (path) => window.location.replace(path),
};

interface Props {
  code?: string;
  deps?: Partial<JoinDeps>;
}

function isFinished(status: string): boolean {
  return status === "completed" || status === "abandoned";
}

function failureText(error: unknown): string {
  if (error instanceof JoinError) {
    if (error.failure === "bad_code") return copy.join.errors.badCode;
    if (error.failure === "started") return copy.join.errors.started;
  }
  return copy.join.errors.failed;
}

export default function JoinScreen({ code: codeFromLink = "", deps }: Props) {
  const d: JoinDeps = { ...DEFAULT_DEPS, ...deps };
  const [name, setName] = useState("");
  const [code, setCode] = useState(codeFromLink.toUpperCase());
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  // A seat the engine already made but this browser would not keep. Trying
  // again saves this one; it never joins a second time.
  const unsavedSeat = useRef<Omit<StoredSeat, "savedAt"> | null>(null);
  // True while a stored seat is being checked, so the form does not flash.
  const [resuming, setResuming] = useState(
    () =>
      (codeFromLink
        ? d.store.findByCode(codeFromLink)
        : d.store.mostRecent()) !== null,
  );

  useEffect(() => {
    const seat = codeFromLink
      ? d.store.findByCode(codeFromLink)
      : d.store.mostRecent();
    if (!seat) return;
    let cancelled = false;
    d.fetchLobby(seat.gameId)
      .then((lobby) => {
        if (cancelled) return;
        if (isFinished(lobby.status)) {
          d.store.clear(seat.gameId);
          setResuming(false);
          return;
        }
        d.store.touch(seat.gameId);
        d.navigate("/play");
      })
      .catch((e) => {
        if (cancelled) return;
        if (e instanceof ApiError && e.status === 404) {
          // The game is gone, so the seat is of no use.
          d.store.clear(seat.gameId);
          setResuming(false);
          return;
        }
        // The engine could not be reached; the phone page keeps trying.
        d.store.touch(seat.gameId);
        d.navigate("/play");
      });
    return () => {
      cancelled = true;
    };
    // The deps object is rebuilt on every render; the link's code is what
    // decides which seat to look for.
  }, [codeFromLink]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) {
      setError(copy.join.errors.noName);
      return;
    }
    if (!code.trim()) {
      setError(copy.join.errors.noCode);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      if (!unsavedSeat.current) {
        const result = await d.join(name.trim(), code.trim());
        const auth = await d.exchange(result.player_token);
        unsavedSeat.current = {
          gameId: result.session_id,
          joinCode: code.trim().toUpperCase(),
          participantId: result.participant_id,
          characterId: result.character_id,
          displayName: result.display_name,
          auth,
        };
      }
      if (!d.store.save(unsavedSeat.current)) {
        // Going on would bounce this phone back here with no seat.
        setError(copy.join.errors.cannotSave);
        setLoading(false);
        return;
      }
      unsavedSeat.current = null;
      d.navigate("/play");
    } catch (e) {
      setError(failureText(e));
      setLoading(false);
    }
  }

  if (resuming) {
    return (
      <div className="sh-phone">
        <main className="sh-phone-body">
          <p className="sh-line">{copy.join.resuming}</p>
        </main>
      </div>
    );
  }

  return (
    <div className="sh-phone">
      <header className="sh-phone-bar">
        <span className="sh-brand">{copy.brand}</span>
      </header>
      <main className="sh-phone-body">
        <form onSubmit={handleSubmit} className="sh-form">
          <label className="sh-label" htmlFor="name">
            {copy.join.nameLabel}
          </label>
          <input
            id="name"
            className="sh-input"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={64}
            disabled={loading}
            autoComplete="given-name"
          />

          <label className="sh-label" htmlFor="code">
            {copy.join.codeLabel}
          </label>
          <input
            id="code"
            className="sh-input sh-input-code"
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            maxLength={8}
            disabled={loading}
            autoCapitalize="characters"
          />

          {error && (
            <p role="alert" className="sh-error">
              {error}
            </p>
          )}

          <button type="submit" className="sh-button" disabled={loading}>
            {loading ? copy.join.joining : copy.join.submit}
          </button>
        </form>
      </main>
    </div>
  );
}
