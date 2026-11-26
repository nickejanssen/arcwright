// Endgame screens (Last Call to the survey), keyed by the engine's phase name,
// one entry per surface. The phone stays eyes-up through "result" and shows its
// own result from "recap" on.

import type { SlotMap } from "../../shell/phaseScreens";
import LastCallTv from "./LastCallTv";
import TheoryPhone from "./TheoryPhone";
import AccusedTv from "./AccusedTv";
import EyesUpEndgame from "./EyesUpEndgame";
import VerdictTv from "./VerdictTv";
import PostmortemTv from "./PostmortemTv";
import ResultPhone from "./ResultPhone";
import ThanksTv from "../survey/ThanksTv";
import SurveyPhone from "../survey/SurveyPhone";
import { AFTER_RECAP } from "./after";

export const endgameScreens: Readonly<Record<string, SlotMap>> = {
  commit: { tv: LastCallTv, phone: TheoryPhone },
  reveal: { tv: AccusedTv, phone: EyesUpEndgame },
  result: { tv: VerdictTv, phone: EyesUpEndgame },
  recap: { tv: PostmortemTv, phone: ResultPhone },
  [AFTER_RECAP]: { tv: ThanksTv, phone: SurveyPhone },
};
