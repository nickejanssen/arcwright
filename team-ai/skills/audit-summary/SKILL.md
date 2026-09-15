---
name: audit-summary
tier: small
---

# audit-summary

Summarize a freshness or coverage audit into a short, actionable list.

## Fixed sequence

1. Read the audit JSON (`freshness-audit` output or a coverage-gap export).
2. Group entries: stale, orphaned, unowned, missing coverage.
3. For each group, list the affected document ids and the named owner.
4. Output the three or four highest-priority items only. No prose beyond one
   line per item.
