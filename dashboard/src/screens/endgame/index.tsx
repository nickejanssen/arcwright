// Endgame screens (reveal, result, recap), keyed by the engine's phase name,
// one entry per surface. AW-333 fills this in; until then the plain "game
// has ended" screen shows.

import type { SlotMap } from "../../shell/phaseScreens";
import LastCallTv from "./LastCallTv";
import TheoryPhone from "./TheoryPhone";
import AccusedTv from "./AccusedTv";
import EyesUpEndgame from "./EyesUpEndgame";

export const endgameScreens: Readonly<Record<string, SlotMap>> = {
  commit: { tv: LastCallTv, phone: TheoryPhone },
  reveal: { tv: AccusedTv, phone: EyesUpEndgame },
};
