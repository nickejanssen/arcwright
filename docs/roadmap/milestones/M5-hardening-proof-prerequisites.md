# M5: Hardening + Proof Prerequisites

**Status:** Planned  
**Build-order coverage:** none (PRD MVP done-criteria)

## Summary

This milestone closes the gap between a technically working product and a product ready for proof sessions. It focuses on adversarial safety, margin visibility, schema cleanliness, and inspection tools.

## Epics

- [M5-A: Adversarial Safety And Remediation](../epics/M5-A-adversarial-safety-and-remediation.md)
- [M5-B: Cost, Usage, And Gross Margin](../epics/M5-B-cost-usage-and-gross-margin.md)
- [M5-C: Second Arc Schema And Executable Follow-Through](../epics/M5-C-second-arc-schema-validation.md)
- [M5-D: Visual Storyworld Knowledge Graph Inspection](../epics/M5-D-visual-storyworld-phase-1-inspection.md)
- [M5-E: Character Behavior Engine Hardening](../epics/M5-E-character-behavior-engine-hardening.md)
- [M5-F: Tell Me Something True Social Opener Implementation](../epics/M5-F-tell-me-something-true-social-opener.md)
- [M5-G: Nightcap Visual Identity and Polish](../epics/M5-G-nightcap-visual-identity-and-polish.md)
- [M5-H: Narrative Fidelity Layer](../epics/M5-H-narrative-fidelity-layer.md)
- [M5-I: Nightcap Couch Race Arc And Interrogation Layer](../epics/M5-I-nightcap-couch-race-arc-and-interrogation.md)

## Exit Gate

- Adversarial safety playtest complete and blocking issues resolved
- Per-session gross margin known at each supported human player count
- A Daily Case second arc schema exists and post-M6 executable follow-through is queued
- The live knowledge graph inspection surface is live; read-only arc structure, live event stream, and character state inspection may ship as logs or defer until after proof
- The continuity and coherence eval suite (AW-272) runs against a synthetic session batch and reports knowledge-leak rate and contradiction count
- A Couch Race thin slice is rehearsable on real devices per ADR-0013 (epic M5-I; AW-272 runs against a Couch Race batch as its gate input)
