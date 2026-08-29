import test from 'node:test';
import assert from 'node:assert/strict';

global.window = {};
await import('../config.js');
const cfg = global.window.NIGHTCAP_PLAYTEST;

function available(entries, earned) {
  const known = new Set(earned);
  return entries.filter(option => !option.requiresAny?.length || option.requiresAny.some(id => known.has(id)));
}

function assertCaseRoute(earned) {
  assert.ok(available(cfg.caseFile.mechanism, earned).length > 0, 'route needs mechanism proof');
  assert.ok(available(cfg.caseFile.access, earned).length > 0, 'route needs access proof');
  assert.ok(available(cfg.caseFile.contradictions, earned).length > 0, 'route needs a failed claim');
}

test('Last Toast presents four meaningful suspects', () => {
  assert.equal(cfg.opening.suspects.length, 4);
  assert.deepEqual(cfg.caseFile.suspects, ['Mara Voss', 'Dr. Theo Bell', 'Celeste Vale', 'Julian Cross']);
  cfg.opening.suspects.forEach(suspect => {
    assert.ok(suspect.role);
    assert.ok(suspect.detail.length > 30);
  });
});

test('scene-first opening offers four concrete observed irregularities', () => {
  assert.equal(cfg.opening.observations.length, 4);
  cfg.opening.observations.forEach(observation => {
    assert.ok(observation.label);
    assert.ok(observation.text);
    assert.ok(observation.discovery);
    assert.ok(observation.unlocks.length >= 2);
  });
});

test('losing the minigame does not make substitution proof unavailable', () => {
  const nonMinigameMechanismRoutes = cfg.caseFile.mechanism.filter(option => !option.requiresAny?.includes('minigame_case'));
  assert.ok(nonMinigameMechanismRoutes.length >= 3);
  assert.ok(nonMinigameMechanismRoutes.some(option => option.requiresAny?.includes('staff_inventory')));
});

test('essential proof categories have redundant routes', () => {
  assert.ok(cfg.caseFile.mechanism.length >= 4);
  assert.ok(cfg.caseFile.access.length >= 4);
  assert.ok(cfg.caseFile.contradictions.length >= 4);
});

test('a red-herring-first route remains capable of supporting a case after a minigame loss', () => {
  assertCaseRoute(['mara_document', 'champagne', 'staff_inventory', 'key_log', 'julian_statement']);
});

test('an indirect Celeste/Theo route can still support all three proof dimensions', () => {
  assertCaseRoute(['celeste_corridor', 'office_route', 'theo_followup', 'waiter_timing', 'julian_statement']);
});

test('an early Julian route does not depend on winning the minigame', () => {
  assertCaseRoute(['julian_cart', 'office_route', 'medication_inventory', 'staff_inventory', 'julian_statement']);
});

test('red-herring suspect paths reveal real story information', () => {
  const ids = new Set(cfg.followups.map(x => x.id));
  assert.ok(ids.has('mara_records'));
  assert.ok(ids.has('letters'));
  assert.match(cfg.followups.find(x => x.id === 'mara_records').text, /video call/i);
  assert.match(cfg.followups.find(x => x.id === 'letters').text, /letters are real/i);
});

test('saved Leverage creates a bounded investigation option instead of free evidence', () => {
  const privateFollowup = cfg.followups.find(x => x.id === 'julian_private');
  assert.ok(privateFollowup);
  assert.match(privateFollowup.label, /saved pressure/i);
  assert.ok(!cfg.rival.priorities.includes('julian_private'));
});
