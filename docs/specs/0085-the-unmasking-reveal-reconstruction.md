> Current version: v0.2
> Last updated: 2026-08-03
> Status: Draft
> Canonical path: docs/specs/0085-the-unmasking-reveal-reconstruction.md

# The Unmasking Reveal-reconstruction Mini-game

## References

- Platform contracts: `docs/specs/0077-mini-game-registration-and-story-opportunities.md` through `docs/specs/0080-mini-game-onboarding-preview-and-certification.md`
- Story: `docs/story-bibles/nightcap-couch-race.md`
- Truth sequence: `docs/design/line-libraries/truth-sequence-shapes.md`
- Scoring: `docs/roadmap/tasks/AW-284-race-scoring-and-accusation-state.md`
- Decision record: `docs/product/decisions-log.csv` D-086, D-093

## Overview and gate

The Unmasking is the first reusable reveal-reconstruction package adapted for
The Truth. It continues and releases pressure by turning immutable accusations
and canonical case truth into suspect clears, culprit reveal, credited
reconstruction, final score animation, ranks, podium, superlatives, and replay
handoff. Its Nightcap placement policy selects only within the human-authored
Truth pool and only where the designer delegates that authority, allowing
future certified alternatives. This Draft requires founder sequence, copy,
audiovisual, pacing, device, real-player, and implementation approval.

## Human collaboration contract

**Profiles:** Decision interview, creative collaboration, and facilitated live operation. The founder approves ordering, credit policy, copy, audiovisual pacing, solved/house-win artifacts, and promotion. Device and real-player reveal gates require observed evidence.

## Preconditions and immutable projection

The game starts only after all eligible Last Call guesses are locked and immutable. Python resolves the complete projection before narration or rendering: canonical killer, solved or house-win state, authored innocent-clear order, secrets, lies, established evidence, contradiction catches, first canonical catcher plus additional stable credits, motive, method, timeline, red herrings, near-misses, final score snapshot, ranks, podium, and superlatives.

```python
class InnocentClear(BaseModel):
    character_id: UUID
    display_name: str
    secret_summary: str
    lie_explanation: str
    credited_participant_ids: tuple[UUID, ...]
    evidence_refs: tuple[str, ...]

class RevealReconstructionProjection(BaseModel):
    model_config = ConfigDict(frozen=True)
    guesses_locked: Literal[True]
    solved: bool
    innocent_clears: tuple[InnocentClear, ...]
    culprit: CulpritReveal
    reconstruction: Reconstruction
    standings: tuple[FinalStanding, ...]
    superlatives: tuple[SuperlativeAward, ...]
    source_revision: int = Field(ge=0)
```

Reject unlocked guesses, missing canonical truth, unestablished evidence, duplicate ranks, or a culprit among innocent clears. Majority guesses, client order, and generated narration cannot change projection values.

## Sequence and gameplay

Movement 1 clears each innocent portrait in authored case-reveal order, or stable cast order when the case omits one. Each clear names the secret, explains the lie, relights the portrait, and credits established catches. The remaining portrait is re-ringed and the killer is named.

Movement 2 reconstructs motive, method, timeline, genuine clues, lies, red herrings, near-misses, and the killer's best move. It declares solved-table or house-win outcome. Nobody solving the case means the case wins; the full reveal still completes.

The handoff animates authoritative final scores, rank movement, tie-safe podium, superlatives, and replay prompt. Movement 3 ends with one approved ordinary Vesper line. The authored runtime config controls pacing within the 3-to-5-minute budget, cue timing, copy set, theme, captions, sound, and reduced-motion sequence, but cannot reorder truth or standings.

## Narration and state authority

```python
class TheUnmaskingState(BaseModel):
    phase: Literal["clearing", "culprit", "reconstruction", "podium", "complete"]
    projection: RevealReconstructionProjection
    clear_index: int = Field(ge=0)
    narration: ResolvedRevealNarration
    acknowledged_cues: set[str] = Field(default_factory=set)
    revision: int = Field(ge=0)
```

Narration resolves once from the public-safe immutable projection, after mandatory knowledge and safety boundaries, and is cached by projection digest. It follows Vesper's grave reconstruction, delight at the killer's best move, and ordinary last line. On generation timeout or validation failure, the authored D-086 copy is used. Server-owned cue acknowledgements advance state; clients cannot skip ahead, reveal the culprit early, or alter scores.

## Presentation and privacy

- Player surface: personal locked-guess reflection, personal credits, final score/rank, and replay prompt; no other private guesses.
- Shared-focus surface: cinematic clears, public credits, culprit ring, reconstruction, solved/house-win outcome, score count-up, rank movement, podium, superlatives, and last line.
- Host surface: pause/resume and cue-safe recovery controls that cannot reorder or mutate truth.

The package-local renderer provides sound controls, captions, accessible focus, color-independent truth states, reconnect-safe cue playback, and reduced-motion equivalents. Nightcap supplies portraits, rings, animation, graphics, and audio through opaque theme configuration; Arcwright emits authorized events without TV or phone assumptions.

## Failure and recovery

Reconnect resumes the persisted phase, index, revision, and acknowledged cues without replaying applied consequences. Host interruption pauses safely. Narration failure uses authored copy. Missing optional credit renders a no-credit clear. No renderer or model failure can alter case truth, locked guesses, score, rank, winner, or podium. The reveal always reaches a deterministic completion or explicit host recovery state.

## Certification and acceptance criteria

- [ ] Version 0.1.0 supports 2 through 8 session players and the configured case cast.
- [ ] The mechanic exists as a destination-neutral reusable package and a
  non-destructive, independently versioned Nightcap adaptation.
- [ ] Truth opportunity selection is deterministic and constrained to certified `reveal_reconstruction` candidates.
- [ ] Projection resolves canonical truth, credits, scores, ranks, and winners before generation or rendering.
- [ ] Solved and house-win variants, short and long casts, ties, missing credits, reconnect, and fallback are deterministic.
- [ ] Private guesses and knowledge never leak to unauthorized players, shared presentation, generation, or telemetry.
- [ ] Score animation, rank movement, podium, superlatives, audio, captions, motion, and reduced motion pass device gates.
- [ ] Real-player rehearsal validates culprit timing, reconstruction clarity, credit fairness, emotional payoff, immersion, and desire to replay.
- [ ] The local lab makes solved, house-win, short-cast, long-cast, tie,
  missing-credit, reconnect, narration-fallback, score, rank, and podium paths
  easy to test and replay.
- [ ] The production lab visualizes truth ordering, privacy release,
  audiovisual quality, pacing, accessibility, device, and human evidence.
- [ ] Founder approves the sequence and package before active promotion and whole-session closeout.

Tests cover projection immutability, ordering, credit, canonical killer, unlocked-guess rejection, generation boundary, authored fallback, cue replay, renderer order, privacy, podium authority, and readiness gates.

## Out of scope

Changing case truth, mutable guesses, model-selected suspects or winners, client-computed ranks, and active promotion before integrated certification are excluded.

## Founder decisions required

Approve or revise innocent-clear ordering, catch-credit display, the three Vesper movements, 3-to-5-minute pacing, solved and house-win treatment, score/rank/podium animation, superlatives, and ordinary last line direction.
