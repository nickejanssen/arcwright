# Battle of Wits

Draft package `battle-of-wits@0.1.0` for one to eight players. The included
invented fixture is `invented-v1`, selected in `definitions/0.1.0.json`.
`server/questions-0.1.0.json` is server input and must stay out of browser
assets and responses. The resolver loads it relative to the selected package,
and the dashboard dev server excludes it. The run saves a copy so that a restart
can continue from the same questions.

The fixture has two 12-second four-choice questions and one 20-second sort.
Each question has a five-second reveal. A correct choice is worth four points.
Sorting earns one point for each correct position, including the pre-placed
card on a valid submission. Ties share rank. A missed question earns zero.
Below a higher-ranked player, every player in the bottom tier gets private help
on the next question. The shared screen shows the correct answer after each
window and reads the final standing from last to first.

## Validate and run the fixture

From the repository root with Python 3.11 or newer and the development
dependencies installed:

```sh
python docs/skills/arcwright-minigame/scripts/minigame_tool.py validate nightcap/mini_games/battle-of-wits
python -m pytest engine/tests/test_battle_of_wits.py -q
npm test --prefix dashboard
```

The Python run exercises the real package and rules with a fixed clock. The
two-, three-, and four-player story tests use an invented arc fixture with a
75-second phase cap, `result_public: true`, and `result_hold_seconds: 10`.
The definition declares a 65-second run budget. The answer and reveal windows
take 59 seconds before tick latency. Allow time for the server to tick and for
the separate final result hold when setting up a destination phase.

AW-348 can use the package directory above, version `0.1.0`, and
`invented-v1` with the normal package resolver and mechanic registry. An
independent join and replay URL, physical devices, and player pacing evidence
are part of the AW-348 live run.
