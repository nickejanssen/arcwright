---
name: kb-answer
tier: small
---

# kb-answer

Answer a question from the knowledge base, with citations, or refuse.

## Fixed sequence

1. `kb_search` the question.
2. Answer strictly from the returned hits. Every sentence of fact must trace to
   a hit.
3. Cite every claim with its document id.
4. If no hit scores above threshold: say you do not know, then call
   `kb_coverage_gap` to log the gap. Do not answer from general knowledge.
