# Service architecture: library plus thin API monolith at MVP

Date: May 7, 2026
Rationale: Engine is a standalone Python library. API server is a thin HTTP wrapper. Same single deployed process, but engine has zero dependency on web framework. Enforces platform-clean discipline at type system level rather than relying on developer discipline. Alternatives: pure monolith (HTTP context leaks into engine), microservices (overkill for solo founder MVP).
Section: Cross-cutting
Status: Committed