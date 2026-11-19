// Round screens (scene, choices, mini_game, bridge, commit), keyed by the
// engine's phase name, one entry per surface. AW-332 fills this in; each
// phase left empty shows the plain "play continues" screen.

import type { SlotMap } from "../../shell/phaseScreens";

export const roundScreens: Readonly<Record<string, SlotMap>> = {};
