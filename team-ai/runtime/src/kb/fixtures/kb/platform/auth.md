---
id: kb.platform.auth
namespace: platform
title: Authentication
owner: solutions-architect
status: active
review_by: 2027-03-15
sensitivity: internal
source: "synced:platform-docs"
source_url: https://example.com/docs/auth
tags:
  - auth
  - tokens
supersedes: []
---

## Token Types

The API accepts bearer tokens and signed service keys.

```sh
# This is a shell comment, not a heading
curl -H "Authorization: Bearer $TOKEN" https://example.com/v1/whoami
```

## Rotation

### Schedule

Rotate service keys every 90 days.

### Revocation

Revoked tokens stop working within one minute.
