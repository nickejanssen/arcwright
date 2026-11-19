// Endgame screens (reveal, result, recap), keyed by the engine's phase name,
// one entry per surface. AW-333 fills this in; until then the plain "game
// has ended" screen shows.

import type { SlotMap } from "../../shell/phaseScreens";

export const endgameScreens: Readonly<Record<string, SlotMap>> = {};
