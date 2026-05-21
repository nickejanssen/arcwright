# D-040 Build path reaffirmed and clarified

Date: May 19, 2026
Rationale: D-059 (build for Nightcap, design platform-clean) stands. Platform-clean means clean internal abstractions and game-agnostic schemas, not external API exposure during H1. External developer exposure is gated by closer-to-Lighthouse plus the updated H2 profitability gate per D-031. The audit's generalized API engine concern is addressed by external-exposure timing, not by abandoning internal architectural discipline. Refactoring debt from a monolith-first approach would fall hardest when Monster RPG ships in H2, which is unacceptable for a solo founder.
Section: Cross-cutting
Status: Committed