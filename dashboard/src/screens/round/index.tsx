// Round screens, keyed by the engine's phase name, one entry per surface. The
// story and eyes-up screens serve both scene and bridge. The mini-game phase
// (screens 10 to 12) is the next pull request of AW-332 and Last Call (commit)
// is AW-333, so those phases show the plain "play continues" screen until then.

import type { SlotMap } from "../../shell/phaseScreens";
import EyesUpPhone from "./EyesUpPhone";
import InvestigatePhone from "./InvestigatePhone";
import StoryTv from "./StoryTv";
import ThinkingTv from "./ThinkingTv";

export const roundScreens: Readonly<Record<string, SlotMap>> = {
  scene: { tv: StoryTv, phone: EyesUpPhone },
  choices: { tv: ThinkingTv, phone: InvestigatePhone },
  bridge: { tv: StoryTv, phone: EyesUpPhone },
};
