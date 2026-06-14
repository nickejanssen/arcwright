# Architecture Decision Records (ADRs)

This directory contains decisions that shape the technical platform. Each ADR captures a decision, the context that required it, and its consequences.

## Structure

- Use sequential numbering: `0001-use-python-statemachine.md`, `0002-chose-postgresql.md`
- Follow the ADR format (see `0000-template.md`)
- Status: Proposed → Accepted → Superseded (if replaced by a later decision)

## Adding a New ADR

1. Copy `0000-template.md` to the next sequential number: `000N-{decision-slug}.md`
2. Fill in all sections (Status, Context, Decision, Consequences, References)
3. Use present tense in decision statement: "We use X because..."
4. Be concise - aim for a single page or two
5. Link to related decisions and open questions in the header
6. Once approved, update status from "Proposed" to "Accepted"
7. If a decision is replaced, create a new ADR and mark the old one "Superseded"

## How ADRs Relate to Other Documents

- **To specs**: An ADR decides technology/approach; specs detail what to build
- **To architecture**: ADRs accumulate to form the architecture document
- **To PRDs**: ADRs may respond to product requirements or constraints
- **To product logs**: Product decisions and open questions live in `docs/product/`; implementation-shaping technical decisions should also become ADRs here

## Consulting ADRs

When proposing changes:
1. Check existing ADRs to understand past decisions
2. Reference relevant ADRs in your new proposal
3. If overriding a decision, create a superseding ADR explaining why

## Current ADRs

- `0001-scaffolding-audit.md` - repository scaffold audit against the technical architecture
- `0002-harness-scenario-execution-contract.md` - AW-111 scenario execution contract for participants, preflight validation, and payload scope
- `0003-nightcap-web-experience-runtime.md` - AW-202 Nightcap web experience runtime and Arcwright integration contract
- `0004-pacing-telemetry-outcome-events.md` - AW-207 append-only pacing trigger and outcome telemetry contract
- `0005-l1-hard-stop-boundary.md` - AW-208 deterministic L1 safety boundary and blocked-generation return contract
- `0006-nightcap-continuity-v11.md` - approved Nightcap Continuity v1.1 fast-follow scope and v1 MVP boundary
- `0007-m2-exit-harness-and-nightcap-eight-beats.md` - AW-214 bundles the Nightcap eight-beat encoding that AW-205 deferred and lands the M2 headless exit harness

## Current Decision Categories

- **Technology choices**: Python, PostgreSQL, python-statemachine, LiteLLM
- **Architecture patterns**: Event-driven, knowledge graph, content safety layers
- **Scope decisions**: MVP vs. H2, schema-clean design, build paths
- **Design choices**: Character model, session state, pacing engine
