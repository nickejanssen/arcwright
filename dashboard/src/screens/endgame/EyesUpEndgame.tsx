import type { SlotProps } from "../../shell/phaseScreens";
import { copy } from "../../shell/copy";
import PhoneRoundFrame from "../round/PhoneRoundFrame";

export default function EyesUpEndgame({
  sessionId,
  getToken,
  seat,
  round,
}: SlotProps) {
  return (
    <PhoneRoundFrame
      sessionId={sessionId}
      getToken={getToken}
      seat={seat}
      round={round}
      left={null}
      now={<p className="sh-title">{copy.round.eyesUp}</p>}
    />
  );
}
