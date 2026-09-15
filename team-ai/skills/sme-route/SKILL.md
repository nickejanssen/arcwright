---
name: sme-route
tier: none
---

# sme-route

Route a question to the domain subagent that owns it. No model call.

## Fixed sequence

1. `kb_manifest` to load the domain table.
2. Match the question against each domain's `keywords` and `description`.
3. One clear match: return that domain's `subagent`. Several: return the best
   and name the rest.
4. No match: return no route and name the likely owner, so the caller can log a
   coverage gap.
