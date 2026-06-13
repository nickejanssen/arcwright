# generation_logs full content population gated behind CONTENT_LOGGING_ENABLED feature flag (default false); non-PII fields populated at MVP

Date: May 11, 2026
Rationale: Player-submitted content (names, character choices, dialogue) may appear in generation prompts. Storing prompt and output text before a GDPR consent architecture is in place creates compliance exposure. The table schema exists from day one with all columns including prompt_text TEXT NULL and output_text TEXT NULL. Non-PII fields (model, latency, tokens, cost, tension score) are populated at MVP. Full content population is deferred until GDPR consent architecture is in place and the flag is explicitly enabled.
Section: Cross-cutting
Status: Committed
Tags: roadmap