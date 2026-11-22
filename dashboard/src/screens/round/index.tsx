// Round screens, keyed by the engine's phase name, one entry per surface. The
// story and eyes-up screens serve both scene and bridge. The mini-game phase
// phase is AW-332 pull request B; Last Call (commit) is AW-333.

import type { SlotMap } from "../../shell/phaseScreens";
import EyesUpPhone from "./EyesUpPhone";
import InvestigatePhone from "./InvestigatePhone";
import MiniGamePhone from "./MiniGamePhone";
import MiniGameTv from "./MiniGameTv";
import StoryTv from "./StoryTv";
import ThinkingTv from "./ThinkingTv";

export const roundScreens: Readonly<Record<string, SlotMap>> = {
  scene: { tv: StoryTv, phone: EyesUpPhone },
  choices: { tv: ThinkingTv, phone: InvestigatePhone },
  mini_game: { tv: MiniGameTv, phone: MiniGamePhone },
  bridge: { tv: StoryTv, phone: EyesUpPhone },
};
