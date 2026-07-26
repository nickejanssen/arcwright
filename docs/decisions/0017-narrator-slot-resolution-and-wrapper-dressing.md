# ADR-0017: Narrator slot resolution — structured location/time plus a wrapper dressing pack

**Status**: Accepted

**Date**: 2026-07-21

## Context

The 2026-07-19 creative session authored six Vesper refrain libraries
(`docs/design/line-libraries/`) plus race-master, twist, and last-line
supplements. Each refrain carries `{{slot}}` variables that the runtime
fills from resolved session state — the pipeline the Couch Race arc
already declares as
`aesthetic_config.asset_generation.narrator_dialogue =
"authored_refrain_library_plus_generative_specifics"`.

A schema-fit audit (`docs/design/authoring/schema-fit-audit.md`, Step 2
of the master plan) mapped all 22 registry slots against the shipped
`ResolvedCase` model (`engine/case/models.py`), the arc definition
(`nightcap/couch-race.arc.json`), and the case taxonomy. It found three
tiers:

- **Tier 1 — resolvable today** from `ResolvedCase`: `{{suspect}}`,
  `{{suspect_2}}`, `{{victim}}`, `{{killer}}`, `{{evidence}}`,
  `{{callback}}`, and `{{occasion}}` (the last via the arc's
  host-selected `aesthetic_config.selection_model.occasion`).
- **Tier 2 — resolvable from another layer that must be wired**:
  `{{detective}}` (AW-279 identity, not yet built), `{{minutes}}` /
  `{{seconds}}` (Last Call timer), `{{count}}` (AW-284 scoring).
- **Tier 3 — no structured home exists.** Two distinct sub-problems:
  1. `{{location}}` and `{{time}}` read as universal case truth but the
     case model has **no discrete location or time field** — they are
     embedded inside generated `EvidenceEntry.text` / `CaseFact.value`
     prose. They are load-bearing for fairness (an alibi is a time plus
     a place).
  2. Pure wrapper aesthetic dressing — `{{drink}}`, `{{stage_name}}`,
     `{{tier}}`, `{{room}}`, `{{weather}}`, `{{floor}}`, `{{title}}`,
     `{{errata}}` — has no home at all. The case model deliberately
     holds no game-specific vocabulary (its field-name policy), and the
     arc exposes only `era` + `occasion`.

The founder selected the split option: treat the two sub-problems as
the two different kinds of thing they are.

## Decision

**Two mechanisms, one per sub-problem.**

1. **Promote `location` and `time` to structured case fields.** They
   are resolved case truth and fairness depends on them, so they belong
   in the typed model, not in dressing. Concretely: add optional typed
   fields for a location reference and a time reference to the case
   resolution surface (`EvidenceEntry` and/or `CaseFact`), populated by
   the resolver at case generation, so a narrator slot resolves to a
   real field rather than a substring of generated prose. Exact column
   shape and whether the anchor lives on `EvidenceEntry`, `CaseFact`,
   or a small shared value object is an implementation decision for the
   migration PR, which this ADR authorizes to be designed.

2. **Add a per-wrapper dressing pack for aesthetic slots.** A small
   authored config, selected at session start alongside `era` /
   `occasion`, supplying wrapper-specific vocabulary: drink names,
   stage-name templates, tier labels, weather options, room/floor
   grammar, errata flavor. This keeps aesthetic dressing OUT of the
   arc-agnostic case model (preserving the `engine/case` field-name
   policy) and matches the existing host-select aesthetic pattern. The
   moodboards (`docs/design/moodboards/`) already name drinks, stage
   titles, and tiers and are the natural authoring source.

**Field-name policy preserved under both mechanisms:** `location` and
`time` are arc-agnostic concepts (any narrative arc has them), not
murder-mystery vocabulary, so they are policy-compliant as typed case
fields. Game-specific dressing stays in wrapper config, never as a
schema field name.

**Rehearsal-1 scope (D-088: Séance 1928 + Big Top 1899):** the dressing
pack needs only two wrappers and a small field set (drinks; Big Top
stage-name templates) to unblock the rehearsal. `location` / `time`
structuring serves every wrapper and is done once.

## Consequences

### Positive consequences
- Fairness-critical `location`/`time` become queryable, testable case
  truth instead of regex-extracted prose — directly supports the
  AW-272 continuity/coherence evals and the AW-278 reveal's fairness
  accounting.
- Aesthetic dressing is cleanly separated from case truth; the
  case model stays arc-agnostic and game-neutral.
- The dressing pack generalizes: every future wrapper (and every future
  arc/genre) adds dressing as config, not code.
- No Vesper line changes. Slots stay verbatim in the libraries (the
  master plan's Risk 5 / verbatim-conversion rule is preserved).

### Negative consequences
- A real migration for the `location`/`time` fields (schema surface,
  downgrade path), plus resolver changes to populate them.
- A new authored artifact (the dressing pack) that needs a source of
  truth and, like the libraries, founder review of its content.
- Two mechanisms to reason about instead of one, justified by the two
  genuinely different kinds of data.

### Trade-offs
- We gained structured fairness data and a clean case/dressing boundary
  at the cost of one migration and one new authored config, versus the
  cheaper single-dressing-pack alternative that would have left
  location/time as loosely-typed dressing.

## Alternatives Considered

- **Option A for everything** (all Tier 3 slots, including
  location/time, in one dressing pack). Rejected: leaves
  fairness-critical case truth as untyped dressing, defeating the
  continuity evals that need structured ground truth.
- **Option C — hand-fix one Séance and one Big Top case for Rehearsal 1
  only.** Rejected as the durable answer (kept available only as a
  fallback if rehearsal-date pressure forces it); it builds no reusable
  system and would be thrown away.

## Open Implementation Questions (for the migration PR)

- Exact placement of the location/time anchors (`EvidenceEntry` vs.
  `CaseFact` vs. a shared value object) and their type (enum reference
  into a per-case location set vs. free label).
- `{{evidence}}` short-form: add an `EvidenceEntry.short_label` at
  generation (recommended) vs. truncating `.text` at resolution.
- Whether the dressing pack is founder-reviewed content or
  engineering-owned config seeded from the moodboards.

## References

- `docs/product/decisions-log.csv` D-089 (approval record)
- `docs/design/authoring/schema-fit-audit.md` (the audit that surfaced this)
- `engine/case/models.py` (`ResolvedCase` and the field-name policy)
- `nightcap/couch-race.arc.json` (`aesthetic_config.selection_model`)
- `docs/decisions/0013-nightcap-couch-race-v1-launch-target.md` (D-088 launch/rehearsal pair)
- `docs/product/2026-07-19-creative-session-master-plan.md` (Step 2/Step 4)
