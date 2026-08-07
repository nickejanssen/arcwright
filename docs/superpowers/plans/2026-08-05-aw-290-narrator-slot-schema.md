# AW-290 Narrator Slot Schema Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give narrator refrain slots typed sources to resolve from — a shared anchor value object for location and time, a generated evidence short form, a per-wrapper dressing pack, a machine-readable slot registry, and normalized case persistence.

**Architecture:** `engine/case/` stays a pure Pydantic module with zero DB coupling; anchors are a value object declared once on `ResolvedCase` and referenced by id, and prose is generated *from* anchors so it never has to be parsed back. Persistence lives in a separate `engine/session/case_store.py` following the existing pure-module-plus-sibling-persister pattern (`engine/resources/` → `engine/telemetry/resources.py`). Dressing vocabulary is game content in `nightcap/`, never a schema field name in `engine/`.

**Tech Stack:** Python 3.11+, Pydantic v2 (`extra="forbid"` on every case model), SQLAlchemy 2.0 async (`Mapped` / `mapped_column`), Alembic, pytest + pytest-asyncio, SQLite in-memory for table tests via `engine/db/testing.py`.

**User decisions (already made):**
- Spec 0087 approved 2026-08-05, conditional on Q1–Q3 being resolved first. Migration-design approval and dressing-content approval remain separate gates.
- **Q1:** case persistence uses `cases.session_id` FK NOT NULL, one case row per session. A case is not shared across sessions.
- **Q2:** the dressing pack declares all six wrappers, authors two (Séance 1928, Big Top 1899), and raises `DressingPackNotAuthored` vs `UnknownWrapper` as two distinct errors.
- **Q3:** the registry coverage test is a pytest in `engine/tests` reading a machine-readable registry file checked in under `nightcap/`.
- D-103 / ADR-0022: persistence is normalized into six tables, approved **in principle only**.
- Standing instruction: do not touch `run_seed` in any resolver — known gap, needs cross-module approval.

---

## Scope split

AW-290 is recorded as Size M. It is not. This plan implements it as four sub-tasks that ship independently. **Only 290a, 290c, and 290d are on the critical path to AW-291 and Rehearsal 1.** Persistence (290b) supplies no narrator slot and blocks nothing downstream.

| Sub-task | Content | Size | Gates |
|---|---|---|---|
| **290a** Typed anchors + short form | Tasks 1–4 | M | none beyond spec approval |
| **290c** Wrapper dressing pack | Tasks 5–7 | M | founder content approval (Task 5) |
| **290d** Registry + coverage test | Tasks 8–10 | S | line-library diff check (Task 10) |
| **290b** Case persistence | Tasks 11–14 | L | founder migration-design approval (Task 11) |

**Carved out entirely — not in this plan.** Wiring case resolution and persistence into `engine/session/service.py:start_session` so production actually writes these tables. It touches `engine/case`, `engine/session`, and `engine/db` together and is an `AGENTS.md` cross-module Hard Rule needing its own design review. See `docs/specs/0087-appendix-a-case-persistence-migration-design.md`.

**Dependency order:** 1 → 2 → 3 → 4, then 5 → 6 → 7, then 8 → 9 → 10. Task 11 gates 12 → 13 → 14. 290b may run in parallel with 290a/c/d.

---

# 290a — Typed anchors and evidence short form

### Task 1: `CaseAnchor` value object and model fields

**Goal:** Add the anchor value object and the optional anchor references, plus `EvidenceEntry.short_label`, to the pure Pydantic case models.

**Files:**
- Modify: `engine/case/models.py`
- Modify: `engine/case/__init__.py:26-55` (re-export `CaseAnchor`)
- Test: `engine/tests/test_case_models.py`

**Acceptance Criteria:**
- [ ] `CaseAnchor` exists with `anchor_id`, `location_ref`, `location_label`, `time_ordinal`, `time_label`, and `extra="forbid"`
- [ ] `ResolvedCase.anchors: list[CaseAnchor]` declares the per-case anchor set once
- [ ] `EvidenceEntry`, `CaseFact`, and `AuthorizedFalsehood` each carry `anchor_id: Optional[str] = None`
- [ ] `EvidenceEntry.short_label: str` is required
- [ ] `ResolvedCase.anchor_by_id()` returns the anchor or `None`
- [ ] Existing tests that construct these models still pass after being updated for the new required field

**Verify:** `python -m pytest engine/tests/test_case_models.py -v` → all pass

**Steps:**

- [ ] **Step 1: Write the failing tests**

Append to `engine/tests/test_case_models.py`:

```python
def test_case_anchor_carries_typed_location_and_ordered_time():
    anchor = CaseAnchor(
        anchor_id="a1",
        location_ref="loc_study",
        location_label="the study",
        time_ordinal=2,
        time_label="just after nine",
    )
    assert anchor.time_ordinal == 2
    assert anchor.location_ref == "loc_study"


def test_case_anchor_forbids_extra_fields():
    with pytest.raises(ValidationError):
        CaseAnchor(
            anchor_id="a1",
            location_ref="loc_study",
            location_label="the study",
            time_ordinal=2,
            time_label="just after nine",
            drink="gin rickey",
        )


def test_resolved_case_resolves_anchor_by_id():
    anchor = CaseAnchor(
        anchor_id="a1",
        location_ref="loc_study",
        location_label="the study",
        time_ordinal=2,
        time_label="just after nine",
    )
    case = _minimal_case(anchors=[anchor])
    assert case.anchor_by_id("a1") is anchor
    assert case.anchor_by_id("nope") is None


def test_evidence_entry_requires_short_label():
    with pytest.raises(ValidationError):
        EvidenceEntry(
            evidence_id="e1",
            evidence_type="trace",
            text="A cut-crystal glass, still wet, on the study desk.",
            points_toward=["s1"],
            points_away_from=[],
            delivery="group",
        )
```

Add a `_minimal_case` helper to the same file if one does not already exist, matching the construction style already used at `engine/tests/test_case_models.py:105`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest engine/tests/test_case_models.py -v -k "anchor or short_label"`
Expected: FAIL with `NameError: name 'CaseAnchor' is not defined`

- [ ] **Step 3: Add `CaseAnchor` to `engine/case/models.py`**

Insert immediately after the module imports (after line 13) and before `class CastMember`:

```python
class CaseAnchor(BaseModel):
    """A typed place-and-time reference shared across a resolved case.

    Declared once per case on ``ResolvedCase.anchors`` and referenced by
    ``anchor_id`` from evidence, facts, and falsehoods, so that comparing
    two statements about where and when is an exact comparison of typed
    values rather than a comparison of generated prose.

    ``time_ordinal`` indexes into the case's own ordered sequence of time
    anchors. It is self-describing within the case; there is no global
    clock and no cross-case comparability.
    """

    model_config = ConfigDict(extra="forbid")

    anchor_id: str
    """Unique within one case."""

    location_ref: str
    """Reference into the per-case location set. Compared by equality."""

    location_label: str
    """Display text. Never compared; only rendered."""

    time_ordinal: int
    """Orders this anchor against others in the same case. Compared by equality."""

    time_label: str
    """Display text. Never compared; only rendered."""
```

- [ ] **Step 4: Add `short_label` and `anchor_id` to `EvidenceEntry`**

In `engine/case/models.py`, add after the `text` field block (which ends at line 41):

```python
    short_label: str
    """Short reference to this clue, generated alongside ``text`` at case
    resolution. Not a truncation of ``text``: it names the object or
    observation in a few words so a narrator line can refer to the clue
    without reciting it."""

    anchor_id: Optional[str] = None
    """Optional CaseAnchor reference. Set when this clue is tied to a
    specific place and time."""
```

- [ ] **Step 5: Add `anchor_id` to `CaseFact` and `AuthorizedFalsehood`**

In `CaseFact`, after `known_by` (line 148):

```python
    anchor_id: Optional[str] = None
    """Optional CaseAnchor reference for facts that assert a place and time."""
```

In `AuthorizedFalsehood`, after `contradicted_by`:

```python
    anchor_id: Optional[str] = None
    """Optional CaseAnchor reference. For a ``location`` topic lie this is
    the place and time the speaker falsely claims, which is what makes the
    contradiction against anchored evidence a typed comparison."""
```

- [ ] **Step 6: Add `anchors` and `anchor_by_id` to `ResolvedCase`**

Add `anchors` to the field block (after `reveal_shape`, line 163):

```python
    anchors: list[CaseAnchor] = Field(default_factory=list)
    """The per-case anchor set, declared once. Evidence, facts, and
    falsehoods reference these by ``anchor_id``."""
```

Add the lookup method alongside `members_by_role`:

```python
    def anchor_by_id(self, anchor_id: str) -> Optional[CaseAnchor]:
        """Return the anchor with this id, or None if the case has no such anchor."""
        for anchor in self.anchors:
            if anchor.anchor_id == anchor_id:
                return anchor
        return None
```

- [ ] **Step 7: Re-export `CaseAnchor`**

In `engine/case/__init__.py`, add `CaseAnchor` to both the import block at lines 26-33 and the `__all__` list at lines 37-55, keeping alphabetical position consistent with the existing entries.

- [ ] **Step 8: Fix every existing `EvidenceEntry` construction**

`short_label` is required and every model uses `extra="forbid"`, so nothing can be added implicitly. Update all construction sites:
- `engine/case/resolver.py:369-378` and `engine/case/resolver.py:413-422` (handled properly in Task 2 — for now pass `short_label=""` to keep the suite green)
- `engine/tests/test_case_models.py` — lines 105, 147, 175, 198, 226, 271
- `engine/tests/test_case_invariants.py:62`
- `engine/tests/test_case_solver.py:134`
- `engine/tests/test_scoring_resolver.py:45`
- `engine/tests/test_scoring_integration.py:96`
- `engine/claims/evidence.py` — check for construction, it imports `EvidenceEntry` at `:10`

- [ ] **Step 9: Run the full case suite**

Run: `python -m pytest engine/tests/ -k "case or scoring or claims" -v`
Expected: all pass

- [ ] **Step 10: Commit**

```bash
git add engine/case/models.py engine/case/__init__.py engine/tests/
git commit -m "feat(case): add CaseAnchor value object, anchor refs, and evidence short_label"
```

---

### Task 2: Resolver generates anchors and derives prose from them

**Goal:** The resolver builds the per-case anchor set, assigns anchors, and generates evidence prose and lie text *from* the anchor, never parsing prose back into one.

**Files:**
- Modify: `engine/case/resolver.py`
- Test: `engine/tests/test_case_resolver.py`

**Acceptance Criteria:**
- [ ] `resolve()` populates `ResolvedCase.anchors` from the case taxonomy's location set and an ordered time list
- [ ] Anchor ids are unique within a case
- [ ] Every `EvidenceEntry` gets a non-empty `short_label` that is not a prefix of `text`
- [ ] Evidence and lie prose contain the anchor's `location_label` and `time_label` because they were generated from it
- [ ] The same seed produces the identical anchor set on every run
- [ ] `run_seed` is not touched anywhere in this task

**Verify:** `python -m pytest engine/tests/test_case_resolver.py -v` → all pass

**Steps:**

- [ ] **Step 1: Write the failing tests**

```python
def test_resolver_populates_unique_anchor_ids():
    case = resolve(_arc(), seed=4242, participant_ids=["p1", "p2", "p3"])
    ids = [a.anchor_id for a in case.anchors]
    assert ids
    assert len(ids) == len(set(ids))


def test_resolver_time_ordinals_order_within_case():
    case = resolve(_arc(), seed=4242, participant_ids=["p1", "p2", "p3"])
    ordinals = sorted(a.time_ordinal for a in case.anchors)
    assert ordinals == list(range(min(ordinals), min(ordinals) + len(ordinals)))


def test_every_evidence_entry_has_short_label_that_is_not_a_prefix_of_text():
    case = resolve(_arc(), seed=4242, participant_ids=["p1", "p2", "p3"])
    for entry in case.evidence:
        assert entry.short_label
        assert not entry.text.startswith(entry.short_label)


def test_anchored_prose_is_generated_from_the_anchor():
    case = resolve(_arc(), seed=4242, participant_ids=["p1", "p2", "p3"])
    anchored = [e for e in case.evidence if e.anchor_id is not None]
    assert anchored, "expected at least one anchored evidence entry"
    for entry in anchored:
        anchor = case.anchor_by_id(entry.anchor_id)
        assert anchor is not None
        assert anchor.location_label in entry.text
        assert anchor.time_label in entry.text


def test_anchor_set_is_deterministic_for_a_seed():
    a = resolve(_arc(), seed=99, participant_ids=["p1", "p2"])
    b = resolve(_arc(), seed=99, participant_ids=["p1", "p2"])
    assert [x.model_dump() for x in a.anchors] == [x.model_dump() for x in b.anchors]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest engine/tests/test_case_resolver.py -v -k anchor`
Expected: FAIL — `case.anchors` is empty

- [ ] **Step 3: Add the anchor builder to `engine/case/resolver.py`**

Add a private helper alongside the other `_resolve_*` functions:

```python
def _resolve_anchors(
    rng: random.Random,
    taxonomy: Any,
    count: int,
) -> list[CaseAnchor]:
    """Build the per-case anchor set from the taxonomy's place and time pools.

    Locations are drawn without replacement so two anchors never share a
    location_ref by accident; time ordinals are assigned densely from zero
    so they order within the case. Duplicate place-and-time pairs remain
    representable because callers may reuse an anchor_id.
    """
    places = list(taxonomy.location_pool)
    times = list(taxonomy.time_pool)
    if len(places) < count or len(times) < count:
        msg = (
            f"case taxonomy supplies {len(places)} locations and "
            f"{len(times)} times; need at least {count} of each"
        )
        raise CaseResolutionError(msg)

    chosen_places = rng.sample(places, count)
    chosen_times = rng.sample(times, count)
    chosen_times.sort(key=lambda t: times.index(t))

    return [
        CaseAnchor(
            anchor_id=f"a{i + 1}",
            location_ref=place["id"],
            location_label=place["label"],
            time_ordinal=i,
            time_label=chosen_times[i]["label"],
        )
        for i, place in enumerate(chosen_places)
    ]
```

The taxonomy needs `location_pool` and `time_pool`. If `nightcap/case_taxonomy/` has no such pools, add them there as arc content — **not** to `engine/case/`, which holds no game vocabulary. Confirm the taxonomy model in `engine/case/loader.py` permits the new keys; every case model uses `extra="forbid"`, so the loader model must gain the fields explicitly.

- [ ] **Step 4: Call it from `resolve()` and thread anchors through**

In `resolve()` (`engine/case/resolver.py:73-156`), after the cast is resolved and before `_resolve_evidence`, add:

```python
    anchors = _resolve_anchors(rng, taxonomy, count=len(suspects))
```

Pass `anchors` into `_resolve_evidence` and `_resolve_lies`, and add `anchors=anchors` to the `ResolvedCase(...)` construction at `engine/case/resolver.py:133-144`.

- [ ] **Step 5: Generate evidence prose from the anchor**

In `_resolve_evidence` (`engine/case/resolver.py:330-381`), assign an anchor per clue stage and build the text from it. Replace the stage-0 text line at `:358` and the later-stage line at `:364` with anchor-derived forms:

```python
        anchor = anchors[i % len(anchors)]
        if i == 0:
            text = (
                f"{prompt} ({trace} on the {descriptor}), "
                f"in {anchor.location_label}, {anchor.time_label}."
            )
        else:
            text = (
                f"{prompt} The {descriptor} traces back to "
                f"{culprit.display_name}, in {anchor.location_label}, "
                f"{anchor.time_label}."
            )
        short_label = f"the {descriptor} in {anchor.location_label}"
```

and add `short_label=short_label, anchor_id=anchor.anchor_id` to the `EvidenceEntry(...)` construction at `:369-378`.

- [ ] **Step 6: Anchor the location lies and their contradiction evidence**

In `_resolve_lies` (`engine/case/resolver.py:383-434`), when `topic == "location"`, give the falsehood one anchor and its contradiction evidence a **different** anchor with the same `time_ordinal` and a different `location_ref`. That is the pair Task 3 detects.

```python
        if topic == "location":
            claimed = anchors[i % len(anchors)]
            actual = next(
                (a for a in anchors if a.time_ordinal == claimed.time_ordinal
                 and a.location_ref != claimed.location_ref),
                None,
            )
            if actual is None:
                actual = CaseAnchor(
                    anchor_id=f"a_contra_{member.member_id}_{i}",
                    location_ref=claimed.location_ref + "_alt",
                    location_label=f"not {claimed.location_label}",
                    time_ordinal=claimed.time_ordinal,
                    time_label=claimed.time_label,
                )
                anchors.append(actual)
            lie_anchor_id = claimed.anchor_id
            contra_anchor_id = actual.anchor_id
        else:
            lie_anchor_id = None
            contra_anchor_id = None
```

Set `anchor_id=lie_anchor_id` on the `AuthorizedFalsehood(...)` at `:425-431`, and `anchor_id=contra_anchor_id` plus a `short_label` on the contradiction `EvidenceEntry(...)` at `:413-422`.

- [ ] **Step 7: Run the tests**

Run: `python -m pytest engine/tests/test_case_resolver.py engine/tests/test_case_property_sweep.py -v`
Expected: all pass

- [ ] **Step 8: Commit**

```bash
git add engine/case/resolver.py engine/case/loader.py nightcap/case_taxonomy/ engine/tests/
git commit -m "feat(case): resolve typed anchors and generate clue prose from them"
```

---

### Task 3: Anchor-based contradiction detection

**Goal:** Prove a location alibi contradiction is detected by comparing typed anchor fields, with no string matching anywhere in the comparison.

**Files:**
- Create: `engine/case/contradiction.py`
- Test: `engine/tests/test_case_contradiction.py`

**Acceptance Criteria:**
- [ ] `find_anchor_contradictions(case)` returns `(falsehood_id, evidence_id)` pairs
- [ ] A pair is returned when the two anchors share `time_ordinal` and differ on `location_ref`
- [ ] No pair is returned when both anchors agree
- [ ] The implementation contains no substring, regex, or `in`-on-string operation
- [ ] A resolved case from `resolve()` yields at least one detected contradiction

**Verify:** `python -m pytest engine/tests/test_case_contradiction.py -v` → all pass

**Steps:**

- [ ] **Step 1: Write the failing test**

```python
def test_same_time_different_place_is_a_contradiction():
    claimed = CaseAnchor(anchor_id="a1", location_ref="loc_study",
                         location_label="the study", time_ordinal=3,
                         time_label="at nine")
    actual = CaseAnchor(anchor_id="a2", location_ref="loc_conservatory",
                        location_label="the conservatory", time_ordinal=3,
                        time_label="at nine")
    case = _case_with(anchors=[claimed, actual],
                      lie_anchor="a1", evidence_anchor="a2")
    assert find_anchor_contradictions(case) == [("l1", "e1")]


def test_same_time_same_place_is_not_a_contradiction():
    anchor = CaseAnchor(anchor_id="a1", location_ref="loc_study",
                        location_label="the study", time_ordinal=3,
                        time_label="at nine")
    case = _case_with(anchors=[anchor], lie_anchor="a1", evidence_anchor="a1")
    assert find_anchor_contradictions(case) == []


def test_different_time_is_not_a_contradiction():
    claimed = CaseAnchor(anchor_id="a1", location_ref="loc_study",
                         location_label="the study", time_ordinal=1,
                         time_label="at eight")
    actual = CaseAnchor(anchor_id="a2", location_ref="loc_conservatory",
                        location_label="the conservatory", time_ordinal=3,
                        time_label="at nine")
    case = _case_with(anchors=[claimed, actual],
                      lie_anchor="a1", evidence_anchor="a2")
    assert find_anchor_contradictions(case) == []


def test_resolved_case_yields_a_detected_contradiction():
    case = resolve(_arc(), seed=4242, participant_ids=["p1", "p2", "p3"])
    assert find_anchor_contradictions(case), (
        "a resolved case must contain at least one anchor contradiction"
    )


def test_detection_uses_no_string_matching():
    source = Path("engine/case/contradiction.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in {
            "startswith", "endswith", "find", "index", "match", "search",
        }:
            raise AssertionError(f"string matching used: .{node.attr}()")
        if isinstance(node, ast.Compare):
            for op in node.ops:
                assert not isinstance(op, (ast.In, ast.NotIn)), (
                    "membership test on text is not a typed comparison"
                )
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest engine/tests/test_case_contradiction.py -v`
Expected: FAIL — `ModuleNotFoundError: engine.case.contradiction`

- [ ] **Step 3: Write `engine/case/contradiction.py`**

```python
"""Typed contradiction detection over case anchors (AW-290).

Comparison is on typed anchor fields only. Generated prose is never read
here: platform architecture principle 2 forbids inferring what happened,
and a model call per interrogation turn would violate principle 6.
"""

from __future__ import annotations

from engine.case.models import ResolvedCase


def find_anchor_contradictions(case: ResolvedCase) -> list[tuple[str, str]]:
    """Return (falsehood_id, evidence_id) pairs contradicted by anchor comparison.

    A location falsehood contradicts an evidence entry when both are
    anchored to the same ``time_ordinal`` but different ``location_ref``
    values. Same place at the same time is consistent; a different time
    proves nothing either way.
    """
    pairs: list[tuple[str, str]] = []
    for falsehood in case.falsehoods:
        if falsehood.topic != "location" or falsehood.anchor_id is None:
            continue
        claimed = case.anchor_by_id(falsehood.anchor_id)
        if claimed is None:
            continue
        for entry in case.evidence:
            if entry.anchor_id is None:
                continue
            actual = case.anchor_by_id(entry.anchor_id)
            if actual is None:
                continue
            if (
                actual.time_ordinal == claimed.time_ordinal
                and actual.location_ref != claimed.location_ref
            ):
                pairs.append((falsehood.falsehood_id, entry.evidence_id))
    return pairs
```

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest engine/tests/test_case_contradiction.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add engine/case/contradiction.py engine/tests/test_case_contradiction.py
git commit -m "feat(case): detect alibi contradictions by typed anchor comparison"
```

---

### Task 4: `engine/case` naming-contract test

**Goal:** Enforce the field-name policy that spec 0087 lists as an acceptance criterion but which currently has no test.

**Files:**
- Create: `engine/tests/test_case_naming_contract.py`

**Acceptance Criteria:**
- [ ] An AST guard over every module in `engine/case/` fails on dressing vocabulary appearing as an identifier
- [ ] The forbidden list covers dressing terms: `drink`, `stage_name`, `tier`, `room`, `weather`, `floor`, `errata`, `wrapper`, `seance`, `bigtop`, `nightcap`
- [ ] The test passes against the current tree

**Verify:** `python -m pytest engine/tests/test_case_naming_contract.py -v` → PASS

**Steps:**

- [ ] **Step 1: Read the sibling pattern before writing**

Read `engine/tests/test_claims_naming_contract.py:14-83` for the AST-guard shape.

**Critical difference — do not copy the sibling word list.** The sibling lists at `test_claims_naming_contract.py:14-33` forbid `suspect`, `victim`, `culprit`, `detective`, `murder`. `engine/case/models.py` **already uses `culprit_id` (line 159) and `is_culprit` (line 24)**, and its own docstring at lines 3-6 defines the policy as being about murder-mystery vocabulary living inside string *values* rather than field names. ADR-0017 lines 70-74 further clarifies that arc-agnostic concepts are policy-compliant and that **game-specific dressing** is what must stay out. Copying the sibling list verbatim fails on the existing tree immediately. Scope this test to dressing vocabulary only.

- [ ] **Step 2: Write the test**

```python
"""AST guard: no wrapper-dressing vocabulary as identifiers in engine/case.

Scope note: this list is deliberately narrower than the sibling contracts in
test_claims_naming_contract.py. engine/case/models.py already uses culprit_id
and is_culprit, and its module docstring defines the policy as keeping
game vocabulary inside string values. ADR-0017 lines 70-74 names dressing as
the thing that must never become a schema field name.
"""

import ast
from pathlib import Path

import pytest

FORBIDDEN = {
    "drink", "stage_name", "tier", "room", "weather",
    "floor", "errata", "wrapper", "seance", "bigtop", "nightcap",
}

CASE_MODULES = sorted(Path("engine/case").glob("*.py"))


@pytest.mark.parametrize("path", CASE_MODULES, ids=lambda p: p.name)
def test_no_dressing_vocabulary_as_identifier(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    offenders: list[str] = []
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(node.name)
        elif isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.arg):
            names.append(node.arg)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.append(node.target.id)
        for name in names:
            if name.lower().strip("_") in FORBIDDEN:
                offenders.append(f"{path.name}: {name}")
    assert not offenders, f"dressing vocabulary in engine/case: {offenders}"
```

- [ ] **Step 3: Run against the current tree**

Run: `python -m pytest engine/tests/test_case_naming_contract.py -v`
Expected: PASS for every module in `engine/case/`

- [ ] **Step 4: Commit**

```bash
git add engine/tests/test_case_naming_contract.py
git commit -m "test(case): guard engine/case against wrapper-dressing vocabulary"
```

---

# 290c — Wrapper dressing pack

### Task 5: GATE — present dressing vocabulary for founder approval

**Goal:** Get founder approval of the Séance 1928 and Big Top 1899 vocabulary before any of it is written to a file.

> **USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Files:**
- Create: `docs/design/authoring/aw-290-dressing-pack-vocabulary.md` (review artifact, prose)

**Acceptance Criteria:**
- [ ] The vocabulary is presented to the founder as a readable list, not raw JSON
- [ ] It is labelled as newly authored, not extracted — the moodboards do not contain it (verified: `seance-1928.md` has no drink pool, `big-top-1899.md` has no drink vocabulary at all and exactly two stage titles at `:50-52`, and its own handoff list at `:170-171` records stage titles as still to author)
- [ ] Coverage: drinks for both wrappers, stage-name templates for Big Top
- [ ] The founder has explicitly approved, and the approval is recorded in `docs/product/decisions-log.csv` as its own record
- [ ] No dressing file is written to `nightcap/` before that approval exists

**Verify:** `grep -c "dressing pack content approved" docs/product/decisions-log.csv` → at least 1

**Steps:**

- [ ] **Step 1: Draft the vocabulary in prose, grounded in moodboard tone**

Séance 1928 tone sources: `docs/design/moodboards/seance-1928.md:59-60` (oxblood, absinthe, malachite), `:80-81` (aged paper, walnut, brass, cut crystal, waxed velvet), `:109-110` and `:116-127` (the decanter, the second glass).
Big Top 1899 tone sources: `big-top-1899.md:18-19` (knife-thrower, escape artist, ringmaster, fortune-teller, contortionist), `:50-52` and `:117-119` (playbill caps, stage title beneath the name), `:83-84` (sawdust, canvas, gilt, greasepaint, cracked mirror).

- [ ] **Step 2: Present to the founder and STOP**

Present as a readable list. Do not proceed to Task 6 until approval is explicit. Silence is not approval, and neither is a merged PR.

- [ ] **Step 3: Record the approval**

Add a row to `docs/product/decisions-log.csv` recording dressing content approval as a record separate from spec approval and migration-design approval, per spec 0087 line 164.

```json:metadata
{"files": ["docs/design/authoring/aw-290-dressing-pack-vocabulary.md", "docs/product/decisions-log.csv"], "verifyCommand": "grep -c 'dressing pack content approved' docs/product/decisions-log.csv", "acceptanceCriteria": ["vocabulary presented as a readable list, not JSON", "labelled as newly authored rather than extracted from moodboards", "drinks for both wrappers and Big Top stage-name templates covered", "founder approval recorded as its own row in docs/product/decisions-log.csv", "no file written under nightcap/ before approval"], "modelTier": "standard", "userGate": true, "tags": ["user-gate", "content-approval"], "gateScope": "founder-content-approval", "failurePolicy": "halt"}
```

---

### Task 6: Dressing pack data file and loader

**Goal:** Load per-wrapper dressing vocabulary from game content, with the two distinct errors Q2 specified.

**Files:**
- Create: `nightcap/dressing/couch-race-wrappers.json`
- Create: `config/dressing_registry.json`
- Create: `engine/dressing/__init__.py`, `engine/dressing/models.py`, `engine/dressing/loader.py`, `engine/dressing/errors.py`
- Test: `engine/tests/test_dressing_pack.py`

**Acceptance Criteria:**
- [ ] All six wrapper ids are declared; only Séance 1928 and Big Top 1899 carry content
- [ ] `load_dressing_pack(arc_id, wrapper_id)` returns the vocabulary for an authored wrapper
- [ ] An unauthored but declared wrapper raises `DressingPackNotAuthored`
- [ ] An id outside the six raises `UnknownWrapper`
- [ ] The two lookup errors are distinct classes, both subclassing `DressingError`
- [ ] **No literal `nightcap` string appears anywhere in `engine/dressing/`** — the path comes from `config/dressing_registry.json` via prefix match, mirroring `engine/case/loader.py:95`
- [ ] An unregistered `arc_id` raises `DressingRegistryError`, not a silent fallback to whichever pack shipped first
- [ ] No dressing vocabulary appears as a Python identifier — it is data only

**Verify:** `python -m pytest engine/tests/test_dressing_pack.py -v` → all pass

**Steps:**

- [ ] **Step 1: Write the failing tests**

```python
ARC = "nightcap-couch-race"


def test_authored_wrapper_returns_vocabulary():
    pack = load_dressing_pack(ARC, "seance_1928")
    assert pack.drinks


def test_big_top_carries_stage_name_templates():
    pack = load_dressing_pack(ARC, "big_top_1899")
    assert pack.stage_name_templates


def test_declared_but_unauthored_wrapper_raises_not_authored():
    with pytest.raises(DressingPackNotAuthored) as exc:
        load_dressing_pack(ARC, "manor_gothic")
    assert "manor_gothic" in str(exc.value)


def test_id_outside_the_six_raises_unknown_wrapper():
    with pytest.raises(UnknownWrapper) as exc:
        load_dressing_pack(ARC, "atlantis_1911")
    assert "atlantis_1911" in str(exc.value)


def test_the_two_lookup_errors_are_distinct_types():
    assert not issubclass(DressingPackNotAuthored, UnknownWrapper)
    assert not issubclass(UnknownWrapper, DressingPackNotAuthored)


def test_all_six_wrappers_are_declared():
    assert set(declared_wrapper_ids(ARC)) == {
        "seance_1928", "orbital_gala_2087", "big_top_1899",
        "boardroom_severance", "manor_gothic", "sim_reunion",
    }


def test_unregistered_arc_raises_rather_than_falling_back():
    with pytest.raises(DressingRegistryError):
        load_dressing_pack("some-other-arc", "seance_1928")


def test_engine_dressing_never_names_a_game():
    """Guard the platform/game boundary. engine/ knows no game exists."""
    for path in Path("engine/dressing").glob("*.py"):
        source = path.read_text(encoding="utf-8").lower()
        assert "nightcap" not in source, f"{path.name} names a specific game"
        assert "seance" not in source, f"{path.name} names a specific wrapper"
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest engine/tests/test_dressing_pack.py -v`
Expected: FAIL — `ModuleNotFoundError: engine.dressing`

- [ ] **Step 3: Write `engine/dressing/errors.py`**

```python
"""Dressing pack lookup errors (AW-290)."""

from __future__ import annotations


class DressingError(Exception):
    """Base for dressing pack lookup failures."""


class UnknownWrapper(DressingError):
    """The requested wrapper id is not one of the declared wrappers.

    This is a typo or a bad configuration value, not missing content.
    """


class DressingPackNotAuthored(DressingError):
    """The wrapper is declared but its vocabulary has not been authored yet.

    Distinct from UnknownWrapper because it is a content gap with a known
    owner, not a bad identifier.
    """
```

- [ ] **Step 4: Write `engine/dressing/models.py`**

```python
"""Per-wrapper dressing vocabulary (AW-290).

Field names here are arc-agnostic container names. The wrapper-specific
vocabulary lives in the string values loaded from nightcap/dressing/,
never as a schema field name — ADR-0017 lines 70-74.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DressingPack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    wrapper_id: str
    authored: bool = False
    drinks: list[str] = Field(default_factory=list)
    stage_name_templates: list[str] = Field(default_factory=list)
```

- [ ] **Step 5: Write `engine/dressing/loader.py`**

**Do not hardcode a `nightcap/` path here.** `engine/` must not know any game
exists. `engine/case/loader.py:98-102` states the rule in its own words: the
registry pattern is "a generic, arc-agnostic prefix match against a registry
file, never a hardcoded path… another `detective_race` arc gets its own
registration and its own config, never Nightcap's by default." Mirror
`resolve_case_resolution_config_path` (`engine/case/loader.py:95`) exactly.

```python
"""Load per-wrapper dressing packs, arc-agnostically (AW-293).

This module knows nothing about any specific game. It resolves an arc_id
to a dressing-pack path through a registry file, the same way
engine/case/loader.py resolves case-resolution configs and
engine/arc/registry.py resolves arc definitions.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from engine.dressing.errors import (
    DressingPackNotAuthored,
    DressingRegistryError,
    UnknownWrapper,
)
from engine.dressing.models import DressingPack

DEFAULT_DRESSING_REGISTRY_PATH = Path("config/dressing_registry.json")


def resolve_dressing_pack_path(arc_id: str, registry_path: Path) -> Path:
    """Resolve which dressing pack an arc_id should load.

    Generic prefix match against a registry file, never a hardcoded path,
    so a second arc gets its own dressing content rather than inheriting
    whichever one happened to ship first.
    """
    if not registry_path.exists():
        raise DressingRegistryError(f"dressing registry missing: {registry_path}")
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    registrations = data.get("registrations")
    if not isinstance(registrations, list) or not registrations:
        raise DressingRegistryError(
            "dressing registry must contain a non-empty 'registrations' "
            f"list: {registry_path}"
        )
    for entry in registrations:
        prefix = entry.get("arc_id_prefix")
        pack_rel_path = entry.get("pack_path")
        if not prefix or not pack_rel_path:
            raise DressingRegistryError(
                f"registry entry needs 'arc_id_prefix' and 'pack_path': {entry!r}"
            )
        if arc_id.startswith(str(prefix)):
            return Path(pack_rel_path)
    raise DressingRegistryError(
        f"no dressing pack registered for arc_id {arc_id!r} in {registry_path}"
    )


@lru_cache(maxsize=4)
def _load_raw(pack_path: str) -> dict[str, dict]:
    return json.loads(Path(pack_path).read_text(encoding="utf-8"))["wrappers"]


def declared_wrapper_ids(arc_id: str, *, registry_path: Path | None = None) -> list[str]:
    """Return every wrapper id this arc declares, authored or not."""
    pack = resolve_dressing_pack_path(
        arc_id, registry_path or DEFAULT_DRESSING_REGISTRY_PATH
    )
    return sorted(_load_raw(str(pack)))


def load_dressing_pack(
    arc_id: str, wrapper_id: str, *, registry_path: Path | None = None
) -> DressingPack:
    """Return the dressing vocabulary for one wrapper of one arc.

    Raises UnknownWrapper if the id is not declared by this arc, and
    DressingPackNotAuthored if it is declared but has no content yet.
    """
    pack = resolve_dressing_pack_path(
        arc_id, registry_path or DEFAULT_DRESSING_REGISTRY_PATH
    )
    raw = _load_raw(str(pack))
    if wrapper_id not in raw:
        msg = f"{wrapper_id!r} is not a declared wrapper; declared: {sorted(raw)}"
        raise UnknownWrapper(msg)
    entry = raw[wrapper_id]
    if not entry.get("authored", False):
        msg = (
            f"wrapper {wrapper_id!r} is declared but its dressing "
            f"vocabulary has not been authored yet"
        )
        raise DressingPackNotAuthored(msg)
    return DressingPack(wrapper_id=wrapper_id, **entry)
```

`engine/dressing/errors.py` gains a third class alongside the two Q2 errors:

```python
class DressingRegistryError(DressingError):
    """The dressing registry is missing, malformed, or has no entry for this arc.

    Distinct from the two lookup errors: this is a deployment or configuration
    fault, not a content gap or a bad wrapper id.
    """
```

Create `config/dressing_registry.json` alongside the existing `config/arcs.json`:

```json
{
  "registrations": [
    {
      "arc_id_prefix": "nightcap-couch-race",
      "pack_path": "nightcap/dressing/couch-race-wrappers.json"
    }
  ]
}
```

- [ ] **Step 6: Write `nightcap/dressing/couch-race-wrappers.json`**

This file is game content and lives under `nightcap/`. Use the founder-approved
vocabulary from Task 5.

```json
{
  "wrappers": {
    "seance_1928":         {"authored": true,  "drinks": ["..."], "stage_name_templates": []},
    "big_top_1899":        {"authored": true,  "drinks": ["..."], "stage_name_templates": ["..."]},
    "orbital_gala_2087":   {"authored": false},
    "boardroom_severance": {"authored": false},
    "manor_gothic":        {"authored": false},
    "sim_reunion":         {"authored": false}
  }
}
```

- [ ] **Step 7: Run tests and both boundary guards**

Run: `python -m pytest engine/tests/test_dressing_pack.py engine/tests/test_case_naming_contract.py -v`
Expected: all pass, including `test_engine_dressing_never_names_a_game`

Then confirm the boundary directly:

```bash
grep -ri "nightcap\|seance\|big_top" engine/dressing/ && echo "VIOLATION" || echo "clean: engine names no game"
```

- [ ] **Step 8: Commit**

```bash
git add engine/dressing/ nightcap/dressing/ config/dressing_registry.json engine/tests/test_dressing_pack.py
git commit -m "feat(dressing): arc-agnostic dressing pack loader with registry-resolved paths"
```

---

### Task 7: Wrapper selection alongside era and occasion

**Goal:** Declare `wrapper` in the arc's `aesthetic_config.selection_model` so the dressing pack is selected at session start the way `era` and `occasion` are.

**Files:**
- Modify: `nightcap/couch-race.arc.json:7-16`
- Test: `engine/tests/test_dressing_selection.py`

**Acceptance Criteria:**
- [ ] `couch-race.arc.json` declares `wrapper` in `selection_model` next to `era` and `occasion`
- [ ] The arc still validates against `engine/arc/models.py:42-47` (`AestheticConfig` uses `extra="forbid"`)
- [ ] A test asserts a selected wrapper id resolves to a dressing pack

**Note before starting:** no engine or API code reads `aesthetic_config` today — it is parsed into a Pydantic model (`engine/arc/models.py:248`) and never consumed. Grep confirms zero production reads of `selection_model`, `era`, or `occasion`. This task declares the field and proves the lookup; it does not build a host-selection UI, which is out of scope.

**Verify:** `python -m pytest engine/tests/test_dressing_selection.py engine/tests/test_arc_models.py -v` → all pass

**Steps:**

- [ ] **Step 1: Write the failing test**

```python
def test_arc_declares_wrapper_selection():
    arc = load_arc(Path("nightcap/couch-race.arc.json"))
    assert "wrapper" in arc.aesthetic_config.selection_model
    assert arc.aesthetic_config.selection_model["wrapper"].type == "host_select"


def test_selected_wrapper_resolves_to_a_dressing_pack():
    arc = load_arc(Path("nightcap/couch-race.arc.json"))
    pack = load_dressing_pack(arc.arc_id, "seance_1928")
    assert pack.wrapper_id == "seance_1928"
    assert pack.drinks
```

Note the arc id comes from the loaded arc, not a literal. The test lives in
`engine/tests/` and may name `nightcap/` paths — `engine/tests/test_case_resolver.py`
is the existing precedent. Production code under `engine/` may not.

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest engine/tests/test_dressing_selection.py -v`
Expected: FAIL — `KeyError: 'wrapper'`

- [ ] **Step 3: Add `wrapper` to the arc**

In `nightcap/couch-race.arc.json`, extend `selection_model` (currently lines 8-11):

```json
    "selection_model": {
      "era": {"type": "host_select", "allow_random": true},
      "occasion": {"type": "host_select", "allow_random": true},
      "wrapper": {"type": "host_select", "allow_random": true}
    },
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest engine/tests/test_dressing_selection.py engine/tests/test_arc_models.py engine/tests/test_arc_state.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add nightcap/couch-race.arc.json engine/tests/test_dressing_selection.py
git commit -m "feat(arc): declare wrapper selection alongside era and occasion"
```

---

# 290d — Slot registry and coverage test

### Task 8: Reconcile the registry and emit it as data

**Goal:** Produce a machine-readable slot registry that matches the authored lines, correcting two errors in the prose registry.

**Files:**
- Create: `nightcap/content/slot_registry.json`
- Modify: `docs/product/2026-07-19-creative-session-master-plan.md:246-270` (correct the two errors)
- Test: `engine/tests/test_slot_registry.py`

**Acceptance Criteria:**
- [ ] Every slot in the registry file carries a `source` naming where it resolves from
- [ ] `{{tier}}` is recorded against Sim Reunion only — **not** Orbital
- [ ] `{{complication_object}}` is not in the whitelist
- [ ] `{{time_1..3}}` and `{{suspect_3}}` are not in the whitelist
- [ ] Registry slot set matches the distinct tokens actually present in `docs/design/line-libraries/`, minus the documented exclusions
- [ ] The prose registry is corrected with a note recording what changed and why

**Verify:** `python -m pytest engine/tests/test_slot_registry.py -v` → all pass

**The two corrections, verified 2026-08-05:**
1. Master plan line 259 claims `{{tier}}` "appears in both sci-fi wrappers". All 9 occurrences are in `sim-reunion.md`; `orbital-gala-2087.md` has **zero**. `docs/design/authoring/schema-fit-audit.md` inherited this error.
2. Master plan line 270 lists `{{complication_object}}` as existing in discovery samples. It appears nowhere in `docs/design/line-libraries/`; its only repo occurrence is `docs/design/authoring/story-to-arc-exemplar.md:126`.

**Steps:**

- [ ] **Step 1: Re-verify the token inventory before writing anything**

```bash
grep -rhoE '\{\{[a-z_0-9]+\}\}' docs/design/line-libraries/ | sort | uniq -c | sort -rn
```

Expected: 31 distinct tokens, `{{suspect}}` highest at 447. Confirm `{{tier}}` appears only in `sim-reunion.md`:

```bash
grep -rl 'tier' docs/design/line-libraries/
```

- [ ] **Step 2: Write the failing test**

```python
REGISTRY = Path("nightcap/content/slot_registry.json")
LIBRARIES = Path("docs/design/line-libraries")
EXCLUDED = {"time_1", "time_2", "time_3", "suspect_3", "flavor_clause", "slot"}


def _tokens_in_libraries() -> set[str]:
    pattern = re.compile(r"\{\{([a-z_0-9]+)\}\}")
    found: set[str] = set()
    for path in LIBRARIES.glob("*.md"):
        found.update(pattern.findall(path.read_text(encoding="utf-8")))
    return found


def test_every_registry_slot_has_a_named_source():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    for name, entry in registry["slots"].items():
        assert entry.get("source"), f"slot {name} has no named source"


def test_registry_covers_every_authored_slot():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    missing = _tokens_in_libraries() - EXCLUDED - set(registry["slots"])
    assert not missing, f"authored slots missing from registry: {sorted(missing)}"


def test_sample_doc_only_slots_are_not_whitelisted():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    for name in ("time_1", "time_2", "time_3", "suspect_3", "complication_object"):
        assert name not in registry["slots"], f"{name} must not be whitelisted"


def test_tier_is_recorded_against_sim_reunion_only():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert registry["slots"]["tier"]["wrappers"] == ["sim_reunion"]
```

- [ ] **Step 3: Run to verify failure**

Run: `python -m pytest engine/tests/test_slot_registry.py -v`
Expected: FAIL — registry file does not exist

- [ ] **Step 4: Write `nightcap/content/slot_registry.json`**

Each entry names its source. Sources are: `case_anchor`, `case_field`, `dressing_pack`, `session_timer`, `scoring`, `identity_aw279`.

```json
{
  "slots": {
    "suspect":     {"source": "case_field",    "detail": "CastMember.display_name where role == suspect"},
    "suspect_2":   {"source": "case_field",    "detail": "second suspect display_name"},
    "victim":      {"source": "case_field",    "detail": "CastMember.display_name where role == victim"},
    "killer":      {"source": "case_field",    "detail": "display_name where member_id == culprit_id; Beat 6 only"},
    "evidence":    {"source": "case_field",    "detail": "EvidenceEntry.short_label"},
    "callback":    {"source": "case_field",    "detail": "prior EvidenceEntry or CaseFact"},
    "location":    {"source": "case_anchor",   "detail": "CaseAnchor.location_label"},
    "time":        {"source": "case_anchor",   "detail": "CaseAnchor.time_label"},
    "occasion":    {"source": "session",       "detail": "aesthetic_config.selection_model.occasion"},
    "drink":       {"source": "dressing_pack", "detail": "DressingPack.drinks"},
    "stage_name":  {"source": "dressing_pack", "detail": "DressingPack.stage_name_templates", "wrappers": ["big_top_1899"]},
    "deck":        {"source": "dressing_pack", "wrappers": ["orbital_gala_2087"]},
    "floor":       {"source": "dressing_pack", "wrappers": ["boardroom_severance"]},
    "title":       {"source": "dressing_pack", "wrappers": ["boardroom_severance"]},
    "room":        {"source": "dressing_pack", "wrappers": ["manor_gothic"]},
    "weather":     {"source": "dressing_pack", "wrappers": ["manor_gothic"]},
    "tier":        {"source": "dressing_pack", "wrappers": ["sim_reunion"]},
    "errata":      {"source": "dressing_pack", "wrappers": ["sim_reunion"]},
    "minutes":     {"source": "session_timer", "detail": "Last Call countdown; AW-284/AW-286 own it"},
    "seconds":     {"source": "session_timer", "detail": "Last Call countdown; AW-284/AW-286 own it"},
    "count":       {"source": "scoring",       "detail": "AW-284 scoring output; superlatives only"},
    "detective":       {"source": "identity_aw279", "detail": "AW-279 identity assignment, unbuilt"},
    "detective_name":  {"source": "identity_aw279", "detail": "AW-279; never on shared surfaces"},
    "flavor":          {"source": "identity_aw279", "detail": "AW-279; never on shared surfaces"},
    "habit":           {"source": "identity_aw279", "detail": "AW-279; never on shared surfaces"}
  }
}
```

- [ ] **Step 5: Correct the prose registry**

In `docs/product/2026-07-19-creative-session-master-plan.md`, fix line 257-259 so `{{tier}}` is listed under Sim Reunion only, remove the "shared sci-fi slot" footnote, and add a dated correction note recording both errors and the grep evidence. Do **not** silently rewrite — record what changed.

- [ ] **Step 6: Run tests**

Run: `python -m pytest engine/tests/test_slot_registry.py -v`
Expected: all pass

- [ ] **Step 7: Commit**

```bash
git add nightcap/content/slot_registry.json docs/product/2026-07-19-creative-session-master-plan.md engine/tests/test_slot_registry.py
git commit -m "feat(content): emit machine-readable slot registry and correct two registry errors"
```

---

### Task 9: Registry coverage test wired to real sources

**Goal:** Fail the build if any registry slot's named source does not actually exist.

**Files:**
- Modify: `engine/tests/test_slot_registry.py`

**Acceptance Criteria:**
- [ ] Every `case_anchor` slot maps to a real `CaseAnchor` attribute
- [ ] Every `case_field` slot maps to a real attribute on a real case model
- [ ] Every `dressing_pack` slot maps to a real `DressingPack` field
- [ ] Slots sourced from unbuilt systems (`identity_aw279`, `session_timer`, `scoring`) are asserted as declared-but-unbuilt, not silently skipped

**Verify:** `python -m pytest engine/tests/test_slot_registry.py -v` → all pass

**Steps:**

- [ ] **Step 1: Write the failing test**

```python
UNBUILT_SOURCES = {"identity_aw279", "session_timer", "scoring"}


def test_case_anchor_slots_map_to_real_anchor_attributes():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    fields = set(CaseAnchor.model_fields)
    for name, entry in registry["slots"].items():
        if entry["source"] != "case_anchor":
            continue
        attr = entry["detail"].split(".")[-1]
        assert attr in fields, f"slot {name} names CaseAnchor.{attr}, which does not exist"


def test_dressing_slots_map_to_real_dressing_fields():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    fields = set(DressingPack.model_fields)
    for name, entry in registry["slots"].items():
        if entry["source"] != "dressing_pack":
            continue
        assert name in fields or f"{name}s" in fields or entry.get("wrappers"), (
            f"dressing slot {name} has no DressingPack field and no wrapper scope"
        )


def test_unbuilt_sources_are_declared_not_hidden():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    unbuilt = {n for n, e in registry["slots"].items() if e["source"] in UNBUILT_SOURCES}
    assert unbuilt == {
        "detective", "detective_name", "flavor", "habit",
        "minutes", "seconds", "count",
    }
```

- [ ] **Step 2: Run, then fix the registry until it passes**

Run: `python -m pytest engine/tests/test_slot_registry.py -v`
Expected: PASS after registry corrections

- [ ] **Step 3: Commit**

```bash
git add engine/tests/test_slot_registry.py
git commit -m "test(content): assert every registry slot resolves to a real source"
```

---

### Task 10: GATE — prove no Vesper refrain line was edited

**Goal:** Prove `docs/design/line-libraries/` is byte-identical to its state at the branch point.

> **USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Files:**
- Create: `engine/tests/test_line_libraries_untouched.py`

**Acceptance Criteria:**
- [ ] `git diff main -- docs/design/line-libraries/` produces empty output, captured verbatim
- [ ] `git diff --stat main -- docs/design/line-libraries/` shows zero files changed, captured verbatim
- [ ] Both commands' actual output is pasted into the close, not summarized
- [ ] A committed test asserts the same property so a later change cannot silently break it

**Verify:** `git diff --stat main -- docs/design/line-libraries/` → empty output, exit 0

**Steps:**

- [ ] **Step 1: Run the diff check and capture output verbatim**

```bash
git diff --stat main -- docs/design/line-libraries/ && echo "CLEAN: no line-library changes"
```

- [ ] **Step 2: Add the committed guard**

```python
"""Guard: AW-290 must not edit any authored Vesper refrain line.

Spec 0087 lists this as an acceptance criterion, and ADR-0017 preserves the
master plan's Risk 5 verbatim-conversion rule. Slots stay verbatim in the
libraries; AW-290 builds sources, it does not touch authored text.
"""

import subprocess
from pathlib import Path


def test_line_libraries_are_unmodified_against_main():
    result = subprocess.run(
        ["git", "diff", "--stat", "main", "--", "docs/design/line-libraries/"],
        capture_output=True, text=True, check=True,
    )
    assert result.stdout.strip() == "", (
        f"AW-290 must not edit authored refrain lines; diff:\n{result.stdout}"
    )


def test_line_library_directory_still_has_its_files():
    files = sorted(Path("docs/design/line-libraries").glob("*.md"))
    assert len(files) == 15, f"expected 15 library files, found {len(files)}"
```

- [ ] **Step 3: Run and capture**

Run: `python -m pytest engine/tests/test_line_libraries_untouched.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add engine/tests/test_line_libraries_untouched.py
git commit -m "test(content): guard authored refrain lines against edits"
```

```json:metadata
{"files": ["engine/tests/test_line_libraries_untouched.py"], "verifyCommand": "git diff --stat main -- docs/design/line-libraries/", "acceptanceCriteria": ["git diff --stat main -- docs/design/line-libraries/ produces empty output, captured verbatim", "git diff main -- docs/design/line-libraries/ produces empty output, captured verbatim", "actual command output pasted into the close, not summarized", "committed test asserts the property so later changes cannot silently break it"], "modelTier": "mechanical", "userGate": true, "tags": ["user-gate", "acceptance-criterion"], "gateScope": "content-integrity", "failurePolicy": "halt"}
```

---

# 290b — Case persistence

### Task 11: GATE — founder approval of the migration design

**Goal:** Obtain explicit founder approval of the concrete table design before any migration file exists.

> **USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in `acceptanceCriteria` has been re-validated independently, with output captured.

**Files:**
- Review: `docs/specs/0087-appendix-a-case-persistence-migration-design.md`
- Modify: `docs/product/decisions-log.csv`

**Acceptance Criteria:**
- [ ] The founder has approved all eight numbered items in the appendix's "What is being asked" section, or sent back specific changes
- [ ] Approval is recorded in `docs/product/decisions-log.csv` as a record separate from spec approval and dressing approval
- [ ] `migrations/versions/0008_*.py` does not exist before that record does
- [ ] The founder has acknowledged that no production caller writes these tables in this task

**Verify:** `ls migrations/versions/ | grep -c 0008` → must be `0` until the approval record exists

**Steps:**

- [ ] **Step 1: Present the appendix and STOP.** Per `AGENTS.md` Hard Rules and ADR-0022 lines 74-77, this is a schema and migration change requiring separate approval. Do not proceed to Task 12 on silence.

- [ ] **Step 2: Record the approval** in `docs/product/decisions-log.csv` once given.

```json:metadata
{"files": ["docs/specs/0087-appendix-a-case-persistence-migration-design.md", "docs/product/decisions-log.csv"], "verifyCommand": "ls migrations/versions/ | grep -c 0008", "acceptanceCriteria": ["founder approved all eight items in the appendix 'What is being asked' section, or sent back specific changes", "approval recorded in docs/product/decisions-log.csv as its own row", "no migrations/versions/0008_*.py exists before that record", "founder acknowledged no production caller writes these tables in this task"], "modelTier": "standard", "userGate": true, "tags": ["user-gate", "schema-approval", "hard-rule"], "gateScope": "founder-migration-approval", "failurePolicy": "halt"}
```

---

### Task 12: ORM models for the six case tables

**Goal:** Add six SQLAlchemy models matching the approved design, in house style.

**Files:**
- Modify: `engine/db/orm.py`
- Test: `engine/tests/test_case_orm.py`

**Acceptance Criteria:**
- [ ] Six models: `Case`, `CaseAnchorRow`, `CaseCastRow`, `CaseEvidenceRow`, `CaseFactRow`, `CaseFalsehoodRow`
- [ ] Every PK is `PGUUID(as_uuid=True)` with `server_default=text("gen_random_uuid()")`
- [ ] `Case.session_id` is a non-nullable FK to `sessions.session_id` with `UNIQUE (session_id)`
- [ ] The three anchor FKs are nullable
- [ ] The `EvidenceEntry.text` column is named `body_text` and mapped explicitly
- [ ] `Base.metadata.create_all` succeeds on SQLite after `patch_metadata_for_sqlite()`

**Verify:** `python -m pytest engine/tests/test_case_orm.py -v` → all pass

**Steps:**

- [ ] **Step 1: Write the failing test**

```python
from engine.db.testing import patch_metadata_for_sqlite

patch_metadata_for_sqlite()


@pytest_asyncio.fixture()
async def db_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_six_case_tables_create(db_session):
    for name in ("cases", "case_anchors", "case_cast",
                 "case_evidence", "case_facts", "case_falsehoods"):
        assert name in Base.metadata.tables


@pytest.mark.asyncio
async def test_one_case_per_session_is_enforced(db_session):
    session_row = await _make_session(db_session)
    db_session.add(Case(session_id=session_row.session_id, case_ref="x::case::1",
                        arc_id="x", seed=1, skeleton_id="s", culprit_ref="s1"))
    await db_session.flush()
    db_session.add(Case(session_id=session_row.session_id, case_ref="x::case::2",
                        arc_id="x", seed=2, skeleton_id="s", culprit_ref="s1"))
    with pytest.raises(IntegrityError):
        await db_session.flush()
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest engine/tests/test_case_orm.py -v`
Expected: FAIL — `ImportError: cannot import name 'Case'`

- [ ] **Step 3: Write the models**

Append to `engine/db/orm.py`, following the `Claim` (`:762`) and `Obligation` (`:714`) style exactly. Full `cases` model:

```python
class Case(Base):
    """Resolved case truth persisted per session (AW-290, ADR-0022).

    One row per session, enforced by the unique constraint. A case is not
    shared across sessions: the same arc and seed recurring in two sessions
    produces two rows.
    """

    __tablename__ = "cases"
    __table_args__ = (
        UniqueConstraint("session_id", name="uq_cases_session_id"),
        Index("ix_cases_case_ref", "case_ref"),
    )

    case_pk: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.session_id"),
        nullable=False,
    )
    case_ref: Mapped[str] = mapped_column(Text, nullable=False)
    arc_id: Mapped[str] = mapped_column(Text, nullable=False)
    seed: Mapped[int] = mapped_column(BigInteger, nullable=False)
    skeleton_id: Mapped[str] = mapped_column(Text, nullable=False)
    culprit_ref: Mapped[str] = mapped_column(Text, nullable=False)
    reveal_shape: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
```

`BigInteger` must be added to the `sqlalchemy` import block at `engine/db/orm.py:3-6`.

Write the remaining five models against the column tables in `docs/specs/0087-appendix-a-case-persistence-migration-design.md`. For `case_evidence`, declare `body_text` **after** every column using `server_default=text(...)`, or the local attribute shadows the imported `text` function — the appendix explains this.

- [ ] **Step 4: Run tests**

Run: `python -m pytest engine/tests/test_case_orm.py -v`
Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add engine/db/orm.py engine/tests/test_case_orm.py
git commit -m "feat(db): add six normalized case tables per approved migration design"
```

---

### Task 13: Alembic migration 0008

**Goal:** Ship the migration with a working downgrade.

**Files:**
- Create: `migrations/versions/0008_add_case_tables.py`

**Acceptance Criteria:**
- [ ] `revision = "0008_add_case_tables"`, `down_revision = "0007_add_accusations_table"`
- [ ] Tables created in dependency order: `cases`, `case_anchors`, then the four referencing tables
- [ ] `downgrade()` drops in exact reverse, each index before its table
- [ ] No existing table is altered
- [ ] Upgrade and downgrade verified against real Postgres, with output captured

**Verify:** `alembic upgrade head && alembic downgrade -1 && alembic upgrade head` → all succeed

**Note on verification honesty:** the only migration up/down test in the repo, `engine/tests/test_mini_game_runtime.py:798-832`, **skips unless `DATABASE_URL` is set** (`:808-810`), and its `integration` marker is unregistered in `pyproject.toml` (which lists only `slow` at lines 23-25). This step must be run manually against Postgres and the output pasted into the PR. Do not claim CI verified it.

**Steps:**

- [ ] **Step 1: Write the migration** following `migrations/versions/0007_add_accusations_table.py` verbatim in style: module docstring with `Revision ID` / `Revises` / `Create Date` plus a rationale paragraph naming AW-290 and ADR-0022; `import sqlalchemy as sa`; `from alembic import op`; `from sqlalchemy.dialects.postgresql import JSONB` and `UUID as PGUUID`; four module-level assignments; `op.create_table` with inline `sa.ForeignKey(...)`; indexes via separate `op.create_index` after each table.

- [ ] **Step 2: Verify against Postgres and capture output**

```bash
alembic upgrade head && alembic downgrade -1 && alembic upgrade head
```

- [ ] **Step 3: Commit**

```bash
git add migrations/versions/0008_add_case_tables.py
git commit -m "feat(db): add migration 0008 for normalized case tables"
```

---

### Task 14: `case_store` round-trip

**Goal:** Persist and reload a `ResolvedCase` without loss, keeping `engine/case/` free of DB imports.

**Files:**
- Create: `engine/session/case_store.py`
- Test: `engine/tests/test_case_store.py`

**Acceptance Criteria:**
- [ ] `persist_case(db, session_id, case)` writes all six tables
- [ ] `load_case(db, session_id)` returns a `ResolvedCase` equal to the original
- [ ] Anchor references survive the round trip as real FKs, not strings
- [ ] `engine/case/` still imports nothing from `engine/db/` after this task
- [ ] The SQL alibi join in the appendix returns the same pairs as `find_anchor_contradictions`

**Verify:** `python -m pytest engine/tests/test_case_store.py -v` → all pass

**Steps:**

- [ ] **Step 1: Write the failing round-trip test**

```python
@pytest.mark.asyncio
async def test_resolved_case_round_trips_without_loss(db_session):
    session_row = await _make_session(db_session)
    original = resolve(_arc(), seed=4242, participant_ids=["p1", "p2", "p3"])
    await persist_case(db_session, session_id=session_row.session_id, case=original)
    reloaded = await load_case(db_session, session_id=session_row.session_id)
    assert reloaded.model_dump() == original.model_dump()


@pytest.mark.asyncio
async def test_anchor_references_survive_as_foreign_keys(db_session):
    session_row = await _make_session(db_session)
    original = resolve(_arc(), seed=4242, participant_ids=["p1", "p2", "p3"])
    await persist_case(db_session, session_id=session_row.session_id, case=original)
    rows = (await db_session.execute(
        select(CaseEvidenceRow).where(CaseEvidenceRow.anchor_pk.isnot(None))
    )).scalars().all()
    assert rows, "expected anchored evidence rows"


def test_engine_case_still_has_no_db_import():
    for path in Path("engine/case").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mod = getattr(node, "module", "") or ""
                assert not mod.startswith("engine.db"), f"{path.name} imports engine.db"
                assert "sqlalchemy" not in mod, f"{path.name} imports sqlalchemy"
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest engine/tests/test_case_store.py -v`
Expected: FAIL — `ModuleNotFoundError: engine.session.case_store`

- [ ] **Step 3: Write `engine/session/case_store.py`**

Follow the house write pattern exactly: construct ORM objects inline, `db.add(row)`, `await db.flush()`, **never `commit()`**. Model it on `engine/session/obligations.py:71-88`. Insert `cases` first, flush to obtain `case_pk`, then `case_anchors` building an `anchor_ref → anchor_pk` map, then the four referencing tables using that map.

- [ ] **Step 4: Run tests**

Run: `python -m pytest engine/tests/test_case_store.py -v`
Expected: all pass

- [ ] **Step 5: Run the whole suite and lint**

```bash
python -m pytest engine/tests/ -q && python -m ruff check engine api && python -m ruff format --check engine api
```

- [ ] **Step 6: Commit**

```bash
git add engine/session/case_store.py engine/tests/test_case_store.py
git commit -m "feat(session): persist and reload resolved cases without loss"
```

---

# Self-review

**Spec coverage.** Every acceptance criterion in spec 0087 maps to a task: typed anchors → 1, 2; anchor value object referenced by id → 1; ordinal and labels → 1, 2; contradiction without string matching → 3; `short_label` not a truncation → 2; six tables round-tripping → 12, 14; alembic up/down → 13; dressing pack for the rehearsal pair → 5, 6, 7; registry coverage test → 8, 9; field-name policy → 4; no Vesper line edited → 10; separate approval records → 5, 11.

**Known gaps, stated rather than hidden.**
- The alembic up/down criterion cannot be met by CI as configured (Task 13 note). It needs either a Postgres service in CI or an honest downgrade of the criterion. **This is a decision for the founder, not for the implementer.**
- No production code writes the case tables after Task 14. That wiring is carved out as a separate cross-module change.
- Task 2 assumes `nightcap/case_taxonomy/` gains `location_pool` and `time_pool`. If the taxonomy shape resists that, Task 2 grows and should be re-scoped before starting.

**Type consistency.** `CaseAnchor` fields (`anchor_id`, `location_ref`, `location_label`, `time_ordinal`, `time_label`) are used identically in Tasks 1, 2, 3, 9, and the appendix. ORM classes are suffixed `Row` (`CaseAnchorRow`, `CaseEvidenceRow`) to avoid colliding with the Pydantic `CaseAnchor` — checked in Tasks 12 and 14. `find_anchor_contradictions` has one signature throughout.
