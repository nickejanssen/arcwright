# Tell Me Something True Browser Golden Path Report

> Canonical path: docs/product/mini-game-readiness/tmst-golden-path-report.md
> Date: 2026-08-03
> Status: Playtest-ready internally, human usability gate not run

## Result

Tell Me Something True now reaches a local `Playtest-ready` preview path through
the browser onboarding flow. The path imports, analyzes, records permission,
creates a Nightcap Couch Race adaptation, mounts phone/shared-display/host
preview renderers, loads exact package and adaptation versions, drives the real
Tell Me Something True runtime event/submission contract, and records
deterministic local playtest evidence.

The result is not Production-ready and should not be generalized as a complete
developer proof yet. The first-time and returning human developer timing
sessions required by the plan were not run.

## Evidence

- Characterization and canary fixture: `d435bf9`
- Authoring sessions and source-preserving workspace:
  `2a0906e273ff70f057518cc3dbb06bb533a621dd`
- Deterministic analysis with uncertainty:
  `5e50f10c07b7b3f705c6255be54708f459079efe`
- Guided onboarding helper: `fa0878ae2431161215dcf53d4470287af2477bbe`
- TMST Nightcap preview adaptation and renderer: `315a1e0`
- Local preview playtest lab and replay evidence: `775c63e`

Internal walkthrough command:

```powershell
python docs/skills/arcwright-minigame/scripts/minigame_tool.py playtest --session tmst-golden-path-review-fixed --scenario happy-path --players 4 --out C:\tmp\arcwright-tmst-golden-path-review-fixed --json
```

Observed result:

- State: `Playtest-ready`
- Authority: `NON_AUTHORITATIVE_PREVIEW`
- Authority profile: `arcwright.authority.preview-only.v1`
- Package: `tell-me-something-true@0.1.0`
- Adaptation: `tell-me-something-true-nightcap-couch-race-v1@0.1.0`
- Players: 4
- Surfaces: phone, shared display, host
- Surface checks:
  - Phone mounted and submitted real TMST `input` and `vote` payloads
  - Shared display mounted and did not render private prompt payloads
  - Host mounted with preview authority visible
- Production consequence applied: false
- Cloud credentials required: false
- Production model call required: false
- Production database write required: false

## Gate Decision

Decision: `REVISE`.

Reason: the technical walking skeleton is sound enough to continue, but the
required human usability proof is missing. The plan's `GO` threshold requires a
first-time developer session at 20 minutes maximum and a returning user session
at 15 minutes maximum. Those are human gates, not agent gates.

No `STOP` criterion was observed. The implementation did not require a second
package model, duplicated CLI, unsafe authority, or destination-specific engine
code.

## Remaining Gates

- Run a first-time developer session with someone who did not build the
  platform.
- Run a returning user session.
- Record elapsed time, interventions, misunderstood concepts, corrections, and
  confidence.
- Promote the gate to `GO` only if timing, comprehension, and local playtest
  evidence all pass.
