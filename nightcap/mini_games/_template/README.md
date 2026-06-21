# Mini-game Template

Copy this entire directory to `nightcap/mini_games/<game_id>/`, then update the
manifest and definition IDs together. The package is intentionally valid before
copying so automated validation can protect the authoring scaffold.

`client/` is a presentation workspace only. Do not place timers, scoring, clue
unlocking, or other canonical state logic there.
