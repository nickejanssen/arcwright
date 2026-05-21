Arcwright Repository Rules

All work in this repository must comply with the Arcwright PRD and technical architecture. If a proposed implementation conflicts with one of the platform architecture principles, the principle wins unless the founder explicitly overrides it with documented rationale.

1. Surface agnosticism
- The engine has no opinion about what displays its output.
- Never write rendering logic, UI assumptions, or surface-specific presentation code in `engine/`.
- The platform emits structured content events with context; surfaces decide whether to render them on phones, shared displays, browsers, voice, or future interfaces.

2. Human arc primacy
- AI is the runtime personalization layer, not the creative author.
- Every experience must have a human-designed arc that defines the structure, constraints, required moments, and allowed variation.
- AI generation is called only after the arc execution layer has resolved the current session state deterministically.
- LLMs compose narrative from resolved, structured state data; they do not manage, infer, or update canonical session state.
- State transitions must always be deterministic. Any feature that asks the AI to decide what happened in the session is an architecture violation and must be redesigned.

3. Configurable composition
- Arc elements may be either authored or generative, per element.
- Preserve the authored-versus-generative dial in schemas and implementation choices.
- Do not collapse an arc into all-authored or all-generative assumptions unless the spec for that arc explicitly says so.

4. Unified character model
- Human-controlled and AI-driven characters are the same platform object type.
- Character identity, personality profile, goals, knowledge state, and relationship graph belong in one shared model.
- Behavior source may differ, but the data model must stay unified.

5. Knowledge graph as first-class infrastructure
- Every session maintains a structured knowledge graph recording who knows what, when they learned it, and from whom.
- AI character responses must be constrained by character knowledge state.
- Knowledge state is mandatory platform infrastructure, not an optional add-on.

6. Cost-aware architecture from day one
- Model routing is task-type plus quality-tier based.
- Classification and safety tasks route to small, fast, low-cost models; generation tasks route to models appropriate for the required quality tier.
- Routing is budget-first by default. Do not default to the best available frontier model when a cheaper model meets the quality bar.
- Prompt caching is a named architectural requirement. Reused session context layers must be cached wherever the provider supports it.

7. Progressive proprietary infrastructure
- Launch on managed third-party AI services first.
- Replace components with proprietary or self-hosted infrastructure only when session volume, data quality, and economics justify the transition.
- Do not introduce foundation-model training or owned compute infrastructure into MVP scope.

8. Provider-agnostic model routing
- No platform operation may hardcode a dependency on any specific AI provider, model name, or model version.
- Every model call must route through the internal abstraction layer that maps task type and quality tier to the active model.
- No provider name or model string may appear anywhere outside `config/routing_table.json` and `engine/routing/router.py`. Treat any violation as a bug.

Implementation guardrails
- Python owns arc execution, knowledge graph, character behavior, model routing, content safety, session state, migrations, and API logic.
- TypeScript owns the web SDK, dashboard rendering, event subscription, and player input submission logic.
- No arc execution logic crosses into TypeScript.
- FastAPI route handlers must stay thin: validate input, call engine functions, return responses. No arc logic in route handlers.
- Prefer scaffolding, interfaces, and configuration over speculative business logic unless the current task explicitly requires implementation.
