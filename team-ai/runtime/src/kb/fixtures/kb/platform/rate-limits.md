---
id: kb.platform.rate-limits
namespace: platform
title: Rate Limits
owner: solutions-architect
status: active
review_by: "2027-06-30"
sensitivity: internal
source: authored
tags:
  - "429"
  - throttling
supersedes: []
---

## Defaults

Every API key starts at 60 requests per minute before the rate limit trips.

## Handling 429s

A 429 response means the request exceeded the rate limit. Callers that ignore
429 rate limit errors keep getting 429 errors until they slow down.

### Backoff

Retry with exponential backoff and jitter after a 429.

### Escalation

Contact the platform team for a rate limit increase.
