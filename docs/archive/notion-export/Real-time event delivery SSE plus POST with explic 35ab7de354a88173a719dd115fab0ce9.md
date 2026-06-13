# Real-time event delivery: SSE plus POST with explicit transport adapter pattern

Date: May 7, 2026
Rationale: Engine emits events to internal event bus (asyncio channels). Transport adapters subscribe and push to clients. MVP implements SSE adapter for Nightcap server push and POST endpoint for player input. WebSocket adapter added later when Couch online or Monster online require it. Adapter pattern means engine never changes when transports are added.
Section: Cross-cutting
Status: Committed