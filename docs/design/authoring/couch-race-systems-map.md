# Couch Race — Grounded Systems Map

> Current version: v1.0
> Last updated: 2026-07-21
> Status: The canonical inventory of every Couch Race gameplay system,
> each mapped to its authoritative doc / ADR / task / code. Created
> after a design session generated recommendations without grounding in
> already-shipped systems (notably Leverage). **Read this FIRST before
> any Couch Race gameplay design work.** If a proposed design touches a
> system below, start from that system's authority, not a blank page.
> Canonical path: docs/design/authoring/couch-race-systems-map.md
> Maintenance: add a row when a new gameplay system is decided; never
> design a "new" mechanic that duplicates one already here.

## The Integrated Gameplay Loop (founder-confirmed 2026-07-21, D-094)

The one-line truth: **a striking cinematic murder-mystery STORY is the
spine; players gather clues, play minigames to earn Leverage currency,
spend Leverage on advantages and sabotages, interrogate AI suspects to
catch lies, and accuse — racing each other to the truth.**

```
STORY (spine, D-093)
  │
  ├─ Beat 1 Pour     cinematic hook + identities + the death
  ├─ Beat 2 Scene    evidence wave + minigame → Leverage + clues
  ├─ Beat 3 Grill    interrogation: ask, catch contradictions
  │                    (spend Leverage: advantages / sabotages)
  ├─ Beat 4 Twist    recontextualization + minigame → Leverage
  ├─ Beat 5 LastCall countdown, accusations lock
  └─ Beat 6 Truth    cinematic reveal + scoreboard + "again?"

ECONOMY:  minigames + accomplishments ──▶ LEVERAGE ──▶ advantages (self)
                                                    └─▶ sabotages (rivals)
SCORING:  contradiction catches + accusation accuracy/speed ──▶ the race
```

## The Systems (each with its authority)

### 1. Story / Arc / Beats — the spine
- **What:** six-beat Couch Race arc; the mystery drives the night.
- **Authority:** `nightcap/couch-race.arc.json`;
  `docs/story-bibles/nightcap-couch-race.md`; `docs/specs/0072-nightcap-couch-race-v1.md`;
  ADR-0013 (D-071 launch target). North Star: D-093.
- **State:** arc shipped; beats configured.

### 2. Case Generation & Truth
- **What:** deterministic case resolution — killer, motive, method, clue
  web, authorized lies — fixed at session start. AI never decides truth.
- **Authority:** `engine/case/` (`ResolvedCase`); `nightcap/case_skeletons/`,
  `nightcap/case_taxonomy/`; AW-281.
- **State:** shipped (AW-281).

### 3. Knowledge Graph & Claims — the platform primitive
- **What:** who knows what, when, from whom; every suspect answer is a
  claim with provenance; contradiction detection is a provenance query.
- **Authority:** `engine/knowledge/`; claims/contradiction_flags schema
  (ADR-0016); AW-283.
- **State:** shipped (AW-283, PR #256).

### 4. Interrogation (the Grill core loop)
- **What:** authored question intents, knowledge-gated AI answers,
  private tells, claim ledger, contradiction flagging & catches.
- **Authority:** `engine/interactions/` (AW-282, spec 0074, ADR-0014);
  AW-283 (answers/contradictions, spec 0071 lineage);
  story bible §6-7. Design review + decisions: D-085 (clue direction),
  D-090/D-091 (experience), `interrogation-experience-review.md`.
- **State:** loop shipped (AW-282/283). Open: G1/G4/competition model
  (paper test); G2 quote-suspects (AW-292, gated).

### 5. Leverage — advantages & sabotages (the competitive economy)
- **What:** an EARNED resource, separate from question tokens, spent on
  **advantages** (Deep Read, Follow the Thread, Sting Operation) or
  **sabotages** (Rattle the Witness, Listen In, Make Them Wait).
  **Earned through minigames and accomplishments.** This is the primary
  player-vs-player competitive layer.
- **Authority:** `engine/resources/`; ADR-0015; specs 0075;
  design doc `docs/product/nightcap-leverage-advantages-sabotages.md`;
  D-075/D-076; configured in the arc's `resource_effects` (6 effects,
  cost 2-3). Anti-snowballing rules in the design doc (§ floor for
  non-winners, no unrecoverable leads).
- **State:** engine capability shipped (AW-287); 6 effects configured.

### 6. Minigames — engagement, variety, Leverage source
- **What:** swappable Mario-Party-style modules that drive engagement
  and **pay out Leverage currency** (and optionally gate clue quality via
  `clue_fallback`). Thematically loose is OK (D-093). Fun + edge-not-gate
  are the bars; failures are swapped, not patched.
- **Authority:** `engine/mini_games/`; `nightcap/mini_games/`
  (crime-scene-smash, evidence-locker-402, tell-me-something-true);
  AW-288 (beat coverage + TMST), AW-289 (Trivia); D-064/D-079/D-093.
- **State:** 3 games exist; 2 beat-bound (Scene, Twist); coverage
  expansion planned (AW-288/289).

### 7. Scoring & Accusation (the race)
- **What:** deterministic scoring from contradiction catches +
  accusation accuracy/speed; first-correct accusation triggers the
  endgame; superlatives at session end. Leverage balances are public,
  separate from score.
- **Authority:** AW-284; story bible §4 (Last Call, Truth).
- **State:** planned (AW-284, plan PR #257). Open: unified weighting
  (recommendation: minigames→Leverage/edge, catches moderate,
  accusation dominant — the *mystery* decides the night).

### 8. Narration (Vesper) — the host
- **What:** authored refrain libraries + generated specifics; the shift;
  race-master duties; roast (D-081); reveal.
- **Authority:** `docs/design/the-host.md` v1.2; `docs/design/line-libraries/`;
  AW-276 (voice injection), AW-277 (transitions), AW-291 (resolver);
  D-081/D-084/D-087.
- **State:** content authored (DRAFT, PR #261); resolver unbuilt (AW-291).

### 9. Clues / Evidence Economy
- **What:** how information reaches players — group/private/split/targeted
  evidence, provenance, evidence-to-intent unlocks; object-spine +
  testimony-valve (D-085).
- **Authority:** AW-280; `clue-release-shapes.md`; `engine/case/`
  (EvidenceEntry); D-080 (evidence via knowledge graph).
- **State:** direction locked (D-085); location/time structuring +
  dressing pack (ADR-0017, AW-290).

### 10. Twist
- **What:** deterministic mid-case revelation; reorders suspicion, never
  changes whodunit; 12 authored families.
- **Authority:** `twist-menu.md`; arc twist beat; story bible §4.
- **State:** menu authored (DRAFT).

### 11. Reveal (The Truth)
- **What:** Unmasking spine + inline crediting (D-086); Vesper's
  3-movement voice; ordinary last lines.
- **Authority:** AW-278; `truth-sequence-shapes.md`, `ordinary-last-lines.md`;
  D-086.
- **State:** architecture locked (D-086); build pending.

### 12. Presentation (D-070) — animation + audio
- **What:** story is staged audiovisual sequences; content events carry
  presentation hints; the catch/squirm quality is a HARD GATE (D-090).
- **Authority:** D-070; AW-285 (rendering); D-090; `nightcap-art-direction.md`.
- **State:** rendering planned (AW-285) with D-090/G3/G5 criteria.

### 13. Pacing
- **What:** stall thresholds, tension-driven nudges, evidence-release
  timing; distinct from *designed* rhythm (session-experience doc).
- **Authority:** `engine/telemetry/pacing.py`; arc `pacing_config`.
- **State:** shipped.

## Cross-Cutting Design Authorities

- **Whole-session integration & rhythm:** `couch-race-session-experience.md` (D-092)
- **Competition model:** `couch-race-competition-model.md` (co-opetition + Leverage)
- **Product North Star:** D-093 (story spine + swappable minigames + Jackbox-but-deeper)
- **Rehearsal 1 = whole-session test:** D-092; `rehearsal-1-observation-guide.md`
- **The de-risk:** `interrogation-paper-test.md`

## How To Use This Map

1. Before proposing any gameplay change, find the affected system above
   and read its authority.
2. If your idea already exists as a system, extend it — do not invent a
   parallel one (the error that created this map: designing "scoring
   integration" while Leverage already answered it).
3. If your idea is genuinely new, it needs its own decision/ADR and a
   new row here.
