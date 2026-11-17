---
id: fixture.platform.authentication
namespace: platform
title: Authentication
owner: solutions-architect
status: active
review_by: "2027-03-15"
sensitivity: internal
source: authored
tags:
  - auth
  - tokens
supersedes: []
---

## Token Types

The API accepts bearer tokens and signed service keys for authentication.

## Rotation

### Schedule

Rotate service keys every 90 days.

### Revocation

Revoked tokens stop working within one minute.
