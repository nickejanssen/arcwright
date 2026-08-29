/* global URL */
const ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';

export function createRunId(random = Math.random) {
  let suffix = '';
  for (let i = 0; i < 6; i += 1) suffix += ALPHABET[Math.floor(random() * ALPHABET.length) % ALPHABET.length];
  return `PT2-${suffix}`;
}

export function createSession(version, startedAt = new Date().toISOString()) {
  return {
    prototypeVersion: version,
    runId: createRunId(),
    startedAt,
    completedAt: '',
    durationSeconds: null,
    actionSequence: [],
    investigationBranches: [],
    discoveries: [],
    pulseResult: '',
    caseCommitment: '',
    finalNextInterest: '',
    completionStatus: 'in_progress',
    currentStep: 0,
    earned: [],
  };
}

export function recordAction(session, { label, branch = '', discovery = '' }) {
  session.actionSequence.push(label);
  if (branch && !session.investigationBranches.includes(branch)) session.investigationBranches.push(branch);
  if (discovery && !session.discoveries.includes(discovery)) session.discoveries.push(discovery);
  return session;
}

export function completeSession(session, completedAt = new Date().toISOString(), status = 'completed') {
  session.completedAt = completedAt;
  session.durationSeconds = Math.max(0, Math.round((Date.parse(completedAt) - Date.parse(session.startedAt)) / 1000));
  session.completionStatus = status;
  return session;
}

export function serializeTelemetry(session, environment = {}) {
  return {
    prototype_version: session.prototypeVersion,
    run_id: session.runId,
    started_at: session.startedAt,
    completed_at: session.completedAt,
    duration_seconds: session.durationSeconds ?? '',
    action_sequence: session.actionSequence.join(' > '),
    investigation_branches: session.investigationBranches.join(' > '),
    discoveries: session.discoveries.join(' > '),
    pulse_result: session.pulseResult,
    case_commitment: session.caseCommitment,
    final_next_interest: session.finalNextInterest,
    device_class: environment.deviceClass || '',
    browser_class: environment.browserClass || '',
    completion_status: session.completionStatus,
  };
}

export function buildFeedbackUrl(baseUrl, telemetry, fieldParamMap = {}) {
  const url = new URL(baseUrl);
  Object.entries(telemetry).forEach(([key, value]) => {
    const param = fieldParamMap[key];
    if (param && value !== undefined && value !== null) url.searchParams.set(param, String(value));
  });
  return url.toString();
}

export function detectEnvironment(userAgent = '', width = 1024) {
  const ua = userAgent.toLowerCase();
  let browserClass = 'Other';
  if (ua.includes('edg/')) browserClass = 'Edge';
  else if (ua.includes('chrome/') || ua.includes('crios/')) browserClass = 'Chrome';
  else if (ua.includes('safari/') && !ua.includes('chrome/')) browserClass = 'Safari';
  else if (ua.includes('firefox/') || ua.includes('fxios/')) browserClass = 'Firefox';
  return { deviceClass: width < 768 ? 'mobile' : width < 1100 ? 'tablet' : 'desktop', browserClass };
}

export function filterEligibleOptions(options, earned = []) {
  const known = new Set(earned);
  return options.filter(option => !option.requiresAny?.length || option.requiresAny.some(id => known.has(id)));
}
