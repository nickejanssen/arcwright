# aesthetic_mode replaced by aesthetic_config with per-element generation strategies. tone_config added to arc definition.

Date: May 15, 2026
Rationale: Aesthetic has four categories: host-selectable (era + occasion, with Pick for Me option), pre-produced per theme (backgrounds, music, animations, UI), generated at session start (character portraits), and generative runtime (all text/narrative). Pre-produced is the v1 implementation; runtime generation is a planned A/B experiment. tone_config has brand_envelope (outer bounds per dimension), scenario_defaults (dial positions), and voice_directive (free text). Nightcap brand envelope: irreverence 0.5-1.0, suspense 0.4-0.9, dark comedy 0.4-0.85, wit density 0.6-1.0, chaos tolerance 0.3-0.8.
Section: Cross-cutting
Status: Committed