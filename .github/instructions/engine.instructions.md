---
applyTo: "engine/**,api/**"
---
These paths are the Python engine and the thin FastAPI layer over it. Follow the always-on rules in `AGENTS.md`, especially the five non-negotiable engine constraints:

- Python 3.11+ only, no earlier.
- Arc execution logic stays in the Python engine; no arc logic in TypeScript.
- A knowledge-state query is mandatory before every AI character generation call.
- Provider and model names stay only in `config/routing_table.json` and `engine/routing/router.py`.
- Safety is enforced at the engine layer and cannot be bypassed by arc configuration.

FastAPI route handlers stay thin: validate input, call engine functions, return responses. No arc logic in route handlers. See `AGENTS.md` for the full rule set, the eight architecture principles, and the approval gates.
