# Couch Race TV and Phone Rendering — Implementation Plan (Phase 1: Structural Layer)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers-extended-cc:subagent-driven-development (recommended) or superpowers-extended-cc:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Couch Race content renderable on the shared display by adding an audience-safe projection layer, and expose the asker identity the G3 acceptance criterion requires.

**Architecture:** A projection layer sits between engine ContentEvents and any renderer, mapping structured Couch Race payloads to view models. It checks `target_audience` before `event_type` and reuses the existing `isSharedDisplayVisibleEvent` allowlist. One engine change (D-096) adds session-scoped participant identity to the public interaction answer event, because asker identity is not currently on the wire at all.

**Tech Stack:** TypeScript (nightcap-web, Node test runner, `node:test` + `node:assert/strict`), Python 3.11+ (engine, pytest, Pydantic v2), Prettier + ESLint + Ruff.

**User decisions (already made):**
- "Design for 6 and wire the arc here too" — AW-285 designs surfaces for six minigame-capable beats and adds the missing arc bindings (D-095).
- "Projection layer" — chosen over extending `getSharedDisplayEventBody`, which returns a string and so cannot carry suspect state (G5) or asker identity (G3).
- "Fold into AW-285" — the G3 asker-crediting engine change lands in this task rather than a separate AW-282 task (D-096).
- "Revert it, rebuild from the approved spec" — the premature commit a5ea5c3 was reset off the branch; this plan rebuilds from the spec.
- Visual layer (layout, hierarchy, catch/squirm treatment) is gated on a Claude Design pass and is **Phase 2**, not this plan.

---

## Scope

**In scope (Phase 1):** the projection layer, its privacy guarantees, the D-096 engine change, and the arc minigame bindings.

**Out of scope (Phase 2, after the Claude Design pass):** layout, visual hierarchy, motion, the D-090 catch/squirm audiovisual treatment, and the G5 suspect-state *vocabulary and thresholds*. Task 8 establishes where `suspectState` comes from architecturally, but deliberately does not invent the "at ease / rattled / cracking" thresholds — that is founder game design.

## Architecture decisions resolved during planning

Both were open questions in the spec. Grounded in `docs/architecture/08-event-system.md §8.2`.

**`suspectState` is engine-emitted in `payload`, not derived in TypeScript.**
Deriving it client-side would compute game state in TypeScript, violating the AGENTS.md Key Engine Constraint ("Arc execution logic stays in the Python engine; no arc logic in TypeScript") and "State transitions must always be deterministic." It is *not* a rendering assumption: "rattled" states what is dramatically true; a rendering assumption would be `animation_hint="red_shake"`. The engine says what is true, the surface decides how to show it. Per ADR-0008 the `payload` is "event-type-specific structured content" owned by the arc/game, so the state vocabulary is game-configured and must not be hardcoded into platform engine code.

**Asker identity goes in `payload`, not `actor_id`.**
`actor_id` is defined as "character who produced this event" — for a suspect's answer that is the suspect, not the asker. The neutral, game-agnostic field name is `participant_ids` (a factual statement about who selected the option), which the Nightcap renderer interprets as askers.

## File structure

| File | Responsibility | Change |
|---|---|---|
| `nightcap-web/src/couch-race/display-projection.ts` | ContentEvent to shared-display view model. Audience-first. No layout. | Create |
| `nightcap-web/tests/couch-race-display-projection.test.ts` | Projection behaviour and privacy guarantees | Create |
| `nightcap-web/tests/index.test.ts` | Test barrel — must import the new suite or it never runs | Modify |
| `engine/interactions/models.py:157` | `PublicInteractionGroup` gains `participant_ids` | Modify |
| `engine/interactions/director.py:182-200` | Collect participant ids alongside selection ids | Modify |
| `engine/interactions/events.py:11-33` | Emit `participant_ids` in the public answer payload | Modify |
| `engine/tests/test_interactions_events.py` | Asserts exact payload equality — will fail until updated | Modify |
| `nightcap/couch-race.arc.json` | Minigame bindings for the 4 empty beats (D-095) | Modify |

---

### Task 1: Projection module with audience guard

**Goal:** A projection function that refuses every privately addressed event before it looks at anything else.

**Files:**
- Create: `nightcap-web/src/couch-race/display-projection.ts`
- Create: `nightcap-web/tests/couch-race-display-projection.test.ts`
- Modify: `nightcap-web/tests/index.test.ts`

**Acceptance Criteria:**
- [ ] A `specific_player` event projects `null` even when its `event_type` is one the projection handles
- [ ] The guard reuses `isSharedDisplayVisibleEvent` from `src/filters.ts` rather than defining a second predicate
- [ ] New suite runs as part of `npm test`

**Verify:** `cd nightcap-web && npm test` → `pass 104, fail 0`

**Steps:**

- [ ] **Step 1: Create the module with a deliberately unguarded implementation**

This is intentionally wrong — the next step proves the guard is missing. Create `nightcap-web/src/couch-race/display-projection.ts`:

```typescript
import type { ContentEvent } from "../types.js";

export type SharedDisplayProjectionKind =
  | "suspect_answer"
  | "resource_effect"
  | "leverage_balance";

export interface SharedDisplayProjection {
  kind: SharedDisplayProjectionKind;
  body: string;
  suspectId: string | null;
  askerIds: string[];
  suspectState: string | null;
}

type ProjectableEvent = Pick<
  ContentEvent,
  "event_type" | "target_audience" | "payload"
>;

function asRecord(value: unknown): Record<string, unknown> | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  return value as Record<string, unknown>;
}

function asNonEmptyString(value: unknown): string | null {
  return typeof value === "string" && value.trim().length > 0 ? value : null;
}

export function projectSharedDisplayEvent(
  event: ProjectableEvent,
): SharedDisplayProjection | null {
  const payload = asRecord(event.payload);
  if (!payload) {
    return null;
  }

  if (event.event_type === "interaction_answer") {
    const body = asNonEmptyString(asRecord(payload.answer)?.text);
    if (!body) {
      return null;
    }
    return {
      kind: "suspect_answer",
      body,
      suspectId: asNonEmptyString(payload.target_id),
      askerIds: [],
      suspectState: null,
    };
  }

  return null;
}
```

- [ ] **Step 2: Write the failing test**

Create `nightcap-web/tests/couch-race-display-projection.test.ts`:

```typescript
import assert from "node:assert/strict";
import test from "node:test";

import { projectSharedDisplayEvent } from "../src/couch-race/display-projection.js";
import type { ContentEvent } from "../src/types.js";

export function contentEvent(overrides: Partial<ContentEvent>): ContentEvent {
  return {
    event_id: "event-1",
    session_id: "session-1",
    timestamp: "2026-08-01T12:00:00.000Z",
    category: "character_dialogue",
    event_type: "interaction_answer",
    actor_id: null,
    target_audience: "all",
    target_player_id: null,
    payload: {},
    presentation_hints: {
      emotion: null,
      urgency: null,
      voice_hint: null,
      animation_hint: null,
      lighting_hint: null,
      pause_before_ms: 0,
    },
    sequence_number: 1,
    ...overrides,
  } as ContentEvent;
}

test("shared display refuses to project any event not addressed to it", () => {
  // Deliberately uses a HANDLED event_type with a private audience. A test
  // using an unhandled type would pass vacuously and prove nothing.
  const event = contentEvent({
    event_type: "interaction_answer",
    target_audience: "specific_player",
    target_player_id: "player-a",
    payload: {
      target_id: "suspect-vesper",
      answer: { text: "Private aside meant only for player A." },
    },
  });

  assert.equal(projectSharedDisplayEvent(event), null);
});
```

- [ ] **Step 3: Register the suite in the test barrel**

`npm test` runs only `dist/tests/index.test.js`. A suite not imported there silently never runs. In `nightcap-web/tests/index.test.ts`, add after the `privacy-matrix` import:

```typescript
import "./couch-race-display-projection.test.js";
```

- [ ] **Step 4: Run the test and verify it fails for the right reason**

Run: `cd nightcap-web && npm test`

Expected: 1 failing test. The failure must show the projection returning the private text, not `null`:

```
actual: { kind: 'suspect_answer', body: 'Private aside meant only for player A.', ... }
expected: null
```

If it fails any other way (module not found, type error), fix that first and re-run until you see this exact leak.

- [ ] **Step 5: Add the guard**

In `display-projection.ts`, add the import:

```typescript
import { isSharedDisplayVisibleEvent } from "../filters.js";
```

and insert this as the first statement in `projectSharedDisplayEvent`, before the `payload` lookup:

```typescript
  // Audience is checked before event_type, never after. Several Couch Race
  // event types (notably resource_effect_outcome) are emitted with either an
  // `all` or a `specific_player` audience depending on the effect, so keying
  // a projection on event_type alone would leak private outcomes to the room.
  if (!isSharedDisplayVisibleEvent(event)) {
    return null;
  }
```

- [ ] **Step 6: Verify green**

Run: `cd nightcap-web && npm test`
Expected: `pass 104, fail 0`

- [ ] **Step 7: Commit**

```bash
git add nightcap-web/src/couch-race/ nightcap-web/tests/couch-race-display-projection.test.ts nightcap-web/tests/index.test.ts
git commit -m "feat(nightcap-web): add Couch Race display projection with audience guard"
```

---

### Task 2: Suspect answer projection

**Goal:** A publicly addressed `interaction_answer` renders the suspect's answer text on the TV instead of the placeholder.

**Files:**
- Modify: `nightcap-web/tests/couch-race-display-projection.test.ts`
- Modify: `nightcap-web/src/couch-race/display-projection.ts`

**Acceptance Criteria:**
- [ ] A public `interaction_answer` projects `kind: "suspect_answer"` with the answer text as `body`
- [ ] `suspectId` carries `payload.target_id`
- [ ] An `interaction_answer` whose payload has no answer text projects `null` rather than an empty body

**Verify:** `cd nightcap-web && npm test` → `pass 106, fail 0`

**Steps:**

- [ ] **Step 1: Write the failing tests**

Append to `nightcap-web/tests/couch-race-display-projection.test.ts`:

```typescript
test("shared display projects a suspect's public answer text", () => {
  const event = contentEvent({
    event_type: "interaction_answer",
    target_audience: "all",
    payload: {
      group_id: "window-1:suspect-vesper:intent-alibi",
      target_id: "suspect-vesper",
      option_id: "intent-alibi",
      selection_ids: ["sel-1"],
      answer: { text: "I was on the terrace the whole time." },
    },
  });

  const projection = projectSharedDisplayEvent(event);

  assert.equal(projection?.kind, "suspect_answer");
  assert.equal(projection?.body, "I was on the terrace the whole time.");
  assert.equal(projection?.suspectId, "suspect-vesper");
});

test("an interaction_answer with no answer text projects nothing", () => {
  const event = contentEvent({
    event_type: "interaction_answer",
    target_audience: "all",
    payload: { target_id: "suspect-vesper", answer: {} },
  });

  assert.equal(projectSharedDisplayEvent(event), null);
});
```

- [ ] **Step 2: Run and verify**

Run: `cd nightcap-web && npm test`

Expected: both new tests PASS immediately, because Task 1's implementation already handles this path. That is correct and expected here — Task 1 built the handler, Task 2 pins its contract. Total: `pass 106, fail 0`.

If either test fails, the Task 1 implementation diverged from this plan. Fix the implementation, not the test.

- [ ] **Step 3: Commit**

```bash
git add nightcap-web/tests/couch-race-display-projection.test.ts
git commit -m "test(nightcap-web): pin suspect answer projection contract"
```

---

### Task 3: Audience-variable resource effect outcomes

**Goal:** `resource_effect_outcome` projects when table-wide and refuses when privately addressed. This is the highest-risk event shape in the vocabulary.

**Files:**
- Modify: `nightcap-web/tests/couch-race-display-projection.test.ts`
- Modify: `nightcap-web/src/couch-race/display-projection.ts`

**Acceptance Criteria:**
- [ ] A table-wide `resource_effect_outcome` projects `kind: "resource_effect"` with the outcome text
- [ ] A `specific_player` `resource_effect_outcome` projects `null`
- [ ] Both shapes are asserted in the same test, so the contrast cannot be split apart later

**Verify:** `cd nightcap-web && npm test` → `pass 107, fail 0`

**Steps:**

- [ ] **Step 1: Write the failing test**

Append to the test file:

```typescript
test("resource_effect_outcome projects only when publicly addressed", () => {
  // engine/resources/events.py emits this one event_type with a per-effect
  // audience: table-wide for effects like Make Them Wait, specific_player for
  // effects like Listen In. Both shapes are exercised here deliberately.
  const publicOutcome = contentEvent({
    category: "state_transition",
    event_type: "resource_effect_outcome",
    target_audience: "all",
    payload: {
      effect_key: "make-them-wait",
      outcome: { text: "Rowan's next question is delayed." },
    },
  });

  const privateOutcome = contentEvent({
    category: "private_delivery",
    event_type: "resource_effect_outcome",
    target_audience: "specific_player",
    target_player_id: "player-b",
    payload: {
      effect_key: "listen-in",
      outcome: { text: "You overhear Vesper's private tell." },
    },
  });

  const projected = projectSharedDisplayEvent(publicOutcome);
  assert.equal(projected?.kind, "resource_effect");
  assert.equal(projected?.body, "Rowan's next question is delayed.");

  assert.equal(projectSharedDisplayEvent(privateOutcome), null);
});
```

- [ ] **Step 2: Run and verify it fails for the right reason**

Run: `cd nightcap-web && npm test`

Expected: FAIL with `actual: undefined, expected: 'resource_effect'`. The private half already passes because of Task 1's guard; only the public half is unimplemented.

- [ ] **Step 3: Implement**

In `display-projection.ts`, insert before the final `return null;`:

```typescript
  if (event.event_type === "resource_effect_outcome") {
    const body = asNonEmptyString(asRecord(payload.outcome)?.text);
    if (!body) {
      return null;
    }
    return {
      kind: "resource_effect",
      body,
      suspectId: null,
      askerIds: [],
      suspectState: null,
    };
  }
```

- [ ] **Step 4: Verify green**

Run: `cd nightcap-web && npm test`
Expected: `pass 107, fail 0`

- [ ] **Step 5: Commit**

```bash
git add nightcap-web/src/couch-race/display-projection.ts nightcap-web/tests/couch-race-display-projection.test.ts
git commit -m "feat(nightcap-web): project public resource effect outcomes only"
```

---

### Task 4: Private vocabulary regression guard

**Goal:** Lock the property that no privately addressed Couch Race event type can ever project, so a future projection cannot quietly reach the TV.

**Files:**
- Modify: `nightcap-web/tests/couch-race-display-projection.test.ts`

**Acceptance Criteria:**
- [ ] All five private event types project `null`
- [ ] A canary string in the payload never appears in any projection output
- [ ] The test comment states it is a regression guard, not a TDD driver

**Verify:** `cd nightcap-web && npm test` → `pass 108, fail 0`

**Steps:**

- [ ] **Step 1: Write the guard**

This test passes on first run by design. It exists to fail *later* if someone adds a projection branch without an audience check. Append:

```typescript
// Regression guard, not a driver: the audience check in Task 1 already refuses
// these. It exists so a future projection added for one of these event types
// cannot quietly reach the shared display without this failing first.
test("no privately addressed Couch Race event type reaches the shared display", () => {
  const privateEventTypes = [
    "interaction_feedback",
    "resource_effect_source_revealed",
    "clue_delivery",
    "mini_game_clue_delivery",
    "tmst_private_prompt_ready",
  ];

  for (const eventType of privateEventTypes) {
    const event = contentEvent({
      category: "private_delivery",
      event_type: eventType,
      target_audience: "specific_player",
      target_player_id: "player-a",
      payload: {
        text: "PRIVATE-CANARY",
        answer: { text: "PRIVATE-CANARY" },
        outcome: { text: "PRIVATE-CANARY" },
      },
    });

    const projection = projectSharedDisplayEvent(event);
    assert.equal(
      projection,
      null,
      `${eventType} must not project to the shared display`,
    );
    assert.ok(
      !JSON.stringify(projection ?? {}).includes("PRIVATE-CANARY"),
      `${eventType} leaked private payload text to the shared display`,
    );
  }
});
```

- [ ] **Step 2: Verify green, then prove the guard actually bites**

Run: `cd nightcap-web && npm test` → expect `pass 108, fail 0`.

Now temporarily comment out the `isSharedDisplayVisibleEvent` guard in `display-projection.ts` and re-run. Expected: this test FAILS. A guard that cannot fail is not a guard. Restore the guard and confirm green again before committing.

- [ ] **Step 3: Commit**

```bash
git add nightcap-web/tests/couch-race-display-projection.test.ts
git commit -m "test(nightcap-web): guard private Couch Race vocabulary from the TV"
```

---

### Task 5: Expose participant identity on the public answer event (D-096)

**Goal:** Put asker identity on the wire. Without it G3 is unbuildable.

**Files:**
- Modify: `engine/interactions/models.py:157-163`
- Modify: `engine/interactions/director.py:182-200`
- Modify: `engine/interactions/events.py:11-33`
- Modify: `engine/tests/test_interactions_events.py`

**Acceptance Criteria:**
- [ ] `PublicInteractionGroup` carries `participant_ids: tuple[UUID, ...]`
- [ ] The public answer payload includes `participant_ids` as strings, ordered to match `selection_ids`
- [ ] Field name is game-agnostic (`participant_ids`, not `asker_ids`) and carries no rendering assumption
- [ ] Private feedback event is unchanged

**Verify:** `cd /path/to/repo && python -m pytest engine/tests/test_interactions_events.py -v` → all pass

**Steps:**

- [ ] **Step 1: Write the failing test**

In `engine/tests/test_interactions_events.py`, add:

```python
def test_public_answer_event_exposes_participant_ids() -> None:
    asker_one = UUID("00000000-0000-0000-0000-0000000000a1")
    asker_two = UUID("00000000-0000-0000-0000-0000000000a2")
    group = PublicInteractionGroup(
        group_id="window-1:host:observe",
        target_id="host",
        option_id="observe",
        selection_ids=["selection-1", "selection-2"],
        participant_ids=[asker_one, asker_two],
    )

    event = build_public_answer_event(
        session_id=SESSION_ID,
        group=group,
        answer_payload={"text": "The room goes quiet."},
        timestamp=TIMESTAMP,
    )

    assert event.payload["participant_ids"] == [str(asker_one), str(asker_two)]
```

- [ ] **Step 2: Run and verify it fails**

Run: `python -m pytest engine/tests/test_interactions_events.py::test_public_answer_event_exposes_participant_ids -v`

Expected: FAIL. `PublicInteractionGroup` uses `model_config = ConfigDict(extra="forbid")`, so passing an unknown field raises `ValidationError: Extra inputs are not permitted`.

- [ ] **Step 3: Add the field to the model**

In `engine/interactions/models.py`, in `PublicInteractionGroup` (line 157), add after `selection_ids`:

```python
    participant_ids: tuple[UUID, ...] = ()
```

Defaulted to empty so existing construction sites stay valid until Step 5 updates them.

- [ ] **Step 4: Emit it in the payload**

In `engine/interactions/events.py`, in `build_public_answer_event`, change the `payload` dict to:

```python
        payload={
            "group_id": group.group_id,
            "target_id": group.target_id,
            "option_id": group.option_id,
            "selection_ids": list(group.selection_ids),
            "participant_ids": [str(pid) for pid in group.participant_ids],
            "answer": answer_payload,
        },
```

- [ ] **Step 5: Populate it in the director**

In `engine/interactions/director.py`, the grouping loop currently accumulates only selection ids. Change `grouped` to carry both. Replace the declaration:

```python
        grouped: dict[tuple[str, str], list[str]] = {}
```

with:

```python
        grouped: dict[tuple[str, str], list[str]] = {}
        grouped_participants: dict[tuple[str, str], list[UUID]] = {}
```

Then inside the `for selection in ordered:` loop, immediately after the existing `grouped.setdefault(...).append(...)` call, add:

```python
            grouped_participants.setdefault(
                (selection.target_id, selection.option_id), []
            ).append(selection.participant_id)
```

Then update the `public_groups` comprehension to pass the new field:

```python
        public_groups = [
            PublicInteractionGroup(
                group_id=f"{window.window_id}:{target_id}:{option_id}",
                target_id=target_id,
                option_id=option_id,
                selection_ids=tuple(selection_ids),
                participant_ids=tuple(
                    grouped_participants[(target_id, option_id)]
                ),
            )
            for (target_id, option_id), selection_ids in grouped.items()
        ]
```

Confirm `UUID` is imported in `director.py`; if not, add `from uuid import UUID`.

- [ ] **Step 6: Fix the pre-existing exact-equality test**

`test_public_answer_event_contains_grouped_selection_metadata` asserts `event.payload == {...}` exactly, so it now fails with the added key. Add the new key to its expected dict:

```python
        "selection_ids": ["selection-1", "selection-2"],
        "participant_ids": [],
```

This is a deliberate contract update, not a workaround — the group in that test declares no participants, so an empty list is correct.

- [ ] **Step 7: Verify green across the engine**

```bash
python -m pytest engine/tests/ -q
python -m ruff check engine
python -m ruff format --check engine
```

Expected: all pass. If any other test asserts on the public answer payload, update it the same way.

- [ ] **Step 8: Commit**

```bash
git add engine/interactions/ engine/tests/test_interactions_events.py
git commit -m "feat(interactions): expose participant ids on public answer events (D-096)"
```

---

### Task 6: Surface asker identity in the projection

**Goal:** The projection carries asker identity through to the renderer, completing the G3 data path.

**Files:**
- Modify: `nightcap-web/tests/couch-race-display-projection.test.ts`
- Modify: `nightcap-web/src/couch-race/display-projection.ts`

**Acceptance Criteria:**
- [ ] A public `interaction_answer` with `participant_ids` projects them as `askerIds`
- [ ] An event with no `participant_ids` projects `askerIds: []`, never `undefined`
- [ ] Non-string entries are filtered out rather than passed through

**Verify:** `cd nightcap-web && npm test` → `pass 110, fail 0`

**Steps:**

- [ ] **Step 1: Write the failing tests**

```typescript
test("suspect answer projection carries asker identity for G3 crediting", () => {
  const event = contentEvent({
    event_type: "interaction_answer",
    target_audience: "all",
    payload: {
      target_id: "suspect-vesper",
      selection_ids: ["sel-1", "sel-2"],
      participant_ids: ["player-a", "player-b"],
      answer: { text: "I never touched the decanter." },
    },
  });

  const projection = projectSharedDisplayEvent(event);

  assert.deepEqual(projection?.askerIds, ["player-a", "player-b"]);
});

test("suspect answer projection defaults askerIds to an empty array", () => {
  const event = contentEvent({
    event_type: "interaction_answer",
    target_audience: "all",
    payload: {
      target_id: "suspect-vesper",
      answer: { text: "I never touched the decanter." },
    },
  });

  assert.deepEqual(projectSharedDisplayEvent(event)?.askerIds, []);
});
```

- [ ] **Step 2: Run and verify it fails**

Run: `cd nightcap-web && npm test`
Expected: FAIL on the first test with `actual: [], expected: [ 'player-a', 'player-b' ]`. The second passes already.

- [ ] **Step 3: Implement**

Add this helper next to `asNonEmptyString` in `display-projection.ts`:

```typescript
function asStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((entry): entry is string => typeof entry === "string");
}
```

Then in the `interaction_answer` branch, replace `askerIds: []` with:

```typescript
      askerIds: asStringArray(payload.participant_ids),
```

- [ ] **Step 4: Verify green**

Run: `cd nightcap-web && npm test`
Expected: `pass 110, fail 0`

- [ ] **Step 5: Full verification before commit**

```bash
cd nightcap-web && npm run typecheck
cd .. && npx prettier --check "nightcap-web/src/couch-race/**" "nightcap-web/tests/couch-race-display-projection.test.ts"
npx eslint nightcap-web/src/couch-race/display-projection.ts
```

Expected: all clean.

- [ ] **Step 6: Commit**

```bash
git add nightcap-web/src/couch-race/display-projection.ts nightcap-web/tests/couch-race-display-projection.test.ts
git commit -m "feat(nightcap-web): carry asker identity through the display projection"
```

---

### Task 7: Wire the projection into the shared display renderer

**Goal:** The shared display actually uses the projection, so Couch Race events stop rendering as the placeholder.

**Files:**
- Modify: `nightcap-web/src/ui.ts:255-276` (`getSharedDisplayEventBody`)
- Modify: `nightcap-web/tests/ui.test.ts`

**Acceptance Criteria:**
- [ ] `getSharedDisplayEventBody` returns the projected body for a public `interaction_answer`
- [ ] It still returns `"A private event was shared."` for events with no projection and no recognised text field
- [ ] Every existing `ui.test.ts` and `privacy-matrix.test.ts` assertion still passes unchanged

**Verify:** `cd nightcap-web && npm test` → `pass 111, fail 0`

**Steps:**

- [ ] **Step 1: Write the failing test**

In `nightcap-web/tests/ui.test.ts`, add:

```typescript
test("shared display body uses the Couch Race projection for suspect answers", () => {
  const body = getSharedDisplayEventBody({
    event_type: "interaction_answer",
    target_audience: "all",
    payload: {
      target_id: "suspect-vesper",
      answer: { text: "I was on the terrace the whole time." },
    },
  });

  assert.equal(body, "I was on the terrace the whole time.");
});
```

If `ui.test.ts` does not already import `getSharedDisplayEventBody`, add it to the existing import from `../src/ui.js`.

- [ ] **Step 2: Run and verify it fails**

Run: `cd nightcap-web && npm test`
Expected: FAIL with `actual: 'A private event was shared.', expected: 'I was on the terrace the whole time.'`

- [ ] **Step 3: Widen the signature and delegate**

`getSharedDisplayEventBody` currently takes `Pick<ContentEvent, "payload" | "event_type">`, which lacks `target_audience` — and the projection needs it. Widen the parameter and delegate before the existing field scan.

In `nightcap-web/src/ui.ts`, add the import at the top:

```typescript
import { projectSharedDisplayEvent } from "./couch-race/display-projection.js";
```

Then change the function to:

```typescript
export function getSharedDisplayEventBody(
  event: Pick<ContentEvent, "payload" | "event_type" | "target_audience">,
): string {
  const projected = projectSharedDisplayEvent(event);
  if (projected) {
    return projected.body;
  }

  const payload = event.payload;
  if (typeof payload === "string") {
    return payload;
  }

  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    return SHARED_DISPLAY_UNKNOWN_PLACEHOLDER;
  }

  const fields = ["text", "message", "summary", "description"] as const;
  for (const field of fields) {
    const value = payload[field];
    if (typeof value === "string" && value.trim().length > 0) {
      return value;
    }
  }

  return SHARED_DISPLAY_UNKNOWN_PLACEHOLDER;
}
```

- [ ] **Step 4: Fix call sites the widened type breaks**

Run `cd nightcap-web && npm run typecheck`. Any caller passing an object without `target_audience` now errors. Fix each by passing the full event rather than a narrowed literal. Existing tests in `privacy-matrix.test.ts` pass whole event objects, so they should already satisfy it.

- [ ] **Step 5: Verify green**

```bash
cd nightcap-web && npm test && npm run typecheck
```
Expected: `pass 111, fail 0`, typecheck clean.

Confirm specifically that `privacy-matrix.test.ts` still passes — it asserts the shared display never contains private clue text, and that guarantee must survive this change.

- [ ] **Step 6: Commit**

```bash
git add nightcap-web/src/ui.ts nightcap-web/tests/ui.test.ts
git commit -m "feat(nightcap-web): render Couch Race events on the shared display"
```

---

### Task 8: Arc minigame beat bindings (D-095)

**Goal:** Wire minigames into the four beats that currently have none, so the surfaces are exercised against a six-beat arc.

> **USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in the acceptance criteria has been re-validated independently, with output captured.

> **BLOCKED ON FOUNDER INPUT.** Which package binds to which beat is game design, not an implementation choice. The founder's brief said explicitly: "Do not design my game for me." Three packages exist (`crime-scene-smash`, `evidence-locker-402`, `tell-me-something-true`); Trivia is AW-289 and unbuilt. Four beats need bindings (Pour, Grill, Last Call, Truth) and only one package is currently unbound. Do not guess an assignment. Ask the founder, or leave this task open and ship Tasks 1-7.

**Files:**
- Modify: `nightcap/couch-race.arc.json` (beats index 0, 2, 4, 5 — `mini_games` arrays)

**Acceptance Criteria:**
- [ ] Founder has specified a package for each of the four empty beats, or explicitly deferred specific beats
- [ ] Each added binding has `binding_id`, `game_id`, and `version` matching the existing pattern
- [ ] Every `game_id` resolves in `nightcap/mini_games/`
- [ ] Arc validation passes

**Verify:** `python -m pytest engine/tests/ -q -k "arc or mini_game"` → all pass

**Steps:**

- [ ] **Step 1: Get the beat-to-package assignment from the founder**

Use `AskUserQuestion`. Present the three existing packages, note that only `tell-me-something-true` is currently unbound, and that AW-289's Trivia game does not exist yet. Do not proceed without an answer.

- [ ] **Step 2: Inspect the existing binding shape**

```bash
python -c "import json; d=json.load(open('nightcap/couch-race.arc.json')); print(json.dumps(d['beats'][1]['mini_games'], indent=2))"
```

Expected output, which every new binding must match structurally:

```json
[
  {
    "binding_id": "scene-crime-scene-smash",
    "game_id": "crime-scene-smash",
    "version": "0.1.0"
  }
]
```

- [ ] **Step 3: Add the founder-specified bindings**

Edit `nightcap/couch-race.arc.json`, replacing the empty `"mini_games": []` array on each specified beat. Use `<beat>-<game>` for `binding_id`, matching the existing convention.

- [ ] **Step 4: Verify**

```bash
python -c "import json; d=json.load(open('nightcap/couch-race.arc.json')); [print(b['beat_id'], [g['game_id'] for g in b['mini_games']]) for b in d['beats']]"
python -m pytest engine/tests/ -q
```

Expected: every beat the founder specified now lists its package, and the engine suite passes.

- [ ] **Step 5: Commit**

```bash
git add nightcap/couch-race.arc.json
git commit -m "feat(nightcap): bind minigames across Couch Race beats (D-095)"
```

---

### Task 9: Final verification and PR

**Goal:** Prove the whole change set is green and open a PR for founder review.

> **USER-ORDERED GATE — NON-SKIPPABLE.** This task was requested by the user in the current conversation. It MUST NOT be closed by walking around it, by declaring it "verified inline", or by substituting a cheaper check. Close only after every item in the acceptance criteria has been re-validated independently, with output captured.
>
> The user's brief defined done as: "tests pass, lint passes, PR open, and you report which acceptance criteria passed with evidence. Stop before merge — I merge." Reporting a criterion as passed without captured command output violates this gate.

**Files:** none modified

**Acceptance Criteria:**
- [ ] Full nightcap-web suite, typecheck, Prettier, ESLint all pass
- [ ] Full engine suite, Ruff check and format all pass
- [ ] PR body includes `Closes: #239` and states which acceptance criteria are met versus deferred to Phase 2
- [ ] PR is opened but NOT merged

**Verify:** `gh pr view --json state` → `OPEN`

**Steps:**

- [ ] **Step 1: Run every check**

```bash
cd nightcap-web && npm test && npm run typecheck && cd ..
python -m pytest engine/tests/ -q
python -m ruff check engine api
python -m ruff format --check engine api
npx prettier --check "nightcap-web/src/**" "nightcap-web/tests/**"
```

Record the actual output of each. Do not claim success without it.

- [ ] **Step 2: Request code review**

Invoke the `superpowers-extended-cc:requesting-code-review` skill before opening the PR.

- [ ] **Step 3: Confirm no stray files are staged**

```bash
git status
```

`dashboard/dist/`, `.superpowers/`, and `.claude/worktrees/` must not appear. Leave any pre-existing unrelated changes untouched and mention them in the PR rather than fixing them.

- [ ] **Step 4: Open the PR**

Body must include `Closes: #239`, the per-criterion evidence table, and an explicit note that the visual layer (D-090 catch treatment, G5 room-watch presentation, layout) is Phase 2 pending the Claude Design pass.

- [ ] **Step 5: Stop**

Do not merge. The founder merges.

---

## Phase 2 (not in this plan)

Begins after the Claude Design pass returns a direction. Covers layout and visual hierarchy for the Grill TV and phone screens, the D-090 catch/squirm audiovisual treatment, G5 suspect-state presentation, the minigame slot's visual framing, and the remaining beats. The `suspectState` field is already declared on the projection; Phase 2 populates it once the founder sets the vocabulary and thresholds.
