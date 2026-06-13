# Six behavior commitments for AI characters (stochastic generation, initiative, NPC-NPC, goal pursuit, per-character profile, arc-level variability)

Date: May 7, 2026
Rationale: (1) Behavior is generated not scripted (non-zero temperature, character voice). (2) Initiative scheduler: AI characters act unprompted based on goals and state. (3) NPC-to-NPC interactions are first-class. (4) Goal pursuit drives behavior, not just colors it. (5) Per-character behavior_profile JSONB column captures initiative threshold, goal pursuit weight, interaction style, variability. (6) Arc-level variability through non-deterministic decision points. These prevent over-predictability and support 'you had to be there' north star.
Section: Cross-cutting
Status: Committed