// Design token composition per docs/specs/0069-nightcap-visual-design-system.md.
// Components reference semantic tokens only (var(--ink-primary), never #hex).
// Raw color literals live in this directory and nowhere else.

import { BASE_TOKENS_CSS } from "./tokens.base.js";
import { MIDNIGHT_THEME_CSS } from "./themes/midnight.js";

export type SurfaceMode = "display" | "phone";

export function renderDesignTokenCss(): string {
  return `${MIDNIGHT_THEME_CSS}\n${BASE_TOKENS_CSS}`;
}

export function surfaceBodyClass(surface?: SurfaceMode): string {
  if (surface === "display") {
    return "surface-display";
  }
  if (surface === "phone") {
    return "surface-phone";
  }
  return "";
}
