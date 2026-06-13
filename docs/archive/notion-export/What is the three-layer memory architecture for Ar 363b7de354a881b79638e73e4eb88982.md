# What is the three-layer memory architecture for Arcwright NPCs?

Category: Product
Date Opened: May 17, 2026
Priority: High
Status: Open

Emergence World separates agent memory into three layers: soul entries (identity, never overwritten), episodic memory (what happened, progressively summarized), and world state (established facts). Arcwright needs an analogous design to prevent NPC character drift across long sessions as the context window fills. Without a stable identity anchor layer, NPCs will gradually lose character consistency. This must be decided and designed before engine coding begins. Key questions: what lives in each layer, what gets summarized vs. kept verbatim, and how is the soul layer protected from overwrite.