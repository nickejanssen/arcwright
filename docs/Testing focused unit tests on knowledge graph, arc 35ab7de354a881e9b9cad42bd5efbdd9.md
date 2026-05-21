# Testing: focused unit tests on knowledge graph, arc engine, safety, model routing

Date: May 7, 2026
Rationale: Solo founder plus Claude Code primary developer plus MVP scope means full TDD too slow and manual-only too risky. Critical correctness paths get unit tests; everything else manual at MVP. Integration tests added in H2 when external developers join. Specifically: knowledge graph correctness, arc state transitions, safety enforcement, model routing fallback get unit tests.
Section: Cross-cutting
Status: Committed