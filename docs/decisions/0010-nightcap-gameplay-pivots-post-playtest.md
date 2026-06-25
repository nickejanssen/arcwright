# Status

**Proposed**

---

# Context

As we approach the first formal playtest for Nightcap, we are capturing two significant potential gameplay pivots to be evaluated based on player feedback and experience. These ideas diverge from the current single-killer, linear-progression model and represent possible future directions for the Nightcap product to enhance player engagement, replayability, and session pacing.

The current model is a multi-hour, turn-based experience where one player is secretly the killer. These proposals challenge that core assumption based on two hypotheses:
1. A faster, more concentrated "couch game" experience might be more appealing to a broader audience than an extended role-playing session.
2. A competitive deduction framework might generate more consistent moment-to-moment engagement than a cooperative (or deceptive) narrative one.

### Alternatives Considered
- **Do nothing:** We could proceed with the current gameplay model without formally documenting these pivots. This was rejected because it risks losing valuable strategic insights and not having a framework to evaluate playtest feedback against potential product futures.

### Constraints
- These ideas are explicitly scoped out of the v1 MVP. They are to be considered *after* the initial playtests and are not approved for implementation.

---

# Decision

We have decided to formally document two potential gameplay pivots for post-playtest consideration:

1.  **Pivot 1: The "Couch Game" Pacing Model.**
    - **Concept:** Shift Nightcap from a long-form, multi-hour experience to a dense, 60-90 minute single-session game. All players would be actively engaged simultaneously, likely in a single physical or virtual space, much like a modern board game.
    - **Rationale:** This could increase accessibility and appeal to groups looking for a "game night" activity rather than a longer role-playing commitment. It prioritizes session density over duration.

2.  **Pivot 2: The "Competitive Investigator" Model.**
    - **Concept:** Remove the secret killer and victim roles among players. Instead, all players are competing investigators trying to be the first to solve a murder that has already occurred. The game becomes a race to accumulate clues, connect evidence, and correctly identify the (NPC) killer.
    - **Rationale:** This model replaces player deception with direct competition, which can be a more straightforward and consistently engaging mechanic for some player groups. It avoids player elimination and the potential for a player to have a "bad" experience by being a victim or an unsuccessful killer.

These decisions will be logged and linked in relevant product and roadmap documentation to ensure they are revisited at the appropriate time.

---

# Consequences

## Positive consequences
- Provides a clear framework for evaluating playtest feedback against concrete alternative models.
- Encourages strategic thinking about the product's future beyond the initial MVP.
- Aligns the team on potential future directions, allowing for more focused architectural and design choices that don't preclude these pivots.

## Negative consequences
- None at this time, as this is a documentation and planning action only. If these pivots were adopted, they would require significant rework of the current arc, character models, and game progression systems.

## Trade-offs
- **Gained:** Formalized strategic options for the product's evolution.
- **Lost:** Time spent documenting ideas that may not be pursued. (This is considered a negligible cost).

---

# References

- **Related PRD:** `docs/prd/03-scope.md` (a note will be added to reference this ADR)
- **Related Log:** `docs/product/decisions-log.csv`
- **Future Work:** A post-playtest roadmap item will be created to review these pivots.
