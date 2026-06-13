# Model routing: LiteLLM SDK in-process at MVP

Date: May 7, 2026
Rationale: LiteLLM is the dominant Python provider abstraction (40k stars, 140+ providers, Y Combinator backed, MIT licensed). SDK mode means no separate service to operate. Provider-agnostic routing through abstraction layer means switching Anthropic to Groq to anything else is a routing-table change. Migration to LiteLLM Proxy Server in H2 if external developers join. Custom abstraction rejected: distraction from core platform work.
Section: Cross-cutting
Status: Committed