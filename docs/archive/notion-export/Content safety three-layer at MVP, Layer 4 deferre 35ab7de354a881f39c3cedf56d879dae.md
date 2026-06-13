# Content safety: three-layer at MVP, Layer 4 deferred with watchpoint

Date: May 7, 2026
Rationale: Layer 1: deterministic hard stops (regex blocklists for absolute prohibited content). Layer 2: GPT-OSS-Safeguard 20B on Groq for pre-generation classification, with arc-defined policy (bring-your-own-policy). Layer 3: main LLM with policy in system prompt. Layer 4 (post-generation safety) deferred with watchpoint to add if real sessions surface output problems. Saves one safety call per turn at MVP. Murder mystery genre adjacent to dark content makes Layer 2 essential. GPT-OSS-Safeguard replaces deprecated Llama Guard 4 (Feb 2026 on Groq).
Section: Cross-cutting
Status: Committed