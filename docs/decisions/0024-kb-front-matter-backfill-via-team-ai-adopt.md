---
id: decisions.decisions.0024-kb-front-matter-backfill-via-team-ai-adopt
namespace: decisions
title: "ADR-0024: KB Front-Matter Backfill via team-ai adopt"
owner: Nico Janssen
status: draft
review_by: "2027-03-13"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# Status

**Proposed** -- awaiting founder review. This record documents a KB-metadata
backfill already applied in a pull request; it does not itself carry
implementation authority until the founder accepts it. See
[PR #308](https://github.com/nickejanssen/arcwright/pull/308).

---

# Context

`docs/` carried no machine-readable front matter (`id`, `namespace`, `owner`,
`status`, `review_by`, `source`, `tags`, `supersedes`) on any of its ~470
markdown files. `team-ai adopt` -- a deterministic, no-model tool external to
this repo -- was run to measure the repo against a front-matter standard and
produce a reviewable plan. The founder reviewed every item and namespace
decision through an interactive artifact (approve / draft / archive / skip
per document, per-folder namespace picks) before anything was applied.

This is a metadata-only change to `docs/`: it adds a retrieval/lifecycle
classification layer on top of existing canonical content. It does not
create, approve, or change any product, architecture, or roadmap decision
recorded in the files it annotates -- those decisions remain exactly as
authored. It was not preceded by a dedicated spec in `docs/specs/` before
work began, which this ADR exists to reconcile after the fact, per
`AGENTS.md`'s rule that a decision affecting schemas or implementation
behavior needs an ADR or approved spec as durable evidence.

---

# Decision

1. Backfill inferred front matter onto every `docs/` markdown file that had
   none, using `id`, `namespace`, `owner`, `status`, `review_by`, `source`,
   `tags`, `supersedes` per the field list above.
2. Map 12 previously-unmapped top-level `docs/` folders to namespaces
   (`operating`, `platform`, `patterns`, `playbooks`, `custom`), recorded in
   `.team-ai-namespaces.yaml`.
3. Classify lifecycle `status` per document based on its own stated
   authority: `docs/gdd/nightcap/` as `active` (current Nightcap design
   authority); other story bibles (`monster-rpg.md`, `daily-case.md`) as
   `draft` (placeholders ahead of their own GDDs); the two Nightcap
   story-bible redirect stubs as `deprecated` (superseded by the GDD);
   documents whose own body explicitly states a draft, proposed, or
   awaiting-approval status as `draft`; documents whose own body explicitly
   states they are superseded or closed as `deprecated`.
4. Leave `docs/design/line-libraries/` untouched -- a pre-existing repo
   guardrail (`engine/tests/test_line_libraries_untouched.py`, AW-290)
   forbids any diff there against `main`, including front matter.
5. Leave `docs/decisions/0000-template.md` untouched (blank template, not a
   decision) and 10 files where `team-ai`'s backfill guard failed to detect
   pre-existing front matter written with CRLF line endings, rather than
   risk corrupting content the guard should have protected.

---

# Consequences

## Positive consequences

- Every canonical doc now carries a machine-readable `status`, so an agent
  or the planned Arcwright SME tooling can filter `draft`/`deprecated`
  content out of retrieval instead of treating everything as equally
  current.
- The Nightcap GDD's authority over prior story bibles, and several
  explicitly-superseded ADRs and specs, is now encoded in structured data
  instead of only in prose cross-references.

## Negative consequences

- 470 files changed in one PR is a large, mechanically-generated diff that
  is harder to review line-by-line than a hand-authored change; review
  relied on sampling and automated review (Codex), not per-file human
  read-through.
- Front matter can drift from body content over time (a doc's stated status
  changes in prose without its `status:` field being updated to match) --
  no automation currently re-checks this after the fact.

## Trade-offs

- Chose a one-time bulk backfill over hand-authoring front matter per file
  over time, trading per-file review depth for getting the whole KB into a
  queryable state immediately.

---

# References

- [PR #308](https://github.com/nickejanssen/arcwright/pull/308) -- the applied change
- [docs/adoption-plan.md](../adoption-plan.md) -- the pre-approval plan snapshot
- [.team-ai-namespaces.yaml](../../.team-ai-namespaces.yaml) -- namespace decisions
- `AGENTS.md` Product Scope Approval Rules -- the rule this ADR satisfies after the fact
