import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import test from "node:test";

function runPlaytest(args: string[]): Record<string, unknown> {
  const output = execFileSync(
    "node",
    ["scripts/playtest-mini-game.mjs", ...args, "--json"],
    {
      cwd: resolve("."),
      encoding: "utf8",
    },
  );
  return JSON.parse(output) as Record<string, unknown>;
}

function tempOut(): string {
  return mkdtempSync(join(tmpdir(), "arcwright-minigame-playtest-"));
}

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
    const evidenceFile = resolve("..", String(result.evidence_file));
    const replayFile = resolve("..", String(result.replay_file));

    assert.equal(result.players, players);
    assert.equal(result.state_label, "Playtest-ready");
    assert.equal(existsSync(evidenceFile), true);
    assert.equal(existsSync(replayFile), true);
    const replay = JSON.parse(readFileSync(replayFile, "utf8")) as {
      players: string[];
      preview_banner: string;
    };
    assert.equal(replay.players.length, players);
    assert.equal(replay.preview_banner, "NON_AUTHORITATIVE_PREVIEW");
  });
}
