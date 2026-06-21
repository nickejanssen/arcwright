# Nightcap Mini-game Authoring

This directory holds Nightcap-specific mini-game packages. Arcwright owns the
generic schema and future deterministic runtime. Nightcap packages own authored
rules, content inputs, assets, and presentation prototypes.

## Add a Game

1. Copy `_template/` to a lowercase kebab-case directory named for the game ID.
2. Replace the template values in `manifest.json` and
   `definitions/0.1.0.json`.
3. Put browser presentation prototypes in `client/` and static files in
   `assets/`.
4. Add every required asset path to `manifest.json`.
5. Validate the package with `load_mini_game_package` before review.

```python
from pathlib import Path

from engine.mini_games import load_mini_game_package

load_mini_game_package(Path("nightcap/mini_games/my-game"))
```

Do not add a draft package to `nightcap/arc.json`. Arc bindings are introduced
only when a game is ready for the lifecycle required by its implementation
spec.

## Package Shape

```text
<game_id>/
  manifest.json
  definitions/<semver>.json
  README.md
  client/
  assets/
```

The manifest is stable package metadata. Definitions are immutable after they
enter playtest. Create a new semantic version instead of changing a playtest or
active definition in place.

## Lifecycle

- `draft`: authoring only; not selectable by sessions.
- `playtest`: explicitly enabled internal sessions only.
- `active`: approved for new production sessions.
- `retired`: unavailable to new sessions; historical run snapshots remain
  valid.

Lifecycle is metadata, not a directory. Moving files between dev, test, and
prod folders would break stable references and encourage configuration drift.

## Architecture Boundary

- Python owns future timers, validation, scoring, outcomes, clue unlocking, and
  persistence.
- Browser code renders authorized state and submits player actions only.
- Definitions may be authored, generative, or hybrid. Generated content never
  determines canonical state.
- Behavioral outputs are neutral metrics or deterministic, game-scoped
  observations. They do not affect killer assignment or cross-session behavior
  in v1.
- Every definition includes a delayed clue fallback so failure cannot make the
  mystery unsolvable.

Directories beginning with `_` are reserved and excluded from the production
catalog loader. `_fixtures/` contains non-shipping validation examples.
