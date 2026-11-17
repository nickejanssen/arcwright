---
id: fixture.platform.rate-limits
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

A 429 response means the request exceeded the rate limit. A caller that keeps
retrying immediately after a 429 rate limit error will keep getting 429 errors.
Slow down, then retry.

### Backoff

Retry with exponential backoff and jitter after a 429 rate limit response.

### Escalation

Contact the platform team to request a rate limit increase for a key.
