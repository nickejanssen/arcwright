# AW-261: ADR-0003 Cloudflare vs GCP Validation Decision

**Milestone / Epic:** M4 / M4-A (closes AW-225 validation gate)
**Size:** S
**Status:** Complete

## Plain-English Summary

Record the Cloudflare vs GCP comparison the AW-225 acceptance criteria
require, close the ADR-0003 validation gate, and file a follow-on M5 task
for the actual cloud deployment.

## Why This Matters

AW-225 closed without recording the comparison ADR-0003 requires before
adding Cloudflare-specific dependencies. This validation gate has been
hanging since 2026-06-22. AW-254 needs the path resolved (or formally
deferred) before Rehearsal 2 picks a cloud target.

## Player Impact

None directly. Indirectly: production deploy quality and cost depend on
choosing the right cloud surface.

## Business Value

Closes a long-standing decision debt. Sets the cloud path criteria so a
future deploy task is unambiguous.

## Technical Scope

- Update `docs/decisions/0003-nightcap-web-experience-runtime.md` with:
  - what Cloudflare gives that Cloud Run plus Firebase plus Cloud CDN does
    not,
  - what Cloud Run plus Firebase plus Cloud CDN gives that Cloudflare does
    not,
  - what Rehearsal 1 (running on neither) does not tell us,
  - decision criteria for the actual cloud deploy,
  - which decision wins.
- Append D-067 to `docs/product/decisions-log.csv` recording the outcome.
- File a new GitHub issue (AW-269 candidate; manifest entry added during
  this task) for the actual cloud deploy implementation in M5.

## Acceptance Criteria

- [ ] ADR-0003 status moves from "Accepted with validation gate" to
  "Accepted, validation complete".
- [ ] D-067 records the comparison outcome with rationale.
- [ ] A new M5 task entry is added to `docs/roadmap/index.json` and a
  corresponding GitHub issue exists for the cloud deploy implementation.

## Tests/Verification

- ADR-0003 status line confirmed.
- Decision log row D-067 exists with non-placeholder rationale.
- New cloud-deploy issue exists in GitHub and in the manifest.

## Dependencies

- ADR-0003 already exists
- AW-225 closed (the validation gate it left open)

## Must Not Do

- Do not provision either provider in this task.
- Do not deploy anything in this task.
- Do not spend money in this task.

## Architecture References

- `docs/decisions/0003-nightcap-web-experience-runtime.md`
- `docs/architecture/02-technology-stack.md`
- `docs/roadmap/epics/M4-A-nightcap-external-platform-integration.md`

## Playtest Relevance

Unblocks AW-254 (verification can start without ambiguity about the future
cloud path) and seeds the M5 cloud deploy work that hosts Rehearsal 2.
