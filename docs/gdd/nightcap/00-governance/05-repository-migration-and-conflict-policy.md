# Nightcap — Repository Migration and Conflict Policy

**Status:** DECIDED migration policy, 2026-08-31.

## Decision

The Nightcap Master GDD at `docs/gdd/nightcap/` is the current Nightcap game-design source of truth. The former Couch Race and Imposter Story Bibles are archived and retained only for history/traceability.

## What this migration supersedes

Where older Nightcap materials conflict with the current GDD, the current GDD wins for new product/design work. Material conflicts already identified include:

- D-052's former four-human-player V1 floor vs. current mandatory first-class two-player support;
- D-071 / ADR-0013's former fixed Couch Race V1 definition and fixed 2–8 range vs. the current GDD and OPEN V1 upper bound;
- former fixed Couch Race beat/scoring assumptions vs. the current WATCH → HUNT → THINK → PLAY → REACT loop and Structured Reconstruction endgame;
- former numerical/subjective case-strength or score-comparison ideas vs. deterministic solve resolution;
- former minigame-primary Leverage sourcing vs. the current reopened TESTING source mix;
- former fully-generative-everything language vs. current deterministic authored state plus hybrid generation.

Historical ADRs and product log rows are preserved rather than rewritten. They describe what was decided at that time.

## Specialist authorities retained

- `docs/design/the-host.md` remains Vesper's specialist character/voice authority where it does not conflict with the GDD.
- `docs/design/nightcap-art-direction.md` remains the visual-direction authority where it does not conflict with the GDD.
- Architecture ADRs continue to govern platform/technical architecture until explicitly superseded.

The GDD owns current gameplay meaning, mystery fairness, player-count design, endgame, competition rules, and experience behavior.

## Implementation conflict rule

A source-of-truth migration does **not** pretend existing code already implements the new design. If a current spec, roadmap item, arc JSON, test, or code path still encodes an older Couch Race assumption, record it as an implementation reconciliation item. Do not silently reinterpret the old implementation as compliant.

## Link compatibility

The old Story Bible paths remain as redirect stubs pointing to the archive and current GDD. This preserves historical links without allowing the old files to masquerade as current canon.

## Known migration gaps

- The GDD's Content / AI direction is authoritative in the decision ledger and world/content-boundary page, but a deeper dedicated Content/AI system page may still be useful if future implementation work requires more detail.
- The V1 upper player-count bound remains OPEN.
- Paper Test #2 Gate 1 remains unpassed; validation evidence can reopen DECIDED design when warranted.

## Verification target

Before merging this migration, repository searches should show no active Nightcap document treating either old Story Bible as current authority. Historical ADRs, product logs, and archive files may reference the old paths only when clearly historical or when the compatibility stub is intentionally used.
