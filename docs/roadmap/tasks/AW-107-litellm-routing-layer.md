# AW-107: LiteLLM routing layer

**Milestone / Epic:** M1 / D  
**Size:** M  
**Implements:** Arch S2.7, S15.7, PRD Principles 6 and 8, S15.9 #3  
**Depends on:** AW-101

## Build

Implement `engine/routing/router.py` and `config/routing_table.json` exactly as specified in the architecture. All model calls go through the router keyed by `task_type` and `quality_tier`.

## Acceptance Criteria

- [ ] All generation calls route through `router.py`
- [ ] No model name or provider string appears anywhere outside `routing_table.json` and `router.py`
- [ ] Swapping a routing-table entry changes behavior with zero code changes
- [ ] `task_type` and `quality_tier` are the only model-selection inputs callers provide

## Do NOT

- Hardcode any provider name outside `routing_table.json`
- Expose model names to any caller

## Testing

Model routing fallback is a locked unit-test area. Test table-swap behavior and fallback.

## Agent Notes

Use one real smoke test per provider if needed, then keep the ongoing suite offline or mocked to avoid token spend.
