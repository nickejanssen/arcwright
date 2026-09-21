---
description: Review which knowledge-base documents have gone stale and fix the ones approved
---

# Document currency review

## 1. Gather

Run the freshness audit and read the JSON:

```bash
python scripts/team_ai_cli.py freshness-audit --instance team-ai
```

Its three categories mean:
- **stale** — past its `review_by` date
- **orphaned** — no `relations` entries connecting it to other documents
- **unowned** — no `owner` in its front matter

Compare against `team-ai/graph/freshness-baseline.json` and report the change,
not the absolute count. 438 of 449 documents are orphaned at baseline; that
number on its own is noise.

## 2. Report

For each stale document tell the founder, in plain language and without jargon:
- what the document is for
- why its being out of date matters, concretely
- what you would change

Do not use the words stale, orphaned or unowned without explaining them.

## 3. Stop

Present the list and ask which to act on. **Wait for an answer.** Never infer
approval from silence, and never act on an item that was not named.
`docs/conventions/human-collaboration.md` governs this gate.

## 4. Act

Update only the approved documents. For each, set a new `review_by` date and
make the content change actually needed — never only the date, which would
hide the staleness rather than resolve it.

## 5. Confirm

List what changed and what was deliberately left, and run:

```bash
python scripts/team_ai_cli.py validate-kb --instance team-ai
```
