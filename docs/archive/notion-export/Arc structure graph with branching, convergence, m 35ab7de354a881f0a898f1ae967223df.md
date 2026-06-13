# Arc structure: graph with branching, convergence, multiple endings, loops

Date: May 7, 2026
Rationale: Arcs are not linear sequences. Beats are nodes; transitions are conditional edges. Graph supports: branching (multiple paths from a beat), convergence (multiple paths into a beat), loops (repeating beats like investigation rounds), multiple terminals (different endings), conditional transitions evaluated at runtime. World mutability supported through state JSONB on locations and objects. Arc mutation at runtime architecturally possible (data-driven YAML, not compiled), implementation deferred until use case requires it.
Section: Cross-cutting
Status: Committed