/* global URL */
import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createRunId,
  createSession,
  recordAction,
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
  recordAction(s, { label: 'Examine bookcase', branch: 'library', discovery: 'Hidden bookcase catch' });
  recordAction(s, { label: 'Press Jonas', branch: 'guest statements', discovery: 'Jonas says west service door was locked' });
  assert.equal(s.actionSequence.join(' > '), 'Examine bookcase > Press Jonas');
  assert.deepEqual(s.investigationBranches, ['library', 'guest statements']);
  assert.deepEqual(s.discoveries, ['Hidden bookcase catch', 'Jonas says west service door was locked']);
});

test('completion stamps duration and status', () => {
  const s = createSession('nightcap-paper-test-02-v2.2', '2026-08-28T20:00:00.000Z');
  completeSession(s, '2026-08-28T20:05:30.000Z', 'completed');
  assert.equal(s.durationSeconds, 330);
  assert.equal(s.completionStatus, 'completed');
});

test('telemetry exports one-row friendly strings', () => {
  const s = createSession('nightcap-paper-test-02-v2.2', '2026-08-28T20:00:00.000Z');
  s.runId = 'PT2-ABC123';
  recordAction(s, { label: 'Examine bookcase', branch: 'library', discovery: 'Hidden bookcase catch' });
  s.caseCommitment = 'Jonas';
  const row = serializeTelemetry(s, { deviceClass: 'mobile', browserClass: 'Chrome' });
  assert.equal(row.prototype_version, 'nightcap-paper-test-02-v2.2');
  assert.equal(row.action_sequence, 'Examine bookcase');
  assert.equal(row.investigation_branches, 'library');
  assert.equal(row.discoveries, 'Hidden bookcase catch');
  assert.equal(row.case_commitment, 'Jonas');
});

test('feedback URL uses configured Jotform unique-name mapping', () => {
  const base = 'https://form.jotform.com/262397917027062';
  const telemetry = { prototype_version: 'v2.2', run_id: 'PT2-ABC123' };
  const map = { prototype_version: 'prototypeVersion', run_id: 'runId' };
  const url = new URL(buildFeedbackUrl(base, telemetry, map));
  assert.equal(url.searchParams.get('prototypeVersion'), 'v2.2');
  assert.equal(url.searchParams.get('runId'), 'PT2-ABC123');
});

test('filters fixture choices that depend on undiscovered evidence', () => {
  const options = [
    { label: 'Use cufflink', requiresAny: ['cufflink'] },
    { label: 'Use corridor', requiresAny: ['bookcase', 'corridor'] },
    { label: 'Stay private' },
  ];
  assert.deepEqual(filterEligibleOptions(options, ['bookcase']).map(x => x.label), ['Use corridor', 'Stay private']);
});
