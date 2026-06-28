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

// TODO: wrapper_id should come from a session-level field once the API
// exposes it. Currently gameId is always "tell-me-something-true" so wrapper
// selection falls back to high-society. Check for a variant suffix on gameId
// (e.g. "tell-me-something-true:corporate") as a forward-compatible path.
export function getDiegeticWrapper(gameId: string): DiegeticWrapper {
  for (const key of Object.keys(WRAPPERS)) {
    if (gameId.includes(key)) return WRAPPERS[key];
  }
  return DEFAULT_WRAPPER;
}
