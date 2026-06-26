// Renderer registry. Maps gameId → MiniGameRenderer.
// Populated at build time from manifest scan (see scripts/discover-mini-games.mjs)
// and at runtime via registerRenderer for tests.

import type { MiniGameRenderer } from "../mini-game-kit/index.js";

export class RendererRegistry {
  private readonly _map = new Map<string, MiniGameRenderer>();

  register(renderer: MiniGameRenderer): void {
    if (this._map.has(renderer.gameId)) {
      throw new Error(
        `Renderer already registered for game: ${renderer.gameId}`,
      );
    }
    this._map.set(renderer.gameId, renderer);
  }

  get(gameId: string): MiniGameRenderer {
    const renderer = this._map.get(gameId);
    if (!renderer) {
      throw new Error(`No renderer registered for game: ${gameId}`);
    }
    return renderer;
  }

  has(gameId: string): boolean {
    return this._map.has(gameId);
  }

  list(): string[] {
    return [...this._map.keys()];
  }

  clear(): void {
    this._map.clear();
  }
}

export const defaultRegistry = new RendererRegistry();
