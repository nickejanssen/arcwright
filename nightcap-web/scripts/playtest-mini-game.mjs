#!/usr/bin/env node
import { createServer } from "node:http";
import { hostname, networkInterfaces } from "node:os";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve, relative } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = resolve(__dirname, "..", "..");
const DEFAULT_OUT = resolve(REPO_ROOT, "nightcap-web", ".mini-game-playtests");
const PREVIEW = "NON_AUTHORITATIVE_PREVIEW";
const DEFAULT_ADAPTATION =
  "nightcap/mini_games/tell-me-something-true/adaptations/nightcap-couch-race-v1/0.1.0.json";
const SCENARIOS = new Set([
  "active",
  "completed",
  "timeout",
  "cancel",
  "pause",
  "reconnect",
  "fallback",
  "reset",
  "happy-path",
]);

function usage() {
  return [
    "usage: playtest-mini-game.mjs --session SESSION [--scenario NAME] [--players N]",
    "       [--surfaces phone,shared_display,host] [--out DIR] [--json]",
    "       [--serve-ms MS]",
  ].join("\n");
}

function parseArgs(argv) {
  const args = {
    scenario: "happy-path",
    players: 4,
    surfaces: ["phone", "shared_display", "host"],
    out: DEFAULT_OUT,
    adaptation: DEFAULT_ADAPTATION,
    json: false,
    serveMs: 0,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    const next = () => {
      const value = argv[i + 1];
      if (!value) throw new Error(`missing value for ${arg}`);
      i += 1;
      return value;
    };
    if (arg === "--session") args.session = next();
    else if (arg === "--scenario") args.scenario = next();
    else if (arg === "--players") args.players = Number(next());
    else if (arg === "--surfaces") args.surfaces = next().split(",");
    else if (arg === "--out") args.out = resolve(next());
    else if (arg === "--adaptation") args.adaptation = next();
    else if (arg === "--json") args.json = true;
    else if (arg === "--serve-ms") args.serveMs = Number(next());
    else if (arg === "--help" || arg === "-h") {
      console.log(usage());
      process.exit(0);
    } else {
      throw new Error(`unknown argument: ${arg}`);
    }
  }
  if (!args.session) throw new Error("--session is required");
  if (!SCENARIOS.has(args.scenario)) {
    throw new Error(`unsupported scenario: ${args.scenario}`);
  }
  if (!Number.isInteger(args.players) || args.players < 2 || args.players > 8) {
    throw new Error("--players must be an integer from 2 to 8");
  }
  for (const surface of args.surfaces) {
    if (!["phone", "shared_display", "host"].includes(surface)) {
      throw new Error(`unsupported surface: ${surface}`);
    }
  }
  if (!Number.isInteger(args.serveMs) || args.serveMs < 0) {
    throw new Error("--serve-ms must be a non-negative integer");
  }
  return args;
}

function statesForScenario(scenario) {
  switch (scenario) {
    case "active":
      return ["active"];
    case "completed":
      return ["active", "completed"];
    case "timeout":
      return ["active", "timed_out"];
    case "cancel":
      return ["active", "cancelled"];
    case "pause":
      return ["active", "paused", "active"];
    case "reconnect":
      return ["active", "paused", "active", "completed"];
    case "fallback":
      return ["active", "timed_out", "fallback"];
    case "reset":
      return ["active", "cancelled", "reset", "active"];
    case "happy-path":
      return ["active", "completed"];
    default:
      return ["active"];
  }
}

function playerIds(players) {
  return Array.from({ length: players }, (_, i) => `sim-player-${i + 1}`);
}

function lanUrl(port, path) {
  const nets = networkInterfaces();
  for (const infos of Object.values(nets)) {
    for (const info of infos ?? []) {
      if (info.family === "IPv4" && !info.internal) {
        return `http://${info.address}:${port}${path}`;
      }
    }
  }
  return null;
}

function buildReplay(args, port) {
  const path = `/playtest/${encodeURIComponent(args.session)}`;
  const localUrl = `http://127.0.0.1:${port}${path}`;
  const players = playerIds(args.players);
  const states = statesForScenario(args.scenario);
  const events = states.map((state, index) => ({
    sequence: index + 1,
    type: state === "fallback" ? "mini_game_fallback" : "mini_game_state",
    state,
    authority: PREVIEW,
  }));
  return {
    schema_version: "1.0",
    session_id: args.session,
    scenario: args.scenario,
    adaptation_ref: args.adaptation,
    authority: PREVIEW,
    local_url: localUrl,
    lan_url: lanUrl(port, path),
    host_name: hostname(),
    players,
    surfaces: args.surfaces,
    states,
    events,
    production_consequence_applied: false,
    preview_banner: PREVIEW,
  };
}

function buildEvidence(replay, replayFile) {
  const completed = replay.states.includes("completed");
  const fallback = replay.states.includes("fallback");
  return {
    schema_version: "1.0",
    evidence_id: `${replay.session_id}-${replay.scenario}`,
    readiness_state: completed || fallback ? "playtest_ready" : "reusable",
    state_label: completed || fallback ? "Playtest-ready" : "Reusable",
    authority: PREVIEW,
    summary:
      "Local deterministic preview evidence recorded without cloud credentials, model calls, database writes, or production consequences.",
    replay_file: replayFile,
    local_url: replay.local_url,
    lan_url: replay.lan_url,
    surfaces: replay.surfaces,
    players: replay.players.length,
    scenario: replay.scenario,
    production_consequence_applied: false,
    blockers:
      completed || fallback
        ? ["Production authority remains blocked by preview-only evidence."]
        : ["Scenario did not reach a completed or fallback state."],
  };
}

async function maybeServe(replay, serveMs) {
  if (serveMs === 0) return;
  const page = `<!doctype html><meta charset="utf-8"><title>Mini-game playtest</title><main data-authority="${PREVIEW}"><h1>${PREVIEW}</h1><pre>${JSON.stringify(
    replay,
    null,
    2,
  )}</pre></main>`;
  const server = createServer((_, res) => {
    res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
    res.end(page);
  });
  await new Promise((resolveReady) =>
    server.listen(8787, "127.0.0.1", resolveReady),
  );
  await new Promise((resolveDone) => setTimeout(resolveDone, serveMs));
  await new Promise((resolveDone) => server.close(resolveDone));
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const port = 8787;
  const replay = buildReplay(args, port);
  const dir = resolve(
    args.out,
    args.session,
    args.scenario,
    String(args.players),
  );
  await mkdir(dir, { recursive: true });
  const replayPath = resolve(dir, "replay.json");
  const evidencePath = resolve(dir, "evidence.json");
  const replayRef = relative(REPO_ROOT, replayPath).replace(/\\/g, "/");
  await writeFile(replayPath, JSON.stringify(replay, null, 2) + "\n", "utf8");
  const evidence = buildEvidence(replay, replayRef);
  await writeFile(
    evidencePath,
    JSON.stringify(evidence, null, 2) + "\n",
    "utf8",
  );
  await maybeServe(replay, args.serveMs);
  const output = {
    ...evidence,
    replay_file: replayRef,
    evidence_file: relative(REPO_ROOT, evidencePath).replace(/\\/g, "/"),
  };
  if (args.json) {
    console.log(JSON.stringify(output, null, 2));
    return;
  }
  console.log(`${output.state_label}: ${output.summary}`);
  console.log(`Authority: ${output.authority}`);
  console.log(`Local URL: ${output.local_url}`);
  if (output.lan_url) console.log(`LAN URL: ${output.lan_url}`);
  console.log(`Replay: ${output.replay_file}`);
  console.log(`Evidence: ${output.evidence_file}`);
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : String(err));
  process.exit(1);
});
