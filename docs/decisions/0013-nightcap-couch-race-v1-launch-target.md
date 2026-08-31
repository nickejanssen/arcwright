# Status

**Superseded as current Nightcap product-design authority by ADR-0023 (August 31, 2026).**

**Historical status:** Accepted founder direction, July 15, 2026. Product log record: D-071 in `docs/product/decisions-log.csv`.

> This ADR remains intact as historical evidence of the Couch Race pivot and the implementation work it authorized. Do not use its Story Bible path, fixed 2–8 range, or Couch Race V1 definition to override the current Master GDD at `docs/gdd/nightcap/`.

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

# Historical Decision

1. **Nightcap Couch Race was selected as the Nightcap v1 launch target at that time.** Its former canonical experience definition was `docs/story-bibles/nightcap-couch-race.md`.
2. **The killer was never a player in that V1 model.** Killer, victim, method, motive, clue web, and authorized suspect lies were resolved deterministically at session start from the authored arc.
3. **Interrogation became shared platform capability.** Structured player questioning of AI characters with knowledge-gated answers, claim/provenance ledger, and deterministic contradiction detection served both Couch Race and Daily Case.
4. **Competition structure was treated as arc configuration.**
5. **The prior killer-among-players design was renamed the Imposter Variant** and retained as future scope.
6. **Rehearsal 1 was retargeted to a Couch Race thin slice.**

These points are preserved to explain subsequent implementation history. Current Nightcap design is defined by ADR-0023 and `docs/gdd/nightcap/`.

---

# Consequences

The original Couch Race pivot reduced the test floor, emphasized interrogation, and drove substantial implementation/spec work. Later design work changed the current Nightcap product definition. Existing code/specs produced under this ADR therefore require explicit comparison with the current GDD rather than being presumed current or deleted as mistakes.

---

# References

- Current authority migration: `docs/decisions/0023-nightcap-master-gdd-authority.md`
- Current GDD: `docs/gdd/nightcap/README.md`
- Archived former Couch Race Bible: `docs/archive/nightcap-story-bibles/nightcap-couch-race.md`
- Archived former Imposter Bible: `docs/archive/nightcap-story-bibles/nightcap-murder-mystery.md`
- Product log historical record: D-071 in `docs/product/decisions-log.csv`
