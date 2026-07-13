# Arcwright Strategic Blueprint

> Current version: v1.1
> Last updated: 2026-07-12
> v1.1: game design deep-dive extracted into spec 0068 (game experience
> quality bar) + fun-observation rubric; §3 and §10 updated accordingly
> Status: Proposal — strategy brainstorm output, NOT approved build scope
> Canonical path: docs/superpowers/specs/2026-07-12-arcwright-strategic-blueprint-design.md

**Scope discipline note (per AGENTS.md):** This document is a strategic review and
blueprint. Nothing in it becomes build scope until it is recorded in
`docs/product/decisions-log.csv` and, where required, an ADR or approved spec.
Items that would need such approval are flagged `[NEEDS APPROVAL]`. Items that
are already approved scope are cited to their existing decision record.

---

## 0. Executive Summary

Arcwright's strategy documents are unusually good. The eight architecture
principles, the proof-gate discipline, the Horizon model, and the
platform-stress-test framing for game selection are the blueprint most startups
never write. The problem is not the plan. The problem is that **the company is
ahead of its own proof chain**: five milestones of engine work exist, and zero
real humans have ever played a session (Rehearsal 1 closed unexecuted, per spec
0067). Every strategic risk in this document is downstream of that one fact.

The blueprint therefore has one prime directive and eight supporting pillars:

**Prime directive: convert built software into observed human joy, on the
shortest possible path, and let everything else re-sequence around what those
sessions reveal.**

The eight pillars:

1. **Games** — make Nightcap's first 10 minutes and last 5 minutes
   world-class; treat Daily Case as the retention/data engine; keep Monster
   RPG as the H2 ambition anchor.
2. **Engine** — the moat is *authorship enforcement + deterministic state +
   knowledge provenance + cost routing + session telemetry*, a stack no
   competitor has assembled. Name it, defend it, and close the latency gap.
3. **Verticals** — the same knowledge-graph constraint that stops an NPC from
   leaking clues is **canon enforcement** for IP owners. That is the wedge
   into animation/streaming and licensed-character experiences.
4. **Business** — unit economics are already exceptional (~$0.09–$0.13 AI cost
   vs. a $30+ price anchor). The unknown is willingness-to-pay and repeat
   rate, both only learnable from real sessions.
5. **Go-to-market** — Nightcap is structurally a streamable, shareable party
   game (the Jackbox distribution playbook). The reveal moment and the recap
   artifact are the growth surfaces.
6. **Trust** — trademark clearance, adversarial safety playtests, and privacy
   posture for group memory are the three trust items that can each
   independently sink the launch.
7. **Speed** — the operating system already exists (proof gates, agent
   workflow, honest specs). The one broken behavior to fix permanently:
   gates must never be closed without being run.
8. **Focus** — an explicit not-doing list, because a solo founder's biggest
   competitor is their own surface area.

There is no way to "guarantee success." The closest available substitute is
**shortening the loop between building and observing real players, and never
letting a proof gate pass unearned.** The repo's own documents already say
this; this blueprint's job is mostly to make it impossible to ignore.

---

## 1. Ground Truth (2026-07-12)

What is true right now, stated without spin:

- **Built:** Arc execution, knowledge graph, character behavior pipeline,
  safety layers (L1/L2/L3), model routing with evals, session persistence and
  resume, SSE event fanout, TypeScript SDK, Nightcap web experience with
  join-in-30-seconds flow, mini-game runtime with two production mini-games,
  Tell Me Something True, cost tracking, five MVP telemetry signals.
  507+ Python tests, green lint, typechecking across three TS packages.
- **Not proven:** That any group of humans enjoys it. Rehearsal 1 (AW-259) was
  closed 2026-06-27 without being executed. The M4 exit gate ("real humans on
  real devices") has not actually been passed. The PRD's pre-build
  Wizard-of-Oz validation signal (personalization perception) has never been
  confirmed against the production system.
- **Known product risks already on file:** Nightcap trademark conflicts
  (Studio Nightcap, NBA Nightcap) with counsel not engaged; pricing untested;
  enterprise buyer interviews (an H1 requirement) not started; external
  developer demand validation not started.
- **In-flight remediation:** Spec 0067 and its Phase 0–4 plan are the correct
  response and are already approved. This blueprint does not replace that
  plan; it wraps strategy around it.

---

## 2. The Prime Directive: Pay Down Validation Debt

**Every week of engine work done before real-session evidence arrives is a
week bet on assumptions.** The portfolio of assumptions currently unvalidated:

| Assumption | Risk if wrong | Only way to learn |
| --- | --- | --- |
| Groups feel the personalization ("this was made for us") | The core thesis fails; platform value prop collapses | Rehearsals + M6 qualifying sessions |
| A host will pay >$30 per session | Business model resets | Price the 5 qualifying sessions' follow-ups |
| Session pacing works with real human chaos | Live-play rework across pacing engine | Rehearsal 1 blocker log |
| Phone+shared-display UX survives real living rooms | UX rework | Rehearsal 1 |
| The reveal lands emotionally | Nightcap's promise ("a reveal worth earning") fails | Rehearsals |

**Action:** Execute spec 0067 Phases 0–1 before *any* other new work, including
anything else in this blueprint. Then let the Rehearsal 1 blocker log
re-prioritize M5. This is already-approved scope; it needs execution, not
approval.

**Permanent rule proposal `[NEEDS APPROVAL — decisions-log entry]`:** A
milestone exit gate that requires a real-world event (rehearsal, playtest,
interview) may only be closed with an attached evidence artifact (blocker log,
recording notes, interview record) committed to `docs/roadmap/operations/`.
Closing a gate task without its evidence artifact is treated as a process
violation, same severity as skipping tests.

---

## 3. Games People Love (Game Designer + Artist View)

> **Executable version of this section:** the concrete quality bars, content
> standards, aesthetic charter, and instrumentation now live in
> `docs/specs/0068-game-experience-quality-bar.md` (fun pillars, per-beat
> moment map, identity-card/clue/narrator writing standards, killer
> experience standard, mini-game feel rules, M5-G aesthetic charter) and
> `docs/roadmap/operations/fun-observation-rubric.md` (used at every human
> session from Rehearsal 1 onward). This section keeps the strategic
> rationale; spec 0068 is the doc implementers work from.

### 3.1 Nightcap: the two moments that decide everything

Party games live or die on two windows:

**The first 10 minutes (time-to-wow).** Target: from "host opens URL" to
"every player has laughed or leaned in" in under 10 minutes. Concretely:
- Join flow is already specced at <30s — protect it fiercely in rehearsals.
- The character-identity delivery moment (each player privately reading who
  they are) is the first personalization proof. It should read like a gift,
  not a form: specific, slightly dangerous, immediately actionable ("You owe
  the victim money. Nobody here knows. Keep it that way.").
- Measure time-to-first-laugh in rehearsals as an informal but tracked signal.

**The last 5 minutes (the reveal).** The PRD promise is "a reveal worth
earning." The reveal is also the *shareable* moment — the thing groups
retell at work on Monday. Design review question for after Rehearsal 1: does
The Truth land as a *story* (narrator-delivered, dramatic, personal) or as a
*scoreboard*? If it reads as a scoreboard, that is the highest-leverage
content fix in the game.

### 3.2 The replay engine

"They wanted to play again" is the stated bar. Structural replay drivers,
in order of current strength:

1. **Variance that shows** (strong today): era/occasion themes, killer
   rotation, generated cast. Make variance *visible at purchase time* — the
   host should see "tonight could be a 1920s séance or a 2087 orbital gala"
   before paying.
2. **Role envy** (free): "next time *I* want to be the killer" is the
   cheapest replay motor in the genre. The recap should tease it ("Marcus has
   now survived two accusations. Someone should look into Marcus.").
3. **Group memory** (approved v1.1, D-051): Continuity is correctly deferred,
   but note for v1.1 planning that the *shareable recap artifact* is as much
   a growth feature as a retention feature (see §7). Recommendation
   `[NEEDS APPROVAL — v1.1 spec]`: when v1.1 planning begins, sequence the
   recap artifact first within Continuity scope, ahead of group-memory
   personalization, because it compounds distribution.

### 3.3 Daily Case: quietly the most strategic game

Daily Case (solo, 5 min/day, week-long interrogation) is positioned in the
docs as a platform-reuse proof. It is more than that:

- **It is the retention product.** Nightcap is occasion-gated (you need a
  party). Daily Case is habit-gated (you need 5 minutes). A daily habit
  product feeds telemetry volume — the Tier 2 data flywheel — orders of
  magnitude faster than party sessions can.
- **It is the cheapest marketing surface.** Solo + async means it can be
  free/cheap with tiny per-session cost, funneling players toward hosting
  Nightcap nights.
- **It stresses provenance and cross-session memory** harder than anything
  else in the portfolio, which is exactly the platform wedge (D-034).

No sequencing change proposed — it stays behind M6 proof — but when it
ships, market it as a product, not a tech demo.

### 3.4 Monster RPG

Correctly parked at H2. One addition for its design phase: it is the first
game where **latency and session length economics** dominate (long sessions,
high call volume). Its design brief should include a per-chapter cost and
latency budget from day one, the same way Nightcap's brief included
platform-capability stress tests.

### 3.5 Craft bar (Artist view)

M5-G (visual identity) is currently "Tier 2 polish." Correct for the proof
phase. But before M6 *outside* qualifying sessions: first impressions of
generated text quality, narrator voice consistency, and visual coherence on
the shared display are part of what "unprompted enthusiasm" measures. Budget
one deliberate craft pass (narrator voice guide adherence, typography,
shared-display motion) between Rehearsal 2 and M6. Ugly-but-magical wins
rehearsals; magical-and-polished wins strangers.

---

## 4. The Engine Nobody Else Has (Architect / CTO View)

### 4.1 The moat, stated precisely

Individually, none of Arcwright's components is unique. **The assembled stack
is:**

1. **Deterministic arc execution with authored constraints** — the engine,
   not the LLM, owns state. (Every "AI game master" competitor does the
   opposite and inherits incoherence.)
2. **Knowledge graph with provenance** (who knows what, since when, from
   whom) enforced *before every generation call* — mandatory, not optional.
3. **Authored-vs-generative dial per element** — human authorship is a
   first-class, enforceable contract, not a prompt suggestion.
4. **Budget-first provider-agnostic routing + caching discipline** — cost as
   an architectural input (the Death-by-AI failure is designed out).
5. **Session telemetry as a data asset from session one** — the Tier 2
   fine-tuning flywheel competitors on the same APIs cannot replicate.

**Positioning sentence to standardize everywhere:** *Arcwright is the
narrative runtime that keeps the human author in charge: deterministic story
state, provable character knowledge, and per-session economics — under any
model provider.*

### 4.2 Competitive map (as of mid-2026 knowledge)

| Player | What they are | Why Arcwright is different |
| --- | --- | --- |
| Inworld | General NPC/agent infra; pivoted toward broad AI runtime | No arc contract, no authored-constraint enforcement; explicitly the pivot Arcwright's docs reject |
| Convai | Embodied NPC conversation for Unity/Unreal | Character-level, not story-level; no session/arc/knowledge substrate |
| Charisma.ai | Interactive story authoring + playback | Closest in spirit; weaker on deterministic multi-player session state and knowledge provenance as infrastructure |
| Hidden Door | Consumer social roleplay in licensed worlds | A destination app, not middleware; validates the canon-safety demand Arcwright can serve as infra |
| Latitude / AI Dungeon | LLM-authored freeform narrative | AI-as-author — the opposite thesis; incoherence is the known failure mode |
| Character.AI et al. | Consumer companion chat | Not narrative, not multiplayer, not authored |
| Jackbox | Party game distribution king (no AI) | Format teacher, not competitor; also the distribution playbook to copy |
| Mursion | Enterprise simulation training (human-in-loop) | Price anchor ($49/person/30min) proving enterprise willingness-to-pay |

**Watch item:** the credible future threat is not these companies; it is a
foundation-model provider shipping "narrative sessions" as a primitive. The
defense is the same either way: proprietary session telemetry, authored-arc
ecosystem, and being the *neutral* layer across providers (principle 8).

### 4.3 Technical priorities the current roadmap underweights

1. **Latency budget as a named requirement `[NEEDS APPROVAL — ADR]`.** Cost
   has a whole architecture section; latency has none of equivalent weight.
   In a live room, a 12-second pause after an accusation is a product
   failure invisible in every offline eval. Proposal: define per-interaction
   latency budgets (e.g., player-visible generation p95 ≤ 4s; pacing/safety
   calls invisible), instrument them in telemetry (realized latency per call
   category already flows through generation logs), and add latency to the
   routing table's quality-tier semantics so a tier can trade quality down
   to meet the room's tempo. Rehearsal 1 will produce the evidence for the
   exact numbers.
2. **Player-drop AI takeover (#138)** — already flagged in 0067 Phase 2;
   reaffirmed here as the top playtest-critical gap. A party game that
   cannot survive one bathroom break is not shippable.
3. **Continuity/coherence eval suite (AW-272)** — the knowledge-leak-rate
   eval is the moat's proof instrument. When external developers or IP
   partners ask "how do you *know* characters don't leak?", this suite is
   the answer. Treat its metrics as marketable numbers, not internal QA.
4. **The data flywheel needs a schema owner.** Telemetry exists; the Tier 2
   trigger is "thousands of structured, labeled sessions." Define now (cheap,
   docs-only) what a *labeled* session means — which signals constitute
   quality labels (completion, replay intent, personalization-perception
   marks, human blocker-log annotations) — so H1 sessions accumulate as
   training-grade data rather than logs to be re-mined later.
   `[NEEDS APPROVAL — spec when acted on]`

### 4.4 What not to build (reaffirmed)

No self-hosting before ~25–50k sessions/month (13.3). No Unity/Unreal SDKs
before demand signal. No visual editor before Phase 2 of Visual Storyworld
triggers. No fine-tuning before Tier 2 conditions. The architecture docs
already say all of this; it stays said.

---

## 5. Verticals Beyond Games (Visionary View)

The PRD names enterprise, museums, language learning. The sharpest framing
for the biggest verticals:

### 5.1 Animation / film / interactive streaming: sell "canon safety"

IP owners' blocking fear about AI character experiences is *canon violation
and brand damage* — a beloved character saying something wrong, revealing
something they shouldn't know, or breaking tone. Arcwright's knowledge graph
+ authored constraints + safety rails is precisely a **canon enforcement
engine**: the character *provably cannot reference* what is outside their
knowledge state, and the arc *provably cannot leave* authored bounds.

- Product shape: "interactive episodes" — a human-authored arc set in a
  licensed world, where the audience talks to characters between authored
  beats. The studio authors the arc; Arcwright guarantees the rails.
- Proof asset: the AW-272 eval suite's knowledge-leak rate is the number an
  IP counsel asks for.
- Sequencing: H2-earliest, and only via a design-partner conversation, not a
  build. The H1 action is zero engineering: **when demo footage exists, add
  2–3 IP/animation contacts to the same interview motion already required
  for enterprise buyers** (PRD open questions, High). `[NEEDS APPROVAL —
  decisions-log entry to extend the interview mandate]`

### 5.2 Enterprise team-building (already H2 scope)

Reaffirm the existing plan (D-046, Mursion price anchor). One addition: the
debrief beat (already a named platform capability to validate) is the
enterprise product. HR buys the debrief; the game is the delivery vehicle.
Design the H1 buyer interviews to test that specific claim.

### 5.3 Education / museums / location-based (parked, correctly)

No action in H1. The platform principle that keeps these free options open is
surface agnosticism — already enforced.

---

## 6. Business Model & Unit Economics (CEO / CFO View)

### 6.1 The economics are a strength; the price is a guess

- AI cost ~$0.085–$0.125/session cached (13.2); infra $0.05–$0.25 amortized.
- Anchor: >$30/session host-pays (approved north star). Even at $15, gross
  margin is >95% at modest volume. **Price is not the risk; demand is.**
- Action (already implied by PRD, restated as explicit sequence): the five
  M6 qualifying sessions are also the pricing lab. After each session, make
  the host a real offer for their *next* session at a real price (vary $19 /
  $29 / $39 across groups) and record acceptance. Willingness-to-pay data
  from five groups beats any survey. `[NEEDS APPROVAL — playtest runbook
  addition, M6-A]`

### 6.2 Revenue sequencing (no change to Horizons, one sharpening)

H1: Nightcap paid sessions (only revenue focus). H2: enterprise pilots (the
$5–15/person × Mursion-anchor gap is large) + Monster RPG. H2-late/H3:
platform tiers as documented. **Do not let platform pricing design consume
H1 time** — the four-tier model is already documented well enough.

### 6.3 Fundraising posture

The story writes itself *only after* M6: "sessions humans paid for, ~97%
gross margin, telemetry flywheel, engine that generalizes (two arcs live)."
Raising before the personalization-perception + willingness-to-pay evidence
means selling the vision at a discount. Recommendation: collect the M6
evidence first, then decide bootstrap-vs-raise from strength. The H1 gate
framework already encodes this; honor it.

### 6.4 Kill / pivot criteria (making "guarantee success" honest)

Success cannot be guaranteed; unrecoverable failure can be made nearly
impossible by predefining pivots. Proposal for the decisions log
`[NEEDS APPROVAL]`:

- If M6 sessions complete but the **personalization gate fails** twice after
  diagnosis-and-fix cycles → the thesis pivots from "felt personalization"
  to "effortless hosting" (Nightcap as the zero-prep murder mystery, which
  rehearsal evidence may show is the actual purchase driver). The engine
  survives either thesis.
- If hosts complete sessions but **decline paid repeats** at every price
  point → pivot revenue weight toward enterprise (price-insensitive,
  outcome-driven) ahead of consumer scale.
- If both fail → the platform IP (knowledge-graph-constrained characters)
  is repositioned toward the canon-safety vertical (§5.1) with games as
  demos. This is the deepest fallback and still a venture-scale market.

---

## 7. Go-to-Market & Growth (Marketer View)

### 7.1 The Jackbox playbook, upgraded

Jackbox grew through streamers and living rooms: the game is the content.
Nightcap is structurally *better* content than Jackbox titles — it has a
narrative reveal, secrets, and betrayal — but only if two things are true:
spectators can follow the shared display alone, and sessions produce a
retellable artifact.

Growth surfaces, in priority order:

1. **The recap artifact** (v1.1, D-051): design it as the share object —
   case name, cast, the accusation history, one "memorable moment" pull
   quote. A group chat screenshot is the acquisition channel. (Sequencing
   note in §3.2.)
2. **The reveal as clip:** The Truth beat on the shared display should be
   built to be filmed — paced, visual, name-dropping the players. People
   film their friends' reactions; that clip is the ad.
3. **Streamer kit (post-M6):** a spectator-legible shared display already
   exists by design; add nothing until M6, then recruit 5–10 mid-size party
   game streamers manually.
4. **Waitlist from day of first demo footage:** a one-page site (name
   pending trademark, §8.1), the reveal clip, an email list. Near-zero cost,
   compounds early. `[NEEDS APPROVAL — it touches naming/trademark timing]`

### 7.2 The platform's marketing is the games (reaffirmed)

No dev-rel spend, no API marketing in H1. The H2 developer beta is gated on
10 recorded external-developer feedback sessions (already in PRD open
questions). The only H1 platform-marketing artifact worth making is a single
technical blog post / demo video: "watch the knowledge graph stop a character
from leaking" — because it doubles as the IP-partner conversation opener.

---

## 8. Trust, Safety, Security, Legal (Security / Counsel View)

1. **Trademark (CRITICAL, already flagged, still unactioned):** "Nightcap"
   has known conflicts and counsel is not engaged. Engage trademark counsel
   **before** any public waitlist, footage, or M6 outside sessions create
   public attachment to the name. Budget for the possibility of renaming;
   a rename after public traction costs 10x. This is the single cheapest
   catastrophic-risk reducer available this quarter.
2. **Adversarial safety playtest (AW-232/233):** already correctly sequenced
   before M6. Add one scenario class to its plan: *host-as-adversary*
   (the paying customer trying to weaponize the narrator against a guest),
   since the host has elevated inputs (seed questions, theme choice).
3. **Group memory privacy (v1.1):** the story bible's consent/deletion
   posture is right. Before v1.1 ships, write the plain-language data page:
   what is stored, for whom, deletable how. Privacy posture is a selling
   point for the enterprise vertical; build the habit early.
4. **Enterprise trust runway (H2):** SOC 2 is already named in the tier
   plan. The cheap H1 move is hygiene that auditors later reward: secrets
   handling per the Hard Rules (already enforced), access logs, and the
   existing safety-activation logging. No new work; just don't regress.
5. **Minors:** Nightcap's content posture (murder, alcohol-adjacent themes)
   implies a 17+/18+ audience statement. Decide and state it before outside
   sessions; it simplifies both safety-rail tuning and legal exposure.
   `[NEEDS APPROVAL — decisions-log entry]`

---

## 9. The Operating System for Speed (Execution View)

The repo already runs a strong system: proof gates, specs-before-code, role
skills, honest surveys (0067 is a model of self-honesty). Three upgrades:

1. **Evidence-or-it-didn't-happen rule** (§2). One-line process change,
   prevents the only serious process failure observed to date.
2. **Weekly cadence anchored on sessions, not code.** The founder's weekly
   review question changes from "what merged?" to "when is the next time a
   human plays, and what will we learn?" Every week without a scheduled
   human session is flagged in the weekly note. (No tooling needed; it's a
   habit.)
3. **Hiring trigger (already documented, sharpened):** the H1 proof-signal
   framework decides *when*; rehearsal evidence decides *what*. If blocker
   logs fill with UX/product findings, the first hire is a product-minded
   generalist; if they fill with infra findings, a platform engineer. Do not
   pre-commit the role before the logs exist.

**Agent workforce note:** the multi-agent operating model (specs 0018/0019/
0021) is a real force multiplier and is why a solo founder has a five-
milestone platform. Its known failure mode is the same as any delegated
workforce: optimizing for closed tickets over verified outcomes. The §2 rule
is the systemic fix.

---

## 10. Prioritized Action Plan

**NOW (0–30 days) — everything here before anything below**

| # | Action | Why | Evidence gate | Approval |
| --- | --- | --- | --- | --- |
| 1 | Execute 0067 Phase 0 (green tests, truthful statuses) | Restore ground truth | Full suite green | Approved (0067) |
| 2 | Execute 0067 Phase 1; run Rehearsal 1 with real humans | The prime directive | Committed blocker log | Approved (0067) |
| 3 | Engage trademark counsel on Nightcap | Cheapest catastrophe insurance | Counsel opinion on file | Founder action |
| 4 | Adopt evidence-or-it-didn't-happen gate rule | Prevent repeat of AW-259 | Decisions-log entry | [NEEDS APPROVAL] |
| 5 | Add latency measurements to Rehearsal 1 observation list | Feeds §4.3 ADR with real numbers | Latency notes in blocker log | Trivial |
| 5a | Approve spec 0068 (game experience quality bar) | Makes "extremely fun" testable before humans arrive | Spec status → Approved | [NEEDS APPROVAL] |
| 5b | Use fun-observation rubric at Rehearsal 1 | Fun signal + personalization-perception quotes captured | Filled rubric committed | Done (wired into quickstart) |
| 5c | Pre-rehearsal content pass against 0068 §3 (identity cards, clues, narrator lines) | The words players read are the cheapest quality lever available now | Content review notes; prompt changes via Hard Rules flow | Gated on #5a |

**NEXT (30–90 days)**

| # | Action | Why | Evidence gate | Approval |
| --- | --- | --- | --- | --- |
| 6 | 0067 Phase 2 (#138 AI takeover, #137) triaged with blocker log | Playtest-critical | Merged + tested | Approved (0067) |
| 7 | 0067 Phase 3 cloud deploy + Rehearsal 2 | M6 prerequisite | Cloud dry-run + blocker log | Approved (0067) |
| 8 | Latency-budget ADR from rehearsal data | §4.3 | ADR accepted | [NEEDS APPROVAL] |
| 9 | Enterprise + IP-partner interviews once demo footage exists (10 + 2–3) | Already-required H1 item, extended | Interview records in docs | Partially approved (PRD); IP extension [NEEDS APPROVAL] |
| 10 | Visual design system Stage A (token extraction + "midnight" base restyle per spec 0069) before Rehearsal 2; Stages B (five staged sequences) and C (two theme skins) in the M5-G/M6 window, sized by Rehearsal 1 evidence | §3.5; strangers judge polish; polish priority B8 → B2 → B6 | Stage A screenshots; Stage B sequence captures; 0068/0069 acceptance criteria | Within M5-G scope; spec 0069 [NEEDS APPROVAL] |
| 11 | Pricing offers embedded in M6 runbook ($19/$29/$39 across groups) | Real willingness-to-pay data | Offer outcomes recorded | [NEEDS APPROVAL — M6-A] |
| 12 | Age-rating / audience statement decision | §8.5 | Decisions-log entry | [NEEDS APPROVAL] |

**LATER (90+ days, gated on M6 outcomes)**

| # | Action | Trigger |
| --- | --- | --- |
| 13 | M6 qualifying sessions → H1 proof analysis (AW-243/244) | Phase 4 chain complete |
| 14 | Labeled-session schema spec (data flywheel, §4.3.4) | Post-M6, pre-volume |
| 15 | v1.1 Continuity planning with recap-artifact-first sequencing | M6 passed; D-051 boundary respected |
| 16 | Waitlist site + reveal clip + streamer outreach | Trademark cleared + M6 passed |
| 17 | Fundraise/bootstrap decision from evidence | H1 gate evaluation |
| 18 | Daily Case build (M5-C design → post-M6 execution) | Per existing roadmap |

---

## 11. What We Deliberately Do Not Do

Restated so the not-doing is as documented as the doing:

- No engine features beyond M5 scope until Rehearsal 1's blocker log exists.
- No self-hosted inference, no fine-tuning, no Unity/Unreal SDKs, no visual
  editor beyond documented phase triggers.
- No public API, dev-rel, or platform marketing in H1.
- No pricing-page design, credit-pack mechanics, or billing infrastructure
  beyond per-session tracking until willingness-to-pay data exists.
- No new game concepts beyond the three documented (Nightcap, Daily Case,
  Monster RPG) until the third-game selection criterion (capability-gap
  closure) is applied against real platform evidence.
- No renaming, rebranding, or public naming investment until trademark
  counsel reports.

---

## References

- PRD: `docs/prd/01-overview.md`, `02-requirements.md`, `03-scope.md`, `04-non-goals.md`
- Architecture: `docs/architecture/01-overview.md`, `13-cost-model.md`
- Story bibles: `docs/story-bibles/nightcap-murder-mystery.md`, `daily-case.md`, `monster-rpg.md`
- Current path to playtest: `docs/specs/0067-development-survey-and-path-to-first-playtest.md`
- Game experience quality bar: `docs/specs/0068-game-experience-quality-bar.md`
- Visual design system: `docs/specs/0069-nightcap-visual-design-system.md`
- Fun instrumentation: `docs/roadmap/operations/fun-observation-rubric.md`
- Decisions cited: D-034 (wedge), D-046 (enterprise adaptation), D-051/ADR-0006 (Continuity v1.1), ADR-0010 (gameplay pivots), ADR-0012 (narrative fidelity)
