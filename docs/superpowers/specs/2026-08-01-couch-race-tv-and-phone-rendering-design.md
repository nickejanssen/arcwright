# Couch Race TV and Phone Rendering — Design

> Status: Draft, awaiting founder spec review
> Date: 2026-08-01
> Task: AW-285 (issue #239) · Milestone M5 / M5-I
> Discovery evidence: `docs/product/aw285-discovery-and-checkpoints.md`
> Decisions: D-095 (minigame beat scope), D-096 (G3 engine change)

## Scope boundary

This spec covers the **structural layer only**: what data reaches each surface,
and the contracts that make the surfaces safe and buildable.

It deliberately does **not** specify layout, visual hierarchy, motion, or the
audiovisual treatment of the catch moment. Those are gated on founder direction
per AW-285's Creative-collaboration contract and will be added as a second
section after the Claude Design pass. No implementation of the visual layer
begins before that section exists and is approved.

## Problem

`nightcap-web` is a working generic renderer (5,171 LOC) with shared-display,
player, and host pages; D-070 presentation-hint handling; an audience-based
privacy filter; and a minigame stage/registry from AW-253. What it lacks is any
Couch Race awareness — grepping the renderer for `pour|scene|grill|twist|truth|
beat|contradiction|accusation|suspect` returns nothing.

The concrete failure: `getSharedDisplayEventBody` (`ui.ts:255`) surfaces only
top-level `text`, `message`, `summary`, or `description` fields, else returns the
placeholder `"A private event was shared."` Every Couch Race event carries a
structured payload — `{group_id, target_id, option_id, selection_ids, answer}`,
`{effect_key, outcome}`, `{player_id, current_amount}` — so the entire Couch Race
vocabulary renders as that placeholder. **The TV cannot stage the Grill at all.**

This is a rendering gap, not a privacy hole. The privacy architecture is sound
and is not being replaced (see Non-goals).

## Approach

A **projection layer** between engine ContentEvents and any renderer:

```
ContentEvent  ──▶  projectSharedDisplayEvent()  ──▶  SharedDisplayProjection | null
```

It answers *what data may reach the TV*, never *how it looks*. Rendering consumes
the projection; the projection knows nothing about layout.

### Alternatives considered

| Option | Verdict |
|---|---|
| Extend `getSharedDisplayEventBody` in place | Rejected. Returns `string`, so it cannot carry suspect state (G5) or asker identity (G3), making two acceptance criteria unbuildable. |
| Render structured payloads generically on the TV | Rejected. Leaks payload internals and reads as debug output. |
| **Projection layer** | **Chosen.** Only option that satisfies G3 and G5. Costs a per-event-type allowlist. |

### Required properties

1. **Audience is checked before `event_type`, never after.**
   `resource_effect_outcome` is emitted by `engine/resources/events.py` with a
   per-effect audience — table-wide for effects like Make Them Wait,
   `specific_player` for effects like Listen In. A projection keyed on
   `event_type` alone leaks private outcomes to the room. This is the single most
   dangerous shape in the event vocabulary.
2. **Reuse `isSharedDisplayVisibleEvent`** from `filters.ts`. One filter, not
   two — a second privacy predicate is a second thing to get wrong.
3. **Allowlist, not blocklist.** An unrecognised `event_type` projects `null`.
   New engine events are invisible-by-default rather than leaky-by-default.
4. **No arc logic.** The projection maps event shapes to view models. It does not
   decide state, sequence beats, or evaluate case truth.

### View model

```ts
type SharedDisplayProjectionKind =
  | "suspect_answer"
  | "resource_effect"
  | "leverage_balance"
  | "claim_recorded"
  | "score_reveal";

interface SharedDisplayProjection {
  kind: SharedDisplayProjectionKind; // closed union, not an open string
  body: string;               // human-readable text, already privacy-screened
  suspectId: string | null;   // who is on stage, when applicable
  askerIds: string[];         // G3 — requires the D-096 engine change
  suspectState: string | null; // G5 — at ease / rattled / cracking
}
```

`askerIds` is plural because the engine groups selections: `PublicInteractionGroup`
collects every selection sharing a `(target_id, option_id)` pair, so two players
who choose the same intent against the same suspect resolve into one answer with
two askers. A singular `askerId` would silently drop the second.

`kind` is a closed union rather than `string` so that adding a projection type is
a deliberate, type-checked act. An open string would let a new event type reach
the TV without review — the opposite of property 3.

`askerId` and `suspectState` are declared here because G3 and G5 are acceptance
criteria; their *presentation* is deferred to the visual section. Whether
`suspectState` is engine-derived or projection-derived is an open question below.

## Phone surfaces

The two surfaces are **not symmetrically broken**, and this asymmetry sets the
sequencing.

`getPlayerEventBody` (`ui.ts:278`) falls back to `JSON.stringify(payload)` —
deliberately, since player-private surfaces are allowed to render their full
structured payload. So the phone already displays Couch Race event content
today; it is ugly, not absent. The TV, by contrast, shows a placeholder and is
genuinely non-functional for Couch Race.

Consequently the projection layer is specified for the shared display first, and
**all phone work is Phase 2.**

The phone's outstanding items — intent menu with token counter, contradiction-flag
submission, accusation submit with lockout state — are input surfaces whose shape
is a UI decision, not a data-contract decision. There is no taste-free version of
"what the intent menu looks like." Grouping them into Phase 1 on the grounds that
they are "structural" would repeat the error this spec exists to correct: calling
a design choice structural because its data plumbing is obvious.

A parallel player-side projection replacing the `JSON.stringify` fallback is
desirable but clears no acceptance criterion, and stays an open question.

## Engine change (D-096)

G3 cannot be satisfied by rendering alone. `build_public_answer_event`
(`engine/interactions/events.py:11`) emits `selection_ids` — selection
identifiers — while asker identity lives on `InteractionSelection.participant_id`,
which travels only the private feedback path. The shared display has no data from
which to credit an asker.

Per D-096 this task exposes session-scoped asker identity on the existing public
answer event. Constraints:

- Additive to the existing payload; no new audience primitive.
- Session-scoped participant identity only. No personal data.
- Must not encode any rendering assumption in the engine event (AW-285 Must Not Do).
- Engine tests updated in the same change.

## Minigame beat coverage (D-095)

Surfaces are designed for six minigame-capable beats. `couch-race.arc.json`
currently binds `mini_games` in 2 of 6 (Scene, Twist); Pour, Grill, Last Call and
Truth are empty. Per D-095 this task adds the missing bindings.

Minigame rendering routes through the existing AW-253 stage/registry and must be
generic off the arc binding, so later packages need no renderer change. **Which
game binds to which beat is founder game-design input, not an implementation
choice** — it is an open question below, not a decision this spec makes.

## Privacy

The trust boundary is the server: `api/routers/events.py` filters through
`registry.route()` per connection role. The browser matrix is defence in depth —
as `tests/privacy-matrix.test.ts` states, it "only proves the browser surfaces do
not widen or leak what scoped streams send."

This spec adds, at the projection level:

- Every privately addressed event projects `null`, verified per event type across
  the private vocabulary: `interaction_feedback`, `resource_effect_source_revealed`,
  `clue_delivery`, `mini_game_clue_delivery`, `tmst_private_prompt_ready`.
- A canary assertion that no private payload text survives into a projection.
- The audience-variance case (`resource_effect_outcome` in both shapes) covered
  explicitly rather than incidentally.

Note for a future task, not addressed here: there is **no Python-side privacy
matrix test**. The server-side `registry.route()` filtering — the actual trust
boundary — is verified only indirectly through the TypeScript suite.

## Testing

TDD, per `docs/conventions/testing.md`. Each behaviour gets a failing test first.

- Projection of each supported public event type.
- Audience guard, tested with a *handled* event type carrying a private audience
  (a test using an unhandled type would pass vacuously and prove nothing).
- `resource_effect_outcome` in both audience shapes.
- Private-vocabulary regression guard with payload canary.
- Engine tests for the D-096 asker-identity change.

Verification: `nightcap-web` tests + typecheck, `pytest engine/tests/`,
`ruff check`, `ruff format --check`, Prettier, ESLint.

## Non-goals

- Replacing the privacy architecture. It is sound; this builds on it.
- Rebuilding the minigame stage/registry (AW-253) or the presentation-hint
  handling (`getSharedDisplayPresentationHintTokens`) — both already exist.
- Tier 2 art, animation, or sound beyond spec 0069 sequences (D-066), except
  where D-090 requires it for the catch moment.
- Any arc execution logic in TypeScript.
- Nightcap Continuity (v1.1 fast-follow, D-051).

## Open questions

1. **Visual layer** — layout, hierarchy, catch/squirm treatment, asker-credit
   staging. Gated on the Claude Design pass. Blocks the visual section only.
2. **Minigame beat assignment** — which of the existing packages binds to Pour,
   Grill, Last Call, Truth. Founder game-design input. Blocks D-095 arc wiring.
3. **`suspectState` derivation** — engine-emitted or projection-derived from
   contradiction-flag state? Engine-emitted is more consistent with deterministic
   state ownership; needs confirmation against the AW-283 claims model.
4. **Text degradation floor** — AC allows text fallback for ambient narration but
   not the catch. Where exactly is that line for evidence waves and the twist?
5. **Player-side projection** — whether to replace the phone's `JSON.stringify`
   fallback with a projection in this task or defer it. Not required by any
   acceptance criterion. Recommendation: defer, and revisit after Rehearsal 1
   shows whether raw payloads on the phone actually hurt play.
