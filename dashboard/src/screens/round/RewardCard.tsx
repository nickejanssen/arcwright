// Screen 12: read saved rewards from the player's menu. Live reward messages
// may be missed, so the room phase feed is the retry trigger.

import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { usePlayerApi } from "../../api/usePlayerApi";
import type { RoundState } from "../../api/round";
import { copy } from "../../shell/copy";

interface RewardCardProps {
  sessionId: string;
  getToken: (() => Promise<string>) | undefined;
  round: RoundState | null;
  children: ReactNode;
}

function readAcknowledged(sessionId: string): Set<string> {
  try {
    const value = window.localStorage.getItem(`nightcap:rewards:${sessionId}`);
    const parsed: unknown = value ? JSON.parse(value) : [];
    return new Set(
      Array.isArray(parsed)
        ? parsed.filter((id) => typeof id === "string")
        : [],
    );
  } catch {
    return new Set();
  }
}

export default function RewardCard(props: RewardCardProps) {
  const api = usePlayerApi(props.sessionId, props.getToken);
  const [rewards, setRewards] = useState<Array<{ grantId: string }>>([]);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [acknowledged, setAcknowledged] = useState(() =>
    readAcknowledged(props.sessionId),
  );

  useEffect(() => {
    if (!props.round || props.round.phaseEntry === null) return;
    let cancelled = false;
    void api
      .menu()
      .then((menu) => {
        if (cancelled) return;
        setRewards(menu.rewards);
        setRemaining(menu.remainingBudget);
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [api, props.round?.phase, props.round?.phaseEntry]);

  const reward = rewards.find((item) => !acknowledged.has(item.grantId));
  if (!reward || remaining === null) return <>{props.children}</>;

  return (
    <section className="rd-reward-card" role="status">
      <p className="sh-title">{copy.round.earnedInvestigation}</p>
      <p className="sh-line">{copy.round.left(remaining)}</p>
      <button
        type="button"
        className="sh-button"
        onClick={() => {
          const next = new Set(acknowledged);
          next.add(reward.grantId);
          try {
            window.localStorage.setItem(
              `nightcap:rewards:${props.sessionId}`,
              JSON.stringify([...next]),
            );
          } catch {
            // Losing this per-phone convenience only means the card may recur.
          }
          setAcknowledged(next);
        }}
      >
        {copy.round.ok}
      </button>
    </section>
  );
}
