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

## Reviewed scenarios

*(Pending — Task 9: representative truthful answers, authorized lies,
contradiction cases, and fairness edge cases have not yet been presented for
review. This section will be completed once that artifact is built and
reviewed, following AW-282's checkpoint pattern.)*

## Checkpoints

| Checkpoint | Artifact | Approval evidence | Result |
|---|---|---|---|
| Discovery | This record | Founder answers captured across the 2026-07-18 session (tone, lie readability, catch mechanic/visibility, latency, success definition) | Approved |
| Behavior brief | *(pending)* | Not yet presented | Pending |
| Answer/lie/contradiction samples | *(pending)* | Not yet presented | Pending |
| Thin slice | *(pending)* | Not yet implemented | Pending |

## Scope owner actions

- Claude Code owns AW-283 implementation, sequenced after AW-287 (Leverage)
  per the founder's explicit build-order decision, since AW-283's
  contradiction-catch and answer-generation behavior varies by active
  Leverage effect.
