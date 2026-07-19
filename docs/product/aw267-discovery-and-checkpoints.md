# AW-267 Discovery and Checkpoint Record

**Date**: 2026-07-18

**Status**: Approved

**Interaction profile**: Creative collaboration

## Discovery decisions

AW-267's discovery, brief, and comparative-direction phases were substantively
completed across three founder review rounds on PR #243 (2026-07-16 through
2026-07-17), rather than as a single structured interview. This record makes
that history durable and closes the gate PR #246 left open: an explicit
founder statement that the resulting document is the approved direction.

1. **v0.1 (2026-07-16)** — first draft covering visual identity, three
   wrapper-level moodboards, motion/typography/color direction, and Vesper as
   a named narrator concept. D-073 recorded, later found insufficient as
   sign-off evidence because the founder had not yet reviewed the assembled
   document.
2. **v0.2 (PR #243 review round 2)** — founder feedback: *"moodboards need
   range, cinema, and obvious appeal."* This produced the "Cinema first"
   governing principle (reference altitude: *Glass Onion*, *Knives Out*,
   *The Menu*, *Death on the Nile*, *Succession*, *Severance*, *Blade Runner
   2049*, *Crimson Peak*), the appeal test ("a stranger flipping past this
   session on a TV should want to sit down"), and the expansion from three
   wrapper-level moodboards to twelve mood-specific moodboards (four per
   wrapper), each written as a producer's pitch with named references,
   palette anchors, and a described reveal moment.
3. **v0.3 (PR #243 review round 3, 2026-07-17)** — founder named the Host,
   **Vesper**, with the reference triad Caine (*The Amazing Digital Circus*)
   + Tennant's Doctor + Jackman's ringmaster-into-tragedian range, and
   established the *shift* (jubilant to grave and back) as her signature.
   Locked the anti-slop authoring model (authored refrains + AI-filled
   specifics). Founder re-ranked the polish priority order when time is
   short: **Reveal → Cold Open → Cast Rail → Interrogation Crack → Beat
   Turns** (`docs/design/nightcap-art-direction.md` §7, cited inline as
   "founder-ranked, AW-267 PR #243 review, 2026-07-17"). Added the cast-rail
   silhouette rule (§5.5) and the launch-surface direction (§8.5, own web
   app, Jackbox-style).
4. **Process gap identified (PR #246, 2026-07-17)**: this feedback was real
   but was captured as scattered PR review comments, not a durable interview
   record, and no single explicit "this is approved, ship it" statement had
   been logged. PR #246 reset the document's status metadata and D-073 to
   `Proposed` pending that explicit sign-off. No creative content changed in
   PR #246.

## Reviewed artifact

- [Nightcap Art Direction Brief v0.3](../design/nightcap-art-direction.md) —
  visual identity, three diegetic wrappers (High Society, Corporate, Sci-Fi)
  with twelve moodboards, motion principles, typography, color, cast-rail art
  rule, the Host (Vesper), the anti-slop authoring model, and launch-surface
  direction.
- [The Host bible](../design/the-host.md) — Vesper's character bible.
- Twelve moodboards under `docs/design/moodboards/`.

## Checkpoints

| Checkpoint | Artifact | Approval evidence | Result |
|---|---|---|---|
| Discovery / brief | v0.1 draft | Founder-directed first pass, 2026-07-16 | Approved (retroactive) |
| Comparative directions | v0.2 moodboard expansion | Founder feedback on PR #243 round 2: "moodboards need range, cinema, and obvious appeal", 2026-07-17 | Approved (retroactive) |
| Wrapper / Host studies | v0.3 revision | Founder naming of Vesper and re-ranking of §7 priority order on PR #243 round 3, 2026-07-17 | Approved (retroactive) |
| Final assembled brief | v0.3 document as a whole | Founder confirmed "Yes, approve as-is" for the v0.3 document as the approved direction for AW-268, 2026-07-18 session | Approved |

## Scope owner actions

- This record supersedes the "founder discovery, founder direction not yet
  selected" status on `docs/design/nightcap-art-direction.md` and reinstates
  D-073 as `Committed`.
- AW-268 (asset pipeline execution) may now proceed from the v0.3 document
  without re-litigating direction, per AW-267's own acceptance criteria.
- No code, schema, or engine change is authorized by this record — AW-267
  remains a documentation-only task (Must Not Do: "Do not ship any code in
  this task").
