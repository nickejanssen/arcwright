// Typed factory that turns a surface-keyed spec into a MiniGameRenderer.
// Renderers do not have to implement every surface; missing surfaces mount
// an inert placeholder so the page does not break.

import type {
  DefineRendererSpec,
  MiniGameContext,
  MiniGameRenderer,
  SurfaceHandler,
  SurfaceLifecycle,
} from "./types.js";

function inertLifecycle(): SurfaceLifecycle {
  return {
    update: () => {},
    handleEvent: () => {},
    unmount: () => {},
  };
}

function pickHandler(
  spec: DefineRendererSpec,
  ctx: MiniGameContext,
): SurfaceHandler | undefined {
  switch (ctx.surface) {
    case "phone":
      return spec.phone;
    case "shared_display":
      return spec.sharedDisplay;
    case "host":
      return spec.host;
  }
}

export function defineRenderer(spec: DefineRendererSpec): MiniGameRenderer {
  return {
    gameId: spec.gameId,
    mount(root, ctx) {
      const handler = pickHandler(spec, ctx);
      if (!handler) {
        return inertLifecycle();
      }
      return handler.mount(root, ctx);
    },
  };
}
