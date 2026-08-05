#!/usr/bin/env node
import { createServer } from "node:http";
import { createHash } from "node:crypto";
import { hostname, networkInterfaces } from "node:os";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, isAbsolute, resolve, relative } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { build as esbuild } from "esbuild";
import { Window as HappyWindow } from "happy-dom";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const REPO_ROOT = resolve(__dirname, "..", "..");
const DEFAULT_OUT = resolve(REPO_ROOT, "nightcap-web", ".mini-game-playtests");
const RENDERER_CACHE = resolve(DEFAULT_OUT, ".renderer-cache");
const MINI_GAMES_ROOT = resolve(REPO_ROOT, "nightcap", "mini_games");
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

async function readJson(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

function requireInside(root, child, label) {
  const rel = relative(root, child);
  if (rel === "" || rel.startsWith("..") || isAbsolute(rel)) {
    throw new Error(`${label} must stay under ${root}`);
  }
  return child;
}

function requireSlug(value, label) {
  if (typeof value !== "string" || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value)) {
    throw new Error(`${label} must be a lowercase slug`);
  }
  return value;
}

function requireVersion(value, label) {
  if (
    typeof value !== "string" ||
    !/^[0-9]+[.][0-9]+[.][0-9]+(?:[-+][A-Za-z0-9.-]+)?$/.test(value)
  ) {
    throw new Error(`${label} must be an exact version`);
  }
  return value;
}

async function loadArtifacts(args) {
  const adaptationPath = requireInside(
    MINI_GAMES_ROOT,
    resolve(REPO_ROOT, args.adaptation),
    "adaptation path",
  );
  const adaptation = await readJson(adaptationPath);
  if (adaptation.authority_profile !== "arcwright.authority.preview-only.v1") {
    throw new Error("playtest requires preview-only authority");
  }
  const packageRef = adaptation.package ?? {};
  if (!packageRef.game_id || !packageRef.version) {
    throw new Error(
      "adaptation must reference an exact package game_id and version",
    );
  }
  const gameId = requireSlug(packageRef.game_id, "package game_id");
  const version = requireVersion(packageRef.version, "package version");
  const packageDir = requireInside(
    MINI_GAMES_ROOT,
    resolve(MINI_GAMES_ROOT, gameId),
    "package directory",
  );
  const manifest = await readJson(resolve(packageDir, "manifest.json"));
  if (manifest.game_id !== gameId) {
    throw new Error("manifest game_id does not match adaptation package ref");
  }
  if (manifest.current_version !== version) {
    throw new Error(
      "manifest current_version does not match adaptation package ref",
    );
  }
  const definition = await readJson(
    requireInside(
      packageDir,
      resolve(packageDir, manifest.definition_path),
      "definition path",
    ),
  );
  if (definition.version !== version) {
    throw new Error("definition version does not match adaptation package ref");
  }
  const rendererPath = requireInside(
    packageDir,
    resolve(packageDir, "client", "renderer.ts"),
    "renderer path",
  );
  const rendererSource = await readFile(rendererPath, "utf8");
  const rendererHash = createHash("sha256")
    .update(rendererSource)
    .digest("hex")
    .slice(0, 12);
  await mkdir(RENDERER_CACHE, { recursive: true });
  const bundlePath = resolve(
    RENDERER_CACHE,
    `${gameId}-${version}-${rendererHash}.mjs`,
  );
  try {
    await readFile(bundlePath, "utf8");
  } catch {
    await esbuild({
      entryPoints: [rendererPath],
      outfile: bundlePath,
      bundle: true,
      format: "esm",
      target: ["es2022"],
      platform: "browser",
      alias: {
        "@arcwright/mini-game-kit": resolve(
          REPO_ROOT,
          "nightcap-web",
          "src",
          "mini-game-kit",
          "index.ts",
        ),
      },
      logLevel: "silent",
    });
  }
  const mod = await import(`${pathToFileURL(bundlePath).href}?t=${Date.now()}`);
  return {
    adaptation,
    adaptationPath,
    bundlePath,
    definition,
    manifest,
    renderer: mod.default,
  };
}

function assertTextAbsent(root, pattern, label) {
  if (pattern.test(root.textContent ?? "")) {
    throw new Error(label);
  }
}

async function driveSurface(surface, artifacts, args) {
  const window = new HappyWindow();
  const doc = window.document;
  const root = doc.createElement("section");
  const submissions = [];
  const state = {
    runId: `${args.session}-${surface}`,
    gameId: artifacts.manifest.game_id,
    definitionVersion: artifacts.definition.version,
    status: "active",
    deadlineAt: null,
    runtimeState: {},
    presentation: {
      title: "Tell Me Something True",
      prompt: "I once hid the ledger under ____.",
    },
    mySubmissions: [],
  };
  const ctx = {
    surface,
    sessionId: args.session,
    participantId: "sim-player-1",
    characterId: "sim-character-1",
    state,
    definition: artifacts.definition,
    submit: async (payload) => {
      submissions.push(payload);
      return { submissionId: `sub-${submissions.length}`, isAccepted: true };
    },
    onEvent: () => () => {},
    reportPerf: () => {},
  };
  const lifecycle = artifacts.renderer.mount(root, ctx);
  if (root.getAttribute("data-authority") !== PREVIEW) {
    throw new Error(`${surface} did not render preview authority`);
  }
  if (surface === "phone") {
    lifecycle.handleEvent({
      event_type: "tmst_private_prompt_ready",
      payload: { phase: "input" },
    });
    const input = root.querySelector('[data-role="statement-input"]');
    if (!input) throw new Error("phone surface did not render statement input");
    input.value = "the old piano";
    root.querySelector('[data-role="truth-action"]')?.click();
    await new Promise((resolveDone) => setTimeout(resolveDone, 0));
    lifecycle.handleEvent({
      event_type: "tmst_spotlight_started",
      payload: {
        target_character_id: "sim-character-2",
        spotlight_label: "Vesper",
        other_player_vote: "must stay hidden",
      },
    });
    root.querySelector('[data-role="vote-lie"]')?.click();
    await new Promise((resolveDone) => setTimeout(resolveDone, 0));
    if (
      !submissions.some(
        (item) =>
          item.action === "input" &&
          item.statement_text === "the old piano" &&
          item.declared_truth === true,
      )
    ) {
      throw new Error("phone surface did not submit TMST input payload");
    }
    if (
      !submissions.some(
        (item) =>
          item.action === "vote" &&
          item.target_character_id === "sim-character-2" &&
          item.vote === "lie",
      )
    ) {
      throw new Error("phone surface did not submit TMST vote payload");
    }
    assertTextAbsent(
      root,
      /must stay hidden/,
      "phone leaked another player's vote",
    );
  }
  if (surface === "shared_display") {
    lifecycle.handleEvent({
      event_type: "tmst_private_prompt_ready",
      payload: { prompt: "private text must not appear" },
    });
    assertTextAbsent(
      root,
      /private text/i,
      "shared display leaked private prompt",
    );
    lifecycle.handleEvent({
      event_type: "tmst_spotlight_started",
      payload: { target_character_id: "sim-character-2" },
    });
    lifecycle.handleEvent({
      event_type: "tmst_reveal_resolved",
      payload: { statement_text: "public reveal" },
    });
  }
  lifecycle.update({
    ...state,
    status: args.scenario === "timeout" ? "timed_out" : "completed",
  });
  lifecycle.unmount();
  return {
    surface,
    mounted: true,
    submissions: submissions.length,
  };
}

async function proveArtifacts(args) {
  const artifacts = await loadArtifacts(args);
  const surface_checks = [];
  for (const surface of args.surfaces) {
    surface_checks.push(await driveSurface(surface, artifacts, args));
  }
  return {
    adaptation_id: artifacts.adaptation.adaptation_id,
    adaptation_version: artifacts.adaptation.adaptation_version,
    authority_profile: artifacts.adaptation.authority_profile,
    package_id: artifacts.manifest.game_id,
    package_version: artifacts.definition.version,
    renderer_bundle: relative(REPO_ROOT, artifacts.bundlePath).replace(
      /\\/g,
      "/",
    ),
    surface_checks,
  };
}

function buildReplay(args, port, proof) {
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
    adaptation_id: proof.adaptation_id,
    adaptation_version: proof.adaptation_version,
    package_id: proof.package_id,
    package_version: proof.package_version,
    authority: PREVIEW,
    authority_profile: proof.authority_profile,
    local_url: localUrl,
    lan_url: lanUrl(port, path),
    host_name: hostname(),
    players,
    surfaces: args.surfaces,
    states,
    events,
    surface_checks: proof.surface_checks,
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
    surface_checks: replay.surface_checks,
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
  const dir = resolve(
    args.out,
    args.session,
    args.scenario,
    String(args.players),
  );
  await mkdir(dir, { recursive: true });
  const proof = await proveArtifacts(args);
  const replay = buildReplay(args, port, proof);
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
