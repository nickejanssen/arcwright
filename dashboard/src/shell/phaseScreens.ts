// The phase-to-screen table. Given what the engine said (lobby and round), it
// names which screen to show on the TV and on a phone. It holds no rule: it
// reads the engine's status and phase name and looks them up.
//
// The round screens are filled in by AW-332 (the mini-game phase waits for its
// next pull request) and the endgame screens by AW-333; until a phase has one,
// the plain "play continues" screen shows.

import type { ComponentType } from "react";
import type { LobbyState } from "../api/lobby";
import type { RoundState } from "../api/round";
import { endgameScreens } from "../screens/endgame";
import { roundScreens } from "../screens/round";

export type SurfaceKind = "tv" | "phone";

export interface SlotProps {
  sessionId: string;
  lobby: LobbyState;
  round: RoundState;
  // A phone's own seat and sign-in. The TV holds neither, so a TV screen is
  // given neither; a screen that needs them is a phone screen.
  seat?: SlotSeat;
  getToken?: () => Promise<string>;
}

export interface SlotSeat {
  // Matches this phone to its row in the room view. Never shown.
  participantId: string;
  displayName: string;
}

// One phase's screens, one per surface. Either may be left empty.
export interface SlotMap {
  tv?: ComponentType<SlotProps>;
  phone?: ComponentType<SlotProps>;
}

export type SlotTable = Readonly<Record<string, SlotMap>>;

export type Resolved =
  | { kind: "room" }
  | { kind: "paused" }
  | { kind: "ended" }
  | { kind: "phase"; phase: string; Slot: ComponentType<SlotProps> }
  | { kind: "fallback" };

export const DEFAULT_SLOTS: SlotTable = { ...roundScreens, ...endgameScreens };

export function resolveScreen(
  surface: SurfaceKind,
  lobby: LobbyState,
  round: RoundState | null,
  slots: SlotTable = DEFAULT_SLOTS,
): Resolved {
  if (lobby.status === "created") return { kind: "room" };
  if (
    lobby.status === "completed" ||
    lobby.status === "abandoned" ||
    round?.status === "ended"
  ) {
    return { kind: "ended" };
  }
  if (lobby.status === "paused" || round?.status === "paused") {
    return { kind: "paused" };
  }
  const phase = round?.phase ?? null;
  const Slot = phase === null ? undefined : slots[phase]?.[surface];
  if (phase !== null && Slot) return { kind: "phase", phase, Slot };
  return { kind: "fallback" };
}
