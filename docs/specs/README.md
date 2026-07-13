# Implementation Specifications

This directory contains detailed specs for implementing features and systems. Each spec takes an architecture decision or product requirement and defines: what will be built, how to test it, and known risks.

## Structure

- Use sequential numbering: `0001-arc-execution-state-machine.md`, `0002-knowledge-graph-api.md`
- Include status, author, date, and acceptance criteria
- Follow the spec format (see `0000-template.md`)
- Status: Draft → Approved → In Progress → Done

## Adding a New Spec

1. Copy `0000-template.md` to the next sequential number: `000N-{feature-slug}.md`
2. Fill all sections (Title, Status, Author/date, References, Overview, In Scope, Out of Scope, Acceptance Criteria, Test Plan, Risks/Unknowns, Open Questions)
3. Link specs to the ADRs and architecture sections that justify them
4. Be specific: list what APIs will look like, database changes, etc.
5. Include acceptance criteria that can be verified by tests or review
6. Flag unknowns and risks explicitly—don't hide them

## How Specs Relate to Other Documents

- **From ADRs**: Specs implement decisions captured in architecture decision records
- **From architecture**: Specs detail how to build the systems described in architecture docs
- **For code reviews**: Use acceptance criteria to verify implementations match specs

## Using Specs During Development

1. Before coding: create a spec and get it reviewed/approved
2. During coding: reference spec acceptance criteria and test plan
3. After coding: verify acceptance criteria met and specs are current

## Spec Lifecycle

- **Draft**: Being written, not ready for review
- **Approved**: Reviewed and ready to implement
- **In Progress**: Someone is actively working on it
- **Done**: Implementation complete and verified against acceptance criteria

## Current Specs

- **Arc Execution**: State machine, beat transitions, pacing
- **Knowledge Graph**: Character state, fact storage, inference
- **Session Management**: Creation, persistence, recovery
- **Content Events**: Schema, routing, SSE delivery
- **Experience Quality**: Game-layer quality bar, content standards, fun instrumentation (0068)
- **Visual Design System**: Nightcap UI, animation, tokens, theme skins (0069)
