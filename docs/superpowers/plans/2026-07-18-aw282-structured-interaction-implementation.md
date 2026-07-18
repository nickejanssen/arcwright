# AW-282 Structured Interaction Implementation Plan

## Goal

Implement the platform-neutral AW-282 interaction capability end to end: authored interaction definitions, deterministic player menus, private selection and allowance tracking, deterministic resolution ordering, public/private event shaping, Nightcap arc wiring, and focused tests. Stop at the AW-282 pull request.

## Architecture

- Python owns interaction definitions, menu eligibility, selection state, limits, ordering, and resolution.
- The interaction layer emits structured resolution data and ContentEvent payloads. It does not generate answers or infer truth.
- Existing event models and fanout remain the delivery boundary.
- Arc definitions reference generic interaction IDs. Nightcap supplies authored content in its arc JSON.
- AW-283 consumes validated InteractionResolution data to generate answer content and contradiction metadata.

## Tech Stack

- Python 3.11+
- Pydantic 2
- Existing Arcwright engine event models
- pytest

## Global Constraints

- No UI, rendering, Nightcap-specific logic, or model-provider names in engine interaction code.
- No free text or voice input in v1.
- No model-generated option menus.
- No mutation of canonical session state outside the Python engine.
- No Leverage implementation in this task.
- Never use em dashes in code, comments, or documentation.
- Do not add dependencies, secrets, migrations, or changes to TypeScript.

## File Map

Create:
- engine/interactions/__init__.py
- engine/interactions/models.py
- engine/interactions/errors.py
- engine/interactions/menu.py
- engine/interactions/director.py
- engine/interactions/events.py
- engine/interactions/runtime.py
- engine/interactions/README.md
- engine/tests/test_interactions_models.py
- engine/tests/test_interactions_menu.py
- engine/tests/test_interactions_director.py
- engine/tests/test_interactions_events.py
- engine/tests/test_interactions_integration.py
- engine/tests/test_interactions_runtime.py

Modify:
- engine/arc/models.py
- engine/arc/__init__.py
- engine/tests/test_arc_models.py
- engine/tests/test_couch_race_arc_json.py
- nightcap/couch-race.arc.json
- docs/specs/0074-aw282-structured-interaction-loop.md
- docs/decisions/0014-structured-interaction-resolution.md

Do not modify:
- engine/events/models.py
- engine/events/fanout.py
- engine/harness/runner.py
- character, knowledge, or mini-game modules

## Implementation Tasks

### 1. Add interaction schemas and typed errors

Test first in engine/tests/test_interactions_models.py.

Add Pydantic models and enums in engine/interactions/models.py:

- ResolutionVisibility with public and private values.
- WindowStatus with selecting, locked, and resolved values.
- InteractionOption with option_id, prompt_key, required_evidence_ids, and resolution_visibility.
- InteractionLimit with min_players, max_players, default_selections_per_player, selections_per_player_by_count, and selections_for(player_count).
- InteractionDefinition with interaction_id, ordered options, baseline_option_ids, and limit.
- InteractionTarget with target_id.
- InteractionSelection with selection_id, participant_id, target_id, and option_id.
- InteractionWindow with window identity, round, participants, eligible targets, per-player menus, remaining allowances, selections, status, and staged target.
- PublicInteractionGroup with group ID, target ID, option ID, and selection IDs.
- InteractionResolution with window ID, round, ordered selections, public groups, and private selections.

Model constraints to test: non-empty IDs, unique option and target IDs, exactly three baseline options, at most two evidence options, valid evidence requirements, valid player-count limits, and immutable selection records.

Add typed errors in engine/interactions/errors.py for closed windows, allowance exhaustion, invalid option or target, duplicate invalid input, and invalid lifecycle transitions.

Export the public types from engine/interactions/__init__.py.

Run:
~~~
..\\..\\.aw102-venv\\Scripts\\python.exe -m pytest engine/tests/test_interactions_models.py -q
~~~
Expected first run: collection or assertion failures because the module does not yet exist. Implement the smallest schemas and errors, then rerun until green.

### 2. Implement deterministic option menus

Test first in engine/tests/test_interactions_menu.py.

Implement build_option_menu(definition, held_evidence_ids) in engine/interactions/menu.py.

Required behavior:

- Preserve authored option order.
- Always include the three baseline options.
- Include an evidence option only when every required evidence ID is held.
- Include no more than two unlocked evidence options.
- Return copies that cannot mutate the definition.
- Produce the same menu for the same definition and evidence set.

Run the focused test, observe red before implementation, then green after implementation.

### 3. Implement the interaction director and lifecycle

Test first in engine/tests/test_interactions_director.py.

Implement InteractionDirector in engine/interactions/director.py with:

- __init__(definition, seed).
- open_window(window_id, round_index, participant_ids, eligible_targets, held_evidence_by_participant).
- menu_for(window_id, participant_id).
- submit_selection(window_id, participant_id, target_id, option_id).
- lock_window(window_id, allow_missing=False).

Required behavior:

- Validate participant count against InteractionLimit.
- Stage one target deterministically using seed plus round index over sorted target IDs.
- Rotate resolution order by round index over the original participant seating order.
- First submission spends one allowance. Revisions before lock replace the selection without spending another allowance.
- Reject submissions after lock and reject exhausted allowances.
- Reject targets or options absent from the participant window menu.
- By default require every participant to submit exactly one selection before lock; allow_missing leaves absent players out.
- Locking is idempotent and returns one InteractionResolution.
- Keep public selections grouped by target and option.
- Keep private selections separate even when target and option match.

Run the focused test, then the entire interactions director test file.

### 4. Shape public answers and private feedback events

Test first in engine/tests/test_interactions_events.py.

Implement event factories in engine/interactions/events.py:

- build_public_answer_event(session_id, group, answer_payload, timestamp, actor_id=None).
- build_private_feedback_event(session_id, selection, feedback_payload, timestamp).

Required behavior:

- Public answer uses existing ContentEvent with category character_dialogue, type interaction_answer, audience all, and payload containing the grouped target, option, selection IDs, and answer data.
- Private feedback uses category private_delivery, type interaction_feedback, audience specific_player, target_player_id equal to the selecting participant, and payload containing selection identity and feedback data.
- Do not place private feedback in public payloads.

Run focused event tests and existing event tests.

### 5. Integrate generic interactions into arc definitions

Test first by extending engine/tests/test_arc_models.py and engine/tests/test_couch_race_arc_json.py.

Modify engine/arc/models.py:

- Add optional interaction_ids list to BeatDefinition.
- Add optional interactions list of InteractionDefinition to ArcDefinition.
- Validate duplicate interaction IDs.
- Validate that every beat interaction ID exists in ArcDefinition.interactions.

Export the types through engine/arc/__init__.py.

Update nightcap/couch-race.arc.json:

- Add one generic investigation InteractionDefinition with three baseline options and evidence-gated options.
- Set public visibility for the baseline questions and private visibility for evidence-gated tells where authored.
- Add interaction_ids containing investigation to grill and last_call beats.
- Encode the approved allowance map for two through eight players: 2 to 3, 3 to 2, 4 to 2, and 5 through 8 to 1.

Run the arc model and Nightcap arc tests.

### 6. Add package documentation and synthetic end-to-end coverage

Write engine/interactions/README.md covering the platform-neutral vocabulary, lifecycle, allowance semantics, visibility, deterministic ordering, and AW-283 handoff.

Add engine/tests/test_interactions_integration.py that creates a synthetic multi-player session, opens a window, verifies baseline and evidence menus, submits selections, locks the window, verifies rotated order and public/private grouping, preserves AW-283 context references, and verifies allowance exhaustion.

Add engine/interactions/runtime.py and engine/tests/test_interactions_runtime.py. The runtime binds an ArcDefinition beat to an InteractionDirector, resolves public answer and private feedback events, and verifies existing SessionConnectionRegistry privacy routing. Include one-player, one-target coverage for the Daily Case configuration.

Promote the approved design into canonical docs/specs/0074-aw282-structured-interaction-loop.md and record the resolution boundary in docs/decisions/0014-structured-interaction-resolution.md.

Run:
~~~
..\\..\\.aw102-venv\\Scripts\\python.exe -m pytest engine/tests/test_interactions_*.py engine/tests/test_arc_models.py engine/tests/test_couch_race_arc_json.py engine/tests/test_events.py -q
~~~

### 7. Verify, review, and open the AW-282 PR

Run the focused suite, then repository checks:

~~~
..\\..\\.aw102-venv\\Scripts\\python.exe -m pytest engine/tests/test_interactions_*.py engine/tests/test_arc_models.py engine/tests/test_couch_race_arc_json.py engine/tests/test_events.py -q
..\\..\\.aw102-venv\\Scripts\\python.exe -m ruff check engine api
..\\..\\.aw102-venv\\Scripts\\python.exe -m ruff format --check engine api
git diff --check
~~~

Review the diff against AW-282 issue #236, the approved spec, the architecture constraints, and the acceptance criteria. Confirm no agent-local files are staged.

Commit with:
~~~
git add engine/interactions engine/tests/test_interactions_*.py engine/arc/models.py engine/arc/__init__.py engine/tests/test_arc_models.py engine/tests/test_couch_race_arc_json.py nightcap/couch-race.arc.json docs/superpowers/plans/2026-07-18-aw282-structured-interaction-implementation.md
git commit -m "feat(interactions): implement structured interaction loop"
~~~

Push codex/aw-282-leverage-catalog and open a PR targeting main. The PR description must mention the AW-282 issue, acceptance evidence, the approved spec, and that AW-283 is intentionally handed to Claude Code. Do not implement AW-283 in this branch.
