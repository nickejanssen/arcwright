---
id: productroadmap.roadmap.operations.session-1-host-cheat-sheet
namespace: product-roadmap
title: Session 1 Host Cheat Sheet
owner: Nico Janssen
status: active
review_by: "2026-12-24"
sensitivity: internal
source: authored
x-scope-evidence: none
tags: []
supersedes: []
---

# Session 1 Host Cheat Sheet

> Current version: v1.0
> Last updated: 2026-11-26
> Status: Current. Checked by reading the code. Not yet run on a TV and phones.
> Canonical path: docs/roadmap/operations/session-1-host-cheat-sheet.md
> Serves: AW-308. Nightcap case 1, version 1a, at home.

**Three rules**

1. Connect phones over your home Wi-Fi. Do not use the `trycloudflare.com` tunnel. It does not carry the live updates the mini-game needs.
2. Each player stays on the same phone and the same browser all game. No private tabs.
3. Do not run `make rehearsal` for this game. It starts the old Couch Race.

Open problems behind these rules: [#509](https://github.com/nickejanssen/arcwright/issues/509) live updates, [#510](https://github.com/nickejanssen/arcwright/issues/510) case files can be read through the screens program (only let people you trust onto the Wi-Fi), [#511](https://github.com/nickejanssen/arcwright/issues/511) one-command start, [#512](https://github.com/nickejanssen/arcwright/issues/512) stuck games.

## When it breaks

| What you see | What to do | Give up when |
| --- | --- | --- |
| **A phone dropped or the browser closed** | Same phone, same browser: open `http://PC-ADDRESS:5173/join` (the TV shows its QR code only before the game starts). It shows "Finding your seat..." and returns to the seat with its notebook. | The phone is dead, was swapped, or its browser data was cleared. That seat cannot be recovered. The game still moves on by its clocks. Continue without them, or start a new game. |
| **The host's phone is lost** (host = first to join) | Use window 3: `Send-HostCommand "round/move-on"` (also `pause`, `resume`, `start`, `end`). | Window 3 was closed or the command is refused twice. The game still moves on by its clocks. |
| **A phone shows the wrong or a stuck screen** | Reload the page. "Eyes on the TV." is normal in some parts. If it says "This game is no longer running.", tap **Join another game**. | Still wrong after two reloads while other phones are right. |
| **The host's menu has no Start game or Move on** | Reload the host's phone. It checks who is host only when the page opens. | Still missing: use `Send-HostCommand` in window 3. |
| **A phone shows the join form during the game** | They opened a different browser or app. Go back to the browser they joined in. | "This game has started. Use the phone you joined with." appears there too. Treat as a lost phone. |
| **TV frozen**, or "Cannot reach the game. Trying again." | Click the TV browser and press F5. If the message stays, check windows 1 and 2 (see crashes below). | Two reloads fail while both windows look healthy. Restart the screens (window 2). |
| **TV says "This game is no longer running."** | The address is wrong or old. Rerun the `Start-Process` line in window 3. | The same message after that: start a new game. |
| **Player cannot join: no page loads** | Phone on the same Wi-Fi, not mobile data or a guest network. VPN off. Type `http://PC-ADDRESS:5173/join`. If Windows asks, allow Node.js on private networks. No QR code on the TV means no internet: type the address and room code. | No phone at all can load it after checking Wi-Fi and the firewall. |
| "That code did not work. Check the TV." | Retype the room code from the TV. | |
| "This game has started. Use the phone you joined with." | Nobody can join after Start game. | Start a new game if they must play. |
| "Something went wrong. Try again." | Check the TV's name list first. The seat may already exist. Check window 1 for an error and check the internet. | A name appears that no phone holds. Start a new game before pressing Start game. |
| "This phone would not save your seat..." | Allow the site to store data, then tap **Join** again. | |
| **Start game does nothing**, "That did not work. Try again." | Run the case file check in "Before guests arrive". It must say `True`. Read the error in window 1. | The file is there and it fails twice. |
| **Mini-game stuck** on one phone | Reload that phone. | |
| **Mini-game stuck** for everyone | Wait: the part ends by itself after 75 seconds. Or host: **Menu**, **Finish mini-game now**. If that fails, **Cancel mini-game** (no winner), then **Move on**. Reload screens that stay behind. | It happens in two rounds running. Note it and decide whether to carry on. |
| **A timer seems stuck** | Is it paused? Anyone can tap **Menu**, **Resume**. Otherwise reload that screen. Host can tap **Move on** (during Last Call it asks first and locks every theory). | The TV and phones all stay at 0:00 for 30 seconds after reload: restart the engine (window 1). |
| **Resume fails** and the game stays paused | Resume usually needs the internet and the writing service. Check the internet, try again, read window 1. Avoid Pause unless you need it. | Three failed tries. Start a new game. |
| **Engine crashed** (window 1 stopped, TV cannot reach the game) | In window 1 press the Up arrow, then Enter. Reload every screen. Saved progress stays. A part whose time ran out while it was down ends at once. | It stops twice more. |
| Window 1 repeats "round tick pass failed" | The database is down. Check Docker Desktop is running, then in window 3 run `docker compose up -d --wait`. | Still repeating after one minute. |
| **Screens program crashed** (window 2 stopped) | In window 2 press the Up arrow, then Enter. Reload every screen. Seats stay if the PC address is unchanged. | It stops twice more. |
| **PC restarted or Wi-Fi changed** | Start windows 1 and 2 again. Run the `$ip` line below. Same address: reload screens. | The address changed. Phones lose their seats. Start a new game. |
| **Private information or the case solution on the TV or another player's phone** | **Stop at once.** Press Ctrl+C in window 2. Say "we hit a bug". Write down what showed. | Do not resume. |

**Start a new game:** rerun the "Create the game" block in window 3. Everyone scans the new QR code. The old game's progress does not carry over.

After a game ends, write down the time, who it hit and what you saw.

## Start the stack

Open three PowerShell windows in the `arcwright` folder (the one that holds `.env`). Start Docker Desktop. Stop the PC from sleeping.

**Before guests arrive.** The first command must say `True`. The second must show nothing (nothing else is using the two ports).

```powershell
Test-Path nightcap\cases\local\agency-race-1a.json
```

```powershell
Get-NetTCPConnection -LocalPort 8000,5173 -State Listen -ErrorAction SilentlyContinue
```

**Window 1: database and engine.** Leave it open.

```powershell
docker compose up -d --wait
```

```powershell
python -m alembic upgrade head
```

```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --env-file .env
```

**Window 2: screens.** Leave it open. First time only, run `npm install` after the `cd` line.

```powershell
cd dashboard
```

```powershell
$env:VITE_FIREBASE_WEB_API_KEY = ((Get-Content ..\.env) -match '^FIREBASE_WEB_API_KEY=' -split '=',2)[1].Trim()
```

```powershell
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort
```

**Window 3: create the game.** Paste the whole block. It opens the TV page; move that browser to the TV. Do it within one go: the host sign-in it fetches must be taken within an hour of creating the game.

```powershell
$ip = (Get-NetIPConfiguration | Where-Object IPv4DefaultGateway | Select-Object -First 1).IPv4Address.IPAddress
$key = ((Get-Content .env) -match '^ARCWRIGHT_API_KEY=' -split '=',2)[1].Trim()
$web = ((Get-Content .env) -match '^FIREBASE_WEB_API_KEY=' -split '=',2)[1].Trim()
$game = Invoke-RestMethod -Method Post http://127.0.0.1:8000/v1/sessions -Headers @{'X-Api-Key'=$key} -ContentType application/json -Body '{"arc_id":"nightcap-agency-race-1a"}'
$signin = Invoke-RestMethod -Method Post "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=$web" -ContentType application/json -Body (@{token=$game.host_token; returnSecureToken=$true} | ConvertTo-Json)
function Send-HostCommand($what) {
  $t = Invoke-RestMethod -Method Post "https://securetoken.googleapis.com/v1/token?key=$web" -ContentType application/x-www-form-urlencoded -Body "grant_type=refresh_token&refresh_token=$($signin.refreshToken)"
  (Invoke-RestMethod -Method Post "http://127.0.0.1:8000/v1/sessions/$($game.session_id)/$what" -Headers @{Authorization="Bearer $($t.id_token)"}) | Out-Host
}
Write-Host "Phones: http://${ip}:5173/join   PC-ADDRESS is $ip"
Start-Process "http://127.0.0.1:5173/display/$($game.session_id)?join_base_url=http://${ip}:5173"
```

**Play:** players scan the TV's QR code. Wait for every name (2 to 4, no extras). The first to join taps **Menu**, **Start game**. After the last recap and the survey, the host taps **Menu**, **End game**.

## Stop the stack

Press Ctrl+C in window 2, then in window 1. Then:

```powershell
docker compose stop
```

This keeps the saved games. Never add `-v` to a `docker compose down` command: that deletes them.

---

## How each step was checked (not needed during a game)

All checks are from reading the code on 2026-11-26 unless marked otherwise. "Tested" means an automated or local check ran.

| Claim | How checked |
| --- | --- |
| Same phone rejoins with its own notebook and findings; nobody else's | **Tested** through the real routes: `api/tests/test_rejoin_api.py` (Firebase signing and checking stand-ins). Page side: `dashboard/src/screens/JoinScreen.tsx`, `dashboard/src/api/seatStore.ts`, `dashboard/tests/join-resume.test.tsx` (read, not rerun) |
| Seat is tied to one browser and one address; no recovery elsewhere | `seatStore.ts` uses browser storage, which browsers keep per address; spec 0095 Part N says not recoverable in session 1 |
| Tunnel does not carry live updates | [Cloudflare's Quick Tunnels limits page](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/) says no Server-Sent Events. `dashboard/src/mini-games/client.ts` and the Battle of Wits renderer move on only from that stream. **Effect on a phone is inferred**, never seen. [#509](https://github.com/nickejanssen/arcwright/issues/509) |
| Home Wi-Fi route | `dashboard/vite.config.ts` (`/v1` proxy, any host name), `DisplayScreen.tsx` (`join_base_url`), `player.ts` and `mini-game-kit/submission.ts` (work without a secure page). **Not run from a real phone** |
| Mini-game screen stops following updates after about two seconds of failures | `client.ts`, three retries; reload starts it again |
| Screens re-read the game every 2 seconds; reload rebuilds them | `dashboard/src/shell/useFeed.ts`, `feed.ts`, `DisplayScreen.tsx`, `WaitingScreen.tsx` |
| Every quoted message and button name | `dashboard/src/shell/copy.ts`, `StartMenu.tsx`, `ConfirmDialog.tsx` |
| Host is the first to join; host commands from the PC | `engine/session/host_seat.py`, `api/auth/seat.py`, `api/auth/__init__.py`. **PC commands not run against a live engine** |
| Host role read once per page load | `WaitingScreen.tsx`, `api/seam.ts` |
| Join refusals; seat made before sign-in finishes; no player maximum at join | `engine/session/service.py` (`lobby_join`), `api/routers/lobby.py`, `JoinScreen.tsx` |
| Part lengths and early endings | `nightcap/agency-race-1a.arc.json`, `engine/session/phases.py`, `mini_game_phase.py` |
| Engine restart keeps saved progress; expired part ends at once | `api/tick_loop.py`, `engine/session/phases.py` (state is saved, events are in memory) |
| Resume usually calls a model (not when there is no saved snapshot) | `api/routers/sessions.py` (`resume_session`), `engine/narrator/bridge.py` |
| Missing case file breaks Start game | `engine/session/case_seating.py`; seen in a headless run recorded on issue #362 |
| `make rehearsal` creates Couch Race and stops everything when one part stops | `scripts/rehearsal.py` |
| Key-reading and address lines in PowerShell | **Tested** on a made-up `.env` file |
| Windows firewall prompt, guest Wi-Fi, VPN | General Windows and router behaviour. **Not checked** |

**Not verified at all:** the start commands run end to end with real settings; Firebase sign-in from a phone on a plain `http` home address; anything on a real TV or phone; the "give up" limits, which are recommendations.
