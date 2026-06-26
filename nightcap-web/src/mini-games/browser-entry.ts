// Browser entry point. Loaded by the page via <script type="module">.
// Discovers stage elements, reads their data attributes, and boots a stage
// controller per element. Renderers are registered statically by the bundler
// (see scripts/discover-mini-games.mjs and registry-bindings.ts).

import { defaultRegistry } from "./registry.js";
import { bootMiniGameStage } from "./client.js";
import "./registry-bindings.js";
import type { Surface, MiniGameDefinition } from "../mini-game-kit/index.js";

const STAGE_SELECTOR = "[data-mini-game-stage]";

interface StageDataset {
  surface: Surface;
  sessionId: string;
  participantId: string;
  characterId: string;
  token: string;
  baseUrl: string;
}

function readDataset(stage: HTMLElement): StageDataset | null {
  const surface = stage.dataset.surface as Surface | undefined;
  if (
    surface !== "phone" &&
    surface !== "shared_display" &&
    surface !== "host"
  ) {
    return null;
  }
  const sessionId = stage.dataset.sessionId ?? "";
  const participantId = stage.dataset.participantId ?? "";
  const characterId = stage.dataset.characterId ?? "";
  const token = stage.dataset.token ?? "";
  const baseUrl = stage.dataset.baseUrl ?? "";
  if (!sessionId || !token || !baseUrl) return null;
  return { surface, sessionId, participantId, characterId, token, baseUrl };
}

async function loadDefinition(
  gameId: string,
  version: string,
): Promise<MiniGameDefinition> {
  const url = `/static/mini-games/definitions/${encodeURIComponent(gameId)}/${encodeURIComponent(version)}.json`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(
      `failed to load mini-game definition ${gameId}@${version}: ${res.status}`,
    );
  }
  return (await res.json()) as MiniGameDefinition;
}

export async function bootAllStages(doc: Document = document): Promise<void> {
  const stages = doc.querySelectorAll<HTMLElement>(STAGE_SELECTOR);
  await Promise.all(
    Array.from(stages).map(async (stage) => {
      const dataset = readDataset(stage);
      if (!dataset) {
        stage.setAttribute("data-mini-game-state", "invalid-config");
        return;
      }
      try {
        await bootMiniGameStage(stage, {
          registry: defaultRegistry,
          baseUrl: dataset.baseUrl,
          sessionId: dataset.sessionId,
          token: dataset.token,
          surface: dataset.surface,
          participantId: dataset.participantId,
          characterId: dataset.characterId,
          loadDefinition,
        });
      } catch {
        stage.setAttribute("data-mini-game-state", "boot-error");
      }
    }),
  );
}

export async function bootStage(stage: HTMLElement): Promise<void> {
  const dataset = readDataset(stage);
  if (!dataset) {
    stage.setAttribute("data-mini-game-state", "invalid-config");
    return;
  }
  await bootMiniGameStage(stage, {
    registry: defaultRegistry,
    baseUrl: dataset.baseUrl,
    sessionId: dataset.sessionId,
    token: dataset.token,
    surface: dataset.surface,
    participantId: dataset.participantId,
    characterId: dataset.characterId,
    loadDefinition,
  });
}

declare global {
  interface Window {
    NightcapMiniGames?: {
      bootAllStages: typeof bootAllStages;
      bootStage: typeof bootStage;
    };
  }
}

if (typeof window !== "undefined") {
  window.NightcapMiniGames = { bootAllStages, bootStage };
}

if (typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      void bootAllStages(document);
    });
  } else {
    void bootAllStages(document);
  }
}
