# Independent retrieval evaluation draft — revised

Source snapshot: `origin/main` at `dff9f0fd938a85de0551bcd80670c305233179fd`; initial draft prepared 2026-11-18 without reading golden cases or retrieval implementation. Revision 2026-11-18 was made after reviewing both, so the revised set is **not blind to existing evaluations**. Independently adjudicate before use; do not treat this document as a frozen secret, a fixture, a run, or evidence of a retrieval rate. The exact questions and keys must remain isolated from tuning and training.

Paths below are KB-relative: the lexical index root is `docs/`. They are relevance judgments, not necessarily the only correct sources. Primary paths identify source authority for static design claims; alternatives should be accepted when independently verified. Source citations are design intent, not evidence of implementation. Score retrieval separately from answer correctness. No question asks for live issue status; any later status evaluation must use a fresh external verification and an independently specified rubric.

1. **Question:** A guest passes along a questionable account through several other characters. What data lets the engine represent the account's reliability and reconstruct who passed it along?
   - Primary: `architecture/04-knowledge-graph.md` §4.2. Confidence and an ordered provenance chain; a direct observation has a one-member chain.
2. **Question:** When the configured primary model times out, what does the architecture say about fallback selection and recording the event?
   - Primary: `architecture/06-model-routing.md` §6.5. Per-task/tier fallback and a logged fallback event; design intent does not prove operational behavior.
3. **Question:** Which portions of a character prompt are expected to be reusable, and which portions change between calls?
   - Primary: `architecture/06-model-routing.md` §6.7. Stable arc/profile material precedes changing knowledge and social pressure.
4. **Question:** In Nightcap's final case resolution, can a persuasive argument allow a model to decide the winner when no player has solved the murder?
   - Primary: `gdd/nightcap/00-governance/00-decision-ledger.md`, Winning / Last Call / Case File. The authored graph determines the outcome, with no player murder winner if no one solves.
5. **Question:** Was cross-session group memory approved as a dependency for the initial Nightcap release?
   - Primary: `decisions/0006-nightcap-continuity-v11.md`, Context and Decision. It is a v1.1 fast-follow, not a v1 prerequisite; approval does not prove implementation.
6. **Question:** What does a character's concealment threshold measure and what happens to behavior once accumulated social pressure exceeds it?
   - Primary: `architecture/07-character-behavior.md` §§7.2 and 7.4. It measures pressure before concealment starts to crack; behavior shifts in ways consistent with pressure style.
7. **Question:** In the API design, which credential is specified for creating a session, and what credentials are specified for starting one?
   - Primary: `architecture/09-developer-api.md` §9.2, Session Management. Use the endpoint catalog, not an assumption about the deployed API.
8. **Question:** What does the telemetry design say should happen to the content and structural portions of a session event when handling a deletion request?
   - Primary: `architecture/11-telemetry.md` §11.2. The stated design removes personal content while retaining the structural record; this is not a legal compliance determination or proof of runtime behavior.
9. **Question:** In Daily Case, who determines whether a contradiction is real, and what role does the AI play?
   - Primary: `story-bibles/daily-case.md`, Arc Design Principles, Human-authored spine. Human-authored structure resolves truth and contradictions; AI expresses the suspect within constraints. Treat this title material as provisional under the manifest.
10. **Question:** For Monster RPG, what term should appear in player-facing text for a load-and-play period, and what term is used technically?
    - Primary: `story-bibles/monster-rpg.md`, Terminology note. Treat this title material as provisional under the manifest.
11. **Question:** How are authored conditions on a transition checked by the engine, and does the engine interpret the meaning of their names?
    - Primary: `architecture/03-arc-execution.md` §3.2. Conditions are keys checked for boolean truth in session context, not semantically interpreted. This describes the architecture rather than asserting deployed behavior.
12. **Question:** How does the session design reconstruct state if its derived state is uncertain?
    - Primary: `architecture/05-session-persistence.md` §5.2. The append-only event log is the authoritative history for reconstruction. Judge other verified sources as alternatives.
13. **Out-of-domain refusal:** How do I renew a driver's licence in an unrelated country?
    - Expected: refuse or explicitly route outside the Arcwright knowledge base; no invented KB citation. Evaluate routing/abstention, not an empty ranking alone.
14. **Negative-corpus / unknown:** What is Arcwright's approved “quantum turnip protocol” retention interval?
    - Expected: report that this named protocol was not found in the searched snapshot and avoid inventing an interval; do not claim no conceivable policy exists. Search validation: exact phrase case-insensitively in all Markdown under `docs/` yielded no matches on the source snapshot. A lexical retriever may still return unrelated hits; score whether the answer recognizes the evidence gap, not whether it returns zero hits.

## Eligibility and limitations

The lexical loader recursively includes Markdown under `docs/`, subject to `team-ai/index.lock` exclusions and valid front matter. The 12 primary paths above exist, have front matter and do not match those exclusions at the snapshot. This establishes source eligibility, not that a particular built index is current or returns any source at a given rank; verify against the actual deployed index before use. Roadmap JSON is not Markdown and is not a lexical document; repository paths or live GitHub issues should not be treated as indexed KB keys.

The set has 12 source-backed cases across 11 primary namespaces and two abstention cases. It is a convenience sample, not representative of production query traffic. The two routing cases share an owner, as do other related concepts; neither independence nor adversarial coverage is established. The title cases are provisional; the negative-corpus check covers an exact phrase, not semantic absence. No live status, deployed behavior, exhaustive alternate sources, inter-rater adjudication, rank threshold, access controls, or deployed-index freshness was verified. Both author and reviewer exposure to the draft and existing evaluations make this unsuitable as a pristine blind holdout without replacement and independent custody. Revalidate the snapshot and adjudicate before scoring; report per-case results and uncertainty, never extrapolate a percentage from this small sample.
