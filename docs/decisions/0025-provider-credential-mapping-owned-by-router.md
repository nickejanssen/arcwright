---
id: productroadmap.decisions.0025-provider-credential-mapping-owned-by-router
namespace: product-roadmap
title: "ADR-0025: Provider Credential Mapping Is Owned by the Router"
owner: Nico Janssen
status: active
review_by: "2027-03-21"
sensitivity: internal
source: authored
tags: []
supersedes: []
---

# ADR 0025: Provider credential mapping is owned by the router

- **Status:** Accepted
- **Date:** 2026-09-21
- **Deciders:** Founder (direction approved in session), Claude Code
- **Related:** AGENTS.md architecture principle 8 (provider-agnostic model routing), `docs/roadmap/operations/cloud-deploy-runbook.md`

## Context

Three places encoded how an LLM provider's credential reaches its SDK, and nothing tied them together:

1. `config/routing_table.json` names providers as `provider/model` prefixes.
2. `engine/routing/router.py` held `_PROVIDER_CREDENTIAL_ENV_MAP`, keyed by the
   provider-neutral deploy slot (`PRIMARY_LLM_API_KEY` → `ANTHROPIC_API_KEY`).
3. `scripts/rehearsal.py` independently *derived* provider env var names from
   the routing table by the convention `{PROVIDER}_API_KEY`.

The router's map was keyed by slot, not by provider, so nothing connected
`anthropic` in the routing table to `ANTHROPIC_API_KEY` in the router. The two
agreed only by coincidence.

The derivation in (3) was also wrong in two ways. It produced illegal
environment variable names for any provider id containing a separator
(`vendor-a` → `VENDOR-A_API_KEY`, which no shell can set). More fundamentally,
`{PROVIDER}_API_KEY` is not a rule LiteLLM actually follows: several providers
authenticate through project or cloud credentials rather than a single
`_API_KEY` variable, so the convention cannot be made correct by fixing its
string handling.

Separately, the two representations disagreed in practice. Cloud deploy binds
the neutral slots and the router hydrates provider variables from them at
startup, but the rehearsal preflight demanded the provider variables outright.
A `.env` written the way the cloud deploy runbook describes was rejected
locally even though the engine would have run.

## Decision

1. **`engine/routing/router.py` owns one provider-keyed credential mapping.**
   `_PROVIDER_CREDENTIALS` maps each routing-table provider id to a
   `ProviderCredential(env_var, deploy_slot)`. The slot-keyed hydration map is
   derived from it, so hydration and requirement checks cannot drift.

2. **The router exposes `required_credential_env_vars()`.** It returns, per
   provider the active routing table references, the env var names that satisfy
   that credential — the provider's own variable first, then its neutral deploy
   slot. Callers check an environment without naming a provider.

3. **No caller derives credential names by convention.** `scripts/rehearsal.py`
   holds no provider names and no derivation; it calls the router. The import is
   lazy and guarded, both because the router pulls in the LLM SDK (roughly ten
   seconds) and because `python scripts/rehearsal.py` does not put the repo root
   on `sys.path`. Cheap `.env` checks run first so the common failures still
   report immediately.

4. **An unmapped provider is an error, not a guess.** A routing-table provider
   with no entry raises `UnmappedProviderError` naming the file to edit. Adding
   a provider now requires two edits — the routing table and the router — which
   was already true for cloud deploy and is now stated rather than implied.

5. **The neutral deploy slot satisfies a provider credential everywhere.** The
   rehearsal preflight accepts either form, matching what the router does at
   runtime.

## Consequences

**Good**

- One mapping. Hydration, cloud deploy, and the local preflight read the same
  source, and a test asserts the first two agree.
- Rule 8 holds without amendment: provider names stay in
  `config/routing_table.json` and `engine/routing/router.py`, the two paths
  `scripts/checks/provider_leak_check.py` permits.
- A `.env` written from the cloud deploy runbook boots locally.
- A provider whose SDK does not read `{NAME}_API_KEY` can be added correctly,
  which the old convention made impossible.

**Costs**

- `scripts/` now depends on `engine/`. This is the first such dependency.
- `make rehearsal` pays the router import before it can check LLM credentials.
  Infrastructure key checks were ordered ahead of it so the common failure path
  is unaffected, but a complete `.env` is now slower to validate.
- Adding a provider requires editing the router, not the routing table alone.
  This is deliberate: the previous "table edit is enough" property was only ever
  true for local rehearsal, and only because it guessed.

**Rejected alternatives**

- *A litellm-free `engine/routing/provider_env.py` imported by both.* Cheapest
  at runtime, but it would hold provider names in a third path, requiring
  AGENTS.md rule 8, its Copilot mirror, and the leak checker's allowlist to be
  amended. Rejected as changing the architecture rule to suit the code.
- *Move the mapping into `config/routing_table.json`.* No engine import and no
  rule change, since the table already legitimately holds provider names.
  Rejected because credential resolution is behaviour, and the router is where
  behaviour that names providers belongs.

## References

- `engine/routing/router.py`
- `scripts/rehearsal.py`
- `engine/tests/test_routing.py`
- `scripts/tests/test_rehearsal.py`
- `scripts/checks/provider_leak_check.py`
