// "Midnight" — the default/fallback theme skin per spec 0069 §4/§7.
// A theme skin overrides semantic color tokens and (optionally) the display
// typeface. Nothing else. A skin that needs a layout change is a defect in
// the base.

export const MIDNIGHT_THEME_CSS = `
:root {
  color-scheme: dark;

  /* Stage surfaces: dark stage, warm light. */
  --stage-0: #0a0a0f;
  --stage-1: #14141d;
  --stage-2: #1d1d29;
  --stage-1-glass: rgba(20, 20, 29, 0.88);
  --veil: rgba(10, 10, 15, 0.55);

  /* Ink: candlelit paper, not pure white. */
  --ink-primary: #f2eee3;
  --ink-muted: #9a94a6;
  --line: rgba(242, 238, 227, 0.14);

  /* Semantic roles. */
  --theme-glow: #d4a853; /* brass — accents, focus, active states */
  --narrator: #c9b98f;   /* narrator text tint */
  --private: #8fb4c9;    /* "for your eyes only" framing */
  --accuse: #b33a4a;     /* accusation, danger, the killer's color */
  --ok: #5fa97f;         /* success, correct, safe */

  --shadow-stage: 0 24px 80px rgba(0, 0, 0, 0.45);
}
`;
