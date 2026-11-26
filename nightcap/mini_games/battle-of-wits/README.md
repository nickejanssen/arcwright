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

## Play over Wi-Fi

From the repo root in Windows PowerShell, with Python 3.11+, Node, and the usual
development dependencies installed (`pip install -r requirements.txt`,
`npm install --prefix sdk`, then `npm ci --prefix dashboard`), run:

```powershell
python -m scripts.play_battle_of_wits
```

Open the printed Wi-Fi link on one to eight phones or computers on the same
network. If Windows Firewall asks, allow Python on the private network. Enter
distinct names and join before someone taps **Start**. Refresh the same tab to
reconnect. Press Ctrl+C on the PC to stop the room and clear the seats.
Players can't join after a round starts. **Play again** starts a fresh round with the same players.

The launcher builds and serves a dedicated page. It needs no external database,
account, model call, or running Nightcap service. Use it on a trusted local
network. The resolver reloads the configured, server-only bank for every round.
It uses the included `invented-v1` bank until the package points to updated
standalone questions that its 0.1.0 rules accept. Active rounds keep the
questions they started with.

The HTTP room tests use a fixed clock to check results, late answers, replay,
and bank replacement. The dashboard tests check isolated phone views. A
physical phone on the founder's Wi-Fi is a separate live check.
