> Current version: v0.2
> Last updated: 2026-08-03
> Status: Draft
> Canonical path: docs/specs/0084-the-grill-interrogation-minigame.md

# The Grill Interrogation Mini-game

## References

- Platform contracts: `docs/specs/0077-mini-game-registration-and-story-opportunities.md` through `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`
- Interaction loop: `docs/specs/0074-aw282-structured-interaction-loop.md`
- Claims ADR: `docs/decisions/0016-aw283-claim-ledger-schema.md`
- Story: `docs/story-bibles/nightcap-couch-race.md`
- Decision record: `docs/product/decisions-log.csv` D-090, D-091, D-096, D-097

## Overview and gate

The Grill is both the Couch Race beat title and the interrogation mini-game in
which players question suspects for clues, notice tells, and catch
contradictions. It becomes a reusable interrogation package plus Nightcap
adaptation. Its placement policy requires one invocation at The Grill beat and
preserves a disabled future player-request grant from any beat. This Draft
requires founder loop, request-seam, audiovisual, device, gameplay, and
implementation approval.

## Human collaboration contract

**Profiles:** Decision interview, creative collaboration, and facilitated live operation. The founder approves the loop, repeat/request direction, artifact, and promotion. The deferred currency policy requires a later separate decision after end-to-end validation.

## Gameplay loop

The automatic invocation provides one authored selection window per active player, scaled by the existing `investigation` interaction-limit configuration. Stable join order defines round order; eligible players may choose private intent inside the current window. A player selects a suspect and an eligible question intent. Existing interaction services resolve the public answer, private tell, claim provenance, asker identity, and knowledge constraints.

Every falsifiable answer opens the existing contradiction-flag path. Competition uses existing asker credit and confirmed contradiction catches; the package creates no parallel scoring authority. Completion occurs when authored selection windows resolve or the host invokes the approved safe completion. Unresolved windows close without removing existing clue or interrogation paths.

## Reuse boundary

The package orchestrates `engine/interactions` and `engine/claims`; it does not copy suspect generation, knowledge queries, answer text, claim storage, contradiction inference, asker credit, Leverage effects, or canonical consequence logic. A knowledge-state query remains mandatory before every AI suspect response. Private tells remain on existing specific-player events. Public answer events carry session-scoped `asker_participant_id`.

The hosted mechanic stores only orchestration references and state:

```python
class TheGrillState(BaseModel):
    phase: Literal["selection", "answer", "catch_window", "complete"]
    round_index: int = Field(ge=0)
    active_character_ids: list[UUID]
    resolved_selection_ids: list[str] = Field(default_factory=list)
    current_group_id: str | None = None
    current_asker_participant_id: UUID | None = None
    catch_window_deadline: datetime | None = None
```

Python owns window order, deadlines, service calls, result semantics, repetition checks, and fallback. TypeScript renders authorized state and submits selections or flags.

## Automatic, repeated, and player-request behavior

The first placement policy anchors to The Grill beat, grants
`designer_required` authority, and starts exactly once despite retries. The
same composable policy model supports a second invocation ceiling and cooldown
without adding Grill or Nightcap fields to the engine.

The product requirement is that a player may eventually request The Grill
during any beat using game currency. This program preserves that direction
without implementing the economy: a disabled `player_requested` authority
grant references a future game-owned policy. No price, deduction, refund,
request UI, transaction semantics, or cross-beat launch is approved or
executable in this version. Validation rejects an enabled player-requested
grant without that separately approved contract.

## Result and story contract

Neutral result semantics cover questions resolved, confirmed catches, false flags, asker-credit count, participation, completion, and fallback. Nightcap maps them to bounded clue, score, or Leverage-compatible effects through authored consequence profiles. A failed question, missed catch, timeout, or cancellation never makes the case unsolvable. The package enhances investigation and social competition but does not decide case truth.

## Presentation and theme

- Player surface: notebook, suspect and intent selection, private tell, catch action, local acknowledgement.
- Shared-focus surface: suspect portrait and answer, public asker credit, room-watch progress, catch window, confirmed-catch or false-flag staging.
- Host surface: progress, connection state, deadlines, and approved safe completion.

The D-090 contradiction catch requires a high-quality audiovisual squirm as
the mechanic's payoff. It may not degrade to flat text-only presentation.
Captions and reduced motion are accessible audiovisual equivalents: captions
carry the audio meaning while a designed visual state change preserves the
reaction; reduced motion replaces large movement with an intentional static or
low-motion visual composition plus timed audio/caption cues. Muted operation
still requires the designed visual reaction. If no approved equivalent can
render, the catch pauses or uses an authored audiovisual-safe recovery instead
of claiming the quality gate passed. The renderer supports 2-to-8-player
pacing, reconnect, timeout, 44-pixel targets, keyboard operation, sound
controls, ARIA updates, and private/public separation. Nightcap provides style,
portrait, animation, and audio configuration through opaque theme data.

## Failure behavior

Duplicate beat entry returns the first run. Duplicate selection or flag resolves once. Disconnect skips or safely closes an unresolved window according to authored policy. Knowledge, generation, safety, or service failure uses authored safe completion and preserves the existing interrogation route. Reconnect reconstructs public room state and only the authenticated player's private notebook/tell.

## Certification and acceptance criteria

- [ ] Package version 0.1.0 supports 2 through 8 players and delegates all interaction, claim, contradiction, knowledge, and Leverage authority.
- [ ] The interrogation loop exists as a destination-neutral reusable package
  and a non-destructive, independently versioned Nightcap adaptation.
- [ ] Automatic beat entry is exactly once, while the package remains repeat-safe and future request-compatible.
- [ ] No executable player-request, price, deduction, refund, or cross-beat UI exists before separate approval.
- [ ] Asker credit, room-watch, contradiction catch, false flag, fallback, reconnect, and privacy work end to end.
- [ ] Phone, shared-focus, and host presentation pass accessibility, audiovisual, reduced-motion, and private-data gates.
- [ ] Confirmed catches never degrade to flat text-only; captioned, muted, and reduced-motion modes preserve a designed audiovisual-equivalent squirm under D-090.
- [ ] Real-player rehearsal validates question clarity, shared attention, competition, clue value, pace, catch satisfaction, fairness, story enhancement, and replay desire.
- [ ] The local lab exercises every player window, private tell, catch, false
  flag, timeout, disconnect, reconnect, fallback, and exact-beat placement.
- [ ] The production lab visualizes D-090 audiovisual quality, accessibility,
  privacy, fairness, device, and human evidence.
- [ ] Founder approves the loop and package before active promotion; whole-session certification owns final registration and status closure.

Tests cover no-duplication delegation, exactly-once start, service and knowledge calls, asker credit, private tells, catch outcomes, room-watch privacy, disconnect, timeout, reconnect, renderer behavior, and readiness gates.

## Founder decisions required

Approve or revise the automatic per-player loop, round timing envelope,
competition semantics, D-090 audiovisual treatment, repeat ceiling, and the
decision to reserve but not enable the any-beat currency request.
