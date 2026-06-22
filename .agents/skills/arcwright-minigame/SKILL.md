---
name: arcwright-minigame
description: Add, import, validate, fit-check, test, and promote a mini-game package in the Arcwright repo as a single gated lifecycle. Use whenever someone wants to bring a mini-game into the platform or move one along its lifecycle, even if they only say "add a mini-game", "import this game", "new puzzle/clue mini-game", "scaffold a Nightcap mini-game", "validate my mini-game package", "does this mini-game fit the story", "is this on-spec", "promote the mini-game to playtest/active", or hands over a zip or folder of a game to ingest. Keeps the engine boundary from ADR 0009 intact: Python owns timers, scoring, submissions, outcomes, clue unlocking, and persistence; clients only render and submit; AI never decides outcomes. Author packages under <experience>/mini_games/, defaulting to nightcap/mini_games/.
---

# Arcwright Mini-game Integrator (Codex launcher)

This is a thin launcher. It carries no role logic of its own. The canonical contract is `docs/skills/arcwright-minigame/SKILL.md`. Read that file in full and follow it exactly.
