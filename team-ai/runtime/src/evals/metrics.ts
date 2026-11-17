// Deterministic. No model calls.
//
// Pure metric math for the golden eval harness. `computeReport` turns a list of
// per-question `EvalOutcome`s into aggregate metrics, gate pass/fail results,
// and an overall pass verdict. No file IO, no retrieval, no clock — same input,
// same output, every time. See docs/architecture.md §16.

export type EvalTier = "none" | "small" | "large";

export interface EvalOutcome {
  id: string;
  question: string;
  hit: boolean;
  citationsValid: boolean;
  routedTo: string;
  routeCorrect: boolean;
  namespaceOk: boolean;
  tier: EvalTier;
  tierOk: boolean;
  refuseExpected: boolean;
  refuseCorrect: boolean;
  covered: boolean | null;
  expectNamespace: string;
  sourceChangedSinceGenerated: boolean;
}

export interface GateThresholds {
  hitRate: number;
  citationValidity: number;
  coverage: number;
}

export interface GateResult {
  value: number;
  threshold: number;
  pass: boolean;
}

export interface EvalMetrics {
  hitRate: number;
  citationValidity: number;
  routingAccuracy: number;
  refusalRate: number;
  namespaceAccuracy: number;
  coverage: number;
  tierCeiling: number;
  count: number;
}

export interface EvalReport {
  outcomes: EvalOutcome[];
  metrics: EvalMetrics;
  coverageByNamespace: Record<string, number>;
  gates: Record<string, GateResult>;
  pass: boolean;
}

// An empty denominator scores a perfect 1: a set with no refuse questions has a
// 100% refusal rate by vacuity, a set with no scorable questions has a 100% hit
// rate, and so on. This keeps a partial golden set from failing its own gates.
function fraction(numerator: number, denominator: number): number {
  return denominator === 0 ? 1 : numerator / denominator;
}

function gate(value: number, threshold: number): GateResult {
  return { value, threshold, pass: value >= threshold };
}

export function computeReport(outcomes: EvalOutcome[], gates: GateThresholds): EvalReport {
  const count = outcomes.length;
  const nonRefuse = outcomes.filter((outcome) => !outcome.refuseExpected);
  const refuse = outcomes.filter((outcome) => outcome.refuseExpected);
  const scored = outcomes.filter((outcome) => outcome.covered !== null);
  const coverage =
    scored.length === 0 ? 1 : scored.filter((outcome) => outcome.covered).length / scored.length;
  const byNs: Record<string, number> = {};
  for (const namespace of new Set(scored.map((outcome) => outcome.expectNamespace))) {
    const group = scored.filter((outcome) => outcome.expectNamespace === namespace);
    byNs[namespace] = group.filter((outcome) => outcome.covered).length / group.length;
  }

  const metrics: EvalMetrics = {
    hitRate: fraction(nonRefuse.filter((outcome) => outcome.hit).length, nonRefuse.length),
    citationValidity: fraction(outcomes.filter((outcome) => outcome.citationsValid).length, count),
    routingAccuracy: fraction(outcomes.filter((outcome) => outcome.routeCorrect).length, count),
    refusalRate: fraction(refuse.filter((outcome) => outcome.refuseCorrect).length, refuse.length),
    namespaceAccuracy: fraction(outcomes.filter((outcome) => outcome.namespaceOk).length, count),
    coverage,
    tierCeiling: fraction(outcomes.filter((outcome) => outcome.tierOk).length, count),
    count,
  };

  const gateResults: Record<string, GateResult> = {
    hitRate: gate(metrics.hitRate, gates.hitRate),
    citationValidity: gate(metrics.citationValidity, gates.citationValidity),
    coverage: gate(metrics.coverage, gates.coverage),
  };

  const gatesPass = Object.values(gateResults).every((result) => result.pass);
  // The tier ceiling is not a soft gate: no answer may exceed its declared
  // `expect_tier_max`, so a single violation fails the whole run.
  const pass = gatesPass && metrics.tierCeiling === 1;

  return { outcomes, metrics, coverageByNamespace: byNs, gates: gateResults, pass };
}
