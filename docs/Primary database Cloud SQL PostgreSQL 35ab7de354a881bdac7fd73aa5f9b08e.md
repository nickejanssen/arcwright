# Primary database: Cloud SQL PostgreSQL

Date: May 7, 2026
Rationale: In-region with Cloud Run (no cross-cloud latency). Real PostgreSQL with full extension support (pgvector, AGE if needed). $300 GCP free credits cover ~20 months of minimum config. Neon initially recommended but rejected: AWS-only as of May 2026, cross-cloud latency penalty 30-40ms per query. Migration to Neon possible if/when GCP support ships.
Section: Cross-cutting
Status: Committed