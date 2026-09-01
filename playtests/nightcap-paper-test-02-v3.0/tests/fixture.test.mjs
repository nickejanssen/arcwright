import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const caseData = JSON.parse(fs.readFileSync(path.join(here, "..", "case.json"), "utf8"));

test("fixture identity and founder-approved core stay locked", () => {
  assert.equal(caseData.fixture_id, "nightcap-paper-test-02-v3.0");
  assert.equal(caseData.fixture_version, "3.0");
  assert.equal(caseData.non_canon, true);
  assert.equal(caseData.culprit_id, "clara-hensley");
  assert.equal(caseData.suspects.length, 4);
  assert.equal(caseData.essential_truths.length, 4);
  assert.ok(caseData.investigation.opening_opportunities.length >= 4);
  assert.equal(caseData.competition.game_id, "the-locked-box");
  assert.equal(caseData.leverage.starting_amount, 1);
  assert.equal(caseData.leverage.source_claim, "test-granted; production sourcing not validated");
});

test("each essential truth has redundant routes and no route requires the lock", () => {
  for (const truth of caseData.essential_truths) {
    assert.ok(truth.routes.length >= 2, `${truth.id} needs redundant routes`);
    for (const route of truth.routes) {
      assert.ok(!route.includes("lock-win"), `${truth.id} may not require lock-win`);
    }
  }
  assert.equal(caseData.fallbacks.essential_truth_requires_lock_win, false);
  assert.equal(caseData.fallbacks.lock_failure_releases_cylinder_publicly, true);
  assert.equal(caseData.fallbacks.lock_timeout_releases_cylinder_publicly, true);
  assert.equal(caseData.fallbacks.lock_abort_releases_cylinder_publicly, true);
});

test("final cast uses approved corrected names", () => {
  const names = caseData.suspects.map((suspect) => suspect.name);
  assert.deepEqual(names, ["Clara Hensley", "Lenora Quill", "Edwin Rusk", "Beatrice Ashcombe"]);
});

test("locked box is a research abstraction, not a production capability claim", () => {
  assert.match(caseData.competition.research_abstraction, /does not validate production simultaneous-picking support/i);
  assert.equal(caseData.competition.pins.length, 4);
  assert.ok(caseData.competition.rival_finish_seconds < caseData.competition.duration_seconds);
});

test("case file requires causal evidence, not culprit-only guessing", () => {
  assert.equal(caseData.case_file.required_truths.length, 4);
  assert.match(caseData.case_file.instructions, /four or five facts/i);
  for (const truthId of caseData.case_file.required_truths) {
    assert.ok(caseData.case_file.proof_groups[truthId]?.length >= 2);
  }
});


test("all referenced evidence IDs exist in the authored case", () => {
  const evidence = new Set([
    ...Object.values(caseData.investigation.routes).flatMap((route) => route.discoveries ?? []).map((item) => item.id),
    ...Object.values(caseData.interviews).flatMap((interview) => [
      ...(interview.discoveries ?? []),
      ...(interview.conditional?.discoveries ?? []),
      ...(interview.follow_thread?.discovery ? [interview.follow_thread.discovery] : [])
    ]).map((item) => item.id),
    caseData.competition.winner_private_observation.id
  ]);
  for (const truth of caseData.essential_truths) {
    for (const route of truth.routes) {
      for (const id of route) assert.ok(evidence.has(id), `${truth.id} references unknown ${id}`);
    }
  }
  for (const groups of Object.values(caseData.case_file.proof_groups)) {
    for (const group of groups) for (const id of group) assert.ok(evidence.has(id), `case file references unknown ${id}`);
  }
});

test("false chronology has witness redundancy beyond Beatrice", () => {
  const truth = caseData.essential_truths.find((item) => item.id === "t2-before-voice");
  assert.ok(truth.routes.some((route) => route.includes("e-beatrice-sighting") || route.includes("e-beatrice-impact")));
  assert.ok(truth.routes.some((route) => route.includes("e-rusk-sighting")));
});

test("fixture does not reuse Last Toast cast or player-facing system-mode jargon", () => {
  const source = [
    fs.readFileSync(path.join(here, "..", "app.js"), "utf8"),
    fs.readFileSync(path.join(here, "..", "index.html"), "utf8"),
    JSON.stringify(caseData)
  ].join("\n");
  for (const oldName of ["Rhea Pike", "Sebastian Vale", "Mara Voss", "Theo Bell", "Celeste Vale", "Julian Cross"]) {
    assert.ok(!source.includes(oldName), `old fixture name leaked: ${oldName}`);
  }
  const visible = fs.readFileSync(path.join(here, "..", "app.js"), "utf8");
  for (const jargon of [">HUNT<", ">THINK<", ">PLAY<", "Case Strength"]) assert.ok(!visible.includes(jargon));
});

test("player-facing files contain no em dash characters", () => {
  for (const filename of ["index.html", "app.js"]) {
    const source = fs.readFileSync(path.join(here, "..", filename), "utf8");
    assert.ok(!source.includes("—"), `${filename} contains an em dash`);
  }
});
