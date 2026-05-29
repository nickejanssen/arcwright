# M1-D: Model Routing Abstraction

**Milestone:** M1  
**Status:** Planned

## What This Epic Covers

Implement the provider-agnostic model-routing layer, routing-table behavior, prompt caching, and generation logging so later milestones can spend tokens safely and traceably.

## Tasks

- [AW-107: LiteLLM routing layer](../tasks/AW-107-litellm-routing-layer.md)
- [AW-108: Prompt caching and generation logging](../tasks/AW-108-prompt-caching-and-generation-logging.md)

## Epic Exit Criteria

- Model calls route through the router abstraction only
- Routing swaps require zero code changes
- Generation logging and cache strategy are wired
