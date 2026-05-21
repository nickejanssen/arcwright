# Arc execution engine: event-driven coordinator with Python asyncio plus python-statemachine v3, graph traversal

Date: May 7, 2026
Rationale: Engine is event-driven coordinator: in-process pub/sub via asyncio, components subscribe and emit. python-statemachine v3.0 (Feb 2026) handles beat progression as graph traversal (branching, convergence, multiple endings, loops). Best fit for concurrent concerns (beat, pacing, initiative, character behavior, safety). Lowest engine overhead for player-perceived latency. Temporal rejected: heavyweight workflow engine designed for long-running cross-service durability, overkill for solo founder MVP with hour-long sessions.
Section: Cross-cutting
Status: Committed