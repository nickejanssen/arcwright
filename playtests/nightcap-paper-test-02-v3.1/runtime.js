/* global URL, URLSearchParams */
const DEFAULT_STORAGE_KEY = "nightcap-paper-test-02-v3.1-state";

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function makeRunId() {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
  return `run-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function createInitialState(caseData, options = {}) {
  const nowMs = options.nowMs ?? Date.now();
  return {
    fixtureId: caseData.fixture_id,
    fixtureVersion: caseData.fixture_version,
    runId: options.runId ?? makeRunId(),
    startedAt: new Date(nowMs).toISOString(),
    startedAtMs: nowMs,
    completedAt: null,
    deviceClass: options.deviceClass ?? "unknown",
    browserClass: options.browserClass ?? "unknown",
    phase: "opening",
    sequenceCounter: 0,
    eventSequence: [],
    majorActions: 0,
    investigatedTargets: [],
    discoveries: [],
    privateDiscoveries: [],
    encounterHistory: [],
    privateNotes: "",
    leverage: caseData.leverage.starting_amount,
    followThreadUsed: false,
    rival: {
      actions: [],
      knownFacts: [...(caseData.rival.initial_knowledge ?? [])],
      lockObservation: null,
      accusation: null,
    },
    lock: {
      status: "unavailable",
      startedAtMs: null,
      currentPin: 0,
      setPins: [],
      winner: null,
      outcome: null,
      firstLookClaimed: false,
      publicReleased: false,
      postResultActions: 0,
      leverageChoice: null,
    },
    caseFile: {
      culprit: null,
      pieces: [],
      draftCulprit: null,
      draftPieces: [],
      correct: null,
      lockedAt: null,
    },
    surveyHandoffAt: null,
    revealReturnAt: null,
    completionStatus: "in-progress",
    abandonmentPoint: null,
    ui: {
      lastScene: null,
      lastTarget: null,
      peoplePickerOpen: false,
      notice: null,
    },
  };
}

export function recordEvent(state, event, nowMs = Date.now()) {
  state.sequenceCounter += 1;
  const normalized = {
    sequence: state.sequenceCounter,
    elapsed_ms: Math.max(0, nowMs - state.startedAtMs),
    phase: event.phase ?? state.phase,
    event_type: event.event_type,
    target: event.target ?? null,
    choice: event.choice ?? null,
    outcome: event.outcome ?? null,
  };
  state.eventSequence.push(normalized);
  return normalized;
}

export function persistState(
  state,
  storage = globalThis.sessionStorage,
  key = DEFAULT_STORAGE_KEY,
) {
  if (!storage?.setItem) return false;
  storage.setItem(key, JSON.stringify(state));
  return true;
}

export function restoreState(
  caseData,
  storage = globalThis.sessionStorage,
  key = DEFAULT_STORAGE_KEY,
) {
  if (!storage?.getItem) return null;
  const raw = storage.getItem(key);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    if (
      parsed.fixtureId !== caseData.fixture_id ||
      parsed.fixtureVersion !== caseData.fixture_version
    )
      return null;
    return parsed;
  } catch {
    return null;
  }
}

export function completeOpening(state, nowMs = Date.now()) {
  if (state.phase !== "opening") return false;
  state.phase = "investigation";
  recordEvent(state, { event_type: "opening_complete" }, nowMs);
  return true;
}

export function chooseInvestigation(
  state,
  targetId,
  nowMs = Date.now(),
  maxActions = 6,
) {
  if (state.phase !== "investigation") return false;
  if (state.majorActions >= maxActions) return false;
  if (state.investigatedTargets.includes(targetId)) return false;
  state.investigatedTargets.push(targetId);
  state.majorActions += 1;
  recordEvent(
    state,
    { event_type: "investigation_choice", target: targetId, choice: targetId },
    nowMs,
  );
  return true;
}

function appendEncounter(state, encounter) {
  state.encounterHistory ??= [];
  if (state.encounterHistory.some((item) => item.id === encounter.id))
    return false;
  state.encounterHistory.push(clone(encounter));
  return true;
}

export function reviewEncounter(state, encounterId) {
  const encounter = (state.encounterHistory ?? []).find(
    (item) => item.id === encounterId,
  );
  return encounter ? clone(encounter) : null;
}

export function setPrivateNotes(state, text) {
  state.privateNotes = Array.from(String(text ?? ""))
    .slice(0, 500)
    .join("");
  return state.privateNotes;
}

export function visitInvestigation(
  state,
  caseData,
  targetId,
  nowMs = Date.now(),
) {
  const route = caseData.investigation.routes[targetId];
  const interview = caseData.interviews[targetId];
  if (!route && !interview) return false;
  const maxActions = caseData.investigation.max_major_actions ?? 6;
  if (!chooseInvestigation(state, targetId, nowMs, maxActions)) return false;
  const scene = route?.scene ?? `${interview.opening}\n\n${interview.claim}`;
  const discoveries = route?.discoveries ?? interview.discoveries ?? [];
  for (const discovery of discoveries)
    recordDiscovery(state, discovery, {}, nowMs);
  appendEncounter(state, {
    id: `${route ? "route" : "interview"}:${targetId}`,
    targetId,
    kind: route ? "route" : "interview",
    scene,
    discoveryIds: discoveries.map((item) => item.id),
  });
  if (state.lock.status === "resolved" && !state.lock.publicReleased)
    releaseCylinderPublicly(state, caseData, nowMs);
  return true;
}

function hasPromptFact(state, requiresAny) {
  return (requiresAny ?? []).some((id) => discoveryOwned(state, id));
}

export function canChallengeClaim(state, caseData, suspectId) {
  const conditional = caseData.interviews[suspectId]?.conditional;
  return (
    state.phase === "investigation" &&
    state.investigatedTargets.includes(suspectId) &&
    Boolean(conditional) &&
    hasPromptFact(state, conditional.requires_any) &&
    !(conditional.discoveries ?? []).every((item) =>
      discoveryOwned(state, item.id),
    ) &&
    !(state.encounterHistory ?? []).some(
      (item) => item.id === `challenge:${suspectId}`,
    )
  );
}

export function challengeClaim(state, caseData, suspectId, nowMs = Date.now()) {
  if (!canChallengeClaim(state, caseData, suspectId)) return false;
  const conditional = caseData.interviews[suspectId].conditional;
  recordInferenceAction(
    state,
    suspectId,
    "challenge-claim",
    "new-testimony",
    nowMs,
  );
  for (const discovery of conditional.discoveries ?? [])
    recordDiscovery(state, discovery, {}, nowMs);
  appendEncounter(state, {
    id: `challenge:${suspectId}`,
    targetId: suspectId,
    kind: "challenge",
    scene: conditional.scene,
    discoveryIds: (conditional.discoveries ?? []).map((item) => item.id),
  });
  return true;
}

export function canFollowThread(state, caseData, suspectId) {
  const follow = caseData.interviews[suspectId]?.follow_thread;
  return (
    state.phase === "investigation" &&
    state.investigatedTargets.includes(suspectId) &&
    Boolean(follow) &&
    state.leverage >= 1 &&
    !state.followThreadUsed &&
    !discoveryOwned(state, follow.discovery.id) &&
    hasPromptFact(state, follow.requires_any)
  );
}

export function followThread(state, caseData, suspectId, nowMs = Date.now()) {
  if (!canFollowThread(state, caseData, suspectId)) return false;
  const follow = caseData.interviews[suspectId].follow_thread;
  if (!spendLeverage(state, caseData, "follow-the-thread", nowMs)) return false;
  recordInferenceAction(
    state,
    suspectId,
    "follow-the-thread",
    follow.discovery.id,
    nowMs,
  );
  recordDiscovery(state, follow.discovery, {}, nowMs);
  appendEncounter(state, {
    id: `follow:${suspectId}`,
    targetId: suspectId,
    kind: "follow",
    scene: follow.scene,
    discoveryIds: [follow.discovery.id],
  });
  return true;
}

function discoveryOwned(state, id) {
  return (
    state.discoveries.some((item) => item.id === id) ||
    state.privateDiscoveries.some((item) => item.id === id)
  );
}

export function recordDiscovery(
  state,
  discovery,
  options = {},
  nowMs = Date.now(),
) {
  if (!discovery || discoveryOwned(state, discovery.id)) return false;
  const copy = clone(discovery);
  const visibility = options.visibility ?? "public";
  if (visibility === "private") state.privateDiscoveries.push(copy);
  else state.discoveries.push(copy);
  recordEvent(
    state,
    {
      event_type: "discovery",
      target: discovery.id,
      outcome: visibility,
    },
    nowMs,
  );
  return true;
}

export function recordInferenceAction(
  state,
  target,
  choice,
  outcome = null,
  nowMs = Date.now(),
) {
  recordEvent(
    state,
    { event_type: "inference_action", target, choice, outcome },
    nowMs,
  );
}

export function triggerRivalActivity(
  state,
  caseData,
  action,
  target,
  nowMs = Date.now(),
) {
  const key = `${action}:${target}`;
  if (state.rival.actions.some((item) => item.key === key)) return false;
  state.rival.actions.push({ key, action, target });
  const earned = caseData.rival.trajectory?.find(
    (item) => item.action === action && item.target === target,
  );
  if (earned?.fact && !state.rival.knownFacts?.includes(earned.fact)) {
    state.rival.knownFacts ??= [];
    state.rival.knownFacts.push(earned.fact);
  }
  recordEvent(
    state,
    { event_type: "rival_activity", target, choice: action },
    nowMs,
  );
  return true;
}

export function shouldOpenLockWindow(state, caseData) {
  if (state.lock.status !== "unavailable") return false;
  const triggerIds = new Set(caseData.competition.trigger_discoveries);
  const hasTrigger = [...state.discoveries, ...state.privateDiscoveries].some(
    (item) => triggerIds.has(item.id),
  );
  if (hasTrigger && state.majorActions >= 2) return true;
  return (
    state.majorActions >=
    caseData.competition.forced_rival_trigger_after_major_actions
  );
}

export function openLockWindow(state, nowMs = Date.now()) {
  if (state.phase !== "investigation" || state.lock.status !== "unavailable")
    return false;
  state.phase = "lock";
  state.lock.status = "active";
  state.lock.startedAtMs = nowMs;
  state.lock.currentPin = 0;
  state.lock.setPins = [];
  recordEvent(
    state,
    { event_type: "competitive_window_opened", target: "the-locked-box" },
    nowMs,
  );
  recordEvent(
    state,
    { event_type: "minigame_started", target: "the-locked-box" },
    nowMs,
  );
  return true;
}

export function declineLockWindow(state, caseData, nowMs = Date.now()) {
  if (state.phase !== "investigation" || state.lock.status !== "unavailable")
    return false;
  state.lock.status = "resolved";
  state.lock.outcome = "declined";
  state.lock.winner = null;
  state.lock.publicReleased = true;
  recordEvent(
    state,
    { event_type: "competitive_window_declined", target: "the-locked-box" },
    nowMs,
  );
  recordDiscovery(
    state,
    caseData.competition.fallback_public_observation,
    { visibility: "public" },
    nowMs,
  );
  return true;
}

export function attemptLockPin(
  state,
  caseData,
  displayedValue,
  nowMs = Date.now(),
) {
  const pinIndex = state.lock.currentPin;
  if (state.lock.status !== "active")
    return { accepted: false, outcome: state.lock.outcome, pinIndex };
  const elapsed = nowMs - state.lock.startedAtMs;
  if (elapsed >= caseData.competition.rival_finish_seconds * 1000) {
    resolveLock(state, caseData, "rival-win", nowMs);
    return { accepted: false, outcome: "rival-win", pinIndex };
  }
  if (elapsed >= caseData.competition.duration_seconds * 1000) {
    resolveLock(state, caseData, "timeout", nowMs);
    return { accepted: false, outcome: "timeout", pinIndex };
  }
  if (
    !Number.isFinite(displayedValue) ||
    displayedValue < 0 ||
    displayedValue > 100 ||
    !caseData.competition.pins[pinIndex]
  )
    return { accepted: false, outcome: "invalid", pinIndex };
  const pin = caseData.competition.pins[pinIndex];
  const outcome =
    displayedValue <= caseData.competition.red_zone_max ||
    displayedValue >= caseData.competition.red_zone_min
      ? "break"
      : Math.abs(displayedValue - pin.target) <= pin.tolerance
        ? "set"
        : "miss";
  setLockProgress(state, pinIndex, displayedValue, outcome, nowMs);
  if (outcome === "break") resolveLock(state, caseData, "break", nowMs);
  if (
    outcome === "set" &&
    state.lock.currentPin === caseData.competition.pins.length
  )
    resolveLock(state, caseData, "human-win", nowMs);
  return { accepted: true, outcome, pinIndex };
}

export function setLockProgress(
  state,
  pinIndex,
  value,
  outcome,
  nowMs = Date.now(),
) {
  if (state.lock.status !== "active") return false;
  if (state.lock.currentPin !== pinIndex) return false;
  recordEvent(
    state,
    {
      event_type: "minigame_action",
      target: `pin-${pinIndex + 1}`,
      choice: String(Math.round(value)),
      outcome,
    },
    nowMs,
  );
  if (outcome === "set") {
    state.lock.setPins.push(pinIndex);
    state.lock.currentPin += 1;
  }
  return true;
}

function cylinderObservation(caseData) {
  return caseData.competition.winner_private_observation;
}

export function resolveLock(state, caseData, outcome, nowMs = Date.now()) {
  if (state.lock.status !== "active") return false;
  if (
    nowMs - state.lock.startedAtMs >=
    caseData.competition.rival_finish_seconds * 1000
  )
    outcome = "rival-win";
  const allowed = new Set([
    "human-win",
    "rival-win",
    "break",
    "timeout",
    "abort",
  ]);
  if (!allowed.has(outcome))
    throw new Error(`Unknown lock outcome: ${outcome}`);

  state.lock.status = "resolved";
  state.lock.outcome = outcome;
  state.lock.winner =
    outcome === "human-win"
      ? "human"
      : outcome === "rival-win"
        ? "rival"
        : null;
  state.phase = "lock";

  if (outcome === "human-win") {
    recordDiscovery(
      state,
      cylinderObservation(caseData),
      { visibility: "private" },
      nowMs,
    );
    state.lock.firstLookClaimed = true;
  } else if (outcome === "rival-win") {
    state.rival.lockObservation = clone(cylinderObservation(caseData));
  } else {
    recordDiscovery(
      state,
      caseData.competition.fallback_public_observation,
      { visibility: "public" },
      nowMs,
    );
    state.lock.publicReleased = true;
  }

  recordEvent(
    state,
    {
      event_type: "minigame_result",
      target: "the-locked-box",
      outcome,
    },
    nowMs,
  );
  return true;
}

export function acknowledgeLockResult(state) {
  if (state.lock.status !== "resolved" || state.phase !== "lock") return false;
  state.phase = "investigation";
  return true;
}

export function releaseCylinderPublicly(state, caseData, nowMs = Date.now()) {
  if (state.lock.publicReleased) return false;
  const observation = caseData.competition.fallback_public_observation;
  if (!state.discoveries.some((item) => item.id === observation.id)) {
    state.privateDiscoveries = state.privateDiscoveries.filter(
      (item) => item.id !== observation.id,
    );
    recordDiscovery(state, observation, { visibility: "public" }, nowMs);
  }
  state.lock.publicReleased = true;
  recordEvent(
    state,
    {
      event_type: "first_look_closed",
      target: observation.id,
      outcome: "public",
    },
    nowMs,
  );
  return true;
}

export function spendLeverage(state, caseData, effectId, nowMs = Date.now()) {
  if (state.leverage < 1) return false;
  const effect = caseData.leverage.effects.find((item) => item.id === effectId);
  if (!effect) return false;
  if (
    effectId === "listen-in" &&
    (!state.rival.lockObservation ||
      state.lock.status !== "resolved" ||
      state.lock.outcome !== "rival-win" ||
      state.lock.leverageChoice)
  )
    return false;
  if (effectId === "follow-the-thread" && state.followThreadUsed) return false;

  state.leverage -= 1;
  if (effectId === "listen-in") {
    state.lock.leverageChoice = "spend";
    state.lock.firstLookClaimed = true;
    recordDiscovery(
      state,
      state.rival.lockObservation,
      { visibility: "private" },
      nowMs,
    );
  }
  if (effectId === "follow-the-thread") state.followThreadUsed = true;
  recordEvent(
    state,
    {
      event_type: "leverage_choice",
      target: effectId,
      choice: "spend",
      outcome: effectId,
    },
    nowMs,
  );
  return true;
}

export function saveLeverage(state, effectId, nowMs = Date.now()) {
  if (
    state.leverage < 1 ||
    state.lock.status !== "resolved" ||
    !["human-win", "rival-win"].includes(state.lock.outcome) ||
    state.lock.leverageChoice ||
    effectId !==
      (state.lock.outcome === "human-win" ? "first-look" : "listen-in")
  )
    return false;
  state.lock.leverageChoice = "save";
  recordEvent(
    state,
    {
      event_type: "leverage_choice",
      target: effectId,
      choice: "save",
      outcome: "saved",
    },
    nowMs,
  );
  return true;
}

export function resolveRivalTheory(state, caseData) {
  const theory = caseData.rival.theory;
  const knownFacts = new Set([
    ...(caseData.rival.initial_knowledge ?? []),
    ...(state.rival.knownFacts ?? []),
  ]);
  if (!theory?.requires_every?.every((fact) => knownFacts.has(fact)))
    return null;
  return theory.accusation;
}

export function canEnterLastCall(state, caseData) {
  return (
    state.phase === "investigation" &&
    state.majorActions >= caseData.investigation.last_call_min_actions &&
    state.lock.status !== "active"
  );
}

export function enterLastCall(state, caseData, nowMs = Date.now()) {
  if (!canEnterLastCall(state, caseData)) return false;
  if (!state.lock.publicReleased && state.lock.status === "resolved") {
    releaseCylinderPublicly(state, caseData, nowMs);
  }
  state.phase = "last-call";
  recordEvent(state, { event_type: "last_call" }, nowMs);
  return true;
}

export function ownedEvidenceIds(state) {
  return new Set(
    [...state.discoveries, ...state.privateDiscoveries].map((item) => item.id),
  );
}

export function setCaseFileDraft(state, culpritId, pieceIds) {
  if (state.phase !== "last-call" || state.caseFile.lockedAt) return false;
  state.caseFile.draftCulprit = culpritId || null;
  state.caseFile.draftPieces = [...new Set(pieceIds)];
  return true;
}

export function evaluateCaseFile(state, caseData, culpritId, pieceIds) {
  const owned = ownedEvidenceIds(state);
  const uniquePieces = [...new Set(pieceIds)];
  if (uniquePieces.length < 4 || uniquePieces.length > 5)
    return { correct: false, reason: "choose-four-or-five" };
  if (uniquePieces.some((id) => !owned.has(id)))
    return { correct: false, reason: "unowned-evidence" };
  if (culpritId !== caseData.culprit_id)
    return { correct: false, reason: "wrong-culprit" };

  for (const truthId of caseData.case_file.required_truths) {
    const groups = caseData.case_file.proof_groups[truthId] ?? [];
    const satisfied = groups.some((group) =>
      group.every((id) => uniquePieces.includes(id)),
    );
    if (!satisfied) return { correct: false, reason: `missing-${truthId}` };
  }
  return { correct: true, reason: "solved" };
}

export function commitCaseFile(
  state,
  caseData,
  culpritId,
  pieceIds,
  nowMs = Date.now(),
) {
  if (state.phase !== "last-call" || state.caseFile.lockedAt) return false;
  const verdict = evaluateCaseFile(state, caseData, culpritId, pieceIds);
  state.caseFile = {
    culprit: culpritId,
    pieces: [...pieceIds],
    draftCulprit: culpritId,
    draftPieces: [...pieceIds],
    correct: verdict.correct,
    reason: verdict.reason,
    lockedAt: new Date(nowMs).toISOString(),
  };
  state.phase = "survey";
  recordEvent(
    state,
    {
      event_type: "case_file_commitment",
      target: culpritId,
      outcome: verdict.correct ? "solved" : "not-solved",
    },
    nowMs,
  );
  return true;
}

export function markSurveyHandoff(state, nowMs = Date.now()) {
  if (state.surveyHandoffAt) return false;
  state.surveyHandoffAt = new Date(nowMs).toISOString();
  recordEvent(state, { event_type: "survey_handoff" }, nowMs);
  return true;
}

export function markRevealReturn(state, nowMs = Date.now()) {
  if (state.revealReturnAt) return false;
  state.revealReturnAt = new Date(nowMs).toISOString();
  state.phase = "reveal";
  recordEvent(
    state,
    { event_type: "reveal_return", outcome: "local-session-state-only" },
    nowMs,
  );
  return true;
}

export function markComplete(state, nowMs = Date.now()) {
  if (state.completedAt) return false;
  state.completedAt = new Date(nowMs).toISOString();
  state.completionStatus = "completed";
  recordEvent(state, { event_type: "completion" }, nowMs);
  return true;
}

export function markAbandoned(state, point, nowMs = Date.now()) {
  if (state.completionStatus === "completed") return false;
  state.completionStatus = "abandoned";
  state.abandonmentPoint = point;
  recordEvent(state, { event_type: "abandonment", target: point }, nowMs);
  return true;
}

export function deriveTelemetry(state) {
  const first = (type) =>
    state.eventSequence.find((event) => event.event_type === type);
  const investigationEvents = state.eventSequence.filter(
    (event) => event.event_type === "investigation_choice",
  );
  const discoveryEvents = state.eventSequence.filter(
    (event) => event.event_type === "discovery",
  );
  const inferenceEvents = state.eventSequence.filter(
    (event) => event.event_type === "inference_action",
  );
  const lockResult = state.eventSequence.find(
    (event) => event.event_type === "minigame_result",
  );
  const lockStart = state.eventSequence.find(
    (event) => event.event_type === "minigame_started",
  );
  const nextAfterLock = lockResult
    ? state.eventSequence.find(
        (event) =>
          event.sequence > lockResult.sequence &&
          ["investigation_choice", "inference_action"].includes(
            event.event_type,
          ),
      )
    : null;

  return {
    prototype_version: state.fixtureVersion,
    run_id: state.runId,
    started_at: state.startedAt,
    completed_at: state.completedAt ?? "",
    duration_seconds: state.completedAt
      ? Math.round((Date.parse(state.completedAt) - state.startedAtMs) / 1000)
      : "",
    action_sequence: investigationEvents
      .map((event) => event.target)
      .join(" > "),
    investigation_branches: [
      ...new Set(investigationEvents.map((event) => event.target)),
    ].join(","),
    discoveries: [...state.discoveries, ...state.privateDiscoveries]
      .map((item) => item.id)
      .join(","),
    pulse_result: lockResult?.outcome ?? "",
    case_commitment: state.caseFile.culprit
      ? JSON.stringify({
          culprit: state.caseFile.culprit,
          pieces: state.caseFile.pieces,
          correct: state.caseFile.correct,
        })
      : "",
    final_next_interest: nextAfterLock?.target ?? "",
    device_class: state.deviceClass,
    browser_class: state.browserClass,
    completion_status: state.completionStatus,
    time_to_first_investigation_seconds: first("investigation_choice")
      ? Math.round(first("investigation_choice").elapsed_ms / 1000)
      : "",
    time_to_first_discovery_seconds: discoveryEvents[0]
      ? Math.round(discoveryEvents[0].elapsed_ms / 1000)
      : "",
    time_to_first_inference_seconds: inferenceEvents[0]
      ? Math.round(inferenceEvents[0].elapsed_ms / 1000)
      : "",
    major_investigations: investigationEvents.length,
    route_diversity: new Set(investigationEvents.map((event) => event.target))
      .size,
    lock_completion_seconds:
      lockStart && lockResult
        ? Math.round((lockResult.elapsed_ms - lockStart.elapsed_ms) / 1000)
        : "",
    post_lock_return_seconds:
      lockResult && nextAfterLock
        ? Math.round((nextAfterLock.elapsed_ms - lockResult.elapsed_ms) / 1000)
        : "",
    event_sequence: JSON.stringify(state.eventSequence),
    abandonment_point: state.abandonmentPoint ?? "",
  };
}

const JOTFORM_FIELD_MAP = {
  prototype_version: "q13_textbox11",
  run_id: "q14_textbox12",
  started_at: "q15_textbox13",
  completed_at: "q16_textbox14",
  duration_seconds: "q17_textbox15",
  action_sequence: "q18_textbox16",
  investigation_branches: "q19_textbox17",
  discoveries: "q20_textbox18",
  pulse_result: "q21_textbox19",
  case_commitment: "q22_textbox20",
  final_next_interest: "q23_textbox21",
  device_class: "q24_textbox22",
  browser_class: "q25_textbox23",
  completion_status: "q26_textbox24",
  time_to_first_investigation_seconds:
    "q28_time_to_first_investigation_seconds",
  major_investigations: "q29_major_investigations",
  event_sequence: "q30_event_sequence",
  abandonment_point: "q31_abandonment_point",
};

export function buildSurveyUrl(
  state,
  baseUrl = "https://form.jotform.com/262397917027062",
) {
  const telemetry = deriveTelemetry(state);
  const url = new URL(baseUrl);
  for (const [key, field] of Object.entries(JOTFORM_FIELD_MAP)) {
    const value = telemetry[key];
    if (value !== undefined && value !== null && value !== "")
      url.searchParams.set(field, String(value));
  }
  return url.toString();
}

export function isRevealMode(search = globalThis.location?.search ?? "") {
  return new URLSearchParams(search).get("reveal") === "1";
}

export { DEFAULT_STORAGE_KEY };
