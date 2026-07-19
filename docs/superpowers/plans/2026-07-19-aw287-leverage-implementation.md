# AW-287 Leverage (Resource/Effect Capability) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the generic resource/effect engine capability (`engine/resources/`) that AW-282's `InteractionRuntime` plugs into, configured by Nightcap as the six-effect Leverage launch set, per spec 0075's runtime contract.

**Architecture:** Mirrors `engine/interactions/` (AW-282) exactly: a `models.py` for Pydantic schemas, a `resolver.py` (analogous to `director.py`) owning targeting eligibility and deterministic effect resolution, a `runtime.py` orchestrating session-facing calls, `events.py` building `ContentEvent`s through the existing `AudienceTarget`/`EventCategory` enums (no new audience primitive), and `errors.py`. No Nightcap-specific name appears in `engine/`; Nightcap's six effects are configured as data (an `EffectDefinition` list) passed in by the arc, the same way AW-282 takes `arc_definition.interactions`.

**Tech Stack:** Python 3.11+, Pydantic v2 (matching `engine/interactions/models.py`'s `ConfigDict(extra="forbid")` style), pytest.

**User decisions (already made):** All resolved in spec 0075 / ADR-0015 — public balances, per-question reveal timing, Sting-Operation-exception, cross-beat persistence with bank cap, per-effect visibility, Call Their Bluff replaced by Make Them Wait, generic engine naming with Nightcap-only configuration naming. No further founder input needed to write this plan; the founder still needs to approve the built thin slice (Task "present thin slice" in the completion roadmap) before this task closes.

---

## File Structure

- `engine/resources/__init__.py` — empty, matches `engine/interactions/__init__.py` convention.
- `engine/resources/models.py` — `ResourceBalance`, `ResourceGrant`, `ResourceSpend`, `EffectFamily` (enum), `EffectDefinition`, `EffectActivation`, `TargetEligibilityResult`.
- `engine/resources/errors.py` — `ResourceError` base, `InsufficientBalanceError`, `TargetIneligibleError`, `UnknownEffectError`.
- `engine/resources/resolver.py` — `ResourceResolver`: balance grant/spend, targeting eligibility checks (the four-guardrail chain from spec 0075), deterministic effect application per family.
- `engine/resources/events.py` — `build_balance_changed_event`, `build_effect_outcome_event`, `build_source_reveal_event`.
- `engine/resources/runtime.py` — `ResourceRuntime`: session-facing orchestration wrapping `ResourceResolver`, called from `InteractionRuntime` at the points spec 0075 specifies (before/after `lock_window`).
- `engine/tests/test_resources_models.py`, `test_resources_resolver.py`, `test_resources_events.py`, `test_resources_runtime.py`, `test_resources_integration.py`, `test_resources_naming_contract.py` (the repo-wide generic-naming grep test).
- Nightcap configuration: extend `engine/arc/models.py`'s `ArcDefinition` with an optional `resource_effects: tuple[EffectDefinition, ...] = ()` field (empty by default — "games without Leverage configuration remain unaffected"), and add the six launch-set `EffectDefinition` instances to the Nightcap Couch Race arc configuration module (wherever `arc_definition.interactions` for Couch Race is currently assembled — locate via Task 1's grounding step).

---

## Task 1: Locate the Nightcap Couch Race arc configuration assembly point

**Goal:** Find the exact file/function where the Couch Race `ArcDefinition` is assembled (where AW-282's `interactions` list is populated), so the new `resource_effects` field has a concrete home.

**Files:** Read-only.

**Acceptance Criteria:**
- [ ] Exact file:function identified where `ArcDefinition(interactions=...)` is constructed for Couch Race.
- [ ] Confirm `ArcDefinition` is a Pydantic model that accepts new optional fields without breaking other games (default empty tuple).

**Verify:** N/A (grounding task).

**Steps:**

- [ ] **Step 1:** `grep -rn "ArcDefinition(" engine/ --include=*.py | grep -v test` to find construction sites.
- [ ] **Step 2:** Read `engine/arc/models.py` for `ArcDefinition`'s current field list and confirm it uses `ConfigDict(extra="forbid")` or similar, so the new field must be added there explicitly (not passed via kwargs).
- [ ] **Step 3:** No commit — grounding only.

---

## Task 2: Resource and effect schemas

**Goal:** Define the Pydantic models for balances, grants/spends, and effect definitions/activations.

**Files:**
- Create: `engine/resources/__init__.py` (empty)
- Create: `engine/resources/models.py`
- Test: `engine/tests/test_resources_models.py`

**Acceptance Criteria:**
- [ ] `ResourceBalance`, `ResourceGrant`, `ResourceSpend`, `EffectFamily`, `EffectDefinition`, `EffectActivation` all defined with `ConfigDict(extra="forbid")`.
- [ ] `ResourceBalance.current_amount` cannot go negative or above `bank_cap` at the model level is NOT enforced here (that's the resolver's job, since it needs atomic check-and-apply); the model only validates `bank_cap >= protected_floor >= 0`.
- [ ] `EffectActivation.source_reveal_at` defaults to `None`.

**Verify:** `pytest engine/tests/test_resources_models.py -v`

**Steps:**

- [ ] **Step 1: Write the failing tests**

```python
# engine/tests/test_resources_models.py
import pytest
from pydantic import ValidationError
from engine.resources.models import (
    EffectActivation,
    EffectDefinition,
    EffectFamily,
    ResourceBalance,
)


def test_resource_balance_rejects_floor_above_cap():
    with pytest.raises(ValidationError):
        ResourceBalance(
            player_id="p1", session_id="s1",
            current_amount=0, bank_cap=5, protected_floor=6,
        )


def test_resource_balance_defaults():
    balance = ResourceBalance(player_id="p1", session_id="s1", bank_cap=20, protected_floor=0)
    assert balance.current_amount == 0


def test_effect_activation_reveal_defaults_none():
    activation = EffectActivation(
        effect_key="sabotage.rattle_the_witness",
        activator_id="p1",
        target_id="p2",
        interaction_window_id="w1",
    )
    assert activation.source_reveal_at is None


def test_effect_definition_rejects_unknown_family():
    with pytest.raises(ValidationError):
        EffectDefinition(
            effect_key="advantage.deep_read",
            family="not-a-family",
            cost=2,
            requires_target=False,
        )
```

- [ ] **Step 2:** Run: `pytest engine/tests/test_resources_models.py -v` — expect FAIL (`ModuleNotFoundError: engine.resources`).

- [ ] **Step 3: Write the implementation**

```python
# engine/resources/models.py
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EffectFamily(str, Enum):
    insight = "insight"
    access = "access"
    tempo = "tempo"
    counterplay = "counterplay"
    risk_and_reward = "risk_and_reward"
    witness_pressure = "witness_pressure"
    information_control = "information_control"
    economy = "economy"
    mind_game = "mind_game"


class ResourceBalance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    current_amount: int = Field(default=0, ge=0)
    bank_cap: int = Field(ge=0)
    protected_floor: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_floor_below_cap(self) -> "ResourceBalance":
        if self.protected_floor > self.bank_cap:
            raise ValueError("protected_floor cannot exceed bank_cap")
        return self


class ResourceGrant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    amount: int = Field(gt=0)
    source: str | None = None
    beat_id: str = Field(min_length=1)
    timestamp: datetime


class ResourceSpend(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    amount: int = Field(gt=0)
    effect_key: str = Field(min_length=1)
    beat_id: str = Field(min_length=1)
    timestamp: datetime


class EffectDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    effect_key: str = Field(min_length=1)
    family: EffectFamily
    cost: int = Field(gt=0)
    requires_target: bool
    is_offensive: bool = False
    is_information_control: bool = False


class EffectActivation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    effect_key: str = Field(min_length=1)
    activator_id: str = Field(min_length=1)
    target_id: str | None = None
    interaction_window_id: str = Field(min_length=1)
    resolved_at: datetime | None = None
    source_reveal_at: datetime | None = None
```

- [ ] **Step 4:** Run: `pytest engine/tests/test_resources_models.py -v` — expect PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/resources/__init__.py engine/resources/models.py engine/tests/test_resources_models.py
git commit -m "feat(resources): add generic resource/effect schemas"
```

---

## Task 3: Targeting eligibility and the danger-combination guardrails

**Goal:** Implement the four-check eligibility chain from spec 0075 (balance sufficiency, post-target protection, one-offensive-modifier-per-interaction, one-information-control-sabotage-per-target-per-beat).

**Files:**
- Create: `engine/resources/errors.py`
- Modify: `engine/resources/resolver.py` (new file)
- Test: `engine/tests/test_resources_resolver.py`

**Acceptance Criteria:**
- [ ] Each of the four checks is independently testable and rejects deterministically with a typed error.
- [ ] A second offensive modifier on the same interaction window is rejected.
- [ ] A second information-control sabotage on the same target within the same beat is rejected.
- [ ] A target under an active post-target protection window rejects a new sabotage; protection clears once another player is targeted or a new interaction window opens.

**Verify:** `pytest engine/tests/test_resources_resolver.py -v`

**Steps:**

- [ ] **Step 1: Write the failing tests**

```python
# engine/tests/test_resources_resolver.py
import pytest
from datetime import datetime, timezone
from engine.resources.errors import InsufficientBalanceError, TargetIneligibleError
from engine.resources.models import EffectDefinition, EffectFamily, ResourceBalance
from engine.resources.resolver import ResourceResolver

NOW = datetime(2026, 7, 19, tzinfo=timezone.utc)


def make_resolver():
    resolver = ResourceResolver()
    resolver.set_balance(ResourceBalance(player_id="p1", session_id="s1", current_amount=5, bank_cap=20, protected_floor=0))
    resolver.set_balance(ResourceBalance(player_id="p2", session_id="s1", current_amount=5, bank_cap=20, protected_floor=0))
    return resolver


RATTLE = EffectDefinition(effect_key="sabotage.rattle_the_witness", family=EffectFamily.witness_pressure, cost=2, requires_target=True, is_offensive=True)
LISTEN_IN = EffectDefinition(effect_key="sabotage.listen_in", family=EffectFamily.information_control, cost=2, requires_target=True, is_offensive=True, is_information_control=True)


def test_rejects_insufficient_balance():
    resolver = make_resolver()
    expensive = EffectDefinition(effect_key="advantage.sting_operation", family=EffectFamily.counterplay, cost=99, requires_target=False)
    with pytest.raises(InsufficientBalanceError):
        resolver.activate(effect=expensive, activator_id="p1", target_id=None, window_id="w1", beat_id="b1", now=NOW)


def test_rejects_second_offensive_modifier_same_window():
    resolver = make_resolver()
    resolver.activate(effect=RATTLE, activator_id="p1", target_id="p2", window_id="w1", beat_id="b1", now=NOW)
    resolver.set_balance(ResourceBalance(player_id="p1", session_id="s1", current_amount=5, bank_cap=20, protected_floor=0))
    with pytest.raises(TargetIneligibleError):
        resolver.activate(effect=LISTEN_IN, activator_id="p1", target_id="p2", window_id="w1", beat_id="b1", now=NOW)


def test_rejects_second_info_control_sabotage_same_beat():
    resolver = make_resolver()
    resolver.activate(effect=LISTEN_IN, activator_id="p1", target_id="p2", window_id="w1", beat_id="b1", now=NOW)
    resolver.set_balance(ResourceBalance(player_id="p1", session_id="s1", current_amount=5, bank_cap=20, protected_floor=0))
    with pytest.raises(TargetIneligibleError):
        resolver.activate(effect=LISTEN_IN, activator_id="p1", target_id="p2", window_id="w2", beat_id="b1", now=NOW)


def test_post_target_protection_clears_on_new_target():
    resolver = make_resolver()
    resolver.activate(effect=RATTLE, activator_id="p1", target_id="p2", window_id="w1", beat_id="b1", now=NOW)
    resolver.set_balance(ResourceBalance(player_id="p1", session_id="s1", current_amount=5, bank_cap=20, protected_floor=0))
    with pytest.raises(TargetIneligibleError):
        resolver.activate(effect=RATTLE, activator_id="p1", target_id="p2", window_id="w2", beat_id="b1", now=NOW)
    resolver.set_balance(ResourceBalance(player_id="p3", session_id="s1", current_amount=5, bank_cap=20, protected_floor=0))
    resolver.activate(effect=RATTLE, activator_id="p1", target_id="p3", window_id="w3", beat_id="b1", now=NOW)
```

- [ ] **Step 2:** Run tests — expect FAIL (`ModuleNotFoundError`).

- [ ] **Step 3: Write the implementation**

```python
# engine/resources/errors.py
from __future__ import annotations


class ResourceError(Exception):
    """Base error for deterministic resource/effect resolution failures."""


class InsufficientBalanceError(ResourceError):
    """Raised when a spend would exceed available balance or breach the protected floor."""


class TargetIneligibleError(ResourceError):
    """Raised when a target fails a targeting-eligibility guardrail check."""


class UnknownEffectError(ResourceError):
    """Raised when an effect_key has no registered EffectDefinition."""
```

```python
# engine/resources/resolver.py
from __future__ import annotations

from datetime import datetime

from engine.resources.errors import InsufficientBalanceError, TargetIneligibleError
from engine.resources.models import EffectActivation, EffectDefinition, ResourceBalance


class ResourceResolver:
    """Owns balance state, targeting eligibility, and deterministic effect application."""

    def __init__(self) -> None:
        self._balances: dict[str, ResourceBalance] = {}
        self._activations: list[EffectActivation] = []
        self._protected_until_retarget: dict[str, str] = {}  # target_id -> window_id that protects them
        self._offensive_modifiers_by_window: dict[str, int] = {}
        self._info_control_targets_this_beat: dict[tuple[str, str], int] = {}  # (target_id, beat_id) -> count

    def set_balance(self, balance: ResourceBalance) -> None:
        self._balances[balance.player_id] = balance

    def get_balance(self, player_id: str) -> ResourceBalance:
        return self._balances[player_id]

    def activate(
        self,
        *,
        effect: EffectDefinition,
        activator_id: str,
        target_id: str | None,
        window_id: str,
        beat_id: str,
        now: datetime,
    ) -> EffectActivation:
        balance = self._balances[activator_id]
        if balance.current_amount - effect.cost < 0:
            raise InsufficientBalanceError(f"{activator_id} cannot afford {effect.effect_key}")
        if balance.current_amount - effect.cost < balance.protected_floor:
            raise InsufficientBalanceError(f"{activator_id} spend would breach protected floor")

        if target_id is not None and effect.is_offensive:
            if self._protected_until_retarget.get(target_id) == target_id:
                raise TargetIneligibleError(f"{target_id} is under post-target protection")
            if self._offensive_modifiers_by_window.get(window_id, 0) >= 1:
                raise TargetIneligibleError(f"window {window_id} already carries an offensive modifier")
            if effect.is_information_control:
                key = (target_id, beat_id)
                if self._info_control_targets_this_beat.get(key, 0) >= 1:
                    raise TargetIneligibleError(f"{target_id} already received an information-control sabotage this beat")

        self._balances[activator_id] = balance.model_copy(update={"current_amount": balance.current_amount - effect.cost})

        if target_id is not None and effect.is_offensive:
            self._offensive_modifiers_by_window[window_id] = self._offensive_modifiers_by_window.get(window_id, 0) + 1
            if effect.is_information_control:
                key = (target_id, beat_id)
                self._info_control_targets_this_beat[key] = self._info_control_targets_this_beat.get(key, 0) + 1
            self._protected_until_retarget[target_id] = target_id

        activation = EffectActivation(
            effect_key=effect.effect_key,
            activator_id=activator_id,
            target_id=target_id,
            interaction_window_id=window_id,
        )
        self._activations.append(activation)
        return activation

    def clear_protection(self, previous_target_id: str) -> None:
        """Call when a new target is selected — clears the prior target's protection."""
        self._protected_until_retarget.pop(previous_target_id, None)
```

- [ ] **Step 4:** Run: `pytest engine/tests/test_resources_resolver.py -v` — expect PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/resources/errors.py engine/resources/resolver.py engine/tests/test_resources_resolver.py
git commit -m "feat(resources): targeting eligibility and danger-combination guardrails"
```

---

## Task 4: Reveal timing (per-question, Sting Operation exception) and resolution completion

**Goal:** Implement `resolve_activation` — marks an activation resolved and sets `source_reveal_at` per spec 0075's timing rule, with Sting Operation's immediate/private exception.

**Files:**
- Modify: `engine/resources/resolver.py`
- Test: `engine/tests/test_resources_resolver.py` (append)

**Acceptance Criteria:**
- [ ] A non-Sting-Operation sabotage's `source_reveal_at` is `None` until `resolve_activation` is called for that specific `window_id` (per-question, not per-round — a second queued question for the same target does not trigger reveal).
- [ ] Calling `resolve_activation` for a Sting Operation counter sets the countered sabotage's `source_reveal_at` immediately upon the Sting Operation's own activation, not upon the countered interaction's resolution.

**Verify:** `pytest engine/tests/test_resources_resolver.py -v`

**Steps:**

- [ ] **Step 1: Write the failing test**

```python
def test_reveal_fires_on_resolve_not_on_activation():
    resolver = make_resolver()
    activation = resolver.activate(effect=RATTLE, activator_id="p1", target_id="p2", window_id="w1", beat_id="b1", now=NOW)
    assert activation.source_reveal_at is None
    resolved = resolver.resolve_activation(window_id="w1", now=NOW)
    assert resolved.source_reveal_at == NOW


def test_reveal_is_per_question_not_per_round():
    resolver = make_resolver()
    resolver.activate(effect=RATTLE, activator_id="p1", target_id="p2", window_id="w1", beat_id="b1", now=NOW)
    resolver.set_balance(ResourceBalance(player_id="p3", session_id="s1", current_amount=5, bank_cap=20, protected_floor=0))
    other = resolver.activate(effect=RATTLE, activator_id="p3", target_id="p2", window_id="w2", beat_id="b1", now=NOW)
    # w2 fails eligibility (post-target protection from w1) — this call should have raised;
    # this test documents that a *different* target's second question in the same round
    # does not retroactively reveal w1's source. Re-target to p4 to isolate the reveal-scope check:
```

(Note: the second scenario above is subsumed by `test_post_target_protection_clears_on_new_target` from Task 3 — the reveal-scope claim is fully covered by `test_reveal_fires_on_resolve_not_on_activation` plus the integration test in Task 6, which queues two *different* targets' questions in one round and asserts only the resolved one reveals. Do not duplicate; keep this task's test to the single case above.)

- [ ] **Step 2:** Run — expect FAIL (`AttributeError: resolve_activation`).

- [ ] **Step 3: Implement**

```python
# append to ResourceResolver in engine/resources/resolver.py

    def resolve_activation(self, *, window_id: str, now: datetime) -> EffectActivation:
        for i, activation in enumerate(self._activations):
            if activation.interaction_window_id == window_id and activation.resolved_at is None:
                resolved = activation.model_copy(update={"resolved_at": now, "source_reveal_at": now})
                self._activations[i] = resolved
                return resolved
        raise ValueError(f"no unresolved activation for window {window_id}")

    def counter_with_sting_operation(self, *, sting_activator_id: str, countered_window_id: str, now: datetime) -> EffectActivation:
        """Sting Operation's exception: reveal the countered sabotage's source immediately, private to the Sting Operation user."""
        for i, activation in enumerate(self._activations):
            if activation.interaction_window_id == countered_window_id:
                revealed = activation.model_copy(update={"source_reveal_at": now})
                self._activations[i] = revealed
                return revealed
        raise ValueError(f"no activation to counter for window {countered_window_id}")
```

- [ ] **Step 4:** Run — expect PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/resources/resolver.py engine/tests/test_resources_resolver.py
git commit -m "feat(resources): per-question reveal timing and Sting Operation exception"
```

---

## Task 5: ContentEvent emission (public balances, per-effect outcome audience)

**Goal:** Build the `ContentEvent` factories for balance changes and effect outcomes, routed through the existing `AudienceTarget`/`EventCategory` enums per each effect's documented visibility.

**Files:**
- Create: `engine/resources/events.py`
- Test: `engine/tests/test_resources_events.py`

**Acceptance Criteria:**
- [ ] Balance-changed events always use `AudienceTarget.all`.
- [ ] Listen In's copied-content event uses `AudienceTarget.specific_player` targeting the saboteur only.
- [ ] Sting Operation's source-exposure event uses `AudienceTarget.specific_player` targeting the Sting Operation user only — never `AudienceTarget.all`.
- [ ] Rattle the Witness / Make Them Wait outcome events use `AudienceTarget.all` (they modify something already public).

**Verify:** `pytest engine/tests/test_resources_events.py -v`

**Steps:**

- [ ] **Step 1: Write the failing tests**

```python
# engine/tests/test_resources_events.py
from datetime import datetime, timezone
from engine.events.models import AudienceTarget
from engine.resources.events import (
    build_balance_changed_event,
    build_effect_outcome_event,
    build_source_reveal_event,
)

NOW = datetime(2026, 7, 19, tzinfo=timezone.utc)


def test_balance_changed_is_public():
    event = build_balance_changed_event(session_id="s1", player_id="p1", new_amount=8, timestamp=NOW)
    assert event.target_audience == AudienceTarget.all


def test_listen_in_outcome_is_private_to_saboteur():
    event = build_effect_outcome_event(
        session_id="s1", effect_key="sabotage.listen_in", outcome_payload={"copied": "..."},
        audience=AudienceTarget.specific_player, recipient_id="saboteur-1", timestamp=NOW,
    )
    assert event.target_audience == AudienceTarget.specific_player


def test_sting_operation_reveal_is_private_to_user_not_table():
    event = build_source_reveal_event(
        session_id="s1", revealed_source_id="p2", recipient_id="sting-user-1", timestamp=NOW,
    )
    assert event.target_audience == AudienceTarget.specific_player
```

- [ ] **Step 2:** Run — expect FAIL.

- [ ] **Step 3: Implement** (mirrors `engine/interactions/events.py`'s factory style)

```python
# engine/resources/events.py
from __future__ import annotations

from datetime import datetime
from typing import Any

from engine.events.models import AudienceTarget, ContentEvent, EventCategory


def build_balance_changed_event(*, session_id: str, player_id: str, new_amount: int, timestamp: datetime) -> ContentEvent:
    return ContentEvent(
        session_id=session_id,
        timestamp=timestamp,
        category=EventCategory.state_transition,
        event_type="resource_balance_changed",
        actor_id=player_id,
        target_audience=AudienceTarget.all,
        payload={"player_id": player_id, "current_amount": new_amount},
    )


def build_effect_outcome_event(
    *, session_id: str, effect_key: str, outcome_payload: dict[str, Any],
    audience: AudienceTarget, recipient_id: str | None, timestamp: datetime,
) -> ContentEvent:
    return ContentEvent(
        session_id=session_id,
        timestamp=timestamp,
        category=EventCategory.private_delivery if audience == AudienceTarget.specific_player else EventCategory.state_transition,
        event_type="resource_effect_outcome",
        target_audience=audience,
        payload={"effect_key": effect_key, "recipient_id": recipient_id, "outcome": outcome_payload},
    )


def build_source_reveal_event(*, session_id: str, revealed_source_id: str, recipient_id: str, timestamp: datetime) -> ContentEvent:
    return ContentEvent(
        session_id=session_id,
        timestamp=timestamp,
        category=EventCategory.private_delivery,
        event_type="resource_effect_source_revealed",
        target_audience=AudienceTarget.specific_player,
        payload={"revealed_source_id": revealed_source_id, "recipient_id": recipient_id},
    )
```

- [ ] **Step 4:** Run — expect PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/resources/events.py engine/tests/test_resources_events.py
git commit -m "feat(resources): ContentEvent factories for balances and effect outcomes"
```

---

## Task 6: ResourceRuntime orchestration, integration with InteractionRuntime, and audience-filtering integration test

**Goal:** Wire `ResourceResolver` + events into a session-facing `ResourceRuntime`, and prove per-question reveal scope, Sting Operation privacy, and public-balance visibility end-to-end.

**Files:**
- Create: `engine/resources/runtime.py`
- Test: `engine/tests/test_resources_runtime.py`, `engine/tests/test_resources_integration.py`

**Acceptance Criteria:**
- [ ] `ResourceRuntime.activate_effect(...)` returns both the `EffectActivation` and the list of `ContentEvent`s to publish.
- [ ] Integration test: two questions queued for the same target in one round; only the resolved one's reveal fires (extends Task 4's per-question claim to a full round scenario, per the walkthrough's resolved judgment call).
- [ ] Integration test: Sting Operation counter never appears in any `AudienceTarget.all` event payload.
- [ ] Existing AW-230/AW-282 privacy-matrix test harness extended with these new event types (import and reuse, do not duplicate the harness).

**Verify:** `pytest engine/tests/test_resources_runtime.py engine/tests/test_resources_integration.py -v`

**Steps:**

- [ ] **Step 1:** Read `engine/tests/test_interactions_integration.py` for the existing privacy-matrix harness pattern to reuse.
- [ ] **Step 2:** Write `ResourceRuntime` wrapping `ResourceResolver`, exposing `activate_effect`, `resolve_window`, `counter_with_sting_operation`, each returning `(EffectActivation, list[ContentEvent])`.
- [ ] **Step 3:** Write the two integration tests described in Acceptance Criteria, following the existing harness's assertion style (iterate emitted events, assert `target_audience` per event, assert no private payload leaks into an `AudienceTarget.all` event).
- [ ] **Step 4:** Run: `pytest engine/tests/test_resources_runtime.py engine/tests/test_resources_integration.py -v` — expect PASS.
- [ ] **Step 5: Commit**

```bash
git add engine/resources/runtime.py engine/tests/test_resources_runtime.py engine/tests/test_resources_integration.py
git commit -m "feat(resources): session runtime orchestration and privacy-matrix integration tests"
```

---

## Task 7: Determinism (seeded replay) and generic-naming enforcement tests

**Goal:** Prove a seeded replay produces identical state, and add the repo-wide test that no Nightcap-specific term appears in `engine/resources/`.

**Files:**
- Test: `engine/tests/test_resources_integration.py` (append), `engine/tests/test_resources_naming_contract.py`

**Acceptance Criteria:**
- [ ] Two runs of the same activation sequence with the same seed/inputs produce byte-identical `ResourceBalance` and `EffectActivation` state.
- [ ] A grep-based test fails the build if `engine/resources/` contains "leverage", "deep_read", "sting_operation", or any of the other five effect names as Python identifiers (class/function/variable names) — Nightcap names may only appear inside string literals used as `effect_key` values (already the pattern used in the tests above), never as identifiers.

**Verify:** `pytest engine/tests/test_resources_integration.py::test_seeded_replay_is_deterministic engine/tests/test_resources_naming_contract.py -v`

**Steps:**

- [ ] **Step 1: Write the determinism test** — run an identical sequence of `activate`/`resolve_activation` calls through two fresh `ResourceResolver` instances, assert equal final state.
- [ ] **Step 2: Write the naming-contract test**

```python
# engine/tests/test_resources_naming_contract.py
import ast
from pathlib import Path

FORBIDDEN_IDENTIFIER_TERMS = ["leverage", "deep_read", "follow_the_thread", "sting_operation", "rattle_the_witness", "listen_in", "make_them_wait"]


def test_no_nightcap_terms_in_engine_resources_identifiers():
    for path in Path("engine/resources").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            name = getattr(node, "id", None) or getattr(node, "name", None) or getattr(node, "attr", None)
            if name is None:
                continue
            lowered = name.lower()
            for term in FORBIDDEN_IDENTIFIER_TERMS:
                assert term.replace("_", "") not in lowered.replace("_", ""), (
                    f"{path}: identifier {name!r} contains forbidden Nightcap-specific term {term!r}"
                )
```

- [ ] **Step 3:** Run both tests — expect PASS (confirms Tasks 2-6 never leaked a Nightcap name into an identifier).
- [ ] **Step 4: Commit**

```bash
git add engine/tests/test_resources_integration.py engine/tests/test_resources_naming_contract.py
git commit -m "test(resources): seeded-replay determinism and generic-naming enforcement"
```

---

## Task 8: Nightcap configuration — the six launch-set EffectDefinitions and ArcDefinition wiring

**Goal:** Wire the generic capability into Nightcap: extend `ArcDefinition` with the optional `resource_effects` field, and configure the six launch-set effects for the Couch Race arc.

**Files:**
- Modify: `engine/arc/models.py` (add `resource_effects: tuple[EffectDefinition, ...] = ()` to `ArcDefinition`)
- Modify: the Couch Race arc configuration module located in Task 1
- Test: `engine/tests/test_resources_integration.py` (append: arc without `resource_effects` behaves identically to before this change)

**Acceptance Criteria:**
- [ ] `ArcDefinition` accepts `resource_effects` as optional, default empty.
- [ ] Existing AW-281/AW-282 tests pass unmodified (proves "games without Leverage configuration remain unaffected").
- [ ] Couch Race arc configuration lists exactly six `EffectDefinition`s matching spec 0075's effect-definition table (costs are implementation-plan tuning values — pick reasonable starting values, e.g. 2-3 per effect, and note in a comment that rehearsal telemetry will tune them).

**Verify:** `pytest engine/tests/ -k "resources or interactions or couch_race" -v`

**Steps:**

- [ ] **Step 1:** Add the field to `ArcDefinition` per Task 1's findings.
- [ ] **Step 2:** Add the six `EffectDefinition` instances to the Couch Race arc configuration, using the exact `effect_key` values from spec 0075's table (`advantage.deep_read`, `advantage.follow_the_thread`, `advantage.sting_operation`, `sabotage.rattle_the_witness`, `sabotage.listen_in`, `sabotage.make_them_wait`).
- [ ] **Step 3:** Run the full existing engine test suite to confirm no regression: `pytest engine/tests/ -v`.
- [ ] **Step 4: Commit**

```bash
git add engine/arc/models.py <couch-race-arc-config-path>
git commit -m "feat(nightcap): configure the six Leverage launch-set effects on the Couch Race arc"
```

---

## Task 9: Bank cap / protected floor / mini-game grant path tuning test and telemetry

**Goal:** Prove the "mini-game rewards cannot create an unrecoverable lead" and "every player has a protected earn path" guardrails hold over a seeded multi-beat session, and emit telemetry per spec 0075.

**Files:**
- Modify: `engine/resources/runtime.py` (telemetry emission on grant/spend/target/outcome/counterplay/recovery)
- Test: `engine/tests/test_resources_integration.py` (append)

**Acceptance Criteria:**
- [ ] A seeded multi-beat test where one player wins every mini-game still leaves every other player able to reach the protected floor by session end.
- [ ] Telemetry events emitted for grants, spends, targets, outcomes, counterplay, and recovery, with no private-content field (assert payload keys against an explicit allowlist).

**Verify:** `pytest engine/tests/test_resources_integration.py -v`

**Steps:**

- [ ] **Step 1:** Write the multi-beat guardrail test and the telemetry-payload allowlist test.
- [ ] **Step 2:** Add telemetry emission calls at each of the six lifecycle points in `ResourceRuntime`, reusing the existing telemetry sink pattern from `engine/architecture/11-telemetry.md` / however AW-282 already emits telemetry (check `engine/interactions/runtime.py` for the pattern first).
- [ ] **Step 3:** Run: `pytest engine/tests/test_resources_integration.py -v` — expect PASS.
- [ ] **Step 4: Commit**

```bash
git add engine/resources/runtime.py engine/tests/test_resources_integration.py
git commit -m "feat(resources): telemetry emission and protected-earn-path guardrail test"
```

---

## Task 10: Full suite, lint, and thin-slice script for founder review

**Goal:** Run the complete verification suite and produce a runnable thin-slice script matching the approved walkthrough scenario, for the founder-approval gate.

**Files:**
- Create: `engine/scripts/leverage_thin_slice_demo.py` (or equivalent existing scripts location — check `engine/` for a `scripts/` convention first) — a runnable script replaying the walkthrough's six steps and printing each `ContentEvent`'s audience and payload.

**Acceptance Criteria:**
- [ ] `pytest engine/tests/ -v` fully green.
- [ ] `python -m ruff check engine api` and `python -m ruff format --check engine api` clean.
- [ ] The demo script's output matches the walkthrough document's six steps (Priya's Deep Read, Marcus's Rattle the Witness on Jordan, the post-target protection rejection, Zoe's Sting Operation, Priya's weakened/exposed Listen In on Zoe, beat transition balance persistence).

**Verify:** `pytest engine/tests/ -v && python -m ruff check engine api && python -m ruff format --check engine api`

**Steps:**

- [ ] **Step 1:** Check for an existing `engine/scripts/` or similar demo-script convention; follow it if present, otherwise place the script at `engine/resources/demo.py` with a `if __name__ == "__main__":` guard.
- [ ] **Step 2:** Run the full verification command above.
- [ ] **Step 3:** Fix any failures found; do not proceed to the founder-approval gate with red tests.
- [ ] **Step 4: Commit**

```bash
git add engine/resources/demo.py  # or engine/scripts/leverage_thin_slice_demo.py
git commit -m "feat(resources): thin-slice demo script for AW-287 founder review"
```

- [ ] **Step 5:** This is the implementation's stopping point. Task 18 in the completion roadmap (present thin slice, get explicit founder approval, then sign-off/PR) picks up from here — do not record sign-off or open the PR from this plan.
