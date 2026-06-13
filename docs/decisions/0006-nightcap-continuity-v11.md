# Status

**Accepted**

---

# Context

Nightcap v1 is scoped to prove the complete single-session party game. During the documentation organization and product review work on 2026-06-13, the founder approved Nightcap Continuity as a v1.1 fast-follow so the repo has a durable record of the next product step without expanding the v1 MVP.

Nightcap Continuity means:

- A post-session recap artifact generated after The Truth.
- Cross-session group memory that can be reused by a host or group in later sessions.
- Host controls for reuse, exclusion, and deletion.
- Privacy-aware retention and redaction rules.

This decision is tied to D-034 because continuity makes Arcwright's wedge visible: cross-session narrative state management, with the knowledge graph as a headline primitive. It is also recorded as D-051 in `docs/product/decisions-log.csv`.

Alternatives considered:

- Keep continuity only as an open question. Rejected because the founder committed it to v1.1 and the roadmap needs a retrievable fast-follow target.
- Move continuity into v1. Rejected because v1 must stay focused on the complete single-session party game and should not absorb consent, retention, deletion, and recap-product complexity.
- Leave continuity only in the story bible. Rejected because product-scope commitments need durable decision evidence outside a narrative design document.

---

# Decision

We commit Nightcap Continuity to v1.1 as an approved fast-follow, not to v1 MVP.

v1 must not require cross-session memory, recap retrieval, continuity selection, or continuity consent flows to ship. v1.1 planning may use the Nightcap story bible continuity section as a roadmap bookmark, but implementation still requires normal spec work before code changes.

Continuity may personalize future generated content, but it may not manage canonical session state, bypass deterministic arc execution, or weaken the human arc primacy principle.

---

# Consequences

## Positive consequences

- The Nightcap roadmap has a clear v1.1 product target after v1 proves the single-session experience.
- Future agents can retrieve the continuity decision from `docs/decisions/0006-nightcap-continuity-v11.md`, D-051, and the Nightcap story bible without scanning archived exports.
- Reviewers can distinguish approved v1.1 scope from accidental v1 MVP expansion.
- The D-034 wedge is connected to an actionable Nightcap fast-follow.

## Negative consequences

- v1.1 now carries privacy, consent, retention, deletion, API, SDK, telemetry, and recap artifact design work.
- Continuity introduces new product and architecture surface area that must not be implemented casually inside unrelated v1 work.

## Trade-offs

- We gain a stronger post-v1 roadmap and a clearer cross-session memory proof point.
- We defer that proof point until after v1 so the MVP remains smaller and easier to validate.

---

# References

- `docs/product/decisions-log.csv` D-051
- `docs/story-bibles/nightcap-murder-mystery.md` approved v1.1 Nightcap Continuity section
- `docs/product/open-questions-log.csv` Nightcap Continuity recap schema question
- `docs/product/open-questions-log.csv` Nightcap Continuity consent and retention question
- `docs/architecture/04-knowledge-graph.md`
- `docs/architecture/05-session-persistence.md`
- `docs/architecture/11-telemetry.md`
- `docs/specs/0029-docs-organization.md`
