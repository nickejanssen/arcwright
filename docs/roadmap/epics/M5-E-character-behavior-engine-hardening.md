# M5-E: Character Behavior Engine Hardening

**Milestone:** M5
**Status:** Planned

## Plain-English Summary

Close the remaining architecture commitments in the character behavior engine before M6 qualifying sessions: per-character social-pressure compute and killer-tell tier selection by group size.

## Why This Matters

Epic M2-E shipped the character behavior engine end to end (behavior profile, knowledge-constrained dialogue, initiative, NPC-NPC exchange). Two specific architecture commitments in `docs/architecture/07-character-behavior.md` were forward-compatibly substituted or deferred during M2-E and need to land before real-user qualifying sessions begin in M6 so the player experience matches the §7.4-§7.5 design.

## Player Impact

These tasks change *how* the room feels when the killer is under stress and *how visible* tells are at different group sizes. The §7.4 compute is what makes the killer become more themselves under pressure — the moment players argue about in retrospect. The §7.5 tier selection is what makes the killer experience scale fairly across the v1 4-player floor and larger groups without retuning.

## Business Value

Protects the M6 qualifying-session proof: without these, the killer experience may feel flat under heavy suspicion and may not calibrate fairly across player counts. Both are explicit v1 architecture commitments, not deferred v1.1 scope.

## Technical Scope

Two focused additions to `engine/characters`:

1. A per-character `social_pressure` compute aligned with §7.4 (separate from session-level `dramatic_tension_score`), wired into initiative threshold and `crumble_threshold` so tells intensify under stress.
2. Killer-tell tier selection by player-group size aligned with §7.5, selecting from `behavior_profile.tells` at session start.

## Tasks

- [AW-246: Per-Character Social Pressure Compute](../tasks/AW-246-per-character-social-pressure-compute.md)
- [AW-247: Killer Tell Tier Selection By Group Size](../tasks/AW-247-killer-tell-tier-selection-by-group-size.md)

## Acceptance Criteria

- All child tasks satisfy their acceptance criteria.
- The architecture §7.4 and §7.5 commitments are demonstrably in code, not narrated in docs.
- No regression on the AW-211/AW-212/AW-213 behavior-engine surface.

## Tests/Verification

- Each child task ships with focused unit tests, including any harness-level proof that initiative and tell expression respond as the architecture describes.
- Behavior-engine regression tests continue to pass.

## Dependencies

- Parent milestone: M5
- Hard prerequisite: M2-E complete (AW-211, AW-212, AW-213 all shipped).
- Soft prerequisite: M5-A adversarial safety playtest may surface additional findings worth folding in before implementation.

## Must Not Do

- Do not redesign the behavior engine. These are additive hardening tasks against the existing surface.
- Do not turn either compute into a Nightcap-specific assumption; architecture §7.4 and §7.5 are platform-level.
- Do not place provider or model strings outside `config/routing_table.json` and `engine/routing/router.py`.

## Architecture References

- docs/architecture/07-character-behavior.md S7.4-S7.5
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This epic is on the direct path to M6 qualifying sessions. The §7.4 compute changes how the killer feels under pressure; the §7.5 tier selection changes how the killer experience scales across player counts. Both must be in code before outside groups sit down to play.
