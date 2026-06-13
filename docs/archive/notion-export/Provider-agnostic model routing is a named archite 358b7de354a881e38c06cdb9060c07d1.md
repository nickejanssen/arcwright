# Provider-agnostic model routing is a named architectural requirement, not an implication

Date: May 5, 2026
Rationale: No platform operation may hard-code a dependency on any specific AI provider or model. All model calls route through an internal abstraction layer. Enables cost optimization through provider switching, compliance flexibility for enterprise customers, and Tier 2 migration from managed APIs to fine-tuned open source models without changing arc execution logic.
Section: Section 2: Strategic Pillars
Status: Committed
Tags: pillars