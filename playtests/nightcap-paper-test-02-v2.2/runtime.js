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
    events: [],
    majorInvestigations: [],
    timeToFirstInvestigationSeconds: null,
    pulseResult: '',
    leverageResult: '',
    caseCommitment: '',
    finalNextInterest: '',
    completionStatus: 'in_progress',
    abandonmentPoint: '',
    currentStep: 'welcome',
    nextStep: '',
    lastLeadId: '',
    earned: [],
    majorCount: 0,
    rivalLead: '',
    minigameOutcome: '',
    leverageUsed: false,
    firstAccess: '',
    caseDraft: { killer: '', mechanism: '', access: '', contradiction: '' },
  };
}

export function recordAction(session, { label, branch = '', discovery = '' }) {
  session.actionSequence.push(label);
  if (branch && !session.investigationBranches.includes(branch)) session.investigationBranches.push(branch);
  if (discovery && !session.discoveries.includes(discovery)) session.discoveries.push(discovery);
  return session;
}

export function recordEvent(session, name, detail = '') {
  session.events.push(detail ? `${name}:${detail}` : name);
  return session;
}

export function recordMajorInvestigation(session, id, at = new Date().toISOString()) {
  if (!session.majorInvestigations.includes(id)) session.majorInvestigations.push(id);
  if (session.timeToFirstInvestigationSeconds === null) {
    session.timeToFirstInvestigationSeconds = Math.max(0, Math.round((Date.parse(at) - Date.parse(session.startedAt)) / 1000));
  }
  return session;
}

export function completeSession(session, completedAt = new Date().toISOString(), status = 'completed') {
  session.completedAt = completedAt;
  session.durationSeconds = Math.max(0, Math.round((Date.parse(completedAt) - Date.parse(session.startedAt)) / 1000));
  session.completionStatus = status;
  if (status === 'abandoned') session.abandonmentPoint = String(session.currentStep || 'unknown');
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
    time_to_first_investigation_seconds: session.timeToFirstInvestigationSeconds ?? '',
    major_investigations: session.majorInvestigations.join(' > '),
    event_sequence: session.events.join(' > '),
    abandonment_point: session.abandonmentPoint,
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
