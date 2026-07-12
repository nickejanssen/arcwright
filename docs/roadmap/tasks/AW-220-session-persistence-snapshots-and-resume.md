# AW-220: Session Persistence Snapshots And Resume

**Milestone / Epic:** M3 / M3-C  
**Size:** L  
**Status:** Complete

## Plain-English Summary

Persist session state and resume from nearest beat.

## Why This Matters

This task advances the documented M2-M6 path to first qualifying Nightcap playtests. It exists because `docs/architecture/05-session-persistence.md` defines this capability or gate as part of the Arcwright MVP path.

## Player Impact

Players benefit when this task reduces session failure, privacy risk, safety risk, pacing problems, or proof ambiguity before outside groups play Nightcap.

## Business Value

This task supports the H1 strategy described in `docs/prd/01-overview.md`: prove the platform through a real game before expanding into broader platform scope.

## Technical Scope

Persist session state and resume from nearest beat. Likely files affected: engine/session, engine/arc, engine/knowledge, migrations, engine/tests.

## Acceptance Criteria

- [ ] Interruption writes an `arc_beat_states` snapshot at the nearest completed beat boundary.
- [ ] Resume restores statemachine configuration, knowledge state, relationship state, and session status.
- [ ] A resumed session never restarts from the beginning unless no valid prior state exists and that exception is documented.

## Tests/Verification

- Run the smallest automated tests that prove this task where product code is changed.
- For documentation, tracker, or playtest-operation tasks, provide review evidence, JSON validation, GitHub state confirmation, or runbook approval as appropriate.
- Follow `docs/conventions/ai-contributions.md`: tests are written with code changes, not later.

## Dependencies

- AW-217
- AW-218

## Likely Files Affected

engine/session, engine/arc, engine/knowledge, migrations, engine/tests

## Must Not Do

- Do not implement product code outside this task scope.
- Do not duplicate closed M1 work.
- Do not hardcode secrets or API keys.

## Architecture References

- docs/architecture/05-session-persistence.md
- `AGENTS.md`
- `docs/architecture/15-development-guide.md`

## Playtest Relevance

This task contributes to the gated progression toward M6. The implementer must state which readiness gate it unlocks or protects when completing the task.
