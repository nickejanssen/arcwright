# AW-283 Discovery and Checkpoint Record

**Date**: 2026-07-18

**Status**: Discovery approved; behavior brief and sample review pending

**Interaction profile**: Creative collaboration

## Discovery decisions

1. **Suspect-answer tone**: naturalistic, character-specific dialogue —
   matches the "cinema first" reference altitude (Knives Out, Succession,
   Severance) directed in the AW-267 art-direction brief. This citation
   tracks AW-267's own approval status as recorded in
   `docs/product/aw267-discovery-and-checkpoints.md` (as of this record's
   date, v0.3 as a whole is founder-approved, with §8.5 launch-surface
   direction excluded — the "cinema first" principle is in §1, not §8.5, so
   it is in the approved scope). Truths
   and lies share the same register; only content differs. Tone is further
   parameterized by the individual suspect's generated identity/personality
   and by the session's active wrapper/era aesthetic (a High Society suspect
   and a Sci-Fi suspect should not sound interchangeable even under the same
   naturalistic baseline).
2. **Lie readability**: a subtle delivery tell is allowed (a lie may be
   slightly less specific, slightly too smooth, or hedge in a small way),
   layered on top of — never a substitute for — the deterministic
   evidence-based contradiction check. The tell is a flavor signal for
   attentive players, not the mechanism that actually confirms a catch.
3. **Contradiction fairness / catch mechanic**: unchanged from the task
   file's own Technical Scope — a player flags a suspect statement; the
   engine deterministically checks it against evidence and prior claims. No
   evidence-pairing UI is required from the player.
4. **Contradiction-catch visibility**: public on the shared TV by default,
   consistent with the catalog's rejection of "Quiet Word" (cut specifically
   for weakening the shared TV moment) and the AW-287 per-effect visibility
   decision. No Leverage effect in the launch set overrides this for a
   generic catch; if a future effect needs to, it will be reasoned through
   explicitly against this default, not assumed.
5. **Acceptable latency**: target p95 of approximately 3 seconds for
   suspect-answer generation, achievable on fast-tier routing
   (`character_dialogue.standard` in `config/routing_table.json`) with
   prompt-cached case context. This is a design target to build and measure
   against, not yet a proven number — recorded per the existing
   `p95 latency recorded in telemetry` acceptance criterion regardless of
   whether the target is hit initially.
6. **Success definition**: two-part, both required —
   (a) a confirmed catch should be traceable to a specific piece of evidence
   or a specific prior claim the player remembered, so it reads as earned
   rather than a lucky guess; (b) a suspect under pressure should read as a
   particular person protecting a particular secret, not a generically
   evasive non-answer. Founder will make the final call at the thin-slice
   review rather than pre-committing to a single written rubric.

## Behavior brief (confirmed 2026-07-19)

Suspect answers are naturalistic and character/wrapper-specific — a High
Society suspect and a Sci-Fi suspect sound different even under the same
naturalistic baseline; truths and lies share the same register. Lies may
carry a subtle delivery tell (less specific, too smooth, a small hedge) as
flavor only — catches are always decided by deterministic evidence/prior-claim
checks, never by the tell itself. A player flags a statement (no
evidence-pairing UI required); catches resolve publicly on the TV by default.
Target ~3s p95 answer-generation latency on fast-tier routing, measured and
recorded regardless of whether it's hit. Success is judged at the thin-slice
review against two qualities: a catch should feel evidence-traceable, and a
suspect under pressure should read as a specific person guarding a specific
secret. Founder confirmed this brief as-is.

## Reviewed scenarios

[Sample review](../superpowers/specs/2026-07-19-aw283-answer-generation-design.md):
representative truthful answers, authorized lies, contradiction cases (a
confirmed catch and a false-positive rejection), and fairness edge cases,
grounded directly in AW-281's real schema (`EvidenceEntry`,
`AuthorizedFalsehood`) rather than invented content. Surfaced and resolved
six further design forks the discovery record hadn't pinned down:

1. **Catch gating**: possession-gated — a catch confirms only if the claim
   matches an `AuthorizedFalsehood` and the flagging player already holds at
   least one of its `contradicted_by` evidence entries.
2. **Claim-versus-claim**: not a separate mechanism — a delivered claim can
   populate a `testimony`-type `EvidenceEntry`, reusing the existing
   claim-versus-evidence check.
3. **Question-to-fact mapping**: deterministic match of the asked question
   against known facts / authorized-lie topics, no AI judgment call.
4. **Repeat-question lies**: `claim_text` renders verbatim on every ask of
   the same lie topic; only surrounding delivery language varies.
5. **Rattle the Witness mechanism**: reuses the existing
   `social_pressure`/`crumble_threshold` system in `engine/characters/dialogue.py`
   (spec 0071) as a per-question boost, rather than a new independent
   mechanism.
6. **AW-283/AW-284 boundary**: AW-283 emits outcome-only
   `contradiction_confirmed`/`contradiction_rejected` events with no score
   value; AW-284 owns all scoring.
7. **Simultaneous-flag ties**: deterministic first-received-flag-wins ships
   now; a tie-break minigame is deferred to post-Rehearsal-1 design (D-077,
   issue #254) — see "Deferred decisions" below.

## Deferred decisions

- **Tie-break minigame** (D-077): the founder's preferred long-term
  resolution for simultaneous contradiction-catch flags is a minigame, but
  its shape is explicitly undecided pending real tie-frequency data from
  Rehearsal 1. Tracked in issue #254, building on the existing
  `engine/mini_games` framework (AW-249/AW-257) when picked up. AW-284 may
  surface an analogous accusation-tie question during its own discovery
  (flagged on issue #238) — not assumed to inherit this answer automatically.

## Checkpoints

| Checkpoint | Artifact | Approval evidence | Result |
|---|---|---|---|
| Discovery | This record | Founder answers captured across the 2026-07-18 session (tone, lie readability, catch mechanic/visibility, latency, success definition) | Approved |
| Behavior brief | This record, "Behavior brief" section | Founder confirmed as-is, 2026-07-19 | Approved |
| Answer/lie/contradiction samples | Sample review doc, seven resolved forks above | Founder answered all seven via `AskUserQuestion`, 2026-07-19 | Approved |
| Implementation plan | [docs/superpowers/plans/2026-07-19-aw283-suspect-answer-generation.md](../superpowers/plans/2026-07-19-aw283-suspect-answer-generation.md), ADR-0016, D-078 | Written by this session for handoff to a separate execution session | Complete |
| Thin slice | *(pending)* | Not yet implemented | Pending |

## Scope owner actions

- AW-287 (Leverage) merged (#253, closes #250); `engine/resources/` is
  available on `main` for AW-283 to consume when generating suspect answers.
- Planning for AW-283 (discovery through the implementation plan) is owned by
  this session; implementation is handed off to a separate execution session
  once the plan is written and approved.
