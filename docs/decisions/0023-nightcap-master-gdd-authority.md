# Status

**Accepted** — founder-directed source-of-truth migration, August 31, 2026.

This ADR supersedes ADR-0013 **as the current Nightcap product-design authority**. ADR-0013 remains historical evidence of the July 2026 Couch Race pivot and its implementation consequences.

---

# Context

Nightcap design evolved materially through subsequent GDD checkpoints and playtest-driven review. The repository still treated `docs/story-bibles/nightcap-couch-race.md` as the canonical V1 experience even though newer approved design decisions now require first-class two-player support, a different core-loop framing, Structured Reconstruction, deterministic solve resolution without numerical Case Strength, revised Leverage sourcing, a hidden authored case graph, and an OPEN V1 upper player-count bound.

Keeping both the Story Bible and the newer GDD as apparent sources of truth creates avoidable conflicts for humans and agents.

---

# Decision

1. `docs/gdd/nightcap/` becomes the canonical source of truth for current Nightcap game design.
2. The current decision ledger has highest Nightcap design authority, followed by current authoritative GDD system pages.
3. The former Couch Race and Imposter Story Bibles are archived under `docs/archive/nightcap-story-bibles/`.
4. Their former paths remain compatibility redirect stubs so historical references do not break.
5. Historical ADRs and product-decision rows are preserved. Where an older Nightcap product-design decision conflicts with the current GDD, the GDD controls new design work; implementation consequences must be reconciled explicitly rather than history being rewritten.
6. `docs/design/the-host.md` remains the specialist authority for Vesper and `docs/design/nightcap-art-direction.md` remains the specialist visual authority, both subordinate to the GDD where gameplay/product structure conflicts.
7. Arcwright architecture remains governed by architecture docs and architecture ADRs; this migration does not silently change platform architecture or claim existing code already implements the new GDD.

---

# Consequences

## Positive consequences

- One unambiguous current Nightcap design authority.
- Older Story Bible links remain usable without becoming zombie canon.
- Historical decisions remain auditable.
- Future playtest evidence can reopen decisions through the GDD governance model rather than spawning another competing source of truth.

## Negative consequences

- Existing specs, roadmap items, tests, and code may still encode Couch Race-era assumptions and require explicit reconciliation work.
- Historical documents will continue to contain superseded statements by design; readers must follow the authority hierarchy.

## Trade-offs

The migration prioritizes provenance and reversible history over pretending that every historical artifact can be rewritten into the present. Current authority is explicit; old decisions remain inspectable.

---

# References

- Current GDD: `docs/gdd/nightcap/README.md`
- Decision ledger: `docs/gdd/nightcap/00-governance/00-decision-ledger.md`
- Migration policy: `docs/gdd/nightcap/00-governance/05-repository-migration-and-conflict-policy.md`
- Superseded current-design authority: ADR-0013
- Historical bibles: `docs/archive/nightcap-story-bibles/`
- Vesper: `docs/design/the-host.md`
- Visual direction: `docs/design/nightcap-art-direction.md`
