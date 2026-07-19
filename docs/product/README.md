# Product Records

This directory holds product-level records that do not belong to architecture ADRs or implementation specs.

## Files

- Decisions log exports from the product workspace
- Open-questions log exports from the product workspace
- Product-log additions that are not architecture ADRs
- [Nightcap Leverage advantages and sabotages design](nightcap-leverage-advantages-sabotages.md): proposed design-only catalog and playtest recommendation

## Rules

- Treat CSV logs as append-only unless correcting a formatting error.
- Treat `decisions-log.csv` and `open-questions-log.csv` as canonical.
- Treat `_all.csv` files as raw/import mirrors stored under [../archive/notion-export/](../archive/notion-export/). Do not manually update them unless the task is explicitly about import reconciliation.
- Architecture decisions that affect implementation should also become ADRs in [../decisions/](../decisions/) when they create a lasting technical constraint.
- Product-scope commitments that affect roadmap, architecture, privacy, APIs, or implementation sequencing must have durable decision evidence: a product log row plus either an ADR or an approved spec.
- Product-content edits should reference the relevant PRD, story bible, roadmap, or architecture section.
- For AI cost control, read only the canonical log and targeted rows unless comparing an import mirror is required.
