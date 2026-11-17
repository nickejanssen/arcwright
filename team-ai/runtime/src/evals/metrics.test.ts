import { describe, expect, it } from "vitest";

import { computeReport, type EvalOutcome, type GateThresholds } from "./metrics.js";

const DEFAULT_GATES: GateThresholds = {
  hitRate: 0.8,
  citationValidity: 1.0,
  coverage: 0.8,
};

function outcome(overrides: Partial<EvalOutcome> = {}): EvalOutcome {
  return {
    id: "eval.test.q",
    question: "q?",
    hit: true,
    citationsValid: true,
    routedTo: "domain-sme",
    routeCorrect: true,
    namespaceOk: true,
    tier: "small",
    tierOk: true,
    refuseExpected: false,
    refuseCorrect: true,
    covered: null,
    expectNamespace: "domain",
    sourceChangedSinceGenerated: false,
    ...overrides,
  };
}

describe("computeReport metrics", () => {
  it("hitRate is the fraction of non-refuse outcomes that hit", () => {
    const report = computeReport(
      [
        outcome({ hit: true }),
        outcome({ hit: false }),
        outcome({ hit: true }),
        outcome({ hit: true }),
        // refuse outcomes are excluded from the denominator entirely
        outcome({ refuseExpected: true, hit: false, refuseCorrect: true }),
      ],
      DEFAULT_GATES,
    );
    expect(report.metrics.hitRate).toBeCloseTo(0.75, 10);
    expect(report.metrics.count).toBe(5);
  });

  it("hitRate is 1 when there are no non-refuse outcomes", () => {
    const report = computeReport(
      [outcome({ refuseExpected: true, hit: false, refuseCorrect: true })],
      DEFAULT_GATES,
    );
    expect(report.metrics.hitRate).toBe(1);
  });

  it("citationValidity counts every outcome, including empty-path refusals as valid", () => {
    const report = computeReport(
      [
        outcome({ citationsValid: true }),
        outcome({ citationsValid: false }),
        outcome({ refuseExpected: true, citationsValid: true, refuseCorrect: true }),
        outcome({ citationsValid: true }),
      ],
      DEFAULT_GATES,
    );
    expect(report.metrics.citationValidity).toBeCloseTo(0.75, 10);
  });

  it("routingAccuracy is the fraction of outcomes routed correctly", () => {
    const report = computeReport(
      [outcome({ routeCorrect: true }), outcome({ routeCorrect: false })],
      DEFAULT_GATES,
    );
    expect(report.metrics.routingAccuracy).toBe(0.5);
  });

  it("refusalRate is the fraction of refuse-expected outcomes that refused", () => {
    const report = computeReport(
      [
        outcome({ refuseExpected: true, refuseCorrect: true }),
        outcome({ refuseExpected: true, refuseCorrect: false }),
        outcome({ refuseExpected: false, refuseCorrect: true }),
      ],
      DEFAULT_GATES,
    );
    expect(report.metrics.refusalRate).toBe(0.5);
  });

  it("refusalRate is 1 when there are no refuse-expected outcomes", () => {
    const report = computeReport([outcome(), outcome()], DEFAULT_GATES);
    expect(report.metrics.refusalRate).toBe(1);
  });

  it("tierCeiling is the fraction of outcomes within their tier ceiling", () => {
    const report = computeReport(
      [outcome({ tierOk: true }), outcome({ tierOk: true }), outcome({ tierOk: false })],
      DEFAULT_GATES,
    );
    expect(report.metrics.tierCeiling).toBeCloseTo(2 / 3, 10);
  });

  it("namespaceAccuracy is the fraction of outcomes with namespaceOk", () => {
    const report = computeReport(
      [
        outcome({ namespaceOk: true }),
        outcome({ namespaceOk: false }),
        outcome({ refuseExpected: true, refuseCorrect: true, namespaceOk: true }),
        outcome({ namespaceOk: true }),
      ],
      DEFAULT_GATES,
    );
    expect(report.metrics.namespaceAccuracy).toBe(0.75);
  });

  it("reports coverage overall and per namespace", () => {
    const outcomes = [
      outcome({ id: "a", expectNamespace: "kg", covered: true }),
      outcome({ id: "b", expectNamespace: "kg", covered: false }),
      outcome({ id: "c", expectNamespace: "safety", covered: true }),
      outcome({ id: "d", expectNamespace: "", covered: null }),
    ];
    const report = computeReport(outcomes, DEFAULT_GATES);
    expect(report.metrics.coverage).toBeCloseTo(2 / 3, 10);
    expect(report.coverageByNamespace["kg"]).toBeCloseTo(0.5, 10);
    expect(report.coverageByNamespace["safety"]).toBeCloseTo(1, 10);
  });
});

describe("computeReport gates", () => {
  it("reports refusalRate without gating on it", () => {
    const outcomes = [outcome({ id: "a", refuseExpected: true, refuseCorrect: false })];
    const report = computeReport(outcomes, DEFAULT_GATES);
    expect(report.metrics.refusalRate).toBe(0);
    expect(report.gates.refusalRate).toBeUndefined();
    expect(report.pass).toBe(true);
  });

  it("passes when every gate meets its threshold and the tier ceiling is perfect", () => {
    const report = computeReport(
      [outcome(), outcome(), outcome({ refuseExpected: true, refuseCorrect: true })],
      DEFAULT_GATES,
    );
    expect(report.gates.hitRate).toEqual({ value: 1, threshold: 0.8, pass: true });
    expect(report.pass).toBe(true);
  });

  it("fails the report when a soft gate misses", () => {
    const report = computeReport([outcome({ hit: true }), outcome({ hit: false })], DEFAULT_GATES);
    expect(report.gates.hitRate?.pass).toBe(false);
    expect(report.pass).toBe(false);
  });

  it("fails the report when the tier ceiling is violated even though all gates pass", () => {
    const report = computeReport([outcome({ tierOk: false })], DEFAULT_GATES);
    expect(report.gates.hitRate?.pass).toBe(true);
    expect(report.gates.citationValidity?.pass).toBe(true);
    expect(report.gates.coverage?.pass).toBe(true);
    expect(report.metrics.tierCeiling).toBe(0);
    expect(report.pass).toBe(false);
  });

  it("reports namespaceAccuracy without gating on it", () => {
    const report = computeReport(
      [outcome({ namespaceOk: false }), outcome({ namespaceOk: false }), outcome()],
      DEFAULT_GATES,
    );
    expect(report.metrics.namespaceAccuracy).toBeCloseTo(1 / 3, 10);
    expect(report.gates.namespaceAccuracy).toBeUndefined();
    expect(report.pass).toBe(true);
  });

  it("uses a >= comparison so a gate exactly at threshold passes", () => {
    const report = computeReport(
      [
        outcome({ hit: true }),
        outcome({ hit: true }),
        outcome({ hit: true }),
        outcome({ hit: true }),
        outcome({ hit: false }),
      ],
      DEFAULT_GATES,
    );
    expect(report.metrics.hitRate).toBe(0.8);
    expect(report.gates.hitRate?.pass).toBe(true);
  });

  it("only the five soft metrics get gate entries (tierCeiling is not a soft gate)", () => {
    const report = computeReport([outcome()], DEFAULT_GATES);
    expect(Object.keys(report.gates).sort()).toEqual(["citationValidity", "coverage", "hitRate"]);
  });
});
