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
- `0008-content-event-type-layering.md` - AW-215 splits ContentEvent classification into a closed platform `category` enum and an open game-defined `event_type` string
- `0009-mini-game-runtime-boundary.md` - AW-249 separates reusable deterministic mini-game contracts from Nightcap presentation and records the v1 behavioral and clue fallback boundaries
- `0010-nightcap-gameplay-pivots-post-playtest.md` - post-playtest gameplay pivots for Nightcap
- `0011-single-cloudrun-service-at-mvp.md` - AW-269 defers arcwright-worker from initial cloud deploy automation until the inter-service communication mechanism is resolved
- `0012-authorial-intent-obligations-continuity-evals.md` - adopts authorial intent block, narrative obligations model with reveal-readiness signal, and continuity evals from the dissertation-draft comparison; defers post-generation continuity classifier and host rollback to open questions
- `0013-nightcap-couch-race-v1-launch-target.md` - Couch Race (competitive-investigator couch game, AI-suspect killer) becomes the Nightcap v1 launch target; killer-among-players becomes the Imposter Variant; interrogation becomes shared platform capability
- `0014-structured-interaction-resolution.md` - AW-282 authored interaction resolution and public/private event boundary
- `0015-nightcap-leverage-advantages-sabotages.md` - AW-287 generic resource/effect engine capability for Nightcap Leverage advantages and sabotages; Call Their Bluff replaced by Make Them Wait in the v1 launch set
- `0016-aw283-claim-ledger-schema.md` - AW-283 claim ledger gets dedicated claims/contradiction_flags tables instead of the generic events table, since claims are the platform's headline mechanic and a hot-path gameplay query, not incidental telemetry
- `0017-narrator-slot-resolution-and-wrapper-dressing.md` - Vesper refrain slots resolve via two mechanisms: location/time promoted to structured case-truth fields (fairness depends on them), while pure aesthetic dressing (drink, stage_name, tier, weather, etc.) moves to a per-wrapper dressing pack seeded from the moodboards; preserves the case model's arc-agnostic field-name policy and changes zero narrator lines

## Current Decision Categories

- **Technology choices**: Python, PostgreSQL, python-statemachine, LiteLLM
- **Architecture patterns**: Event-driven, knowledge graph, content safety layers
- **Scope decisions**: MVP vs. H2, schema-clean design, build paths
- **Design choices**: Character model, session state, pacing engine
