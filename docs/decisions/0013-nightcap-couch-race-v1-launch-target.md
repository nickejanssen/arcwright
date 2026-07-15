# Status

**Accepted** (founder direction, July 15, 2026)

Related: accepts and executes the pivots proposed in ADR-0010. Product log record: D-071 in `docs/product/decisions-log.csv`.

---

# Context

ADR-0010 (June 24, 2026) documented two proposed Nightcap gameplay pivots for post-playtest evaluation: a "Couch Game" pacing model and a "Competitive Investigator" model. On July 15, 2026 — before Rehearsal 1 ran — the founder directed that these pivots be combined and pulled forward as the Nightcap v1 launch target, on the rationale that the couch-race model is dramatically cheaper to playtest, has far lower onboarding friction, and showcases the platform's knowledge-graph primitive as visible gameplay.

Timing matters: the platform layers built to date (arc engine, knowledge graph, routing, safety, shared display, phone privacy, mini-games, Cloudflare runtime) are model-agnostic, and the narrative content pipeline (D-069, AW-276–AW-280) is in flight but not yet committed against the old model's beat structure. This is the cheapest moment the pivot will ever be.

Market context: Netflix launched TV party games with phones-as-controllers including a Knives Out killer-among-players title, validating the living-room format while crowding that specific lane with major IP. Death by AI reached ~20M players and profitability, proving AI-native party games scale. No competitor ships coherent, fair, infinitely generated mysteries with knowledge-state-constrained suspects.

### Alternatives considered

- **Run Rehearsal 1 on the current model first, decide after.** Rejected by founder: the current model's test cost (4-player floor, long sessions, role burden) slows the validation loop the rehearsal exists to serve.
- **Reskin only (NPC killer on the existing 8-beat arc, no interrogation).** Rejected: undifferentiated; hides the platform's strengths.
- **Full replacement (archive the old model).** Rejected: the Imposter Variant is commercially validated by Netflix's entry and shares most infrastructure; it stays approved future scope.

---

# Decision

1. **Nightcap Couch Race is the Nightcap v1 launch target.** Canonical experience definition: `docs/story-bibles/nightcap-couch-race.md`. Core shape: 2–8 players, 20–40 minutes, TV shared display plus phones as private surfaces, all players are investigators racing to solve a murder committed by an AI suspect.
2. **The killer is never a player in v1.** Killer, victim, method, motive, clue web, and authorized suspect lies are resolved deterministically at session start from the authored arc. AI composes suspect dialogue from resolved knowledge state; it never decides or mutates case truth.
3. **Interrogation becomes shared platform capability.** Structured player questioning of AI characters with knowledge-gated answers, claim/provenance ledger, and deterministic contradiction detection serves both Couch Race and Daily Case. Question intents are menu-driven in v1; free-text is deferred.
4. **Competition structure is arc configuration** (solo race / teams / co-op dial). v1 ships the solo race.
5. **The prior killer-among-players design is renamed the Imposter Variant** and remains approved future scope in `docs/story-bibles/nightcap-murder-mystery.md`. ADR-0010's status moves to Accepted (executed via this ADR).
6. **Rehearsal 1 retargets to a Couch Race thin slice** (AW-286). D-065 (local tunnel) and D-066 (Tier 1 polish bar) apply unchanged. D-069 narrative tasks (AW-276–AW-280) carry over with beat-structure alignment to the six-beat arc. D-070 (animation + audio staging) applies with the cold open and suspect stage as its showcase moments.

---

# Consequences

## Positive consequences

- Founder test loop shrinks from one long session per evening to several complete cases per evening.
- Player floor drops from 4 to 2, widening the addressable audience to couples and small households.
- Eliminates the old model's worst failure modes: bad role draws, acting burden, player elimination, killer-role privacy leaks between players.
- One interrogation build feeds two products (Couch Race, Daily Case), strengthening the D-034 wedge.
- Mini-games already promoted for Rehearsal 1 (D-062/D-064) slot into the new arc unchanged.

## Negative consequences

- The M4 rehearsal plan, D-069 narrative task framing, and several roadmap gates written against the eight-beat killer-among-players arc need realignment (tracked in epic M5-I).
- Killer-assignment and killer-revelation engine work (AW-206 lineage) is not exercised by v1; it remains valid for the Imposter Variant.
- Generated-case fairness becomes the central quality risk; the AW-272 continuity/coherence eval suite becomes a launch gate rather than a hardening nicety.

## Trade-offs

- **Gained:** faster proof loop, broader market, visible platform differentiation, lower per-session cost.
- **Lost:** the social-deception experience at launch (deferred to the Imposter Variant), and some sunk design/engine work idles until that variant ships.

---

# References

- ADR-0010: `docs/decisions/0010-nightcap-gameplay-pivots-post-playtest.md` (proposals this ADR accepts and executes)
- Story bibles: `docs/story-bibles/nightcap-couch-race.md`, `docs/story-bibles/nightcap-murder-mystery.md`, `docs/story-bibles/daily-case.md`
- Design session record: `docs/superpowers/specs/2026-07-15-nightcap-couch-race-design.md`
- Spec: `docs/specs/0072-nightcap-couch-race-v1.md`
- Epic: `docs/roadmap/epics/M5-I-nightcap-couch-race-arc-and-interrogation.md`
- Product log: D-071 in `docs/product/decisions-log.csv`
- Related decisions: D-034 (wedge), D-053 (beat count is arc-level), D-062/D-064 (mini-games), D-065/D-066 (rehearsal posture), D-069/D-070 (narrative pipeline and audiovisual staging)
