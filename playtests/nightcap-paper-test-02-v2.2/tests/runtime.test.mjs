/* global URL */
import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createRunId,
  createSession,
  recordAction,
  recordEvent,
  recordMajorInvestigation,
  completeSession,
  serializeTelemetry,
  buildFeedbackUrl,
  filterEligibleOptions,
} from '../runtime.js';

test('run IDs are anonymous and readable', () => {
  assert.match(createRunId(() => 0.123456), /^PT2-[A-Z0-9]{6}$/);
});

test('records readable ordered actions without opaque IDs', () => {
  const s = createSession('nightcap-paper-test-02-v2.2', '2026-08-28T20:00:00.000Z');
  recordAction(s, { label: 'Inspect restoration cart', branch: 'access', discovery: 'Fresh plaster grit at office threshold' });
  recordAction(s, { label: 'Press Julian', branch: 'statements', discovery: 'Julian denies entering the office' });
  assert.equal(s.actionSequence.join(' > '), 'Inspect restoration cart > Press Julian');
  assert.deepEqual(s.investigationBranches, ['access', 'statements']);
  assert.deepEqual(s.discoveries, ['Fresh plaster grit at office threshold', 'Julian denies entering the office']);
});

test('records structured events without interrupting play', () => {
  const s = createSession('nightcap-paper-test-02-v2.2', '2026-08-28T20:00:00.000Z');
  recordEvent(s, 'opening_completed');
  recordEvent(s, 'rival_pursued', 'office');
  assert.deepEqual(s.events, ['opening_completed', 'rival_pursued:office']);
});

test('first major investigation records time-to-first-action once', () => {
  const s = createSession('nightcap-paper-test-02-v2.2', '2026-08-28T20:00:00.000Z');
  recordMajorInvestigation(s, 'cart', '2026-08-28T20:00:45.000Z');
  recordMajorInvestigation(s, 'medication', '2026-08-28T20:02:00.000Z');
  assert.equal(s.timeToFirstInvestigationSeconds, 45);
  assert.deepEqual(s.majorInvestigations, ['cart', 'medication']);
});

test('completion stamps duration, status, and abandonment point', () => {
  const s = createSession('nightcap-paper-test-02-v2.2', '2026-08-28T20:00:00.000Z');
  s.currentStep = 'minigame';
  completeSession(s, '2026-08-28T20:05:30.000Z', 'abandoned');
  assert.equal(s.durationSeconds, 330);
  assert.equal(s.completionStatus, 'abandoned');
  assert.equal(s.abandonmentPoint, 'minigame');
});

test('telemetry exports one-row friendly strings and representative-test signals', () => {
  const s = createSession('nightcap-paper-test-02-v2.2', '2026-08-28T20:00:00.000Z');
  s.runId = 'PT2-ABC123';
  recordMajorInvestigation(s, 'cart', '2026-08-28T20:00:45.000Z');
  recordAction(s, { label: 'Inspect restoration cart', branch: 'access', discovery: 'Fresh plaster grit at office threshold' });
  recordEvent(s, 'minigame_result', 'win');
  s.pulseResult = 'win';
  s.caseCommitment = 'killer=Julian | mechanism=Substituted dose | access=Restoration key | failed_claim=Never entered office';
  const row = serializeTelemetry(s, { deviceClass: 'mobile', browserClass: 'Chrome' });
  assert.equal(row.prototype_version, 'nightcap-paper-test-02-v2.2');
  assert.equal(row.action_sequence, 'Inspect restoration cart');
  assert.equal(row.investigation_branches, 'access');
  assert.equal(row.discoveries, 'Fresh plaster grit at office threshold');
  assert.equal(row.case_commitment, s.caseCommitment);
  assert.equal(row.time_to_first_investigation_seconds, 45);
  assert.equal(row.major_investigations, 'cart');
  assert.equal(row.event_sequence, 'minigame_result:win');
});

test('feedback URL uses configured field mapping', () => {
  const base = 'https://form.jotform.com/262397917027062';
  const telemetry = { prototype_version: 'v2.2', run_id: 'PT2-ABC123' };
  const map = { prototype_version: 'prototype_version', run_id: 'run_id' };
  const url = new URL(buildFeedbackUrl(base, telemetry, map));
  assert.equal(url.searchParams.get('prototype_version'), 'v2.2');
  assert.equal(url.searchParams.get('run_id'), 'PT2-ABC123');
});

test('filters fixture choices that depend on undiscovered evidence', () => {
  const options = [
    { label: 'Use medication case', requiresAny: ['medication'] },
    { label: 'Use office access', requiresAny: ['cart', 'key'] },
    { label: 'Keep it private' },
  ];
  assert.deepEqual(filterEligibleOptions(options, ['cart']).map(x => x.label), ['Use office access', 'Keep it private']);
});
