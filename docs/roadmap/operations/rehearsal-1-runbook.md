# Rehearsal 1 - Founder Runbook

> **Superseded for day-of use (2026-07-11):** start with
> [rehearsal-quickstart.md](rehearsal-quickstart.md) — the stack is now one
> command (`make rehearsal`). This document remains as the deep
> troubleshooting reference; its five-terminal manual procedure is obsolete.

> **Status:** Active
> **Last updated:** 2026-06-27
> **For:** First real-human Nightcap session (M4 exit, AW-231)
> **Owner:** Founder
> **Related:** [blocker-log-template.md](blocker-log-template.md), [rehearsal-1-failure-cheat-sheet.md](rehearsal-1-failure-cheat-sheet.md)

---

## 0. Before the day - one-time machine setup

Do this once, at least the day before. Everything here is a prerequisite for the pre-flight in Section 1.

### Step 1 - Create your .env file

The engine and database both read from a `.env` file at the repo root. It does not exist yet; you need to create it from the template.

Open PowerShell at the repo root and run:

```powershell
Copy-Item .env.example .env
```

Then open `.env` in any text editor and fill in your real API keys:

```
ANTHROPIC_API_KEY=sk-ant-...your key here...
GROQ_API_KEY=gsk_...your key here...
```

Leave everything else as-is. The Postgres values (`arcwright` / `arcwright` / `arcwright`) are correct for local dev. The `DATABASE_URL` line can stay blank - the engine assembles it from the individual `POSTGRES_*` values.

> **How to get the keys:**
> - Anthropic key: console.anthropic.com - API Keys section
> - Groq key: console.groq.com - API Keys section

**Verify:** open `.env` and confirm neither key line ends with `=` alone.

---

### Step 2 - Verify Docker Desktop is installed and running

1. Open Docker Desktop from your Start menu.
2. Wait until the whale icon in the taskbar tray is solid (not animated). This means the engine is up.
3. In PowerShell, confirm: `docker version` - you should see both Client and Server sections.

If Docker Desktop is not installed: download it from docker.com/products/docker-desktop. Install, restart your machine, then come back here.

---

### Step 3 - Verify Python environment

The engine runs on Python 3.11+. In PowerShell:

```powershell
python --version
```

Expected: `Python 3.11.x` or higher. If you see 3.10 or lower, activate your conda env first:

```powershell
conda activate base
```

Then install engine dependencies (if you have not done this already):

```powershell
pip install -r requirements.txt
```

This only needs to run once, or after pulling changes that update `requirements.txt`.

---

### Step 4 - Verify Node / npm for the dashboard

```powershell
node --version   # expect v18 or higher
npm --version    # expect 9 or higher
```

If Node is not installed: download LTS from nodejs.org and install.

Install dashboard dependencies (once, or after `npm` changes):

```powershell
cd dashboard
npm install
cd ..
```

---

### Step 5 - Install cloudflared and set up a named tunnel

`cloudflared` creates the public tunnel so players can reach your local server from their phones. There are two modes:

**Quick tunnel (no account, random URL):** URL changes every restart. Fine for solo testing, not for a rehearsal where you're texting people a link.

**Named tunnel (recommended for Rehearsal 1):** Fixed URL, runs under your Cloudflare account. Set this up once; the URL never changes.

#### 5a - Install cloudflared

Check if it is already installed:
```powershell
cloudflared --version
```

If not found:
1. Go to: developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
2. Download the Windows AMD64 `.exe`.
3. Save it to a directory on your PATH (e.g. `C:\Windows\System32\cloudflared.exe`).

#### 5b - Create a free Cloudflare account (if you do not have one)

1. Go to cloudflare.com and sign up for a free account.
2. You do NOT need to buy a domain. Cloudflare gives you a free `*.cfargotunnel.com` subdomain for tunnels, or you can use a domain you already own.

#### 5c - Log in with cloudflared

```powershell
cloudflared tunnel login
```

This opens a browser. Authorize cloudflared with your Cloudflare account. A credentials file is saved at `~/.cloudflared/cert.pem`. You only do this once per machine.

#### 5d - Create a named tunnel

```powershell
cloudflared tunnel create nightcap-rehearsal
```

Expected output: a tunnel ID (UUID). Note it — you will need it in the next step.

#### 5e - Create the config file

Create the file `~/.cloudflared/config.yml` (or `C:\Users\<you>\.cloudflared\config.yml` on Windows):

```yaml
tunnel: nightcap-rehearsal
credentials-file: C:\Users\<your-username>\.cloudflared\<tunnel-id>.json

ingress:
  - hostname: nightcap.<your-subdomain>.cfargotunnel.com
    service: http://localhost:5173
  - service: http_status:404
```

Replace `<your-username>` and `<tunnel-id>` with your actual values. The `hostname` can be any subdomain under `cfargotunnel.com` as long as you add a DNS record for it.

#### 5f - Add a DNS record

```powershell
cloudflared tunnel route dns nightcap-rehearsal nightcap.<your-subdomain>.cfargotunnel.com
```

This creates a CNAME in your Cloudflare DNS. After this step, your fixed URL is:
`https://nightcap.<your-subdomain>.cfargotunnel.com`

Send this URL to players in advance. It does not change between runs.

#### 5g - Test the tunnel (quick check, no config file needed)

If you just want to verify cloudflared is working before setting up the named tunnel:
```powershell
cloudflared tunnel --url http://localhost:5173
```

Note the `https://*.trycloudflare.com` URL. This is the quick-tunnel mode — valid for solo testing only. The URL changes every time you restart.

> **Vite and external hostnames:** If you see "Blocked request. This host is not allowed" in the browser, it means Vite's dev server is rejecting the tunnel URL. This is already fixed in the dashboard config (`allowedHosts: true` in `dashboard/vite.config.ts`). Make sure you are running the latest version of the dashboard code.

---

### Step 6 - Run the engine tests

This confirms both mini-games are properly promoted and the engine is healthy.

```powershell
pytest engine/tests/ -k "mini_game or arc" -v
```

Expected: all tests pass. One test is skipped (the database integration test that requires a live Postgres - that is fine and expected). Zero failures.

> **If tests fail:** ping me before the rehearsal day. Do not proceed until tests are green.

---

### Step 7 - Verify mini-game lifecycle and arc bindings

```powershell
python -c "
from pathlib import Path
import json
root = Path('nightcap/mini_games')
for d in sorted(root.iterdir()):
    m = d / 'manifest.json'
    if m.exists():
        data = json.loads(m.read_text())
        print(data['game_id'], '->', data['lifecycle'])
"
```

Expected output includes:
```
crime-scene-smash -> active
evidence-locker-402 -> active
```

And confirm arc bindings:

```powershell
python -c "
import json
arc = json.loads(open('nightcap/arc.json').read())
for beat in arc['beats']:
    if beat['mini_games']:
        print(beat['beat_id'], '->', [g['game_id'] for g in beat['mini_games']])
"
```

Expected:
```
opening_move -> ['crime-scene-smash']
dig -> ['evidence-locker-402']
```

---

### Step 8 - Confirm invitees

- At least 3 people have confirmed they are coming (you + 3 = 4-player minimum for Crime Scene Smash).
- They know to bring a phone (iOS Safari or Android Chrome).
- You have a way to message them a URL the night of (group chat, iMessage, WhatsApp, etc.).

---

## 1. Pre-flight (30 minutes before)

All five terminals below can be PowerShell tabs. Open them now.

### Terminal 1 - Database

```powershell
docker compose up -d
```

Wait 10 seconds, then check:

```powershell
docker compose ps
```

Expected: `arcwright-postgres` is `running (healthy)`. If it shows `starting`, wait another 10 seconds and check again. If it shows `exited`, run `docker compose logs postgres` and look for the error.

> **Common issue:** Docker Desktop not running. Open it from Start menu and wait for the tray icon to go solid before running `docker compose up -d`.

### Terminal 2 - Migrations

```powershell
alembic upgrade head
```

Expected: one or more `Running upgrade` lines, ending cleanly. No errors.

> **If you see "Database configuration is missing":** your `.env` file is missing or the `POSTGRES_*` variables are blank. Re-do Section 0, Step 1.

> **If you see "Connection refused":** Postgres is not healthy yet. Wait 15 more seconds and try again.

### Terminal 3 - API engine

```powershell
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload --env-file .env
```

Wait for the line: `Application startup complete.`

> **Why `--env-file .env`:** The API reads `os.environ` directly (no `load_dotenv()` call). Without this flag, `POSTGRES_*` and `ARCWRIGHT_API_KEY` are not visible to uvicorn, so the engine falls back to defaults and the database connection fails.

Verify it is reachable (open a new terminal tab, leave uvicorn running in Terminal 3):

```powershell
curl.exe http://localhost:8000/health
```

Expected: `{"status":"ok"}`

> **Why `curl.exe` not `curl`:** PowerShell aliases `curl` to `Invoke-WebRequest`. The `.exe` suffix bypasses the alias and calls the real curl binary.

> **If uvicorn is not found:** you are not in the right Python env. Run `conda activate base` first.

### Terminal 4 - Dashboard

```powershell
cd dashboard
npm run dev
```

Wait for: `Local: http://localhost:5173/`

Open `http://localhost:5173` in your browser and confirm the dashboard loads. Leave this terminal running.

> **If you see module errors:** run `npm install` first, then try again.

### Terminal 5 - Cloudflared tunnel

```powershell
cloudflared tunnel --url http://localhost:5173
```

Within 10 seconds you will see:

```
Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):
https://some-random-words.trycloudflare.com
```

**Write down or copy that URL.** This is the join URL you will send to players. Leave this terminal running.

> **The URL changes every time you restart cloudflared.** Do not restart it unless something breaks - players will lose access.

> **If cloudflared is not found:** use the full path, e.g. `C:\path\to\cloudflared.exe tunnel --url http://localhost:5173`

---

## 2. Session setup (5 minutes before players arrive)

1. On the shared display (laptop screen / TV / monitor that everyone can see), open Chrome and navigate to:

   `https://<your-tunnel-url>/host`

2. Sign in as host using the Firebase test account (email: see your password manager, or use the "play as guest" flow if auth is not wired yet).

3. Create a new session:
   - Arc: **Nightcap**
   - Diegetic frame: your pick - High Society, Corporate, or Sci-Fi all work

4. The shared display shows a 6-character join code (example: `WREN42`).

5. Message players: "Open `https://<your-tunnel-url>` on your phone and enter code `WREN42`."

6. Watch the lobby on the shared display. As each player joins, their name appears.

7. Wait until at least 4 players are in the lobby, then press Start.

---

## 3. In-session checks

Log any failure in the blocker log. Do not stop the session unless the failure is marked P0.

| Checkpoint | What to look for | Severity if wrong | Recovery |
|---|---|---|---|
| Player join | Each join under 30 seconds | P1 | Log it; continue |
| Private event delivery | Each player's role / clue shows on THEIR device only, NOT on shared display | P0 | **STOP. Do not resume without an engineering fix.** |
| Crime Scene Smash launch | All players see the match-3 board; shared display shows leaderboard | P1 | Log it; if board is broken for all players, skip to narrator fallback |
| Crime Scene Smash completion | Highest score player gets the lead clue; others do not | P1 | Log it; narrator reads the clue aloud as fallback |
| Beat transition (opening_move to dig) | Narrator acknowledges the transition on shared display | P1 | Log it; host narrates manually |
| Evidence Locker launch | The current solo player sees the pin-lock UI on their phone | P1 | Log it; host narrates the clue instead |
| Evidence Locker - success path | Solo player cracks the lock; gets the clue privately | P1 | Log it |
| Evidence Locker - fallback path | If timer runs out: authored delayed-clue fires automatically | P1 | Log it if neither path fires |
| Accusation | Every player can submit a killer vote from their device | P0 | **STOP if voting is broken for any player.** |
| Reveal | Killer identity shown on shared display only after all votes are in | P0 | **STOP if revealed early - this is a privacy P0.** |

---

## 4. Wrap

1. **Verbal debrief.** After the killer reveal, ask the room two questions:
   - "What felt fun?"
   - "What was confusing or broke?"
   Take notes or voice-memo while it is fresh.

2. **Export the session log** (replace `<session-id>` and `<host-token>`):

   ```powershell
   New-Item -ItemType Directory -Force docs/roadmap/operations/rehearsal-1-artifacts
   $date = Get-Date -Format "yyyyMMdd"
   Invoke-RestMethod `
     -Uri "http://localhost:8000/api/sessions/<session-id>/export" `
     -Headers @{ Authorization = "Bearer <host-token>" } `
     | ConvertTo-Json -Depth 20 `
     | Out-File "docs/roadmap/operations/rehearsal-1-artifacts/session-$date.json"
   ```

3. **Tear down:**

   - Terminal 5 (cloudflared): Ctrl+C
   - Terminal 4 (dashboard): Ctrl+C
   - Terminal 3 (uvicorn): Ctrl+C
   - Terminal 1 (docker): `docker compose down`

4. **Save the blocker log.** Copy your notes from the session into:

   `docs/roadmap/operations/rehearsal-1-artifacts/blockers-<YYYYMMDD>.md`

   Use [blocker-log-template.md](blocker-log-template.md) as the format.

5. **Post on AW-231** (GitHub issue): number of players, number of blockers by severity (P0 / P1 / P2), link to the artifacts folder.

6. **Triage every blocker** into a new GitHub issue with the right milestone:
   - Engineering bug → M5 hardening
   - Visual / UX issue → M5-G polish
   - Operational / infra → M6 ops
   - Not worth fixing → wontfix

   After all blockers are triaged, close M4 in `docs/roadmap/index.json` and close AW-231 and AW-259 on GitHub.

---

## See also

- [blocker-log-template.md](blocker-log-template.md)
- [rehearsal-1-failure-cheat-sheet.md](rehearsal-1-failure-cheat-sheet.md)
