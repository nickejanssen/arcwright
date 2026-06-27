# Rehearsal 1 - Founder Runbook

> **Status:** Active
> **Last updated:** 2026-06-27
> **For:** First real-human Nightcap session (M4 exit, AW-231)
> **Owner:** Founder
> **Related:** [blocker-log-template.md](blocker-log-template.md), [rehearsal-1-failure-cheat-sheet.md](rehearsal-1-failure-cheat-sheet.md)

## 0. Before the day

- [ ] Crime Scene Smash + Evidence Locker manifests at `lifecycle: active`.
- [ ] Both packages bound in `nightcap/arc.json`.
- [ ] Engine tests pass: `pytest engine/tests/ -k "mini_game or arc" -v`.
- [ ] Docker Desktop installed and running.
- [ ] `ANTHROPIC_API_KEY` and `GROQ_API_KEY` set in `.env` at repo root.
- [ ] `cloudflared` installed (`cloudflared --version` returns a version).
- [ ] At least 3 invitees RSVPed (you + 3 = 4-player floor for Crime Scene Smash).
- [ ] Invitees told: "Bring a phone (iOS or Android). I'll send a join link the night of."

## 1. Pre-flight (30 minutes before)

1. Open a terminal at repo root.

2. Start Postgres + engine:

   ```bash
   docker compose up -d
   ```

   Wait for `docker compose ps` to show both services `running (healthy)`.

3. Apply migrations:

   ```bash
   alembic upgrade head
   ```

   Expected: zero or more "Running upgrade" lines, no errors.

4. Verify engine is reachable:

   ```bash
   curl -s http://localhost:8000/health | jq .
   ```

   Expected: `{"status": "ok"}` (or equivalent healthy payload).

5. Start the Nightcap web app:

   ```bash
   cd web && npm run dev
   ```

   Note the port (default 5173). Leave running.

6. Start the cloudflared quick-tunnel in a separate terminal:

   ```bash
   cloudflared tunnel --url http://localhost:5173
   ```

   Note the printed `https://<random>.trycloudflare.com` URL. **This is the join URL for players.**

7. On the shared display device, navigate to:

   `https://<random>.trycloudflare.com/host`

   Sign in as host (use the existing Firebase test account or follow the auth flow).

8. Verify the host page loads cleanly: no console errors, no missing assets.

## 2. Session setup (5 minutes before players arrive)

1. On the shared display, create a new session. Pick arc: **Nightcap**. Pick diegetic frame: High Society / Corporate / Sci-Fi (your call).
2. Note the 6-character join code shown on the shared display.
3. Send to players in the group chat: "Open `https://<random>.trycloudflare.com` and enter join code `XXXXXX`."
4. As each player joins, confirm their name appears on the shared display lobby.
5. Wait until at least 4 players are in the lobby.
6. Start the session.

## 3. In-session checks

Run these at the moments listed. Note any failure in the blocker log.

| Checkpoint | What to look for | If wrong |
|---|---|---|
| Player join | Each join under 30 seconds | Log P1, continue |
| Private event | Each player's role / clue appears on their device, NOT on shared display | Log P0, STOP the session |
| Crime Scene Smash launch | All players see the match-3 board; shared display shows leaderboard | Log P1, continue if board is usable |
| Crime Scene Smash completion | Highest score gets the lead clue; others get nothing | Log P1, host narrates fallback if needed |
| Evidence Locker launch | The current solo player sees the pin-lock UI | Log P1, host narrates fallback if needed |
| Evidence Locker completion | Success: solo player gets clue. Failure: authored delayed-clue fallback fires automatically | Log P1 if neither path fires |
| Accusation | Every player can submit a killer vote | Log P0 if voting is broken |
| Reveal | Killer identity shown on shared display only after all votes are in | Log P0 if revealed early |

## 4. Wrap

1. After the killer reveal, ask players for spoken feedback. Take notes.

2. Export the session log (replace `<session-id>` and `<host-token>`):

   ```bash
   mkdir -p docs/roadmap/operations/rehearsal-1-artifacts
   curl -s "http://localhost:8000/api/sessions/<session-id>/export" \
     -H "Authorization: Bearer <host-token>" \
     > docs/roadmap/operations/rehearsal-1-artifacts/session-$(date +%Y%m%d).json
   ```

3. Tear down:

   ```bash
   docker compose down
   ```

   Stop cloudflared (Ctrl+C). Stop the web dev server (Ctrl+C).

4. Save the blocker log to `docs/roadmap/operations/rehearsal-1-artifacts/blockers-<YYYYMMDD>.md`.

5. Post a comment on AW-231 GitHub issue with: number of players, number of blockers by severity, link to artifacts.

6. Triage every blocker into a new GitHub issue (M5 / M5-G / M6 / wontfix). See AW-231 step 5.

## See also

- [blocker-log-template.md](blocker-log-template.md)
- [rehearsal-1-failure-cheat-sheet.md](rehearsal-1-failure-cheat-sheet.md)
