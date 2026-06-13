# Knowledge graph data architecture: state tables plus append-only event log plus in-memory cache plus embedding-ready schema

Date: May 7, 2026
Rationale: Pure SQL tables for current state. Append-only event log captures all changes (telemetry, replay, audit, recovery for free). In-memory cache during active sessions for sub-millisecond reads. Optional VECTOR(1536) columns on facts and events for future semantic features without migration. pgvector extension installed but not actively used at MVP. Apache AGE rejected at MVP: graph requirements do not justify complexity. Schema designed to add AGE later if monster RPG inference needs it.
Section: Cross-cutting
Status: Committed