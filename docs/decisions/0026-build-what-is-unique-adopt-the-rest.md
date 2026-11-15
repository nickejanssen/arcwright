---
id: productroadmap.decisions.0026-build-what-is-unique-adopt-the-rest
namespace: product-roadmap
title: "ADR-0026: Build What Is Unique, Adopt The Rest"
owner: Nico Janssen
status: active
review_by: "2027-05-15"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# ADR 0026: Build what is unique, adopt the rest

- **Status:** Accepted
- **Date:** 2026-11-15
- **Deciders:** Founder (stated 2026-11-14; recording approved 2026-11-15), Claude Code as Scribe
- **Related:** D-114 in `docs/product/decisions-log.csv`; `AGENTS.md` architecture principles 7 (progressive proprietary infrastructure) and 8 (provider-agnostic routing); `docs/architecture/02-technology-stack.md` section 2.11

## Context

The November 2026 reset audit found the clearest case of building what already exists: the Nightcap web client is about 5,300 lines with no third-party libraries. A first market pass in the same audit found that most pieces around the engine are mature and often free: writer-controlled branching story (Ink, Yarn Spinner, Twine, Arcweave), voices (ElevenLabs, Inworld, Kokoro), animation (Rive), game and UI frameworks (React, PixiJS, Phaser), and model routing (LiteLLM, already adopted).

The founder's direction, in his words on 2026-11-14: "We should not build what exists. We should build what makes Arcwright unique, use other tech as part of our stack, and replace third parties only when we need features they don't offer, they get too expensive, or we want to build our own custom version for a strong purpose." He also asked that any session say plainly when Arcwright's purpose is already solved by existing technology.

Principle 7 already says to launch on managed third-party AI services first. This ADR applies the same idea to the whole stack, not only AI services.

Alternatives considered:

- **Keep building in-house where code already exists.** Rejected: it spends the scarcest resource, founder hours and build sessions, on parts that do not make Arcwright different.
- **Adopt a whole "talking character" product.** Rejected: those products decide what a character says. Arcwright's possible edge is that a character speaks only from what it knows, by rule.

## Decision

We build only what makes Arcwright unique and adopt existing technology for everything else.

1. **Ours to build:** deterministic story state, the knowledge graph (who knows what, from whom), character behavior constrained by knowledge, pacing, fairness checks on authored content, audience-targeted events, and play records in one shape for every game.
2. **Adopt:** screens and UI frameworks, animation, voices, sound, story-writing tools, graph drawing, model providers and routing, hosting, sign-in, payments.
3. **Replace an adopted tool only when** it lacks a feature we need, it becomes too expensive, or there is a strong purpose for a custom version. Record the trigger when it happens.
4. **Integrate at two places.** Model providers plug into the router inside the engine. Everything a player sees or hears belongs to the game's display side, which the engine knows nothing about.
5. **Take voices, not brains.** An adopted product may speak a line; it never decides the line or the session state.
6. **Budget:** free options first. Up to $50 a month in total when a free option falls short, decided ahead of time when a needed feature is known to be paid. Nothing is installed, signed up for or bought without the founder's approval.
7. **Say so.** When a session finds that existing technology already does what a task proposes to build, it says so plainly before building.

## Consequences

### Positive consequences

- Build sessions go to the parts only Arcwright has.
- The thin Nightcap can reach players sooner, which is the only real test of the product.
- Each adopted layer can be swapped later without touching the engine.

### Negative consequences

- More licences, terms and free-tier limits to track. Two known today: the ElevenLabs free plan carries no commercial licence, and Rive's free exports show a splash screen.
- A new dependency is a hard rule in `AGENTS.md`, so each adoption needs its own founder approval.
- Importers and adapters become real work (for example AW-306).

### Trade-offs

We give up full control of the outer layers in exchange for speed and focus. The engine boundary (surface agnosticism) is what makes that trade safe.

## References

- `docs/architecture/02-technology-stack.md` section 2.11: the full target stack, with verified licences and prices and the date each was checked.
- `docs/product/2026-11-15-reset-audit.md`: finding F18 and the first market pass.
- Tasks AW-306 (story-tool importer), AW-309 (build-versus-adopt review), AW-316 (competitor research).
