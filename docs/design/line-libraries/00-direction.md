# Vesper Line Libraries — Authoring Direction and Queue

> Current version: v1.0
> Last updated: 2026-07-19
> Status: Founder-approved direction (interactive interview, 2026-07-19 evening); libraries in this directory are DRAFT until individually founder-reviewed
> Canonical path: docs/design/line-libraries/00-direction.md
> Parent authority: `docs/design/the-host.md` (Vesper bible, v1.1)
> Feeds: AW-277, AW-278, AW-279, AW-280 (epic M5-I)

## What This Is

The founder-approved creative direction for authoring Vesper's refrain
libraries (the-host.md §5), plus the execution queue for the authoring
session that produced the drafts in this directory. Written so any
future session — on any model — can resume exactly where this one
stopped.

**Context for future sessions:** these drafts were authored 2026-07-19
on a creative-tier model available only that night. The direction below
was locked live with the founder; the drafts were produced unattended
afterward. Nothing in this directory is approved content until the
founder reviews it (Monday review pass expected).

## Founder Decisions Locked 2026-07-19

1. **Voice register.** Vesper as already specified in the-host.md — no
   new voice invented. Founder's register preference ordering when
   choices arise: warm-theatrical host first, dry-complicit second,
   lush-gothic third, clipped-procedural last. "I want a personality;
   not a robot."
2. **Roast rule amendment (D-081).** Vesper MAY tease players by
   detective name or tease the room. Permitted tease registers: witty,
   unhinged, absurd, silly, dad-jokey, solemn, gravitas, flirty. This
   amends the-host.md §3's former "never mocks a player" rule (now
   v1.1). Unchanged guardrails: teasing targets the detective identity,
   never the human on the couch; Vesper still takes the death itself
   seriously (§3); comedy lives in specificity of the awfulness, never
   the death.
3. **Liar texture (feeds AW-283-adjacent content).** Mixed by suspect:
   some suspects are smooth liars, some crack visibly — a per-character
   trait set at case resolution. Richest cast, best replay; accepted
   authoring/balance cost.
4. **Wrapper order.** Séance 1928 first and deepest, then Big Top 1899.
   Wrapper-neutral core is NOT authored directly — it is extracted
   later, analytically, from the concrete libraries (rationale: concrete
   lines need the creative model; extraction doesn't, and the bible's
   authoring model is per-wrapper on purpose). Boardroom Severance
   ranked last by founder.
5. **Launch-pair flag (open question for Monday).** the-host.md §5 names
   the v1 launch skin pair as Séance 1928 + **Orbital Gala 2087**.
   Tonight's founder order named Big Top second. Queue below authors
   Orbital Gala immediately after Big Top to protect the launch
   commitment; founder should confirm or re-rank the launch pair.

## Library Format (Binding)

Per the-host.md §5. Every entry carries:

- `beat`: pour | scene | grill | twist | last-call | truth
- `mood`: jubilant | grave | wondering | ominous | wink (plus the
  §5 table's specialized slots: stinger-dry, stinger-ominous,
  stinger-delighted, wrong-accusation, reveal)
- `wrapper`: the wrapper tag
- `shift_target`: which mood this line can shift into on delivery
  (entries with no shift target are permitted but budgeted — shifts
  are the signature)
- `{{slot}}` variables: the ONLY parts AI may fill at runtime
  (suspect name, location, timestamp, evidence detail, case callback)

Minimum counts per wrapper (the-host.md §5 table): cold-open jubilant 8,
drop 6, beat turns 18, stage stingers 24, wrong accusation 6, reveal 6,
wink 6 — ~74 per wrapper. New since D-081: wrong-accusation entries may
include by-name roasts across the permitted tease registers.

## Execution Queue

Committed after each item completes. Status updated in place.

| # | Item | Feeds | Status |
| --- | --- | --- | --- |
| 1 | Direction doc + the-host.md v1.1 amendment + D-081 | — | This commit |
| 2 | Séance 1928 refrain library (`seance-1928.md`) | AW-277, AW-280 | Committed (78 lines) |
| 3 | Detective identity pools + opening briefing shapes (`detective-identities.md`) | AW-279 | Committed (16 identities, 4 briefing shapes) |
| 4 | Clue-release content shapes (`clue-release-shapes.md`) | AW-280 | Committed (discovery packet, 3 directions) |
| 5 | Big Top 1899 refrain library (`big-top-1899.md`) | AW-277 | Committed (78 lines) |
| 6 | Orbital Gala 2087 refrain library (`orbital-gala-2087.md`) | AW-277, launch pair | Committed (78 lines — launch pair complete) |
| 7 | Truth-sequence / reveal shapes (`truth-sequence-shapes.md`) — DRAFT-ONLY flag, most engine-coupled | AW-278 | Committed (discovery packet, 3 architectures) |
| 8 | Boardroom Severance refrain library (`boardroom-severance.md`) | AW-277 | Committed (78 lines — original queue complete) |
| 9 | Orbital Gala detective identities (`detective-identities-orbital.md`) — bonus round | AW-279 | Committed (16 identities, 4 shapes) |
| 10 | Race-master supplement (`race-master-supplement.md`) — bonus round; proposes 4 new §5 moods | AW-277, AW-284 | Committed (launch pair) |
| 11 | Liar-texture calibration samples (`liar-texture-samples.md`) — bonus round | AW-283-adjacent | Committed (smooth/brittle/leaky) |
| 12 | Ordinary last lines (`ordinary-last-lines.md`) — bonus round | AW-278 | Committed (24 archetype-keyed) |
| 13 | Manor Gothic refrain library (`manor-gothic.md`) — D-082 round | AW-277 | Committed (78 lines) |
| 14 | Sim Reunion refrain library (`sim-reunion.md`) — D-083 round, maximum Caine | AW-277 | Committed (78 lines — range proof complete) |

D-082 platform round (see `docs/design/authoring/` and `docs/product/vision-narrative.md`): story-to-arc exemplar, vision narrative draft, Daily Case sample week, author craft guide.

**Deferred to a renewable model (not this session):** wrapper-neutral
core extraction from items 2/5/6/8; conversion of libraries to the
runtime content format at `nightcap/content/host_lines/` (an AW-283 /
narrative-content-pipeline engineering decision); AW-284 execution.

## Resume Instructions

If this session died mid-queue: pick the first non-committed item,
re-read the-host.md v1.1 in full, match the entry format of the last
committed library exactly, and keep everything DRAFT. Do not merge, do
not convert to runtime format, do not touch engine code from this
direction.

## Open Questions for Founder (Monday)

Consolidated across all committed artifacts, highest-leverage first:

1. ~~**Vesper's diegetic presence.**~~ **RESOLVED 2026-07-20 — D-084.**
   Vesper is a single entity (one host and narrator, core personality)
   who redresses per wrapper; diegetic presence is declared per wrapper
   in each library header. All six current libraries declare
   **witness**, because every authored wrapper role is an in-world
   staff/host role. The declaration mechanism matters for future
   wrappers where Vesper may be non-diegetic.
2. **D-081 roast calibration.** Each library flags its two probe lines
   (unhinged + absurd registers) in its review notes. Read the **six**
   wrong-accusation sections first; they are where the amendment sings
   or stings. (Tier 2 work — does not gate engineering.)
3. ~~**AW-280 direction selection**~~ **RESOLVED 2026-07-20 — D-085**
   (provisional): object-forward spine + testimony valve; ledger register
   rejected to preserve art-direction §4.4. Provisional because the
   interrogation-experience review may change what testimony clues feed.
4. ~~**AW-278 architecture selection**~~ **RESOLVED 2026-07-20 — D-086**:
   Unmasking spine + inline player crediting; Confession deferred as a
   post-Rehearsal-1 premium candidate. Vesper's 3-movement voice
   structure (the-host.md §6.3) governs delivery within it.
5. **Launch wrapper pair.** Séance + Orbital Gala per bible (both now
   authored), or re-rank after tonight's Big Top preference.
6. **Per-wrapper audience address.** "detectives" / "friends" /
   "everyone" — confirm the variation or flatten.
7. **br-4 (Vesper's handwritten note)** tests the no-Vesper-on-phone
   boundary — cut or keep.
8. **Per-suspect liar-texture trait** needs a schema home —
   AW-283-adjacent, engineering to spec it.
9. **Per-wrapper slot whitelists** ({{stage_name}}, {{deck}}, {{floor}},
   {{title}}, {{suspect_2}}, {{killer}}) — spec when converting to
   runtime format at `nightcap/content/host_lines/`.
