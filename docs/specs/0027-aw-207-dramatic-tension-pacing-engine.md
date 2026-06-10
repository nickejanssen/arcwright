# AW-207: Dramatic Tension Pacing Engine

**Status**: Approved

**Author**: Codex | **Date**: 2026-06-10

---

# References

- Related ADRs: `docs/decisions/0001-scaffolding-audit.md`, `docs/decisions/0004-pacing-telemetry-outcome-events.md`
- Architecture sections: `docs/architecture/03-arc-execution.md`, `docs/architecture/11-telemetry.md`, `docs/architecture/15-development-guide.md`
- Related specs: `docs/specs/0024-aw-204-dynamic-arcstatechart-generation.md`
- PRD sections: `docs/prd/02-requirements.md`
- Roadmap task: `docs/roadmap/tasks/AW-207-dramatic-tension-pacing-engine.md`

---

# Overview

This spec defines the deterministic pacing core for dramatic tension scoring and pacing intervention decisions. The pacing core consumes normalized session signals, computes the weighted score from arc configuration, produces a stable intervention descriptor, and defines append-only-safe telemetry payloads for later persistence.

---

# Design Decisions

## Signal Derivation Boundary

AW-207 does not derive pacing signals from database rows, knowledge graph facts, or event streams. It defines a caller-supplied `PacingSignalSnapshot` input model:

```python
class PacingSignalSnapshot(BaseModel):
    beat_id: str
    time_pressure: float = Field(ge=0.0, le=1.0)
    action_rate: float = Field(ge=0.0, le=1.0)
    suspicion: float = Field(ge=0.0, le=1.0)
    clue_coverage: float = Field(ge=0.0, le=1.0)
```

All four numeric fields are normalized and validated as `0.0` through `1.0` before they reach the pacing core.

Future coordinator or telemetry integration work owns derivation:

- `time_pressure`: derived from beat entry time, elapsed time, and authored pacing metadata.
- `action_rate`: derived from recent player-action events over a defined window.
- `suspicion`: derived from generic accusation or confidence signals, not hardcoded Nightcap killer literals.
- `clue_coverage`: derived from generic authored-progress or knowledge-distribution signals, not hardcoded Nightcap clue literals.

This keeps AW-207 pure, deterministic, and platform-generic while leaving the harder derivation contract explicit for the future session coordinator work.

## Score Formula

The pacing core computes:

```text
dramatic_tension_score =
  w_time * time_pressure
  + w_action * action_rate
  + w_suspicion * suspicion
  + w_coverage * clue_coverage
```

Weights come from `ArcDefinition.pacing_config`. Existing `PacingConfig` validation already requires weights to sum to `1.0`.

## Intervention Descriptor Schema

The pacing core returns zero or more `PacingIntervention` descriptors. A descriptor is a deterministic instruction for downstream runtime code, not a model call and not a rendered event.

```python
class PacingInterventionType(str, Enum):
    stall = "stall"
    misdirection = "misdirection"
    quality_upgrade = "quality_upgrade"

class PacingRecommendedAction(str, Enum):
    inject_clue_or_narrator_prompt = "inject_clue_or_narrator_prompt"
    inject_misdirection = "inject_misdirection"
    upgrade_quality_tier = "upgrade_quality_tier"

class PacingIntervention(BaseModel):
    intervention_type: PacingInterventionType
    recommended_action: PacingRecommendedAction
    beat_id: str
    tension_score_at_trigger: float
    threshold: float
    signal_snapshot: PacingSignalSnapshot
```

Threshold behavior is mutually exclusive:

- `score < stall_threshold`: emits `stall` with `inject_clue_or_narrator_prompt`.
- `score >= premium_threshold`: emits `quality_upgrade` with `upgrade_quality_tier`.
- `misdirection_threshold < score < premium_threshold`: emits `misdirection` with `inject_misdirection`.

Premium threshold takes precedence over misdirection because a peak dramatic moment should upgrade dialogue quality, not inject a red herring that may undercut the scene. With the current threshold model, `stall` and the upper-threshold interventions should not both match for the same score.

## Telemetry Event Payloads

AW-207 defines payload builders for append-only event rows. It does not introduce the async pacing loop that will call these builders on an interval.

### Tension Update

Event type: `tension_update`

Payload:

```json
{
  "score": 0.42,
  "beat_id": "investigation"
}
```

`beat_id` enriches the `docs/architecture/11-telemetry.md` baseline payload of `{"score": float}` so tension curves can be grouped by beat during training-data review. AW-207 updates the architecture text to make this enrichment canonical.

### Pacing Intervention

Event type: `pacing_intervention`

Payload:

```json
{
  "trigger_type": "stall",
  "tension_score_at_trigger": 0.18,
  "beat_id": "investigation"
}
```

This event is emitted at trigger time. It intentionally does not include `outcome_resumed_within_60s`, because that value is retrospective and cannot be appended safely to the same row later.

This event is emitted only for `stall` and `misdirection`. `quality_upgrade` does not emit a `pacing_intervention` event because `outcome_resumed_within_60s` has no meaningful interpretation for a quality-tier upgrade.

### Pacing Intervention Outcome

Event type: `pacing_intervention_outcome`

Payload:

```json
{
  "trigger_type": "stall",
  "tension_score_at_trigger": 0.18,
  "beat_id": "investigation",
  "outcome_resumed_within_60s": true
}
```

AW-207 only defines the payload builder. The future async pacing-loop or coordinator ticket owns waiting 60 seconds, assessing resumed activity, and emitting this outcome event.

This event is emitted only for `stall` and `misdirection`. AW-207 adopts this distinct event type for outcome tracking and updates `docs/architecture/11-telemetry.md` so the architecture matches the append-only event-table rule in the same architecture section.

## DecisionLog Shape

Pacing interventions also produce a `decision_logs` payload contract. The future persistence integration may write this to the `decision_logs` table.

`decision_type`:

```text
pacing_intervention
```

`input_context` contains the full reproducible pacing decision input:

```json
{
  "signal_snapshot": {
    "beat_id": "investigation",
    "time_pressure": 0.2,
    "action_rate": 0.1,
    "suspicion": 0.3,
    "clue_coverage": 0.4
  },
  "pacing_config": {
    "stall_threshold": 0.25,
    "misdirection_threshold": 0.8,
    "premium_threshold": 0.85,
    "w_time": 0.3,
    "w_action": 0.3,
    "w_suspicion": 0.2,
    "w_coverage": 0.2
  },
  "computed_score": 0.24
}
```

`outcome` contains the emitted intervention descriptor:

```json
{
  "intervention_type": "stall",
  "recommended_action": "inject_clue_or_narrator_prompt",
  "beat_id": "investigation",
  "tension_score_at_trigger": 0.24,
  "threshold": 0.25
}
```

`signal_snapshot` is intentionally omitted from `outcome` because it is already stored in `input_context`. This avoids duplicating the same decision input in both JSONB fields while preserving replayability.

For `quality_upgrade`, the decision-log builder records the descriptor even though no `pacing_intervention` or `pacing_intervention_outcome` event is emitted.

## Architecture Naming Precedence

`docs/architecture/03-arc-execution.md` previously used `score_at_trigger`, while `docs/architecture/11-telemetry.md` used `tension_score_at_trigger`. AW-207 treats §11.3 as authoritative for telemetry field naming and updates §3.3 to match.

## BeatPacingConfig Overrides

`BeatPacingConfig.stall_threshold_seconds`, `acceleration_trigger`, and `misdirection_trigger` are not wired into threshold evaluation in AW-207. They require signal derivation and coordinator timing semantics, which are out of scope for this task.

AW-207 may carry beat id through the snapshot and telemetry payloads so future derivation can use beat-level pacing metadata without changing the scoring interface.

## Module Placement

`engine/telemetry/` already exists as an empty package. AW-207 uses it for telemetry payload builders and decision-log payload construction. This is still a cross-module engine change, and this spec records the design review rationale:

- `engine/arc/pacing.py`: deterministic score and intervention descriptors.
- `engine/telemetry/pacing.py`: event payload and decision-log payload builders for pacing.

This preserves separation between arc decision logic and telemetry formatting.

---

# In Scope

- `PacingSignalSnapshot` model with normalized platform-generic inputs
- `DramaticTensionScore` or equivalent deterministic scorer
- `PacingIntervention` descriptor schema
- Threshold evaluation for stall, misdirection, and quality upgrade
- Tension update event payload builder
- Pacing intervention event payload builder
- Pacing intervention outcome payload builder
- Pacing decision-log payload builder
- Unit tests proving score math, threshold decisions, descriptor shape, and payload fields

---

# Out Of Scope

- Deriving pacing signals from database rows, event streams, or knowledge graph facts
- Async pacing loop scheduling
- Waiting 60 seconds and emitting outcome events
- Writing persistent `events` or `decision_logs` rows from a live coordinator
- LLM calls, prompt assembly, model routing, or quality-tier mutation
- API route changes
- UI or Nightcap web experience changes
- Database schema or migration changes
- Nightcap-specific clue, killer, or accusation derivation logic

---

# Acceptance Criteria

- [ ] Dramatic tension score is computed from configured time, action, suspicion, and clue coverage weights.
- [ ] Signal inputs are normalized and validated as `0.0` through `1.0`.
- [ ] Stall threshold emits a deterministic `stall` intervention descriptor with the documented recommended action.
- [ ] Misdirection threshold emits a deterministic `misdirection` intervention descriptor with the documented recommended action.
- [ ] Premium threshold emits a deterministic `quality_upgrade` intervention descriptor without calling routing or generation.
- [ ] Threshold evaluation is mutually exclusive, with `quality_upgrade` taking precedence over `misdirection` at or above `premium_threshold`.
- [ ] Tension update payload includes `score` and `beat_id`.
- [ ] Pacing intervention payload includes `trigger_type`, `tension_score_at_trigger`, and `beat_id`.
- [ ] Pacing intervention outcome payload includes `trigger_type`, `tension_score_at_trigger`, `beat_id`, and `outcome_resumed_within_60s`.
- [ ] `quality_upgrade` does not emit `pacing_intervention` or `pacing_intervention_outcome` telemetry.
- [ ] Pacing decision-log input context includes full signal snapshot, pacing config, and computed score.
- [ ] Pacing decision-log outcome includes the intervention descriptor fields needed to replay the decision.
- [ ] `docs/architecture/03-arc-execution.md` and `docs/architecture/11-telemetry.md` match the AW-207 telemetry contracts.
- [ ] No provider/model strings, LLM calls, API changes, migrations, or Nightcap-specific signal derivation are introduced.

---

# Test Plan

- Unit tests: weighted score uses `ArcDefinition.pacing_config` weights exactly.
- Unit tests: normalized signal fields reject values below `0.0` or above `1.0`.
- Unit tests: stall, misdirection, and quality upgrade thresholds produce expected intervention descriptors.
- Unit tests: score at or above `premium_threshold` emits `quality_upgrade` instead of both `misdirection` and `quality_upgrade`.
- Unit tests: no intervention is emitted when no threshold is crossed.
- Unit tests: `tension_update` payload matches architecture-required fields plus `beat_id`.
- Unit tests: `pacing_intervention` payload omits retrospective outcome.
- Unit tests: `quality_upgrade` does not produce pacing intervention event payloads.
- Unit tests: `pacing_intervention_outcome` payload includes `outcome_resumed_within_60s`.
- Unit tests: decision-log payload contains full input context and intervention outcome.

Run:

- `python -m pytest engine/tests/test_pacing.py engine/tests/test_pacing_telemetry.py -q`
- `python -m pytest engine/tests/ -q`
- `python -m ruff check engine/arc engine/telemetry engine/tests`
- `python -m ruff format --check engine/arc engine/telemetry engine/tests`
- `git diff --check`

---

# Risks And Unknowns

**Risks**:

- If derivation is added prematurely, AW-207 may hardcode Nightcap concepts and violate platform reuse boundaries.
- If the outcome is written by updating the original intervention event, telemetry would violate the append-only events-table contract.
- If the intervention descriptor is underspecified, the future coordinator and async loop will need a breaking interface change.

**Unknowns**:

- Exact event-type taxonomy for player action rate is deferred to the coordinator or event-system work.
- Exact knowledge graph queries for suspicion and clue coverage are deferred to later integration work.
- Exact timing ownership for `pacing_intervention_outcome` is deferred to the async pacing-loop implementation.

---

# Open Questions

None.
