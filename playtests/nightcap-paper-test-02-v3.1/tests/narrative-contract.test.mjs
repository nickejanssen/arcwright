import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const fixture = path.resolve(here, "..");
const caseData = JSON.parse(
  fs.readFileSync(path.join(fixture, "case.json"), "utf8"),
);
const app = fs.readFileSync(path.join(fixture, "app.js"), "utf8");

test("editorial pass preserves case identity, cast and fixed chronology", () => {
  assert.equal(caseData.culprit_id, "clara-hensley");
  assert.deepEqual(
    caseData.suspects.map(({ id }) => id),
    ["clara-hensley", "lenora-quill", "edwin-rusk", "beatrice-ashcombe"],
  );
  assert.deepEqual(
    caseData.canonical_timeline.map(({ time }) => time),
    [
      "11:18 PM",
      "11:23 PM",
      "11:30 PM",
      "11:33 PM",
      "11:35 PM",
      "11:40 PM",
      "11:47 PM",
      "11:50 PM",
      "11:53 PM",
      "Midnight",
    ],
  );
});

test("each granted fact is attributable to its earned encounter", () => {
  const anchors = {
    "e-bookend": /bookend.*(dust|moved)/i,
    "e-gideon-final-note": /After Quill, Hensley/i,
    "e-cylinder-index": /42 to 44/i,
    "e-cylinder-transcript": /Mrs\. Quill, do carry on/i,
    "e-clara-access": /transcription initials/i,
    "e-service-route": /coupling.*service wall/i,
    "e-quill-cue-sheet": /cue sheet.*Ashcombe voice/i,
    "e-clara-lie": /last saw Gideon.*eleven twenty/i,
    "e-clara-transcribed-43": /transcribed cylinder 43/i,
    "e-clara-evasion": /Quill obtained material.*private files/i,
    "e-quill-denial": /never receive information/i,
    "e-quill-admission": /tube, a cabinet/i,
    "e-quill-payment": /receipt.*cash payments/i,
    "e-rusk-denial": /did not touch the séance apparatus/i,
    "e-rusk-found-cylinder": /found one of his cylinders/i,
    "e-rusk-sighting": /saw Clara come out/i,
    "e-clara-quill-connection": /Clara.*service corridor/i,
    "e-beatrice-threat": /threatened him twice/i,
    "e-beatrice-letters": /giving Quill letters and objects/i,
    "e-beatrice-impact": /heard Gideon say.*heavy impact/i,
    "e-beatrice-sighting": /saw Clara leave/i,
    "e-clara-visible-seance": /seated with.*voice came through/i,
    "e-private-detail-match": /sealed family account.*private research notes/i,
    "e-cylinder-43": /Cylinder 43 contains Gideon speaking/i,
  };
  const encounters = [
    ...Object.entries(caseData.investigation.routes).map(([id, route]) => [
      id,
      route.scene,
      route.discoveries,
    ]),
    ...Object.entries(caseData.interviews).flatMap(([id, interview]) => [
      [id, `${interview.opening} ${interview.claim}`, interview.discoveries],
      ...(interview.conditional
        ? [
            [
              `${id}:challenge`,
              interview.conditional.scene,
              interview.conditional.discoveries,
            ],
          ]
        : []),
      ...(interview.follow_thread
        ? [
            [
              `${id}:follow`,
              interview.follow_thread.scene,
              [interview.follow_thread.discovery],
            ],
          ]
        : []),
    ]),
    [
      "locked-box:public",
      caseData.competition.fallback_public_observation.fact,
      [caseData.competition.fallback_public_observation],
    ],
    [
      "locked-box:private",
      caseData.competition.winner_private_observation.fact,
      [caseData.competition.winner_private_observation],
    ],
  ];
  for (const [id, scene, discoveries] of encounters) {
    assert.ok(scene && scene.trim(), `${id} has visible content`);
    for (const discovery of discoveries) {
      assert.ok(
        discovery.source && discovery.fact,
        `${id}/${discovery.id} has a declared source`,
      );
      assert.ok(
        anchors[discovery.id],
        `${discovery.id} needs a contract anchor`,
      );
      assert.match(
        scene,
        anchors[discovery.id],
        `${id}/${discovery.id} must appear in its scene`,
      );
    }
  }
});

test("contextual challenge prompts ask without supplying the conclusion", () => {
  for (const [id, interview] of Object.entries(caseData.interviews)) {
    if (!interview.conditional) continue;
    assert.ok(interview.conditional.prompt, `${id} needs a specific prompt`);
    assert.doesNotMatch(
      interview.conditional.prompt,
      /killer|murderer|therefore|proves|must have/i,
    );
  }
  assert.match(app, /interview\.conditional\.prompt/);
});

test("Beatrice challenge uses her stated claim, not unearned whereabouts", () => {
  const interview = caseData.interviews["beatrice-ashcombe"];
  assert.match(interview.claim, /saw nothing useful near his room/i);
  assert.match(
    interview.conditional.prompt,
    /what she meant by seeing nothing useful near Gideon's room/i,
  );
  assert.doesNotMatch(interview.conditional.prompt, /her time near/i);
});

test("opening gives the approved invitation without premature evidence", () => {
  const opening = app.slice(
    app.indexOf("function renderOpening()"),
    app.indexOf("function rivalBeatAfterAction()"),
  );
  assert.match(opening, /Gideon March invited you/);
  assert.match(opening, /invited Nora Vance too/);
  assert.doesNotMatch(opening, /cylinder 43|Clara killed|private research/i);
  for (const suspect of caseData.suspects) {
    assert.doesNotMatch(
      suspect.public_hook,
      /killed|cylinder 43|strongbox|leaked/i,
    );
  }
});

test("private notes never qualify as case proof", () => {
  const proofIds = Object.values(caseData.case_file.proof_groups).flat(2);
  const earnedIds = new Set([
    ...Object.values(caseData.investigation.routes).flatMap((route) =>
      route.discoveries.map(({ id }) => id),
    ),
    ...Object.values(caseData.interviews).flatMap((interview) => [
      ...interview.discoveries.map(({ id }) => id),
      ...(interview.conditional?.discoveries ?? []).map(({ id }) => id),
      ...(interview.follow_thread
        ? [interview.follow_thread.discovery.id]
        : []),
    ]),
    caseData.competition.fallback_public_observation.id,
  ]);
  assert.ok(proofIds.length > 0);
  assert.ok(proofIds.every((id) => earnedIds.has(id)));
});

test("new narration avoids em dashes and implementation jargon in the ending", () => {
  for (const file of ["case.json", "app.js"]) {
    assert.doesNotMatch(fs.readFileSync(path.join(fixture, file), "utf8"), /—/);
  }
  const ending = app.slice(
    app.indexOf("function renderReveal()"),
    app.indexOf("function render()"),
  );
  assert.doesNotMatch(ending, /fixture|model judged|solution graph/i);
});
