// Base (structural) design tokens per docs/specs/0069-nightcap-visual-design-system.md.
// Structure never changes per theme: spacing, radius, type scale, motion, fonts.
// Theme skins may override semantic color tokens only (see themes/).

export const BASE_TOKENS_CSS = `
:root {
  /* Typefaces. The display face is the narrator's voice; the UI face is chrome.
     Fraunces ships as a self-hosted woff2 when the font asset lands; the serif
     stack below is the interim fallback. */
  --font-ui: Inter, "Segoe UI", system-ui, sans-serif;
  --font-display: "Fraunces", Georgia, "Times New Roman", serif;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 18px;
  --space-5: 28px;

  /* Radius */
  --radius-card: 18px;
  --radius-control: 12px;
  --radius-pill: 999px;

  /* Motion. --t-dramatic is reserved for the five named story sequences
     (seq-join, seq-beat-turn, seq-body, seq-spotlight, seq-truth; Stage B).
     Chrome uses --t-instant and --t-quick only. */
  --t-instant: 80ms linear;
  --t-quick: 180ms ease-out;
  --t-scene: 420ms cubic-bezier(0.2, 0, 0.1, 1);
  --t-dramatic: 900ms cubic-bezier(0.6, 0, 0.2, 1);

  /* Neutral type scale; surface modes below retune it. */
  --type-title: clamp(2rem, 4vw, 3.5rem);
  --type-heading: 1.2rem;
  --type-body: 1rem;
  --type-detail: 0.88rem;
}

/* Shared display: read from ~3 meters. 28px floor for supporting text. */
body.surface-display {
  --type-title: clamp(3rem, 6vw, 6rem);
  --type-heading: clamp(1.75rem, 2.6vw, 2.5rem);
  --type-body: clamp(1.375rem, 2vw, 1.875rem);
  --type-detail: clamp(1.25rem, 1.7vw, 1.5rem);
}

/* Phone: the dossier, read at arm's length in a dim room. 17px body floor. */
body.surface-phone {
  --type-title: clamp(1.75rem, 7vw, 2.25rem);
  --type-heading: 1.25rem;
  --type-body: 1.0625rem;
  --type-detail: 0.875rem;
}

@media (prefers-reduced-motion: reduce) {
  * {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
  }
}
`;
