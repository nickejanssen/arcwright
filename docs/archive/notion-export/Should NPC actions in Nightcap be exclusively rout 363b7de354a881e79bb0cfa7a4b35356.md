# Should NPC actions in Nightcap be exclusively routed through a finite, defined tool call vocabulary?

Category: Product
Date Opened: May 17, 2026
Priority: High
Status: Open

Emergence World's tool-as-interface pattern routes every agent action through explicit tool calls, making behavior observable, auditable, and replayable. Constraining NPC actions to a defined vocabulary (e.g., accuse, alibi, reveal, deflect, move) would also enable narrative-state-gating and clean separation between AI reasoning and game state. The alternative is free-form LLM output with post-processing, which is harder to audit and constrain. This needs an answer before engine architecture is finalized. Recommendation: adopt tool-as-interface; define an MVP action vocabulary of 8-15 tools for Nightcap before writing engine code.