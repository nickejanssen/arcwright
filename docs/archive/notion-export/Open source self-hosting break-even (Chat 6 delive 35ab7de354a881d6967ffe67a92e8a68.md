# Open source self-hosting break-even (Chat 6 deliverable, RESOLVED)

Category: Product
Date Opened: May 7, 2026
Date Resolved: May 7, 2026
Priority: High
Resolution Notes: Calculated in Chat 6a (May 7, 2026). At managed API rates (Anthropic Sonnet 4.6 + Groq GPT-OSS-Safeguard) per-session cost is ~$0.20 with prompt caching. Self-hosting Llama 3.3 70B-class on a single A100 80GB at $2/hr does not break even with managed pricing until ~25,000-50,000 sessions/month, depending on utilization. Conclusion: stay on managed APIs through H2. Architecture supports switching via LiteLLM abstraction (routing-table change, not rewrite). Tier 2 fine-tuning trigger is ~25K sessions/month.
Status: Resolved
Where Resolved: Chat 6a, May 7, 2026.