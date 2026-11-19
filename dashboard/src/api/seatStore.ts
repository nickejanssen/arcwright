// Keeps a player's seat on this phone so closing the tab does not lose it
// (spec 0095 decision 3). One entry per game. The TV never uses this file.
// Nothing here is written to a link, a screen or a log.

import type { FirebaseAuthSession } from "./auth";

export const SEAT_KEY_PREFIX = "arcwright.seat.";
export const SEAT_MAX_AGE_MS = 3 * 24 * 60 * 60 * 1000;

export interface StoredSeat {
  gameId: string;
  joinCode: string;
  participantId: string;
  characterId: string;
  displayName: string;
  auth: FirebaseAuthSession;
  savedAt: number;
}

export interface KeyValueStorage {
  readonly length: number;
  key(index: number): string | null;
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
  removeItem(key: string): void;
}

export interface SeatStore {
  save(seat: Omit<StoredSeat, "savedAt">): void;
  get(gameId: string): StoredSeat | null;
  findByCode(joinCode: string): StoredSeat | null;
  mostRecent(): StoredSeat | null;
  updateAuth(gameId: string, auth: FirebaseAuthSession): void;
  // Marks the seat as used now, so unused seats age out after three days.
  touch(gameId: string): void;
  clear(gameId: string): void;
}

function isSeat(value: unknown): value is StoredSeat {
  if (typeof value !== "object" || value === null) return false;
  const seat = value as Partial<StoredSeat>;
  const auth = seat.auth as Partial<FirebaseAuthSession> | undefined;
  return (
    typeof seat.gameId === "string" &&
    typeof seat.joinCode === "string" &&
    typeof seat.participantId === "string" &&
    typeof seat.characterId === "string" &&
    typeof seat.displayName === "string" &&
    typeof seat.savedAt === "number" &&
    typeof auth?.idToken === "string" &&
    typeof auth.refreshToken === "string" &&
    typeof auth.expiresAt === "number"
  );
}

export function createSeatStore(
  getStorage: () => KeyValueStorage | null,
  now: () => number = Date.now,
): SeatStore {
  function storage(): KeyValueStorage | null {
    try {
      return getStorage();
    } catch {
      return null;
    }
  }

  function remove(store: KeyValueStorage, key: string): void {
    try {
      store.removeItem(key);
    } catch {
      // Nothing more to do: a locked store keeps its entry.
    }
  }

  // Bad or old entries are deleted as they are met.
  function readKey(store: KeyValueStorage, key: string): StoredSeat | null {
    let raw: string | null;
    try {
      raw = store.getItem(key);
    } catch {
      return null;
    }
    if (raw === null) return null;
    let parsed: unknown;
    try {
      parsed = JSON.parse(raw);
    } catch {
      remove(store, key);
      return null;
    }
    if (!isSeat(parsed) || now() - parsed.savedAt > SEAT_MAX_AGE_MS) {
      remove(store, key);
      return null;
    }
    return parsed;
  }

  function all(): StoredSeat[] {
    const store = storage();
    if (!store) return [];
    const keys: string[] = [];
    try {
      for (let i = 0; i < store.length; i += 1) {
        const key = store.key(i);
        if (key?.startsWith(SEAT_KEY_PREFIX)) keys.push(key);
      }
    } catch {
      return [];
    }
    const seats: StoredSeat[] = [];
    for (const key of keys) {
      const seat = readKey(store, key);
      if (seat) seats.push(seat);
    }
    return seats;
  }

  function write(seat: StoredSeat): void {
    const store = storage();
    if (!store) return;
    try {
      store.setItem(SEAT_KEY_PREFIX + seat.gameId, JSON.stringify(seat));
    } catch {
      // A full or locked store: the player can still play this tab.
    }
  }

  return {
    save(seat) {
      write({ ...seat, savedAt: now() });
    },
    get(gameId) {
      const store = storage();
      return store ? readKey(store, SEAT_KEY_PREFIX + gameId) : null;
    },
    findByCode(joinCode) {
      const code = joinCode.trim().toUpperCase();
      return all().find((seat) => seat.joinCode.toUpperCase() === code) ?? null;
    },
    mostRecent() {
      return all().sort((a, b) => b.savedAt - a.savedAt)[0] ?? null;
    },
    updateAuth(gameId, auth) {
      const store = storage();
      const seat = store ? readKey(store, SEAT_KEY_PREFIX + gameId) : null;
      // The saved time stays: refreshing a token is not a use of the seat.
      if (seat) write({ ...seat, auth });
    },
    touch(gameId) {
      const store = storage();
      const seat = store ? readKey(store, SEAT_KEY_PREFIX + gameId) : null;
      if (seat) write({ ...seat, savedAt: now() });
    },
    clear(gameId) {
      const store = storage();
      if (store) remove(store, SEAT_KEY_PREFIX + gameId);
    },
  };
}

export const seatStore: SeatStore = createSeatStore(() => {
  const store = (globalThis as { localStorage?: KeyValueStorage }).localStorage;
  return store ?? null;
});
