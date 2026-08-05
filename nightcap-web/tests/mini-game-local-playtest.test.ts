import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import {
  existsSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import test from "node:test";

const nightcapWebRoot = [
  resolve("."),
  resolve("nightcap-web"),
  resolve("..", "nightcap-web"),
].find((candidate) =>
  existsSync(resolve(candidate, "scripts", "playtest-mini-game.mjs")),
);

if (!nightcapWebRoot) {
  throw new Error("Could not locate nightcap-web playtest script");
}

const NIGHTCAP_WEB_ROOT = nightcapWebRoot;
const REPO_ROOT = resolve(NIGHTCAP_WEB_ROOT, "..");

function runPlaytest(args: string[]): Record<string, unknown> {
  const output = execFileSync(
    "node",
    ["scripts/playtest-mini-game.mjs", ...args, "--json"],
    {
      cwd: NIGHTCAP_WEB_ROOT,
      encoding: "utf8",
    },
  );
  return JSON.parse(output) as Record<string, unknown>;
}

function tempOut(): string {
  return mkdtempSync(join(tmpdir(), "arcwright-minigame-playtest-"));
}

function assertPlaytestFails(args: string[], pattern: RegExp): void {
  assert.throws(
    () => runPlaytest(args),
    (err) => {
      const stderr = (err as { stderr?: { toString?: () => string } | string })
        .stderr;
      const message =
        err instanceof Error
          ? `${err.message}\n${
              typeof stderr === "string" ? stderr : (stderr?.toString?.() ?? "")
            }`
          : String(err);
      assert.match(message, pattern);
      return true;
    },
  );
}

test("local playtest: rejects adaptation paths outside mini-game catalog", () => {
  const outside = join(tempOut(), "adaptation.json");
  writeFileSync(
    outside,
    JSON.stringify({
      authority_profile: "arcwright.authority.preview-only.v1",
      package: {
        game_id: "tell-me-something-true",
        version: "0.1.0",
      },
    }),
  );

  assertPlaytestFails(
    [
      "--session",
      "session-outside-adaptation",
      "--adaptation",
      outside,
      "--out",
      tempOut(),
    ],
    /adaptation path must stay under/,
  );
});

test("local playtest: rejects unsafe package ids before resolving paths", () => {
  const fixtureDir = mkdtempSync(
    join(REPO_ROOT, "nightcap", "mini_games", ".playtest-validation-"),
  );
  const adaptation = join(fixtureDir, "unsafe-package.json");
  try {
    writeFileSync(
      adaptation,
      JSON.stringify({
        authority_profile: "arcwright.authority.preview-only.v1",
        package: {
          game_id: "../outside",
          version: "0.1.0",
        },
      }),
    );

    assertPlaytestFails(
      [
        "--session",
        "session-unsafe-package",
        "--adaptation",
        adaptation,
        "--out",
        tempOut(),
      ],
      /package game_id must be a lowercase slug/,
    );
  } finally {
    rmSync(fixtureDir, { recursive: true, force: true });
  }
});

for (const scenario of [
  "active",
  "completed",
  "timeout",
  "cancel",
  "pause",
  "reconnect",
  "fallback",
  "reset",
]) {
  test(`local playtest: records ${scenario} preview evidence`, () => {
    const result = runPlaytest([
      "--session",
      `session-${scenario}`,
      "--scenario",
      scenario,
      "--players",
      "4",
      "--out",
      tempOut(),
    ]);

    assert.equal(result.authority, "NON_AUTHORITATIVE_PREVIEW");
    assert.equal(result.production_consequence_applied, false);
    assert.deepEqual(
      (
        result.surface_checks as Array<{ surface: string; mounted: boolean }>
      ).map((item) => [item.surface, item.mounted]),
      [
        ["phone", true],
        ["shared_display", true],
        ["host", true],
      ],
    );
    assert.match(String(result.local_url), /^http:\/\/127\.0\.0\.1:8787\//);
    assert.ok(String(result.replay_file).endsWith("replay.json"));
    assert.ok(String(result.evidence_file).endsWith("evidence.json"));
  });
}

for (const players of [2, 4, 8]) {
  test(`local playtest: deterministic replay supports ${players} players`, () => {
    const out = tempOut();
    const result = runPlaytest([
      "--session",
      `session-${players}`,
      "--scenario",
      "happy-path",
      "--players",
      String(players),
      "--out",
      out,
    ]);
    const evidenceFile = resolve(REPO_ROOT, String(result.evidence_file));
    const replayFile = resolve(REPO_ROOT, String(result.replay_file));

    assert.equal(result.players, players);
    assert.equal(result.state_label, "Playtest-ready");
    assert.equal(existsSync(evidenceFile), true);
    assert.equal(existsSync(replayFile), true);
    const replay = JSON.parse(readFileSync(replayFile, "utf8")) as {
      players: string[];
      preview_banner: string;
      surface_checks: unknown[];
    };
    assert.equal(replay.players.length, players);
    assert.equal(replay.preview_banner, "NON_AUTHORITATIVE_PREVIEW");
    assert.equal(replay.surface_checks.length, 3);
  });
}
