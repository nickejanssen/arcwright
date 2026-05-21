# Provenance chains adopted as first-class knowledge graph feature: every knowledge state record tracks why a character knows something, not just what they know

Date: May 11, 2026
Rationale: Provenance chains (ordered list of character IDs from original source to current knower) enable contradiction detection, realistic 'I heard from someone that...' dialogue, deception modeling via confidence scores, and richer telemetry. Characters with short chains speak with certainty; characters at the end of long chains express appropriate uncertainty. Added to knowledge_states schema as provenance_chain JSONB array with confidence float. No schema migration required to use; it is present from day one.
Section: Cross-cutting
Status: Committed
Tags: roadmap