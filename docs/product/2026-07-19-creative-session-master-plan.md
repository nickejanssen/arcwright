# Master Plan — 2026-07-19 Creative Session: Review, Integration, Roadmap

> Current version: v1.0
> Last updated: 2026-07-19 (end of session)
> Status: The single entry point for everything the 2026-07-19 Fable
> session produced. Start here. Every other artifact is linked, gated,
> and sequenced from this document.
> Canonical path: docs/product/2026-07-19-creative-session-master-plan.md
> Branch: `claude/vesper-line-libraries` (all DRAFT, nothing merged)
> Decisions recorded live: D-081, D-082, D-083

---

## 1. What Exists (Complete Inventory)

**Verified counts, no estimates.** Six libraries × 78 entries = 468
Vesper refrain lines (plus race-master, twist-menu, and last-line
supplements). As of the 2026-07-20/21 Tier-1 + review pass: ~30
commits, 26 files, ~4,770 insertions vs main; 21 files retain DRAFT
headers. Tier 1 decisions D-084–D-088 recorded.

### Rehearsal-1-critical (feeds M5-I directly)

| Artifact | Feeds | State |
| --- | --- | --- |
| `docs/design/line-libraries/00-direction.md` | all | Founder direction record + queue + open questions |
| `seance-1928.md`, `orbital-gala-2087.md` | AW-277 | **Launch pair** — 156 lines vs ~148 minimum |
| `detective-identities.md`, `detective-identities-orbital.md` | AW-279 | Both launch wrappers covered |
| `race-master-supplement.md` | AW-277, AW-284 | Countdown / evidence-wave / nudge / superlative — proposes 4 new §5 moods |
| `clue-release-shapes.md` | AW-280 | Discovery packet — **direction NOT locked, founder gate** |
| `truth-sequence-shapes.md` | AW-278 | Discovery packet — **architecture NOT locked, founder gate** |
| `ordinary-last-lines.md` | AW-278 | 24 archetype-keyed screenshot lines |
| `liar-texture-samples.md` | AW-283-adjacent | smooth/brittle/leaky + engineering handoff list |
| `docs/design/the-host.md` v1.1 | canon | **Amended, founder-approved (D-081)** — the only non-draft change |

### Depth beyond launch (post-Rehearsal-1)

`big-top-1899.md`, `boardroom-severance.md`, `manor-gothic.md`,
`sim-reunion.md` — four more full libraries; range proof from most
reduced to maximum Caine.

### Platform proof (D-082/D-083 — strategy tier)

| Artifact | Claim |
| --- | --- |
| `docs/design/authoring/story-to-arc-exemplar.md` | Heist genre: not a mystery engine |
| `docs/design/authoring/daily-case-sample-week.md` | D-034 wedge playable on paper; Murdle-differentiated |
| `docs/design/authoring/writing-for-living-stories.md` | Authoring is teachable craft |
| `docs/design/authoring/living-worlds-genre-studies.md` | Monster RPG + couch co-op run on the same five primitives |
| `docs/product/vision-narrative.md` | Brand DNA (Layer 2 thesis) |
| `docs/product/frontier-vision.md` | H1–H4 map; non-LLM AI stack; NOS endgame |

## 2. Adversarial Review Findings (this session, self-audit)

Findings from a verification pass over everything above. F1–F3 are
fixed or fixable now; F4–F8 are decisions or Wednesday work.

- **F1 — Slot sprawl (real defect).** Grep-verified: 38 distinct
  `{{slot}}` tokens across all artifacts, including one-off variants
  that would each become a runtime bug: `{{time_1}}/{{time_2}}/
  {{time_3}}` and `{{suspect_3}}` (truth-sequence samples only),
  `{{flavor_clause}}` (identity doc only), `{{count}}` (superlatives,
  never whitelisted). **Resolution:** canonical slot registry in §5
  below; conversion to runtime format must validate against it and
  normalize the one-offs.
- **F2 — Stale cross-reference.** 00-direction open Q1 said "four
  libraries"; six exist. **Fixed this session**, with the per-wrapper
  diegesis recommendation added.
- **F3 — Audience-handle collision.** Boardroom Severance and Sim
  Reunion both use "everyone." Defensible (both institutional-voice
  wrappers) but unflagged until now. Folded into the existing
  per-wrapper-address decision (Q6).
- **F4 — Review bandwidth is the binding constraint.** ~4,000 lines of
  draft vs one founder. Untiered, review stalls and drafts rot.
  **Resolution:** the tiered protocol in §3 — total founder time
  budgeted at ~2.5 hours across the week, not one heroic sitting.
- **F5 — Voice-name clearance (previously unconsidered).** "Vesper"
  is now load-bearing across 468 lines, merchandising notes, and the
  art bible — and has known collisions in the cultural namespace
  (cocktail; the Bond character; existing tech products). The repo has
  a trademark-clearance open question for the game name but none for
  the host name. **Action:** add Vesper clearance to the same legal
  pass as the Nightcap mark. Cheap now; brutal after launch.
- **F6 — Recordability as review criterion (previously implicit).**
  the-host.md §9 commits Vesper's lines to future real-actor
  recording. The unhinged/absurd registers (wa-7 entries, Sim Reunion
  drops) are the stress cases. **Action:** during the Tier-2 read,
  ask of each probe line: "can a director direct this?" If not, it
  fails §9 even if it reads well.
- **F7 — Localization economics (previously unconsidered, and good
  news).** Pun-dependent lines (wa-3 entries) won't translate — but
  the refrain architecture means localization is *re-authoring a
  finite line library per language*, not re-solving generation
  quality. That's a per-language cost ceiling competitors using
  free-generation don't have. Note for the cost model when
  internationalization is ever scoped; no action now.
- **F8 — The drafts are not tested against the engine.** Nothing
  tonight has touched a running session. Slots may not match what
  case resolution actually resolves (e.g., does the engine resolve a
  `{{weather}}`? an `{{errata}}`?). **Resolution:** Wednesday's
  conversion task starts with a schema-fit audit: every slot in §5
  mapped to a resolvable state field or explicitly added to case
  generation's output contract. No library line ships unmapped.

## 3. The Founder Review Protocol (your week, budgeted)

Do these in order. Each tier is independently valuable; stop anywhere
and the work above the line is usable.

**Tier 1 — Unblocking decisions. ✅ COMPLETE 2026-07-20/21.**
All five recorded (D-084 through D-088):

1. ✅ Diegetic presence — **D-084**: one entity, per-wrapper
   declaration; all six current libraries resolve to witness.
2. ✅ AW-280 clue direction — **D-085** (provisional): object-forward
   spine + testimony valve; ledger rejected (art-direction §4.4).
3. ✅ AW-278 reveal architecture — **D-086**: Unmasking spine + inline
   crediting; Confession deferred to post-Rehearsal-1 premium.
4. ✅ Launch/rehearsal pair — **D-088**: launch stays Séance + Orbital;
   Rehearsal 1 tests Séance + Big Top (decoupled).
5. ✅ Race-master moods + nudge — **D-087**: four moods into
   the-host.md v1.2; hybrid escalation nudge (TV room → TV named →
   silent UI phone), §7 preserved.

**Surfaced during Tier 1 (not a Tier 1 item):** the founder raised
whether interrogating AI suspects delivers world-class gameplay. This
is captured in `../design/authoring/interrogation-experience-review.md`
and routed to a dedicated session (founder chose: finish Tier 1
first). It gates nothing here but is the single highest-value open
gameplay question — recommended de-risk is a 30-minute paper test
before Rehearsal 1.

**Tier 2 — Taste calibration (~60 min, any evening this week).**
Read the six wrong-accusation sections + each library's flagged probe
lines (each library's Review Notes lists its two). You are answering
exactly one question per line: *"is this Vesper?"* Kill list > edit
list — cutting is cheap, line inventory is over minimum everywhere.
Apply the F6 recordability test to every probe.

**Tier 3 — Strategy reactions (~45 min, before Wednesday planning).**
`vision-narrative.md` (is "stories that are alive" the phrase?),
`frontier-vision.md` (is "narrative operating system" the endgame
frame?), genre studies (is The Long Thaw an exhibit or a real future
candidate?). Nothing gates on these; they steer Wednesday's discovery
passes.

**Explicitly NOT your job:** proofreading 468 lines. Tier 2 sampling
plus the Wednesday code review covers quality; your scarce resource is
taste, spend it only where taste decides.

## 4. The Roadmap (Wednesday forward, gated and sequenced)

Every step names its gate. Nothing starts before its gate clears.

**Step 0 (Wed AM) — Code review of this branch.** The queued
`/code-review` (renewable model). Gate: none. Output: findings fixed
on-branch before founder merge decision.

**Step 1 (Wed) — Merge decision.** One PR from
`claude/vesper-line-libraries`. Gate: Tier 1 answers + code review.
Draft status survives merge — merged-as-draft content is still gated
by per-task founder sign-off (the M5-I collaboration checkpoints).

**Step 2 — Schema-fit audit + slot registry enforcement (F8).**
✅ **DONE 2026-07-21** — `../design/authoring/schema-fit-audit.md`.
Findings resolved: Tier 1 slots map to `ResolvedCase`; Tier 2 slots
depend on AW-279 (identity) and AW-284 (timer/scoring); Tier 3 gap
closed by **ADR-0017 / D-089** — location & time promoted to
structured case fields, other dressing to a per-wrapper dressing pack.
That schema change is now the **prerequisite migration** for Step 4
and must land (migration + review per AGENTS.md) before conversion.

**Step 3 (Wed/Thu) — AW-284 execution.** Race scoring + accusation
state — the plan PR (#257) is already founder-handed-off and is the
critical path to the slice; superlative *selection* logic lands here
consuming the race-master supplement. Gate: none beyond its existing
plan (it never depended on tonight).

**Step 4 (Thu/Fri) — Runtime conversion.** Rehearsal-pair libraries
(Séance 1928 + **Big Top 1899**, per D-088) + identities +
race-master lines into engine-consumable content, with D-070 hints
preserved. **Prerequisite: the ADR-0017 / D-089 migration** (structured
location/time + dressing pack) plus a refrain-resolver component (none
exists yet — the audit confirmed the pipeline is declared but unbuilt).
Big Top adds `{{stage_name}}` (dressing pack) and needs a rehearsal
identity pool via AW-279. The v1 *launch* pair remains Séance + Orbital;
converting Orbital's content is launch work, not rehearsal-blocking.
Gate: Step 1 (merge) + ADR-0017 migration + AW-279 + Tier 1 answers.

**Step 5 (following week) — AW-277/279/280 content tasks close.**
Each cites tonight's artifacts as founder-reviewed evidence per its
collaboration contract; AW-280 authors its full library against the
locked direction. Gate: Tier 1 #2 + Tier 2 kill list applied.

**Step 6 — AW-278 truth sequence.** Built to the locked architecture,
consuming `ordinary-last-lines.md` via archetype tags (add the tag to
case generation output if absent — Step 2 will have said). Gate:
Tier 1 #3.

**Step 7 — AW-285/286: rendering + the rehearsal slice.** With
content real, TV/phone rendering has something true to render.
**Gate: everything above. Output: Rehearsal 1.** The breadth test you
named as priority one — now with six beats of authored voice, both
launch skins, race-master coverage, and reveal accounting to test.

**Parallel track (any time, renewable model):** neutral-core
extraction from the six libraries; Vesper name clearance (F5) added
to the trademark pass; discovery passes on frontier near-items
(diffusion pipeline, voice tiering, adaptive score) — each behind the
cost-policy lens, none blocking the rehearsal.

## 5. Canonical Slot Registry (F1 resolution)

The complete verified inventory, normalized. Conversion validates
against this table; anything not here fails the build.

**Universal (all wrappers):** `{{suspect}}` `{{suspect_2}}`
`{{victim}}` `{{killer}}` (Beat 6 only) `{{detective}}` `{{location}}`
`{{time}}` `{{evidence}}` `{{drink}}` `{{occasion}}` `{{callback}}`
`{{minutes}}` `{{seconds}}` `{{count}}` (superlatives only)

**Per-wrapper:** Big Top `{{stage_name}}` · Orbital `{{deck}}`
`{{tier}}`* · Boardroom `{{floor}}` `{{title}}` · Manor `{{room}}`
`{{weather}}` · Sim Reunion `{{tier}}` `{{errata}}`
*(`{{tier}}` appears in both sci-fi wrappers — shared sci-fi slot.)*

**Identity/briefing docs only:** `{{detective_name}}` `{{flavor}}`
`{{habit}}` (never on shared surfaces — AW-279 privacy contract);
`{{flavor_clause}}` → **normalize to `{{flavor}}`** at conversion.

**Daily Case only:** `{{case_no}}` `{{next_case_no}}` `{{day}}`
`{{day_ref}}` `{{claim_count}}` `{{flag_count}}`

**Sample-doc-only (do NOT whitelist; rewrite at library authoring):**
`{{time_1..3}}`, `{{suspect_3}}`, `{{complication_object}}` — these
exist in discovery samples, not in refrain libraries.

## 6. Risk Register (the productively adversarial section)

Ranked by expected damage to the billion-dollar path:

1. **Rehearsal slip via review stall.** 4,000 draft lines could eat
   founder weeks. *Mitigation: §3's tiers — 2.5 budgeted hours; only
   Tier 1 gates engineering.*
2. **Frontier gravity.** The H4 documents are seductive; every hour
   on them before Rehearsal 1 is misallocated. *Mitigation: they gate
   nothing, and their own text says so. Hold that line — including
   against yourself.*
3. **D-081 lands wrong in a real living room.** A roast that stings a
   real guest damages the product's warmth promise at the moment of
   first contact. *Mitigation: Tier 2 kill list now; and Rehearsal 1
   should deliberately include wrong accusations so roast reception is
   an observed result, not a hope. Add it to the rehearsal script when
   AW-286 plans the slice.*
4. **Draft-canon bleed.** Merged draft content starts getting treated
   as approved (the exact AW-267/AW-281 failure your process memory
   records). *Mitigation: DRAFT headers stay until per-task sign-off;
   the M5-I checkpoint gates remain the authority, not merge status.*
5. **Voice inconsistency at conversion.** Engineering "normalizes"
   lines while converting and flattens the shifts. *Mitigation: the
   conversion contract is verbatim-text-plus-metadata; any wording
   change requires the founder loop. Put it in the Step 4 task.*
6. **Single-author voice risk.** All 468 lines came from one model on
   one night. Consistent — but a monoculture. *Mitigation: the craft
   guide + libraries are now a training corpus; future authors
   (human or model) write against them and get reviewed against
   the-host.md. The bible remains the authority, not tonight's
   output.*

## 7. Definition of Done for Tonight's Content

Tonight's work is DONE when: (a) Tier 1 answers recorded in the
decisions log; (b) branch merged with drafts intact; (c) launch-pair
content converted and rendering in the AW-286 slice; (d) Tier 2 kill
list applied; (e) each fed task (AW-277/278/279/280) closes citing
its artifact + founder sign-off. Everything else tonight produced —
depth wrappers, platform docs, frontier map — is *ahead of need* by
design and carries no deadline.
