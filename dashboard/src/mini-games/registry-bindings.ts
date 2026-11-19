// Finds every mini-game package's own renderer and definition. A new package
// under nightcap/mini_games/<game-id>/ needs no edit here: its renderer is
// found by path and registered by the game ID it declares.
//
// The dashboard's Vite config maps @arcwright/mini-game-kit to the copy of the
// kit in src/mini-game-kit, which is what package renderers import.

import type {
  MiniGameDefinition,
  MiniGameRenderer,
} from "../mini-game-kit/index.js";
import { defaultRegistry, type RendererRegistry } from "./registry.js";

const rendererModules = import.meta.glob<{ default: MiniGameRenderer }>(
  [
    "../../../nightcap/mini_games/*/client/renderer.ts",
    "!../../../nightcap/mini_games/_template/**",
  ],
  { eager: true },
);

const definitionLoaders = import.meta.glob<MiniGameDefinition>(
  "../../../nightcap/mini_games/*/definitions/*.json",
  { import: "default" },
);

export function registerPackageRenderers(
  registry: RendererRegistry = defaultRegistry,
): RendererRegistry {
  for (const module of Object.values(rendererModules)) {
    const renderer = module.default;
    if (!registry.has(renderer.gameId)) registry.register(renderer);
  }
  return registry;
}

export function loadPackageDefinition(
  gameId: string,
  version: string,
): Promise<MiniGameDefinition> {
  const key = `../../../nightcap/mini_games/${gameId}/definitions/${version}.json`;
  const load = definitionLoaders[key];
  if (!load) {
    return Promise.reject(
      new Error(`no definition for mini-game ${gameId}@${version}`),
    );
  }
  return load();
}
