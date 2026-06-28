export interface DiegeticWrapper {
  title: string;
  scaffold: string;
  // TODO: replace placeholder strings with human-authored narrator prose
  inputIntro: string;
  spotlightIntro: string;
  allTruthMock: string;
  allLieMock: string;
}

const WRAPPERS: Record<string, DiegeticWrapper> = {
  "high-society": {
    title: "The Host's Parlor Game",
    scaffold: "blackmail journal pages",
    inputIntro:
      "Our host has devised a confession exercise. Everyone has secrets. Let us see who reveals theirs — and who invents new ones. You have forty-five seconds.",
    spotlightIntro:
      "And now, let us turn our attention to this evening's most interesting disclosure.",
    allTruthMock:
      "How disappointingly honest. One expects at least a little embellishment at a dinner party.",
    allLieMock:
      "Not a single honest soul at the table. How delightfully scandalous.",
  },
  corporate: {
    title: "Mandatory Synergy",
    scaffold: "radical candor app",
    inputIntro:
      "Team building exercise initiated. Please submit your workplace disclosure into the radical candor application. You have forty-five seconds to complete your entry.",
    spotlightIntro: "Processing disclosure for alignment review.",
    allTruthMock:
      "Acceptable. Though leadership appreciates a degree of strategic ambiguity in high-performers.",
    allLieMock:
      "Impressive. The entire team demonstrates advanced stakeholder management capabilities.",
  },
  "sci-fi": {
    title: "Biometric Calibration",
    scaffold: "AI stress test",
    inputIntro:
      "Biometric honesty calibration sequence initiated. All subjects must submit a statement within forty-five seconds. The AI cannot be deceived. Probably.",
    spotlightIntro: "Analyzing subject disclosure for deception signatures.",
    allTruthMock:
      "Anomaly detected. Zero deception signatures across all subjects. Recalibrating baseline assumptions.",
    allLieMock:
      "Critical error. Deception signatures at maximum. Trust protocol suspended.",
  },
};

const DEFAULT_WRAPPER = WRAPPERS["high-society"];

// Select the diegetic wrapper for the current session.
//
// gameVariant is the arc-level wrapper identifier ("high-society", "corporate",
// "sci-fi"). It is not yet returned by the API — pass it as undefined until the
// engine exposes it (tracked in AW-265 follow-up). gameId is used as a
// fallback: the engine may append a variant suffix
// (e.g. "tell-me-something-true:corporate") for forward-compatibility.
export function getDiegeticWrapper(
  gameId: string,
  gameVariant?: string,
): DiegeticWrapper {
  if (gameVariant && WRAPPERS[gameVariant]) return WRAPPERS[gameVariant];
  for (const key of Object.keys(WRAPPERS)) {
    if (gameId.includes(key)) return WRAPPERS[key];
  }
  return DEFAULT_WRAPPER;
}
