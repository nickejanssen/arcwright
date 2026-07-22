# Schema-Fit Audit — Vesper Slots vs. Engine State

> Current version: v1.0
> Last updated: 2026-07-21
> Status: Report for founder review (master plan Step 2 / prompt step 3).
> Reports unmappable slots WITH OPTIONS. Changes nothing until the
> founder picks. No library line has been edited.
> Canonical path: docs/design/authoring/schema-fit-audit.md
> Scope prioritised for the Rehearsal 1 pair (D-088): Séance 1928 +
> Big Top 1899. Launch-only and non-rehearsal slots audited but flagged
> lower priority.

## Method (grounded, not assumed)

Every slot mapped against the actual shipped models, read this session:

- `engine/case/models.py` → `ResolvedCase` (cast, culprit_id, evidence,
  falsehoods, facts, reveal_shape) and its members: `CastMember`
  (member_id, display_name, role, is_culprit, tags), `EvidenceEntry`
  (evidence_id, evidence_type, text, delivery, delivery_target,
  truth_value), `CaseFact` (predicate, subject_id, object_id, value,
  known_by).
- `nightcap/couch-race.arc.json` → `aesthetic_config.selection_model`
  exposes **`era`** and **`occasion`** as host-selected fields;
  `setting_constraint = "social_gathering"`.
- `nightcap/case_taxonomy/*.json` → cast names, victim names, evidence
  types, lie topics, method/motive families. **No wrapper-dressing
  vocabulary** (no drinks, weather, stage names, tiers).
- `engine/interactions/` (AW-282) → the interaction window carries the
  on-stage target and each player's held evidence.

**Two structural facts found:**

1. **No refrain-resolver component exists yet.** Grep for
   `host_line`/`refrain`/`narrator_line` finds only the arc's
   `asset_generation.narrator_dialogue =
   "authored_refrain_library_plus_generative_specifics"` declaration —
   the pipeline is *specified* but *unbuilt*. Step 4 (runtime
   conversion) must build the consumer, or it is a
   narrative-content-pipeline task in its own right.
2. **AW-279 detective identity assignment is not built.** So
   `{{detective}}` currently has no runtime source; it depends on
   AW-279 shipping (identity pools already authored;
   `detective-identities.md` + Big Top pool pending per D-088).

## Tier 1 — Directly resolvable from ResolvedCase / arc (no new work)

| Slot | Source | Notes |
| --- | --- | --- |
| `{{suspect}}` | `CastMember.display_name`, role=suspect, bound to the interaction window's on-stage target | The resolver already knows who is on stage. |
| `{{suspect_2}}` | a second suspect `display_name` | Needs a *selection rule* — recommend: the suspect named in the on-stage suspect's `relationship` CaseFact (`object_id`). Deterministic. |
| `{{victim}}` | `CastMember.display_name`, role=victim | Single victim per case. |
| `{{killer}}` | `display_name` where `member_id == culprit_id` | Beat 6 only — resolver must gate exposure to the Truth beat (matches the-host.md §3 hard rule). |
| `{{evidence}}` | `EvidenceEntry` | Slot wants a *short reference*; `.text` is full clue prose. Recommend adding a short-form label at generation (see Q3). |
| `{{callback}}` | a prior `EvidenceEntry.evidence_id` or `CaseFact` | Needs a "most-recently-surfaced salient detail" selector; deterministic from event order. |
| `{{occasion}}` | `aesthetic_config.selection_model.occasion` (host-selected) | **Confirmed resolvable** — this was a suspected gap; it is not. |

## Tier 2 — Resolvable from another existing layer (must be wired)

| Slot | Source layer | Wiring needed |
| --- | --- | --- |
| `{{detective}}` | AW-279 identity assignment | AW-279 must ship; identity name projects to shared surfaces (its privacy contract already forbids `{{habit}}`/private fields on shared surfaces). |
| `{{minutes}}` / `{{seconds}}` | Last Call beat timer / session runtime | Countdown refrains fire from the timer, not the case. AW-284/AW-286 territory. |
| `{{count}}` | session scoring / telemetry | Superlative counts (contradictions caught, questions asked). AW-284 scoring output. |

## Tier 3 — GAP: no structured home exists (wrapper dressing)

These slots are **wrapper aesthetic dressing**, not case truth. The
case model deliberately holds no game-specific vocabulary
(`engine/case/models.py` field-name policy), and the arc exposes only
`era` + `occasion`. There is currently **nowhere** for these to
resolve from:

| Slot | Wrapper | In rehearsal pair? |
| --- | --- | --- |
| `{{drink}}` | universal dressing | **YES** — both Séance and Big Top use it |
| `{{location}}` / `{{time}}` | universal | **YES** — used heavily; see note |
| `{{stage_name}}` | Big Top | **YES** (D-088 rehearsal) |
| `{{deck}}` / `{{tier}}` | Orbital | launch only |
| `{{room}}` / `{{weather}}` | Manor | neither |
| `{{floor}}` / `{{title}}` | Boardroom | neither |
| `{{errata}}` | Sim Reunion | neither |

**Important nuance on `{{location}}` and `{{time}}`:** these read like
universal case facts, but the case model has **no discrete `location`
or `time` field** — they live *inside* generated `EvidenceEntry.text`
and `CaseFact.value` prose. They are real case truth with no
structured slot. This is the highest-priority gap because they are
used in every wrapper and are load-bearing for fairness (an alibi is a
time + place).

## The Decision You Owe (before Step 4 changes anything)

Three ways to close the Tier 3 gap. This is a real architecture choice;
I recommend but do not decide.

**Option A — Wrapper dressing pack (recommended).** Add a per-wrapper
`dressing` config (a small authored JSON: drink names, stage-name
templates, tier labels, weather options, etc.) selected at session
start alongside `era`/`occasion`. Clean, matches the existing
host-select aesthetic pattern, keeps dressing out of the arc-agnostic
case model (respects the field-name policy). Cost: one new config
shape + a selection step. Rehearsal-blocking subset is small: drinks +
Big Top stage-name templates.

**Option B — Promote location/time to structured case fields.** Add
`location` and `time` as first-class fields on `EvidenceEntry` /
`CaseFact` (they are genuine case truth, unlike drinks). Fixes the
fairness-load-bearing gap properly; leaves pure dressing (drink,
weather) to Option A. Recommend **B for location/time specifically,
A for the rest** — they are different kinds of thing.

**Option C — Author around the gap for Rehearsal 1 only.** For the
rehearsal, hand-fix a single Séance and single Big Top case with
dressing baked into the authored refrain instances (no generalised
system). Fastest path to a rehearsal; explicitly throwaway. Only
choose if Rehearsal 1 date pressure beats doing it right once.

## Recommended Resolution

- **Location/time → Option B** (structured fields; they are case truth
  and fairness depends on them).
- **All other dressing → Option A** (a per-wrapper dressing pack).
- **Rehearsal unblock:** the dressing pack needs only two wrappers
  (Séance, Big Top) and a handful of fields to run Rehearsal 1 — small.
- **Sequencing:** this is a **schema/generation change**, so per
  AGENTS.md it needs a migration/ADR-level review and is engineering
  scope, NOT a content edit. It does not touch a single Vesper line
  (Risk 5 / verbatim rule preserved). It slots into master-plan Step 2
  as the concrete conversion contract.

## What Does NOT Change

- No Vesper line is edited. Slots stay verbatim in the libraries.
- The case model's arc-agnostic field-name policy is preserved under
  every option (dressing lives in wrapper config or typed fields, never
  as game-specific schema names).
- Nothing here alters MVP scope or the Rehearsal-1 gate sequence.

## Open Questions Rolled Up For The Founder

1. Approve **B for location/time + A for dressing**, or pick one option
   for everything?
2. The wrapper dressing pack is authored content — is that a new
   founder-reviewed artifact (like the libraries), or engineering-owned
   config seeded from the moodboards? (Moodboards already name drinks,
   stage titles, tiers — they are the natural source.)
3. `{{evidence}}` short-form label (Q from Tier 1): add a
   `short_label` to `EvidenceEntry` at generation, or resolve the slot
   to a truncated `.text`? Recommend `short_label`.
