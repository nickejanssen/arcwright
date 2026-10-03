// Pure analysis helpers. Inputs must contain only eligible, included sessions.
export function classifyLeverage(events, initialBalance) {
  const choices = events.filter(
    (event) => event.event_type === "leverage_choice",
  );
  const spent = choices.filter((event) => event.choice === "spend").length;
  const explicitlySaved = choices.filter(
    (event) => event.choice === "save",
  ).length;
  const remaining = Math.max(0, initialBalance - spent);
  return { spent, explicitlySaved, remaining, unused: remaining };
}

export function firstTargetGate(targets) {
  const included = targets.length;
  const counts = new Map();
  let measured = 0;
  for (const target of targets) {
    if (typeof target !== "string" || target.length === 0) continue;
    measured += 1;
    counts.set(target, (counts.get(target) ?? 0) + 1);
  }
  const missing = included - measured;
  const maxObserved = Math.max(0, ...counts.values());
  const lowerConcentration = included ? maxObserved / included : null;
  const upperConcentration = included
    ? (maxObserved + missing) / included
    : null;
  let status = "inconclusive";
  if (measured > 0 && upperConcentration <= 0.75) status = "pass";
  else if (measured > 0 && lowerConcentration > 0.75) status = "fail";
  return {
    status,
    included,
    measured,
    missing,
    maxObserved,
    lowerConcentration,
    upperConcentration,
  };
}

export function postLockTimingGate(intervals) {
  const attempted = intervals.length;
  const valid = intervals.filter(
    (seconds) =>
      typeof seconds === "number" && Number.isFinite(seconds) && seconds >= 0,
  );
  const measured = valid.length;
  const missing = attempted - measured;
  const sorted = valid.toSorted((left, right) => left - right);
  const center = Math.floor(measured / 2);
  const median =
    measured === 0
      ? null
      : measured % 2
        ? sorted[center]
        : (sorted[center - 1] + sorted[center]) / 2;
  const status =
    measured < 6 || missing > 0
      ? "inconclusive"
      : median <= 60
        ? "pass"
        : "fail";
  return { status, attempted, measured, missing, median };
}
